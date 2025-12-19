from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import httpx

from arp_sdk.daemon import DaemonClient, UpsertRuntimeProfileRequest
from arp_sdk.daemon.models import InstanceCreateRequest, InstanceRegisterRequest, RuntimeProfileUpsertRequest
from arp_sdk.runtime.models.run_request import RunRequest

from .config import DaemonConfig
from .daemon import DaemonCore


def main(argv: list[str] | None = None) -> int:
    args_list = sys.argv[1:] if argv is None else list(argv)
    if not args_list or args_list[0].startswith("-"):
        return _cmd_serve(args_list)
    if args_list[0] == "serve":
        return _cmd_serve(args_list[1:])
    return _cmd_client(args_list)


def _cmd_serve(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="arp-jarvis-daemon", description="Run the ARP Jarvis Daemon HTTP API server.")
    parser.add_argument("--data-dir", type=Path, default=None)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8082)
    parser.add_argument("--log-level", default=os.getenv("LOG_LEVEL", "info"))
    parser.add_argument("--allow-unsafe-runtime-profiles", action="store_true", help="Allow creating instances from unknown profiles.")

    parser.add_argument("--pip-index-url", default=None)
    parser.add_argument("--pip-extra-index-url", action="append", default=[])
    parser.add_argument("--pip-trusted-host", action="append", default=[])
    parser.add_argument("--pip-no-index", action="store_true")
    parser.add_argument("--pip-upgrade-pip", action="store_true")
    parser.add_argument("--pip-arg", action="append", default=[], help="Extra pip install arg (repeatable)")

    args = parser.parse_args(argv)

    config_kwargs: dict[str, object] = {
        "allow_unsafe_runtime_profiles": bool(args.allow_unsafe_runtime_profiles),
        "pip_index_url": args.pip_index_url,
        "pip_extra_index_urls": tuple(args.pip_extra_index_url),
        "pip_trusted_hosts": tuple(args.pip_trusted_host),
        "pip_no_index": bool(args.pip_no_index),
        "pip_upgrade_pip": bool(args.pip_upgrade_pip),
        "pip_install_args": tuple(args.pip_arg),
    }
    if args.data_dir is not None:
        config_kwargs["data_dir"] = args.data_dir

    config = DaemonConfig(**config_kwargs)  # type: ignore[arg-type]
    core = DaemonCore(config=config)

    from .server import create_app

    try:
        import uvicorn  # type: ignore
    except Exception as exc:  # pragma: no cover
        print(f"Missing server dependencies. Install with: python -m pip install fastapi uvicorn\n{exc}", file=sys.stderr)
        return 2

    app = create_app(core=core)
    uvicorn.run(app, host=args.host, port=args.port, log_level=args.log_level)
    return 0


def _cmd_client(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="arp-jarvis-daemon", description="CLI client for a running ARP Jarvis Daemon server.")
    parser.add_argument(
        "--daemon-url",
        default=os.getenv("ARP_DAEMON_URL") or os.getenv("JARVIS_DAEMON_URL") or "http://127.0.0.1:8082",
        help="Daemon base URL (default: $ARP_DAEMON_URL or http://127.0.0.1:8082)",
    )
    parser.add_argument("--timeout", type=float, default=30.0)
    sub = parser.add_subparsers(dest="cmd", required=True)

    start = sub.add_parser("start", help="Create runtime instances via the daemon server")
    start.add_argument("--runtime-profile", default="default")
    start.add_argument("--count", type=int, default=1)
    start.add_argument("--tool-registry-url", default=None)
    start.add_argument("--env", action="append", default=[], help="KEY=VALUE (repeatable)")
    start.add_argument("--arg", action="append", default=[], help="Extra runtime CLI arg (repeatable)")

    sub.add_parser("list", help="List runtime instances via the daemon server")

    register = sub.add_parser("register", help="Register an external runtime endpoint (unmanaged)")
    register.add_argument("--runtime-api-endpoint", required=True)
    register.add_argument("--runtime-profile", default=None)
    register.add_argument("--runtime-name", default=None)

    rm = sub.add_parser("delete", help="Delete a runtime instance (managed) or deregister (external)")
    rm.add_argument("instance_id")

    profiles = sub.add_parser("runtime-profiles", help="Manage runtime profiles (safe list)")
    profiles_sub = profiles.add_subparsers(dest="profiles_cmd", required=True)
    profiles_sub.add_parser("list", help="List runtime profiles")
    profiles_upsert = profiles_sub.add_parser("upsert", help="Upsert a runtime profile from JSON")
    profiles_upsert.add_argument("runtime_profile")
    profiles_upsert.add_argument("--request-json", required=True, help="JSON file path containing a RuntimeProfileUpsertRequest")
    profiles_delete = profiles_sub.add_parser("delete", help="Delete a runtime profile")
    profiles_delete.add_argument("runtime_profile")

    run = sub.add_parser("run", help="Submit a run request (JSON)")
    run.add_argument("--request-json", required=True, help="JSON file path containing a RunRequest")

    runs_ls = sub.add_parser("runs", help="List runs")
    runs_ls.add_argument("--page-size", type=int, default=None)
    runs_ls.add_argument("--page-token", default=None)

    status = sub.add_parser("status", help="Get run status")
    status.add_argument("run_id")

    result = sub.add_parser("result", help="Get run result")
    result.add_argument("run_id")

    trace = sub.add_parser("trace", help="Get run trace")
    trace.add_argument("run_id")

    args = parser.parse_args(argv)

    client = DaemonClient(base_url=str(args.daemon_url).rstrip("/"), timeout=httpx.Timeout(float(args.timeout)))

    if args.cmd == "start":
        env: dict[str, str] = {}
        for item in args.env:
            if "=" not in item:
                raise SystemExit(f"Invalid --env value (expected KEY=VALUE): {item}")
            k, v = item.split("=", 1)
            env[k] = v

        payload: dict[str, object] = {"runtime_profile": args.runtime_profile, "count": int(args.count)}
        overrides: dict[str, object] = {}
        if env:
            overrides["env"] = env
        if args.arg:
            overrides["args"] = list(args.arg)
        if args.tool_registry_url:
            overrides["tool_registry_url"] = str(args.tool_registry_url)
        if overrides:
            payload["overrides"] = overrides

        req = InstanceCreateRequest.from_dict(payload)
        resp = client.create_instances(req)
        print(json.dumps(resp.to_dict(), indent=2, sort_keys=True))
        return 0

    if args.cmd == "list":
        resp = client.list_instances()
        print(json.dumps(resp.to_dict(), indent=2, sort_keys=True))
        return 0

    if args.cmd == "register":
        payload: dict[str, object] = {"runtime_api_endpoint": args.runtime_api_endpoint}
        if args.runtime_profile:
            payload["runtime_profile"] = args.runtime_profile
        if args.runtime_name:
            payload["runtime_name"] = args.runtime_name
        req = InstanceRegisterRequest.from_dict(payload)
        resp = client.register_instance(req)
        print(json.dumps(resp.to_dict(), indent=2, sort_keys=True))
        return 0

    if args.cmd == "delete":
        client.delete_instance(args.instance_id)
        return 0

    if args.cmd == "runtime-profiles":
        if args.profiles_cmd == "list":
            resp = client.list_runtime_profiles()
            print(json.dumps(resp.to_dict(), indent=2, sort_keys=True))
            return 0

        if args.profiles_cmd == "upsert":
            request_path = Path(args.request_json)
            payload = json.loads(request_path.read_text(encoding="utf-8"))
            req = RuntimeProfileUpsertRequest.from_dict(payload)
            profile = client.upsert_runtime_profile(UpsertRuntimeProfileRequest(runtime_profile=args.runtime_profile, body=req))
            print(json.dumps(profile.to_dict(), indent=2, sort_keys=True))
            return 0

        if args.profiles_cmd == "delete":
            client.delete_runtime_profile(args.runtime_profile)
            return 0

        print(f"Unknown runtime-profiles command: {args.profiles_cmd}", file=sys.stderr)
        return 2

    if args.cmd == "run":
        request_path = Path(args.request_json)
        payload = json.loads(request_path.read_text(encoding="utf-8"))
        run_request = RunRequest.from_dict(payload)
        status_obj = client.submit_run(run_request)
        print(json.dumps(status_obj.to_dict(), indent=2, sort_keys=True))
        return 0

    if args.cmd == "runs":
        resp = client.list_runs(page_size=args.page_size, page_token=args.page_token)
        print(json.dumps(resp.to_dict(), indent=2, sort_keys=True))
        return 0

    if args.cmd == "status":
        status_obj = client.get_run_status(args.run_id)
        print(json.dumps(status_obj.to_dict(), indent=2, sort_keys=True))
        return 0

    if args.cmd == "result":
        result_obj = client.get_run_result(args.run_id)
        print(json.dumps(result_obj.to_dict(), indent=2, sort_keys=True))
        return 0

    if args.cmd == "trace":
        trace_obj = client.get_run_trace(args.run_id)
        print(json.dumps(trace_obj.to_dict(), indent=2, sort_keys=True))
        return 0

    print(f"Unknown command: {args.cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
