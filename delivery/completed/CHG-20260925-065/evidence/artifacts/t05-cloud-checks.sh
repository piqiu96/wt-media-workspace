#!/usr/bin/env bash
# AC-09 (infra enumeration matches disk) and AC-11 (no exclusion list left in
# AGENT-INDEX.md), each with a positive control proving the check can fail.
set -uo pipefail
CLOUD=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud
BASE=0346edf   # cloud pre-change commit (T-05 = 0db02ab); never HEAD
T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

echo "=== AC-09: every directory named on the infra rule line must exist ==="
python3 -B -X pycache_prefix=/tmp/pyc-none - "$CLOUD" <<'PY'
import re, sys
from pathlib import Path
repo = Path(sys.argv[1])
text = (repo / "AGENT-INDEX.md").read_text(encoding="utf-8")
lines = [l for l in text.splitlines() if "`internal/infra` 保存" in l]
print(f"matched rule line(s): {len(lines)} (denominator)")
names = re.findall(r"`([a-z]+)`", lines[0]) if lines else []
print(f"enumerated: {names}")
missing = [n for n in names if not (repo / "internal" / "infra" / n).is_dir()]
print(f"missing on disk: {missing or 'none'}")
print("RESULT:", "PASS" if lines and not missing else "FAIL")

# positive control: same check, one invented name added
bogus = names + ["cache"]
missing_bogus = [n for n in bogus if not (repo / "internal" / "infra" / n).is_dir()]
print(f"PC (inject 'cache'): missing -> {missing_bogus} =>",
      "check CAN fail" if missing_bogus else "CHECK IS BLIND")
PY

echo
echo "=== AC-11: no exclusion list left in AGENT-INDEX.md ==="
python3 -B -X pycache_prefix=/tmp/pyc-none - "$CLOUD" <<'PY'
import sys
from pathlib import Path
repo = Path(sys.argv[1])
name = "AGENT-INDEX.md"
# Anchor on the pre-change commit, NOT HEAD: once T-05 commits, HEAD is the
# fixed file and the control reads 0 - a mirror, not a control.
BASE = "0346edf"
text = (repo / name).read_text(encoding="utf-8")
lines = text.splitlines()
# An exclusion-list line names a build/artifact path AND a scan instruction.
marks = ("dist", "node_modules", "logs/", ".git")
hits = [(i, l) for i, l in enumerate(lines, 1)
        if any(m in l for m in marks) and ("禁止" in l or "扫描" in l)]
print(f"{name}: {len(lines)} line(s) (denominator), exclusion-list line(s): {len(hits)}")
for i, l in hits:
    print(f"  :{i} {l}")
print("RESULT:", "PASS" if not hits else "FAIL")

# positive control: same scan against the pre-change file from git
import subprocess
old = subprocess.run(["git", "-C", str(repo), "show", BASE + ":" + name],
                     capture_output=True, text=True).stdout
if not old:
    print("PC unavailable: no pre-change version")
else:
    old_hits = [(i, l) for i, l in enumerate(old.splitlines(), 1)
                if any(m in l for m in marks) and ("禁止" in l or "扫描" in l)]
    print(f"PC ({BASE}:{name}) exclusion-list line(s): {len(old_hits)} =>",
          "scan CAN see them" if old_hits else "CHECK IS BLIND")
PY

echo
echo "=== AC-10: line counts, pre-change ($BASE) vs now ==="
for f in AGENT-INDEX.md AGENTS.md CLAUDE.md DIRECTORY_MAP.md; do
  before=$(git -C "$CLOUD" show "$BASE:$f" | wc -l | tr -d ' ')
  after=$(wc -l < "$CLOUD/$f" | tr -d ' ')
  printf '%-18s before=%-5s after=%-5s\n' "$f" "$before" "$after"
done
