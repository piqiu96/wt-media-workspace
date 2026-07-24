# Login proxy fix evidence

## 时间

2026-07-24

## 问题

用户在真实 Desktop 登录 `operator01` 时页面提示“服务器返回格式错误”。

## 定位

Desktop dev server 的 `/api` 代理仍指向旧端口 `127.0.0.1:8080`，而当前验收 Cloud API 固定运行在 `127.0.0.1:18080`。因此登录请求没有稳定返回统一 API JSON。

同时，本地 HTTP 验收环境需要禁用 session cookie 的 `Secure` 标记，否则 Desktop/WebView 在 `http://127.0.0.1` 下可能无法稳定保存登录会话。

## 修改

- `web/vite.config.cloud.js`：`/api` 代理改为 `http://127.0.0.1:18080`。
- `web/vite.config.desktop.js`：`/api` 代理改为 `http://127.0.0.1:18080`。
- `web/src/apps/desktop/features/local-agent/init.js`：Desktop 本地 `cloudBaseUrl()` 开发默认值改为 `http://127.0.0.1:18080`。
- Cloud 验收启动参数增加 `WT_MEDIA_SESSION_COOKIE_SECURE=false`。

## 验证

通过 Desktop dev server 代理请求：

```text
POST http://127.0.0.1:5174/api/v1/auth/login
```

实际返回：

```text
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Set-Cookie: wt_media_session=...; path=/; HttpOnly; SameSite=Lax
{"errcode":0,"message":"success","data":{"username":"operator01","role":"operator",...}}
```

测试登录会话已随后注销，避免影响用户人工验收。

## 结论

Desktop 登录链路已恢复为标准统一响应；用户可重新在真实 Desktop 窗口使用 `operator01 / operator123` 登录验收。
