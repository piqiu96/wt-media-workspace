# 2026-09-06 代理来源与绑定窗口可见性

- 变更：新增静态代理地址解析、动态 API 手动提取/刷新、绑定窗口详情和代理表格多选列；动态提取仅更新 Cloud 台账并重新检测，未调用 BitBrowser 写入。
- Cloud 验证：`env GOCACHE=... go test ./internal/app ./internal/modules/proxy ./internal/modules/profilebinding -count=1` 通过。
- Web 验证：`npm test -- --run`，12 个测试文件、47 项通过；`npm run build:cloud` 与 `npm run build:desktop` 通过（仅既有包体积告警）。
- Agent 验证：`.venv/bin/python -m unittest discover -s tests`，83 项通过；包含本地 `/api/v1/proxy-extract` 回环路由和纯文本首条代理解析测试。
- 安全事实：`proxy_configs.extract_url` 仅服务端保存；代理列表和普通详情不包含提取 URL、用户名或密码。地址解析和提取预览仅向当前已授权请求返回草稿字段。动态 API 仅允许 HTTP/HTTPS 来源；无 BitBrowser Profile 写入或读回副作用。
- 未替代人工验收：真实供应商 API、真实代理连通性及后续浏览器窗口同步仍需在有真实资源的本地环境中验收。
