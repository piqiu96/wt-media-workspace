#!/usr/bin/env python3
"""AC-05 and T-07's two remaining gaps: the real Desktop, launched, four times.

Everything here runs against the real binary — the real config loader, the real
CSP injection, the real `generate_handler!` table, the real sidecar spawn — and
every judgement is made on what the running application did, not on what its
source says it would do.

**Why a launch and not a unit test.** Three of T-07's claims are invisible to
`cargo test`, and the CHG registers them as such:

  * `get_public_config` is in `generate_handler!` — an unregistered command is a
    green test suite and a "command not found" at runtime.
  * both spawn paths are handed the same four environment variables — the
    `Command` needs an `AppHandle`, so no test can build one.
  * the CSP the window is served under — `cargo test` sees `csp_policy` as a
    string; nothing sees the browser enforce it.

**How the probe page gets there.** `tauri.conf.json` is not edited. The build is
given `TAURI_CONFIG` with `build.devUrl` nulled and `build.frontendDist` pointing
at `evidence/tools/ac05_probe/`, and `tauri-codegen` embeds a `frontendDist`
whenever `devUrl` is absent (`tauri-codegen/src/context.rs:178`), so the probe is
served from `tauri://localhost` by Tauri's own asset protocol.

That indirection is the whole reason the CSP is observable. `Manager::get_asset`
attaches the policy header only to assets Tauri serves itself
(`tauri/src/manager/mod.rs:435-463`, consumed by `src/protocol/tauri.rs:182`), so
a page loaded from an external `devUrl` — the ordinary `tauri dev` shape — is
governed by no policy at all and cannot answer this question either way. The
"wrong `csp_connect_src` must produce a violation" leg is what proves the header
was really there.

The IPC is unaffected by all of this: on macOS it is
`window.webkit.messageHandlers.ipc` (wry `wkwebview/mod.rs:639`), a script
message handler rather than a request, so a `connect-src` that blocks every fetch
still lets the page report what it saw. That asymmetry is what makes a
deliberately wrong CSP measurable instead of merely fatal.

**Four launches, because four questions have four different shapes.**

  M1  file says `python_fallback = true`, the env gate is *unset*, no sidecar
      beside the executable, `csp_connect_src` pointed at a dead origin.
      -> the file's `true` does not decide; the CSP violation does happen.
  M2  file says `python_fallback = false`, the env gate is *set*, no sidecar
      -> the file's `false` does not decide either; the CSP is now correct.
  M3  same as M2 but with a sidecar in the slot
      -> which of the two spawn paths wins, and that the same four variables
         reached it.
  M4  same as M2 but with `ipc:` added to `csp_connect_src`
      -> the counterfactual for the one violation every other leg shows.

M1 vs M2 are the two-way CSP check: identical probe, identical fetch URL, one
config token apart, and the result flips. M2 vs M3 are the two spawn paths with
everything else held still. M1 vs M2 on the fallback gate is the same trick
applied to `development.python_fallback`, whose consumer the code does not have.

**The `ipc://` violation, and why M4 exists.** Every launch refuses one request
that has nothing to do with Cloud: `fetch('ipc://localhost/<command>')`. That is
Tauri's *preferred* IPC transport — `ipc-protocol.js:30-70` posts every invoke to
the `ipc://` scheme first and only falls back to `window.ipc.postMessage` after a
failure, which it then caches for the rest of the session. `connect-src 'self'
<cloud origin>` does not list `ipc:`, so the first attempt is refused, a console
violation is logged, and every command afterwards takes the fallback. Commands
still work, which is why this is registered as a finding with a measured
counterfactual rather than treated as a failure: M4 adds the missing source to
`csp_connect_src` and must show the violation gone and nothing else changed. The
same policy shape shipped before this CHG (`git show 14ff67c^:src-tauri/tauri.conf.json`),
so this is inherited behaviour, not a regression T-07 introduced.

**What is not read, and why.** The four variables reach the Agent through its
environment, which is exactly where the per-launch token lives. Dumping a child's
environment to prove a point would put that token in this tool's output, which is
the thing the CHG forbids. So the token is never read: it is proven *behaviourally*
— a request with no token must be refused (401), which can only happen if the
child holds a non-empty one, because `_check_auth` waves everything through when
its token is empty. The child's *argv* is read, because D-04 is a claim about the
argv.

Usage: python3 ac05_desktop_launch.py [--skip-build]
"""

from __future__ import annotations

import json
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

DESKTOP = Path("/Users/aqiuye/Develop/workspace/wt-media/wt-media-desktop")
CRATE = DESKTOP / "src-tauri"
BINARY = DESKTOP / "target/debug/wt-media-desktop-shell"
# Where `tauri-plugin-shell` resolves a sidecar to: `relative_command_path` takes
# the directory of the running executable (`tauri-plugin-shell/src/process/mod.rs:120-134`).
SIDECAR_SLOT = DESKTOP / "target/debug/wt-media-agent"

AGENT = Path("/Users/aqiuye/Develop/workspace/wt-media/wt-media-agent")
VENV_PYTHON = AGENT / ".venv/bin/python"
PROBE_SOURCE = Path(__file__).resolve().parent / "ac05_probe"

SCRATCH = Path("/tmp/wt-ac05")
CLOUD = "http://127.0.0.1:18080"
# Nothing listens here. It is named in the "wrong" `csp_connect_src`, so the
# number turns up in `originalPolicy` and makes the violation's *source* — the
# config file — visible in the report.
DEAD_ORIGIN = "http://127.0.0.1:19998"

FAIL_MESSAGE_MARKER = "未找到或无法启动"

failures: list[str] = []


def fail(what: str) -> None:
    failures.append(what)
    print(f"    FAIL: {what}")


def note(what: str) -> None:
    print(f"    NOTE: {what}")


def section(title: str) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


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


def request(url: str, token: str | None = None) -> tuple[int, str]:
    req = urllib.request.Request(url)
    if token is not None:
        req.add_header("authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status, response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")


def listener_of(port: int) -> tuple[int, str]:
    """The pid listening on `port`, and the address it is bound to."""
    out = subprocess.run(
        ["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN"],
        capture_output=True, text=True,
    ).stdout.splitlines()
    for line in out[1:]:
        fields = line.split()
        if len(fields) >= 9:
            return int(fields[1]), fields[8]
    return 0, ""


def process_row(pid: int) -> tuple[int, str]:
    """`(ppid, argv)` for a pid. Argv only — never the environment."""
    out = subprocess.run(
        ["ps", "-o", "ppid=,command=", "-p", str(pid)], capture_output=True, text=True
    ).stdout.strip()
    if not out:
        return 0, ""
    head, _, argv = out.partition(" ")
    return int(head), argv.strip()


# A command line that looks like it carries a credential. The control below
# feeds it a token-shaped argument on purpose: a negative check that cannot
# fail is indistinguishable from one that is not looking.
SECRET_SHAPED = re.compile(r"(?i)(token|secret|bearer|password)|[0-9a-f]{16,}")


def argv_carries_a_secret(argv: str) -> bool:
    return bool(SECRET_SHAPED.search(argv))


def secret_checker_control() -> None:
    planted = "python -m x --token 9f2ac41d7be04e5a8c31f0d2b7e94a16"
    if not argv_carries_a_secret(planted):
        fail("HARD STOP: the argv secret-checker cannot even see a planted token, "
             "so its verdict on the real argv means nothing")
    else:
        print(f"    control: a planted token-shaped argv is caught -> "
              f"{argv_carries_a_secret(planted)}")


def build(probe_dir: Path) -> None:
    """Embed the probe page and build the binary the launches will run."""
    override = {"build": {"devUrl": None, "frontendDist": str(probe_dir)}}
    env = os.environ.copy()
    env["TAURI_CONFIG"] = json.dumps(override)
    print(f"  TAURI_CONFIG={env['TAURI_CONFIG']}")
    started = time.time()
    proc = subprocess.run(
        ["cargo", "build", "-p", "wt-media-desktop-shell"],
        cwd=DESKTOP, env=env, capture_output=True, text=True,
    )
    print(f"  cargo build -> exit={proc.returncode} in {time.time() - started:.1f}s")
    if proc.returncode != 0:
        print(proc.stderr[-3000:])
        raise SystemExit("HARD STOP: the desktop binary did not build")


def write_config(path: Path, port: int, data_dir: Path, csp_connect_src: str, python_fallback: bool) -> None:
    """One config file, written in full so nothing is inherited by accident.

    `cloud.base_url` is the real Cloud in every leg: the CSP legs need a fetch
    that can actually succeed, and a refused connection is not a CSP verdict.
    """
    path.write_text(
        "environment = \"development\"\n"
        "\n"
        "[agent]\n"
        "host = \"127.0.0.1\"\n"
        f"port = {port}\n"
        f"data_dir = {json.dumps(str(data_dir))}\n"
        "\n"
        "[cloud]\n"
        f"base_url = \"{CLOUD}\"\n"
        "\n"
        "[browser]\n"
        f"csp_connect_src = \"{csp_connect_src}\"\n"
        "\n"
        "[http]\n"
        "request_timeout_seconds = 30\n"
        "connect_timeout_seconds = 10\n"
        "\n"
        "[sidecar]\n"
        "start_timeout_ms = 15000\n"
        "\n"
        "[development]\n"
        f"python_fallback = {'true' if python_fallback else 'false'}\n"
    )


def install_sidecar_shim() -> None:
    """A stand-in for the frozen sidecar, running the module the real one does.

    `scripts/build_desktop_sidecar.py` takes `sidecar_main.py` as its PyInstaller
    entry, so this executes that same module from the checkout. It is a script
    rather than a binary because what is under test is the *spawn* — the path
    resolution, the environment, the argument list — not PyInstaller's output,
    which `binaries/` holds and CHG-D(059) validates.
    """
    SIDECAR_SLOT.write_text(
        "#!/bin/sh\n"
        "# Stands in for the bundled sidecar. See ac05_desktop_launch.py.\n"
        f'exec "{VENV_PYTHON}" -m wt_media_agent.sidecar_main\n'
    )
    SIDECAR_SLOT.chmod(0o755)


def parse_reports(log: Path) -> list[tuple[str, dict]]:
    reports = []
    for line in log.read_text(errors="replace").splitlines():
        marker = "[WEBVIEW] AC05 "
        if marker not in line:
            continue
        body = line.split(marker, 1)[1]
        tag, _, raw = body.partition(" ")
        try:
            reports.append((tag, json.loads(raw)))
        except json.JSONDecodeError:
            reports.append((tag, {"unparsed": raw}))
    return reports


def only(reports: list[tuple[str, dict]], tag: str) -> dict | None:
    found = [payload for name, payload in reports if name == tag]
    if len(found) != 1:
        fail(f"expected exactly one {tag} report, got {len(found)}")
        return found[0] if found else None
    return found[0]


def run_leg(
    name: str,
    *,
    python_fallback: bool,
    env_fallback: str | None,
    sidecar_present: bool,
    csp_connect_src: str,
    expect_start: tuple[str, str],
    expect_ipc_violation: bool,
) -> None:
    """One launch, one report, all assertions for that launch.

    `expect_start` is `(kind, value)`: kind is `"label"` for a spawn that
    succeeds, `"error"` for one that must not.

    `expect_ipc_violation` is the observed state of Tauri's `ipc://` transport,
    which this tool records per leg rather than assumes: M1-M3 must show it
    refused (that is the finding) and M4, whose only difference is the extra CSP
    source, must show it gone (that is the finding's root cause).
    """
    section(f"{name}  (csp_connect_src = {csp_connect_src})")
    scratch = SCRATCH / name
    if scratch.exists():
        shutil.rmtree(scratch)
    (scratch / "probe").mkdir(parents=True)
    for item in PROBE_SOURCE.iterdir():
        shutil.copy(item, scratch / "probe" / item.name)

    port = free_port()
    data_dir = scratch / "agent-data"
    config_path = scratch / "desktop.toml"
    write_config(config_path, port, data_dir, csp_connect_src, python_fallback)

    if sidecar_present:
        install_sidecar_shim()
    elif SIDECAR_SLOT.exists():
        SIDECAR_SLOT.unlink()

    print(f"  config      {config_path}")
    print(f"  agent port  {port} (8765 belongs to the developer's own Agent — untouched)")
    print(f"  data dir    {data_dir}")
    print(f"  fallback    file={python_fallback} env="
          f"{'set' if env_fallback else 'unset'} sidecar_beside_exe={sidecar_present}")

    # A deliberately small environment: the Desktop needs PATH and HOME, and
    # everything else it reads it must have been given. Inheritance cannot
    # explain a pass, and the fallback gate cannot leak in from this shell.
    env = {
        "PATH": f"{VENV_PYTHON.parent}:{os.environ.get('PATH', '/usr/bin:/bin')}",
        "HOME": os.environ.get("HOME", str(Path.home())),
        "PYTHONPATH": str(AGENT / "src"),
        "WT_MEDIA_DESKTOP_CONFIG": str(config_path),
        "LANG": os.environ.get("LANG", "en_US.UTF-8"),
    }
    if env_fallback is not None:
        env["WT_MEDIA_DESKTOP_ALLOW_PYTHON_FALLBACK"] = env_fallback

    log = scratch / "desktop.log"
    handle = log.open("w")
    proc = subprocess.Popen(
        [str(BINARY)], cwd=CRATE, env=env,
        stdout=handle, stderr=subprocess.STDOUT, text=True, start_new_session=True,
    )
    print(f"  launched    pid={proc.pid}")
    try:
        deadline = time.time() + 90
        reports: list[tuple[str, dict]] = []
        while time.time() < deadline:
            reports = parse_reports(log)
            if any(tag == "Done" for tag, _ in reports):
                break
            if proc.poll() is not None:
                break
            time.sleep(0.5)

        text = log.read_text(errors="replace")
        summary = [ln for ln in text.splitlines() if ln.startswith("[wt-media-desktop]")]
        print(f"  desktop stderr: {summary[0] if summary else '(no summary line)'}")
        print(f"  reports: {[tag for tag, _ in reports]}")

        if not reports:
            fail(f"{name}: the page reported nothing at all — the window never "
                 f"loaded, the IPC never reached the native side, or the script "
                 f"was blocked before its first line")
            print(text[-2500:])
            return

        # --- provenance -------------------------------------------------
        if not summary or "环境变量指定的文件" not in summary[0]:
            fail(f"{name}: the launch did not report the config file the tool "
                 f"selected as its source ({summary[:1]})")
        if "被拒绝" in (summary[0] if summary else ""):
            fail(f"{name}: the file this tool wrote was rejected by the loader")

        boot = only(reports, "Boot") or {}
        print(f"  Boot: {boot}")
        if not boot.get("internals"):
            fail(f"{name}: the WebView has no Tauri IPC bridge")
        if not str(boot.get("href", "")).startswith("tauri://"):
            fail(f"{name}: the page is not served by Tauri's own protocol "
                 f"({boot.get('href')!r}), so the CSP would not apply to it")

        public = only(reports, "PublicConfig") or {}
        value = public.get("value") or {}
        print(f"  get_public_config -> {value}")
        if not public.get("ok"):
            fail(f"{name}: get_public_config is not a registered command: "
                 f"{public.get('error')!r}")
        elif value.get("cloud_base_url") != CLOUD:
            fail(f"{name}: cloud_base_url is {value.get('cloud_base_url')!r}, "
                 f"not the file's {CLOUD!r}")
        if value.get("local_agent_port") != port:
            fail(f"{name}: local_agent_port is {value.get('local_agent_port')!r}, "
                 f"not the file's {port}")
        if value.get("environment") != "development":
            fail(f"{name}: environment is {value.get('environment')!r}")
        if len(value) != 3:
            fail(f"{name}: get_public_config answered {sorted(value)} — it must be "
                 f"the closed set of three non-sensitive fields")

        # --- the two-way CSP check --------------------------------------
        # Two kinds of violation live in this report and they answer different
        # questions, so they are separated before anything is asserted: Tauri's
        # own `ipc://` transport, which is refused in every launch and is the
        # finding below, and a refusal of the URL under test, which is the CSP
        # verdict. Asserting on the flat count would have made M3 fail for a
        # violation that has nothing to do with the origin being measured.
        ipc_seen = [
            payload
            for tag, payload in reports
            if tag == "Violation" and str(payload.get("blocked", "")).startswith("ipc://")
        ]
        print(f"  ipc:// refusals  {len(ipc_seen)} (Tauri's preferred transport)")
        for payload in ipc_seen[:2]:
            print(f"    refused: {payload.get('blocked')}")
        if expect_ipc_violation and not ipc_seen:
            fail(f"{name}: no ipc:// refusal appeared, so this leg cannot be the "
                 f"counterfactual the M4 leg is compared against")
        if not expect_ipc_violation and ipc_seen:
            fail(f"{name}: adding ipc: to csp_connect_src did not stop the "
                 f"refusal: {ipc_seen[:1]}")
        if expect_ipc_violation and ipc_seen:
            print(f"    (registered finding: connect-src does not list ipc:, so "
                  f"Tauri falls back to postMessage for every later command)")

        want_blocked = csp_connect_src.startswith(DEAD_ORIGIN)
        cloud_fetch = only(reports, "CspFetchCloud") or {}
        refusals = [
            v for v in (cloud_fetch.get("violations") or [])
            if not str(v.get("blocked", "")).startswith("ipc://")
        ]
        print(f"  fetch {cloud_fetch.get('url')} -> {cloud_fetch.get('outcome')} "
              f"refusals={len(refusals)}")
        expected = "rejected" if want_blocked else "resolved"
        if cloud_fetch.get("outcome") != expected:
            fail(f"{name}: the Cloud fetch was {cloud_fetch.get('outcome')!r}, "
                 f"expected {expected!r} for csp_connect_src={csp_connect_src!r}")
        if want_blocked:
            if not refusals:
                fail(f"{name}: a wrong csp_connect_src produced no violation — the "
                     f"policy is not reaching the window")
            elif not any("connect-src" in (v.get("directive") or "") for v in refusals):
                fail(f"{name}: the violation is not a connect-src one: {refusals}")
            elif not any(str(DEAD_ORIGIN) in (v.get("policy") or "") for v in refusals):
                fail(f"{name}: the enforced policy does not name the origin the "
                     f"config file gave it: {refusals}")
            else:
                print(f"    violation: {refusals[0]['directive']} "
                      f"blocked {refusals[0]['blocked']}")
                print(f"    policy: {refusals[0]['policy']}")
        else:
            if refusals:
                fail(f"{name}: a correct csp_connect_src still produced a "
                     f"violation of the URL under test: {refusals}")
            print("    no violation: the configured origin is allowed")
        # The control, in every leg: the same Cloud under its other name is in
        # no config, so it must be refused every time. Without this, "rejected"
        # in the leg above would also be consistent with a window where every
        # request to anywhere fails.
        loopback = only(reports, "CspFetchLoopback") or {}
        loopback_refusals = [
            v for v in (loopback.get("violations") or [])
            if not str(v.get("blocked", "")).startswith("ipc://")
        ]
        print(f"  fetch {loopback.get('url')} -> {loopback.get('outcome')} "
              f"refusals={len(loopback_refusals)} (control: must be rejected in "
              f"every leg, whatever the config says about the real origin)")
        if loopback.get("outcome") != "rejected" or not loopback_refusals:
            fail(f"{name}: the same origin under another name was not refused, so "
                 f"the CSP is not discriminating between origins at all")

        # Anything refused that is neither Tauri's own ipc:// transport nor one
        # of the two URLs this leg deliberately asked for is a violation nobody
        # planned — either a real third-party request or a policy the tool has
        # misunderstood.
        accounted = {cloud_fetch.get("url"), loopback.get("url")}
        for tag, body in reports:
            if tag != "Violation" or str(body.get("blocked", "")).startswith("ipc://"):
                continue
            if body.get("blocked") not in accounted:
                fail(f"{name}: an unaccounted-for CSP violation: {body}")

        # --- the spawn path ---------------------------------------------
        started = only(reports, "AgentStart") or {}
        kind, wanted = expect_start
        print(f"  local_agent_start -> ok={started.get('ok')} "
              f"value={started.get('value')!r} error={started.get('error')!r}")
        if kind == "label":
            if started.get("value") != wanted:
                fail(f"{name}: local_agent_start returned {started.get('value')!r}, "
                     f"expected the {wanted!r} path")
        elif kind == "error":
            if started.get("ok"):
                fail(f"{name}: local_agent_start unexpectedly succeeded "
                     f"({started.get('value')!r}); the file said "
                     f"python_fallback={python_fallback} and the env gate was "
                     f"{'set' if env_fallback else 'unset'}")
            elif FAIL_MESSAGE_MARKER not in (started.get("error") or ""):
                fail(f"{name}: local_agent_start failed with "
                     f"{started.get('error')!r}, which is not the product's "
                     f"reinstall message")

        if kind == "error":
            print("  no agent was started in this leg, so there is none to inspect")
            return

        # --- what the child actually did --------------------------------
        health = only(reports, "AgentHealth") or {}
        raw_body = health.get("body") or ""
        print(f"  local_agent_health -> ok={health.get('ok')} "
              f"body={raw_body!r} attempts={health.get('attempt')}")
        # The Agent's `/healthz` answers a JSON object, not the bare word `ok`
        # (first measurement of this tool asserted the word and failed on a
        # healthy Agent — the assertion was wrong, not the Agent).
        try:
            facts = json.loads(raw_body)
        except json.JSONDecodeError:
            facts = {}
        if facts.get("status") != "ok":
            fail(f"{name}: the Agent never answered the native client, so the port "
                 f"or the token it was told does not match what the client uses "
                 f"(body={raw_body!r})")

        if not wait_for_port(port, 10):
            fail(f"{name}: nothing is listening on {port}")
            return

        pid, address = listener_of(port)
        print(f"  listener    pid={pid} bound={address}")
        if address != f"127.0.0.1:{port}":
            fail(f"{name}: the Agent is bound to {address!r}, not loopback:{port}")

        parent, argv = process_row(pid)
        print(f"  child       ppid={parent} argv={argv}")
        if parent != proc.pid:
            fail(f"{name}: the listener's parent is {parent}, not the Desktop "
                 f"process {proc.pid}")
        if "wt_media_agent" not in argv:
            fail(f"{name}: the child is not running the Agent's module: {argv!r}")
        if argv_carries_a_secret(argv):
            fail(f"{name}: D-04 — the child's argument list looks like it carries "
                 f"a credential: {argv!r}")
        else:
            print("    argv carries no token-shaped argument")

        # The token, proven by behaviour rather than read: an empty token makes
        # `_check_auth` wave every request through, so a refusal is only possible
        # if a non-empty one arrived.
        no_token, _ = request(f"http://127.0.0.1:{port}/healthz")
        wrong_token, _ = request(f"http://127.0.0.1:{port}/healthz", "ac05-not-the-token")
        print(f"  /healthz    no token -> {no_token}, wrong token -> {wrong_token}, "
              f"the Desktop's own client -> 200")
        if no_token != 401:
            fail(f"{name}: /healthz answered {no_token} without a token; the child "
                 f"was not told one")
        if wrong_token != 401:
            fail(f"{name}: /healthz accepted a wrong token ({wrong_token})")

        db = data_dir / "local-agent.sqlite3"
        print(f"  data dir    {sorted(p.name for p in data_dir.iterdir()) if data_dir.exists() else '(missing)'}")
        if not db.is_file():
            fail(f"{name}: the child did not write its database under the data dir "
                 f"the config named, so WT_MEDIA_AGENT_DATA_DIR did not arrive")
        if (AGENT / ".local").exists() and not env_fallback:
            pass  # the checkout's own dev dir is not an assertion; see the notes
    finally:
        app_alive = proc.poll() is None
        if app_alive:
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait(timeout=5)
        print(f"  desktop stopped (exit={proc.returncode}, was running={app_alive})")

        # The plugin kills its children on `RunEvent::Exit`
        # (`tauri-plugin-shell/src/lib.rs:133-139`), which a SIGTERM does not
        # raise. What is left behind is reported rather than quietly tidied.
        time.sleep(0.5)
        if listening(port):
            pid, _ = listener_of(port)
            note(f"the Agent outlived the SIGTERM (pid={pid}); killing it here. "
                 f"The product's own exit path is RunEvent::Exit, which does kill it")
            try:
                os.killpg(os.getpgid(pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
            time.sleep(0.5)
            if listening(port):
                fail(f"{name}: port {port} is still held after cleanup")
        else:
            print(f"  after stop: nothing listening on {port}")


def main() -> int:
    print(f"desktop binary: {BINARY}")
    print(f"agent source:   {AGENT / 'src'}")
    print(f"probe page:     {PROBE_SOURCE}")
    print(f"cloud:          {CLOUD}")

    status, _ = request(f"{CLOUD}/healthz")
    if status != 200:
        print(f"HARD STOP: no Cloud at {CLOUD} (healthz -> {status}); the "
              f"'correct CSP' leg needs a fetch that can succeed")
        return 2

    secret_checker_control()

    SCRATCH.mkdir(parents=True, exist_ok=True)
    (SCRATCH / "probe").mkdir(parents=True, exist_ok=True)
    for item in PROBE_SOURCE.iterdir():
        shutil.copy(item, SCRATCH / "probe" / item.name)

    if "--skip-build" not in sys.argv:
        section("BUILD: the probe page, embedded as the app's frontend")
        build(SCRATCH / "probe")
    if not BINARY.is_file():
        print(f"HARD STOP: no binary at {BINARY}")
        return 2

    try:
        run_leg(
            "M1-file-true-env-unset",
            python_fallback=True,
            env_fallback=None,
            sidecar_present=False,
            csp_connect_src=DEAD_ORIGIN,
            expect_start=("error", FAIL_MESSAGE_MARKER),
            expect_ipc_violation=True,
        )
        run_leg(
            "M2-file-false-env-set",
            python_fallback=False,
            env_fallback="1",
            sidecar_present=False,
            csp_connect_src=CLOUD,
            expect_start=("label", "started"),
            expect_ipc_violation=True,
        )
        run_leg(
            "M3-sidecar-beside-exe",
            python_fallback=False,
            env_fallback="1",
            sidecar_present=True,
            csp_connect_src=CLOUD,
            expect_start=("label", "sidecar_started"),
            expect_ipc_violation=True,
        )
        # M2's config plus one CSP source, so the only thing that can change is
        # the refusal this tool is explaining.
        run_leg(
            "M4-ipc-source-added",
            python_fallback=False,
            env_fallback="1",
            sidecar_present=False,
            csp_connect_src=f"ipc: http://ipc.localhost {CLOUD}",
            expect_start=("label", "started"),
            expect_ipc_violation=False,
        )
    finally:
        if SIDECAR_SLOT.exists():
            SIDECAR_SLOT.unlink()
            print(f"\n  removed the stand-in sidecar from {SIDECAR_SLOT}")

    print()
    print("=" * 78)
    if failures:
        print(f"RESULT: FAIL ({len(failures)})")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("RESULT: PASS -- four real launches: both spawn paths carried the four "
          "variables, the wrong CSP was enforced and the right one was not, and "
          "the ipc:// refusal follows from the missing CSP source alone")
    return 0


if __name__ == "__main__":
    sys.exit(main())
