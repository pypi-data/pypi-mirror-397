from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from arp_sdk.runtime.models.run_request import RunRequest
from arp_sdk.runtime.models.run_result import RunResult
from arp_sdk.runtime.models.run_status import RunStatus

from .types import RunRecord


def _atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass(slots=True)
class RunStore:
    root_dir: Path

    def run_dir(self, run_id: str) -> Path:
        return self.root_dir / "runs" / run_id

    def write_index(self, record: RunRecord) -> None:
        _atomic_write_json(self.run_dir(record.run_id) / "run.json", {
            "run_id": record.run_id,
            "instance_id": record.instance_id,
            "runtime_api_base_url": record.runtime_api_base_url,
        })

    def read_index(self, run_id: str) -> RunRecord | None:
        path = self.run_dir(run_id) / "run.json"
        if not path.exists():
            return None
        data = _read_json(path)
        return RunRecord(
            run_id=str(data.get("run_id") or run_id),
            instance_id=data.get("instance_id"),
            runtime_api_base_url=data.get("runtime_api_base_url"),
        )

    def write_request(self, run_id: str, request: RunRequest) -> None:
        _atomic_write_json(self.run_dir(run_id) / "request.json", request.to_dict())

    def write_status(self, run_id: str, status: RunStatus) -> None:
        _atomic_write_json(self.run_dir(run_id) / "status.json", status.to_dict())

    def read_status(self, run_id: str) -> RunStatus | None:
        path = self.run_dir(run_id) / "status.json"
        if not path.exists():
            return None
        return RunStatus.from_dict(_read_json(path))

    def write_result(self, run_id: str, result: RunResult) -> None:
        _atomic_write_json(self.run_dir(run_id) / "result.json", result.to_dict())

    def read_result(self, run_id: str) -> RunResult | None:
        path = self.run_dir(run_id) / "result.json"
        if not path.exists():
            return None
        return RunResult.from_dict(_read_json(path))

    def write_trace_pointer(self, run_id: str, trace_uri: str) -> None:
        _atomic_write_json(self.run_dir(run_id) / "trace_pointer.json", {"trace_uri": trace_uri})

    def read_trace_pointer(self, run_id: str) -> str | None:
        path = self.run_dir(run_id) / "trace_pointer.json"
        if not path.exists():
            return None
        data = _read_json(path)
        uri = data.get("trace_uri")
        return uri if isinstance(uri, str) else None

