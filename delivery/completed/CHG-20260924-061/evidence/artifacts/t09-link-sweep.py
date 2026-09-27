import re, subprocess, sys, pathlib

root = pathlib.Path(subprocess.run(
    ["git","rev-parse","--show-toplevel"], capture_output=True, text=True).stdout.strip())

def tracked_md():
    out = subprocess.run(["git","ls-files","-z","-c","--","*.md"],
                         capture_output=True, text=True).stdout
    return [p for p in out.split("\0") if p]

files = tracked_md()
print(f"denominator: {len(files)} tracked *.md")
print(f"  openable:   {sum(1 for f in files if (root/f).is_file())}")

# strip fenced code blocks and inline code spans so code-shaped link text
# cannot masquerade as a real link (both directions verified separately).
FENCE = re.compile(r"```.*?```", re.S)
SPAN  = re.compile(r"`[^`\n]*`")
LINK  = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")

unresolved = []
checked = 0
for rel in files:
    p = root/rel
    if not p.is_file():
        continue
    text = SCI = FENCE.sub("", p.read_text(encoding="utf-8", errors="replace"))
    text = SPAN.sub("", text)
    for target in LINK.findall(text):
        if target.startswith(("http://","https://","mailto:","#")) or target.startswith("<"):
            continue
        path_part = target.split("#")[0]
        if not path_part:
            continue
        checked += 1
        dest = (p.parent/path_part).resolve()
        if not dest.exists():
            unresolved.append((rel, target))
print(f"relative in-site links checked: {checked}")
print(f"unresolved: {len(unresolved)}")
for rel, t in unresolved:
    print(f"  MISS  {rel}  ->  {t}")
