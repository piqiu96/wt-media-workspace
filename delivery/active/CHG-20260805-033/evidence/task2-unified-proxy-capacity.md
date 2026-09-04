# Task 2：统一代理窗口配额

## 变更事实

- 迁移 026 将每个代理的容量收敛为 `proxy_configs.max_profile_count`；旧表中如有多平台配额，取其最大值。当前开发库 `proxy_configs` 与旧配额表均为 0 行。
- 迁移新增 `browser_profiles.proxy_id`，作为后续读回成功后的正式 Profile—代理关系；当前不做不可靠的 host/port 猜测迁移。
- 旧 `proxy_platform_quotas` 在迁移完成后删除；代理 API 和页面改为单一“最大窗口数”。

## 验证

- `go test ./internal/modules/proxy ./internal/modules/migration -count=1`：通过。
- `npm test -- --run`：41 项通过。
- `npm run build:cloud`、`npm run build:desktop`：通过。

## 后续

Task 3 在 Agent 写入 BitBrowser 并读回成功后才写入 `browser_profiles.proxy_id`，再以该正式关系计算已用/剩余；本 Task 不提前伪造分配事实。
