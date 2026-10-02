# CHG-20261002-074 实施进度（2026-10-02）

契约 v2 主线：**阶段 1（会话 client_type 解耦）已完成并提交**；阶段 2/3 未开始。范围与验收以 [change.md](change.md) 为准。

## 阶段 1 完成（wt-media-cloud `11ce766`，2026-10-02）

- `user_sessions` 新增 `client_type` 列（迁移 `20261002_046`，存量会话回填 `web`）。
- client_type 由服务端从 `Origin` 头推断（`tauri.localhost` → desktop，其余 → web），复用既有 `isLocalDesktopOrigin`；落库 `Session.ClientType`，**非客户端自报字段**（浏览器 Origin 为 forbidden header 不可伪造）。
- 登录替换只失效**同类型**旧会话（20010 仅同类型活跃会话存在时触发）；desktop 与 web 会话共存互不挤。
- `Logout` 改为只失效当前会话；用户停用/更新仍全量失效（安全动作，语义与登录替换不同）。
- 契约 `identity.openapi.yaml` 登录接口补充 client_type 推断语义。
- 单测：`go test ./internal/modules/identity/...` 全绿；新增登录矩阵（共存、同类型冲突、跨类型不冲突、Logout 只清自身）。
- 前端零改动（Origin 由 desktop webview 自动携带）。

## 下一步

- **实机走查**（用户驱动）：迁移 046 先经 `scripts/migrate.sh` 应用到真实 MySQL，再验 desktop 与 web 同账号双会话并存不互挤、同类型才 20010。
- 阶段 2：执行凭据独立 + 设备级持久化（cloud + desktop）。
- 阶段 3：数据模型（dedupe 改维、解绑重分配、DownloadCentre 重取、profilebinding 自助、23002/23003）。
