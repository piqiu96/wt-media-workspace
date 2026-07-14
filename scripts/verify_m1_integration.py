#!/usr/bin/env python3
"""Run the M1 Cloud-Agent-Desktop integration verification."""

from __future__ import annotations

import json
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any
from urllib import error, request


ROOT = Path(__file__).resolve().parents[1]
OUTER_ROOT = ROOT.parent
DEVELOP_WORKSPACE_ROOT = OUTER_ROOT.parent
CLOUD_ROOT = OUTER_ROOT / "wt-media-cloud"
AGENT_ROOT = OUTER_ROOT / "wt-media-agent"
DESKTOP_ROOT = OUTER_ROOT / "wt-media-desktop"
GO_BIN = DEVELOP_WORKSPACE_ROOT / "devenv" / "go26" / "go" / "bin" / "go"


class IntegrationError(RuntimeError):
    pass


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def http_json(method: str, url: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    body = None
    headers = {}
    if payload is not None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        headers["content-type"] = "application/json"
    req = request.Request(url, data=body, method=method, headers=headers)
    try:
        with request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise IntegrationError(f"{method} {url} failed: {exc.code} {detail}") from exc
    decoded = json.loads(raw)
    if not isinstance(decoded, dict):
        raise IntegrationError(f"{method} {url} did not return a JSON object")
    return decoded


def http_text(url: str) -> str:
    with request.urlopen(url, timeout=10) as resp:
        return resp.read().decode("utf-8")


def wait_until_json(url: str, deadline_s: float = 45.0) -> dict[str, Any]:
    deadline = time.time() + deadline_s
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            return http_json("GET", url)
        except Exception as exc:  # noqa: BLE001 - surfaced if the service never becomes ready.
            last_error = exc
            time.sleep(0.5)
    raise IntegrationError(f"service did not become ready at {url}: {last_error}")


def start_cloud(port: int) -> subprocess.Popen[str]:
    if not GO_BIN.is_file():
        raise IntegrationError(f"go binary not found: {GO_BIN}")

    env = os.environ.copy()
    env.update(
        {
            "GOROOT": str(DEVELOP_WORKSPACE_ROOT / "devenv" / "go26" / "go"),
            "GOPATH": str(DEVELOP_WORKSPACE_ROOT / "devenv" / "go19" / "gopath"),
            "GOCACHE": str(CLOUD_ROOT / ".cache" / "go-build"),
            "WT_MEDIA_CLOUD_HTTP_ADDR": f"127.0.0.1:{port}",
        }
    )
    (CLOUD_ROOT / ".cache" / "go-build").mkdir(parents=True, exist_ok=True)
    return subprocess.Popen(
        [str(GO_BIN), "run", "./cmd/server"],
        cwd=CLOUD_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )


def start_local_agent(port: int) -> subprocess.Popen[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(AGENT_ROOT / "src")
    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "wt_media_agent.local_api.server",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=AGENT_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )


def stop_process(proc: subprocess.Popen[str], name: str) -> None:
    if proc.poll() is None:
        os.killpg(proc.pid, signal.SIGTERM)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait(timeout=10)
    stdout, stderr = proc.communicate(timeout=5)
    if proc.returncode not in (0, -15, -9):
        raise IntegrationError(f"{name} exited with {proc.returncode}\nstdout:\n{stdout}\nstderr:\n{stderr}")


def run_desktop_verify() -> str:
    result = subprocess.run(
        ["npm", "run", "verify"],
        cwd=DESKTOP_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode != 0:
        raise IntegrationError(f"desktop verify failed:\n{result.stdout}")
    return result.stdout


def assert_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise IntegrationError(f"{label}: expected {expected!r}, got {actual!r}")


def main() -> int:
    cloud_port = free_port()
    local_agent_port = free_port()
    cloud_base = f"http://127.0.0.1:{cloud_port}"
    local_base = f"http://127.0.0.1:{local_agent_port}"
    cloud_proc: subprocess.Popen[str] | None = None
    local_proc: subprocess.Popen[str] | None = None

    sys.path.insert(0, str(AGENT_ROOT / "src"))
    from wt_media_agent.cloud_agent_client import AgentIdentity, CloudAgentClient
    from wt_media_agent.executors.noop import NoopExecutor

    try:
        cloud_proc = start_cloud(cloud_port)
        wait_until_json(f"{cloud_base}/api/v1/health")

        local_proc = start_local_agent(local_agent_port)
        local_health = wait_until_json(f"{local_base}/healthz")
        assert_equal(local_health.get("mode"), "m1", "local agent mode")

        compatibility = http_json("GET", f"{cloud_base}/api/v1/cloud-agent/compatibility")["data"]
        assert_equal(compatibility.get("major_version"), "v1", "cloud-agent major version")
        assert_equal(compatibility.get("contract_revision"), "2026.07.14.4", "cloud-agent contract revision")

        client = CloudAgentClient(cloud_base)
        agent_id = "agent-m1-c7"
        registered = client.register(
            AgentIdentity(
                agent_id=agent_id,
                mode="local",
                version="0.1.0",
                capabilities=("noop",),
            )
        )
        assert_equal(registered.get("agent_id"), agent_id, "registered agent id")

        heartbeat = client.heartbeat(agent_id, "online")
        assert_equal(heartbeat.get("status"), "online", "heartbeat status")

        created = http_json(
            "POST",
            f"{cloud_base}/api/v1/tasks/noop",
            {"idempotency_key": "m1-c7-noop"},
        )["data"]
        assert_equal(created.get("status"), "pending", "created task status")

        claimed = client.claim_task(agent_id, lease_seconds=30)
        assert_equal(claimed.get("task_type"), "noop_task", "claimed task type")
        assert_equal(claimed.get("agent_id"), agent_id, "claimed task agent")

        final_report = NoopExecutor(client, agent_id).execute(claimed)
        assert_equal(final_report.get("status"), "succeeded", "final report status")
        assert_equal(final_report.get("progress"), 100, "final report progress")

        final_task = http_json("GET", f"{cloud_base}/api/v1/cloud-agent/tasks/{claimed['task_id']}")["data"]
        assert_equal(final_task.get("status"), "succeeded", "stored task status")
        assert_equal(final_task.get("progress"), 100, "stored task progress")

        local_status = http_json("GET", f"{local_base}/api/v1/status")
        assert_equal(local_status.get("agent_id"), "local-agent-dev", "local status agent id")
        sse = http_text(f"{local_base}/api/v1/events")
        if "event: status" not in sse or "pending_result_count" not in sse:
            raise IntegrationError(f"local SSE status event missing expected fields: {sse!r}")

        desktop_output = run_desktop_verify()

        summary = {
            "cloud": {
                "port": cloud_port,
                "compatibility_revision": compatibility.get("contract_revision"),
                "final_task_status": final_task.get("status"),
                "final_task_progress": final_task.get("progress"),
            },
            "agent": {
                "agent_id": agent_id,
                "claimed_task_id": claimed.get("task_id"),
                "noop_executor_result": final_report.get("status"),
            },
            "local_agent": {
                "port": local_agent_port,
                "status": local_status,
                "sse_event": "status",
            },
            "desktop": {
                "verify": "passed",
                "output": desktop_output.strip().splitlines()[-1],
            },
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    finally:
        if local_proc is not None:
            stop_process(local_proc, "local agent")
        if cloud_proc is not None:
            stop_process(cloud_proc, "cloud")


if __name__ == "__main__":
    raise SystemExit(main())
