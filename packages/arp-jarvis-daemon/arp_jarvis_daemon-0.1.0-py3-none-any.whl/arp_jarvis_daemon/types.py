from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class InstanceRecord:
    instance_id: str
    runtime_profile: str | None
    runtime_name: str | None
    runtime_version: str | None
    runtime_api_endpoint: str
    managed: bool
    pid: int | None = None
    metadata: dict[str, Any] | None = None
    extensions: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class RunRecord:
    run_id: str
    instance_id: str | None
    runtime_api_endpoint: str | None
