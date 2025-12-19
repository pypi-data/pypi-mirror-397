from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from arp_sdk.daemon.models.runtime_instance_state import RuntimeInstanceState

from .types import InstanceRecord


def _atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _coerce_state(value: Any) -> RuntimeInstanceState:
    if isinstance(value, RuntimeInstanceState):
        return value
    if isinstance(value, str):
        try:
            return RuntimeInstanceState(value)
        except ValueError:
            return RuntimeInstanceState.ERROR
    return RuntimeInstanceState.ERROR


@dataclass(slots=True)
class InstanceStore:
    path: Path

    def load(self) -> list[tuple[InstanceRecord, RuntimeInstanceState]]:
        if not self.path.exists():
            return []
        raw = _read_json(self.path)
        items = raw.get("instances") if isinstance(raw, dict) else raw
        if not isinstance(items, list):
            return []

        loaded: list[tuple[InstanceRecord, RuntimeInstanceState]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            instance_id = item.get("instance_id")
            runtime_api_endpoint = item.get("runtime_api_endpoint")
            if not isinstance(instance_id, str) or not instance_id.strip():
                continue
            if not isinstance(runtime_api_endpoint, str) or not runtime_api_endpoint.strip():
                continue

            state = _coerce_state(item.get("state"))

            managed = item.get("managed")
            managed_bool = bool(managed) if managed is not None else True

            pid = item.get("pid")
            pid_int = int(pid) if isinstance(pid, int) else None

            runtime_profile = item.get("runtime_profile")
            runtime_name = item.get("runtime_name")
            runtime_version = item.get("runtime_version")
            metadata = item.get("metadata")
            extensions = item.get("extensions")
            loaded.append(
                (
                    InstanceRecord(
                        instance_id=instance_id.strip(),
                        runtime_profile=runtime_profile if isinstance(runtime_profile, str) else None,
                        runtime_name=runtime_name if isinstance(runtime_name, str) else None,
                        runtime_version=runtime_version if isinstance(runtime_version, str) else None,
                        runtime_api_endpoint=runtime_api_endpoint.strip(),
                        managed=managed_bool,
                        pid=pid_int,
                        metadata=metadata if isinstance(metadata, dict) else None,
                        extensions=extensions if isinstance(extensions, dict) else None,
                    ),
                    state,
                )
            )
        return loaded

    def save(self, entries: list[tuple[InstanceRecord, RuntimeInstanceState]]) -> None:
        payload: list[dict[str, Any]] = []
        for record, state in entries:
            item: dict[str, Any] = {
                "instance_id": record.instance_id,
                "state": str(state.value),
                "managed": bool(record.managed),
                "runtime_api_endpoint": record.runtime_api_endpoint,
            }
            if record.runtime_profile:
                item["runtime_profile"] = record.runtime_profile
            if record.runtime_name:
                item["runtime_name"] = record.runtime_name
            if record.runtime_version:
                item["runtime_version"] = record.runtime_version
            if record.pid is not None:
                item["pid"] = int(record.pid)
            if record.metadata:
                item["metadata"] = record.metadata
            if record.extensions:
                item["extensions"] = record.extensions
            payload.append(item)

        _atomic_write_json(self.path, {"instances": payload})

