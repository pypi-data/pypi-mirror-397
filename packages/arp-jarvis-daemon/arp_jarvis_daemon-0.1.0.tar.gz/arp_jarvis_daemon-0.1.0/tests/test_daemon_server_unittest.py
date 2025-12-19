from __future__ import annotations

import asyncio
import json
import sys
import tempfile
import time
import unittest
from pathlib import Path
from typing import Any

import httpx

from arp_jarvis_daemon import DaemonConfig, DaemonCore
from arp_jarvis_daemon.server import create_app


def _runtime_stub_command() -> list[str]:
    code = r"""
import json, sys, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

runs = {}

def _now():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

class H(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        b = json.dumps(obj).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        p = urlparse(self.path).path
        if p == '/v1/health':
            return self._send(200, {'status':'ok','time':_now(),'checks':[]})
        if p == '/v1/version':
            return self._send(200, {'service_name':'runtime-stub','service_version':'0.0.0','supported_api_versions':['v1']})
        if p.startswith('/v1/runs/') and p.endswith('/result'):
            run_id = p.split('/')[3]
            return self._send(200, runs[run_id]['result'])
        if p.startswith('/v1/runs/'):
            run_id = p.split('/')[3]
            return self._send(200, runs[run_id]['status'])
        return self._send(404, {'error':'not found'})

    def do_POST(self):
        p = urlparse(self.path).path
        if p == '/v1/runs':
            n = int(self.headers.get('Content-Length','0'))
            body = json.loads(self.rfile.read(n) or b'{}')
            run_id = body.get('run_id') or 'run_123'
            status = {'run_id': run_id, 'state': 'succeeded', 'started_at': _now(), 'ended_at': _now()}
            result = {'run_id': run_id, 'ok': True, 'output': {'echo_goal': body.get('input',{}).get('goal')}}
            runs[run_id] = {'status': status, 'result': result}
            return self._send(200, status)
        return self._send(404, {'error':'not found'})

    def log_message(self, fmt, *args):
        pass

port = int(sys.argv[1])
HTTPServer(('127.0.0.1', port), H).serve_forever()
"""
    return [sys.executable, "-c", code, "{port}"]


class DaemonServerTests(unittest.TestCase):
    def test_server_endpoints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "daemon"
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

            transport = httpx.MockTransport(handler)
            config = DaemonConfig(
                data_dir=data_dir,
                virtual_runtime_instances=True,
                runtime_httpx_args={"transport": transport},
                runtime_command_template=_runtime_stub_command(),
                runtime_startup_timeout_s=5.0,
            )
            core = DaemonCore(config=config)
            app = create_app(core=core)

            asyncio.run(_exercise_server(app))


async def _exercise_server(app: Any) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        health = await client.get("/v1/health")
        assert health.status_code == 200
        assert health.json().get("status") == "ok"

        version = await client.get("/v1/version")
        assert version.status_code == 200
        assert "v1" in version.json().get("supported_api_versions", [])

        no_instances = await client.post("/v1/runs", json={"input": {"goal": "hello"}})
        assert no_instances.status_code == 404
        assert "error" in no_instances.json()

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
        instance_id = created.json()["instances"][0]["instance_id"]

        submitted = await client.post("/v1/runs", json={"input": {"goal": "hello"}})
        assert submitted.status_code == 202
        run_id = submitted.json()["run_id"]

        result: httpx.Response | None = None
        for _ in range(50):
            candidate = await client.get(f"/v1/runs/{run_id}/result")
            if candidate.status_code == 200:
                result = candidate
                break
            await asyncio.sleep(0.05)

        assert result is not None
        assert result.json().get("ok") is True

        listed = await client.get("/v1/runs")
        assert listed.status_code == 200
        assert any(item.get("run_id") == run_id for item in listed.json().get("runs", []))

        deleted = await client.delete(f"/v1/instances/{instance_id}")
        assert deleted.status_code == 204


if __name__ == "__main__":
    raise SystemExit(unittest.main())
