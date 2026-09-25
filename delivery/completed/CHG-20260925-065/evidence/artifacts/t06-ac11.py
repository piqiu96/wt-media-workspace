#!/usr/bin/env python3
"""AC-11: no file may keep an exclusion list of build/artifact paths.

Criterion (line level): the line says 扫描 AND enumerates at least one
concrete build/artifact path.  The vocabulary matters -- a POINTER line
(`禁止默认扫描的目录见 `DIRECTORY_MAP.md` 的「禁止扫描区」`) also says 扫描
but enumerates nothing, and a lock-file RULE (`...由依赖工具生成，禁止手改。`)
says 禁止 but not 扫描.  Both were false positives before the criterion was
tightened; see evidence/task-05-cloud.md s4 and task-06-agent.md s4.

Anchors are commits, never HEAD: HEAD stops being a control the instant the
fix is committed (it becomes a mirror -- same reading as "no such line").
"""
import re
import subprocess
import sys

# Build/artifact paths. Deliberately a closed vocabulary so a pointer line
# cannot satisfy it by naming a document.
PATH_RE = re.compile(
    r"(dist|node_modules|__pycache__|\.venv|logs?|target|build|"
    r"\.gitignore|uv\.lock|dependency\.lock|[A-Za-z0-9_.-]+\.(log|out|pyc))"
)
SCAN_RE = re.compile("扫描")

REPOS = {
    "cloud": "/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud",
    "agent": "/Users/aqiuye/Develop/workspace/wt-media/wt-media-agent",
    "desktop": "/Users/aqiuye/Develop/workspace/wt-media/wt-media-desktop",
    "workspace": "/Users/aqiuye/Develop/workspace/wt-media/wt-media-workspace",
}


def hits(lines):
    out = []
    for i, line in enumerate(lines, 1):
        if SCAN_RE.search(line) and PATH_RE.search(line):
            out.append((i, line.strip()))
    return out


def read(repo, name, ref):
    if ref == "WORKTREE":
        with open(f"{REPOS[repo]}/{name}", encoding="utf-8") as fh:
            return fh.read().splitlines()
    txt = subprocess.run(
        ["git", "-C", REPOS[repo], "show", f"{ref}:{name}"],
        capture_output=True, text=True, check=True,
    ).stdout
    return txt.splitlines()


def main():
    repo, name, ref = sys.argv[1], sys.argv[2], sys.argv[3]
    lines = read(repo, name, ref)
    nonempty = [l for l in lines if l.strip()]
    h = hits(lines)
    print(f"{repo}:{name} @ {ref} -- {len(lines)} line(s) scanned "
          f"({len(nonempty)} non-empty), {len(h)} hit(s)")
    for i, line in h:
        print(f"  {i}: {line}")
    return 0 if not h else 1


if __name__ == "__main__":
    sys.exit(main())
