#!/usr/bin/env python3
"""AC-06: the four chains the Desktop proxies, driven against the Agent itself.

bind / account-check / cookie-read / profile, hitting the Agent's local API --
which is exactly what the Desktop's commands call, so this exercises the same
target with a shorter path.

**What this tool refuses to do.** `POST /api/v1/cookie-read` returns real cookie
values for a real logged-in profile. Those are credentials under ADR-0016 and by
this CHG's own rule they may not be logged or put in evidence. So no cookie
value is ever printed, formatted, or written to the output of this tool: the
tool keeps them in memory only to *search the agent's log for them* and assert
they are absent, which is the one use that improves the evidence instead of
polluting it. Counts, names, and lengths are printed; values never are.

**What it does to the machine.** It opens and then closes one BitBrowser
profile, so the end state is the starting state. The profile is discovered by
name (`m2b-bilibili-login`, the acceptance profile) rather than hardcoded, and
the tool asserts at the end that the profile is closed again -- a chain that
leaves a browser window open on someone's desktop would be a side effect the
evidence failed to mention.

**Coverage is enumerated, not implied.** The summary at the end lists, per
chain, what was exercised and what could not be -- a green run over three of
four branches is not a green run over the chain.

Usage: python3 ac06_local_chains.py
"""

from __future__ import annotations

import json
import os
import re
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
TOKEN = "ac06-token-5b90e2"
PROFILE_NAME = "m2b-bilibili-login"

failures: list[str] = []
#: (chain, what was exercised) -- printed as the coverage table.
covered: list[tuple[str, str]] = []
#: (chain, what was NOT exercised, and why) -- printed as loudly as the rest.
uncovered: list[tuple[str, str]] = []


def fail(what: str) -> None:
    failures.append(what)
    print(f"    FAIL: {what}")


def ok(chain: str, what: str) -> None:
    covered.append((chain, what))


def gap(chain: str, what: str) -> None:
    uncovered.append((chain, what))


def section(title: str) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def call(port: int, path: str, payload: dict | None = None, token: str | None = TOKEN,
         timeout: int = 60) -> tuple[int, dict]:
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=data, method="POST")
    if data is not None:
        request.add_header("content-type", "application/json")
    if token is not None:
        request.add_header("authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            return response.status, _json(raw)
    except urllib.error.HTTPError as exc:
        return exc.code, _json(exc.read())


def _json(raw: bytes) -> dict:
    try:
        return json.loads(raw or b"{}")
    except json.JSONDecodeError:
        return {"raw": raw.decode("utf-8", "replace")[:300]}


def scan(port: int) -> list[dict]:
    status, body = call(port, "/api/v1/bit-browser/profile-scans", {})
    if status != 200:
        fail(f"profile-scans -> {status} {body}")
        return []
    return body.get("profiles") or []


def profile_status(port: int, profile_id: str) -> object:
    for record in scan(port):
        if record.get("bit_profile_id") == profile_id:
            return record.get("status")
    return None


def wait_for_status(port: int, profile_id: str, wanted, timeout: float = 20) -> object:
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        last = profile_status(port, profile_id)
        if last == wanted:
            return last
        time.sleep(0.5)
    return last


def close_until_settled(port: int, profile_id: str, baseline, timeout: float = 30) -> object:
    """Close, and keep asking BitBrowser until its own status agrees.

    One call is not enough, and the reason is worth stating: closing a profile
    that BitBrowser still considers to be starting up is refused with
    `{"success":false,"msg":"浏览器正在打开中"}`, and `close_profile`
    (`clients/bitbrowser/client.py:169-174`) catches that error and passes, so
    the Agent reports `{"status": "closed"}` either way. BitBrowser's own
    `status` field is therefore the only ground truth for whether a close took
    effect, and this helper treats it as such.
    """
    deadline = time.time() + timeout
    status = profile_status(port, profile_id)
    while time.time() < deadline:
        call(port, "/api/v1/bit-browser/profile-close", {"id": profile_id})
        status = wait_for_status(port, profile_id, baseline, timeout=5)
        if status == baseline:
            return status
        time.sleep(1)
    return status


# ---------------------------------------------------------------- chains


def chain_bind(port: int) -> None:
    section("CHAIN 1/4: bind")
    status, body = call(port, "/api/v1/bind", {"binding_token": "ac06-ticket", "node_id": "ac06-node"})
    print(f"  POST /api/v1/bind                     -> {status} {json.dumps(body)[:160]}")
    session = body.get("session_token", "")
    if status != 200 or body.get("status") != "bound":
        fail("bind did not report a completed binding")
    elif body.get("node_id") != "ac06-node":
        fail(f"bind did not echo the node id: {body.get('node_id')!r}")
    elif not re.fullmatch(r"[0-9a-f]{64}", session or ""):
        fail(f"bind's session token is not 32 random bytes: {len(session or '')} chars")
    else:
        ok("bind", "200 with a node id and a fresh 64-hex session token")

    status, body = call(port, "/api/v1/bind", {"node_id": "ac06-node"})
    print(f"  POST /api/v1/bind  (no token)         -> {status} {json.dumps(body)[:100]}")
    if status != 400 or (body.get("error") or "") != "binding_token_required":
        fail(f"a bind with no binding_token gave {status} {body}")
    else:
        ok("bind", "400 binding_token_required when the token is missing")

    # Two binds must not hand out the same session token.
    _, first = call(port, "/api/v1/bind", {"binding_token": "t1"})
    _, second = call(port, "/api/v1/bind", {"binding_token": "t2"})
    if first.get("session_token") == second.get("session_token"):
        fail("two binds produced the same session token")
    else:
        ok("bind", "each bind mints a distinct session token")

    # Recorded rather than asserted: this handler answers entirely on its own.
    # It never contacts Cloud, so "bound" here means "the Agent minted itself a
    # session", not "Cloud accepted the binding".
    gap("bind", "no Cloud round trip: the handler only mints a local session token "
                "and sets node_id in memory (local_api/server.py:474-497)")


def chain_profile(port: int, profile: dict) -> None:
    section("CHAIN 2/4: profile")
    profile_id = profile["bit_profile_id"]
    profiles = scan(port)
    print(f"  POST /api/v1/bit-browser/profile-scans -> 200, {len(profiles)} profiles, "
          f"main_user_id={profiles[0].get('main_user_id') if profiles else None}")
    if not profiles:
        fail("the scan returned no profiles")
        return
    ok("profile", f"scan returns the real profile set ({len(profiles)} profiles with names and groups)")

    status, body = call(port, "/api/v1/bit-browser/profile-groups", {})
    groups = (body.get("data") or {}).get("groups") or []
    print(f"  POST /api/v1/bit-browser/profile-groups -> {status}, {len(groups)} groups")
    if status != 200 or not groups:
        fail(f"profile-groups -> {status} {body}")
    else:
        ok("profile", f"group listing ({len(groups)} groups)")

    before = profile["status"]
    print(f"  using {PROFILE_NAME!r} = {profile_id} (status={before})")

    status, body = call(port, "/api/v1/bit-browser/profile-open", {"id": profile_id})
    opened = (body.get("data") or {}).get("status")
    print(f"  POST /api/v1/bit-browser/profile-open  -> {status} {json.dumps(body)[:120]}")
    if status != 200 or opened != "opened":
        fail(f"profile-open -> {status} {body}")
    after_open = wait_for_status(port, profile_id, 1) if before != 1 else profile_status(port, profile_id)
    print(f"    BitBrowser profile status: {before} -> {after_open}")

    status, body = call(port, "/api/v1/bit-browser/profile-close", {"id": profile_id})
    closed = (body.get("data") or {}).get("status")
    after_close = close_until_settled(port, profile_id, before)
    print(f"  POST /api/v1/bit-browser/profile-close -> {status} {json.dumps(body)[:120]}")
    print(f"    BitBrowser profile status: {after_open} -> {after_close} (after retrying)")

    if after_open == after_close:
        # Not a failure of the API -- it answered 200 -- but this evidence then
        # cannot tell an open from a close by BitBrowser's own state, so the
        # claim narrows to "the calls were accepted".
        gap("profile", "open and close both answered 200, but BitBrowser's own `status` "
                       f"field did not move ({before} -> {after_open} -> {after_close}), so the "
                       "state change is reported by the Agent and not confirmed by the browser")
    else:
        ok("profile", f"open and close move BitBrowser's own status field "
                      f"({before} -> {after_open} -> {after_close})")

    status, body = call(port, "/api/v1/bit-browser/profile-close", {})
    print(f"  POST /api/v1/bit-browser/profile-close (no id) -> {status} {json.dumps(body)[:90]}")
    if status != 400:
        fail(f"profile-close without an id gave {status}")
    else:
        ok("profile", "400 when the profile id is missing")

    gap("profile", "profile-create / -update / -delete were NOT driven: they mutate the "
                   "real profile inventory, and this CHG has no mandate to add or destroy "
                   "the user's profiles. Only scan/groups/open/close were exercised.")
    gap("profile", "a close that BitBrowser refuses is reported as success: closing a profile "
                   "that is still starting up answers {\"success\":false,\"msg\":\"浏览器正在打开中\"}, "
                   "and close_profile (clients/bitbrowser/client.py:169-174) catches that and "
                   "passes, so the API returns status=closed either way. BitBrowser's own "
                   "status field is the only way to tell. Pre-existing, not changed by this CHG.")


def chain_account_check(port: int, profile_id: str) -> dict:
    section("CHAIN 3/4: account-check")
    status, body = call(port, "/api/v1/account-check",
                        {"profile_id": profile_id, "platform": "bilibili"})
    data = body.get("data") or {}
    print(f"  POST /api/v1/account-check (bilibili)  -> {status}")
    print(f"    login_status={data.get('login_status')!r} "
          f"platform_account_id={data.get('platform_account_id')!r} "
          f"check_items={len(data.get('check_items') or [])}")
    if status != 200:
        fail(f"account-check -> {status} {json.dumps(body)[:200]}")
        gap("account-check", f"the call failed ({status}), so nothing about identification ran")
        return {}

    status, body = call(port, "/api/v1/account-check", {"profile_id": profile_id, "platform": "weibo"})
    print(f"  POST /api/v1/account-check (weibo)     -> {status} "
          f"{(body.get('error') or {}).get('code') if isinstance(body.get('error'), dict) else body.get('error')!r}")
    if status != 400:
        fail(f"an unsupported platform gave {status}, expected 400")
    else:
        ok("account-check", "400 account_check_input_invalid for a platform outside "
                            "{bilibili, baijiahao, douyin}")

    account_id = data.get("platform_account_id")
    if not account_id:
        gap("account-check", f"the profile is not logged in to bilibili "
                             f"(login_status={data.get('login_status')!r}), so the "
                             "expected-account branch could not be reached")
        return data

    ok("account-check", f"identified a real logged-in account ({account_id!r}) "
                        f"with {len(data.get('check_items') or [])} check items")

    status, body = call(port, "/api/v1/account-check",
                        {"profile_id": profile_id, "platform": "bilibili",
                         "expected_platform_account_id": account_id})
    matching = (body.get("data") or {}).get("login_status")
    print(f"  POST /api/v1/account-check (expected=the real id) -> {status} login_status={matching!r}")
    if matching == "account_mismatch":
        fail("the real account id was reported as a mismatch")
    else:
        ok("account-check", "the expected id matching the real one is not flagged")

    status, body = call(port, "/api/v1/account-check",
                        {"profile_id": profile_id, "platform": "bilibili",
                         "expected_platform_account_id": "ac06-not-the-real-account"})
    mismatched = body.get("data") or {}
    print(f"  POST /api/v1/account-check (expected=a wrong id) -> {status} "
          f"login_status={mismatched.get('login_status')!r} message={mismatched.get('message')!r}")
    if mismatched.get("login_status") != "account_mismatch":
        fail("a wrong expected id was not flagged as account_mismatch")
    elif mismatched.get("message") != "当前窗口登录账号与媒体账号台账不一致":
        fail(f"the mismatch message changed: {mismatched.get('message')!r}")
    else:
        ok("account-check", "a wrong expected id is flagged account_mismatch with the "
                            "product's message -- both directions of the rule")
    return data


def chain_cookie_read(port: int, profile_id: str, log: Path) -> None:
    section("CHAIN 4/4: cookie-read")
    status, body = call(port, "/api/v1/cookie-read", {"profile_id": profile_id})
    cookies = (body.get("data") or {}).get("cookies") or []
    print(f"  POST /api/v1/cookie-read              -> {status}, {len(cookies)} cookies")
    if status != 200:
        fail(f"cookie-read -> {status} {json.dumps(body)[:200]}")
        gap("cookie-read", f"the call failed ({status})")
        return
    if not cookies:
        fail("cookie-read returned an empty jar for a logged-in profile")
        return

    pairs = [(str(c.get("name", "")), str(c.get("value", ""))) for c in cookies if isinstance(c, dict)]
    names = [name for name, _ in pairs]
    # Names and sizes only. The values stay in this process.
    print(f"    names={sorted(names)}")
    print(f"    total value bytes={sum(len(v) for _, v in pairs)} (values deliberately not printed)")
    ok("cookie-read", f"the real cookie jar came back ({len(cookies)} cookies: {', '.join(sorted(names))})")

    # The reason the values were kept: the product must not log them.
    #
    # Only values long enough to be a credential are searched, and the sizes
    # matter: `home_feed_column` and `bmg_af_switch` come back with a
    # one-character value, which matches any log that contains that character.
    # The first version of this check searched those too and duly reported a
    # leak that did not exist. A substring search is only evidence for a value
    # that could not plausibly occur by accident, so the searchable set is
    # values of >= 8 characters and everything shorter is named as unsearched.
    text = log.read_text() if log.is_file() else ""
    searchable = [(name, value) for name, value in pairs if len(value) >= 8]
    too_short = sorted({name for name, value in pairs if len(value) < 8})
    leaked = [name for name, value in searchable if value in text]

    # Control: the scan must be able to find something that is definitely there,
    # or "not found" says nothing about the logger.
    control = profile_id in text
    print(f"    agent log: searched {len(searchable)}/{len(pairs)} values (>=8 chars); "
          f"too short to search: {too_short or 'none'}")
    print(f"    control: the profile id is present in the log -> {control}"
          f" ({'scan works' if control else 'SCAN IS BROKEN'})")
    print(f"    leak: {'LEAKED ' + str(leaked) if leaked else 'no cookie value found'}")
    if not control:
        fail("the log scan cannot find a string that must be in the log, so its "
             "'no leak' result is meaningless")
    elif leaked:
        fail(f"the agent logged cookie values for {leaked}")
    else:
        ok("cookie-read", f"none of the {len(searchable)} searchable cookie values appear "
                          f"in the agent's log ({len(too_short)} too short to search: {too_short})")

    status, body = call(port, "/api/v1/cookie-read", {})
    print(f"  POST /api/v1/cookie-read (no id)      -> {status} {json.dumps(body)[:90]}")
    if status != 400:
        fail(f"cookie-read without a profile id gave {status}")
    else:
        ok("cookie-read", "400 cookie_read_input_invalid when the profile id is missing")


def main() -> int:
    port = free_port()
    log = Path(tempfile.gettempdir()) / "ac06-agent.log"
    data_dir = Path(tempfile.mkdtemp(prefix="wt-ac06-")) / "data"
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": os.environ.get("HOME", str(Path.home())),
        "PYTHONPATH": str(AGENT_DIR / "src"),
        "WT_MEDIA_AGENT_DATA_DIR": str(data_dir),
        "WT_MEDIA_AGENT_RUNTIME_TOKEN": TOKEN,
        "WT_MEDIA_LOCAL_API_HOST": "127.0.0.1",
        "WT_MEDIA_LOCAL_API_PORT": str(port),
        "WT_MEDIA_LOG_LEVEL": "INFO",
        "PYTHONUNBUFFERED": "1",
    }
    print(f"agent: {AGENT_DIR}")
    print(f"log:   {log}")
    proc = subprocess.Popen(
        [str(PYTHON), "-m", "wt_media_agent.local_main"],
        cwd=AGENT_DIR, env=env, stdout=log.open("w"), stderr=subprocess.STDOUT,
        text=True, start_new_session=True,
    )

    profile_id = ""
    try:
        deadline = time.time() + 30
        up = False
        while time.time() < deadline and not up:
            try:
                status, _ = call(port, "/api/v1/bind", {"binding_token": "probe"}, timeout=3)
                up = status == 200
            except Exception:
                time.sleep(0.3)
        if not up:
            print("HARD STOP: the agent never came up")
            print(log.read_text()[-2000:])
            return 2
        print(f"agent up on 127.0.0.1:{port} (token enforced)")

        status, body = call(port, "/api/v1/bind", {"binding_token": "x"}, token=None)
        if status != 401:
            fail(f"a chain answered {status} without the token")
        else:
            ok("all chains", "401 without the bearer token")

        profiles = [p for p in scan(port) if p.get("name") == PROFILE_NAME]
        if not profiles:
            print(f"HARD STOP: no profile named {PROFILE_NAME!r}; the chains that need a "
                  f"logged-in profile cannot be judged without one")
            return 2
        profile = profiles[0]
        profile_id = profile["bit_profile_id"]

        chain_bind(port)
        chain_profile(port, profile)
        chain_account_check(port, profile_id)
        chain_cookie_read(port, profile_id, log)

        # Leave the machine as it was found. account-check and cookie-read both
        # open the profile as a side effect of what they do, so this is the
        # close that actually matters.
        final = close_until_settled(port, profile_id, profile["status"])
        print()
        print(f"  end state: {PROFILE_NAME} status={final} (started at {profile['status']})")
        if final != profile["status"]:
            fail(f"the profile was left at status={final}, not {profile['status']}")
        else:
            ok("profile", f"the profile was returned to its starting state (status={final}) "
                          f"after account-check and cookie-read opened it")
    finally:
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
        print(f"  agent stopped (exit={proc.returncode})")

    print()
    print("=" * 78)
    print(f"COVERAGE ({len(covered)} exercised, {len(uncovered)} not)")
    print("=" * 78)
    for chain, what in covered:
        print(f"  [x] {chain:<15} {what}")
    for chain, what in uncovered:
        print(f"  [ ] {chain:<15} {what}")

    print()
    if failures:
        print(f"RESULT: FAIL ({len(failures)})")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("RESULT: PASS -- every driven chain answered as specified, and nothing was left open")
    return 0


if __name__ == "__main__":
    sys.exit(main())
