# Dev runtime guardrails

## 时间

2026-07-24

## 背景

在真实 Desktop 验收中，登录和本机可信绑定反复失败，原因不是用户操作，而是开发运行环境和业务校验口径没有被固定：

- Desktop dev `/api` 代理曾指向旧端口 `8080`，当前 Cloud 使用 `18080`；
- 本地 HTTP 验收时 session cookie 不能带 `Secure`；
- 本机可信绑定曾错误要求 BitBrowser 所有窗口都已同步到 Cloud；
- 接口测试使用 `replace_existing=true` 会挤占页面会话，测试后必须注销。

## 固定规则

后续启动 M2 Desktop 验收环境必须满足：

```text
Cloud API: 127.0.0.1:18080
Desktop Web: 127.0.0.1:5174
Local Agent: 127.0.0.1:8765
Cloud session cookie: WT_MEDIA_SESSION_COOKIE_SECURE=false
Desktop /api proxy: http://127.0.0.1:18080
Desktop cloudBaseUrl: http://127.0.0.1:18080
```

本机可信绑定规则：

```text
只校验当前用户会话、Local Agent节点凭证、BitBrowser可用性、main_user_id一致。
不要求本机所有BitBrowser窗口都已存在于Cloud。
未知窗口进入M2-B Profile Diff，不阻断可信绑定。
```

接口测试规则：

```text
如果用 operator01 + replace_existing=true 做接口测试，测试后必须立即 logout。
否则会挤占用户正在验收的Desktop页面会话。
```

## 目的

防止后续 Codex 或人工验收再次把启动配置、Cookie配置、Profile Diff边界和会话挤占误判为业务功能失败。
