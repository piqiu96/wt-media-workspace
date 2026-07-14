#!/usr/bin/env python3
"""Prepare or inspect the outer WT Media AI workspace."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = ROOT.parent
REQUIRED_DIRS = [
    "wt-media-workspace",
    "wt-media-cloud",
    "wt-media-agent",
    "wt-media-desktop",
]


def main() -> int:
    missing = [name for name in REQUIRED_DIRS if not (WORKSPACE_ROOT / name).is_dir()]
    if missing:
        print(f"missing required directories: {', '.join(missing)}")
        return 1

    summary = {
        "workspace_root": str(WORKSPACE_ROOT),
        "mode": "workspace-governance-active",
        "runtime_repositories": REQUIRED_DIRS[1:],
        "docs_location": str(ROOT / "docs"),
        "delivery_active": str(ROOT / "delivery" / "active"),
        "workspace_repository": str(ROOT),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
