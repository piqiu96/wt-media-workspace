#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
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

GO_BIN = Path(os.environ.get("GO_BIN", "/Users/aqiuye/Develop/workspace/devenv/go26/go/bin/go"))
GOROOT = os.environ.get("GOROOT", "/Users/aqiuye/Develop/workspace/devenv/go26/go")
GOPATH = os.environ.get("GOPATH", "/Users/aqiuye/Develop/workspace/devenv/go19/gopath")
AGENT_PYTHON = Path(os.environ.get("PYTHON_BIN", AGENT_DIR / ".venv" / "bin" / "python"))
DMG_PATH = DESKTOP_DIR / "target" / "release" / "bundle" / "dmg" / "WT Media_0.1.0_aarch64.dmg"


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


def run(cmd: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    print("+ " + " ".join(cmd))
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, env=env, check=True)


def http_json(url: str, timeout: float = 3.0) -> dict[str, object]:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
    return json.loads(raw)


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


def pid_alive(pid_file: Path) -> bool:
    if not pid_file.exists():
        return False
    try:
        os.kill(int(pid_file.read_text(encoding="utf-8").strip()), 0)
        return True
    except (OSError, ValueError):
        return False


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
        env_with(
            GOROOT=GOROOT,
            GOPATH=GOPATH,
            GOCACHE=str(CLOUD_DIR / ".cache" / "go-build"),
            WT_MEDIA_CLOUD_HTTP_ADDR=CLOUD_ADDR,
            WT_MEDIA_MYSQL_DSN=MYSQL_DSN,
            WT_MEDIA_SESSION_COOKIE_SECURE="false",
        ),
    )
    wait_http(f"{CLOUD_BASE_URL}/api/v1/health", "Cloud")


def start_agent() -> None:
    try:
        wait_http(f"{AGENT_BASE_URL}/healthz", "Agent already healthy", timeout_seconds=1.0)
        return
    except Exception:
        pass
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
    if not any("127.0.0.1:18080/api/v1" in path.read_text(encoding="utf-8", errors="ignore") for path in assets_dir.glob("http-*.js")):
        raise RuntimeError("Desktop assets: packaged API base not found in http chunk")
    print("Desktop assets: PASS")


def verify_dmg() -> None:
    log("Verifying DMG")
    if not DMG_PATH.is_file() or DMG_PATH.stat().st_size == 0:
        raise RuntimeError(f"DMG: missing {DMG_PATH}")
    print(f"DMG: PASS {DMG_PATH}")


def clean_artifacts() -> None:
    log("Cleaning generated Desktop artifacts")
    targets = [
        DESKTOP_DIR / ".generated" / "frontend",
        CLOUD_DIR / "web" / "dist-desktop",
        DESKTOP_DIR / "target" / "release" / "bundle" / "dmg",
        DESKTOP_DIR / "target" / "release" / "bundle" / "macos",
    ]
    for target in targets:
        if target.exists():
            run(["rm", "-rf", str(target)])


def build_dmg() -> None:
    clean_artifacts()
    log("Building Desktop DMG")
    run([str(SCRIPT_DIR / "build-desktop.sh")])
    run(["cargo", "tauri", "build", "--bundles", "dmg", "--no-sign"], cwd=DESKTOP_DIR)


def rebuild_cloud_dist() -> None:
    log("Regenerating Cloud dist-desktop artifact copy")
    run(["npm", "run", "build:desktop"], cwd=CLOUD_DIR / "web")


def launch_dmg() -> None:
    log("Launching latest DMG")
    subprocess.run(["pkill", "-f", "wt-media-desktop-shell"], check=False)
    for volume in ["/Volumes/WT Media", "/Volumes/WT Media 1"]:
        subprocess.run(["hdiutil", "detach", volume], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    run(["hdiutil", "attach", str(DMG_PATH)])
    run(["open", "/Volumes/WT Media/WT Media.app"])


def verify_all() -> None:
    log("Verifying local M2-B environment")
    wait_http(f"{CLOUD_BASE_URL}/api/v1/health", "Cloud")
    wait_http(f"{AGENT_BASE_URL}/healthz", "Agent")
    verify_bitbrowser()
    verify_assets()
    verify_dmg()


def stop_started() -> None:
    log("Stopping processes started by this script")
    for name in ["cloud", "agent"]:
        pid_file = PID_DIR / f"{name}.pid"
        if pid_alive(pid_file):
            pid = int(pid_file.read_text(encoding="utf-8").strip())
            os.kill(pid, signal.SIGTERM)
            print(f"{name}: stopped {pid}")
        pid_file.unlink(missing_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare and verify WT Media M2-B local acceptance environment.")
    parser.add_argument(
        "command",
        choices=["up", "verify", "build-dmg", "launch-dmg", "all", "stop"],
        help="workflow command to execute",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "up":
            run_migrations()
            start_cloud()
            start_agent()
            verify_bitbrowser()
        elif args.command == "verify":
            verify_all()
        elif args.command == "build-dmg":
            build_dmg()
            rebuild_cloud_dist()
        elif args.command == "launch-dmg":
            launch_dmg()
        elif args.command == "all":
            run_migrations()
            start_cloud()
            start_agent()
            verify_bitbrowser()
            build_dmg()
            launch_dmg()
            rebuild_cloud_dist()
            verify_all()
        elif args.command == "stop":
            stop_started()
    except (subprocess.CalledProcessError, RuntimeError, urllib.error.URLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
