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

    def select_instance(
        self,
        *,
        instance_id: str | None = None,
        runtime_profile: str | None = None,
        runtime_name: str | None = None,
    ) -> InstanceRecord | None:
        if instance_id:
            record = self.instance_manager.get(instance_id)
            if record is None:
                return None
            if self.instance_manager.get_state(record.instance_id) != RuntimeInstanceState.READY:
                return None
            return record

        instances = self.instance_manager.list()
        ready = [inst for inst in instances if self.instance_manager.get_state(inst.instance_id) == RuntimeInstanceState.READY]
        if runtime_profile:
            ready = [inst for inst in ready if inst.runtime_profile == runtime_profile]
        if runtime_name:
            ready = [inst for inst in ready if inst.runtime_name == runtime_name]
        if not ready:
            return None

        ready_ids = [inst.instance_id for inst in ready]
        if ready_ids != self._rr_order:
            self._rr_order = ready_ids
            self._rr_index = 0

        chosen_id = self._rr_order[self._rr_index % len(self._rr_order)]
        self._rr_index = (self._rr_index + 1) % len(self._rr_order)
        return next(inst for inst in ready if inst.instance_id == chosen_id)
