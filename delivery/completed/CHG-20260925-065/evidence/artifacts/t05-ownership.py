#!/usr/bin/env python3
"""Line-level ownership analysis for cloud's four entry files.

For each CLAUDE.md line, ask: is there a normalised equivalent in AGENTS.md?
Lines with no equivalent are the ones that carry content the target shape would
LOSE, so they must each be given a destination. Denominator = pre-change lines.
"""
import re
import sys
from pathlib import Path

REPO = Path("/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud")
CLOUD = Path("wt-media-cloud")

EMPHASIS = re.compile(r"[*_`#>|\-—–:：。，、；;！!？?（）()\[\]{}「」【】\s]+")
NUM = re.compile(r"^\d+[.、)]?\s*")


def norm(text: str) -> str:
    return EMPHASIS.sub("", NUM.sub("", text.strip()))


def lines_of(name: str) -> list[str]:
    return (REPO / name).read_text(encoding="utf-8").splitlines()


def cover_report(src_name: str, ref_names: tuple[str, ...]) -> None:
    src = lines_of(src_name)
    ref_text = norm(" ".join(l for n in ref_names for l in lines_of(n)))
    unique: list[tuple[int, str]] = []
    covered = 0
    counted = 0
    for number, line in enumerate(src, start=1):
        stripped = line.strip()
        if not stripped:
            continue
        counted += 1
        key = norm(stripped)
        if not key:
            covered += 1
            continue
        if key in ref_text:
            covered += 1
        else:
            unique.append((number, stripped))
    print(f"\n=== {src_name}: {counted} non-empty line(s) (denominator), "
          f"{covered} covered by {', '.join(ref_names)}, {len(unique)} without an equivalent ===")
    for number, stripped in unique:
        print(f"  :{number} {stripped[:150]}")


print("### reference: AGENTS.md lines vs AGENT-INDEX.md (rules the body already holds)")
cover_report("AGENTS.md", ("AGENT-INDEX.md", "DIRECTORY_MAP.md"))
print("\n### CLAUDE.md lines vs AGENTS.md + AGENT-INDEX.md + DIRECTORY_MAP.md")
cover_report("CLAUDE.md", ("AGENTS.md", "AGENT-INDEX.md", "DIRECTORY_MAP.md"))
print("\n### AGENT-INDEX.md lines vs AGENTS.md (body lines not yet in AGENTS.md)")
cover_report("AGENT-INDEX.md", ("AGENTS.md",))
print("\n### DIRECTORY_MAP.md lines vs AGENT-INDEX.md + AGENTS.md")
cover_report("DIRECTORY_MAP.md", ("AGENT-INDEX.md", "AGENTS.md"))
