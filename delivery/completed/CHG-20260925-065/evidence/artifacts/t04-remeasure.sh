#!/usr/bin/env bash
# Re-measure the generator's output with the GATE'S OWN functions (not an ad-hoc
# script). Builds a throwaway workspace whose ROOT is the tmpdir, so
# verify_agent_entry.py resolves the generated repo relative to it.
set -uo pipefail

WS=/Users/aqiuye/Develop/workspace/wt-media/wt-media-workspace
T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

mkdir -p "$T/cloud-generated"
git -C "$T/cloud-generated" init -q
cp -R "$WS/scripts" "$T/scripts"

bash "$WS/scripts/init-agent-entry.sh" repo "$T/cloud-generated" >"$T/gen.log" 2>&1
echo "generator exit=$? ; files:"; (cd "$T/cloud-generated" && ls -1)

echo
echo "=== gate functions on the generator's own output ==="
python3 -B -X pycache_prefix=/tmp/pyc-none - "$T" <<'PY'
import importlib.util, sys
from pathlib import Path

T = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("vae", T / "scripts" / "verify_agent_entry.py")
m = importlib.util.module_from_spec(spec)
sys.modules["vae"] = m
spec.loader.exec_module(m)
print("ROOT resolved to:", m.ROOT)

repos = {"cloud": "cloud-generated"}

def show(label, value):
    if label == "check_rule_text_duplication":
        warnings, note = value
        print(f"{label}: WARN {len(warnings)} ; note: {note}")
        for w in warnings:
            print("   W", w)
    elif isinstance(value, tuple):
        errors, warnings = value[0], value[1] if len(value) > 1 else []
        print(f"{label}: ERROR {len(errors)} / WARN {len(warnings)}")
        for e in errors:
            print("   E", e)
        for w in warnings:
            print("   W", w)
    else:
        print(f"{label}: {len(value)} finding(s)")
        for item in value:
            print("   ", item)

show("check_repo_entry_files", m.check_repo_entry_files(repos))
show("check_pointer_shape", m.check_pointer_shape(repos))
show("check_rule_body_consistency", m.check_rule_body_consistency(repos))
show("check_layer3_shape", m.check_layer3_shape(repos))
show("check_rule_text_duplication", m.check_rule_text_duplication(repos))
show("check_local_order_scope", m.check_local_order_scope(repos))

print()
print("=== positive controls (same functions, deliberately broken tree) ===")
repo = T / "cloud-generated"

# 1. delete an entry file
(repo / "DIRECTORY_MAP.md").unlink()
show("PC1 rm DIRECTORY_MAP.md -> check_repo_entry_files", m.check_repo_entry_files(repos))
(repo / "DIRECTORY_MAP.md").write_text("# d\n## x\n", encoding="utf-8")

# 2. restate a rule in a pointer
pointer = repo / "CLAUDE.md"
pointer.write_text(pointer.read_text(encoding="utf-8") + "\n不得新建 internal/runtime。\n", encoding="utf-8")
show("PC2 rule line in CLAUDE.md -> check_pointer_shape", m.check_pointer_shape(repos))

# 3. break the local-order scope in the body
body = repo / "AGENT-INDEX.md"
text = body.read_text(encoding="utf-8")
text = text.replace("## 本仓内加载顺序", "## 本仓内加载顺序\n\n1. `.ai/CURRENT_CONTEXT.md`\n", 1)
body.write_text(text, encoding="utf-8")
show("PC3 CURRENT_CONTEXT in local order -> check_local_order_scope", m.check_local_order_scope(repos))
PY
