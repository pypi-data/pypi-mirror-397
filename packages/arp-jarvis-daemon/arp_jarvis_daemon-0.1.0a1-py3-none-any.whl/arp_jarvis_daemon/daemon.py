from __future__ import annotations

import uuid
from dataclasses import dataclass, field

import httpx

from arp_sdk.daemon.models import (
    InstanceCreateRequest,
    InstanceCreateResponse,
    InstanceListResponse,
    RuntimeInstanceState,
    TraceResponse,
)
from arp_sdk.daemon.types import Unset as DaemonUnset
from arp_sdk.runtime import Client as RuntimeClient
from arp_sdk.runtime.api.default import (
    get_v1alpha2_runs_run_id,
    get_v1alpha2_runs_run_id_result,
    post_v1alpha2_runs,
)
from arp_sdk.runtime.models import (
    ErrorEnvelope as RuntimeErrorEnvelope,
    RunRequest,
    RunRequestRuntimeSelector,
    RunResult,
    RunStatus,
    RunStatusState,
)
from arp_sdk.runtime.types import Unset as RuntimeUnset

from .config import DaemonConfig
from .instance_manager import InstanceManager
from .run_router import RunRouter
from .run_store import RunStore
from .types import RunRecord


def _ensure_run_id(run_request: RunRequest) -> str:
    if isinstance(run_request.run_id, RuntimeUnset):
        # openapi-python-client uses an UNSET sentinel; avoid importing it here.
        run_request.run_id = f"run_{uuid.uuid4().hex[:12]}"
    return str(run_request.run_id)


def _merge_runtime_selector(run_request: RunRequest, *, instance_id: str, runtime_type: str, address: str) -> None:
    if isinstance(run_request.runtime_selector, RuntimeUnset):
        run_request.runtime_selector = RunRequestRuntimeSelector(
            instance_id=instance_id,
            runtime_type=runtime_type,
            address=address,
        )
        return

    selector = run_request.runtime_selector
    if isinstance(selector.instance_id, RuntimeUnset):
        selector.instance_id = instance_id
    if isinstance(selector.runtime_type, RuntimeUnset):
        selector.runtime_type = runtime_type
    if isinstance(selector.address, RuntimeUnset):
        selector.address = address


@dataclass(slots=True)
class DaemonCore:
    config: DaemonConfig
    _instances: InstanceManager = field(init=False)
    _router: RunRouter = field(init=False)
    _store: RunStore = field(init=False)

    def __post_init__(self) -> None:
        self.config.data_dir.mkdir(parents=True, exist_ok=True)
        self._instances = InstanceManager(config=self.config)
        self._router = RunRouter(instance_manager=self._instances)
        self._store = RunStore(root_dir=self.config.data_dir)

    def create_instances(self, request: InstanceCreateRequest) -> InstanceCreateResponse:
        env = {} if isinstance(request.env, DaemonUnset) else {k: str(v) for k, v in request.env.to_dict().items()}
        args = [] if isinstance(request.args, DaemonUnset) else list(request.args)
        runtime_type = None if isinstance(request.runtime_type, DaemonUnset) else str(request.runtime_type)
        count = 1 if isinstance(request.count, DaemonUnset) else int(request.count)
        created = self._instances.create(profile=request.profile, count=count, runtime_type=runtime_type, env=env, args=args)
        instances = []
        for record in created:
            state = self._instances.get_state(record.instance_id)
            instances.append(
                {
                    "instance_id": record.instance_id,
                    "state": str(state.value),
                    "runtime_type": record.runtime_type,
                    "runtime_api_base_url": record.runtime_api_base_url,
                    **({"runtime_version": record.runtime_version} if record.runtime_version else {}),
                }
            )
        payload = {"instances": instances}
        return InstanceCreateResponse.from_dict(payload)

    def list_instances(self) -> InstanceListResponse:
        instances = []
        for record in self._instances.list():
            state = self._instances.get_state(record.instance_id)
            instances.append({
                "instance_id": record.instance_id,
                "state": str(state.value),
                "runtime_type": record.runtime_type,
                "runtime_api_base_url": record.runtime_api_base_url,
                **({"runtime_version": record.runtime_version} if record.runtime_version else {}),
            })
        return InstanceListResponse.from_dict({"instances": instances})

    def delete_instance(self, instance_id: str) -> None:
        self._instances.delete(instance_id)

    def submit_run(self, run_request: RunRequest) -> RunStatus:
        run_id = _ensure_run_id(run_request)

        chosen = self._router.select_instance()
        if chosen is None:
            status = RunStatus(run_id=run_id, state=RunStatusState.QUEUED)
            self._store.write_request(run_id, run_request)
            self._store.write_status(run_id, status)
            self._store.write_index(RunRecord(run_id=run_id, instance_id=None, runtime_api_base_url=None))
            return status

        _merge_runtime_selector(
            run_request,
            instance_id=chosen.instance_id,
            runtime_type=chosen.runtime_type,
            address=chosen.runtime_api_base_url,
        )

        self._store.write_request(run_id, run_request)
        self._store.write_index(RunRecord(run_id=run_id, instance_id=chosen.instance_id, runtime_api_base_url=chosen.runtime_api_base_url))

        self._instances.set_state(chosen.instance_id, RuntimeInstanceState.BUSY)
        try:
            client = RuntimeClient(
                base_url=chosen.runtime_api_base_url, timeout=httpx.Timeout(self.config.runtime_request_timeout_s)
            )
            created = post_v1alpha2_runs.sync(client=client, body=run_request)
            if created is None:
                raise RuntimeError("Runtime POST /runs returned no response")
            if isinstance(created, RuntimeErrorEnvelope):
                raise RuntimeError(f"Runtime error: {created.error.message if created.error else created.to_dict()}")
            if isinstance(created.runtime_instance_id, RuntimeUnset):
                created.runtime_instance_id = chosen.instance_id
            self._store.write_status(run_id, created)

            if created.state in (RunStatusState.SUCCEEDED, RunStatusState.FAILED, RunStatusState.CANCELED):
                result = get_v1alpha2_runs_run_id_result.sync(run_id=run_id, client=client)
                if isinstance(result, RuntimeErrorEnvelope):
                    raise RuntimeError(f"Runtime error fetching result: {result.error.message if result.error else result.to_dict()}")
                if result is not None:
                    self._store.write_result(run_id, result)
            return created
        finally:
            self._instances.set_state(chosen.instance_id, RuntimeInstanceState.READY)

    def get_run_status(self, run_id: str) -> RunStatus:
        stored = self._store.read_status(run_id)
        if stored is not None:
            return stored

        record = self._store.read_index(run_id)
        if record is None or not record.runtime_api_base_url:
            raise FileNotFoundError(f"Unknown run_id: {run_id}")

        client = RuntimeClient(base_url=record.runtime_api_base_url, timeout=httpx.Timeout(self.config.runtime_request_timeout_s))
        status = get_v1alpha2_runs_run_id.sync(run_id=run_id, client=client)
        if status is None:
            raise RuntimeError("Runtime GET /runs/{id} returned no response")
        if isinstance(status, RuntimeErrorEnvelope):
            raise RuntimeError(f"Runtime error: {status.error.message if status.error else status.to_dict()}")
        self._store.write_status(run_id, status)
        return status

    def get_run_result(self, run_id: str) -> RunResult:
        stored = self._store.read_result(run_id)
        if stored is not None:
            return stored

        record = self._store.read_index(run_id)
        if record is None or not record.runtime_api_base_url:
            raise FileNotFoundError(f"Unknown run_id: {run_id}")

        client = RuntimeClient(base_url=record.runtime_api_base_url, timeout=httpx.Timeout(self.config.runtime_request_timeout_s))
        result = get_v1alpha2_runs_run_id_result.sync(run_id=run_id, client=client)
        if result is None:
            raise RuntimeError("Runtime GET /runs/{id}/result returned no response")
        if isinstance(result, RuntimeErrorEnvelope):
            raise RuntimeError(f"Runtime error: {result.error.message if result.error else result.to_dict()}")
        self._store.write_result(run_id, result)
        return result

    def get_run_trace(self, run_id: str) -> TraceResponse:
        trace_uri = self._store.read_trace_pointer(run_id)
        if trace_uri:
            return TraceResponse(trace_uri=trace_uri)

        # Default to a deterministic on-disk location even if empty; callers can decide how to handle.
        trace_path = self.config.data_dir / "runs" / run_id / "trace.jsonl"
        if trace_path.exists():
            return TraceResponse(trace_uri=trace_path.as_uri())

        return TraceResponse()
