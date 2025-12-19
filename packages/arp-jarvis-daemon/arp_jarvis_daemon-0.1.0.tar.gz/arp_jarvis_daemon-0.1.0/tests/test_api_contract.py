import asyncio
import json
import tempfile
import unittest
import warnings
from pathlib import Path
from typing import Any

import httpx

from arp_jarvis_daemon import DaemonConfig, DaemonCore
from arp_jarvis_daemon.server import create_app

try:  # optional, used for schema validation tests
    import jsonschema  # type: ignore
except Exception:  # pragma: no cover
    jsonschema = None


def _arp_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _standard_schemas_root() -> Path:
    return _arp_root() / "ARP_Standard" / "spec" / "v1" / "schemas"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_against_schema(*, schema_rel: str, instance: Any) -> list[str]:
    if jsonschema is None:  # pragma: no cover
        raise RuntimeError("jsonschema is not installed")

    schema_path = _standard_schemas_root() / schema_rel
    schema = _load_json(schema_path)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        resolver = jsonschema.RefResolver(base_uri=schema_path.as_uri(), referrer=schema)
    validator = jsonschema.Draft7Validator(schema, resolver=resolver)

    errors = sorted(validator.iter_errors(instance), key=lambda exc: list(exc.path))
    rendered: list[str] = []
    for err in errors:
        location = "/".join(str(p) for p in err.path) or "<root>"
        rendered.append(f"{location}: {err.message}")
    return rendered


class TestDaemonApiContract(unittest.TestCase):
    def test_responses_validate_against_standard_schemas(self) -> None:
        if jsonschema is None:
            self.skipTest("jsonschema not installed")

        asyncio.run(_exercise_and_validate())


async def _exercise_and_validate() -> None:
    runs: dict[str, dict[str, object]] = {}

    def runtime_handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if request.method == "GET" and path == "/v1/health":
            return httpx.Response(200, json={"status": "ok", "time": "2025-01-01T00:00:00Z", "checks": []})
        if request.method == "GET" and path == "/v1/version":
            return httpx.Response(
                200,
                json={"service_name": "runtime-mock", "service_version": "0.0.0", "supported_api_versions": ["v1"]},
            )
        if request.method == "POST" and path == "/v1/runs":
            body = json.loads(request.content.decode("utf-8") or "{}")
            run_id = body.get("run_id") or "run_123"
            status = {
                "run_id": run_id,
                "state": "succeeded",
                "started_at": "2025-01-01T00:00:00Z",
                "ended_at": "2025-01-01T00:00:00Z",
            }
            result = {"run_id": run_id, "ok": True, "output": {"echo_goal": body.get("input", {}).get("goal")}}
            runs[run_id] = {"status": status, "result": result}
            return httpx.Response(200, json=status)
        if request.method == "GET" and path.startswith("/v1/runs/") and path.endswith("/result"):
            run_id = path.split("/")[3]
            return httpx.Response(200, json=runs[run_id]["result"])
        if request.method == "GET" and path.startswith("/v1/runs/"):
            run_id = path.split("/")[3]
            return httpx.Response(200, json=runs[run_id]["status"])
        return httpx.Response(404, json={"error": {"code": "not_found", "message": "not found"}})

    runtime_transport = httpx.MockTransport(runtime_handler)
    with tempfile.TemporaryDirectory() as tmp:
        config = DaemonConfig(
            data_dir=Path(tmp) / "daemon",
            virtual_runtime_instances=True,
            runtime_httpx_args={"transport": runtime_transport},
            runtime_startup_timeout_s=1.0,
        )
        core = DaemonCore(config=config)
        app = create_app(core=core)

        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            health = await client.get("/v1/health")
            assert health.status_code == 200
            assert _validate_against_schema(schema_rel="common/health.schema.json", instance=health.json()) == []
            version = await client.get("/v1/version")
            assert version.status_code == 200
            assert _validate_against_schema(schema_rel="common/version_info.schema.json", instance=version.json()) == []

            unknown_profile = await client.post("/v1/instances", json={"runtime_profile": "missing", "count": 1})
            assert unknown_profile.status_code == 400
            assert _validate_against_schema(schema_rel="common/error.schema.json", instance=unknown_profile.json()) == []

            upsert = await client.put(
                "/v1/admin/runtime-profiles/default",
                json={
                    "runtime_name": "runtime-stub",
                    "extensions": {
                        "arp.jarvis.exec": {
                            "driver": "command",
                            "command_template": [str(Path(__file__).resolve()), "{port}"],
                        }
                    },
                },
            )
            assert upsert.status_code == 200
            assert (
                _validate_against_schema(schema_rel="daemon/runtime_profiles/runtime_profile.schema.json", instance=upsert.json())
                == []
            )

            profiles = await client.get("/v1/admin/runtime-profiles")
            assert profiles.status_code == 200
            assert (
                _validate_against_schema(
                    schema_rel="daemon/runtime_profiles/runtime_profile_list_response.schema.json", instance=profiles.json()
                )
                == []
            )

            created = await client.post("/v1/instances", json={"runtime_profile": "default", "count": 1})
            assert created.status_code == 200
            assert (
                _validate_against_schema(
                    schema_rel="daemon/instances/instance_create_response.schema.json", instance=created.json()
                )
                == []
            )
            instance_id = created.json()["instances"][0]["instance_id"]

            listed_instances = await client.get("/v1/instances")
            assert listed_instances.status_code == 200
            assert (
                _validate_against_schema(schema_rel="daemon/instances/instance_list_response.schema.json", instance=listed_instances.json())
                == []
            )

            registered = await client.post(
                "/v1/instances:register",
                json={"runtime_api_endpoint": "http://external.runtime.local", "runtime_profile": "external"},
            )
            assert registered.status_code == 200
            assert (
                _validate_against_schema(
                    schema_rel="daemon/instances/instance_register_response.schema.json", instance=registered.json()
                )
                == []
            )

            submitted = await client.post("/v1/runs", json={"input": {"goal": "hello"}})
            assert submitted.status_code == 202
            assert _validate_against_schema(schema_rel="daemon/runs/run_status.schema.json", instance=submitted.json()) == []
            run_id = submitted.json()["run_id"]

            status = await client.get(f"/v1/runs/{run_id}")
            assert status.status_code == 200
            assert _validate_against_schema(schema_rel="daemon/runs/run_status.schema.json", instance=status.json()) == []

            result = await client.get(f"/v1/runs/{run_id}/result")
            assert result.status_code == 200
            assert _validate_against_schema(schema_rel="daemon/runs/run_result.schema.json", instance=result.json()) == []

            trace = await client.get(f"/v1/runs/{run_id}/trace")
            assert trace.status_code == 200
            assert _validate_against_schema(schema_rel="daemon/runs/trace_response.schema.json", instance=trace.json()) == []

            listed = await client.get("/v1/runs")
            assert listed.status_code == 200
            assert _validate_against_schema(schema_rel="daemon/runs/run_list_response.schema.json", instance=listed.json()) == []

            deleted = await client.delete(f"/v1/instances/{instance_id}")
            assert deleted.status_code == 204
