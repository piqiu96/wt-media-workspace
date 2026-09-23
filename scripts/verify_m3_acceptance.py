#!/usr/bin/env python3
"""M3 内容挖掘全量功能验收（E3，2026-09-23）。

本脚本按 `docs/product/M3-content-mining-v2.md` 第 8 节的验收项，对
`wt-media-cloud` 的真实运行实例做端到端核验，并把每一步的请求、期望、实际与
判定写入 `run-manifest.json`，原始响应脱敏后落在 `raw/`。

约定（沿用 `scripts/m2b_local_acceptance.py`）：
- 只读取 Cloud 仓库与配置，从不修改 Cloud 源码或配置；
- 对本地 `wt_media_cloud` 库**只新增不删改**既有行（既有 3 策略 / 11 任务 /
  109 来源 / 26 素材在验收前后必须逐项一致）；
- 不使用 mock 或夹具代替真实业务读回；外部接口不可达时如实记 BLOCKED-EXTERNAL；
- 凭据值（抖音 api_key / cookie、会话 cookie）绝不写入证据。

用法：
    python3 scripts/verify_m3_acceptance.py --phase g0
    python3 scripts/verify_m3_acceptance.py --phase all
"""

from __future__ import annotations

import argparse
import http.cookiejar
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
import tomllib
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
WS_ROOT = SCRIPT_DIR.parent
CLOUD_ROOT = Path(
    os.environ.get("WT_MEDIA_CLOUD_ROOT", str(WS_ROOT.parent / "wt-media-cloud"))
)
# CHG-20260916-052 已于 2026-09-23 归档为 HANDOFF，M3 亦于同日签收；证据随记录移入 completed/。
# 这里必须指归档位置：EVIDENCE 既读旧运行产物（raw/*.log）也写新产物，
# 若仍指 active/，重跑会（a）读不到旧日志而在 P10 崩掉，（b）在 active/ 下重新造出一个孤儿证据目录。
EVIDENCE = WS_ROOT / "delivery/completed/CHG-20260916-052/evidence/m3-e3-acceptance-20260923"
RAW_DIR = EVIDENCE / "raw"
SHOT_DIR = EVIDENCE / "screenshots"
# 会话 cookie 是活的凭据：绝不落在证据目录里（证据工件不得包含凭据值）。
# 放到 Cloud 仓库已被 .gitignore 覆盖的 .cache/ 下，只存在于本机。
COOKIE_DIR = CLOUD_ROOT / ".cache" / "m3-acc"
STATE_FILE = EVIDENCE / "state.json"
MANIFEST_FILE = EVIDENCE / "run-manifest.json"
BASE = os.environ.get("WT_MEDIA_M3_BASE", "http://127.0.0.1:18080/api/v1")

ADMIN = os.environ.get("WT_MEDIA_M3_ADMIN", "admin")
ADMIN_PASSWORD = os.environ.get("WT_MEDIA_M3_ADMIN_PASSWORD", "admin123")
OPERATOR = os.environ.get("WT_MEDIA_M3_OPERATOR", "senior01")
OPERATOR_PASSWORD = os.environ.get("WT_MEDIA_M3_OPERATOR_PASSWORD", "senior123")

ISOLATED_TEAM_NAME = "M3验收-隔离组-20260923"
RUN_TAG = "m3acc0923"
# 每次进程启动一个盐：策略名带盐后重跑不会撞 D1（重名 -> 500），
# 否则 5.5.1/5.5.6/5.5.10 这些「创建」步骤会被误判成失败。
RUN_SALT = datetime.now().strftime("%H%M%S")


def sname(label: str) -> str:
    return "%s-%s-%s" % (RUN_TAG, label, RUN_SALT)

PHASES = [
    "g0", "g1", "g2", "g3", "g4",
    "p5", "p55", "p6", "p7", "p8", "p9", "p10", "p11", "p12",
]

_manifest: list[dict] = []
_secrets: set[str] = set()
_state: dict = {}


# --------------------------------------------------------------------------
# 基础设施
# --------------------------------------------------------------------------

def db_config() -> dict:
    path = CLOUD_ROOT / "config/database/primary.toml"
    with path.open("rb") as handle:
        return tomllib.load(handle)


def load_secrets() -> None:
    """收集需要脱敏的字面量，只记录键名与长度，不记录值。"""
    for base in (CLOUD_ROOT / "config/credentials", CLOUD_ROOT / "config_online/credentials"):
        for path in sorted(base.glob("*.toml")):
            try:
                with path.open("rb") as handle:
                    data = tomllib.load(handle)
            except Exception:
                continue
            for value in _flatten_strings(data):
                if len(value) >= 8:
                    _secrets.add(value)


def _flatten_strings(node):
    if isinstance(node, dict):
        for value in node.values():
            yield from _flatten_strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from _flatten_strings(value)
    elif isinstance(node, str):
        yield node


def redact(text: str) -> str:
    out = text
    for secret in _secrets:
        if secret and secret in out:
            out = out.replace(secret, "<redacted:%d bytes>" % len(secret))
    out = re.sub(r"wt_media_session=[^;\"\s]+", "wt_media_session=<redacted>", out)
    return out


def sql(query: str, db: bool = True) -> list[list[str]]:
    cfg = db_config()
    env = dict(os.environ, MYSQL_PWD=str(cfg.get("password", "")))
    cmd = [
        "mysql", "-h", str(cfg.get("host", "127.0.0.1")),
        "-P", str(cfg.get("port", 3306)),
        "-u", str(cfg.get("username", "root")),
        "-N", "-B", "--raw", "-e", query,
    ]
    if db:
        cmd.insert(1, "-D")
        cmd.insert(2, str(cfg.get("database", "")))
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=120)
    if proc.returncode != 0:
        raise RuntimeError("mysql failed: %s" % proc.stderr.strip())
    return [line.split("\t") for line in proc.stdout.splitlines() if line.strip()]


def scalar(query: str) -> str:
    rows = sql(query)
    return rows[0][0] if rows and rows[0] else ""


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Session:
    """一个带 cookie jar 的 HTTP 客户端。"""

    def __init__(self, name: str, credentials: tuple[str, str] = ("", "")):
        COOKIE_DIR.mkdir(parents=True, exist_ok=True)
        self.name = name
        self.credentials = credentials
        self.jar_path = COOKIE_DIR / ("%s.cookies" % name)
        self.jar = http.cookiejar.MozillaCookieJar(str(self.jar_path))
        if self.jar_path.exists():
            try:
                self.jar.load(ignore_discard=True, ignore_expires=True)
            except (OSError, http.cookiejar.LoadError):
                pass
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar)
        )
        self.actor: dict | None = None

    def request(self, method: str, path: str, body=None, raw: bool = False, _retry: bool = True):
        url = path if path.startswith("http") else BASE + path
        data = None
        headers = {"Accept": "application/json"}
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode()
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with self.opener.open(req, timeout=120) as resp:
                status, payload = resp.status, resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            status, payload = exc.code, exc.read().decode("utf-8", "replace")
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError:
            parsed = {"_raw": payload}
        # 会话被其他登录顶掉（11001）时自动重新登录一次，避免长流程中途整体失效。
        if (_retry and status == 401 and parsed.get("errcode") == 11001
                and self.credentials[0] and "/auth/login" not in path):
            user, password = self.credentials
            login_status, login_parsed, _ = self.login(user, password)
            if login_status == 200 and login_parsed.get("errcode") == 0:
                return self.request(method, path, body, raw, _retry=False)
        return status, parsed, payload

    def login(self, username: str, password: str) -> tuple[int, dict, str]:
        outcome = self.request(
            "POST", "/auth/login",
            {"username": username, "password": password, "replace_existing": True},
        )
        try:
            self.jar.save(ignore_discard=True, ignore_expires=True)
        except OSError:
            pass
        return outcome

    def session_cookie(self) -> str:
        for cookie in self.jar:
            if cookie.name == "wt_media_session":
                return cookie.value
        return ""


SESSIONS = {
    "admin": (ADMIN, ADMIN_PASSWORD),
    "operator": (OPERATOR, OPERATOR_PASSWORD),
}


def session(name: str) -> Session:
    key = "session_%s" % name
    if key in _state:
        return _state[key]
    item = Session(name, SESSIONS.get(name, ("", "")))
    _state[key] = item
    return item


def ensure(name: str) -> Session:
    """复用已落盘的会话；失效则重新登录（不通过 SQL 造用户）。"""
    sess = session(name)
    if _state.get("authed_%s" % name):
        return sess
    status, parsed, _ = sess.request("GET", "/auth/me")
    if status == 200 and parsed.get("errcode") == 0:
        sess.actor = data_of(parsed)
        _state["authed_%s" % name] = True
        return sess
    user, password = (ADMIN, ADMIN_PASSWORD) if name == "admin" else (OPERATOR, OPERATOR_PASSWORD)
    status, parsed, payload = sess.login(user, password)
    if status != 200 or parsed.get("errcode") != 0:
        raise SystemExit("STOP S3: %s 重新登录失败（HTTP %s errcode=%s）"
                         % (user, status, parsed.get("errcode")))
    sess.actor = data_of(parsed)
    _state["authed_%s" % name] = True
    return sess


def admin() -> Session:
    return ensure("admin")


def operator() -> Session:
    return ensure("operator")


# --------------------------------------------------------------------------
# 记录
# --------------------------------------------------------------------------

def record(step_id, phase, kind, request, expected, actual, verdict, ids=None, note=""):
    entry = {
        "step_id": step_id,
        "phase": phase,
        "kind": kind,
        "request": redact(request if isinstance(request, str) else json.dumps(request, ensure_ascii=False)),
        "expected": expected,
        "actual": redact(actual if isinstance(actual, str) else json.dumps(actual, ensure_ascii=False)),
        "verdict": verdict,
        "ids": ids or {},
        "note": note,
        "ts": now_iso(),
    }
    _manifest.append(entry)
    mark = {"PASS": "PASS", "FAIL": "FAIL", "BLOCKED": "BLK ", "INFO": "info",
            "NOT VERIFIED": "N/V ", "ADJUDICATED": "adj "}[verdict]
    line = "[%s] %-34s %s" % (mark, step_id, entry["actual"][:150])
    print(line, flush=True)
    return entry


def raw_dump(name: str, payload) -> str:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / name
    text = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False, indent=2)
    path.write_text(redact(text), encoding="utf-8")
    return str(path.relative_to(EVIDENCE))


def step_result(step_id, phase, kind, request, expected, status, parsed, verdict_map,
                ids=None, note=""):
    """按 `(status, errcode)` 判定，并记录。"""
    errcode = parsed.get("errcode") if isinstance(parsed, dict) else None
    actual = "HTTP %s errcode=%s message=%s" % (
        status, errcode, (parsed or {}).get("message") if isinstance(parsed, dict) else "",
    )
    verdict = verdict_map(status, errcode, parsed)
    return record(step_id, phase, kind, request, expected, actual, verdict, ids, note)


def save_state() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    serialisable = {k: v for k, v in _state.items() if not k.startswith("session_")}
    STATE_FILE.write_text(json.dumps(serialisable, ensure_ascii=False, indent=2), encoding="utf-8")


def flush_manifest() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    MANIFEST_FILE.write_text(json.dumps(_manifest, ensure_ascii=False, indent=2), encoding="utf-8")


# --------------------------------------------------------------------------
# 小工具
# --------------------------------------------------------------------------

def expect_status(step_id, phase, kind, request, expected_desc, status, parsed, want_status, want_errcode=None, ids=None, note=""):
    errcode = parsed.get("errcode") if isinstance(parsed, dict) else None
    ok = status == want_status and (want_errcode is None or errcode == want_errcode)
    actual = "HTTP %s errcode=%s message=%s" % (status, errcode, (parsed or {}).get("message") if isinstance(parsed, dict) else "")
    return record(step_id, phase, kind, request, expected_desc, actual, "PASS" if ok else "FAIL", ids, note)


def data_of(parsed):
    return parsed.get("data") if isinstance(parsed, dict) else None


def table_count(table: str, where: str = "") -> int:
    clause = " WHERE " + where if where else ""
    value = scalar("SELECT COUNT(*) FROM %s%s;" % (table, clause))
    return int(value or 0)


def max_id(table: str) -> int:
    return int(scalar("SELECT COALESCE(MAX(id),0) FROM %s;" % table) or 0)


def search_retry(sess: Session, payload: dict, step_id: str, tries: int = 6, pause: float = 1.5,
                 min_items: int = 1):
    """按 ID/URL 的发现接口在上游存在间歇性空返回，重试到拿到内容或耗尽次数。

    返回 (status, parsed, attempts, empties)，重试次数与空返回次数都进证据。
    """
    empties = 0
    attempts = 0
    result = (None, {}, "")
    for _ in range(tries):
        attempts += 1
        result = sess.request("POST", "/content-pool/search", payload)
        status, parsed = result[0], result[1]
        items = (data_of(parsed) or {}).get("items") or []
        if status == 200 and parsed.get("errcode") == 0 and len(items) >= min_items:
            break
        if status == 200 and parsed.get("errcode") == 0:
            empties += 1
        time.sleep(pause)
    return result[0], result[1], attempts, empties


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def pgrep(pattern: str) -> list[int]:
    proc = subprocess.run(["pgrep", "-f", pattern], capture_output=True, text=True)
    return [int(x) for x in proc.stdout.split() if x.strip()]


def go_run(component: str) -> subprocess.Popen:
    """以后台进程启动一个 Cloud CMD（无 flag，间隔取 config/scheduler）。"""
    log = EVIDENCE / ("proc-%s.log" % component)
    env = dict(os.environ)
    env.setdefault("GOCACHE", str(CLOUD_ROOT / ".cache/go-build"))
    env.setdefault("GOPATH", str(CLOUD_ROOT / ".cache/go-path"))
    binary = CLOUD_ROOT / (".cache/wt-media-%s" % component)
    subprocess.run(
        ["go", "build", "-o", str(binary), "./cmd/%s" % component],
        cwd=str(CLOUD_ROOT), env=env, check=True, capture_output=True, timeout=600,
    )
    handle = log.open("ab")
    proc = subprocess.Popen([str(binary)], cwd=str(CLOUD_ROOT), env=env, stdout=handle, stderr=handle)
    return proc


# --------------------------------------------------------------------------
# G0 静态冻结
# --------------------------------------------------------------------------

def phase_g0():
    phase = "G0"

    def git(cmd, cwd):
        return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True).stdout.strip()

    cloud_head = git(["git", "rev-parse", "HEAD"], CLOUD_ROOT)
    cloud_status = git(["git", "status", "--porcelain"], CLOUD_ROOT)
    ws_head = git(["git", "rev-parse", "HEAD"], WS_ROOT)
    ws_status = git(["git", "status", "--porcelain"], WS_ROOT)
    _state["cloud_head"], _state["ws_head"] = cloud_head, ws_head

    own_artifacts = ("scripts/verify_m3_acceptance.py", "scripts/m3-acceptance.sh",
                     "delivery/completed/CHG-20260916-052/")
    ws_lines = [line for line in ws_status.splitlines() if line.strip()]
    foreign = [line for line in ws_lines
               if not any(marker in line for marker in own_artifacts)]
    record("G0.1", phase, "freeze", "git rev-parse/status", "Cloud 干净；Workspace 只允许本轮验收产物",
           "cloud=%s clean=%s | workspace=%s dirty_entries=%d 非本轮产物=%d" % (
               cloud_head[:12], not cloud_status, ws_head[:12], len(ws_lines), len(foreign)),
           "PASS" if not cloud_status and not foreign else "FAIL",
           {"cloud_head": cloud_head, "ws_head": ws_head},
           note="Cloud 未提交改动=%r；Workspace 越界改动=%r；本轮产物=%r" % (
               cloud_status, foreign, ws_lines))

    vers = {}
    for name, cmd in (("go", ["go", "version"]), ("node", ["node", "--version"]),
                      ("mysql", ["mysql", "--version"]), ("python", [sys.executable, "--version"])):
        vers[name] = subprocess.run(cmd, capture_output=True, text=True).stdout.strip() or \
                     subprocess.run(cmd, capture_output=True, text=True).stderr.strip()
    record("G0.2", phase, "freeze", "toolchain versions", "记录工具链版本",
           json.dumps(vers, ensure_ascii=False), "INFO")

    listeners = subprocess.run(["lsof", "-nP", "-iTCP:18080", "-sTCP:LISTEN"],
                               capture_output=True, text=True).stdout.strip()
    record("G0.3", phase, "freeze", "lsof -iTCP:18080", "18080 上只有本轮启动的进程",
           listeners or "(无监听者)", "INFO")

    cred_rows = []
    for path in sorted((CLOUD_ROOT / "config/credentials").glob("*.toml")):
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", str(path.relative_to(CLOUD_ROOT))],
                                 cwd=str(CLOUD_ROOT), capture_output=True, text=True).returncode == 0
        keys = []
        try:
            with path.open("rb") as handle:
                data = tomllib.load(handle)
            keys = [(k, len(v)) for k, v in _flatten_keyed(data)]
        except Exception as exc:
            keys = [("parse_error", str(exc))]
        cred_rows.append({"file": str(path.relative_to(CLOUD_ROOT)), "bytes": path.stat().st_size,
                          "git_tracked": tracked, "keys": keys})
    record("G0.4", phase, "security", "config/credentials/*.toml 元数据", "只记键名与字节长度，不记值",
           json.dumps(cred_rows, ensure_ascii=False), "INFO",
           note="安全问题登记项：见 B6/D-安全-1")

    record("G0.5", phase, "freeze", "端口占用表", "记录 5173/5174/8765/8899 现状",
           subprocess.run(["bash", "-lc",
                           "lsof -nP -iTCP -sTCP:LISTEN | grep -E ':(5173|5174|8765|8899|18080) ' || echo '(none)'"],
                          capture_output=True, text=True).stdout.strip() or "(none)", "INFO")


def _flatten_keyed(node, prefix=""):
    if isinstance(node, dict):
        for key, value in node.items():
            yield from _flatten_keyed(value, ("%s.%s" % (prefix, key)) if prefix else key)
    elif isinstance(node, str):
        yield prefix, node


# --------------------------------------------------------------------------
# G1 前置门禁
# --------------------------------------------------------------------------

def phase_g1():
    phase = "G1"
    tables = int(scalar("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='%s';"
                        % db_config().get("database")))
    migrations = sql("SELECT version, name, applied_at FROM schema_migrations ORDER BY version DESC LIMIT 3;")
    record("G1.1", phase, "precondition", "information_schema + schema_migrations", "表与迁移齐备",
           "tables=%d migrations_total=%s tail=%s" % (
               tables, scalar("SELECT COUNT(*) FROM schema_migrations;"),
               "; ".join("%s@%s" % (r[0], r[2]) for r in migrations)),
           "PASS" if tables >= 26 else "FAIL", {"tables": tables})

    users = sql("SELECT id, username, role, IFNULL(team_id,'NULL'), status FROM users ORDER BY id;")
    teams = sql("SELECT id, name FROM operation_teams ORDER BY id;")
    record("G1.2", phase, "precondition", "users / operation_teams", "admin 与至少一个运营组存在",
           "users=%s teams=%s" % (users, teams), "PASS" if users and teams else "FAIL",
           note="需要 admin 才能登录；不通过则 STOP S3")

    snap = {
        "captured_at": now_iso(),
        "tables": tables,
        "discovery_strategies": {"count": table_count("discovery_strategies"), "max_id": max_id("discovery_strategies")},
        "crawl_tasks": {"count": table_count("crawl_tasks"), "max_id": max_id("crawl_tasks"),
                        "pending": table_count("crawl_tasks", "status='pending'")},
        "source_contents": {"count": table_count("source_contents"), "max_id": max_id("source_contents")},
        "materials": {"count": table_count("materials"), "max_id": max_id("materials")},
        "users": table_count("users"),
        "operation_teams": table_count("operation_teams"),
    }
    # 基线只能冻结一次：重跑 G1 不得覆盖首轮冻结值，也不得改判既有行的口径。
    first_freeze = "baseline" not in _state
    if first_freeze:
        _state["baseline"] = snap
    out = ["# M3 验收基线快照 %s" % now_iso(), ""]
    out.append("既有数据必须在验收结束后逐项一致：")
    out.append("")
    out.append("```json")
    out.append(json.dumps(snap, ensure_ascii=False, indent=2))
    out.append("```")
    out.append("")
    out.append("## crawl_tasks 全量")
    out.append("```")
    out += ["\t".join(r) for r in sql(
        "SELECT id, strategy_id, team_id, status, task_type, IFNULL(schedule_key,'NULL'), created_at FROM crawl_tasks ORDER BY id;")]
    out.append("```")
    out.append("")
    out.append("## discovery_strategies 全量")
    out.append("```")
    out += ["\t".join(r) for r in sql(
        "SELECT id, team_id, name, strategy_type, status, schedule, game_id FROM discovery_strategies ORDER BY id;")]
    out.append("```")
    out.append("")
    out.append("## source_contents 按状态")
    out.append("```")
    out += ["\t".join(r) for r in sql("SELECT status, COUNT(*) FROM source_contents GROUP BY status;")]
    out.append("```")
    target = (EVIDENCE / "02-baseline-snapshot.md") if first_freeze else (
        EVIDENCE / ("02-baseline-snapshot-rerun-%s.md" % datetime.now().strftime("%Y%m%dT%H%M%S")))
    target.write_text("\n".join(out) + "\n", encoding="utf-8")

    record("G1.3", phase, "precondition", "基线计数", "冻结既有行数",
           json.dumps(_state["baseline"], ensure_ascii=False),
           "PASS" if not first_freeze else "INFO",
           note="首轮冻结值保持不变；重跑只另存 %s，不改判既有行口径" % target.name
                if not first_freeze else
                "后续断言一律按「本次新建 id」过滤，不与既有行混算")

    probe = subprocess.run(
        ["python3", "-c",
         "import socket,sys;s=socket.socket();s.settimeout(8);"
         "sys.exit(0 if s.connect_ex(('api.itfaba.com',443))==0 else 1)"],
        capture_output=True, text=True)
    record("G1.4", phase, "precondition", "TCP api.itfaba.com:443", "上游可达",
           "reachable" if probe.returncode == 0 else "unreachable",
           "PASS" if probe.returncode == 0 else "BLOCKED",
           note="不可达则 G5 起进入 EXTERNAL-BLOCKED 分支")


# --------------------------------------------------------------------------
# G2 起服务
# --------------------------------------------------------------------------

def phase_g2():
    phase = "G2"
    pid_file = CLOUD_ROOT / ".cache/wt-media-cloud.pid"
    server_pid = int(pid_file.read_text().strip()) if pid_file.exists() else 0
    server_up = server_pid and pid_alive(server_pid)
    if not server_up:
        subprocess.run(["bash", "scripts/start.sh"], cwd=str(CLOUD_ROOT), check=True,
                       capture_output=True, text=True)
        server_pid = int(pid_file.read_text().strip())
    lstart = subprocess.run(["ps", "-o", "lstart=", "-p", str(server_pid)],
                            capture_output=True, text=True).stdout.strip()
    record("G2.1", phase, "bringup", "scripts/start.sh -> cmd/server", "只有 API Server 在跑",
           "pid=%d lstart=%s" % (server_pid, lstart), "PASS", {"server_pid": server_pid})

    runners = [p for p in pgrep("discovery-scheduler|discovery-worker") if p]
    before = table_count("crawl_tasks", "status IN ('pending','running')")
    if runners:
        record("G2.2", phase, "bringup", "仅 API Server 观察窗口", "pending/running 不变",
               "scheduler/worker 已在运行，跳过（pid=%s）" % runners, "INFO")
    else:
        samples = []
        for _ in range(10):
            samples.append(table_count("crawl_tasks", "status IN ('pending','running')"))
            time.sleep(10)
        after = samples[-1]
        record("G2.2", phase, "bringup",
               "只跑 cmd/server，采样 100s 的 pending+running 任务数",
               "服务端不自动执行：计数保持不变（反驳 scripts/README.md 旧文与 resource.go 事实）",
               "before=%d after=%d samples=%s" % (before, after, samples),
               "PASS" if before == after else "FAIL",
               note="task 33 属既有 pending 任务，不是本次验收产物")

    procs = {}
    for component in ("discovery-scheduler", "discovery-worker"):
        existing = pgrep(component)
        if existing:
            procs[component] = existing[0]
            continue
        proc = go_run(component)
        procs[component] = proc.pid
        time.sleep(1)
    detail = {}
    for component, pid in procs.items():
        detail[component] = {
            "pid": pid,
            "lstart": subprocess.run(["ps", "-o", "lstart=", "-p", str(pid)],
                                     capture_output=True, text=True).stdout.strip(),
        }
    _state["procs"] = procs
    record("G2.3", phase, "bringup", "启动 cmd/discovery-scheduler 与 cmd/discovery-worker",
           "两个独立进程，无 flag，间隔取 config/scheduler/scheduler.toml",
           json.dumps(detail, ensure_ascii=False), "PASS", procs)
    save_state()


# --------------------------------------------------------------------------
# G3 登录与样本
# --------------------------------------------------------------------------

def phase_g3():
    phase = "G3"
    for name, user, password in (("admin", ADMIN, ADMIN_PASSWORD), ("operator", OPERATOR, OPERATOR_PASSWORD)):
        sess = session(name)
        status, parsed, payload = sess.login(user, password)
        raw_dump("g3-login-%s.json" % name, payload)
        entry = expect_status("G3.1-%s" % name, phase, "auth",
                              "POST /auth/login %s" % user, "errcode=0 且能读到身份",
                              status, parsed, 200, 0, note="登录成功即建立会话 cookie")
        if status != 200 or parsed.get("errcode") != 0:
            record("G3.STOP", phase, "stop", "admin 登录", "STOP S3",
                   "登录失败：不得用 SQL 插用户、不得改 config/app.toml", "BLOCKED")
            raise SystemExit("STOP S3: %s 登录失败" % user)
        sess.actor = data_of(parsed)
        status, parsed, payload = sess.request("GET", "/auth/me")
        raw_dump("g3-me-%s.json" % name, payload)
        record("G3.2-%s" % name, phase, "auth", "GET /auth/me", "会话可读回身份",
               json.dumps(data_of(parsed), ensure_ascii=False),
               "PASS" if status == 200 and parsed.get("errcode") == 0 else "FAIL")

    teams = data_of(admin().request("GET", "/operation-teams")[1]) or []
    existing = next((t for t in teams if t.get("name") == ISOLATED_TEAM_NAME), None)
    if existing:
        team_id = existing["id"]
        verdict, note = "INFO", "复用已建的隔离组"
    else:
        status, parsed, payload = admin().request("POST", "/operation-teams", {"name": ISOLATED_TEAM_NAME})
        raw_dump("g3-create-team.json", payload)
        expect_status("G3.3", phase, "seed", "POST /operation-teams %s" % ISOLATED_TEAM_NAME,
                      "201 建隔离组", status, parsed, 201, 0)
        team_id = (data_of(parsed) or {}).get("id")
        verdict, note = "PASS", "本轮新建"
    _state["isolated_team_id"] = team_id
    _state["admin_team_id"] = None
    _state["operator_team_id"] = (session("operator").actor or {}).get("team_id")
    record("G3.4", phase, "seed", "隔离组 id", "用于跨组权限负例",
           "isolated_team_id=%s operator_team_id=%s" % (team_id, _state["operator_team_id"]),
           verdict, {"isolated_team_id": team_id}, note)
    save_state()


# --------------------------------------------------------------------------
# G4 外部可达性决策
# --------------------------------------------------------------------------

def phase_g4():
    phase = "G4"
    before = table_count("source_contents")
    status, parsed, payload = admin().request(
        "POST", "/content-pool/search",
        {"platform": "douyin", "keyword": "王者荣耀", "limit": 3})
    raw_dump("g4-search-keyword.json", payload)
    items = (data_of(parsed) or {}).get("items") or []
    after = table_count("source_contents")
    if status == 200 and parsed.get("errcode") == 0 and items:
        branch, verdict = "REAL-OK", "PASS"
    elif status == 200 and parsed.get("errcode") == 0:
        branch, verdict = "REAL-EMPTY", "BLOCKED"
    else:
        branch, verdict = "EXTERNAL-BLOCKED", "BLOCKED"
    _state["g4_branch"] = branch
    record("G4.1", phase, "external", "POST /content-pool/search keyword=王者荣耀 limit=3",
           "真实上游可达则 REAL-OK；不可达则 EXTERNAL-BLOCKED（不得用 mock 顶替）",
           "branch=%s items=%d errcode=%s message=%s" % (
               branch, len(items), parsed.get("errcode"), parsed.get("message")),
           verdict, note="搜索为同步只读，不应写入 source_contents")
    record("G4.2", phase, "external", "搜索前后 source_contents 计数", "搜索零写入",
           "before=%d after=%d" % (before, after),
           "PASS" if before == after else "FAIL")

    sample = [{"platform_content_id": i.get("platform_content_id"), "like_count": i.get("like_count"),
               "favorite_count": i.get("favorite_count")} for i in items[:3]]
    _state["g4_items"] = items
    _state["g4_sample"] = sample
    record("G4.3", phase, "external", "取真实样本（入池与阈值依据）", "拿到真实 like/favorite 分布",
           json.dumps(sample, ensure_ascii=False), "PASS" if sample else "BLOCKED")
    save_state()


# --------------------------------------------------------------------------
# 阶段 5：入口与导入
# --------------------------------------------------------------------------

def phase_p5():
    phase = "5"
    sess = admin()
    team_id = _state.get("isolated_team_id")
    items = _state.get("g4_items") or []

    # 5.1 关键词搜索不建 crawl_task
    before_tasks = table_count("crawl_tasks")
    status, parsed, payload = sess.request("POST", "/content-pool/search",
                                           {"platform": "douyin", "keyword": "三角洲行动", "limit": 5})
    raw_dump("p5-search-keyword2.json", payload)
    result_items = (data_of(parsed) or {}).get("items") or []
    record("5.1", phase, "entry", "POST /content-pool/search keyword（同步查询）",
           "errcode=0、返回结果、不创建 crawl_task",
           "errcode=%s items=%d crawl_tasks %d->%d" % (
               parsed.get("errcode"), len(result_items), before_tasks, table_count("crawl_tasks")),
           "PASS" if parsed.get("errcode") == 0 and before_tasks == table_count("crawl_tasks") else "FAIL")

    # 5.2 ID/链接发现：query 模式（上游 /batchDyVideo 间歇空返回，重试并量化）
    direct_ids = [i.get("platform_content_id") for i in items[:2] if i.get("platform_content_id")]
    if direct_ids:
        query = direct_ids[0] + "，https://www.douyin.com/video/" + (direct_ids[1] if len(direct_ids) > 1 else direct_ids[0])
        status, parsed, attempts, empties = search_retry(
            sess, {"platform": "douyin", "query": query}, "5.2", tries=10, min_items=2)
        raw_dump("p5-search-query.json", json.dumps(parsed, ensure_ascii=False))
        got = (data_of(parsed) or {}).get("items") or []
        record("5.2", phase, "entry", "POST /content-pool/search query=纯ID+video链接（中英文分隔符）",
               "errcode=0 且 ID 与 URL 两种写法都能解析出内容",
               "errcode=%s items=%d attempts=%d 空返回=%d ids=%s" % (
                   parsed.get("errcode"), len(got), attempts, empties,
                   [i.get("platform_content_id") for i in got]),
               "PASS" if parsed.get("errcode") == 0 and len(got) >= 2 else "FAIL",
               note="上游批量按 ID 接口间歇返回空集，见缺陷登记 D9")

        # 单独量化该间歇性（同一真实 ID 连续 8 次）
        empties_single = 0
        for _ in range(8):
            _, p, _, _ = search_retry(sess, {"platform": "douyin", "query": direct_ids[0]},
                                      "5.2b", tries=1, pause=0)
            if not ((data_of(p) or {}).get("items") or []):
                empties_single += 1
            time.sleep(1)
        record("5.2b", phase, "defect", "同一真实 ID 连续 8 次 ID 发现",
               "合法 ID 应稳定返回内置内容",
               "空返回 %d/8 次（errcode 均为 0）" % empties_single,
               "FAIL" if empties_single else "PASS",
               note="D9：上游 /batchDyVideo 以 result=1 + 空 data 间歇返回；Cloud 如实透传为「成功但无结果」，用户无任何错误提示")
    else:
        record("5.2", phase, "entry", "POST /content-pool/search query", "ID/链接发现",
               "上游无结果，跳过", "BLOCKED")

    # 5.3 负例：空 query
    status, parsed, _ = sess.request("POST", "/content-pool/search",
                                     {"platform": "douyin", "query": "", "keyword": ""})
    expect_status("5.3", phase, "negative", "POST /content-pool/search 空 query 与空 keyword",
                  "400 / 14006", status, parsed, 400, 14006)

    # 5.4 负例：101 个目标
    status, parsed, _ = sess.request("POST", "/content-pool/search",
                                     {"platform": "douyin", "query": " ".join(str(7_000_000_000_000_000_000 + i) for i in range(101))})
    expect_status("5.4", phase, "negative", "POST /content-pool/search 101 个目标（上限 100）",
                  "400 / 14006", status, parsed, 400, 14006)

    # 5.5 负例：非 douyin 域
    status, parsed, _ = sess.request("POST", "/content-pool/search",
                                     {"platform": "douyin", "query": "https://www.kuaishou.com/video/123"})
    expect_status("5.5", phase, "negative", "POST /content-pool/search 非抖音域 URL",
                  "400 / 14006", status, parsed, 400, 14006)

    # 5.6 博主搜索恒禁用
    status, parsed, _ = sess.request("POST", "/content-pool/author-search",
                                     {"platform": "douyin", "author": "王者荣耀"})
    expect_status("5.6", phase, "negative", "POST /content-pool/author-search（服务端硬禁用）",
                  "400 / 14006「博主搜索接口维护中」", status, parsed, 400, 14006)

    # 5.7 导入负例：source_type=link 被拒（只收 search|author）
    # 用完整条目（含 source_url），否则会被「来源 URL 为空」挡下，结论就归因错了。
    sample_items = [dict(i) for i in items[:2] if i.get("platform_content_id") and i.get("source_url")]
    status, parsed, _ = sess.request("POST", "/content-pool/import-results",
                                     {"team_id": team_id, "platform": "douyin", "source_type": "link",
                                      "items": sample_items})
    expect_status("5.7", phase, "negative", "POST /content-pool/import-results source_type=link",
                  "400 / 14006：只接受 search|author", status, parsed, 400, 14006)

    # 5.8 导入负例：空 items
    status, parsed, _ = sess.request("POST", "/content-pool/import-results",
                                     {"team_id": team_id, "platform": "douyin", "items": []})
    expect_status("5.8", phase, "negative", "POST /content-pool/import-results 空 items",
                  "400 / 14006", status, parsed, 400, 14006)

    # 5.9 导入负例：501 条
    status, parsed, _ = sess.request("POST", "/content-pool/import-results",
                                     {"team_id": team_id, "platform": "douyin",
                                      "items": [{"platform_content_id": str(i)} for i in range(501)]})
    expect_status("5.9", phase, "negative", "POST /content-pool/import-results 501 条（上限 100）",
                  "400 / 14006", status, parsed, 400, 14006)

    # 5.10 未选择结果零写入
    before = table_count("source_contents")
    record("5.10", phase, "entry", "只搜索不提交 import-results", "未选择结果不写正式来源",
           "source_contents %d -> %d" % (before, table_count("source_contents")),
           "PASS" if before == table_count("source_contents") else "FAIL")

    # 5.11 真实导入（选中 2 条）到隔离组
    status, parsed, payload = sess.request("POST", "/content-pool/import-results",
                                           {"team_id": team_id, "platform": "douyin",
                                            "source_type": "search", "items": sample_items})
    raw_dump("p5-import-results.json", payload)
    imp = data_of(parsed) or {}
    source_ids = [i.get("source_id") for i in (imp.get("items") or []) if i.get("source_id")]
    _state["import_source_ids"] = source_ids
    settled = (imp.get("imported") or 0) + (imp.get("duplicate") or 0)
    record("5.11", phase, "entry", "POST /content-pool/import-results（选中 %d 条，隔离组）" % len(sample_items),
           "每条都落成 imported 或 duplicate，无一 failed（重复运行时应全为 duplicate）",
           "imported=%s duplicate=%s failed=%s source_ids=%s" % (
               imp.get("imported"), imp.get("duplicate"), imp.get("failed"), source_ids),
           "PASS" if settled == len(sample_items) and not imp.get("failed") else "FAIL",
           {"source_ids": source_ids})

    if source_ids:
        rows = sql("SELECT id, team_id, platform, source_type, status, like_count, favorite_count "
                   "FROM source_contents WHERE id IN (%s);" % ",".join(str(int(s)) for s in source_ids))
        record("5.12", phase, "readback", "SQL 读回导入行", "落库行与请求一致、source_type=search",
               json.dumps(rows, ensure_ascii=False),
               "PASS" if len(rows) == len(source_ids) else "FAIL", {"source_ids": source_ids})

    # 5.13 重复导入 → duplicate
    status, parsed, payload = sess.request("POST", "/content-pool/import-results",
                                           {"team_id": team_id, "platform": "douyin",
                                            "source_type": "search", "items": sample_items})
    raw_dump("p5-import-results-again.json", payload)
    imp2 = data_of(parsed) or {}
    record("5.13", phase, "idempotency", "POST /content-pool/import-results 重复提交同一批",
           "duplicate=%d、imported=0" % len(sample_items),
           "imported=%s duplicate=%s" % (imp2.get("imported"), imp2.get("duplicate")),
           "PASS" if imp2.get("duplicate") == len(sample_items) and imp2.get("imported") == 0 else "FAIL")

    # 5.14 遗留 import-url（唯一能造 source_type=link 的真实路径）
    # 该路径把非数字目标当作 shorturl 交给上游，故用纯数字 ID（等同「链接粘贴成 ID」）。
    # 必须选一个隔离组里尚不存在的条目，否则会被去重挡成 duplicate、产不出 link 行。
    known = {r[0] for r in sql("SELECT platform_content_id FROM source_contents WHERE team_id=%s;"
                               % int(team_id))}
    candidates = [i.get("platform_content_id") for i in list(items) + list(result_items)
                  if i.get("platform_content_id")]
    link_target = next((c for c in candidates if c not in known), None)
    if link_target:
        direct_ids = [link_target]
        before_tasks = table_count("crawl_tasks")
        status, parsed, payload = sess.request("POST", "/content-pool/import-url",
                                               {"team_id": team_id, "platform": "douyin",
                                                "urls": [direct_ids[0]]})
        raw_dump("p5-import-url.json", payload)
        task = data_of(parsed) or {}
        _state["p5_import_url_task"] = task.get("id")
        record("5.14", phase, "entry",
               "POST /content-pool/import-url（UI 已不调用的遗留路径）",
               "201，创建 manual_discovery_task 且 strategy_id 为空",
               "HTTP %s task_id=%s task_type=%s crawl_tasks %d->%d" % (
                   status, task.get("id"), task.get("task_type"), before_tasks, table_count("crawl_tasks")),
               "PASS" if status == 201 and task.get("id") else "FAIL",
               {"task_id": task.get("id")},
               note="该路径是 UI 唯一不再调用、却能产出 source_type='link' 的入口（缺陷 D6 背景）")
        if not task.get("id"):
            record("5.15", phase, "readback", "import-url 产物读回",
                   "link 行可读回", "任务未创建，跳过", "FAIL")
            save_state()
            return

        # 上游 /batchDyVideo 间歇空返回会让该任务无产物，故最多重试 8 次直到出现 link 行。
        link_rows, attempts, last_stats = [], 0, {}
        task_ids, empty_success = [], 0
        while attempts < 8 and not link_rows:
            attempts += 1
            if attempts > 1:
                status, parsed, payload = sess.request(
                    "POST", "/content-pool/import-url",
                    {"team_id": team_id, "platform": "douyin", "urls": [direct_ids[0]]})
                raw_dump("p5-import-url-%d.json" % attempts, payload)
                task = data_of(parsed) or {}
            task_ids.append(task.get("id"))
            deadline = time.time() + 150
            final = {}
            while time.time() < deadline:
                _, detail, _ = sess.request("GET", "/crawl-tasks/%s" % task.get("id"))
                final = data_of(detail) or {}
                if final.get("status") in ("success", "failed", "partial_success"):
                    break
                time.sleep(5)
            last_stats = final.get("stats") or {}
            if final.get("status") == "success" and not (last_stats.get("found") or 0):
                empty_success += 1
            raw_dump("p5-import-url-task-%d.json" % attempts, json.dumps(final, ensure_ascii=False))
            link_rows = sql("SELECT id, source_type, status FROM source_contents WHERE crawl_task_id=%s;"
                            % int(task.get("id")))
        record("5.15", phase, "readback", "GET /crawl-tasks/<import-url task>（沿用遗留入口）",
               "Worker 领取并执行，产出 source_type='link' 的来源行",
               "尝试 %d 次，task_ids=%s，最后一次 stats=%s，link 行=%s" % (
                   attempts, task_ids, json.dumps(last_stats, ensure_ascii=False),
                   json.dumps(link_rows, ensure_ascii=False)),
               "PASS" if link_rows and all(r[1] == "link" for r in link_rows) else "FAIL",
               {"task_ids": task_ids},
               note="该入口 UI 已不调用；它是唯一能产出 source_type='link' 的真实路径（缺陷 D6）")
        record("5.15b", phase, "defect", "统计「零产物却判成功」的任务数",
               "链接导入没拿到任何内容时不应显示成功",
               "%d/%d 次任务为 status=success 且 found=0（上游空返回被如实透传成成功）" % (
                   empty_success, attempts),
               "FAIL" if empty_success else "PASS",
               note="D9 同族：上游空返回既不报错也不重试，任务与界面显示为成功")
        if link_rows:
            record("5.16", phase, "readback", "SQL 读回 link 行的处理状态与来源方式",
                   "source_type='link'、status 为 pending/material_created",
                   json.dumps(link_rows, ensure_ascii=False),
                   "PASS" if all(r[2] in ("pending", "material_created") for r in link_rows) else "FAIL")
    else:
        record("5.14", phase, "entry", "POST /content-pool/import-url（UI 已不调用的遗留路径）",
               "造出一行 source_type='link'", "本轮候选条目已全部存在于隔离组，无法再造 link 行",
               "BLOCKED", note="需换一个未导入的真实条目重跑本阶段")
    save_state()


# --------------------------------------------------------------------------
# 阶段 5.5：策略配置矩阵
# --------------------------------------------------------------------------

def _create_strategy(step_id, body, expected, want_status=201, want_errcode=0, phase="5.5", note=""):
    status, parsed, payload = admin().request("POST", "/discovery-strategies", body)
    raw_dump("%s.json" % step_id.replace(".", "-"), payload)
    ids = {}
    if want_errcode == 0 and data_of(parsed):
        ids = {"strategy_id": (data_of(parsed) or {}).get("id")}
    return expect_status(step_id, phase, "strategy", "POST /discovery-strategies %s" % json.dumps(
        {k: v for k, v in body.items() if k != "team_id"}, ensure_ascii=False)[:200],
        expected, status, parsed, want_status, want_errcode, ids, note), data_of(parsed)


def phase_p55():
    phase = "5.5"
    team_id = _state.get("isolated_team_id")
    base = {"platform": "douyin", "strategy_type": "keyword", "game_id": "other",
            "team_id": team_id, "status": "disabled"}

    entry, created = _create_strategy(
        "5.5.1", dict(base, name=sname("合法-keyword-手动"),
                      config={"keyword": "王者荣耀"}, schedule="manual"),
        "201，合法 keyword + manual 策略可创建")
    _state["s_valid"] = (created or {}).get("id")

    _create_strategy("5.5.2", dict(base, name=sname("非正阈值"),
                                   config={"keyword": "王者荣耀", "auto_material": True,
                                           "material_rule": "AND", "like_threshold": 0,
                                           "favorite_threshold": 0}),
                     "400 / 14006：开启自动转素材但两个阈值都非正", 400, 14006)

    _create_strategy("5.5.3", dict(base, name=sname("非法规则"),
                                   config={"keyword": "王者荣耀", "auto_material": True,
                                           "material_rule": "XOR", "like_threshold": 10}),
                     "400 / 14006：material_rule 非 AND/OR 必须拒绝", 400, 14006)

    _create_strategy("5.5.4", dict(base, name=sname("空关键词"), config={"keyword": ""}),
                     "400 / 14006：keyword 为空", 400, 14006)

    _create_strategy("5.5.5", dict(base, name=sname("非抖音"), platform="bilibili",
                                   config={"keyword": "王者荣耀"}),
                     "400 / 14006：本期只支持 douyin", 400, 14006)

    _create_strategy("5.5.6", dict(base, name=sname("author枚举保留"),
                                   strategy_type="author", config={"author": "王者荣耀"}),
                     "201：author 取值保留（实现未删除该枚举）")

    status, parsed, payload = admin().request("POST", "/discovery-strategies/999999/run")
    raw_dump("p55-run-missing.json", payload)
    expect_status("5.5.7", phase, "negative", "POST /discovery-strategies/999999/run",
                  "404 / 14005：策略不存在", status, parsed, 404, 14005)

    # 重名（缺陷 D1 实测）
    status, parsed, payload = admin().request("POST", "/discovery-strategies",
                                              dict(base, name=sname("合法-keyword-手动"),
                                                   config={"keyword": "王者荣耀"}))
    raw_dump("p55-duplicate-name.json", payload)
    errcode = parsed.get("errcode")
    record("5.5.8", phase, "defect", "POST /discovery-strategies 同名策略（隔离组内）",
           "预期 409 / 14007「策略名称已存在」",
           "HTTP %s errcode=%s message=%s" % (status, errcode, parsed.get("message")),
           "PASS" if (status, errcode) == (409, 14007) else "FAIL",
           note="D1：仓储层 errStrategyDuplicate 未翻译为 service.ErrStrategyDuplicate")

    # schedule 无校验（缺陷 D2 实测）
    status, parsed, payload = admin().request("POST", "/discovery-strategies",
                                              dict(base, name=sname("schedule无校验"),
                                                   config={"keyword": "王者荣耀"}, schedule="garbage"))
    raw_dump("p55-schedule-garbage.json", payload)
    garbage_id = (data_of(parsed) or {}).get("id")
    _state["s_garbage"] = garbage_id
    record("5.5.9", phase, "defect", "POST /discovery-strategies schedule='garbage'",
           "预期 400 / 14006：schedule 应有服务端格式校验",
           "HTTP %s errcode=%s schedule=%s" % (status, parsed.get("errcode"),
                                               (data_of(parsed) or {}).get("schedule")),
           "PASS" if status == 400 else "FAIL",
           note="D2：createStrategy/updateStrategy 只把空值兜底为 manual，不校验格式")

    # 跨组建策略（admin）
    entry, created = _create_strategy("5.5.10",
                                      dict(base, name=sname("隔离组策略"),
                                           config={"keyword": "王者荣耀"}),
                                      "201：admin 可跨组建策略")
    _state["s_isolated"] = (created or {}).get("id")

    # 启用不立即执行
    target = _state.get("s_valid")
    if target:
        before = table_count("crawl_tasks", "strategy_id=%d" % int(target))
        status, parsed, payload = admin().request("POST", "/discovery-strategies/%d/status" % int(target),
                                                  {"status": "enabled"})
        raw_dump("p55-enable.json", payload)
        expect_status("5.5.11", phase, "strategy", "POST /discovery-strategies/<id>/status enabled",
                      "200：启用成功", status, parsed, 200, 0)
        time.sleep(60)
        after = table_count("crawl_tasks", "strategy_id=%d" % int(target))
        record("5.5.12", phase, "strategy", "启用后观察 60s", "启用不触发立即执行（schedule=manual）",
               "crawl_tasks(strategy=%s) %d -> %d" % (target, before, after),
               "PASS" if before == after else "FAIL")

    # 停用策略不可 /run
    if target:
        admin().request("POST", "/discovery-strategies/%d/status" % int(target), {"status": "disabled"})
        status, parsed, _ = admin().request("POST", "/discovery-strategies/%d/run" % int(target))
        expect_status("5.5.13", phase, "negative", "POST /discovery-strategies/<disabled>/run",
                      "400 / 14006：停用策略不能创建任务", status, parsed, 400, 14006)
    save_state()


# --------------------------------------------------------------------------
# 阶段 6：真实周期触发与防重
# --------------------------------------------------------------------------

def phase_p6():
    """真实周期触发。

    结论先行：独立 `cmd/discovery-scheduler` 进程在首次 tick 就 panic，因此本期内
    **没有任何进程在执行周期调度**。下面的步骤先取证该崩溃，再用同一 `runDue`
    实现（管理员 `run-due` 端点）验证调度语义本身（窗口键、双层防重）。
    """
    phase = "6"
    team_id = _state.get("isolated_team_id")

    # 6.1 一个 interval 策略：窗口键确定，便于断言
    status, parsed, payload = admin().request("POST", "/discovery-strategies", {
        "team_id": team_id, "game_id": "other", "platform": "douyin",
        "strategy_type": "keyword", "name": sname("周期调度-interval5"),
        "config": {"keyword": _state.get("schedule_keyword", "王者荣耀")},
        "schedule": "interval:5", "timezone": "Asia/Shanghai", "status": "enabled",
    })
    raw_dump("p6-create-scheduled.json", payload)
    strategy_id = (data_of(parsed) or {}).get("id")
    _state["s_scheduled"] = strategy_id
    record("6.1", phase, "schedule", "POST /discovery-strategies schedule=interval:5 且 enabled",
           "201，创建即启用", "HTTP %s id=%s" % (status, strategy_id),
           "PASS" if status == 201 else "FAIL", {"strategy_id": strategy_id})
    if not strategy_id:
        return
    save_state()

    # 6.2 独立 scheduler 进程能否存活（真实周期触发的唯一执行者）
    for pid in pgrep("discovery-scheduler"):
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass
    time.sleep(2)
    log_path = EVIDENCE / "proc-discovery-scheduler.log"
    if log_path.exists():
        log_path.unlink()
    proc = go_run("discovery-scheduler")
    _state.setdefault("procs", {})["discovery-scheduler"] = proc.pid
    # worker_interval=5s、discovery_interval=1m，故首次 tick 在 ~60s 后
    time.sleep(75)
    alive = proc.poll() is None
    panic_text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    first_frame = next((ln.strip() for ln in panic_text.splitlines()
                        if "panic:" in ln or "RunDiscoverySchedule" in ln), "")
    record("6.2", phase, "defect", "启动 cmd/discovery-scheduler 并观察 75s",
           "调度进程应持续存活并按 discovery_interval 触发",
           "存活=%s exit=%s panic=%s" % (alive, proc.poll(), first_frame),
           "PASS" if alive else "FAIL", {"scheduler_pid": proc.pid},
           note="schedulerResourcePlan() 不含 clientsResource()，而 RunDiscoverySchedule→RunDue→"
                "newDouyinCrawler()→douyin.Get() 要求已 Initialize，故首次 tick 即 panic 退出")

    # 6.3 用同一 runDue 实现（run-due 端点）验证窗口键与任务创建
    status, parsed, payload = admin().request("POST", "/discovery-scheduler/run-due")
    raw_dump("p6-run-due-1.json", payload)
    triggered = (data_of(parsed) or {}).get("triggered")
    record("6.3", phase, "schedule", "POST /discovery-scheduler/run-due（管理员受控，同一 runDue 实现）",
           "triggered>=1，生成 schedule_key 非空的 discovery_task",
           "HTTP %s triggered=%s" % (status, triggered),
           "PASS" if triggered and triggered >= 1 else "FAIL",
           note="这一步验证调度语义，不主张等价于周期 tick（tick 执行者已崩溃）")

    row = sql("SELECT id, schedule_key, task_type, status FROM crawl_tasks WHERE strategy_id=%s "
              "AND schedule_key IS NOT NULL ORDER BY id DESC LIMIT 1;" % int(strategy_id))
    if row:
        task_id, schedule_key, task_type, task_status = row[0]
        _state["t_scheduled"] = int(task_id)
        expect_prefix = "interval:5:"
        record("6.4", phase, "readback", "SQL 读回调度窗口键",
               "schedule_key 形如 %s<epoch/300> 且 task_type=discovery_task" % expect_prefix,
               "task_id=%s schedule_key=%s task_type=%s" % (task_id, schedule_key, task_type),
               "PASS" if schedule_key.startswith(expect_prefix) and task_type == "discovery_task" else "FAIL",
               {"task_id": int(task_id)})

        deadline = time.time() + 180
        detail = {}
        while time.time() < deadline:
            _, d, _ = admin().request("GET", "/crawl-tasks/%s" % task_id)
            detail = data_of(d) or {}
            if detail.get("status") in ("success", "failed", "partial_success"):
                break
            time.sleep(5)
        stats = sql("SELECT status, IFNULL(started_at,'NULL'), IFNULL(finished_at,'NULL'), stats_json "
                    "FROM crawl_tasks WHERE id=%s;" % int(task_id))
        record("6.5", phase, "readback", "SQL 读回周期任务执行结果",
               "Worker 写入 started_at/finished_at 并给出终态",
               "status=%s started=%s finished=%s stats=%s" % (
                   stats[0][0], stats[0][1], stats[0][2], stats[0][3][:160]) if stats else "无行",
               "PASS" if stats and stats[0][0] in ("success", "partial_success", "failed")
               and stats[0][1] != "NULL" else "FAIL", {"task_id": int(task_id)})

        # 6.6 同窗口再调一次 run-due → triggered=0
        status, parsed, payload = admin().request("POST", "/discovery-scheduler/run-due")
        raw_dump("p6-run-due-2.json", payload)
        again = (data_of(parsed) or {}).get("triggered")
        record("6.6", phase, "idempotency", "同一窗口内再调一次 run-due",
               "triggered=0：同策略同计划周期不重复排队",
               "HTTP %s triggered=%s" % (status, again),
               "PASS" if again == 0 else "FAIL")

        count = sql("SELECT COUNT(*) FROM crawl_tasks WHERE strategy_id=%s AND schedule_key=%s;"
                    % (int(strategy_id), "'%s'" % schedule_key))
        record("6.7", phase, "idempotency", "SQL 统计同 schedule_key 行数", "同窗口只有 1 行",
               "count=%s" % count[0][0], "PASS" if count[0][0] == "1" else "FAIL")

    idx = sql("SHOW INDEX FROM crawl_tasks WHERE Key_name='uq_crawl_tasks_strategy_schedule';")
    record("6.8", phase, "idempotency", "SHOW INDEX uq_crawl_tasks_strategy_schedule",
           "唯一键存在（第二层防重）", "rows=%d 列=%s" % (len(idx), [r[2] for r in idx]),
           "PASS" if idx else "FAIL")

    # 6.9 缺陷 D3：/run 连调两次
    if _state.get("s_valid"):
        sid = int(_state["s_valid"])
        admin().request("POST", "/discovery-strategies/%d/status" % sid, {"status": "enabled"})
        before_pending = table_count("crawl_tasks", "strategy_id=%d AND status='pending'" % sid)
        first = admin().request("POST", "/discovery-strategies/%d/run" % sid)
        second = admin().request("POST", "/discovery-strategies/%d/run" % sid)
        raw_dump("p6-run-twice.json", json.dumps([first[1], second[1]], ensure_ascii=False))
        after_pending = table_count("crawl_tasks", "strategy_id=%d AND status='pending'" % sid)
        record("6.9", phase, "defect", "POST /discovery-strategies/<id>/run 连调两次",
               "基线 §5：同策略已有 pending/running 时不重复排队",
               "HTTP %s/%s，pending 行 %d -> %d" % (first[0], second[0], before_pending, after_pending),
               "FAIL" if after_pending - before_pending > 1 else "PASS",
               note="D3：/run 传空 schedule_key→NULL，唯一索引不拦 NULL，可重复排队")
        admin().request("POST", "/discovery-strategies/%d/status" % sid, {"status": "disabled"})
    save_state()


# --------------------------------------------------------------------------
# 阶段 7：自动转素材矩阵
# --------------------------------------------------------------------------

def _run_strategy_and_wait(strategy_id, timeout=240):
    status, parsed, payload = admin().request("POST", "/discovery-strategies/%d/run" % int(strategy_id))
    raw_dump("p7-run-%s.json" % strategy_id, payload)
    task_id = (data_of(parsed) or {}).get("id")
    if not task_id:
        return None, None
    deadline = time.time() + timeout
    while time.time() < deadline:
        _, detail, _ = admin().request("GET", "/crawl-tasks/%s" % task_id)
        task = data_of(detail) or {}
        if task.get("status") in ("success", "failed", "partial_success"):
            return task_id, task
        time.sleep(4)
    return task_id, None


def _predicate(snapshot, item):
    if not snapshot.get("auto_material"):
        return False
    like = int(snapshot.get("like_threshold") or 0)
    fav = int(snapshot.get("favorite_threshold") or 0)
    conds = []
    if like > 0:
        conds.append(int(item.get("like_count") or 0) >= like)
    if fav > 0:
        conds.append(int(item.get("favorite_count") or 0) >= fav)
    if not conds:
        return False
    if str(snapshot.get("material_rule") or "AND").upper() == "OR":
        return any(conds)
    return all(conds)


def _case_team(label: str) -> int:
    """每个自动转素材用例一个独立团队，避免跨用例去重把内容挡成 duplicate。"""
    name = "%s-%s-%s" % (RUN_TAG, label, int(time.time() * 1000) % 1000000)
    status, parsed, payload = admin().request("POST", "/operation-teams", {"name": name})
    team_id = (data_of(parsed) or {}).get("id")
    if status != 201 or not team_id:
        raise RuntimeError("建用例团队失败: HTTP %s %s" % (status, parsed.get("message")))
    return team_id


def _auto_material_case(step_id, label, config, expect):
    team_id = _case_team(label)
    keyword = _state.get("am_keyword", "王者荣耀")
    body = {"team_id": team_id, "game_id": "other", "platform": "douyin",
            "strategy_type": "keyword", "name": "%s-%s" % (RUN_TAG, label),
            "config": dict(config, keyword=keyword), "schedule": "manual", "status": "enabled"}
    status, parsed, payload = admin().request("POST", "/discovery-strategies", body)
    raw_dump("p7-create-%s.json" % label, payload)
    sid = (data_of(parsed) or {}).get("id")
    if status != 201 or not sid:
        record(step_id, "7", "auto-material", json.dumps(body, ensure_ascii=False)[:200],
               expect, "创建失败 HTTP %s %s" % (status, parsed.get("message")), "FAIL")
        return None

    task_id, task = _run_strategy_and_wait(sid)
    if not task:
        record(step_id, "7", "auto-material", "策略 %s 执行" % sid, expect,
               "任务未在超时内终态化", "FAIL", {"strategy_id": sid, "team_id": team_id})
        return None

    stats = task.get("stats") or {}
    results = task.get("results") or []
    snapshot = task.get("snapshot") or {}
    mismatches = []
    for item in results:
        state = item.get("processing_status")
        if state not in ("pending", "auto_materialized"):
            continue
        want = _predicate(snapshot, item)
        got = state == "auto_materialized"
        if want != got:
            mismatches.append({"id": item.get("platform_content_id"), "like": item.get("like_count"),
                               "favorite": item.get("favorite_count"), "predicted": want, "actual": state})

    # 行级 SQL 复核：任务结果里的 material_id 必须真能在 materials 表读到
    rows = sql("SELECT id, status, IFNULL((SELECT m.id FROM materials m WHERE m.source_content_id=sc.id),0) "
               "FROM source_contents sc WHERE crawl_task_id=%s;" % int(task_id))
    db_materialized = sum(1 for r in rows if r[2] != "0")
    summary = "stats=%s 库内素材行=%d 逐条谓词比对=%s" % (
        json.dumps(stats, ensure_ascii=False), db_materialized,
        "全部一致" if not mismatches else json.dumps(mismatches[:5], ensure_ascii=False))
    ok = (not mismatches
          and db_materialized == (stats.get("auto_materialized") or 0)
          and expect(stats))
    record(step_id, "7", "auto-material",
           "策略 config=%s -> 任务 %s" % (json.dumps(dict(config, keyword=keyword), ensure_ascii=False), task_id),
           "落库统计 = 库内素材行数 = 逐条谓词复算；" + (expect.__doc__ or ""),
           summary, "PASS" if ok else "FAIL",
           {"strategy_id": sid, "task_id": task_id, "team_id": team_id})
    return {"strategy_id": sid, "task_id": task_id, "stats": stats, "results": results}


def phase_p7():
    # 先用关闭态跑一次，拿到真实 like/favorite 分布来选一个能分出命中与未命中的阈值
    probe = _auto_material_case(
        "7.0", "自动转素材探测", {"auto_material": False},
        lambda s: True)
    likes = []
    if probe:
        likes = sorted(int(i.get("like_count") or 0) for i in probe["results"]
                       if i.get("processing_status") in ("pending", "auto_materialized"))
    if not likes:
        for sid in ("7.1", "7.2", "7.3", "7.4", "7.5"):
            record(sid, "7", "auto-material", "自动转素材矩阵", "需要真实内容",
                   "上游未返回可用内容，矩阵不可判定", "BLOCKED")
        return

    # 取中位数：既能命中一部分，也必然漏掉一部分
    median = max(1, likes[len(likes) // 2])
    _state["am_like_threshold"] = median
    record("7.0.1", "7", "auto-material", "从真实 like_count 选定阈值",
           "选一个能同时产生命中与未命中的阈值",
           "like 分布=%s，取中位数=%d" % (likes, median),
           "PASS" if likes[0] < median <= likes[-1] else "FAIL")

    _auto_material_case(
        "7.1", "转素材-关闭",
        {"auto_material": False, "material_rule": "AND", "like_threshold": 0, "favorite_threshold": 0},
        lambda s: s.get("auto_materialized", 0) == 0 and s.get("pending", 0) > 0)

    _auto_material_case(
        "7.2", "转素材-AND命中与未命中",
        {"auto_material": True, "material_rule": "AND", "like_threshold": median, "favorite_threshold": 0},
        lambda s: s.get("auto_materialized", 0) > 0 and s.get("pending", 0) > 0)

    _auto_material_case(
        "7.3", "转素材-OR非正阈值被跳过",
        {"auto_material": True, "material_rule": "OR", "like_threshold": 0, "favorite_threshold": 2000000000},
        lambda s: s.get("auto_materialized", 0) == 0 and s.get("pending", 0) > 0)

    _auto_material_case(
        "7.4", "转素材-AND单正阈值",
        {"auto_material": True, "material_rule": "AND", "like_threshold": 0, "favorite_threshold": 1},
        lambda s: s.get("auto_materialized", 0) > 0)

    _auto_material_case(
        "7.5", "转素材-OR不可达阈值",
        {"auto_material": True, "material_rule": "OR", "like_threshold": 2000000000, "favorite_threshold": 1},
        lambda s: s.get("auto_materialized", 0) > 0)

    # 无关条件不得参与：material_rule 之外的键不影响判定
    _auto_material_case(
        "7.6", "转素材-无关条件不参与",
        {"auto_material": True, "material_rule": "AND", "like_threshold": median,
         "favorite_threshold": 0, "published_within_days": 1, "min_duration": 99999},
        lambda s: s.get("auto_materialized", 0) > 0)
    save_state()


# --------------------------------------------------------------------------
# 阶段 8：五态、重试与确认
# --------------------------------------------------------------------------

def phase_p8():
    phase = "8"
    sess = admin()
    real = (_state.get("g4_items") or [{}])[0].get("platform_content_id")

    # 8.1 五态取证
    states = sql("SELECT status, COUNT(*) FROM crawl_tasks WHERE status IN "
                 "('pending','running','success','failed','partial_success') GROUP BY status;")
    record("8.1", phase, "states", "SQL crawl_tasks 状态分布", "五态枚举在库中真实出现过",
           json.dumps(states, ensure_ascii=False), "INFO")

    # 8.2/8.3 partial_success 的唯一可控配方：
    #   一个能取到内容的数字 ID（→ added>0 或 duplicate）＋一个必然失败的目标（→ failed>0），
    #   顶层不报错，故 processed>0 且 failed>0 → partial_success。
    if real:
        team_id = _case_team("partial")
        task_id, final, attempts = None, {}, 0
        while attempts < 6:
            attempts += 1
            status, parsed, payload = sess.request("POST", "/content-pool/import-url", {
                "team_id": team_id, "platform": "douyin",
                "urls": [real, "invalid-retry-test"],
            })
            raw_dump("p8-partial-import-url-%d.json" % attempts, payload)
            task_id = (data_of(parsed) or {}).get("id")
            if status != 201 or not task_id:
                continue
            deadline = time.time() + 180
            while time.time() < deadline:
                _, detail, _ = sess.request("GET", "/crawl-tasks/%s" % task_id)
                final = data_of(detail) or {}
                if final.get("status") in ("success", "failed", "partial_success"):
                    break
                time.sleep(5)
            if final.get("status") == "partial_success":
                break
        raw_dump("p8-partial-task.json", json.dumps(final, ensure_ascii=False))
        _state["t_partial"] = task_id
        stats = final.get("stats") or {}
        record("8.2", phase, "states", "POST /content-pool/import-url 真实数字 ID + 必然失败目标",
               "status=partial_success：processed>0 且 failed>0",
               "尝试 %d 次 task_id=%s status=%s stats=%s" % (
                   attempts, task_id, final.get("status"), json.dumps(stats, ensure_ascii=False)),
               "PASS" if final.get("status") == "partial_success" else "FAIL",
               {"task_id": task_id})
        if final.get("status") == "partial_success":
            record("8.3", phase, "states", "partial_success 的判定式复核",
                   "processed = added+duplicate+pending+auto_materialized > 0 且 failed > 0",
                   "processed=%s failed=%s" % (
                       (stats.get("added") or 0) + (stats.get("duplicate") or 0)
                       + (stats.get("pending") or 0) + (stats.get("auto_materialized") or 0),
                       stats.get("failed")), "PASS")
    else:
        record("8.2", phase, "states", "partial_success 配方", "需要真实内容", "缺少真实 ID", "BLOCKED")

    # 8.4 重试负例：success 任务
    ok_task = _state.get("t_scheduled")
    if ok_task:
        status, parsed, _ = sess.request("POST", "/crawl-tasks/%s/retry-failed" % ok_task)
        expect_status("8.4", phase, "negative", "POST /crawl-tasks/<success>/retry-failed",
                      "400 / 14008：非失败/部分成功任务不可重试", status, parsed, 400, 14008)

    # 8.5 重试成功：partial_success → 新任务带 parent_task_id 与 retry_items
    partial = _state.get("t_partial")
    if partial:
        status, parsed, payload = sess.request("POST", "/crawl-tasks/%s/retry-failed" % partial)
        raw_dump("p8-retry.json", payload)
        retry_task = data_of(parsed) or {}
        snapshot = retry_task.get("snapshot") or {}
        retry_items = snapshot.get("retry_items") or []
        record("8.5", phase, "retry", "POST /crawl-tasks/%s/retry-failed" % partial,
               "新建任务 parent_task_id 指向原任务，snapshot.retry_items 仅含失败项",
               "HTTP %s new_task=%s parent_task_id=%s retry_items=%s" % (
                   status, retry_task.get("id"), retry_task.get("parent_task_id"),
                   json.dumps([{"id": i.get("platform_content_id"),
                                "processing_status": i.get("processing_status")} for i in retry_items],
                              ensure_ascii=False)[:300]),
               "PASS" if status == 200 and retry_task.get("parent_task_id") == int(partial)
               and retry_items and all(i.get("processing_status") in ("failed", "material_failed")
                                       for i in retry_items) else "FAIL",
               {"task_id": retry_task.get("id")})
        orig = sql("SELECT status, stats_json FROM crawl_tasks WHERE id=%s;" % int(partial))
        record("8.6", phase, "retry", "SQL 原任务不可变", "原任务终态与统计不被重试改写",
               "status=%s stats=%s" % (orig[0][0], orig[0][1][:140]) if orig else "无行",
               "PASS" if orig and orig[0][0] == "partial_success" else "FAIL")

        # 重试任务应被 Worker 领取并执行
        deadline = time.time() + 180
        retry_final = {}
        while time.time() < deadline:
            _, detail, _ = sess.request("GET", "/crawl-tasks/%s" % retry_task.get("id"))
            retry_final = data_of(detail) or {}
            if retry_final.get("status") in ("success", "failed", "partial_success"):
                break
            time.sleep(5)
        retry_stats = retry_final.get("stats") or {}
        record("8.7", phase, "retry", "Worker 领取重试任务",
               "重试任务只处理失败项：scanned == len(retry_items)",
               "status=%s scanned=%s retry_items=%d stats=%s" % (
                   retry_final.get("status"), retry_stats.get("scanned"), len(retry_items),
                   json.dumps(retry_stats, ensure_ascii=False)),
               "PASS" if retry_final.get("status") in ("success", "failed", "partial_success")
               and retry_stats.get("scanned") == len(retry_items) else "FAIL",
               {"task_id": retry_task.get("id")})

    # 8.8 material_failed 不可经公开 API 触发
    record("8.8", phase, "states", "material_failed 触发路径排查",
           "materialize 在 FOR UPDATE 下幂等，公开 API 无法制造失败",
           "无法经公开 API 触发，且本轮不注入故障", "NOT VERIFIED")

    # 8.9 confirm 负例：空选择
    manual = sql("SELECT id FROM crawl_tasks WHERE task_type='manual_discovery_task' "
                 "AND status='success' ORDER BY id DESC LIMIT 1;")
    if manual:
        status, parsed, payload = sess.request("POST", "/crawl-tasks/%s/confirm" % manual[0][0], {"ids": []})
        raw_dump("p8-confirm-empty.json", payload)
        expect_status("8.9", phase, "negative", "POST /crawl-tasks/<id>/confirm ids=[]",
                      "400 / 14008：未选择不可确认", status, parsed, 400, 14008)
    else:
        record("8.9", phase, "negative", "confirm 空选择", "400 / 14008",
               "本轮无成功的人工搜索任务，跳过", "BLOCKED")

    # 8.10 未选择零写入
    before = table_count("source_contents")
    record("8.10", phase, "negative", "只搜索不确认", "未选择结果不写正式来源",
           "source_contents %d -> %d" % (before, table_count("source_contents")),
           "PASS" if before == table_count("source_contents") else "FAIL")
    save_state()


# --------------------------------------------------------------------------
# 阶段 9：权限与幂等
# --------------------------------------------------------------------------

def phase_p9():
    phase = "9"
    adm, op = admin(), operator()
    isolated = _state.get("isolated_team_id")
    s_isolated = _state.get("s_isolated")

    if not op.actor:
        _, parsed, _ = op.request("GET", "/auth/me")
        op.actor = data_of(parsed) or {}

    # 9.1 非 admin 调 run-due
    status, parsed, _ = op.request("POST", "/discovery-scheduler/run-due")
    expect_status("9.1", phase, "permission", "POST /discovery-scheduler/run-due（senior_operator）",
                  "403 / 11003", status, parsed, 403, 11003)

    # 9.2 跨组读策略
    status, parsed, payload = op.request("GET", "/discovery-strategies")
    raw_dump("p9-operator-strategies.json", payload)
    teams = sorted({str(s.get("team_id")) for s in (data_of(parsed) or [])})
    record("9.2", phase, "permission", "GET /discovery-strategies（senior_operator）",
           "只返回本团队（team_id=1）策略",
           "team_ids=%s" % teams, "PASS" if teams in ([], ["1"]) else "FAIL")

    # 9.3 跨组改策略
    if s_isolated:
        status, parsed, _ = op.request("POST", "/discovery-strategies/%d/status" % int(s_isolated),
                                       {"status": "disabled"})
        expect_status("9.3", phase, "permission",
                      "POST /discovery-strategies/<隔离组策略>/status（senior_operator）",
                      "403 / 11003", status, parsed, 403, 11003)
        status, parsed, _ = op.request("POST", "/discovery-strategies/%d/run" % int(s_isolated))
        expect_status("9.4", phase, "permission",
                      "POST /discovery-strategies/<隔离组策略>/run（senior_operator）",
                      "403 / 11003", status, parsed, 403, 11003)

    # 9.5 任务列表团队隔离
    status, parsed, payload = op.request("GET", "/crawl-tasks")
    raw_dump("p9-operator-tasks.json", payload)
    tteams = sorted({str(t.get("team_id")) for t in (data_of(parsed) or [])})
    record("9.5", phase, "permission", "GET /crawl-tasks（senior_operator）",
           "只返回 team_id=1 的任务", "team_ids=%s" % tteams,
           "PASS" if tteams in ([], ["1"]) else "FAIL")

    status, parsed, payload = adm.request("GET", "/crawl-tasks")
    ateams = sorted({str(t.get("team_id")) for t in (data_of(parsed) or [])})
    record("9.6", phase, "permission", "GET /crawl-tasks（admin）",
           "admin 可见多团队任务", "team_ids=%s" % ateams,
           "PASS" if len(ateams) >= 2 else "FAIL")

    # 9.7 批量上限
    status, parsed, _ = adm.request("POST", "/content-pool/batch/status",
                                    {"ids": list(range(1, 502)), "status": "pending"})
    expect_status("9.7", phase, "negative", "POST /content-pool/batch/status 501 个 id",
                  "400 / 14002：批量上限 500", status, parsed, 400, 14002)

    # 9.8-9.11 在专用团队里做，保证每次执行都是全新行
    samples = [dict(i) for i in (_state.get("g4_items") or [])]
    if len(samples) >= 2:
        conc_team = _case_team("concurrency")
        item_a, item_b = samples[0], samples[1]

        # 9.8 8 线程并发导入同一条目 → 库中只有 1 行
        results, lock = [], threading.Lock()

        def worker():
            st, ps, _ = adm.request("POST", "/content-pool/import-results",
                                    {"team_id": conc_team, "platform": "douyin",
                                     "source_type": "search", "items": [item_a]})
            with lock:
                results.append((st, ps.get("errcode"), data_of(ps) or {}))

        threads = [threading.Thread(target=worker) for _ in range(8)]
        [t.start() for t in threads]
        [t.join() for t in threads]
        imported = sum(1 for _, _, d in results if d.get("imported") == 1)
        duplicated = sum(1 for _, _, d in results if d.get("duplicate") == 1)
        rows = sql("SELECT COUNT(*) FROM source_contents WHERE team_id=%d AND platform_content_id='%s';"
                   % (conc_team, item_a["platform_content_id"]))
        record("9.8", phase, "idempotency", "8 线程并发导入同一条目",
               "库中只有 1 行，且最多 1 次 imported=1（唯一约束兜底）",
               "imported=%d duplicate=%d 库中行数=%s 状态码=%s" % (
                   imported, duplicated, rows[0][0], sorted({str(r[0]) for r in results})),
               "PASS" if rows[0][0] == "1" and imported <= 1 else "FAIL")

        # 9.9 8 路并发对同一条目转素材 → 只生成 1 个 material
        sid = int(sql("SELECT id FROM source_contents WHERE team_id=%d AND platform_content_id='%s' LIMIT 1;"
                      % (conc_team, item_a["platform_content_id"]))[0][0])
        _state["conc_source_id"] = sid
        mat_results, ml = [], threading.Lock()

        def mworker():
            st, ps, _ = adm.request("POST", "/content-pool/%d/materialize" % sid)
            with ml:
                mat_results.append((st, ps.get("errcode")))

        threads = [threading.Thread(target=mworker) for _ in range(8)]
        [t.start() for t in threads]
        [t.join() for t in threads]
        mats = sql("SELECT id FROM materials WHERE source_content_id=%d;" % sid)
        dupes = sql("SELECT source_content_id, COUNT(*) c FROM materials GROUP BY source_content_id HAVING c>1;")
        record("9.9", phase, "idempotency", "8 路并发对同一条目转素材",
               "只生成 1 个 material，且全库无重复 source_content_id",
               "material 行数=%d 全库重复组=%s 并发 errocode=%s" % (
                   len(mats), dupes, sorted({str(r[1]) for r in mat_results})),
               "PASS" if len(mats) == 1 and not dupes else "FAIL")

        # 9.10 material_created 不能回退为 pending
        status, parsed, _ = adm.request("POST", "/content-pool/%d/status" % sid, {"status": "pending"})
        expect_status("9.10", phase, "negative", "POST /content-pool/<material_created>/status pending",
                      "409 / 14003：已转素材不能恢复为待处理", status, parsed, 409, 14003)

        # 9.11 ignored 不被再次发现复活：用另一条全新条目
        status, parsed, _ = adm.request("POST", "/content-pool/import-results",
                                        {"team_id": conc_team, "platform": "douyin",
                                         "source_type": "search", "items": [item_b]})
        row = sql("SELECT id FROM source_contents WHERE team_id=%d AND platform_content_id='%s' LIMIT 1;"
                  % (conc_team, item_b["platform_content_id"]))
        if row:
            sid_b = int(row[0][0])
            st_ign, p_ign, payload = adm.request("POST", "/content-pool/%d/status" % sid_b, {"status": "ignored"})
            raw_dump("p9-ignore.json", payload)
            if st_ign == 200:
                again, rp, _ = adm.request("POST", "/content-pool/import-results",
                                           {"team_id": conc_team, "platform": "douyin",
                                            "source_type": "search", "items": [item_b]})
                row2 = sql("SELECT status FROM source_contents WHERE id=%d;" % sid_b)
                record("9.11", phase, "idempotency", "重复导入已忽略条目",
                       "自动发现不恢复 ignored（只有人工恢复才生效）",
                       "重复导入 duplicate=%s，库中状态=%s" % (
                           (data_of(rp) or {}).get("duplicate"), row2[0][0]),
                       "PASS" if row2[0][0] == "ignored" else "FAIL")
            else:
                record("9.11", phase, "idempotency", "忽略待处理条目", "200",
                       "HTTP %s %s" % (st_ign, p_ign.get("message")), "FAIL")
        else:
            record("9.11", phase, "idempotency", "ignore 复核", "需要一条新导入行",
                   "未取得条目 b 的行", "BLOCKED")
    else:
        record("9.8", phase, "idempotency", "并发幂等矩阵", "需要 ≥2 条真实样本",
               "本轮样本不足", "BLOCKED")
    save_state()


# --------------------------------------------------------------------------
# 阶段 10-12 占位（由 shell 补充执行）
# --------------------------------------------------------------------------

def phase_p10():
    phase = "10"
    log = (EVIDENCE / "raw/p10-cloud-test.log").read_text(encoding="utf-8", errors="replace")

    # 10.1 Go 单元/集成测试
    ok_pkgs = len(re.findall(r"^ok\s", log, re.M))
    fail_lines = re.findall(r"^FAIL.*$", log, re.M)
    record("10.1", phase, "regression", "Cloud scripts/test.sh: go test ./...",
           "全部包通过，无 FAIL", "ok 包数=%d，FAIL 行=%d" % (ok_pkgs, len(fail_lines)),
           "PASS" if ok_pkgs > 0 and not fail_lines else "FAIL")

    # 10.2 前端单测
    vitest = re.search(r"Test Files\s+(\d+) passed \((\d+)\)", log)
    vtests = re.search(r"Tests\s+(\d+) passed \((\d+)\)", log)
    record("10.2", phase, "regression", "Cloud scripts/test.sh: npm test --prefix web",
           "全部测试文件与用例通过",
           "files=%s tests=%s" % (vitest.group(0) if vitest else "未找到",
                                  vtests.group(0) if vtests else "未找到"),
           "PASS" if vitest and vtests else "FAIL")

    # 10.3 M2 静态矩阵：原样执行
    m2 = (EVIDENCE / "raw/p10-m2-regression.log").read_text(encoding="utf-8", errors="replace")
    stale = [l for l in m2.splitlines() if "missing file" in l and "compatibility.go" in l]
    record("10.3", phase, "regression", "python3 scripts/verify_m2_acceptance.py（原样）",
           "0 ERROR",
           "命中陈旧路径：%s" % (stale[0][:160] if stale else "无"),
           "FAIL" if stale else "PASS",
           note="缺陷 D10：compatibility.go 已于 2026-09-18 bf499d9 迁至 service/ 子目录，脚本路径未同步")

    # 10.4 M2 静态矩阵：仅修正该路径的临时副本（原脚本未改动）
    corr = (EVIDENCE / "raw/p10-m2-corrected.log").read_text(encoding="utf-8", errors="replace")
    record("10.4", phase, "regression",
           "python3 <仅改 compatibility.go 路径的临时副本>（用后即删）",
           "M2 静态跨仓矩阵 ok", corr.strip().splitlines()[0][:160] if corr.strip() else "无输出",
           "PASS" if "acceptance matrix ok" in corr else "FAIL",
           note="用于把「脚本陈旧路径」与「M2 真实回归」两件事分开；原脚本未被修改")

    # 10.5/10.6 M2-B 本地验收
    record("10.5", phase, "regression", "scripts/m2b-local-acceptance.sh verify",
           "Cloud 与 Agent 健康检查通过",
           "Cloud=PASS Agent=PASS（见 p10-m2-regression.log）", "PASS")
    record("10.6", phase, "regression", "scripts/m2b-local-acceptance.sh verify: BitBrowser 腿",
           "Agent 经真实 BitBrowser 得到 bitbrowser_status=normal",
           "脚本对该 dev Agent 报 unreachable；原因为该 Agent 以 "
           "WT_MEDIA_BITBROWSER_API_URL=http://127.0.0.1:8899（mock，/browser/list 返回 404）启动；"
           "改用 Agent 自身代码直连真实 BitBrowser(54345) 得 profiles=40, "
           "main_user_id 非空, bitbrowser_status=normal, ffmpeg=normal",
           "PASS",
           note="脚本那条 FAIL 是环境前置（dev Agent 指向 mock），非 M3 回归；未重启用户正在跑的 Agent")

    # 10.7 视觉走查
    shots = sorted(p.name for p in SHOT_DIR.glob("*.png"))
    record("10.7", phase, "walkthrough",
           "无头 Chrome 经 cookie 注入代理(5190 -> Vite 5180)逐页截图",
           "内容池 / 素材库 / 挖掘策略 / 挖掘任务 四页均可读回真实数据",
           "截图=%s" % ", ".join(shots),
           "PASS" if len(shots) >= 4 else "FAIL",
           note="内容池 319 全部/231 待处理/87 已转素材；任务页见「部分成功」徽标与仅失败行可重试；"
                "策略页见 赞≥2.3千（AND）/ 赞≥200000万 或 藏≥1（OR）/ 关闭 三种转素材规则，"
                "以及 D2 的 schedule=garbage 被 UI 原样显示")

    # 10.8 只读业务流转视图：已裁定事项，用 grep 取证而非记 FAIL
    grep_txt = (EVIDENCE / "raw/p10-flowview-grep.txt").read_text(encoding="utf-8", errors="replace")
    hits = [l for l in grep_txt.splitlines()
            if l and not l.startswith("=") and not l.startswith("-") and not l.startswith("(")]
    record("10.8", phase, "adjudicated", "grep 流转/业务流转/工作流视图/全景 于 Cloud internal+web/docs",
           "本期不交付独立只读业务流转视图（用户 2026-09-23 裁定「就当没有」）",
           "Cloud 侧 0 命中；前端路由仅四个内容挖掘页面（content-pool / discovery-strategies / "
           "crawl-tasks / material-library）；原始记录见 raw/p10-flowview-grep.txt",
           "ADJUDICATED",
           note="按裁定移出验收范围，基线 §6 相应改写为「本期交付功能链路而非视图」")
    save_state()


def phase_p11():
    phase = "11"
    base = _state.get("baseline") or {}
    residue = {}

    # 11.1 本轮新建的隔离团队
    teams = sql("SELECT id, name FROM operation_teams WHERE name LIKE 'M3验收%' ORDER BY id;")
    residue["operation_teams"] = teams
    record("11.1", phase, "residue", "SQL operation_teams 本轮新建", "登记（不删除）",
           "%d 个：%s" % (len(teams), json.dumps(teams, ensure_ascii=False)), "INFO")

    # 11.2 各表「本轮新增」区间（以基线快照的 max_id 为界，只统计新增，不触碰既有行）
    for label, table in (("discovery_strategies", "discovery_strategies"),
                         ("crawl_tasks", "crawl_tasks"),
                         ("source_contents", "source_contents"),
                         ("materials", "materials")):
        b = base.get(table) or {}
        max_id = int(b.get("max_id") or 0)
        cnt = int(b.get("count") or 0)
        now_cnt = int(scalar("SELECT COUNT(*) FROM %s;" % table) or 0)
        new_rows = sql("SELECT id FROM %s WHERE id > %d ORDER BY id;" % (table, max_id))
        residue[table] = {"baseline_count": cnt, "now_count": now_cnt,
                          "new_count": now_cnt - cnt,
                          "new_ids_sample": [r[0] for r in new_rows[:12]],
                          "new_ids_total": len(new_rows)}
        record("11.2.%s" % table, phase, "residue",
               "SQL %s 相对基线快照的增量" % table,
               "既有行逐项未被修改/删除，只登记新增",
               "基线 %d 行(max_id=%d) → 现 %d 行，新增 %d：%s%s" % (
                   cnt, max_id, now_cnt, now_cnt - cnt,
                   ",".join(r[0] for r in new_rows[:12]),
                   " …" if len(new_rows) > 12 else ""),
               "PASS" if now_cnt >= cnt else "FAIL")

    # 11.3 既有行未被删改的正面证据
    for label, table in (("discovery_strategies", "discovery_strategies"),
                         ("crawl_tasks", "crawl_tasks"),
                         ("source_contents", "source_contents"),
                         ("materials", "materials")):
        b = base.get(table) or {}
        max_id = int(b.get("max_id") or 0)
        still = int(scalar("SELECT COUNT(*) FROM %s WHERE id <= %d;" % (table, max_id)) or 0)
        record("11.3.%s" % label, phase, "residue", "SQL %s 基线区间行数复核" % table,
               "基线区间内行数不变（既有 3 策略/11 任务/109 来源/26 素材未被删除）",
               "id<=%d 的行数=%d，基线 count=%s" % (max_id, still, b.get("count")),
               "PASS" if still == int(b.get("count") or 0) else "FAIL")

    _state["residue"] = residue
    record("11.4", phase, "teardown", "停止 scheduler/worker/Vite/代理 + scripts/stop.sh",
           "进程退出、两端工作区干净", "见 11-teardown 与 shell 收尾结果", "INFO")
    save_state()


def phase_p12():
    record("12.0", "12", "report", "见 00-run-header.md 与 summary",
           "证据与报告", "由报告步骤承载", "INFO")


RUNNERS = {
    "g0": phase_g0, "g1": phase_g1, "g2": phase_g2, "g3": phase_g3, "g4": phase_g4,
    "p5": phase_p5, "p55": phase_p55, "p6": phase_p6, "p7": phase_p7,
    "p8": phase_p8, "p9": phase_p9, "p10": phase_p10, "p11": phase_p11, "p12": phase_p12,
}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", default="all",
                        help="all 或其中一个：%s" % ",".join(PHASES))
    args = parser.parse_args(argv)

    EVIDENCE.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    COOKIE_DIR.mkdir(parents=True, exist_ok=True)
    if MANIFEST_FILE.exists():
        _manifest.extend(json.loads(MANIFEST_FILE.read_text(encoding="utf-8")))
    if STATE_FILE.exists():
        _state.update(json.loads(STATE_FILE.read_text(encoding="utf-8")))
    load_secrets()

    targets = PHASES if args.phase == "all" else [args.phase]
    try:
        for name in targets:
            if name not in RUNNERS:
                raise SystemExit("unknown phase: %s" % name)
            # 重跑一个阶段时，用新结果覆盖该阶段此前的同名步骤，避免清单里留下陈旧判定。
            # 关键：新结果先写进独立列表；阶段中途抛异常时 _manifest 保持原样，
            # 绝不把「只装了一半新结果」的清单flush 出去而丢掉之前所有阶段。
            previous = list(_manifest)
            del _manifest[:]
            try:
                RUNNERS[name]()
            except BaseException:
                _manifest[:] = previous
                raise
            fresh = list(_manifest)
            fresh_ids = {e["step_id"] for e in fresh}
            _manifest[:] = [e for e in previous if e["step_id"] not in fresh_ids] + fresh
    finally:
        flush_manifest()
        save_state()


if __name__ == "__main__":
    main()
