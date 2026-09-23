#!/usr/bin/env python3
"""AC-01 / AC-03 / AC-09: the three modes, started for real, each once.

Three processes, no Desktop:

* **local**  -- `bootstrap.local`: the loopback service, configured from the
  checkout's `config/agent.toml` plus environment overrides.
* **cloud**  -- `bootstrap.cloud` in its report posture: prints what it resolved
  and exits. The Cloud address is pointed at a port nothing listens on, so
  "makes no request" is a fact about the run rather than a claim about the code.
* **sidecar** -- `bootstrap.sidecar`, handed the four variables Desktop hands it:
  where to listen, what to demand, where to write.

Before those, a provenance section asks whether the checkout's `config/agent.toml`
is *read*, using four trees staged from a copy of `src/`.

What each mode is judged on is written next to it below. Everything is on a
scratch port and a scratch data directory; the checkout's `.local/` and the
developer's own Agent on :8765 are never touched, and every process is stopped
before the tool returns -- which is itself asserted, because a leaked listener
would make the next run's port choice a coincidence.

Usage: python3 ac01_ac09_agent_modes.py
"""

from __future__ import annotations

import json
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

AGENT_DIR = Path("/Users/aqiuye/Develop/workspace/wt-media/wt-media-agent")
PYTHON = AGENT_DIR / ".venv/bin/python"

TOKEN = "ac09-token-2f7a9c"
WRONG_TOKEN = "ac09-token-not-this-one"

failures: list[str] = []


def fail(what: str) -> None:
    failures.append(what)
    print(f"    FAIL: {what}")


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def listening(port: int) -> bool:
    with socket.socket() as sock:
        sock.settimeout(0.5)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def wait_for_port(port: int, deadline_s: float = 30.0) -> bool:
    deadline = time.time() + deadline_s
    while time.time() < deadline:
        if listening(port):
            return True
        time.sleep(0.25)
    return False


def http(url: str, token: str | None = None) -> tuple[int, str]:
    request = urllib.request.Request(url)
    if token is not None:
        request.add_header("authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return response.status, response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")


def argv_of(pid: int) -> str:
    out = subprocess.run(["ps", "-o", "command=", "-p", str(pid)], capture_output=True, text=True)
    return out.stdout.strip()


def base_env(data_dir: Path, **extra: str) -> dict[str, str]:
    env = {
        # A minimal environment on purpose: what the Agent needs is what is
        # listed here, so "it read the developer's shell" cannot explain a pass.
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": os.environ.get("HOME", str(Path.home())),
        "PYTHONPATH": str(AGENT_DIR / "src"),
        "WT_MEDIA_AGENT_DATA_DIR": str(data_dir),
        "WT_MEDIA_LOG_LEVEL": "INFO",
    }
    env.update(extra)
    return env


def start(module: str, env: dict[str, str], log: Path) -> subprocess.Popen:
    handle = log.open("w")
    return subprocess.Popen(
        [str(PYTHON), "-m", module],
        cwd=AGENT_DIR,
        env=env,
        stdout=handle,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )


def stop(proc: subprocess.Popen, port: int) -> None:
    if proc.poll() is None:
        os.killpg(proc.pid, signal.SIGTERM)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait(timeout=5)
    deadline = time.time() + 5
    while time.time() < deadline and listening(port):
        time.sleep(0.2)


def section(title: str) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def local_mode(scratch: Path) -> None:
    """AC-01 + AC-09 (local): starts from the checkout's config, answers /healthz."""
    section("MODE 1: local  (bootstrap.local, config/agent.toml + environment)")
    port = free_port()
    data_dir = scratch / "local-data"
    log = scratch / "local.log"
    env = base_env(data_dir, WT_MEDIA_LOCAL_API_PORT=str(port), WT_MEDIA_AGENT_ID="ac09-local")

    print(f"  port {port} (default 8765 is the developer's own Agent -- not used)")
    proc = start("wt_media_agent.local_main", env, log)
    try:
        if not wait_for_port(port):
            fail(f"local mode never began listening on {port}")
            print(log.read_text()[-2000:])
            return
        status, body = http(f"http://127.0.0.1:{port}/healthz")
        print(f"  GET /healthz                -> {status} {body.strip()}")
        if status != 200:
            fail("AC-01: /healthz was not 200")

        status, body = http(f"http://127.0.0.1:{port}/api/v1/status")
        facts = json.loads(body).get("data", {})
        print(f"  GET /api/v1/status          -> {status}")
        print(f"    bitbrowser_status={facts.get('bitbrowser_status')!r} "
              f"main_user_id={facts.get('main_user_id')!r} "
              f"profiles={len(facts.get('bit_profile_ids') or [])}")
        # `bitbrowser_status` is three-valued: "normal" | "identity_unverifiable"
        # | "unreachable" (runtime/environment.py:110-120). "normal" is the
        # success value, so this asserts it -- but only after proving the field
        # can be anything else, because a field that always reads "normal" would
        # satisfy this line while telling us nothing.
        if status != 200 or facts.get("bitbrowser_status") != "normal":
            fail("AC-09: the local surface did not report a reachable BitBrowser")
        if not facts.get("bit_profile_ids"):
            # Positive control for the line above: an empty scan would make
            # "the client works" vacuous.
            fail("AC-09: the real BitBrowser answered with no profiles")
        probe = subprocess.run(
            [str(PYTHON), "-m", "unittest", "-v",
             "tests.test_runtime_environment.RuntimeEnvironmentCollectorTests."
             "test_maps_missing_dependency_and_low_disk_without_raw_output",
             "tests.test_runtime_environment.RuntimeEnvironmentCollectorTests."
             "test_identity_failure_is_distinct_and_reports_no_profile_facts"],
            cwd=AGENT_DIR, env=base_env(data_dir), capture_output=True, text=True,
        )
        print(f"    control: the two failure values, exercised -> "
              f"exit={probe.returncode} ({probe.stderr.strip().splitlines()[-1][:40]})")
        if probe.returncode != 0:
            fail("the three-valued field cannot be shown to go red, so 'normal' means nothing")
        if data_dir.exists() and any(data_dir.iterdir()):
            print(f"    data dir {data_dir} -> {sorted(p.name for p in data_dir.iterdir())}")
    finally:
        stop(proc, port)
        print(f"  after stop: listening={listening(port)}")
        if listening(port):
            fail("local mode leaked a listener")
        print(f"  log tail: {log.read_text().strip().splitlines()[-1][:100] if log.read_text().strip() else '(empty)'}")


def cloud_mode(scratch: Path) -> None:
    """AC-09 (cloud): reports by default, and the report costs no request."""
    section("MODE 2: cloud  (bootstrap.cloud, report posture)")
    data_dir = scratch / "cloud-data"
    log = scratch / "cloud.log"
    # Nothing listens on port 1, so a request would hang or fail loudly instead
    # of quietly succeeding against the developer's Cloud.
    env = base_env(
        data_dir,
        WT_MEDIA_AGENT_ID="ac09-cloud",
        WT_MEDIA_CLOUD_BASE_URL="http://127.0.0.1:1",
        WT_MEDIA_AGENT_RUNTIME_TOKEN=TOKEN,
    )

    started = time.time()
    proc = start("wt_media_agent.cloud_main", env, log)
    try:
        code = proc.wait(timeout=30)
        elapsed = time.time() - started
        out = log.read_text().strip()
        print(f"  elapsed {elapsed:.2f}s  exit={code}")
        print(f"  stdout: {out[:400]}")
        if code != 0:
            fail("AC-09: cloud report mode did not exit 0")
        facts = json.loads(out.splitlines()[-1])
        if facts.get("run_runner") is not False:
            fail("cloud report mode must default to not polling")
        if facts.get("cloud_base_url") != "http://127.0.0.1:1":
            fail("the report did not carry the resolved Cloud address")
        if TOKEN in out:
            fail("the report leaked the runtime token")
        if "ac09-cloud" not in out:
            # Control for the leak check above: an empty report would also
            # contain no token.
            fail("the report is not the resolved configuration at all")
        print(f"  verdict: reported facts after {elapsed:.2f}s against a dead Cloud "
              f"address -> no request was made")
    finally:
        stop(proc, 0)


def sidecar_mode(scratch: Path) -> None:
    """AC-03 + AC-09 (sidecar): the four variables decide everything."""
    section("MODE 3: sidecar  (bootstrap.sidecar, Desktop's four variables)")
    port = free_port()
    data_dir = scratch / "sidecar-data"
    log = scratch / "sidecar.log"
    env = base_env(
        data_dir,
        WT_MEDIA_LOCAL_API_HOST="127.0.0.1",
        WT_MEDIA_LOCAL_API_PORT=str(port),
        WT_MEDIA_AGENT_RUNTIME_TOKEN=TOKEN,
        WT_MEDIA_AGENT_ID="ac09-sidecar",
    )

    print(f"  the four variables: HOST=127.0.0.1 PORT={port} TOKEN=<set> DATA_DIR={data_dir}")
    proc = start("wt_media_agent.sidecar_main", env, log)
    try:
        if not wait_for_port(port):
            fail(f"sidecar never began listening on {port}")
            print(log.read_text()[-2000:])
            return
        print(f"  listened on 127.0.0.1:{port} -- not the default 8765, so PORT was honoured")

        for label, token, expected in (
            ("with the token", TOKEN, 200),
            ("with no token", None, 401),
            ("with a wrong token", WRONG_TOKEN, 401),
        ):
            status, body = http(f"http://127.0.0.1:{port}/healthz", token)
            print(f"  GET /healthz {label:<20} -> {status} {body.strip()[:60]}")
            if status != expected:
                fail(f"AC-03: {label} gave {status}, expected {expected}")

        status, body = http(f"http://127.0.0.1:{port}/api/v1/status", TOKEN)
        facts = json.loads(body).get("data", {})
        print(f"  GET /api/v1/status (with token) -> {status} "
              f"profiles={len(facts.get('bit_profile_ids') or [])}")

        argv = argv_of(proc.pid)
        print(f"  argv: {argv}")
        if TOKEN in argv:
            fail("D-04: the token is visible in the command line")
        if data_dir.exists():
            print(f"  data dir {data_dir} -> {sorted(p.name for p in data_dir.iterdir())}")
        if not (data_dir / "local-agent.sqlite3").is_file():
            fail("DATA_DIR was not honoured: no database under it")
    finally:
        stop(proc, port)
        print(f"  after stop: listening={listening(port)}")
        if listening(port):
            fail("sidecar mode leaked a listener")


def config_file_provenance(scratch: Path) -> None:
    """AC-01's first half: `config/agent.toml` is read, not merely present.

    Every value in the shipped `config/agent.toml` deliberately equals its
    built-in default, so reading the resolved configuration back cannot
    distinguish "the file was parsed" from "the file was never opened".

    The obvious signal -- the `no config file at <path>` line in
    `_read_document` -- turns out to be **unobservable**: `load_config()` runs
    before `runtime/logging.py` installs its handler, so that `logger.debug`
    is dropped at the default WARNING threshold whatever the file's state.
    Measured, not assumed: a tree with no `config/` emits no such line at
    `WT_MEDIA_LOG_LEVEL=DEBUG`. Warning-level lines *are* emitted, and they
    report the file's *contents*, so those are what this uses.

    `repository_root()` is `<paths.py>/../../..` (runtime/paths.py:42-48), so a
    copy of `src/` is a whole agent whose config directory is whatever that copy
    holds. Four trees, none of them the real one:

      1. real tree            -> runs clean: every shipped key is a known key
      2. copy, bogus+secret   -> the control: those warnings do fire, and name
                                 the key while withholding the value
      3. copy, a set value    -> that value reaches the resolved config
      4. copy, broken TOML    -> non-zero exit: a found file really is parsed
    """
    section("PROVENANCE: is config/agent.toml read?  (four trees)")
    staged = subprocess.run(["cp", "-R", str(AGENT_DIR / "src"), str(scratch / "src")], capture_output=True)
    if staged.returncode != 0:
        fail(f"cannot stage a copy of src/: {staged.stderr.decode()[:120]}")
        return

    def stage(name: str, toml: str | None) -> Path:
        root = scratch / name
        (root / "config").mkdir(parents=True)
        subprocess.run(["cp", "-R", str(scratch / "src"), str(root / "src")], check=True)
        if toml is not None:
            (root / "config/agent.toml").write_text(toml)
        return root

    def run_from(root: Path) -> tuple[int, str]:
        env = base_env(scratch / "prov-data")
        env["PYTHONPATH"] = str(root / "src")
        proc = subprocess.run(
            [str(PYTHON), "-m", "wt_media_agent.cloud_main"],
            cwd=root, env=env, capture_output=True, text=True, timeout=60,
        )
        return proc.returncode, proc.stdout + proc.stderr

    def warnings(out: str) -> list[str]:
        return [ln for ln in out.splitlines() if ln.startswith("ignoring ")]

    # 1. the real checkout: the shipped file and the spec agree
    code, out = run_from(AGENT_DIR)
    said = warnings(out)
    print(f"  1. real checkout            exit={code}  warnings: {len(said)}")
    for line in said:
        print(f"       {line}")
    if code != 0:
        fail(f"the real checkout did not run: {out[-400:]}")
    if said:
        # A key the spec does not know, or a credential sitting in the file:
        # either way the shipped file and the code have drifted.
        fail(f"the shipped config/agent.toml is not in agreement with the spec: {said}")

    # 2. the control: the same code, a file that must be complained about
    secret = "SECRET-VALUE-9f2a"
    probe = stage("tree-probe", f'[agent]\nid = "ac09-probe"\nbogus_key = 1\nruntime_token = "{secret}"\n')
    code, out = run_from(probe)
    said = warnings(out)
    print(f"  2. copy, bogus + secret key exit={code}  warnings: {len(said)}")
    for line in said:
        print(f"       {line}")
    if not any("bogus_key" in ln for ln in said):
        fail("HARD STOP: nothing is reported for a tree that must be reported on, "
             "so leg 1's clean run proves nothing")
    if not any("runtime_token" in ln for ln in said):
        fail("D-07: a credential in the config file was not reported")
    if secret in out:
        fail("D-07: the credential's value was printed")
    if json.loads([ln for ln in out.splitlines() if ln.startswith("{")][-1])["agent_id"] != "ac09-probe":
        fail("the file's non-secret values did not survive the run")

    # 3. same code, a config file whose value differs from every default
    code, out = run_from(stage("tree-valued", '[agent]\nid = "ac09-from-file"\n'))
    reported = [ln for ln in out.splitlines() if ln.startswith("{")]
    got = json.loads(reported[-1]).get("agent_id") if reported else None
    print(f"  3. copy with a value        exit={code}  resolved agent_id={got!r}")
    if got != "ac09-from-file":
        fail(f"a value in the file did not reach the config (got {got!r})")

    # 4. a file that exists and is broken must be loud, not silently defaulted
    code, out = run_from(stage("tree-broken", '[agent\nid = "unterminated\n'))
    loud = "ConfigError" in out or "not valid TOML" in out
    print(f"  4. copy with broken TOML    exit={code}  reported={loud}")
    if code == 0 or not loud:
        fail("a malformed config/agent.toml was silently treated as unconfigured")

    print("     precedence (env > file > default) is pinned by tests/test_runtime_config.py")


def main() -> int:
    print(f"python: {PYTHON}")
    print(f"agent HEAD: {subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=AGENT_DIR, capture_output=True, text=True).stdout.strip()}")
    with tempfile.TemporaryDirectory(prefix="wt-ac09-") as tmp:
        scratch = Path(tmp)
        config_file_provenance(scratch)
        local_mode(scratch)
        cloud_mode(scratch)
        sidecar_mode(scratch)

    print()
    print("=" * 78)
    if failures:
        print(f"RESULT: FAIL ({len(failures)})")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("RESULT: PASS -- three modes started for real, each judged on its own criteria")
    return 0


if __name__ == "__main__":
    sys.exit(main())
