from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class InstanceRecord:
    instance_id: str
    runtime_type: str
    runtime_version: str | None
    runtime_api_base_url: str
    pid: int | None


@dataclass(frozen=True, slots=True)
class RunRecord:
    run_id: str
    instance_id: str | None
    runtime_api_base_url: str | None

