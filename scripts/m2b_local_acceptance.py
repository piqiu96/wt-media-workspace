#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = SCRIPT_DIR.parent
ROOT_DIR = WORKSPACE_DIR.parent
CLOUD_DIR = ROOT_DIR / "wt-media-cloud"
AGENT_DIR = ROOT_DIR / "wt-media-agent"
DESKTOP_DIR = ROOT_DIR / "wt-media-desktop"
RUNTIME_DIR = Path(os.environ.get("WT_MEDIA_M2B_RUNTIME_DIR", ROOT_DIR / ".local" / "m2b"))
LOG_DIR = RUNTIME_DIR / "logs"
PID_DIR = RUNTIME_DIR / "pids"

CLOUD_HOST = os.environ.get("WT_MEDIA_CLOUD_HOST", "127.0.0.1")
CLOUD_PORT = os.environ.get("WT_MEDIA_CLOUD_PORT", "18080")
CLOUD_ADDR = f"{CLOUD_HOST}:{CLOUD_PORT}"
CLOUD_BASE_URL = f"http://{CLOUD_ADDR}"
MYSQL_DSN = os.environ.get(
    "WT_MEDIA_MYSQL_DSN",
    "root:root123@tcp(127.0.0.1:3306)/wt_media_cloud?parseTime=true&multiStatements=true",
)

AGENT_HOST = os.environ.get("WT_MEDIA_AGENT_HOST", "127.0.0.1")
AGENT_PORT = os.environ.get("WT_MEDIA_AGENT_PORT", "8765")
AGENT_ADDR = f"{AGENT_HOST}:{AGENT_PORT}"
AGENT_BASE_URL = f"http://{AGENT_ADDR}"
BIT_API_URL = os.environ.get("WT_MEDIA_BITBROWSER_API_URL", "http://127.0.0.1:54345")
DOUYIN_ENV_FILE = Path(
    os.environ.get("WT_MEDIA_DOUYIN_ENV_FILE", CLOUD_DIR / ".env.local")
)

GO_BIN = Path(os.environ.get("GO_BIN", "/Users/aqiuye/Develop/workspace/devenv/go26/go/bin/go"))
GOROOT = os.environ.get("GOROOT", "/Users/aqiuye/Develop/workspace/devenv/go26/go")
GOPATH = os.environ.get("GOPATH", "/Users/aqiuye/Develop/workspace/devenv/go19/gopath")
AGENT_PYTHON = Path(os.environ.get("PYTHON_BIN", AGENT_DIR / ".venv" / "bin" / "python"))
# Where launch_dmg attaches the freshly built DMG. A fixed private mountpoint
# (instead of the default /Volumes/<product>) so the script never depends on the
# product or volume name, and never opens a leftover mount instead of the new build.
DMG_MOUNT = RUNTIME_DIR / "dmg-mount"

# The Cloud worker's build output. A built binary rather than `go run` because
# `go run` compiles into a child of the `go` process, and the stop path can only
# signal the pid it recorded: CHG-20260930-069 measured that child surviving its
# parent as an orphan (pid 42569) still holding the same job loops. The build
# output lives under the tree's `.cache`, next to the server binary.
WORKER_BIN = CLOUD_DIR / ".cache" / "wt-media-discovery-worker"

# Where `cargo tauri build` writes the app bundle and where this script assembles
# the DMG from it. The app bundle's own name is the product name from
# `tauri.conf.json`, so both are globbed/derived rather than written out here --
# the same reason `current_dmg()` globs.
APP_BUNDLE_DIR = DESKTOP_DIR / "target" / "release" / "bundle" / "macos"
DMG_DIR = DESKTOP_DIR / "target" / "release" / "bundle" / "dmg"

# The packaged app's main binary, which is also the process that supervises the
# sidecar it spawns. Matched by name rather than path: the app can run from the
# mount point or from a build tree, and both own the Agent port the same way.
DESKTOP_SHELL = "wt-media-desktop-shell"


def log(message: str) -> None:
    print(f"\n== {message} ==")


def ensure_dirs() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    PID_DIR.mkdir(parents=True, exist_ok=True)
    (CLOUD_DIR / ".cache" / "go-build").mkdir(parents=True, exist_ok=True)


def env_with(base: dict[str, str] | None = None, **kwargs: str) -> dict[str, str]:
    env = os.environ.copy()
    if base:
        env.update(base)
    env.update({k: v for k, v in kwargs.items() if v is not None})
    return env


def local_douyin_env() -> dict[str, str]:
    """Load repo-local Douyin credentials without putting them in source or Git.

    Explicit process environment variables always win. The file is intentionally
    limited to the Cloud crawler settings and must be owner-readable only.
    """
    if not DOUYIN_ENV_FILE.is_file():
        return {}
    permissions = DOUYIN_ENV_FILE.stat().st_mode & 0o777
    if permissions & 0o077:
        raise RuntimeError(
            f"Douyin env file must be owner-readable only (chmod 600): {DOUYIN_ENV_FILE}"
        )
    allowed = {
        "WT_MEDIA_DOUYIN_API_BASE",
        "WT_MEDIA_DOUYIN_API_KEY",
        "WT_MEDIA_DOUYIN_COOKIE",
        "WT_MEDIA_DOUYIN_AUTHOR_ENDPOINT",
    }
    values: dict[str, str] = {}
    for raw_line in DOUYIN_ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key not in allowed:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        values[key] = value
    return values


def cloud_runtime_env(**kwargs: str) -> dict[str, str]:
    """Build Cloud env with explicit shell variables taking precedence."""
    env = env_with(**kwargs)
    for key, value in local_douyin_env().items():
        env.setdefault(key, value)
    return env


def run(cmd: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    print("+ " + " ".join(cmd))
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, env=env, check=True)


def http_json(url: str, timeout: float = 3.0) -> dict[str, object]:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
    return json.loads(raw)


def http_answers(url: str, timeout: float = 2.0) -> bool:
    """Whether anything HTTP answers at `url`, whatever the status code.

    A 401 is an answer. The packaged Agent only talks to callers holding the
    per-launch token Desktop generates and hands to it, so an unauthenticated
    probe from here is *expected* to be refused -- `src-tauri/src/commands/agent.rs`
    makes the same distinction, treating any HTTP answer as "something is
    listening" while `sidecar::readiness` asks the different question of whether
    the Agent can be used. Asking the second question here would report a healthy
    environment as down.
    """
    try:
        urllib.request.urlopen(url, timeout=timeout)
        return True
    except urllib.error.HTTPError:
        return True
    except Exception:  # noqa: BLE001 - no answer is the reading this reports.
        return False


def wait_http(url: str, name: str, timeout_seconds: float = 20.0) -> None:
    deadline = time.time() + timeout_seconds
    last_error = ""
    while time.time() < deadline:
        try:
            http_json(url)
            print(f"{name}: PASS {url}")
            return
        except Exception as exc:  # noqa: BLE001 - report last readiness failure.
            last_error = str(exc)
            time.sleep(0.25)
    raise RuntimeError(f"{name}: FAIL {url}: {last_error}")


def process_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def pid_alive(pid_file: Path) -> bool:
    if not pid_file.exists():
        return False
    try:
        return process_alive(int(pid_file.read_text(encoding="utf-8").strip()))
    except ValueError:
        return False


def close_desktop_app() -> None:
    """Close the packaged app and wait for the Agent port it supervises to free.

    The app owns its Agent's lifecycle -- `src-tauri` starts, supervises and
    stops the sidecar itself -- so the order matters in both directions: killing
    the sidecar behind the app's back gets it restarted, and launching an app
    while the previous one's sidecar still holds the port leaves the new one with
    nothing to bind.
    """
    subprocess.run(["pkill", "-f", DESKTOP_SHELL], check=False)
    deadline = time.time() + 15.0
    while time.time() < deadline and lsof_listener_pids(AGENT_PORT):
        time.sleep(0.3)
    stop_listener(AGENT_PORT, "agent port")
    wait_port_free(AGENT_PORT)


def hand_over_agent_port() -> None:
    """Stop this script's Agent so the app's own Agent can hold `AGENT_PORT`.

    Only one process can listen there, and which one it is decides whether the
    environment has a local executor at all. The python Agent started here is an
    API-only stand-in: it answers `/healthz` and `/status` but runs no task loop
    (`wt_media_agent/bootstrap/cloud.py` claims nothing without a credential
    delivered by Desktop). The app ships the real one -- its bundled config sets
    `python_fallback = false`, so inside a bundle the packaged sidecar is the only
    Agent there is.

    Left in place, the stand-in costs the walkthrough its executor: measured
    2026-10-02, the freshly packaged sidecar started, failed to bind with
    `OSError: [Errno 48] Address already in use`, and was stopped by the app's own
    supervisor -- so the queued `local_agent` download had no claimant while
    every health check in this script read green.
    """
    log("Handing the Agent port to the Desktop app")
    pid_file = PID_DIR / "agent.pid"
    if pid_alive(pid_file):
        pid = int(pid_file.read_text(encoding="utf-8").strip())
        os.kill(pid, signal.SIGTERM)
        print(f"agent: stopped pid {pid} from pid file")
    pid_file.unlink(missing_ok=True)
    stop_listener(AGENT_PORT, "agent")
    wait_port_free(AGENT_PORT)


def start_background(name: str, cmd: list[str], cwd: Path, env: dict[str, str]) -> None:
    ensure_dirs()
    pid_file = PID_DIR / f"{name}.pid"
    log_file = LOG_DIR / f"{name}.log"
    if pid_alive(pid_file):
        print(f"{name}: existing pid {pid_file.read_text(encoding='utf-8').strip()}")
        return
    with log_file.open("ab") as log_handle:
        child = subprocess.Popen(
            cmd,
            cwd=str(cwd),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=log_handle,
            stderr=log_handle,
            start_new_session=True,
        )
    pid_file.write_text(f"{child.pid}\n", encoding="utf-8")
    print(f"{name}: started pid {child.pid}, log {log_file}")


def run_migrations() -> None:
    log("Running Cloud migrations")
    run(
        ["scripts/migrate.sh"],
        cwd=CLOUD_DIR,
        env=env_with(
            GOROOT=GOROOT,
            GOPATH=GOPATH,
            GOCACHE=str(CLOUD_DIR / ".cache" / "go-build"),
            WT_MEDIA_MYSQL_DSN=MYSQL_DSN,
        ),
    )


def start_cloud() -> None:
    try:
        wait_http(f"{CLOUD_BASE_URL}/api/v1/health", "Cloud already healthy", timeout_seconds=1.0)
        return
    except Exception:
        pass
    log(f"Starting Cloud on {CLOUD_ADDR}")
    start_background(
        "cloud",
        [str(GO_BIN), "run", "./cmd/server"],
        CLOUD_DIR,
        cloud_runtime_env(
            GOROOT=GOROOT,
            GOPATH=GOPATH,
            GOCACHE=str(CLOUD_DIR / ".cache" / "go-build"),
            WT_MEDIA_CLOUD_HTTP_ADDR=CLOUD_ADDR,
            WT_MEDIA_MYSQL_DSN=MYSQL_DSN,
            WT_MEDIA_SESSION_COOKIE_SECURE="false",
        ),
    )
    wait_http(f"{CLOUD_BASE_URL}/api/v1/health", "Cloud")


def start_worker() -> None:
    """Start the Cloud worker as a managed component.

    The worker is where Cloud's polled jobs live -- `discovery-worker`,
    `material-prepare-worker` and `transfer-reconcile` are all registered on this
    one entry point (internal/bootstrap/jobs.go). `cmd/server` runs none of them,
    so before this component existed an environment could report healthy and
    still have no executor for anything Cloud prepares.

    The scheduler process (`cmd/discovery-scheduler`) is deliberately left out:
    it only enqueues new discoveries on a timer, which is noise for a local
    review environment and unrelated to whether work already queued gets done.
    """
    log("Building and starting Cloud worker")
    run(
        [str(GO_BIN), "build", "-o", str(WORKER_BIN), "./cmd/discovery-worker"],
        cwd=CLOUD_DIR,
        env=env_with(
            GOROOT=GOROOT,
            GOPATH=GOPATH,
            GOCACHE=str(CLOUD_DIR / ".cache" / "go-build"),
        ),
    )
    start_background("worker", [str(WORKER_BIN)], CLOUD_DIR, env_with())


def start_agent() -> None:
    """Start this script's Agent, taking the Agent port if the app is holding it.

    One Agent fits on the port and the two are alternatives rather than
    neighbours: this is the headless environment, so it takes the port back. Left
    running, the app's Agent would keep the port and the Agent started below would
    die on `Address already in use` while `start_background` recorded its pid as
    if it had started -- and the checks that read the Agent's own state would be
    reading a caller it refuses (`verify_bitbrowser`).
    """
    if pid_alive(PID_DIR / "agent.pid"):
        return
    close_desktop_app()
    log(f"Starting Agent on {AGENT_ADDR}")
    start_background(
        "agent",
        [
            str(AGENT_PYTHON),
            "-m",
            "wt_media_agent.local_api.server",
            "--host",
            AGENT_HOST,
            "--port",
            AGENT_PORT,
        ],
        AGENT_DIR,
        env_with(
            PYTHONPATH="src",
            WT_MEDIA_AGENT_LOG_LEVEL="INFO",
            WT_MEDIA_BITBROWSER_API_URL=BIT_API_URL,
        ),
    )
    wait_http(f"{AGENT_BASE_URL}/healthz", "Agent")


def verify_bitbrowser() -> None:
    log("Verifying BitBrowser through Agent")
    if not pid_alive(PID_DIR / "agent.pid"):
        # This reads the Agent's own view of BitBrowser, so it needs an Agent it
        # can query -- and after `launch-dmg` the port belongs to the packaged
        # app's, which refuses a caller without its token. Naming that beats
        # turning a 401 into "BitBrowser is not normal".
        raise RuntimeError(
            f"BitBrowser via Agent: cannot check -- {AGENT_ADDR} is not this script's "
            "Agent (the Desktop app's is serving it); start the headless environment "
            "with `bin/control.sh start`, or read it from the app"
        )
    data = http_json(f"{AGENT_BASE_URL}/api/v1/status")
    status = (data.get("data") or {}).get("bitbrowser_status") if isinstance(data.get("data"), dict) else None
    if status != "normal":
        raise RuntimeError(f"BitBrowser via Agent: FAIL status={status!r}")
    print("BitBrowser via Agent: PASS")


def verify_assets() -> None:
    log("Verifying Desktop assets")
    index = DESKTOP_DIR / ".generated" / "frontend" / "index.html"
    if not index.is_file() or index.stat().st_size == 0:
        raise RuntimeError(f"Desktop assets: missing {index}")
    assets_dir = DESKTOP_DIR / ".generated" / "frontend" / "assets"
    javascript_assets = assets_dir.glob("*.js")
    if not any(
        "127.0.0.1:18080/api/v1" in path.read_text(encoding="utf-8", errors="ignore")
        for path in javascript_assets
    ):
        raise RuntimeError("Desktop assets: packaged API base not found in JavaScript assets")
    check_fresh(index, [(CLOUD_DIR, ("web",))], "Desktop assets")
    print("Desktop assets: PASS")


def current_dmg() -> Path:
    """The freshest built DMG.

    The filename embeds the product name and version
    (WT Media_0.1.0_aarch64.dmg -> 起飞_0.1.0_aarch64.dmg), so it is found by glob
    rather than hardcoded: a rename or version bump must not break the script.
    """
    candidates = sorted(
        DMG_DIR.glob("*.dmg"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    if not candidates:
        raise RuntimeError(f"DMG: no *.dmg under {DMG_DIR}")
    return candidates[0]


def verify_dmg() -> None:
    log("Verifying DMG")
    dmg = current_dmg()
    if dmg.stat().st_size == 0:
        raise RuntimeError(f"DMG: empty {dmg}")
    check_fresh(dmg, [(CLOUD_DIR, ("web",)), (DESKTOP_DIR, ("src-tauri",))], "DMG")
    print(f"DMG: PASS {dmg}")


def clean_artifacts() -> None:
    log("Cleaning generated Desktop artifacts")
    targets = [
        DESKTOP_DIR / ".generated" / "frontend",
        CLOUD_DIR / "web" / "dist-desktop",
        DMG_DIR,
        APP_BUNDLE_DIR,
    ]
    for target in targets:
        if target.exists():
            run(["rm", "-rf", str(target)])


def build_dmg() -> None:
    """Build the DMG in the shape the app's own integrity check accepts.

    `cargo tauri build --bundles dmg` produces a bundle with no
    `Contents/Resources/sidecar-manifest.json`, and *inside a bundle* that file is
    what `src-tauri/src/sidecar/integrity.rs` reads before it will start the Agent:
    bundle + sidecar + no record is a refusal, not a warning. Measured on the
    2026-10-02 build -- the packaged app logged "包内缺少记录文件" from 21:52 on and
    never claimed a task, so the one `local_agent` download in the queue sat there
    while every health check in this script read green.

    The record is written by `scripts/repair-macos-signing.sh`, which belongs to
    the release path -- that is why a plain `--bundles dmg` never runs it. The
    sequence below mirrors `scripts/build-release-macos.sh`, minus
    `stage-release-config.sh`: that one rebuilds the sidecar against
    `config_online/`, and this environment is deliberately built against the local
    config.
    """
    clean_artifacts()
    log("Building Desktop frontend")
    run(["bash", str(SCRIPT_DIR / "build-desktop-frontend.sh")])
    log("Building Desktop app bundle")
    run(["cargo", "tauri", "build", "--bundles", "app", "--no-sign"], cwd=DESKTOP_DIR)
    apps = sorted(APP_BUNDLE_DIR.glob("*.app"))
    if len(apps) != 1:
        raise RuntimeError(
            f"Desktop app bundle: expected one .app under {APP_BUNDLE_DIR}, "
            f"found {[p.name for p in apps]}"
        )
    app = apps[0]
    log("Writing the sidecar record into the bundle and re-signing")
    run(["bash", str(DESKTOP_DIR / "scripts" / "repair-macos-signing.sh"), str(app)])
    dmg = _dmg_path(app)
    log("Packing the DMG")
    staging = Path(tempfile.mkdtemp(prefix="wt-media-dmg.", dir="/private/tmp"))
    try:
        run(["cp", "-R", str(app), str(staging / app.name)])
        (staging / "Applications").symlink_to("/Applications")
        DMG_DIR.mkdir(parents=True, exist_ok=True)
        run([
            "hdiutil", "create", "-volname", app.stem, "-srcfolder", str(staging),
            "-ov", "-format", "UDZO", str(dmg),
        ])
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def _dmg_path(app: Path) -> Path:
    """Where this script's DMG goes, named the way the release path names it.

    `<product>_<version>_<arch>.dmg` -- the product name is the app bundle's own
    name and the version comes from `tauri.conf.json`, so a rename or a version
    bump lands in the filename instead of breaking it.
    """
    config = json.loads((DESKTOP_DIR / "src-tauri" / "tauri.conf.json").read_text(encoding="utf-8"))
    arch = {"arm64": "aarch64", "x86_64": "x64"}.get(os.uname().machine, os.uname().machine)
    return DMG_DIR / f"{app.stem}_{config['version']}_{arch}.dmg"


def rebuild_cloud_dist() -> None:
    log("Regenerating Cloud dist-desktop artifact copy")
    run(["npm", "run", "build:desktop"], cwd=CLOUD_DIR / "web")


def launch_dmg() -> None:
    log("Launching latest DMG")
    dmg = current_dmg()
    close_desktop_app()
    # Mount at a fixed private mountpoint and detach it first: a leftover
    # /Volumes/<product> mount from an earlier run could otherwise be opened
    # instead of the fresh build, and its name is not scripted anywhere.
    subprocess.run(
        ["hdiutil", "detach", str(DMG_MOUNT)],
        check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    DMG_MOUNT.mkdir(parents=True, exist_ok=True)
    run(["hdiutil", "attach", "-mountpoint", str(DMG_MOUNT), str(dmg)])
    apps = sorted(DMG_MOUNT.glob("*.app"))
    if len(apps) != 1:
        raise RuntimeError(
            f"DMG mount: expected one .app under {DMG_MOUNT}, found {[p.name for p in apps]}"
        )
    # After the mount, before the app opens: the app's own Agent needs the port,
    # and the mounted bundle is the only place the packaged sidecar lives.
    hand_over_agent_port()
    run(["open", str(apps[0])])


def verify_worker() -> None:
    """Refuse a "ready" environment whose Cloud-side jobs have no runner.

    Nothing else in this script can tell the difference: a worker that was never
    started leaves health endpoints green, assets fresh and the DMG launchable
    (CHG-20260930-069 measured exactly that -- a cloud-scope preparation sat
    `pending` for five minutes with every other check passing).
    """
    log("Verifying Cloud worker")
    pid_file = PID_DIR / "worker.pid"
    if not pid_alive(pid_file):
        raise RuntimeError(
            f"Cloud worker: not running (pid file {pid_file}); "
            "start the environment with `bin/control.sh start` before verifying"
        )
    print(f"Cloud worker: PASS pid={pid_file.read_text(encoding='utf-8').strip()}")


def verify_agent() -> None:
    """The Agent endpoint, accepting either of the two providers that can hold it.

    This script's python Agent answers 2xx. The packaged Desktop app's refuses
    callers without the per-launch token Desktop generates, so its correct answer
    to this probe is 401 -- see `http_answers`. Which provider is up is not
    something this check decides; it only refuses to call "nothing listening"
    healthy.
    """
    log("Verifying Local Agent")
    if pid_alive(PID_DIR / "agent.pid"):
        wait_http(f"{AGENT_BASE_URL}/healthz", "Agent")
        return
    if http_answers(f"{AGENT_BASE_URL}/healthz"):
        print(f"Agent: PASS {AGENT_BASE_URL}/healthz (served by the Desktop app)")
        return
    raise RuntimeError(f"Agent: FAIL {AGENT_BASE_URL}/healthz: nothing is listening")


def verify_all() -> None:
    log("Verifying local M2-B environment")
    wait_http(f"{CLOUD_BASE_URL}/api/v1/health", "Cloud")
    verify_agent()
    verify_worker()
    verify_bitbrowser()
    verify_assets()
    verify_dmg()


def cmd_status() -> int:
    """Report Cloud/Agent/Worker liveness without changing anything.

    This is the reading behind `bin/control.sh status`. It is deliberately a
    query: it never starts, stops, or waits on anything, so calling it is safe
    on a machine where nothing is running. Prints one line per component and
    returns 1 when any of them is not alive -- and, where the component serves
    one, not answering, so the exit code is usable from a shell (the same verb
    in the other three repositories' `bin/control.sh` has the same contract).

    The worker's `url` is `None`: it is a poller, not a server, so it has no
    endpoint to answer on and its process is the whole of its liveness. Reading
    that as anything but a probe would be inventing a health check it does not
    have.

    The Agent is the one component with two possible providers. After
    `launch-dmg` the port belongs to the packaged app, which runs its own Agent
    there -- so "no pid file, but something answers" is the intended state rather
    than a fault, and the line says who owns it instead of leaving the reader to
    guess from a `pid=-` next to a status. That state prints
    `health=refused owner=desktop`: the app's Agent only talks to callers holding
    the per-launch token Desktop generates, so 401 is its correct answer to this
    probe (`http_answers`). `alive` still reports this script's process
    truthfully -- it is not alive, it just is not the one being asked about.
    """
    log("Local M2-B environment status")
    all_healthy = True
    for name, pid_file, url in (
        ("cloud", PID_DIR / "cloud.pid", f"{CLOUD_BASE_URL}/api/v1/health"),
        ("agent", PID_DIR / "agent.pid", f"{AGENT_BASE_URL}/healthz"),
        ("worker", PID_DIR / "worker.pid", None),
    ):
        pid_text = (
            pid_file.read_text(encoding="utf-8").strip() if pid_file.exists() else "-"
        )
        alive = pid_alive(pid_file)
        if url is None:
            health = "pid-only"
        else:
            try:
                http_json(url, timeout=2.0)
                health = "ok"
            except Exception:  # noqa: BLE001 - a down probe is a reading, not a failure.
                health = "down"
        served_by_desktop = name == "agent" and not alive and http_answers(url)
        owner = " owner=desktop" if served_by_desktop else ""
        if served_by_desktop:
            # The app's Agent refuses an unauthenticated probe, so `health` above is
            # `down` and would be the wrong reading to print next to `owner=desktop`.
            health = "refused"
        all_healthy = (
            all_healthy
            and health in ("ok", "pid-only", "refused")
            and (alive or served_by_desktop)
        )
        print(
            f"{name}: pid={pid_text} alive={'yes' if alive else 'no'} "
            f"health={health} url={url or '-'}{owner}"
        )
    return 0 if all_healthy else 1


def lsof_listener_pids(port: str) -> list[str]:
    # `-tiTCP:<port>` and `-sTCP:LISTEN` must each stay a single argv element;
    # lsof otherwise treats `:port` as a file path and exits nonzero.
    result = subprocess.run(
        ["lsof", f"-tiTCP:{port}", "-sTCP:LISTEN"],
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in result.stdout.split() if line.strip().isdigit()]


def stop_listener(port: str, label: str) -> None:
    """Kill whatever currently listens on the given port, PID-file or not.

    A stale Cloud/Agent started manually (no PID file) would otherwise survive
    `--force-restart` and keep serving old code.
    """
    for pid in lsof_listener_pids(port):
        try:
            os.kill(int(pid), signal.SIGTERM)
            print(f"{label}: stopped pid {pid} on :{port}")
        except OSError:
            pass


def wait_port_free(port: str, timeout_seconds: float = 10.0) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if not lsof_listener_pids(port):
            return
        time.sleep(0.3)


def stop_started() -> None:
    log("Stopping stale Cloud/Agent/Worker processes")
    # First, so the port sweep below is final rather than a race with a supervisor
    # that would start the Agent again.
    close_desktop_app()
    signalled: list[tuple[str, int]] = []
    for name in ["cloud", "agent", "worker"]:
        pid_file = PID_DIR / f"{name}.pid"
        if pid_alive(pid_file):
            pid = int(pid_file.read_text(encoding="utf-8").strip())
            os.kill(pid, signal.SIGTERM)
            signalled.append((name, pid))
            print(f"{name}: stopped pid {pid} from pid file")
        pid_file.unlink(missing_ok=True)
    stop_listener(CLOUD_PORT, "cloud")
    wait_port_free(CLOUD_PORT)
    stop_listener(AGENT_PORT, "agent")
    wait_port_free(AGENT_PORT)
    # Cloud and the Agent are each swept a second time by port above, so a
    # SIGTERM they ignored still gets caught. The worker holds no port and the
    # pid file is gone by now, which makes this wait the only thing standing
    # between "asked to stop" and "did stop" -- and a surviving worker would go
    # on draining queues with nothing left to find it by.
    for name, pid in signalled:
        if name != "worker":
            continue
        deadline = time.time() + 10.0
        while time.time() < deadline and process_alive(pid):
            time.sleep(0.2)
        if process_alive(pid):
            print(f"worker: pid {pid} ignored SIGTERM and is still running", file=sys.stderr)


def source_commit_epoch(repo_dir: Path, paths: tuple[str, ...] = ()) -> float:
    """Epoch of the newest commit in repo_dir touching `paths` (or the repo HEAD).

    Scoping to the paths that feed a build artifact avoids false staleness from
    unrelated commits (e.g. a skill-sync commit invalidating a DMG).
    """
    cmd = ["git", "-C", str(repo_dir), "log", "-1", "--format=%ct"]
    if paths:
        cmd.append("--")
        cmd.extend(paths)
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    out = result.stdout.strip()
    return float(out) if out else 0.0


def check_fresh(path: Path, sources: list[tuple[Path, tuple[str, ...]]], label: str) -> None:
    if not path.exists() or path.stat().st_size == 0:
        raise RuntimeError(f"{label}: missing or empty {path}")
    newest_source = max(source_commit_epoch(repo, paths) for repo, paths in sources)
    if path.stat().st_mtime < newest_source:
        raise RuntimeError(
            f"{label}: stale build (mtime {path.stat().st_mtime:.0f} "
            f"< newest source commit {newest_source:.0f})"
        )
    print(f"{label}: fresh")


def verify_login() -> None:
    log("Verifying login smoke")
    username = os.environ.get("WT_MEDIA_LOGIN_USER", "admin")
    password = os.environ.get("WT_MEDIA_LOGIN_PASSWORD", "admin123")
    req = json.dumps(
        {"username": username, "password": password, "replace_existing": True}
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{CLOUD_BASE_URL}/api/v1/auth/login",
        data=req,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        body = json.loads(response.read().decode("utf-8"))
    if body.get("errcode") != 0:
        raise RuntimeError(
            f"Login smoke: FAIL errcode={body.get('errcode')} message={body.get('message')!r}"
        )
    print(f"Login smoke: PASS user={username}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare and verify WT Media M2-B local acceptance environment.")
    parser.add_argument(
        "command",
        choices=["up", "verify", "status", "build-dmg", "launch-dmg", "all", "stop"],
        help="workflow command to execute",
    )
    parser.add_argument(
        "--force-restart",
        action="store_true",
        help="stop stale Cloud/Agent processes before starting",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.force_restart:
            stop_started()
        if args.command == "up":
            run_migrations()
            start_cloud()
            start_worker()
            start_agent()
            verify_bitbrowser()
        elif args.command == "verify":
            verify_all()
            verify_login()
        elif args.command == "status":
            return cmd_status()
        elif args.command == "build-dmg":
            build_dmg()
            rebuild_cloud_dist()
        elif args.command == "launch-dmg":
            launch_dmg()
        elif args.command == "all":
            run_migrations()
            start_cloud()
            start_worker()
            start_agent()
            verify_bitbrowser()
            build_dmg()
            rebuild_cloud_dist()
            verify_all()
            verify_login()
            # Last, and not merely for tidiness: launching hands the Agent port to
            # the app, after which the checks above cannot run -- they need an
            # Agent they can query, and the app's refuses callers without the token
            # Desktop generates per launch. Everything this script can verify, it
            # verifies before the handover.
            launch_dmg()
        elif args.command == "stop":
            stop_started()
    except (subprocess.CalledProcessError, RuntimeError, urllib.error.URLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
