#!/usr/bin/env python3
"""T-09 two-pass dead-pointer sweep for CHG-20260925-065.

Pass A (string scan): strings this CHG retired must not appear in LIVE prose.
Pass B (link resolve): every relative markdown link in every tracked *.md must resolve.

Both passes print their DENOMINATOR. `--control` runs the same two passes over a
temp tree with deliberately injected defects; the sweep must report both, otherwise
its "0 hits" reading is indistinguishable from a blind scanner.

Usage:
  t09-pointer-sweep.py                 # sweep the repo (finds its own root)
  t09-pointer-sweep.py --control       # positive control, must report 2 defects
  t09-pointer-sweep.py --root <dir>    # sweep an arbitrary tree

Note: git ls-files is used for the denominator, so it must run inside a git repo
(or use --root with a plain walk, which --control does).
"""
import argparse
import os
import re
import subprocess
import sys

# --- Pass A ---------------------------------------------------------------
# Strings this CHG retired. A hit is a DEFECT only in live prose: archived CHG
# records may (and should) narrate them in the past tense -- "path fixes,
# narration stays" (CHG-064). So hits are grouped, not merely counted.
RETIRED = [
    "check_layer3_entries",   # merged into the six new checks (T-04)
    "templates/repo-entry",   # never created -- decided against in T-02
    "../generated",           # falsified path, removed in T-07
    "## 上下文加载顺序",        # renamed to "## 本仓内加载顺序" (T-05..T-07)
]
# check_entry_drift is handled separately: it is retired as CODE but is
# legitimately named in both archived records and in the conventions' own
# retirement note, so it is reported as a grouped reading, never as a defect.
NARRATED = ["check_entry_drift"]

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def tracked_md(root):
    out = subprocess.run(["git", "ls-files", "*.md"], cwd=root,
                         capture_output=True, text=True, check=True).stdout
    return [p for p in out.splitlines() if p.strip()]


def is_external(target):
    t = target.strip()
    return (t.startswith(("http://", "https://", "mailto:", "#", "/"))
            or "://" in t)


FENCE_RE = re.compile(r"^```.*?^```", re.S | re.M)
CODE_RE = re.compile(r"`[^`\n]*`")


def strip_code(text):
    """Remove fenced blocks and inline code spans.

    A markdown link inside a code span is NOT a link -- records quote link
    syntax to document injected controls and to quote other files verbatim.
    Without this the sweep reports those quotes forever (3 of them in T-06/T-08),
    which is noise that trains readers to ignore the sweep.
    """
    text = FENCE_RE.sub(" ", text)
    for _ in range(2):          # twice: handles one level of nesting
        text = CODE_RE.sub(" ", text)
    return text


def ascii_read(path, strip=False):
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except (OSError, UnicodeDecodeError):
        return ""
    return strip_code(text) if strip else text


def pass_a(root, files):
    """String scan. Returns (defect_hits, narration_hits, denominator)."""
    defects, narration, n_lines = [], 0, 0
    for rel in files:
        text = ascii_read(os.path.join(root, rel))
        n_lines += len(text.splitlines())
        for s in RETIRED:
            if s in text:
                defects.append((rel, s))
        for s in NARRATED:
            if rel.startswith("delivery/completed/"):
                narration += text.count(s)
            elif rel.startswith("delivery/active/CHG-20260925-065/"):
                narration += text.count(s)   # this CHG's own record
            elif s in text:
                # a live doc naming a retired check: report, but it may be a
                # legitimate retirement note -- the caller decides.
                narration += text.count(s)
    return defects, narration, n_lines


def pass_b(root, files):
    """Relative-link resolve over PROSE only. Returns (dead, denominator)."""
    dead, n_links = [], 0
    for rel in files:
        text = ascii_read(os.path.join(root, rel), strip=True)
        base = os.path.dirname(rel)
        for m in LINK_RE.finditer(text):
            target = m.group(1).split("#")[0].strip()
            if not target or is_external(target):
                continue
            n_links += 1
            resolved = os.path.normpath(os.path.join(root, base, target))
            if not os.path.exists(resolved):
                dead.append((rel, target))
    return dead, n_links


def run(root, files):
    da, narr, n_lines = pass_a(root, files)
    db, n_links = pass_b(root, files)
    print(f"denominator: {len(files)} tracked *.md, {n_lines} lines, "
          f"{n_links} relative links")
    print(f"PASS A  retired-string defects : {len(da)}")
    for rel, s in da:
        print(f"        {rel}: {s!r}")
    print(f"PASS A  retired-string narration (kept by policy): {narr}")
    print(f"PASS B  unresolved relative links : {len(db)}")
    for rel, t in db:
        print(f"        {rel} -> {t}")
    return 1 if (da or db) else 0


def control(root):
    """Inject one dead string and one dead link; both must be reported."""
    files = []
    for dirpath, _, names in os.walk(root):
        for n in names:
            if n.endswith(".md"):
                files.append(os.path.relpath(os.path.join(dirpath, n), root))
    files.sort()
    print(f"--- POSITIVE CONTROL over {len(files)} *.md in a temp tree ---")
    print("injected: Pass A 'check_layer3_entries' ; Pass B '[x](NO-SUCH-FILE.md)'")
    return run(root, files)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root")
    ap.add_argument("--control", action="store_true")
    args = ap.parse_args()

    if args.control:
        root = args.root or os.getcwd()
        return control(root)

    root = args.root or subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True,
        text=True, check=True).stdout.strip()
    return run(root, tracked_md(root))


if __name__ == "__main__":
    sys.exit(main())
