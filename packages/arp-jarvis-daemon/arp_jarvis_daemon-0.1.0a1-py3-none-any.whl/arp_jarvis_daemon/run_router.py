from __future__ import annotations

from dataclasses import dataclass, field

from arp_sdk.daemon.models.runtime_instance_state import RuntimeInstanceState

from .instance_manager import InstanceManager
from .types import InstanceRecord


@dataclass(slots=True)
class RunRouter:
    instance_manager: InstanceManager
    _rr_index: int = 0
    _rr_order: list[str] = field(default_factory=list)

    def select_instance(self) -> InstanceRecord | None:
        instances = self.instance_manager.list()
        ready = [inst for inst in instances if self.instance_manager.get_state(inst.instance_id) == RuntimeInstanceState.READY]
        if not ready:
            return None

        ready_ids = [inst.instance_id for inst in ready]
        if ready_ids != self._rr_order:
            self._rr_order = ready_ids
            self._rr_index = 0

        chosen_id = self._rr_order[self._rr_index % len(self._rr_order)]
        self._rr_index = (self._rr_index + 1) % len(self._rr_order)
        return next(inst for inst in ready if inst.instance_id == chosen_id)

