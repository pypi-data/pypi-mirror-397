from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from arp_sdk.daemon.models.instance_create_request import InstanceCreateRequest
from arp_sdk.runtime.models.run_request import RunRequest

from .config import DaemonConfig
from .daemon import DaemonCore


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="arp-jarvis-daemon")
    parser.add_argument("--data-dir", type=Path, default=None)
    sub = parser.add_subparsers(dest="cmd", required=True)

    start = sub.add_parser("start", help="Create local runtime instances")
    start.add_argument("--profile", default="default")
    start.add_argument("--count", type=int, default=1)

    ls = sub.add_parser("list", help="List runtime instances")

    rm = sub.add_parser("delete", help="Delete a runtime instance")
    rm.add_argument("instance_id")

    run = sub.add_parser("run", help="Submit a run request (JSON)")
    run.add_argument("--request-json", required=True, help="JSON file path containing a RunRequest")

    status = sub.add_parser("status", help="Get run status")
    status.add_argument("run_id")

    result = sub.add_parser("result", help="Get run result")
    result.add_argument("run_id")

    args = parser.parse_args(argv)

    config = DaemonConfig()
    if args.data_dir is not None:
        config.data_dir = args.data_dir

    core = DaemonCore(config=config)

    if args.cmd == "start":
        req = InstanceCreateRequest(profile=args.profile, count=args.count)
        resp = core.create_instances(req)
        print(json.dumps(resp.to_dict(), indent=2, sort_keys=True))
        return 0

    if args.cmd == "list":
        resp = core.list_instances()
        print(json.dumps(resp.to_dict(), indent=2, sort_keys=True))
        return 0

    if args.cmd == "delete":
        core.delete_instance(args.instance_id)
        return 0

    if args.cmd == "run":
        request_path = Path(args.request_json)
        payload = json.loads(request_path.read_text(encoding="utf-8"))
        run_request = RunRequest.from_dict(payload)
        status_obj = core.submit_run(run_request)
        print(json.dumps(status_obj.to_dict(), indent=2, sort_keys=True))
        return 0

    if args.cmd == "status":
        status_obj = core.get_run_status(args.run_id)
        print(json.dumps(status_obj.to_dict(), indent=2, sort_keys=True))
        return 0

    if args.cmd == "result":
        result_obj = core.get_run_result(args.run_id)
        print(json.dumps(result_obj.to_dict(), indent=2, sort_keys=True))
        return 0

    print(f"Unknown command: {args.cmd}", file=sys.stderr)
    return 2

