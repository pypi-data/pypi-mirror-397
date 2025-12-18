from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from arp_sdk.daemon.models.instance_create_request import InstanceCreateRequest
from arp_sdk.runtime.models.run_request import RunRequest
from arp_sdk.runtime.models.run_request_input import RunRequestInput

from arp_jarvis_daemon import DaemonConfig, DaemonCore


def _runtime_stub_command() -> list[str]:
    # Minimal in-process HTTP server exposing the ARP Runtime surface for tests.
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
        if p in ('/v1alpha2/health', '/v1alpha1/health'):
            return self._send(200, {'status':'ok','time':_now(),'checks':[]})
        if p in ('/v1alpha2/version', '/v1alpha1/version'):
            return self._send(200, {'service_name':'runtime-stub','service_version':'0.0.0','supported_api_versions':['v1alpha2']})
        if p.startswith('/v1alpha2/runs/') and p.endswith('/result'):
            run_id = p.split('/')[3]
            return self._send(200, runs[run_id]['result'])
        if p.startswith('/v1alpha2/runs/'):
            run_id = p.split('/')[3]
            return self._send(200, runs[run_id]['status'])
        return self._send(404, {'error':'not found'})

    def do_POST(self):
        p = urlparse(self.path).path
        if p == '/v1alpha2/runs':
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


class DaemonCoreTests(unittest.TestCase):
    def test_create_instances_and_submit_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "daemon"
            config = DaemonConfig(
                data_dir=data_dir,
                runtime_command_template=_runtime_stub_command(),
                runtime_startup_timeout_s=5.0,
            )
            core = DaemonCore(config=config)

            create_resp = core.create_instances(InstanceCreateRequest(profile="default", count=1))
            self.assertEqual(1, len(create_resp.instances))
            instance_id = create_resp.instances[0].instance_id
            self.assertEqual("0.0.0", create_resp.instances[0].runtime_version)

            run_req = RunRequest(input_=RunRequestInput(goal="hello"))
            status = core.submit_run(run_req)
            self.assertEqual("succeeded", status.state.value)

            result = core.get_run_result(status.run_id)
            self.assertTrue(result.ok)
            core.delete_instance(instance_id)


if __name__ == "__main__":
    raise SystemExit(unittest.main())
