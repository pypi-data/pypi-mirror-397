from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class DaemonApiError(Exception):
    code: str
    message: str
    status_code: int = 400
    details: Any | None = None

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.code}: {self.message}"

