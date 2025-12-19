from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from arp_sdk.daemon.models import RuntimeProfile, RuntimeProfileListResponse, RuntimeProfileUpsertRequest
from arp_sdk.daemon.types import UNSET, Unset

_EXEC_EXTENSION_KEY = "arp.jarvis.exec"


@dataclass(frozen=True, slots=True)
class RuntimeExecConfig:
    driver: str
    pip_spec: str | None = None
    entrypoint: str | None = None
    entrypoint_args: list[str] | None = None
    command_template: list[str] | None = None


def _atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _coerce_extensions(value: Any | Unset) -> dict[str, Any]:
    if isinstance(value, Unset):
        return {}
    if hasattr(value, "to_dict"):
        return value.to_dict()  # type: ignore[no-any-return]
    if isinstance(value, dict):
        return value
    return {}


def _is_pinned_pip_spec(pip_spec: str) -> bool:
    spec = pip_spec.strip()
    if not spec:
        return False
    if spec.startswith(("/", "./", "../")) or spec.startswith("file://"):
        return True
    if "@" in spec:
        return True
    return "==" in spec


def parse_exec_config(profile: RuntimeProfile) -> RuntimeExecConfig:
    payload = _coerce_extensions(profile.extensions).get(_EXEC_EXTENSION_KEY)
    if not isinstance(payload, dict):
        raise ValueError(f"Runtime profile '{profile.runtime_profile}' is missing required extensions['{_EXEC_EXTENSION_KEY}'] object")

    driver = payload.get("driver") or "pip"
    if not isinstance(driver, str) or not driver.strip():
        raise ValueError(f"Runtime profile '{profile.runtime_profile}' has invalid exec driver")
    driver = driver.strip()

    if driver == "pip":
        pip_spec = payload.get("pip_spec")
        entrypoint = payload.get("entrypoint")
        if not isinstance(pip_spec, str) or not pip_spec.strip():
            raise ValueError(f"Runtime profile '{profile.runtime_profile}' is missing exec pip_spec")
        if pip_spec.lstrip().startswith("-"):
            raise ValueError(f"Runtime profile '{profile.runtime_profile}' has invalid exec pip_spec (must not start with '-')")
        if not _is_pinned_pip_spec(pip_spec):
            raise ValueError(
                f"Runtime profile '{profile.runtime_profile}' has unpinned exec pip_spec; use 'pkg==version', a local path, or 'name @ file:///...'"
            )
        if not isinstance(entrypoint, str) or not entrypoint.strip():
            raise ValueError(f"Runtime profile '{profile.runtime_profile}' is missing exec entrypoint")
        entrypoint_args = payload.get("entrypoint_args")
        if entrypoint_args is None:
            entrypoint_args_list: list[str] = ["serve"]
        elif isinstance(entrypoint_args, list) and all(isinstance(x, str) for x in entrypoint_args):
            entrypoint_args_list = [str(x) for x in entrypoint_args]
        else:
            raise ValueError(f"Runtime profile '{profile.runtime_profile}' has invalid exec entrypoint_args")
        return RuntimeExecConfig(
            driver="pip",
            pip_spec=pip_spec.strip(),
            entrypoint=entrypoint.strip(),
            entrypoint_args=entrypoint_args_list,
        )

    if driver == "command":
        command_template = payload.get("command_template")
        if not isinstance(command_template, list) or not command_template or not all(isinstance(x, str) for x in command_template):
            raise ValueError(f"Runtime profile '{profile.runtime_profile}' is missing exec command_template")
        return RuntimeExecConfig(driver="command", command_template=[str(x) for x in command_template])

    raise ValueError(f"Runtime profile '{profile.runtime_profile}' has unsupported exec driver '{driver}'")


@dataclass(slots=True)
class RuntimeProfileStore:
    path: Path

    def list_profiles(self) -> RuntimeProfileListResponse:
        profiles = sorted(self._load_all(), key=lambda p: p.runtime_profile)
        return RuntimeProfileListResponse.from_dict({"profiles": [p.to_dict() for p in profiles]})

    def get(self, runtime_profile: str) -> RuntimeProfile | None:
        for profile in self._load_all():
            if profile.runtime_profile == runtime_profile:
                return profile
        return None

    def upsert(self, runtime_profile: str, request: RuntimeProfileUpsertRequest) -> RuntimeProfile:
        payload = request.to_dict()
        payload["runtime_profile"] = runtime_profile
        profile = RuntimeProfile.from_dict(payload)
        parse_exec_config(profile)

        profiles = [p for p in self._load_all() if p.runtime_profile != runtime_profile]
        profiles.append(profile)
        self._save_all(profiles)
        return profile

    def delete(self, runtime_profile: str) -> None:
        profiles = [p for p in self._load_all() if p.runtime_profile != runtime_profile]
        self._save_all(profiles)

    def _load_all(self) -> list[RuntimeProfile]:
        if not self.path.exists():
            return []
        raw = _read_json(self.path)
        if isinstance(raw, dict) and isinstance(raw.get("profiles"), list):
            items = raw["profiles"]
        elif isinstance(raw, list):
            items = raw
        else:
            items = []

        profiles: list[RuntimeProfile] = []
        for item in items:
            if isinstance(item, dict):
                try:
                    profiles.append(RuntimeProfile.from_dict(item))
                except Exception:
                    continue
        return profiles

    def _save_all(self, profiles: list[RuntimeProfile]) -> None:
        _atomic_write_json(self.path, {"profiles": [p.to_dict() for p in sorted(profiles, key=lambda p: p.runtime_profile)]})
