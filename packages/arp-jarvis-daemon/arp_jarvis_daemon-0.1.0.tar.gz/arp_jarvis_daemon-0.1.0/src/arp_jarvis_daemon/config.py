from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence


@dataclass(slots=True)
class DaemonConfig:
    data_dir: Path = field(default_factory=lambda: Path.home() / ".arp" / "daemon")
    runtime_profiles_path: Path | None = None
    instances_path: Path | None = None
    allow_unsafe_runtime_profiles: bool = False
    virtual_runtime_instances: bool = False
    runtime_httpx_args: dict[str, Any] = field(default_factory=dict)
    pip_index_url: str | None = None
    pip_extra_index_urls: Sequence[str] = field(default_factory=tuple)
    pip_trusted_hosts: Sequence[str] = field(default_factory=tuple)
    pip_no_index: bool = False
    pip_upgrade_pip: bool = False
    pip_install_args: Sequence[str] = field(default_factory=tuple)
    runtime_command_template: Sequence[str] = field(
        default_factory=lambda: ("arp-jarvis-runtime", "serve", "--port", "{port}")
    )
    runtime_health_paths: Sequence[str] = ("/v1/health",)
    runtime_startup_timeout_s: float = 15.0
    runtime_health_poll_interval_s: float = 0.25
    runtime_request_timeout_s: float = 30.0
    runtime_stop_timeout_s: float = 5.0
    runtime_default_env: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.runtime_profiles_path is None:
            self.runtime_profiles_path = self.data_dir / "runtime_profiles.json"
        if self.instances_path is None:
            self.instances_path = self.data_dir / "instances.json"
