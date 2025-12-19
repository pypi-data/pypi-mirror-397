from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import httpx

from arp_sdk.errors import ArpApiError
from arp_sdk.daemon.models import (
    InstanceCreateRequest,
    InstanceCreateResponse,
    InstanceListResponse,
    InstanceRegisterRequest,
    InstanceRegisterResponse,
    RunListResponse,
    RuntimeProfile,
    RuntimeProfileListResponse,
    RuntimeProfileUpsertRequest,
    RuntimeInstanceState,
    TraceResponse,
    TraceResponseTraceEvent,
)
from arp_sdk.daemon.types import Unset as DaemonUnset
from arp_sdk.runtime import RuntimeClient
from arp_sdk.runtime.models import (
    RunRequest,
    RunRequestRuntimeSelector,
    RunResult,
    RunStatus,
    RunStatusState,
)
from arp_sdk.runtime.types import Unset as RuntimeUnset

from .config import DaemonConfig
from .errors import DaemonApiError
from .instance_manager import InstanceManager
from .run_router import RunRouter
from .run_store import RunStore
from .runtime_profiles import RuntimeProfileStore
from .types import RunRecord


def _ensure_run_id(run_request: RunRequest) -> str:
    if isinstance(run_request.run_id, RuntimeUnset):
        # openapi-python-client uses an UNSET sentinel; avoid importing it here.
        run_request.run_id = f"run_{uuid.uuid4().hex[:12]}"
    return str(run_request.run_id)


def _merge_runtime_selector(
    run_request: RunRequest,
    *,
    instance_id: str | None,
    runtime_profile: str | None,
    runtime_name: str | None,
    runtime_api_endpoint: str,
) -> None:
    if isinstance(run_request.runtime_selector, RuntimeUnset):
        kwargs: dict[str, Any] = {"runtime_api_endpoint": runtime_api_endpoint}
        if instance_id is not None:
            kwargs["instance_id"] = instance_id
        if runtime_profile is not None:
            kwargs["runtime_profile"] = runtime_profile
        if runtime_name is not None:
            kwargs["runtime_name"] = runtime_name
        run_request.runtime_selector = RunRequestRuntimeSelector(**kwargs)
        return

    selector = run_request.runtime_selector
    if instance_id is not None and isinstance(selector.instance_id, RuntimeUnset):
        selector.instance_id = instance_id
    if runtime_profile is not None and isinstance(selector.runtime_profile, RuntimeUnset):
        selector.runtime_profile = runtime_profile
    if runtime_name is not None and isinstance(selector.runtime_name, RuntimeUnset):
        selector.runtime_name = runtime_name
    if isinstance(selector.runtime_api_endpoint, RuntimeUnset):
        selector.runtime_api_endpoint = runtime_api_endpoint


@dataclass(slots=True)
class DaemonCore:
    config: DaemonConfig
    _instances: InstanceManager = field(init=False)
    _router: RunRouter = field(init=False)
    _store: RunStore = field(init=False)
    _profiles: RuntimeProfileStore = field(init=False)

    def __post_init__(self) -> None:
        self.config.data_dir.mkdir(parents=True, exist_ok=True)
        self._instances = InstanceManager(config=self.config)
        self._router = RunRouter(instance_manager=self._instances)
        self._store = RunStore(root_dir=self.config.data_dir)
        profiles_path = self.config.runtime_profiles_path or (self.config.data_dir / "runtime_profiles.json")
        self._profiles = RuntimeProfileStore(path=profiles_path)

    def create_instances(self, request: InstanceCreateRequest) -> InstanceCreateResponse:
        count = 1 if isinstance(request.count, DaemonUnset) else int(request.count)

        metadata: dict[str, Any] | None = None
        if not isinstance(request.metadata, DaemonUnset):
            metadata = request.metadata.to_dict()

        extensions: dict[str, Any] | None = None
        if not isinstance(request.extensions, DaemonUnset):
            extensions = request.extensions.to_dict()

        overrides_env: dict[str, str] = {}
        overrides_args: list[str] = []
        tool_registry_url: str | None = None
        if not isinstance(request.overrides, DaemonUnset):
            if not isinstance(request.overrides.env, DaemonUnset):
                overrides_env = {k: str(v) for k, v in request.overrides.env.to_dict().items()}
            if not isinstance(request.overrides.args, DaemonUnset):
                overrides_args = [str(x) for x in list(request.overrides.args)]
            if not isinstance(request.overrides.tool_registry_url, DaemonUnset):
                tool_registry_url = str(request.overrides.tool_registry_url)

        if tool_registry_url:
            overrides_env.setdefault("ARP_TOOL_REGISTRY_URL", tool_registry_url)

        profile = self._profiles.get(request.runtime_profile)
        if profile is None:
            if not self.config.allow_unsafe_runtime_profiles:
                raise ValueError(f"Unknown runtime_profile: {request.runtime_profile}")
            profile = RuntimeProfile.from_dict(
                {
                    "runtime_profile": request.runtime_profile,
                    "extensions": {
                        "arp.jarvis.exec": {
                            "driver": "command",
                            "command_template": list(self.config.runtime_command_template),
                        }
                    },
                }
            )

        created = self._instances.create_managed(
            profile=profile,
            count=count,
            env=overrides_env,
            args=overrides_args,
            metadata=metadata,
            extensions=extensions,
        )

        instances = []
        for record in created:
            state = self._instances.get_state(record.instance_id)
            instance: dict[str, Any] = {
                "instance_id": record.instance_id,
                "state": str(state.value),
                "managed": bool(record.managed),
                "runtime_api_endpoint": record.runtime_api_endpoint,
            }
            if record.runtime_profile:
                instance["runtime_profile"] = record.runtime_profile
            if record.runtime_name:
                instance["runtime_name"] = record.runtime_name
            if record.runtime_version:
                instance["runtime_version"] = record.runtime_version
            if record.metadata:
                instance["metadata"] = record.metadata
            if record.extensions:
                instance["extensions"] = record.extensions
            instances.append(instance)

        return InstanceCreateResponse.from_dict({"instances": instances})

    def list_instances(self) -> InstanceListResponse:
        instances = []
        for record in self._instances.list():
            state = self._instances.get_state(record.instance_id)
            instance: dict[str, Any] = {
                "instance_id": record.instance_id,
                "state": str(state.value),
                "managed": bool(record.managed),
                "runtime_api_endpoint": record.runtime_api_endpoint,
            }
            if record.runtime_profile:
                instance["runtime_profile"] = record.runtime_profile
            if record.runtime_name:
                instance["runtime_name"] = record.runtime_name
            if record.runtime_version:
                instance["runtime_version"] = record.runtime_version
            if record.metadata:
                instance["metadata"] = record.metadata
            if record.extensions:
                instance["extensions"] = record.extensions
            instances.append(instance)
        return InstanceListResponse.from_dict({"instances": instances})

    def delete_instance(self, instance_id: str) -> None:
        self._instances.delete(instance_id)

    def register_instance(self, request: InstanceRegisterRequest) -> InstanceRegisterResponse:
        metadata: dict[str, Any] | None = None
        if not isinstance(request.metadata, DaemonUnset):
            metadata = request.metadata.to_dict()

        extensions: dict[str, Any] | None = None
        if not isinstance(request.extensions, DaemonUnset):
            extensions = request.extensions.to_dict()

        runtime_profile = None if isinstance(request.runtime_profile, DaemonUnset) else str(request.runtime_profile)
        runtime_name = None if isinstance(request.runtime_name, DaemonUnset) else str(request.runtime_name)

        record = self._instances.register_external(
            runtime_api_endpoint=str(request.runtime_api_endpoint),
            runtime_profile=runtime_profile,
            runtime_name=runtime_name,
            metadata=metadata,
            extensions=extensions,
        )
        state = self._instances.get_state(record.instance_id)
        payload: dict[str, Any] = {
            "instance": {
                "instance_id": record.instance_id,
                "state": str(state.value),
                "managed": False,
                "runtime_api_endpoint": record.runtime_api_endpoint,
            }
        }
        if record.runtime_profile:
            payload["instance"]["runtime_profile"] = record.runtime_profile
        if record.runtime_name:
            payload["instance"]["runtime_name"] = record.runtime_name
        if record.runtime_version:
            payload["instance"]["runtime_version"] = record.runtime_version
        if record.metadata:
            payload["instance"]["metadata"] = record.metadata
        if record.extensions:
            payload["instance"]["extensions"] = record.extensions
        return InstanceRegisterResponse.from_dict(payload)

    def list_runtime_profiles(self) -> RuntimeProfileListResponse:
        return self._profiles.list_profiles()

    def upsert_runtime_profile(self, runtime_profile: str, request: RuntimeProfileUpsertRequest) -> RuntimeProfile:
        return self._profiles.upsert(runtime_profile, request)

    def delete_runtime_profile(self, runtime_profile: str) -> None:
        self._profiles.delete(runtime_profile)

    def submit_run(self, run_request: RunRequest) -> RunStatus:
        run_id = _ensure_run_id(run_request)

        selector = None if isinstance(run_request.runtime_selector, RuntimeUnset) else run_request.runtime_selector
        target_instance_id = None
        runtime_profile = None
        runtime_name = None
        runtime_api_endpoint = None
        if selector is not None:
            if not isinstance(selector.instance_id, RuntimeUnset):
                target_instance_id = str(selector.instance_id)
            if not isinstance(selector.runtime_profile, RuntimeUnset):
                runtime_profile = str(selector.runtime_profile)
            if not isinstance(selector.runtime_name, RuntimeUnset):
                runtime_name = str(selector.runtime_name)
            if not isinstance(selector.runtime_api_endpoint, RuntimeUnset):
                runtime_api_endpoint = str(selector.runtime_api_endpoint)

        if runtime_api_endpoint and (target_instance_id or runtime_profile or runtime_name):
            raise DaemonApiError(
                code="bad_request",
                message="runtime_selector cannot combine runtime_api_endpoint with instance_id/runtime_profile/runtime_name",
                status_code=400,
            )

        chosen = None
        if runtime_api_endpoint:
            chosen = None
        elif target_instance_id:
            record = self._instances.get(target_instance_id)
            if record is None:
                raise DaemonApiError(code="instances.not_found", message=f"Unknown instance_id: {target_instance_id}", status_code=404)
            state = self._instances.get_state(record.instance_id)
            if state != RuntimeInstanceState.READY:
                raise DaemonApiError(
                    code="instances.not_ready",
                    message=f"Instance is not ready: {record.instance_id}",
                    status_code=409,
                    details={"state": str(state.value)},
                )
            chosen = record
        elif runtime_api_endpoint:
            chosen = None
        else:
            chosen = self._router.select_instance(instance_id=None, runtime_profile=runtime_profile, runtime_name=runtime_name)
            if chosen is None:
                instances = self._instances.list()
                matched = instances
                if runtime_profile:
                    matched = [inst for inst in matched if inst.runtime_profile == runtime_profile]
                if runtime_name:
                    matched = [inst for inst in matched if inst.runtime_name == runtime_name]
                if not matched:
                    raise DaemonApiError(
                        code="instances.not_found",
                        message="No runtime instances match the requested selector",
                        status_code=404,
                        details={"runtime_profile": runtime_profile, "runtime_name": runtime_name},
                    )
                raise DaemonApiError(
                    code="instances.no_ready",
                    message="No ready runtime instances are available for the requested selector",
                    status_code=409,
                    details={"runtime_profile": runtime_profile, "runtime_name": runtime_name},
                )

        selected_instance_id = target_instance_id
        selected_runtime_profile = runtime_profile
        selected_runtime_name = runtime_name
        selected_runtime_api_endpoint = runtime_api_endpoint.rstrip("/") if runtime_api_endpoint else chosen.runtime_api_endpoint  # type: ignore[union-attr]
        if chosen is not None:
            selected_instance_id = chosen.instance_id
            selected_runtime_profile = chosen.runtime_profile
            selected_runtime_name = chosen.runtime_name

        _merge_runtime_selector(
            run_request,
            instance_id=selected_instance_id,
            runtime_profile=selected_runtime_profile,
            runtime_name=selected_runtime_name,
            runtime_api_endpoint=selected_runtime_api_endpoint,
        )

        self._store.write_request(run_id, run_request)
        self._store.write_index(RunRecord(run_id=run_id, instance_id=selected_instance_id, runtime_api_endpoint=selected_runtime_api_endpoint))

        if chosen is not None and chosen.managed:
            self._instances.set_state(chosen.instance_id, RuntimeInstanceState.BUSY)
        try:
            client = RuntimeClient(
                base_url=selected_runtime_api_endpoint,
                timeout=httpx.Timeout(self.config.runtime_request_timeout_s),
                httpx_args=self.config.runtime_httpx_args,
            )
            try:
                created = client.create_run(run_request)
            except ArpApiError as exc:
                raise RuntimeError(f"Runtime error: {exc.code}: {exc.message}") from exc
            if selected_instance_id is not None and isinstance(created.runtime_instance_id, RuntimeUnset):
                created.runtime_instance_id = selected_instance_id
            self._store.write_status(run_id, created)

            if created.state in (RunStatusState.SUCCEEDED, RunStatusState.FAILED, RunStatusState.CANCELED):
                try:
                    result = client.get_run_result(run_id)
                except ArpApiError as exc:
                    raise RuntimeError(f"Runtime error fetching result: {exc.code}: {exc.message}") from exc
                self._store.write_result(run_id, result)
            return created
        finally:
            if chosen is not None and chosen.managed:
                self._instances.set_state(chosen.instance_id, RuntimeInstanceState.READY)

    def get_run_status(self, run_id: str) -> RunStatus:
        stored = self._store.read_status(run_id)
        if stored is not None:
            return stored

        record = self._store.read_index(run_id)
        if record is None or not record.runtime_api_endpoint:
            raise FileNotFoundError(f"Unknown run_id: {run_id}")

        client = RuntimeClient(
            base_url=record.runtime_api_endpoint,
            timeout=httpx.Timeout(self.config.runtime_request_timeout_s),
            httpx_args=self.config.runtime_httpx_args,
        )
        try:
            status = client.get_run_status(run_id)
        except ArpApiError as exc:
            raise RuntimeError(f"Runtime error: {exc.code}: {exc.message}") from exc
        self._store.write_status(run_id, status)
        return status

    def get_run_result(self, run_id: str) -> RunResult:
        stored = self._store.read_result(run_id)
        if stored is not None:
            return stored

        record = self._store.read_index(run_id)
        if record is None or not record.runtime_api_endpoint:
            raise FileNotFoundError(f"Unknown run_id: {run_id}")

        client = RuntimeClient(
            base_url=record.runtime_api_endpoint,
            timeout=httpx.Timeout(self.config.runtime_request_timeout_s),
            httpx_args=self.config.runtime_httpx_args,
        )
        try:
            result = client.get_run_result(run_id)
        except ArpApiError as exc:
            raise RuntimeError(f"Runtime error: {exc.code}: {exc.message}") from exc
        self._store.write_result(run_id, result)
        return result

    def get_run_trace(self, run_id: str) -> TraceResponse:
        trace_uri = self._store.read_trace_pointer(run_id)
        trace_path = self.config.data_dir / "runs" / run_id / "trace.jsonl"
        if trace_path.exists():
            events: list[TraceResponseTraceEvent] = []
            seq = 0
            try:
                with trace_path.open("r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            raw = json.loads(line)
                        except Exception:
                            continue
                        if not isinstance(raw, dict):
                            continue

                        ts = raw.get("ts")
                        if not isinstance(ts, str) or not ts.strip():
                            ts = datetime.now(timezone.utc).isoformat()

                        event_type = raw.get("type")
                        if not isinstance(event_type, str) or not event_type.strip():
                            event_type = "trace"

                        level = "info"
                        if event_type.endswith("failed") or event_type.endswith("error") or "error" in raw or raw.get("status") == "failed":
                            level = "error"

                        data = dict(raw)
                        data.pop("ts", None)
                        data.pop("type", None)

                        events.append(
                            TraceResponseTraceEvent.from_dict(
                                {
                                    "run_id": run_id,
                                    "seq": seq,
                                    "time": ts,
                                    "level": level,
                                    "type": event_type,
                                    "data": data,
                                }
                            )
                        )
                        seq += 1
            except Exception:
                events = []

            return TraceResponse(events=events, trace_uri=trace_uri or trace_path.absolute().as_uri())

        if trace_uri:
            return TraceResponse(trace_uri=trace_uri)

        return TraceResponse()

    def list_runs(self, *, page_size: int | None = None, page_token: str | None = None) -> RunListResponse:
        runs, next_page_token = self._store.list_statuses_paginated(page_size=page_size, page_token=page_token)

        payload: dict[str, Any] = {"runs": [run.to_dict() for run in runs]}

        pagination: dict[str, Any] = {}
        if next_page_token is not None:
            pagination["next_page_token"] = next_page_token
        if page_size is not None:
            pagination["page_size"] = int(page_size)
        if pagination:
            payload["pagination"] = pagination

        return RunListResponse.from_dict(payload)
