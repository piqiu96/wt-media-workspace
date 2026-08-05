# CHG-20260725-031：M2-B 浏览器窗口收口

> 日期：2026-07-25（创建时标题"M2-B7 批量账号检查与 M2-B 综合收口"；2026-08-05 拆分收窄）
> 状态：DONE（2026-08-05 窗口收口完成）
> 所属 Milestone：M2-B 浏览器窗口与媒体账号真实闭环
> 关联闭环：`delivery/milestones/M2-account-runtime.md#M2-B-浏览器窗口与媒体账号真实闭环`
> 当前仓库：`wt-media-workspace`
> 预计影响仓库：`wt-media-cloud`、`wt-media-agent`、`wt-media-desktop`

## 0. 拆分说明（2026-08-05）

原 CHG-031 范围同时覆盖「浏览器窗口收口」与「社媒账号收口」两条垂直切片。经确认拆分：

- **本 CHG 收窄为「M2-B 浏览器窗口收口」**：窗口扫描、Diff 接受/恢复、真实创建、打开/关闭/批量开关、停用、Agent 状态页、边界一致性。窗口环境是后续账号/发布/互动的必须依赖，先完成。
- **社媒账号收口（含批量账号检查真实回填与账号功能缺口）拆至后续新 CHG**（M2-B 社媒账号收口，待窗口验收完成后创建）。
- 原 Task 1–4（批量账号检查的 Start Gate、入口、逐项执行回填、结果重试）已在本 CHG 内完成，其证据 `evidence/batch-account-check.md`、`evidence/batch-retry.md`、`evidence/start-gate.md`、`evidence/tests.md`、`evidence/real-account-readback-acceptance.md` 作为账号收口 CHG 的**继承证据**。

## 1. 用户可见目标

普通运营通过 Desktop 管理自己的 BitBrowser 窗口环境：扫描本机窗口、处理 Diff（接受本地变化 / 恢复 Cloud 配置）、真实创建/打开/关闭/批量开关窗口、停用窗口，并保持页面、Cloud 镜像、Agent 读回与 BitBrowser 实际状态一致。

本 CHG 交付"必须依赖的窗口环境"，是 M2-B 进入社媒账号收口与后续里程碑的前置。不涉及媒体账号上号、代理写入、Cookie、发布与互动。

## 2. 当前背景

已完成/继承：

- M2-A 已人工验收通过；
- B1/B2/B5 浏览器窗口扫描、Diff、接受/恢复、真实创建、打开/关闭、停用（business_status）已完成；
- 8/3–8/5 窗口产品优化三轮、Diff 闭环修复批、布局修复、自增主键迁移均已完成并有证据；
- 打包 Desktop 登录链路（base URL/CORS/X-Session-Token/登录冒烟门）可用。

未完成的窗口出口事实：

- A2 恢复 Cloud 配置（Diff 反向：恢复 Cloud 配置→写回 BitBrowser→读回验证）已实现但未真实环境验收；
- A3 新建窗口、A4 批量开/关的打包 Desktop GUI 复验未执行；
- Agent 状态页显示问题（`evidence/login-blocks.md` 8/4 待办）工程已修，用户未确认；
- 窗口收口矩阵（`evidence/window-closure.md`）待用户 GUI 确认项回填。

## 3. 本 CHG 范围

### 包含

- 窗口扫描与 Diff：自动/手工扫描只产生 Diff；接受本地变化→Cloud 镜像；恢复 Cloud 配置→写回 BitBrowser→读回验证；
- 窗口真实操作：创建、打开、关闭、批量打开/关闭、停用/启用、编辑 Cloud 备注；
- 窗口业务状态与退役：不真实删除 BitBrowser Profile；停用仅影响账号匹配/执行资格（不可参与账号匹配、不可打开/关闭）；停用+本机已删→同步删除 Cloud 镜像；
- 窗口边界与一致性：Cloud Web 只查看 Cloud 基本信息，Desktop 才处理依赖本机 BitBrowser 的扫描/Diff/执行；页面、Cloud 镜像、Agent 读回、BitBrowser 实际状态一致；
- 管理员分配未授权 Profile；高级运营只查看同组授权范围；
- Agent 状态页环境状态展示（打包 Desktop 登录后正常）。

### 不包含（拆分/后续）

- 媒体账号台账、绑定、单项/批量检查与真实身份回填 → 社媒账号收口 CHG；
- 代理写入/读回、窗口代理变化正式闭环 → M2-C；
- Cookie、CK、接码、人工验证码 → M2-D；
- 窗口编辑写回（Agent update_profile 写回名称/分组/代理）、标签展示/搜索、历史同步记录独立查询 → 后续 CHG。

## 4. 关键规则

- 扫描只产生 Diff，不落库；关闭弹窗/抽屉 ≠ 接受/取消/恢复，未处理 Diff 保持待处理（Milestone L209）；
- 接受本地变化→Cloud 镜像；恢复 Cloud 配置→写回 BitBrowser 并读回验证；
- 不真实删除 BitBrowser Profile，只管理 Cloud 镜像与业务状态；
- Cloud Web 不触发 Local Agent 或 BitBrowser；Desktop Vue 必须经 Tauri/Rust 调 Local Agent；
- 同一 Profile 同时只能有一个本地敏感操作。

## 5. 执行任务

### Task 1：窗口扫描与 Diff 闭环

- 自动/手工扫描只产生 Diff（字段级变更展示、操作态不入 diff、缺失窗口处理、备注接受生效）；
- 接受本地变化→Cloud 镜像，读回一致；
- 恢复 Cloud 配置→写回 BitBrowser→读回验证（A2，待真实环境验收）。

> 已完成：扫描/Diff/接受方向，见 `evidence/browser-window-product-optimization.md`「Diff 闭环修复批」。

### Task 2：窗口真实操作

- 真实创建（A3）、打开/关闭、批量打开/关闭（A4）、停用/启用（A5）、编辑 Cloud 备注。

> 已完成实现 + API/自动验证；A3/A4 待打包 Desktop GUI 复验，A5 已 PASS。

### Task 3：窗口收口判定

- 汇总窗口收口矩阵（`evidence/window-closure.md`）；
- 对照 M2-B 窗口完成标准输出 PASS/DEFER；
- 用户 GUI 验收确认后回填 PASS，判定窗口收口完成，为社媒账号/发布/互动提供依赖环境。

## 6. 验收标准

- **A5 停用**：启用/停用切换、停用窗口排除账号绑定候选、停用+本机已删→同步删除 Cloud 镜像 → PASS（API 实测）；
- **A2 恢复 Cloud 配置**：Diff 选择恢复→写回 BitBrowser→重扫读回一致 → 待用户 GUI 确认；
- **A3 新建窗口**：打包 Desktop 新建窗口→列表出现（ID/seq/名称/分组）→ 待用户 GUI 确认；
- **A4 批量开/关**：多选窗口→批量打开/关闭→运行状态列随操作切换 → 待用户 GUI 确认；
- **Agent 状态页**：打包 Desktop 登录后环境状态正常 → 待用户 GUI 确认；
- **边界一致性**：Cloud Web 不展示本机操作入口，Desktop 经 Tauri 调 Agent → PASS；
- **页面、Cloud 镜像、Agent 读回、BitBrowser 实际状态一致** → 窗口侧 PASS。

## 7. Evidence 要求

`evidence/` 已提供：

- `browser-window-product-optimization.md`：窗口产品优化三轮 + Diff 闭环修复批 + 布局修复；
- `manual-acceptance-*.md`：真实创建/打开/关闭/登录人工验收；
- `login-blocks.md`：打包登录链路 + Agent 状态页根因修复；
- `start-gate.md`、`tests.md`；
- `window-closure.md`（本次新增）：窗口收口矩阵。

账号侧证据（`batch-account-check.md`、`batch-retry.md`、`real-account-readback-acceptance.md`）移交社媒账号收口 CHG 作为继承证据。

## 8. Checkpoint

- Completed：
  - B7 active CHG 已创建；
  - 窗口实现与自动/API 验证全部完成：Diff 闭环（字段级展示、操作态不入 diff、缺失窗口清理、备注接受生效、友好提示、分页、布局）用户已 GUI 确认；真实 BitBrowser 创建/读回/开/关、停用 PASS；自增主键迁移 PASS；打包 Desktop 登录链路可用。
  - 2026-08-05 拆分：本 CHG 收窄为浏览器窗口收口；社媒账号收口拆至后续新 CHG（待窗口验收完成后创建）；
  - 2026-08-05 新建 `evidence/window-closure.md` 窗口收口矩阵；
  - 2026-08-05 GUI 验收：A3 新建窗口 PASS、A4 批量开/关 PASS；「取消变更」按钮已移除（与关闭抽屉行为重复，属误导性 UX），后端 `/reject` 空操作路由保留待清理；
  - 2026-08-05 A2 恢复 Cloud 配置修复并**验证通过**：缺 browserFingerPrint、缺 proxyMethod 两个 502 均修复（Agent `update_profile` 从 `/browser/detail` 读回当前指纹与代理方式原样传回，指纹/代理方式不出本地运行时），66 tests PASS，用户 GUI 重验写回无问题，见 `evidence/a2-restore-fix.md`；
  - Agent 状态页可用但重启需重绑，记优化项；
  - **2026-08-05 窗口收口判定 DONE**：A3 新建窗口、A4 批量开/关、A2 恢复写回、A5 停用、边界一致性全部 PASS。
- Current：2026-08-05 **窗口收口完成**，CHG-031 判定 DONE，交付"必须依赖的窗口环境"。
- Next：CHG-031 关闭归档；社媒账号收口 CHG（含批量检查真实回填 + 账号功能缺口）经 planning-wt-media-delivery 规划后执行；M2-C 代理管理完善后处理"有代理窗口恢复字段对齐"延后项。
- Blockers：无。延后项：有代理窗口的恢复字段对齐 → M2-C；Agent 状态页重启重绑定 → M2-E 优化。
- Recent verification：`wt-media-workspace/scripts/m2b-local-acceptance.sh all` PASS，已清理旧产物、重建并启动 DMG；Cloud `/api/v1/health` PASS；Cloud CORS preflight from `http://tauri.localhost` PASS；Cloud `POST /api/v1/auth/login` with `operator01` returned unified JSON and `Set-Cookie` PASS；packaged Desktop process verified from `/Volumes/WT Media/WT Media.app/Contents/MacOS/wt-media-desktop-shell`；Agent `/healthz` 和 `/api/v1/status` PASS；BitBrowser `54345` 可用且主账号匹配；真实创建并读回 `m2b-acceptance-20260803-2257` / `9e6c697c69fc467fa5e0829ca4fbebee` PASS；Agent open/close retest PASS；Desktop `.generated/frontend/index.html` present PASS；Agent tests PASS，16 tests；Web `npm test` PASS，10 files / 36 tests；Cloud `go test ./internal/app` PASS；`cargo tauri build --bundles dmg --no-sign` PASS；`wt-media-workspace/scripts/m2b-local-acceptance.sh verify` PASS。

## 9. Pending Questions

None.
