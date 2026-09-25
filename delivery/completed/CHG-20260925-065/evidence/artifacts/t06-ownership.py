#!/usr/bin/env python3
"""Line-level ownership analysis for a runtime repo's entry files.

Usage: t06-ownership.py <repo> <ref>

For every NON-EMPTY line of each pre-change file, ask whether a normalised
equivalent survives in the post-change tree.  A line with no equivalent is a
candidate for silent content loss and must be given an explicit destination --
that is the whole point of "只搬家不改义".  Lines that DO have an equivalent
are reported as covered without listing them individually.

Denominator: the pre-change non-empty line count, per file.  Reported, because
"0 lines lost" is meaningless without it.

Anchor is a commit ref, never HEAD -- see t06-ac11.py for why.
"""
import re
import subprocess
import sys
from pathlib import Path

REPOS = {
    "cloud": Path("/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud"),
    "agent": Path("/Users/aqiuye/Develop/workspace/wt-media/wt-media-agent"),
    "desktop": Path("/Users/aqiuye/Develop/workspace/wt-media/wt-media-desktop"),
    "workspace": Path("/Users/aqiuye/Develop/workspace/wt-media/wt-media-workspace"),
}
SOURCES = ("AGENTS.md", "CLAUDE.md", "AGENT-INDEX.md")
TARGETS = ("AGENT-INDEX.md", "DIRECTORY_MAP.md")

EMPHASIS = re.compile(r"[*_`#>|\-—–:：。，、；;！!？?（）()\[\]{}「」【】\s]+")
NUM = re.compile(r"^\d+[.、)]?\s*")


def norm(text):
    return EMPHASIS.sub("", NUM.sub("", text.strip()))


def git_show(repo, ref, name):
    out = subprocess.run(["git", "-C", str(repo), "show", f"{ref}:{name}"],
                         capture_output=True, text=True)
    return out.stdout.splitlines() if out.returncode == 0 else []


def worktree(repo, name):
    p = repo / name
    return p.read_text(encoding="utf-8").splitlines() if p.exists() else []


def main():
    repo_key, ref = sys.argv[1], sys.argv[2]
    repo = REPOS[repo_key]
    target_text = norm(" ".join(l for n in TARGETS for l in worktree(repo, n)))
    total_unique = total_lines = 0
    for src in SOURCES:
        before = git_show(repo, ref, src)
        after = worktree(repo, src)
        nonempty = [l for l in before if l.strip()]
        changed = before != after
        print(f"\n=== {src}  ({'CHANGED' if changed else 'unchanged'})  "
              f"denominator = {len(before)} lines / {len(nonempty)} non-empty ===")
        if not changed:
            print("  (not modified by this task -- no ownership question)")
            continue
        unique = [l for l in nonempty if norm(l) and norm(l) not in target_text]
        total_unique += len(unique)
        total_lines += len(nonempty)
        print(f"  covered by target files: {len(nonempty) - len(unique)}"
              f"   /   needing manual disposition: {len(unique)}")
        for l in unique:
            print(f"    ? {l.strip()[:150]}")
    print(f"\nTOTAL: {total_unique} line(s) need disposition out of "
          f"{total_lines} non-empty pre-change line(s) in modified files")


if __name__ == "__main__":
    main()
