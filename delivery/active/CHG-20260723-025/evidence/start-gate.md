# CHG-20260723-025 Start Gate：M2-B1 浏览器窗口扫描与 Diff 只读闭环

> 日期：2026-07-23  
> 执行范围：Task 1 Start Gate 与现状审计  
> 结论：可以继续作为 M2-B1 执行；进入 Task 2 前必须先处理/确认现有 runtime 脏改动。

## 1. Active CHG 一致性

| 检查项 | 结果 |
|---|---|
| `.ai/CURRENT_CONTEXT.md` | 指向 `CHG-20260723-025` |
| `delivery/LEDGER.md` | 指向 `CHG-20260723-025` |
| `delivery/active/CHG-20260723-025/change.md` | 存在，状态 `TODO` |
| Milestone 关联 | `delivery/milestones/M2-account-runtime.md#M2-B-浏览器窗口与媒体账号真实闭环` |

当前只有一个 M/L Active CHG 符合执行规则。

## 2. 本 CHG 用户可见结果

普通运营在 Desktop 可信环境下触发浏览器窗口扫描，Local Agent 同步读取 BitBrowser 窗口列表，Cloud 生成只读 Diff，页面展示新增、缺失和变更结果。

本 CHG 不应用 Diff，不创建窗口，不恢复 Cloud 配置，不绑定账号。

## 3. 权威依据

- `AGENTS.md`：M/L 实施必须存在 active CHG，并使用 `executing-wt-media-change`。
- `.ai/CURRENT_CONTEXT.md`：当前 Active CHG 为 `CHG-20260723-025`。
- `delivery/active/CHG-20260723-025/change.md`：本次只做 M2-B1 扫描与 Diff 只读闭环。
- `delivery/milestones/M2-account-runtime.md`：M2-B 要求扫描只生成 Diff，不应用；Cloud 授权用户、账号绑定、游戏、标签、备注、Cookie 和业务状态不能被扫描覆盖。
- `wt-media-cloud/AGENTS.md`：Cloud 拥有正式业务事实和权限。
- `wt-media-agent/AGENTS.md`：Agent 拥有 BitBrowser 集成和外部执行。
- `wt-media-desktop/AGENTS.md`：Vue 不直接访问 Local Agent 动态端口或 token，Rust 代理 Local Agent HTTP/SSE。
- 用户于 2026-07-23 确认：Desktop 后续严格通过 Rust 调 Local Agent；Cloud 没有 Agent 执行环境，只能查看 Cloud 基本信息，不能支持依赖 BitBrowser 的扫描、Diff处理或本机执行能力。

## 4. 当前代码事实

### Cloud ProfileBinding

可复用：

- `wt-media-cloud/internal/modules/profilebinding/service.go`
  - `SubmitScan` 已能接收快照并创建 `ProfileScan`；
  - 已校验 `main_user_id`、`profile_user_id`、重复 `bit_profile_id` 和已绑定主账号不匹配；
  - 已生成 `added`、`changed`、`missing` 三类 Diff；
  - `TestSubmitScanStagesDiffWithoutFormalMutation` 已覆盖“提交扫描不修改正式 profiles/bindings”。
- `wt-media-cloud/internal/modules/profilebinding/store_mysql.go`
  - `CreateScan` 写入 `profile_sync_scans` 和 `profile_sync_candidates`；
  - `FindScan` 可读取扫描和候选数据。
- `wt-media-cloud/internal/modules/profilebinding/routes.go`
  - 已有 `POST /api/v1/bit-browser/profile-scans`；
  - 已有 `GET /api/v1/bit-browser/profile-scans/:scan_id`。

需修正/补齐：

- `ProfileInput` 目前缺 `remark`、`proxy_type`、`proxy_host`、`proxy_port` 字段；前端 `safeProfile` 允许这些字段，但 Cloud input 没接住，导致代理/备注 Diff 不完整。
- `changedFields` 目前比较 `main_user_id`、`profile_user_id`、`name`、`seq`、`group_id`、`group_name`、`bit_status`、`bit_updated_at`，未比较代理和备注。
- Diff 结构只有 `kind/bit_profile_id/profile_id/fields`，页面能展示基本分类，但不足以表达“已绑定媒体账号影响”。
- `POST /profile-scans/:scan_id/confirm` 会应用 Profile 镜像，属于后续 B2；M2-B1 页面不能把它作为可操作结果。
- `POST /profile-scans/:scan_id/confirm-main-identity` 属于 M2-A 主账号确认链路，M2-B1 不应在扫描 Diff 页面继续突出为主要动作。

### Agent BitBrowser 扫描

可复用：

- `wt-media-agent/src/wt_media_agent/runtimes/bitbrowser.py`
  - `scan_profiles()` 已分页调用 BitBrowser `/browser/list`；
  - 已要求所有 Profile 具备 `userId`、`mainUserId`，且 `mainUserId` 唯一；
  - `BitProfile` 已是 allow-list，未携带 Cookie/密码；
  - `_safe_profile` 已提取 `id`、`userId`、`mainUserId`、名称、分组、状态、备注、代理摘要。
- `wt-media-agent/src/wt_media_agent/local_api/server.py`
  - `profile_scan_response()` 已提供 `POST /api/v1/bit-browser/profile-scans`；
  - 身份不可验证返回 `bitbrowser_identity_unverifiable`；
  - BitBrowser调用失败返回 `bitbrowser_response_error`。
- `wt-media-agent/tests/test_local_profile_scan.py`
  - 已覆盖 secret-free payload；
  - 已覆盖身份失败和 Local API 失败映射。

需修正/补齐：

- Agent 返回字段为 `status`，Cloud 当前使用 `bit_status`；需要在提交 Cloud 前规范映射，避免运行状态 Diff 丢失。
- 当前 `wt-media-agent/src/wt_media_agent/local_api/server.py` 有未提交改动，且会影响本 CHG 的 Local Agent 状态/身份入口；进入 Task 2 前必须确认是否保留并作为本 CHG 继承事实。

### Desktop / Web 入口

可复用：

- `wt-media-desktop/src-tauri/src/main.rs`
  - 已有 Rust 命令：`local_agent_status`、`local_agent_health`、`local_agent_start`、`local_agent_stop`、`local_agent_task_status`、`local_agent_bind`；
  - 已有 Rust 代理 Local Agent 状态的模式。
- `wt-media-cloud/web/src/apps/desktop/features/local-agent/service.js`
  - 已通过 Tauri `invoke` 调用 Local Agent 状态/启动/停止/绑定。
- `wt-media-cloud/web/src/modules/profiles/pages/ProfilesPage.vue`
  - 已有“触发扫描”按钮；
  - 已有扫描结果抽屉；
  - 已能按新增、变更、缺失展示 Diff。

需修正/补齐：

- `ProfilesPage.vue` 当前直接 `fetch("http://127.0.0.1:8765/api/v1/status")` 获取 `node_id`，违反 Desktop 规则。
- `ProfilesPage.vue` 当前直接 `fetch("http://127.0.0.1:8765/api/v1/bit-browser/profile-scans")` 触发扫描，违反 Desktop 规则。
- `wt-media-desktop/src-tauri/src/main.rs` 当前没有 `local_agent_profile_scan` 这类 Rust 命令，后续 Task 4 需要新增。
- 扫描抽屉底部当前展示“仅确认主账号”“确认同步窗口”，这两个都会引导用户进入 M2-A/B2 范围；M2-B1 应隐藏、禁用或明确标记为后续。
- 页面标题仍出现“浏览器窗口 (Profile)”，需要面向用户改成“浏览器窗口”，Profile 只可作为技术字段出现在详情中。
- Cloud Web 的浏览器窗口页面应只展示 Cloud 已保存的基本信息；扫描、Diff处理、读回、打开、关闭、创建、更新等依赖 BitBrowser/Local Agent 的能力只能在 Desktop 页面提供。

## 5. 文件映射

| 类别 | 文件 | 判断 |
|---|---|---|
| Cloud服务 | `wt-media-cloud/internal/modules/profilebinding/service.go` | 可复用，需补字段和Diff |
| Cloud路由 | `wt-media-cloud/internal/modules/profilebinding/routes.go` | 可复用，M2-B1只使用 submit/review |
| Cloud存储 | `wt-media-cloud/internal/modules/profilebinding/store_mysql.go` | 可复用，需确认候选表是否存代理/备注字段 |
| Cloud测试 | `wt-media-cloud/internal/modules/profilebinding/service_test.go` | 可复用，需补只读/代理/运行状态/账号影响测试 |
| Web API | `wt-media-cloud/web/src/shared/api/profileBindings.js` | 可复用，字段allow-list需与Cloud input对齐 |
| Web页面 | `wt-media-cloud/web/src/modules/profiles/pages/ProfilesPage.vue` | 需修：不能直连Agent，隐藏/禁用应用类动作 |
| Web测试 | `wt-media-cloud/web/src/profileBindings.test.js` | 可复用，需增加Desktop扫描服务/只读按钮测试 |
| Agent适配器 | `wt-media-agent/src/wt_media_agent/runtimes/bitbrowser.py` | 可复用，需统一 `status`→`bit_status` 映射策略 |
| Agent Local API | `wt-media-agent/src/wt_media_agent/local_api/server.py` | 可复用，有未提交改动需先确认 |
| Agent测试 | `wt-media-agent/tests/test_local_profile_scan.py` | 可复用，需补运行状态/代理字段断言 |
| Desktop Rust | `wt-media-desktop/src-tauri/src/main.rs` | 需新增本机扫描代理命令；当前有未提交改动需先确认 |
| Desktop规则 | `wt-media-desktop/AGENTS.md` | 明确要求Rust代理Local Agent，禁止Vue直连动态端口 |

## 6. 当前脏改动与冲突判断

当前存在以下未提交改动：

- `wt-media-workspace/delivery/LEDGER.md`
- `wt-media-workspace/delivery/MASTER_IMPLEMENTATION_PLAN.md`
- `wt-media-workspace/delivery/active/CHG-20260723-025/`
- `wt-media-workspace/docs/engineering/.DS_Store`
- `wt-media-agent/src/wt_media_agent/local_api/server.py`
- `wt-media-agent/src/wt_media_agent/local_api/state.py`
- `wt-media-agent/tests/test_app.py`
- `wt-media-desktop/src-tauri/src/main.rs`

判断：

- Workspace治理改动属于本 CHG 创建与Task 1证据，可继续。
- `.DS_Store` 与本 CHG 无关，不应提交。
- Agent/Desktop 脏改动触及后续 Task 4 会修改的文件，进入 Task 2/4 前必须先决定：
  - 作为上一任务遗留提交；
  - 纳入本 CHG 并在 start-gate 后继续完善；
  - 或由用户确认其来源后再继续。

## 7. Gap to CHG

| CHG要求 | 当前状态 | Gap |
|---|---|---|
| Desktop可信环境触发扫描 | 页面用端口判断Desktop，并直连 8765 | 需要改为 Desktop Rust/Tauri bridge |
| Cloud/Desktop页面边界 | Cloud/Web和Desktop复用页面里混有本机扫描入口 | 需要拆清：Cloud只看基本信息，Desktop展示扫描Diff |
| Agent同步读取BitBrowser窗口 | 已有Local Agent扫描接口 | 可复用，需确认字段映射 |
| Cloud生成只读Diff | 已有SubmitScan，只读提交有测试 | 需补代理、备注、运行状态、账号影响Diff |
| 页面展示Diff | 已有抽屉和新增/变更/缺失tab | 需去除应用动作，优化用户语言 |
| 扫描不修改正式镜像 | Service测试已有覆盖 | 需补MySQL/API级证据 |
| 敏感字段不泄漏 | Agent测试和前端safeProfile已有部分覆盖 | 需补Cloud input和页面响应检查 |

## 8. 推荐后续任务顺序

1. Task 2：先统一扫描快照字段和敏感字段边界，补 Cloud/Agent/Web 测试。
2. Task 3：补 Cloud 只读 Diff 字段和账号影响表达，确认提交扫描不应用正式镜像。
3. Task 4：新增 Desktop Rust 本机扫描命令，Desktop 页面通过 Tauri invoke 调用，不再直连 8765。
4. Task 5：调整 Cloud/Desktop 浏览器窗口页面边界；Cloud只看基本信息，Desktop只展示扫描Diff，不提供应用/确认同步入口。
5. Task 6：补齐 tests/evidence/manual acceptance。

## 9. 风险与阻断

### 阻断

- 进入实现前，需要先确认 `wt-media-agent` 和 `wt-media-desktop` 当前未提交改动的归属。它们覆盖本 CHG 会触及的 Local Agent 状态和 Rust桥文件。

### 风险

- Cloud 当前候选表可能未保存代理/备注字段，即使 Agent 读取到了，也可能在 Diff详情里丢失。
- 已绑定媒体账号影响需要查询 `media_accounts` 关系；当前 `ProfileDiff` 没有承载影响账号摘要。
- 单项扫描不应走异步task，但页面已有其他Profile操作仍显示“已创建任务”，后续 B2 要单独处理，不能在本 CHG 偷做。

## 10. 提交边界建议

如果后续继续实施，建议独立提交：

1. Workspace：Task 1 evidence 与 checkpoint；
2. Cloud：扫描字段、Diff只读逻辑与测试；
3. Agent/Desktop/Web：Desktop桥接扫描路径与页面只读展示；
4. Workspace：测试/evidence/checkpoint收口。

Task 1 本身只产生治理证据，不修改 runtime 代码。
