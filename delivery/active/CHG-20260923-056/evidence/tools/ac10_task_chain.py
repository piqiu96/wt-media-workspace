#!/usr/bin/env python3
"""AC-10: the task chain, end to end, against a real Cloud.

Cloud Task -> runner -> executor -> client/service -> report -> checkpoint ->
restart recovery, with a real agent process, a real HTTP transport, and a real
Cloud server.

**Which Cloud, and why not the developer's.** The instance used here is the
release `cmd/server` binary, built from the checkout, reading a *copy* of
`config/` (its own port, its own MySQL schema `wt_media_cloud_ac10`). The
developer's instance on :18080 is left alone because its task table carries a
backlog a polling agent must not touch: `claimTask` is
`ORDER BY created_at ASC LIMIT 1` with no type or agent filter
(`repository/mysql_task_store.go:123-126`), and the oldest rows are July's
`profile_open_task` -- starting an agent there would open real browser profiles
and mark someone else's tasks failed. An empty schema exercises the same code
with no third party in the blast radius.

**Two legs, because "it worked" and "it survives a crash" are different claims.**

* Leg A -- one task, all the way through, both ends observed: the Cloud's copy
  of the task and the agent's own SQLite checkpoints.
* Leg B -- the agent is killed *mid-task* (blocked inside its report call, so a
  `running` checkpoint is on disk), then restarted. This is the only way to see
  what recovery actually does, and what it does is deliberately reported as it
  is: `_recover_incomplete_tasks` (`runner/runner.py:65-75`) *re-discovers and
  logs* the unfinished task. It does not re-execute it, and this tool asserts
  that it does not, rather than assuming the stronger behaviour.

Usage: python3 ac10_task_chain.py
"""

from __future__ import annotations

import http.server
import json
import os
import signal
import socket
import socketserver
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

AGENT_DIR = Path("/Users/aqiuye/Develop/workspace/wt-media/wt-media-agent")
PYTHON = AGENT_DIR / ".venv/bin/python"
CLOUD = os.environ.get("WT_AC10_CLOUD", "http://127.0.0.1:18199")

TOKEN = "ac10-token-7c41bd"
AGENT_ID = "ac10-agent"

failures: list[str] = []


def fail(what: str) -> None:
    failures.append(what)
    print(f"    FAIL: {what}")


def section(title: str) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def cloud(method: str, path: str, payload: dict | None = None) -> tuple[int, dict]:
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(f"{CLOUD}{path}", data=data, method=method)
    if data is not None:
        request.add_header("content-type", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, _as_json(response.read())
    except urllib.error.HTTPError as exc:
        return exc.code, _as_json(exc.read())


def create_noop_task(label: str) -> str:
    """Create a noop task, and prove it exists before handing the id out.

    An `idempotency_key` is passed because creating *without* one is broken on
    this Cloud, and the breakage is silent. `createTask` inserts
    `idempotency_key` as Go's empty string
    (`repository/mysql_task_store.go:39-45`) into a column with
    `UNIQUE KEY uq_idempotency_key`, and swallows the duplicate with
    `ON DUPLICATE KEY UPDATE task_id=task_id`. So the first keyless create in a
    schema persists a row and every later one persists nothing -- yet still
    returns a freshly generated id and `status: pending`. Measured, not read:
    four keyless creates produced one row, and the third returned
    `task_2d0a4def...` which `GET` then reported as "任务不存在".

    A distinct key per task is the API's own way to say "this is a new task", so
    the chain is exercised as designed. The defect itself is out of this CHG's
    scope (the Cloud task store is untouched here) and is registered in the CHG
    record instead of being fixed.

    The row is then read back, so a phantom id fails here rather than as a
    mysterious absence three steps later.
    """
    status, body = cloud("POST", "/api/v1/tasks/noop", {"idempotency_key": label})
    task_id = (body.get("data") or {}).get("task_id") or ""
    reported = (body.get("data") or {}).get("status")
    persisted = task_state(task_id) if task_id else {}
    print(f"  POST /api/v1/tasks/noop -> {status} task_id={task_id} "
          f"reported={reported!r} persisted={persisted.get('status')!r}")
    if status != 201 or not task_id:
        fail(f"{label}: the Cloud did not create a noop task")
    elif persisted.get("status") != "pending":
        fail(f"{label}: the create returned {task_id}, which the Cloud cannot read back")
    return task_id


def _as_json(raw: bytes) -> dict:
    """`/healthz` answers `ok`, not JSON; everything else answers an envelope."""
    try:
        return json.loads(raw or b"{}")
    except json.JSONDecodeError:
        return {"raw": raw.decode("utf-8", "replace")[:200]}


def task_state(task_id: str) -> dict:
    _, body = cloud("GET", f"/api/v1/cloud-agent/tasks/{task_id}")
    return body.get("data", {}) or {}


def checkpoints(db_path: Path, task_id: str | None = None) -> list[dict]:
    """Read the agent's checkpoint table without disturbing the running agent."""
    if not db_path.is_file():
        return []
    query = "SELECT task_id, task_type, checkpoint_status, progress FROM task_checkpoints"
    params: tuple = ()
    if task_id is not None:
        query += " WHERE task_id = ?"
        params = (task_id,)
    connection = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=5)
    try:
        connection.row_factory = sqlite3.Row
        return [dict(row) for row in connection.execute(query, params).fetchall()]
    except sqlite3.OperationalError:
        # The table appears only once the agent has run a migration; before that
        # there is nothing to find, which is not an error.
        return []
    finally:
        connection.close()


class StallProxy:
    """Forwards to the Cloud, except that `.../report` never gets an answer.

    Stalling the report is what puts the agent in the state this leg is about:
    claimed, checkpointed as `running`, and unable to finish.
    """

    def __init__(self, upstream: str, stall_on: str) -> None:
        self.upstream = upstream
        self.stall_on = stall_on
        self.port = free_port()
        self._stalled: list[threading.Event] = []
        proxy = self

        class Handler(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *args) -> None:  # keep the tool's output clean
                pass

            def _relay(self) -> None:
                length = int(self.headers.get("content-length") or 0)
                body = self.rfile.read(length) if length else None
                if body is not None and self.command == "POST" and self.path.endswith(proxy.stall_on):
                    print(f"    proxy: holding {self.command} {self.path} open (no response)")
                    event = threading.Event()
                    proxy._stalled.append(event)
                    event.wait(timeout=600)
                    self.close_connection = True
                    return
                request = urllib.request.Request(
                    f"{proxy.upstream}{self.path}", data=body, method=self.command
                )
                for name, value in self.headers.items():
                    if name.lower() not in ("host", "content-length", "connection"):
                        request.add_header(name, value)
                try:
                    with urllib.request.urlopen(request, timeout=20) as response:
                        payload, status = response.read(), response.status
                        content_type = response.headers.get("content-type", "application/json")
                except urllib.error.HTTPError as exc:
                    payload, status = exc.read(), exc.code
                    content_type = "application/json"
                except Exception as exc:  # the Cloud being down is a fact, not a crash
                    payload, status, content_type = str(exc).encode(), 502, "text/plain"
                self.send_response(status)
                self.send_header("content-type", content_type)
                self.send_header("content-length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            do_GET = do_POST = _relay

        self._server = http.server.ThreadingHTTPServer(("127.0.0.1", self.port), Handler)
        self._server.daemon_threads = True

    def start(self) -> None:
        threading.Thread(target=self._server.serve_forever, daemon=True).start()

    def release(self) -> None:
        for event in self._stalled:
            event.set()

    def stop(self) -> None:
        self.release()
        self._server.shutdown()
        self._server.server_close()


def start_agent(scratch: Path, base_url: str, port: int, extra: dict[str, str] | None = None) -> tuple[subprocess.Popen, Path, Path]:
    data_dir = scratch / "agent-data"
    log = scratch / f"agent-{port}.log"
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": os.environ.get("HOME", str(Path.home())),
        "PYTHONPATH": str(AGENT_DIR / "src"),
        "WT_MEDIA_AGENT_DATA_DIR": str(data_dir),
        "WT_MEDIA_CLOUD_BASE_URL": base_url,
        "WT_MEDIA_AGENT_RUN_RUNNER": "1",
        "WT_MEDIA_AGENT_ID": AGENT_ID,
        "WT_MEDIA_AGENT_RUNTIME_TOKEN": TOKEN,
        "WT_MEDIA_LOCAL_API_HOST": "127.0.0.1",
        "WT_MEDIA_LOCAL_API_PORT": str(port),
        "WT_MEDIA_LOG_LEVEL": "INFO",
        # The agent's stdout is a file here, so it would otherwise be block
        # buffered and this tool would be reading a log that lags its process.
        "PYTHONUNBUFFERED": "1",
    }
    env.update(extra or {})
    proc = subprocess.Popen(
        [str(PYTHON), "-m", "wt_media_agent.sidecar_main"],
        cwd=AGENT_DIR, env=env, stdout=log.open("w"), stderr=subprocess.STDOUT,
        text=True, start_new_session=True,
    )
    return proc, log, data_dir / "local-agent.sqlite3"


def kill_hard(proc: subprocess.Popen) -> None:
    if proc.poll() is None:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait(timeout=10)


def stop_agent(proc: subprocess.Popen) -> None:
    if proc.poll() is None:
        os.killpg(proc.pid, signal.SIGTERM)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            kill_hard(proc)


def wait_for(predicate, timeout: float, describe: str):
    deadline = time.time() + timeout
    while time.time() < deadline:
        value = predicate()
        if value:
            return value
        time.sleep(0.2)
    return None


def leg_a(scratch: Path) -> None:
    section("LEG A: one task, all the way through")
    task_id = create_noop_task(f"ac10-leg-a-{int(time.time())}")
    if not task_id:
        return

    port = free_port()
    proc, log, db = start_agent(scratch, CLOUD, port)
    try:
        print(f"  agent {AGENT_ID} started (runner on), local api on {port}")

        def reached_success():
            state = task_state(task_id)
            return state if state.get("status") == "succeeded" else None

        state = wait_for(reached_success, 90, "the task to succeed")
        if state is None:
            fail(f"the task never succeeded; last state {task_state(task_id)}")
            print(log.read_text()[-2500:])
            return
        print(f"  GET /api/v1/cloud-agent/tasks/{task_id} -> status={state.get('status')} "
              f"progress={state.get('progress')} message={state.get('message')!r}")
        print(f"    agent_id on the Cloud row: {state.get('agent_id')!r}")

        if state.get("progress") != 100:
            fail(f"a succeeded task reported progress {state.get('progress')}")
        if state.get("agent_id") != AGENT_ID:
            fail("the Cloud row is not attributed to this agent")
        if (state.get("message") or "") != "noop succeeded":
            fail(f"the final report's message is {state.get('message')!r}")

        text = log.read_text()
        executed = f"executing task {task_id}" in text
        succeeded = f"task {task_id} succeeded" in text
        print(f"  agent log: 'executing task'={executed} 'task succeeded'={succeeded}")

        # The agent-side half: the checkpoint that the chain wrote and then
        # cleared. "No rows" would also hold if there were no database at all,
        # so the file is required to exist first -- and leg B shows the same
        # table holding a `running` row, which is what makes the empty result
        # here mean "cleared" rather than "never written".
        rows = checkpoints(db, task_id)
        all_rows = checkpoints(db)
        print(f"  agent sqlite: file={db.is_file()} ({db.name}), rows for this task="
              f"{len(rows)}, rows in total={len(all_rows)}")
        if not db.is_file():
            fail(f"the agent never created its checkpoint database at {db}")
        elif rows:
            fail(f"the checkpoint survived a successful task: {rows}")

        # And the local surface agrees: no undelivered results left behind.
        request = urllib.request.Request(f"http://127.0.0.1:{port}/api/v1/status")
        request.add_header("authorization", f"Bearer {TOKEN}")
        with urllib.request.urlopen(request, timeout=15) as response:
            facts = json.loads(response.read()).get("data", {})
        print(f"  agent /api/v1/status: pending_result_count={facts.get('pending_result_count')} "
              f"bitbrowser_status={facts.get('bitbrowser_status')!r}")
        if facts.get("pending_result_count") not in (0, None):
            fail("a delivered result is still queued offline")
    finally:
        stop_agent(proc)
        print(f"  agent stopped (exit={proc.returncode})")


def leg_b(scratch: Path) -> None:
    section("LEG B: killed mid-task, then restarted")
    proxy = StallProxy(CLOUD, "/report")
    proxy.start()
    print(f"  stall proxy on 127.0.0.1:{proxy.port} -> {CLOUD} (POST .../report is held open)")

    task_id = create_noop_task(f"ac10-leg-b-{int(time.time())}")
    if not task_id:
        proxy.stop()
        return

    port = free_port()
    # A long client timeout is what keeps the agent *inside* the report call
    # instead of timing out and failing the task: cloud_timeout_seconds is 10 by
    # default, and a 10s timeout would turn this leg into an ordinary failure.
    proc, log, db = start_agent(
        scratch, f"http://127.0.0.1:{proxy.port}", port, {"WT_MEDIA_CLOUD_TIMEOUT": "600"}
    )
    try:
        def running_checkpoint():
            rows = checkpoints(db, task_id)
            return rows[0] if rows and rows[0]["checkpoint_status"] == "running" else None

        row = wait_for(running_checkpoint, 60, "a running checkpoint on disk")
        if row is None:
            fail(f"no running checkpoint appeared; rows={checkpoints(db)}")
            print(log.read_text()[-2500:])
            return
        print(f"  agent sqlite, mid-flight: {row}")
        state = task_state(task_id)
        print(f"  Cloud row while the agent is blocked: status={state.get('status')!r} "
              f"progress={state.get('progress')}")
        if state.get("status") == "succeeded":
            fail("the Cloud says succeeded although the report was never answered")

        kill_hard(proc)
        print(f"  agent SIGKILLed (exit={proc.returncode}); the process got no chance to clean up")
        survivor = checkpoints(db, task_id)
        print(f"  agent sqlite after the kill: {survivor}")
        if not survivor or survivor[0]["checkpoint_status"] != "running":
            fail("the checkpoint did not survive the crash, so recovery has nothing to find")

        # Restart against the stalled proxy as well: keeping the report blocked
        # makes the leg deterministic, since a re-claimed task cannot complete
        # and quietly remove the checkpoint the recovery is meant to report.
        restarted, log2, _ = start_agent(
            scratch, f"http://127.0.0.1:{proxy.port}", free_port(),
            {"WT_MEDIA_CLOUD_TIMEOUT": "600"},
        )
        try:
            found = wait_for(lambda: "recovering 1 incomplete task(s)" in log2.read_text(), 60, "recovery")
            text = log2.read_text()
            print(f"  restart log: 'recovering 1 incomplete task(s)'={bool(found)}")
            resumed = [ln for ln in text.splitlines() if f"resuming task {task_id}" in ln]
            print(f"  restart log: {resumed[0] if resumed else '(no resume line)'}")
            if not found:
                fail("the restarted runner did not report the incomplete task")
                print(text[-2000:])
            elif not resumed:
                fail("the incomplete task was counted but not identified in the log")

            # What recovery does *not* do, asserted rather than glossed: the
            # checkpoint is still there and still `running`. If a future change
            # makes recovery re-execute, this assertion is what will notice.
            after = checkpoints(db, task_id)
            print(f"  agent sqlite after the restart: {after}")
            if after and after[0]["checkpoint_status"] != "running":
                fail(f"recovery changed the checkpoint to {after[0]['checkpoint_status']} "
                     f"without the task having been re-run")
        finally:
            stop_agent(restarted)
            print(f"  restarted agent stopped (exit={restarted.returncode})")
    finally:
        proxy.release()
        stop_agent(proc)
        proxy.stop()


def main() -> int:
    print(f"agent: {AGENT_DIR}")
    print(f"cloud: {CLOUD} (isolated instance, schema wt_media_cloud_ac10)")
    try:
        status, _ = cloud("GET", "/healthz")
    except Exception as exc:
        print(f"HARD STOP: no Cloud at {CLOUD}: {type(exc).__name__}: {exc}")
        return 2
    if status != 200:
        print(f"HARD STOP: {CLOUD}/healthz -> {status}")
        return 2
    _, stats = cloud("GET", "/api/v1/tasks/stats")
    counts = stats.get("data", {})
    print(f"isolated cloud task stats before: {counts}")
    if any(counts.get(key) for key in ("pending", "leased", "succeeded", "failed")):
        print("HARD STOP: this Cloud already holds tasks; the chain must start from an empty table")
        return 2

    with tempfile.TemporaryDirectory(prefix="wt-ac10-") as tmp:
        scratch = Path(tmp)
        leg_a(scratch)
        leg_b(scratch)

    print()
    print("=" * 78)
    if failures:
        print(f"RESULT: FAIL ({len(failures)})")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("RESULT: PASS -- the chain ran end to end, and the crash leg recovered what it must")
    return 0


if __name__ == "__main__":
    sys.exit(main())
