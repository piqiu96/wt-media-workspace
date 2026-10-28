"""从Workspace根目录执行，检查离线示例的Token、资源、标识与规范引用。"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import re

root = Path.cwd()
class Document(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.ids=[]; self.labels=[]
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        for key in ['href','src']:
            if attrs.get(key): self.links.append(attrs[key])
        if attrs.get('id'): self.ids.append(attrs['id'])
        if tag=='label' and attrs.get('for'): self.labels.append(attrs['for'])

checks=[]
for file in sorted((root/'example').rglob('*.html')):
    doc=Document(); doc.feed(file.read_text())
    assert len(doc.ids)==len(set(doc.ids)), f'{file}: 重复ID'
    assert all(target in doc.ids for target in doc.labels), f'{file}: label关联丢失'
    for link in doc.links:
        url=urlsplit(link)
        assert not url.scheme and not url.netloc, f'{file}: 外部资源 {link}'
        assert not url.path or (file.parent/unquote(url.path)).exists(), f'{file}: 路径失效 {link}'
    checks.append(str(file.relative_to(root))+': IDs / labels / local links PASS')
for file in [*(root/'example').rglob('*.md'),root/'docs/standards/frontend/README.md']:
    text=re.sub(r'```.*?```','',file.read_text(),flags=re.S)
    for link in re.findall(r'\[[^\]]*\]\(([^)\s]+)\)',text):
        url=urlsplit(link)
        if not url.scheme and url.path: assert (file.parent/unquote(url.path)).exists(), f'{file}: {link}'
    checks.append(str(file.relative_to(root))+': Markdown links PASS')
source=(root/'docs/standards/frontend/前端架构与视觉规范.md').read_text()
block=re.search(r'### 3\.6\.1 颜色\s+```css\n(.*?)\n```',source,re.S).group(1)
css=(root/'example/common/example.css').read_text()
tokens=lambda text: dict(re.findall(r'(--wt-[\w-]+):\s*([^;]+);',text))
assert tokens(block)==tokens(css), '示例Token与正式规范不一致'
checks.append(f'{len(tokens(block))} Token values: exact match PASS')
js=(root/'example/common/example.js').read_text()+(root/'example/common/controls.js').read_text()
assert not re.search(r'\b(fetch\s*\(|XMLHttpRequest|WebSocket\s*\(|setInterval\s*\(|setTimeout\s*\()',js), '禁止联网或自动成功计时器'
assert '/Users/' not in js+css, '公共素材不可依赖本机路径'
checks.append('Offline behavior / portable resources PASS')
print('\n'.join(checks))
print(f'STATIC PASS ({len(checks)} groups)')
