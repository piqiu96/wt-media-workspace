#!/usr/bin/env python3
"""AC-02: does the value the *shipped* config declares stop the `ipc://` refusals?

CHG-20260923-056 measured a counterfactual: with `ipc: http://ipc.localhost
http://127.0.0.1:18080` the `ipc://` refusals went 3 -> 0. That leg passed the
value in as a literal. It did not read it from anywhere, so it proved the *value*
works and said nothing about whether the *shipped file* carries it.

This driver closes that gap, and nothing more. It reads `csp_connect_src` out of
`resources/desktop.production.toml` — the real file on disk — and launches the
real binary with it, twice:

  S1  the value parsed from the shipped file  -> ipc:// refusals must be 0
  S2  the pre-change value, by hand           -> ipc:// refusals must be > 0

S2 is the positive control, and without it S1's zero means nothing: a counter
that never increments also reads zero. S2 is the same launch, same probe, same
binary, one config line apart, and it must reproduce CHG-056's non-zero
baseline. If S2 ever reads 0, this tool has stopped measuring and S1's zero is
not evidence.

**Deliberate narrowness, stated rather than implied.** The legs run with
`environment = "development"` and a scratch agent port, because the shipped file
is a *production* config with `agent.port = 8765` — the port the developer's own
dev Agent holds. A faithful whole-file launch would try to bind it, so this is
not that. What is under test here is the shipped `csp_connect_src` **value**; the
production validation rules around the file are covered by `config.rs`'s unit
tests, and the fact that the shipped file's value reaches the policy is covered
by the golden test in `bootstrap.rs`. Neither of those is re-asserted here.

Everything else — the probe page, the launch, the violation collection, the
per-leg assertions — is CHG-056's tool, imported rather than copied, so the two
runs cannot drift apart.

Usage: python3 t02_csp_shipped_value_launch.py [--skip-build] [--legs S1|S2]
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

WORKSPACE = Path("/Users/aqiuye/Develop/workspace/wt-media/wt-media-workspace")
TOOL = (
    WORKSPACE
    / "delivery/completed/CHG-20260923-056/evidence/tools/ac05_desktop_launch.py"
)
SHIPPED_TOML = (
    WORKSPACE / "../wt-media-desktop/src-tauri/resources/desktop.production.toml"
).resolve()

# What the file said before CHG-20260924-060, spelled out here rather than read
# from git: the control arm must stay pinned to a fixed string, or a future edit
# to either the file or the history would silently move it.
PRE_CHANGE = "http://127.0.0.1:18080"


def load_tool():
    spec = importlib.util.spec_from_file_location("ac05_tool", TOOL)
    if spec is None or spec.loader is None:
        raise SystemExit(f"HARD STOP: cannot import {TOOL}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def shipped_csp_value(path: Path) -> str:
    """The one line under test, as the file actually spells it."""
    match = re.search(
        r'^\s*csp_connect_src\s*=\s*"(.*)"\s*$', path.read_text(encoding="utf-8"), re.M
    )
    if match is None:
        raise SystemExit(f"HARD STOP: no csp_connect_src in {path}")
    return match.group(1)


def main() -> int:
    legs = sys.argv[sys.argv.index("--legs") + 1].split(",") if "--legs" in sys.argv else ["S1", "S2"]

    tool = load_tool()
    shipped = shipped_csp_value(SHIPPED_TOML)

    print(f"shipped config: {SHIPPED_TOML}")
    print(f"  csp_connect_src = {shipped!r}")
    print(f"  pre-change value = {PRE_CHANGE!r}")

    if shipped == PRE_CHANGE:
        print("HARD STOP: the shipped value is unchanged, so S1 would be vacuous")
        return 2
    if "ipc:" not in shipped:
        print("HARD STOP: the shipped value carries no `ipc:`, so S1 cannot pass")
        return 2

    status, _ = tool.request(f"{tool.CLOUD}/healthz")
    if status != 200:
        print(f"HARD STOP: no Cloud at {tool.CLOUD} (healthz -> {status})")
        return 2

    tool.SCRATCH.mkdir(parents=True, exist_ok=True)
    (tool.SCRATCH / "probe").mkdir(parents=True, exist_ok=True)
    for item in tool.PROBE_SOURCE.iterdir():
        import shutil

        shutil.copy(item, tool.SCRATCH / "probe" / item.name)

    if "--skip-build" not in sys.argv:
        tool.section("BUILD: the probe page, embedded as the app's frontend")
        tool.build(tool.SCRATCH / "probe")
    if not tool.BINARY.is_file():
        print(f"HARD STOP: no binary at {tool.BINARY}")
        return 2

    try:
        if "S1" in legs:
            tool.run_leg(
                "S1-shipped-value",
                python_fallback=False,
                env_fallback="1",
                sidecar_present=False,
                csp_connect_src=shipped,
                expect_start=("label", "started"),
                expect_ipc_violation=False,
            )
        if "S2" in legs:
            tool.run_leg(
                "S2-control-pre-change-value",
                python_fallback=False,
                env_fallback="1",
                sidecar_present=False,
                csp_connect_src=PRE_CHANGE,
                expect_start=("label", "started"),
                expect_ipc_violation=True,
            )
    finally:
        if tool.SIDECAR_SLOT.exists():
            tool.SIDECAR_SLOT.unlink()
            print(f"\n  removed the stand-in sidecar from {tool.SIDECAR_SLOT}")

    print()
    print("=" * 78)
    if tool.failures:
        print(f"RESULT: FAIL ({len(tool.failures)})")
        for item in tool.failures:
            print(f"  - {item}")
        return 1
    print(
        "RESULT: PASS -- the value the shipped config declares drives the ipc:// "
        "refusals to zero, and the pre-change value still produces them"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
