from __future__ import annotations

import os
import socket
import subprocess
import time
from dataclasses import dataclass
from typing import Mapping, Sequence

import httpx


def allocate_local_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _format_command(template: Sequence[str], *, port: int, extra_args: Sequence[str]) -> list[str]:
    formatted = [part.replace("{port}", str(port)) for part in template]
    return [*formatted, *extra_args]


def _merged_env(*, base_env: Mapping[str, str], override_env: Mapping[str, str]) -> dict[str, str]:
    env = dict(os.environ)
    env.update({str(k): str(v) for k, v in base_env.items()})
    env.update({str(k): str(v) for k, v in override_env.items()})
    # Back-compat convenience: if CP passes the generic ARP var, also provide the current Jarvis var.
    if "ARP_TOOL_REGISTRY_URL" in env and "JARVIS_TOOL_REGISTRY_URL" not in env:
        env["JARVIS_TOOL_REGISTRY_URL"] = env["ARP_TOOL_REGISTRY_URL"]
    return env


@dataclass(slots=True)
class RuntimeProcess:
    instance_id: str
    runtime_type: str
    runtime_version: str | None
    port: int
    api_base_url: str
    popen: subprocess.Popen[str] | None = None

    @classmethod
    def spawn(
        cls,
        *,
        instance_id: str,
        runtime_type: str,
        runtime_version: str | None,
        command_template: Sequence[str],
        extra_args: Sequence[str],
        base_env: Mapping[str, str],
        env: Mapping[str, str],
    ) -> "RuntimeProcess":
        port = allocate_local_port()
        api_base_url = f"http://127.0.0.1:{port}"
        cmd = _format_command(command_template, port=port, extra_args=extra_args)
        merged_env = _merged_env(base_env=base_env, override_env=env)
        popen = subprocess.Popen(cmd, env=merged_env, text=True)
        return cls(
            instance_id=instance_id,
            runtime_type=runtime_type,
            runtime_version=runtime_version,
            port=port,
            api_base_url=api_base_url,
            popen=popen,
        )

    @property
    def pid(self) -> int | None:
        return None if self.popen is None else int(self.popen.pid)

    def poll(self) -> int | None:
        return None if self.popen is None else self.popen.poll()

    def wait_for_health(
        self,
        *,
        health_paths: Sequence[str],
        timeout_s: float,
        poll_interval_s: float,
    ) -> str:
        deadline = time.time() + timeout_s
        last_exc: Exception | None = None
        with httpx.Client(timeout=2.0) as client:
            while time.time() < deadline:
                if self.popen is not None and self.popen.poll() is not None:
                    raise RuntimeError(f"Runtime process exited early (pid={self.pid}, code={self.popen.returncode})")
                for path in health_paths:
                    try:
                        resp = client.get(f"{self.api_base_url}{path}")
                        if resp.status_code == 200:
                            return path
                    except Exception as exc:  # noqa: BLE001 - used for retry loop
                        last_exc = exc
                time.sleep(poll_interval_s)
        raise TimeoutError(f"Runtime did not become healthy within {timeout_s}s (last_error={last_exc})")

    def try_fetch_version_info(self, *, version_path: str, timeout_s: float = 2.0) -> tuple[str | None, str | None]:
        try:
            with httpx.Client(timeout=timeout_s) as client:
                resp = client.get(f"{self.api_base_url}{version_path}")
                if resp.status_code != 200:
                    return None, None
                data = resp.json()
        except Exception:
            return None, None

        if not isinstance(data, dict):
            return None, None

        service_name = data.get("service_name")
        service_version = data.get("service_version")
        return (service_name if isinstance(service_name, str) else None, service_version if isinstance(service_version, str) else None)

    def stop(self, *, timeout_s: float) -> None:
        if self.popen is None:
            return
        try:
            self.popen.terminate()
            self.popen.wait(timeout=timeout_s)
        except subprocess.TimeoutExpired:
            self.popen.kill()
            self.popen.wait(timeout=timeout_s)
        finally:
            if self.popen.stdout is not None:
                self.popen.stdout.close()
            if self.popen.stderr is not None:
                self.popen.stderr.close()
            self.popen = None
