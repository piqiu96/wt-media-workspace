# CHG-20260724-029 Start Gate

日期：2026-07-24

## 核对结果

- Active CHG：`CHG-20260724-029`
- `CURRENT_CONTEXT`：指向 `CHG-20260724-029`
- `delivery/LEDGER.md`：仅列出 `CHG-20260724-029`
- 关联 Milestone：`delivery/milestones/M2-account-runtime.md#M2-B-浏览器窗口与媒体账号真实闭环`
- 影响仓库：`wt-media-cloud`、`wt-media-agent`、`wt-media-desktop`、`wt-media-workspace`

## 当前事实

- `wt-media-agent` 已有 Local Agent 同步接口雏形：
  - `/api/v1/bit-browser/profile-scans`
  - `/api/v1/bit-browser/profile-create`
  - `/api/v1/bit-browser/profile-open`
  - `/api/v1/bit-browser/profile-close`
  - `/api/v1/bit-browser/profile-update`
- Agent BitBrowser adapter 已有 `group_list()`，但 Local Agent HTTP API 尚未暴露分组读取入口。
- `wt-media-desktop` 已有 Tauri/Rust：
  - `local_agent_profile_scan`
  - `local_agent_profile_restore`
- `wt-media-desktop` 尚缺 Tauri/Rust：
  - 打开窗口
  - 关闭窗口
  - 新建窗口
  - 读取 BitBrowser 分组
- `wt-media-cloud/web` 的浏览器窗口页仍通过 Cloud API 调用新建/打开/关闭，并提示“已创建任务”，与本 CHG 的同步本机操作口径不一致。
- `wt-media-cloud/internal/modules/profilebinding/routes.go` 仍保留 `POST /api/v1/browser-profiles`、`/open`、`/close`、`PATCH` 创建 Cloud Agent 异步任务的实现。
- Cloud schema 当前 `browser_profiles.id` 仍是字符串主键，且被媒体账号、敏感锁和运行态表引用；Milestone 中“自增主键”要求需要单独 schema CHG 处理，本 CHG 不强行迁移主键。

## 缺口

- Desktop 页面需要改为通过 Tauri/Rust 调 Local Agent，而不是通过 Cloud 创建异步任务。
- Cloud Web 需要保持只读，不能展示或触发本机 BitBrowser 操作入口。
- 新建窗口必须选择真实 BitBrowser 分组并在 BitBrowser 创建成功、读回后再更新 Cloud 镜像。
- 打开/关闭窗口必须同步调用 BitBrowser，并给运营展示明确成功/失败结果。
- 删除语义需要从“删除”改为“停用/归档 Cloud 镜像”，不得真实删除 BitBrowser Profile。
- 浏览器窗口列表需要补齐搜索、分页、状态筛选和用户可读字段。

## 文件映射

- Cloud Profile 路由与服务：
  - `wt-media-cloud/internal/modules/profilebinding/routes.go`
  - `wt-media-cloud/internal/modules/profilebinding/service.go`
  - `wt-media-cloud/internal/modules/profilebinding/store_mysql.go`
- Cloud/Desktop 共用前端：
  - `wt-media-cloud/web/src/modules/profiles/pages/ProfilesPage.vue`
  - `wt-media-cloud/web/src/shared/api/profileBindings.js`
  - `wt-media-cloud/web/src/apps/desktop/features/local-agent/service.js`
- Desktop Rust：
  - `wt-media-desktop/src-tauri/src/main.rs`
- Local Agent：
  - `wt-media-agent/src/wt_media_agent/local_api/server.py`
  - `wt-media-agent/src/wt_media_agent/runtimes/bitbrowser.py`
  - `wt-media-agent/contracts/local-agent-api/v1/local-agent.openapi.yaml`

## 测试计划

- Agent：新增/更新 Local Agent profile 操作单元测试。
- Desktop：`cargo test` 覆盖 Rust payload 和读回校验辅助函数。
- Web：`npm test` 覆盖 Local Agent service 和 Profile Binding client 基础行为。
- Cloud：`go test ./internal/modules/profilebinding` 覆盖列表、归档/停用和 Cloud 只读边界。

## 风险

- `browser_profiles.id` 主键迁移牵动多表外键，本 CHG 不处理；只在页面明确展示系统记录ID与 BitBrowser Profile ID。
- BitBrowser 创建字段可能随真实接口有差异，本 CHG 以现有 adapter allow-list 字段为准，并通过读回验证避免 Cloud 假成功。
