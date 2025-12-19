from __future__ import annotations

from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version as package_version
from typing import Any

from fastapi import Body, FastAPI, Query, Response
from fastapi.responses import JSONResponse

from arp_sdk.daemon.models import InstanceCreateRequest, InstanceRegisterRequest, RuntimeProfileUpsertRequest
from arp_sdk.runtime.models import RunRequest

from .config import DaemonConfig
from .daemon import DaemonCore
from .errors import DaemonApiError


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _service_version() -> str:
    try:
        return package_version("arp-jarvis-daemon")
    except PackageNotFoundError:
        return "0.0.0"


def _error_envelope(*, code: str, message: str, details: Any | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    return payload


def create_app(*, core: DaemonCore | None = None, config: DaemonConfig | None = None) -> FastAPI:
    if core is None:
        core = DaemonCore(config=config or DaemonConfig())

    app = FastAPI(title="ARP Jarvis Daemon", version=_service_version())

    @app.get("/v1/health")
    def health() -> dict[str, Any]:
        return {"status": "ok", "time": _utc_now_iso(), "checks": []}

    @app.get("/v1/version")
    def version() -> dict[str, Any]:
        return {
            "service_name": "arp-jarvis-daemon",
            "service_version": _service_version(),
            "supported_api_versions": ["v1"],
        }

    @app.get("/v1/instances")
    def list_instances() -> dict[str, Any]:
        return core.list_instances().to_dict()

    @app.post("/v1/instances")
    def create_instances(body: dict[str, Any] = Body(...)) -> JSONResponse:
        try:
            request = InstanceCreateRequest.from_dict(body)
        except Exception as exc:  # noqa: BLE001 - parse errors to API envelope
            return JSONResponse(
                status_code=400,
                content=_error_envelope(code="bad_request", message="Invalid InstanceCreateRequest", details={"error": str(exc)}),
            )

        try:
            response = core.create_instances(request)
        except DaemonApiError as exc:
            return JSONResponse(status_code=int(exc.status_code), content=_error_envelope(code=exc.code, message=exc.message, details=exc.details))
        except ValueError as exc:
            return JSONResponse(status_code=400, content=_error_envelope(code="bad_request", message=str(exc)))
        except Exception as exc:  # noqa: BLE001 - surface core errors
            return JSONResponse(
                status_code=500,
                content=_error_envelope(code="internal_error", message=str(exc)),
            )

        return JSONResponse(status_code=200, content=response.to_dict())

    @app.delete("/v1/instances/{instance_id}")
    def delete_instance(instance_id: str) -> Response:
        core.delete_instance(instance_id)
        return Response(status_code=204)

    @app.post("/v1/instances:register")
    def register_instance(body: dict[str, Any] = Body(...)) -> JSONResponse:
        try:
            request = InstanceRegisterRequest.from_dict(body)
        except Exception as exc:  # noqa: BLE001 - parse errors to API envelope
            return JSONResponse(
                status_code=400,
                content=_error_envelope(code="bad_request", message="Invalid InstanceRegisterRequest", details={"error": str(exc)}),
            )

        try:
            response = core.register_instance(request)
        except DaemonApiError as exc:
            return JSONResponse(status_code=int(exc.status_code), content=_error_envelope(code=exc.code, message=exc.message, details=exc.details))
        except ValueError as exc:
            return JSONResponse(status_code=400, content=_error_envelope(code="bad_request", message=str(exc)))
        except Exception as exc:  # noqa: BLE001 - surface core errors
            return JSONResponse(
                status_code=500,
                content=_error_envelope(code="internal_error", message=str(exc)),
            )

        return JSONResponse(status_code=200, content=response.to_dict())

    @app.get("/v1/admin/runtime-profiles")
    def list_runtime_profiles() -> dict[str, Any]:
        return core.list_runtime_profiles().to_dict()

    @app.put("/v1/admin/runtime-profiles/{runtime_profile}")
    def upsert_runtime_profile(runtime_profile: str, body: dict[str, Any] = Body(...)) -> JSONResponse:
        try:
            request = RuntimeProfileUpsertRequest.from_dict(body)
        except Exception as exc:  # noqa: BLE001 - parse errors to API envelope
            return JSONResponse(
                status_code=400,
                content=_error_envelope(code="bad_request", message="Invalid RuntimeProfileUpsertRequest", details={"error": str(exc)}),
            )

        try:
            profile = core.upsert_runtime_profile(runtime_profile, request)
        except DaemonApiError as exc:
            return JSONResponse(status_code=int(exc.status_code), content=_error_envelope(code=exc.code, message=exc.message, details=exc.details))
        except ValueError as exc:
            return JSONResponse(status_code=400, content=_error_envelope(code="bad_request", message=str(exc)))
        except Exception as exc:  # noqa: BLE001 - surface core errors
            return JSONResponse(
                status_code=500,
                content=_error_envelope(code="internal_error", message=str(exc)),
            )

        return JSONResponse(status_code=200, content=profile.to_dict())

    @app.delete("/v1/admin/runtime-profiles/{runtime_profile}")
    def delete_runtime_profile(runtime_profile: str) -> Response:
        core.delete_runtime_profile(runtime_profile)
        return Response(status_code=204)

    @app.get("/v1/runs")
    def list_runs(
        page_size: int | None = Query(default=None, ge=1, le=1000),
        page_token: str | None = Query(default=None),
    ) -> dict[str, Any]:
        return core.list_runs(page_size=page_size, page_token=page_token).to_dict()

    @app.post("/v1/runs")
    def submit_run(body: dict[str, Any] = Body(...)) -> JSONResponse:
        try:
            request = RunRequest.from_dict(body)
        except Exception as exc:  # noqa: BLE001 - parse errors to API envelope
            return JSONResponse(
                status_code=400,
                content=_error_envelope(code="bad_request", message="Invalid RunRequest", details={"error": str(exc)}),
            )

        try:
            status = core.submit_run(request)
        except DaemonApiError as exc:
            return JSONResponse(status_code=int(exc.status_code), content=_error_envelope(code=exc.code, message=exc.message, details=exc.details))
        except ValueError as exc:
            return JSONResponse(status_code=400, content=_error_envelope(code="bad_request", message=str(exc)))
        except Exception as exc:  # noqa: BLE001 - surface core errors
            return JSONResponse(
                status_code=500,
                content=_error_envelope(code="internal_error", message=str(exc)),
            )

        return JSONResponse(status_code=202, content=status.to_dict())

    @app.get("/v1/runs/{run_id}")
    def get_run_status(run_id: str) -> JSONResponse:
        try:
            status = core.get_run_status(run_id)
        except FileNotFoundError as exc:
            return JSONResponse(status_code=404, content=_error_envelope(code="not_found", message=str(exc)))
        except Exception as exc:  # noqa: BLE001 - surface core errors
            return JSONResponse(status_code=500, content=_error_envelope(code="internal_error", message=str(exc)))
        return JSONResponse(status_code=200, content=status.to_dict())

    @app.get("/v1/runs/{run_id}/result")
    def get_run_result(run_id: str) -> JSONResponse:
        try:
            result = core.get_run_result(run_id)
        except FileNotFoundError as exc:
            return JSONResponse(status_code=404, content=_error_envelope(code="not_found", message=str(exc)))
        except Exception as exc:  # noqa: BLE001 - surface core errors
            return JSONResponse(status_code=500, content=_error_envelope(code="internal_error", message=str(exc)))
        return JSONResponse(status_code=200, content=result.to_dict())

    @app.get("/v1/runs/{run_id}/trace")
    def get_run_trace(run_id: str) -> JSONResponse:
        try:
            trace = core.get_run_trace(run_id)
        except Exception as exc:  # noqa: BLE001 - surface core errors
            return JSONResponse(status_code=500, content=_error_envelope(code="internal_error", message=str(exc)))
        return JSONResponse(status_code=200, content=trace.to_dict())

    return app
