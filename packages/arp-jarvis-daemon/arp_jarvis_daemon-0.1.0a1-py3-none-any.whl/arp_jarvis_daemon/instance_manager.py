from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Mapping

from arp_sdk.daemon.models.runtime_instance_state import RuntimeInstanceState

from .config import DaemonConfig
from .runtime_process import RuntimeProcess
from .types import InstanceRecord


@dataclass(slots=True)
class InstanceManager:
    config: DaemonConfig
    _processes: dict[str, RuntimeProcess] = field(default_factory=dict)
    _states: dict[str, RuntimeInstanceState] = field(default_factory=dict)

    def create(
        self,
        *,
        profile: str,
        count: int,
        runtime_type: str | None,
        env: Mapping[str, str],
        args: list[str],
    ) -> list[InstanceRecord]:
        requested_runtime_type = runtime_type
        runtime_type = requested_runtime_type or profile
        created: list[InstanceRecord] = []
        for _ in range(count):
            instance_id = f"inst_{uuid.uuid4().hex[:10]}"
            self._states[instance_id] = RuntimeInstanceState.STARTING
            process = RuntimeProcess.spawn(
                instance_id=instance_id,
                runtime_type=runtime_type,
                runtime_version=None,
                command_template=self.config.runtime_command_template,
                extra_args=args,
                base_env=self.config.runtime_default_env,
                env=env,
            )
            self._processes[instance_id] = process
            health_path = process.wait_for_health(
                health_paths=self.config.runtime_health_paths,
                timeout_s=self.config.runtime_startup_timeout_s,
                poll_interval_s=self.config.runtime_health_poll_interval_s,
            )
            version_path = health_path.replace("/health", "/version")
            service_name, service_version = process.try_fetch_version_info(version_path=version_path)
            if requested_runtime_type is None and service_name:
                process.runtime_type = service_name
            if service_version:
                process.runtime_version = service_version
            self._states[instance_id] = RuntimeInstanceState.READY
            created.append(
                InstanceRecord(
                    instance_id=instance_id,
                    runtime_type=process.runtime_type,
                    runtime_version=process.runtime_version,
                    runtime_api_base_url=process.api_base_url,
                    pid=process.pid,
                )
            )
        return created

    def list(self) -> list[InstanceRecord]:
        records: list[InstanceRecord] = []
        for instance_id, process in self._processes.items():
            state = self._states.get(instance_id, RuntimeInstanceState.ERROR)
            if process.poll() is not None:
                state = RuntimeInstanceState.ERROR
                self._states[instance_id] = state
            records.append(
                InstanceRecord(
                    instance_id=instance_id,
                    runtime_type=process.runtime_type,
                    runtime_version=process.runtime_version,
                    runtime_api_base_url=process.api_base_url,
                    pid=process.pid,
                )
            )
        return records

    def get_state(self, instance_id: str) -> RuntimeInstanceState:
        return self._states.get(instance_id, RuntimeInstanceState.ERROR)

    def set_state(self, instance_id: str, state: RuntimeInstanceState) -> None:
        if instance_id in self._processes:
            self._states[instance_id] = state

    def delete(self, instance_id: str) -> None:
        process = self._processes.pop(instance_id, None)
        self._states.pop(instance_id, None)
        if process is not None:
            process.stop(timeout_s=self.config.runtime_stop_timeout_s)

    def get(self, instance_id: str) -> InstanceRecord | None:
        process = self._processes.get(instance_id)
        if process is None:
            return None
        return InstanceRecord(
            instance_id=instance_id,
            runtime_type=process.runtime_type,
            runtime_version=process.runtime_version,
            runtime_api_base_url=process.api_base_url,
            pid=process.pid,
        )
