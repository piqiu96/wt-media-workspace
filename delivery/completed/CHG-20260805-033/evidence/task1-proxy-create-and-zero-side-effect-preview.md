# Task 1：代理创建与零副作用导入预览

## 变更事实

- Cloud 增加 `POST /api/v1/proxies/import/preview`：认证后只解析输入行并返回 `parsed`，不调用 Store 创建。
- `POST /api/v1/proxies/import` 保持为确认写入端点：服务端重新解析 `lines` 后才持久化，避免信任客户端预览对象。
- ProxyPage 增加“新增代理”表单；批量导入先调用预览端点，点击“确认导入”才调用写入端点。

## 验证

- 先执行新增路由测试，预览路由不存在时返回 404（红测）。
- 实现后执行 `go test ./internal/modules/proxy -run TestImportPreviewDoesNotPersistUntilConfirmed -count=1`：通过；同一请求预览后 Store 为 0，确认导入后 Store 为 1。
- `npm test -- --run`：41 项通过。
- `npm run build:cloud` 与 `npm run build:desktop`：通过。

## 边界

本 Task 不写入 BitBrowser、不调用 Agent、不调整代理配额或 Profile 关系；这些属于 CHG-033 后续 Task 2–6。
