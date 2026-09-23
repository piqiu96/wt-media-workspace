#!/usr/bin/env python3
"""视觉走查用：把已登录会话 cookie 注入到 /api 请求的本地反向代理。

浏览器直接访问 Vite(5180) 时没有会话 cookie，页面会跳登录页；本代理在
转发 /api/v1/* 时补上 `Cookie: wt_media_session=<值>`，使无头 Chrome 拿到
已登录的界面。

用法：
    WT_MEDIA_M3_SESSION=<cookie 值> python3 cookie-proxy.py 5190 5180

安全：cookie 值只从环境变量读入，不写入日志、不落盘。
"""
import http.server, os, sys, urllib.error, urllib.request

LISTEN = int(sys.argv[1]) if len(sys.argv) > 1 else 5190
TARGET = int(sys.argv[2]) if len(sys.argv) > 2 else 5180
SESSION = os.environ["WT_MEDIA_M3_SESSION"]

UPSTREAM = "http://127.0.0.1:%d" % TARGET
HOP = {"connection", "keep-alive", "transfer-encoding", "upgrade", "proxy-authenticate",
       "proxy-authorization", "te", "trailers", "content-length", "host"}


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
                status, payload = resp.status, resp.read()
                rheaders = resp.headers
        except urllib.error.HTTPError as exc:
            status, payload, rheaders = exc.code, exc.read(), exc.headers
        except urllib.error.URLError as exc:
            status, payload, rheaders = 502, str(exc).encode(), {}
        self.send_response(status)
        for key, value in (rheaders.items() if hasattr(rheaders, "items") else []):
            if key.lower() in HOP:
                continue
            self.send_header(key, value)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = do_OPTIONS = do_HEAD = _proxy


if __name__ == "__main__":
    http.server.ThreadingHTTPServer(("127.0.0.1", LISTEN), Handler).serve_forever()
