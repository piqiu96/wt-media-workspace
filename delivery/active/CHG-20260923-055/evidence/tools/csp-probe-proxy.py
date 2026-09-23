#!/usr/bin/env python3
"""CSP 模拟台：在 5174 上服务「打包 Desktop 前端产物」，并**原样附加应用的 CSP 响应头**。

为什么需要它
------------
DMG 里跑的是 WKWebView + Tauri 注入的 CSP，普通浏览器里跑的是「没有 CSP」。
首轮 Desktop 走查用无头 Chrome 直接看静态产物，**没有施加 CSP**，
因此结构上不可能发现「远程封面被 CSP 拦截」。本工具补上这一层：
把 `wt-media-desktop/src-tauri/tauri.conf.json` 的 `app.security.csp`
原样作为 `Content-Security-Policy` 响应头发给文档响应，
其余静态资源与 `/api` 反向代理行为与既有 `desktop-walkthrough-proxy.py` 一致。

为什么必须是 5174：与该工具相同（`defaultApiBase()` 与 CORS 白名单两处硬编码）。

探针
----
`/__probe.js` 只在 URL 带 `#probe=<标签>` 时动作；测得的 JSON 由它 POST 回
`/__probe`，代理侧打印为一行 `PROBE <标签> <json>`，便于脚本抓取。
被测对象是**应用自身产物逐字节未改**的静态文件（注入发生在 HTTP 响应阶段）。

用法：
    python3 csp-probe-proxy.py <静态根> --csp-file <tauri.conf.json> [--no-csp]
    WT_MEDIA_M3_SESSION=<cookie 值> 从环境变量读入

安全：cookie 只从环境变量读入，不写入日志、不落盘。
"""
import http.server
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

LISTEN = 5174
TARGET = 18080
UPSTREAM = "http://127.0.0.1:%d" % TARGET
HOP = {"connection", "keep-alive", "transfer-encoding", "upgrade", "proxy-authenticate",
       "proxy-authorization", "te", "trailers", "content-length", "host"}

SANDBOX = "%s:%d/api/v1" % ("http://127.0.0.1", TARGET)

WALK_JS = """
(function () {
  var m = (location.hash || '').match(/probe=([a-z0-9-]+)/i);
  if (!m) return;
  var label = m[1];
  function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
  function waitFor(fn, timeout) {
    timeout = timeout || 25000; var start = Date.now();
    return new Promise(function (resolve, reject) {
      (function loop() {
        var v = null; try { v = fn(); } catch (e) { v = null; }
        if (v) return resolve(v);
        if (Date.now() - start > timeout) return reject(new Error('waitFor timeout'));
        setTimeout(loop, 150);
      })();
    });
  }
  function ready() { return (document.body.innerText || '').indexOf('内容池') >= 0
                        && document.querySelectorAll('.t-table__body tr').length > 0; }
  function rect(el) {
    if (!el) return null;
    var r = el.getBoundingClientRect();
    return { left: Math.round(r.left), right: Math.round(r.right),
             width: Math.round(r.width), height: Math.round(r.height) };
  }
  async function run() {
    var out = { label: label, viewport: { w: window.innerWidth, h: window.innerHeight } };
    try {
      await waitFor(ready, 25000);
      await sleep(2500);                       // 留出图片加载/失败的时间
      // ---- 图片加载状态 ----
      var imgs = Array.prototype.slice.call(document.querySelectorAll('.title-media img'));
      out.img = {
        total: imgs.length,
        loaded: imgs.filter(function (i) { return i.complete && i.naturalWidth > 0; }).length,
        failed: imgs.filter(function (i) { return i.complete && i.naturalWidth === 0; }).length,
        pending: imgs.filter(function (i) { return !i.complete; }).length,
        sampleSrc: imgs.length ? String(imgs[0].src).slice(0, 90) : null
      };
      // ---- 表格几何：表头单元格 vs 右侧固定层 ----
      var host = document.querySelector('.wt-resource-table');
      var headers = Array.prototype.slice.call(
        document.querySelectorAll('.wt-resource-table .t-table__header th'));
      out.header = headers.map(function (th) {
        return { text: (th.innerText || '').trim().slice(0, 8), r: rect(th) };
      });
      var fixedEls = Array.prototype.slice.call(
        document.querySelectorAll('.t-table__fixed-right, .t-table__row--fixed-right, .t-table__cell--fixed-right'));
      out.fixed = fixedEls.map(function (e) { return { cls: e.className.slice(0, 60), r: rect(e) }; });
      // 内容区（承载横向滚动的那一层）
      var content = host ? host.querySelector('.t-table__content') : null;
      out.content = content ? {
        rect: rect(content),
        scrollWidth: content.scrollWidth,
        clientWidth: content.clientWidth,
        overflowX: getComputedStyle(content).overflowX
      } : null;
      var inner = content ? content.querySelector('table') : null;
      out.innerTable = inner ? {
        rect: rect(inner),
        styleWidth: inner.style.width || null,
        minWidth: getComputedStyle(inner).minWidth,
        tableLayout: getComputedStyle(inner).tableLayout,
        declaredWidth: inner.getAttribute('style')
      } : null;
      out.wrap = rect(document.querySelector('.table-scroll-wrap'));
      // 行高：是否被内容撑高超出行高声明（resource-module.css 声明 tr{height:56px}）
      var trs = Array.prototype.slice.call(
        document.querySelectorAll('.wt-resource-table .t-table__body tr')).slice(0, 8);
      out.rows = trs.map(function (tr) { return rect(tr).height; });
      // 右侧固定列每个 td 的实际高度：与本行行高逐一比对。
      // 若固定列被单独同步成「声明行高」而主表格行被内容撑高，两者会错位，
      // 视觉上就是「操作列压在来源列上」。
      var fcells = Array.prototype.slice.call(document.querySelectorAll(
        '.wt-resource-table .t-table__body .t-table__cell--fixed-right-first')).slice(0, 8);
      out.fixedBodyHeights = fcells.map(function (td) { return rect(td).height; });
      // 拆开一行：逐 td 高度 + 标题单元内部各件高度，定位到底是谁把行撑高的
      if (trs.length) {
        var tds = Array.prototype.slice.call(trs[0].querySelectorAll('td'));
        out.row0Cells = tds.map(function (td) {
          return { w: rect(td).width, h: rect(td).height,
                   txt: (td.innerText || '').trim().slice(0, 12) };
        });
        // td 的高度恒等于行高，本身说明不了谁把行撑高；只有内层「内容件」的高度
        // 和它的实际行盒数（getClientRects）能指出真正的驱动者。
        out.row0CellInners = tds.map(function (td) {
          var inner = td.querySelector('.title-cell, .source-cell, .interaction-cell, .author-cell')
                      || td.firstElementChild;
          if (!inner) return null;
          var rng = document.createRange();
          rng.selectNodeContents(inner);
          return { txt: (td.innerText || '').trim().slice(0, 10),
                   cls: String(inner.className).slice(0, 36),
                   h: rect(inner).height, w: rect(inner).width,
                   lineBoxes: rng.getClientRects().length };
        });
        // 来源列：服务端拼的 strategy_name + '_' + 14 位时间戳，是一段不可断行的长 ASCII
        var sc = trs[0].querySelector('.source-cell');
        out.sourceCell = sc ? {
          rect: rect(sc),
          whiteSpace: getComputedStyle(sc).whiteSpace,
          overflowWrap: getComputedStyle(sc).overflowWrap,
          wordBreak: getComputedStyle(sc).wordBreak,
          inner: Array.prototype.map.call(sc.children, function (c) {
            return { tag: c.tagName, h: rect(c).height,
                     txt: (c.innerText || '').trim().slice(0, 44) };
          })
        } : null;
        var tcell = trs[0].querySelector('.title-cell');
        out.row0TitleParts = tcell ? {
          cell: rect(tcell),
          media: rect(tcell.querySelector('.title-media')),
          mediaImg: rect(tcell.querySelector('.title-media img')),
          copy: rect(tcell.querySelector('.title-copy')),
          first: rect(tcell.querySelector('.title-copy > a, .title-copy > span')),
          small: rect(tcell.querySelector('.title-copy > small')),
          cellMinHeight: getComputedStyle(tcell).minHeight,
          tdPadding: getComputedStyle(tds[2] || tds[0]).padding,
          lineHeight: getComputedStyle(tcell.querySelector('.title-copy > a, .title-copy > span')).lineHeight,
          fontSize: getComputedStyle(tcell.querySelector('.title-copy > a, .title-copy > span')).fontSize
        } : null;
      }
      var tc = document.querySelector('.title-cell');
      out.titleCell = rect(tc);
      var tm = document.querySelector('.title-media');
      out.titleMedia = tm ? { rect: rect(tm), boxSizing: getComputedStyle(tm).boxSizing } : null;
      // 标题元素：是 <a> 还是 <span>，以及实际计算样式（省略号是否生效）
      var tlink = document.querySelector('.title-copy > a, .title-copy > span');
      if (tlink) {
        var cs = getComputedStyle(tlink);
        var r = tlink.getBoundingClientRect();
        out.titleEl = {
          tag: tlink.tagName, cls: tlink.className,
          textLen: (tlink.textContent || '').length,
          clientHeight: Math.round(r.height),
          whiteSpace: cs.whiteSpace, textOverflow: cs.textOverflow, overflow: cs.overflow
        };
      }
      // 滚到最右，检查右侧固定列与其自身表头/单元格是否仍然对齐
      if (label.indexOf('right') >= 0 && content) {
        content.scrollLeft = content.scrollWidth;
        await sleep(500);
        out.afterScrollRight = {
          scrollLeft: content.scrollLeft,
          fixedHeader: rect(document.querySelector('.t-table__header .t-table__cell--fixed-right-first')),
          fixedBody: rect(document.querySelector('.t-table__body .t-table__cell--fixed-right-first')),
          contentRect: rect(content)
        };
      }
      out.ok = true;
    } catch (e) {
      out.ok = false;
      out.error = (e && e.message) || String(e);
    }
    try {
      await fetch('/__probe', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(out)
      });
    } catch (e) {}
  }
  run();
})();
"""

INJECT = b'<script src="/__probe.js"></script>'


def load_csp(conf_path):
    """从 tauri.conf.json 读出应用真实生效的 CSP 字符串。"""
    data = json.loads(Path(conf_path).read_text(encoding="utf-8"))
    return data["app"]["security"]["csp"]


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):
        pass

    def _proxy(self):
        body = None
        length = self.headers.get("Content-Length")
        if length:
            body = self.rfile.read(int(length))
        headers = {k: v for k, v in self.headers.items() if k.lower() not in HOP}
        if self.path.startswith("/api/"):
            headers["Cookie"] = "wt_media_session=%s" % SESSION
        req = urllib.request.Request(UPSTREAM + self.path, data=body, headers=headers,
                                     method=self.command)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                code, payload, rheaders = resp.status, resp.read(), resp.headers
        except urllib.error.HTTPError as exc:
            code, payload, rheaders = exc.code, exc.read(), exc.headers
        except urllib.error.URLError as exc:
            code, payload, rheaders = 502, str(exc).encode(), {}
        self.send_response(code)
        for key, value in (rheaders.items() if hasattr(rheaders, "items") else []):
            if key.lower() in HOP:
                continue
            self.send_header(key, value)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _send(self, code, payload, ctype, csp=False):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        if csp and CSP:
            self.send_header("Content-Security-Policy", CSP)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _static(self):
        rel = self.path.split("?", 1)[0].split("#", 1)[0].lstrip("/")
        candidate = (ROOT / rel) if rel else (ROOT / "index.html")
        if candidate.is_dir():
            candidate = candidate / "index.html"
        if not candidate.is_file() or ROOT not in candidate.resolve().parents:
            candidate = ROOT / "index.html"
        payload = candidate.read_bytes()
        if candidate.name.endswith(".html"):
            if INJECT not in payload:
                payload = payload.replace(b"</body>", INJECT + b"</body>")
                if INJECT not in payload:
                    payload += INJECT
            return self._send(200, payload, "text/html; charset=utf-8", csp=True)
        ctype = {
            ".js": "text/javascript", ".css": "text/css", ".json": "application/json",
            ".svg": "image/svg+xml", ".png": "image/png", ".woff2": "font/woff2",
        }.get(candidate.suffix, "application/octet-stream")
        return self._send(200, payload, ctype)

    def _handle(self):
        path = self.path.split("?", 1)[0]
        if path == "/__probe" and self.command == "POST":
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length)
            try:
                data = json.loads(raw.decode("utf-8"))
                print("PROBE %s %s" % (data.get("label"), json.dumps(data, ensure_ascii=False)),
                      flush=True)
            except Exception as exc:
                print("PROBE-BAD %s" % exc, flush=True)
            return self._send(204, b"", "text/plain")
        if path.startswith("/api/"):
            return self._proxy()
        if path == "/__probe.js":
            return self._send(200, WALK_JS.encode("utf-8"), "text/javascript; charset=utf-8")
        if not ROOT:
            return self._send(500, b"static root not configured", "text/plain")
        return self._static()

    do_GET = _handle
    do_POST = _handle
    do_PUT = _handle
    do_PATCH = _handle
    do_DELETE = _handle
    do_OPTIONS = _handle
    do_HEAD = _handle


if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    csp_file = None
    if "--csp-file" in args:
        i = args.index("--csp-file")
        csp_file = args[i + 1]
        del args[i:i + 2]
    no_csp = "--no-csp" in args
    if no_csp:
        args.remove("--no-csp")
    ROOT = Path(args[0]).resolve() if args else None
    CSP = "" if no_csp else (load_csp(csp_file) if csp_file else "")
    SESSION = os.environ["WT_MEDIA_M3_SESSION"]
    print("CSP in effect: %s" % (CSP or "(none)"), flush=True)
    print("static root: %s" % ROOT, flush=True)
    http.server.ThreadingHTTPServer(("127.0.0.1", LISTEN), Handler).serve_forever()
