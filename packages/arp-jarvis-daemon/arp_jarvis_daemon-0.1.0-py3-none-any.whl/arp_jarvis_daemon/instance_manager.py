from __future__ import annotations

import os
import signal
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Mapping
from urllib.parse import urlparse

import httpx

from arp_sdk.daemon.models import RuntimeProfile
from arp_sdk.daemon.models.runtime_instance_state import RuntimeInstanceState
from arp_sdk.daemon.types import Unset

from .config import DaemonConfig
from .instance_store import InstanceStore
from .runtime_process import RuntimeProcess, _venv_bin_dir, ensure_venv, pip_install
from .runtime_profiles import RuntimeExecConfig, parse_exec_config
from .types import InstanceRecord


@dataclass(slots=True)
class InstanceManager:
    config: DaemonConfig
    _store: InstanceStore = field(init=False, repr=False)
    _processes: dict[str, RuntimeProcess] = field(default_factory=dict)
    _managed: dict[str, InstanceRecord] = field(default_factory=dict)
    _external: dict[str, InstanceRecord] = field(default_factory=dict)
    _states: dict[str, RuntimeInstanceState] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.config.data_dir.mkdir(parents=True, exist_ok=True)
        store_path = self.config.instances_path or (self.config.data_dir / "instances.json")
        self._store = InstanceStore(path=store_path)

        for record, state in self._store.load():
            if record.managed:
                self._managed[record.instance_id] = record
            else:
                self._external[record.instance_id] = record
            self._states[record.instance_id] = state

        # Refresh state/version for persisted instances (best-effort).
        for record in list(self._managed.values()):
            if record.pid is not None and not _pid_alive(record.pid):
                self._states[record.instance_id] = RuntimeInstanceState.STOPPED
                continue
            self._managed[record.instance_id] = self._probe_runtime(record)

        for record in list(self._external.values()):
            self._external[record.instance_id] = self._probe_runtime(record)

        self._persist()

    def create_managed(
        self,
        *,
        profile: RuntimeProfile,
        count: int,
        env: Mapping[str, str],
        args: list[str],
        metadata: dict[str, Any] | None = None,
        extensions: dict[str, Any] | None = None,
    ) -> list[InstanceRecord]:
        exec_config = parse_exec_config(profile)

        runtime_profile = profile.runtime_profile
        runtime_name = None if isinstance(profile.runtime_name, Unset) else str(profile.runtime_name)
        defaults_env: dict[str, str] = {}
        defaults_args: list[str] = []
        default_tool_registry_url: str | None = None
        if not isinstance(profile.defaults, Unset):
            if not isinstance(profile.defaults.env, Unset):
                defaults_env = {k: str(v) for k, v in profile.defaults.env.to_dict().items()}
            if not isinstance(profile.defaults.args, Unset):
                defaults_args = [str(x) for x in list(profile.defaults.args)]
            if not isinstance(profile.defaults.tool_registry_url, Unset):
                default_tool_registry_url = str(profile.defaults.tool_registry_url)

        merged_env = {**defaults_env, **{k: str(v) for k, v in env.items()}}
        merged_args = [*defaults_args, *[str(x) for x in args]]

        created: list[InstanceRecord] = []

        tool_registry_url = merged_env.get("ARP_TOOL_REGISTRY_URL") or merged_env.get("JARVIS_TOOL_REGISTRY_URL") or default_tool_registry_url
        if tool_registry_url:
            merged_env.setdefault("ARP_TOOL_REGISTRY_URL", tool_registry_url)

        for _ in range(max(0, int(count))):
            instance_id = f"inst_{uuid.uuid4().hex[:10]}"
            self._states[instance_id] = RuntimeInstanceState.STARTING

            if self.config.virtual_runtime_instances:
                endpoint = f"http://{instance_id}.runtime.local"
                record = InstanceRecord(
                    instance_id=instance_id,
                    runtime_profile=runtime_profile,
                    runtime_name=runtime_name,
                    runtime_version=None,
                    runtime_api_endpoint=endpoint,
                    managed=True,
                    pid=None,
                    metadata=metadata,
                    extensions=extensions,
                )
                record = self._probe_runtime(record)
                self._managed[instance_id] = record
                created.append(record)
                self._persist()
                continue

            base_env = dict(self.config.runtime_default_env)
            if "JARVIS_TRACE_DIR" not in base_env and "JARVIS_TRACE_DIR" not in merged_env:
                base_env["JARVIS_TRACE_DIR"] = str(self.config.data_dir / "runs")

            command_template = self._resolve_command_template(exec_config, runtime_profile=runtime_profile)
            process = RuntimeProcess.spawn(
                instance_id=instance_id,
                runtime_profile=runtime_profile,
                runtime_name=runtime_name,
                runtime_version=None,
                command_template=command_template,
                extra_args=merged_args,
                base_env=base_env,
                env=merged_env,
            )
            self._processes[instance_id] = process

            health_path = process.wait_for_health(
                health_paths=self.config.runtime_health_paths,
                timeout_s=self.config.runtime_startup_timeout_s,
                poll_interval_s=self.config.runtime_health_poll_interval_s,
            )
            version_path = health_path.replace("/health", "/version")
            service_name, service_version = process.try_fetch_version_info(version_path=version_path)
            if process.runtime_name is None and service_name:
                process.runtime_name = service_name
            if service_version:
                process.runtime_version = service_version

            self._states[instance_id] = RuntimeInstanceState.READY
            record = InstanceRecord(
                instance_id=instance_id,
                runtime_profile=runtime_profile,
                runtime_name=process.runtime_name,
                runtime_version=process.runtime_version,
                runtime_api_endpoint=process.runtime_api_endpoint,
                managed=True,
                pid=process.pid,
                metadata=metadata,
                extensions=extensions,
            )
            self._managed[instance_id] = record
            created.append(record)
            self._persist()

        return created

    def register_external(
        self,
        *,
        runtime_api_endpoint: str,
        runtime_profile: str | None = None,
        runtime_name: str | None = None,
        metadata: dict[str, Any] | None = None,
        extensions: dict[str, Any] | None = None,
    ) -> InstanceRecord:
        instance_id = f"ext_{uuid.uuid4().hex[:10]}"
        record = InstanceRecord(
            instance_id=instance_id,
            runtime_profile=runtime_profile,
            runtime_name=runtime_name,
            runtime_version=None,
            runtime_api_endpoint=runtime_api_endpoint.rstrip("/"),
            managed=False,
            pid=None,
            metadata=metadata,
            extensions=extensions,
        )
        self._external[instance_id] = record
        self._states[instance_id] = RuntimeInstanceState.STARTING

        try:
            with httpx.Client(timeout=2.0, **self.config.runtime_httpx_args) as client:
                health_ok = False
                for path in self.config.runtime_health_paths:
                    resp = client.get(f"{record.runtime_api_endpoint}{path}")
                    if resp.status_code == 200:
                        health_ok = True
                        break
                self._states[instance_id] = RuntimeInstanceState.READY if health_ok else RuntimeInstanceState.ERROR

                version_path = "/v1/version"
                resp = client.get(f"{record.runtime_api_endpoint}{version_path}")
                if resp.status_code == 200 and isinstance(resp.json(), dict):
                    payload = resp.json()
                    service_name = payload.get("service_name")
                    service_version = payload.get("service_version")
                    updated = InstanceRecord(
                        instance_id=record.instance_id,
                        runtime_profile=record.runtime_profile,
                        runtime_name=record.runtime_name or (service_name if isinstance(service_name, str) else None),
                        runtime_version=service_version if isinstance(service_version, str) else None,
                        runtime_api_endpoint=record.runtime_api_endpoint,
                        managed=record.managed,
                        pid=record.pid,
                        metadata=record.metadata,
                        extensions=record.extensions,
                    )
                    self._external[instance_id] = updated
                    record = updated
        except Exception:
            self._states[instance_id] = RuntimeInstanceState.ERROR

        self._persist()
        return record

    def _probe_runtime(self, record: InstanceRecord) -> InstanceRecord:
        try:
            with httpx.Client(timeout=2.0, **self.config.runtime_httpx_args) as client:
                health_ok = False
                for path in self.config.runtime_health_paths:
                    resp = client.get(f"{record.runtime_api_endpoint}{path}")
                    if resp.status_code == 200:
                        health_ok = True
                        break
                self._states[record.instance_id] = RuntimeInstanceState.READY if health_ok else RuntimeInstanceState.ERROR

                resp = client.get(f"{record.runtime_api_endpoint}/v1/version")
                if resp.status_code != 200 or not isinstance(resp.json(), dict):
                    return record
                payload = resp.json()
                service_name = payload.get("service_name")
                service_version = payload.get("service_version")
                return InstanceRecord(
                    instance_id=record.instance_id,
                    runtime_profile=record.runtime_profile,
                    runtime_name=record.runtime_name or (service_name if isinstance(service_name, str) else None),
                    runtime_version=service_version if isinstance(service_version, str) else None,
                    runtime_api_endpoint=record.runtime_api_endpoint,
                    managed=record.managed,
                    pid=record.pid,
                    metadata=record.metadata,
                    extensions=record.extensions,
                )
        except Exception:
            self._states[record.instance_id] = RuntimeInstanceState.ERROR
            return record

    def _resolve_command_template(self, exec_config: RuntimeExecConfig, *, runtime_profile: str) -> list[str]:
        if exec_config.driver == "command":
            return list(exec_config.command_template or [])

        if exec_config.driver != "pip":
            raise RuntimeError(f"Unsupported exec driver: {exec_config.driver}")

        pip_spec = str(exec_config.pip_spec or "").strip()
        entrypoint = str(exec_config.entrypoint or "").strip()
        if not pip_spec or not entrypoint:
            raise RuntimeError(f"Invalid pip exec config for profile '{runtime_profile}'")

        venv_dir = self.config.data_dir / "venvs" / _safe_dirname(runtime_profile)
        venv_python = ensure_venv(venv_dir)
        pip_install(venv_python, pip_spec, pip_args=_pip_install_args(self.config), upgrade_pip=bool(self.config.pip_upgrade_pip))

        bin_dir = _venv_bin_dir(venv_dir)
        exe = f"{entrypoint}.exe" if os.name == "nt" else entrypoint
        entrypoint_path = bin_dir / exe
        if not entrypoint_path.exists():
            raise RuntimeError(f"Entrypoint not found after install: {entrypoint_path}")

        entrypoint_args = exec_config.entrypoint_args or ["serve"]
        return [str(entrypoint_path), *entrypoint_args, "--port", "{port}"]

    def list(self) -> list[InstanceRecord]:
        records: list[InstanceRecord] = []
        dirty = False
        for instance_id, record in list(self._managed.items()):
            process = self._processes.get(instance_id)
            if process is None:
                records.append(record)
                continue

            if process.poll() is not None:
                if self._states.get(instance_id) != RuntimeInstanceState.ERROR:
                    self._states[instance_id] = RuntimeInstanceState.ERROR
                    dirty = True

            if record.runtime_name != process.runtime_name or record.runtime_version != process.runtime_version:
                record = InstanceRecord(
                    instance_id=record.instance_id,
                    runtime_profile=record.runtime_profile,
                    runtime_name=process.runtime_name,
                    runtime_version=process.runtime_version,
                    runtime_api_endpoint=record.runtime_api_endpoint,
                    managed=record.managed,
                    pid=record.pid,
                    metadata=record.metadata,
                    extensions=record.extensions,
                )
                self._managed[instance_id] = record
                dirty = True

            records.append(record)

        records.extend(self._external.values())
        if dirty:
            self._persist()
        return records

    def get_state(self, instance_id: str) -> RuntimeInstanceState:
        return self._states.get(instance_id, RuntimeInstanceState.ERROR)

    def set_state(self, instance_id: str, state: RuntimeInstanceState) -> None:
        if instance_id in self._managed or instance_id in self._external:
            self._states[instance_id] = state
            self._persist()

    def delete(self, instance_id: str) -> None:
        process = self._processes.pop(instance_id, None)
        record = self._managed.get(instance_id) or self._external.get(instance_id)
        self._managed.pop(instance_id, None)
        self._external.pop(instance_id, None)
        self._states.pop(instance_id, None)
        if process is not None:
            process.stop(timeout_s=self.config.runtime_stop_timeout_s)
        elif record is not None and record.managed and record.pid is not None:
            _terminate_local_pid(record.runtime_api_endpoint, record.pid, timeout_s=self.config.runtime_stop_timeout_s)
        self._persist()

    def get(self, instance_id: str) -> InstanceRecord | None:
        record = self._managed.get(instance_id)
        if record is not None:
            return record
        return self._external.get(instance_id)

    def _persist(self) -> None:
        entries: list[tuple[InstanceRecord, RuntimeInstanceState]] = []
        for record in self._managed.values():
            entries.append((record, self.get_state(record.instance_id)))
        for record in self._external.values():
            entries.append((record, self.get_state(record.instance_id)))
        entries.sort(key=lambda item: item[0].instance_id)
        self._store.save(entries)


def _safe_dirname(value: str) -> str:
    value = value.strip()
    if not value:
        return "default"
    keep = []
    for ch in value:
        if ch.isalnum() or ch in ("-", "_", "."):
            keep.append(ch)
        else:
            keep.append("_")
    return "".join(keep)[:120]


def _pip_install_args(config: DaemonConfig) -> list[str]:
    args: list[str] = []
    if config.pip_no_index:
        args.append("--no-index")
    if config.pip_index_url:
        args.extend(["--index-url", str(config.pip_index_url)])
    for url in config.pip_extra_index_urls:
        args.extend(["--extra-index-url", str(url)])
    for host in config.pip_trusted_hosts:
        args.extend(["--trusted-host", str(host)])
    args.extend([str(x) for x in config.pip_install_args])
    return args


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(int(pid), 0)
    except Exception:
        return False
    return True


def _terminate_local_pid(runtime_api_endpoint: str, pid: int, *, timeout_s: float) -> None:
    try:
        parsed = urlparse(runtime_api_endpoint)
    except Exception:
        return
    host = (parsed.hostname or "").lower()
    if host not in {"127.0.0.1", "localhost", "::1"}:
        return

    try:
        os.kill(int(pid), signal.SIGTERM)
    except Exception:
        return

    deadline = time.time() + float(timeout_s)
    while time.time() < deadline:
        if not _pid_alive(pid):
            return
        time.sleep(0.05)
    sigkill = getattr(signal, "SIGKILL", None)
    try:
        if sigkill is not None:
            os.kill(int(pid), sigkill)
    except Exception:
        return
