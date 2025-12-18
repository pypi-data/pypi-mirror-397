from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Sequence


@dataclass(slots=True)
class DaemonConfig:
    data_dir: Path = field(default_factory=lambda: Path.home() / ".arp" / "daemon")
    runtime_command_template: Sequence[str] = field(
        default_factory=lambda: ("arp-jarvis-runtime", "serve", "--port", "{port}")
    )
    runtime_health_paths: Sequence[str] = ("/v1alpha2/health", "/v1alpha1/health")
    runtime_startup_timeout_s: float = 15.0
    runtime_health_poll_interval_s: float = 0.25
    runtime_request_timeout_s: float = 30.0
    runtime_stop_timeout_s: float = 5.0
    runtime_default_env: Mapping[str, str] = field(default_factory=dict)

