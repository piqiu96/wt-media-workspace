#!/usr/bin/env python3
"""Desktop 走查用：在 5174 上同时提供「打包 Desktop 前端产物」的静态服务与 /api 反向代理。

为什么必须是 5174（两处都是硬编码，无法换端口）：
  - `wt-media-cloud/web/src/shared/api/http.js` 的 `defaultApiBase()` 只在
    `window.location.port === '5174'` 时保留相对基址 `/api/v1`，其他端口一律改用
    编译期写死的 `http://127.0.0.1:18080/api/v1`。
  - `wt-media-cloud/internal/middleware/cors.go` 的 CORS 白名单只放行
    `tauri.localhost` 与 `127.0.0.1:5174`。

静态根是 DMG 里打进 Tauri 的那份产物（`wt-media-desktop/.generated/frontend`），
因此走查对象就是打包产物本身，不是 dev 模式前端。

代理在转发 /api/* 时补上 `Cookie: wt_media_session=<值>`，使无头 Chrome 拿到已登录
界面——与既有 `tools/cookie-proxy.py` 同一手法。

三项点击交互由注入的 `/__walk.js` 驱动（无头 Chrome 本身不能点击）。注入方式是在
静态返回的 index.html 的 </body> 前插入**一个** script 标签；应用自身产物逐字节未改。
即使注入了，`__walk.js` 也只在 URL 带 `#walk=<场景>` 时动作，否则立即返回。

用法：
    WT_MEDIA_M3_SESSION=<cookie 值> python3 desktop-walkthrough-proxy.py 5174 18080 <静态根>

安全：cookie 值只从环境变量读入，不写入日志、不落盘。
"""
import http.server
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

LISTEN = int(sys.argv[1]) if len(sys.argv) > 1 else 5174
TARGET = int(sys.argv[2]) if len(sys.argv) > 2 else 18080
ROOT = Path(sys.argv[3]) if len(sys.argv) > 3 else None
SESSION = os.environ["WT_MEDIA_M3_SESSION"]

UPSTREAM = "http://127.0.0.1:%d" % TARGET
HOP = {"connection", "keep-alive", "transfer-encoding", "upgrade", "proxy-authenticate",
       "proxy-authorization", "te", "trailers", "content-length", "host"}

WALK_JS = """
(function () {
  var m = (location.hash || '').match(/walk=([a-z0-9-]+)/i);
  if (!m) return;
  var scenario = m[1];
  function status(s) { document.title = 'WALK:' + s; }
  function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
  function waitFor(fn, timeout) {
    timeout = timeout || 20000;
    var start = Date.now();
    return new Promise(function (resolve, reject) {
      (function loop() {
        var v = null;
        try { v = fn(); } catch (e) { v = null; }
        if (v) return resolve(v);
        if (Date.now() - start > timeout) return reject(new Error('waitFor timeout'));
        setTimeout(loop, 150);
      })();
    });
  }
  function byText(sel, text) {
    var list = document.querySelectorAll(sel), i;
    for (i = 0; i < list.length; i++) {
      if ((list[i].textContent || '').trim() === text) return list[i];
    }
    for (i = 0; i < list.length; i++) {
      if ((list[i].textContent || '').indexOf(text) >= 0) return list[i];
    }
    return null;
  }
  function sidebarReady() {
    return (document.body.innerText || '').indexOf('挖掘策略') >= 0;
  }
  function progress() {
    var m = (document.body.innerText || '').match(/当前\s*(\d+)\s*\/\s*(\d+)/);
    return m ? { index: m[1], total: m[2] } : null;
  }
  var TABS = {
    'task-detail': '结果概览',
    'task-detail-items': '发现内容',
    'task-detail-process': '执行过程',
    'task-detail-errors': '异常记录'
  };
  async function run() {
    try {
      await waitFor(sidebarReady, 25000);   // 等登录态与主框架渲染
      await sleep(800);
      if (scenario === 'strategy-edit') {
        var editBtn = await waitFor(function () { return byText('button', '编辑'); }, 15000);
        editBtn.click();
        await waitFor(function () {
          return byText('.t-dialog', '编辑挖掘策略');
        }, 10000);
      } else if (scenario.indexOf('task-detail') === 0) {
        var detailBtn = await waitFor(function () { return byText('button', '详情'); }, 15000);
        detailBtn.click();
        await waitFor(function () {
          return byText('.t-drawer', '挖掘任务详情');
        }, 10000);
        var tabName = TABS[scenario];
        if (tabName && tabName !== TABS['task-detail']) {
          var tab = await waitFor(function () {
            return byText('.t-tabs__nav-item', tabName) || byText('.t-tabs__tab', tabName);
          }, 8000);
          tab.click();
          await sleep(600);
        }
      } else if (scenario === 'review-mode' || scenario === 'review-skip') {
        var btn = await waitFor(function () { return document.querySelector('.review-mode-button'); }, 15000);
        if (btn.disabled) throw new Error('review-mode-button disabled');
        btn.click();
        await waitFor(function () {
          return byText('.t-drawer', '内容审核');
        }, 10000);
        if (scenario === 'review-skip') {
          await sleep(800);
          var before = progress();
          var skip = await waitFor(function () { return byText('button', '跳过'); }, 8000);
          skip.click();
          await waitFor(function () {
            var p = progress();
            return p && before && p.index !== before.index;
          }, 12000);
          status('OK ' + scenario + ' ' + before.index + '->' + progress().index);
        }
      } else {
        throw new Error('unknown scenario');
      }
      await sleep(1500);
      // 冻结过渡/动画，避免把入场动画中途定格进截图
      var st = document.createElement('style');
      st.textContent = '*,*::before,*::after{transition:none !important;animation:none !important;}';
      document.head.appendChild(st);
      await sleep(1500);
      if (!document.title || document.title.indexOf('WALK:') !== 0) status('OK ' + scenario);
    } catch (e) {
      status('FAIL ' + scenario + ' ' + ((e && e.message) || 'error'));
    }
  }
  run();
})();
"""

INJECT = b'<script src="/__walk.js"></script>'


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):  # 静默
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

    def _send(self, code, payload, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _static(self):
        rel = self.path.split("?", 1)[0].split("#", 1)[0].lstrip("/")
        candidate = (ROOT / rel) if rel else (ROOT / "index.html")
        if candidate.is_dir():
            candidate = candidate / "index.html"
        if not candidate.is_file() or ROOT not in candidate.resolve().parents:
            candidate = ROOT / "index.html"      # SPA 回退
        payload = candidate.read_bytes()
        if candidate.name.endswith(".html"):
            if INJECT not in payload:
                payload = payload.replace(b"</body>", INJECT + b"</body>")
                if INJECT not in payload:
                    payload += INJECT
            return self._send(200, payload, "text/html; charset=utf-8")
        ctype = {
            ".js": "text/javascript", ".css": "text/css", ".json": "application/json",
            ".svg": "image/svg+xml", ".png": "image/png", ".woff2": "font/woff2",
        }.get(candidate.suffix, "application/octet-stream")
        return self._send(200, payload, ctype)

    def _handle(self):
        path = self.path.split("?", 1)[0]
        if path.startswith("/api/"):
            return self._proxy()
        if path == "/__walk.js":
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
    http.server.ThreadingHTTPServer(("127.0.0.1", LISTEN), Handler).serve_forever()
