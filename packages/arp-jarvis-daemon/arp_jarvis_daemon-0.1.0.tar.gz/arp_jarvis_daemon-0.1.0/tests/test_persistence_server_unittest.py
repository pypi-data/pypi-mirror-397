from __future__ import annotations

import asyncio
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

import httpx

from arp_jarvis_daemon import DaemonConfig, DaemonCore
from arp_jarvis_daemon.server import create_app


def _runtime_stub_command() -> list[str]:
    code = "print('noop')"
    return [sys.executable, "-c", code, "{port}"]


class DaemonPersistenceTests(unittest.TestCase):
    def test_instances_persist_across_restart(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            asyncio.run(_exercise_persistence(Path(tmp)))


async def _exercise_persistence(tmp_path: Path) -> None:
    runs: dict[str, dict[str, object]] = {}

    def handler(request: httpx.Request) -> httpx.Response:
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
            status = {"run_id": run_id, "state": "succeeded", "started_at": "2025-01-01T00:00:00Z", "ended_at": "2025-01-01T00:00:00Z"}
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

    runtime_transport = httpx.MockTransport(handler)
    config = DaemonConfig(
        data_dir=tmp_path / "daemon",
        virtual_runtime_instances=True,
        runtime_httpx_args={"transport": runtime_transport},
        runtime_command_template=_runtime_stub_command(),
        runtime_startup_timeout_s=2.0,
    )
    core = DaemonCore(config=config)
    app = create_app(core=core)

    daemon_transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=daemon_transport, base_url="http://test") as client:
        upsert = await client.put(
            "/v1/admin/runtime-profiles/default",
            json={
                "runtime_name": "runtime-stub",
                "extensions": {"arp.jarvis.exec": {"driver": "command", "command_template": _runtime_stub_command()}},
            },
        )
        assert upsert.status_code == 200

        created = await client.post("/v1/instances", json={"runtime_profile": "default", "count": 1})
        assert created.status_code == 200
        created_instance_id = created.json()["instances"][0]["instance_id"]

        registered = await client.post(
            "/v1/instances:register",
            json={"runtime_api_endpoint": "http://external.runtime.local", "runtime_profile": "external"},
        )
        assert registered.status_code == 200
        external_instance_id = registered.json()["instance"]["instance_id"]

    restarted_config = DaemonConfig(
        data_dir=tmp_path / "daemon",
        virtual_runtime_instances=True,
        runtime_httpx_args={"transport": runtime_transport},
        runtime_command_template=_runtime_stub_command(),
    )
    restarted_core = DaemonCore(config=restarted_config)
    restarted_app = create_app(core=restarted_core)

    restarted_transport = httpx.ASGITransport(app=restarted_app)
    async with httpx.AsyncClient(transport=restarted_transport, base_url="http://test") as client:
        listed = await client.get("/v1/instances")
        assert listed.status_code == 200
        ids = {item.get("instance_id") for item in listed.json().get("instances", [])}
        assert created_instance_id in ids
        assert external_instance_id in ids
