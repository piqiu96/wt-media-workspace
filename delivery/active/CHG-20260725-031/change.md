# CHG-20260725-031：M2-B7 批量账号检查与 M2-B 综合收口

> 日期：2026-07-25  
> 状态：ACTIVE  
> 所属 Milestone：M2-B 浏览器窗口与媒体账号真实闭环  
> 关联闭环：`delivery/milestones/M2-account-runtime.md#M2-B-浏览器窗口与媒体账号真实闭环`  
> 当前仓库：`wt-media-workspace`  
> 预计影响仓库：`wt-media-cloud`、`wt-media-agent`、`wt-media-desktop`

## 1. 用户可见目标

普通运营可以在 Desktop 对多个已绑定窗口的媒体账号发起批量检查，系统按账号逐项真实读取平台身份，并把每个账号的结果回填到 Cloud：

```text
选择多个媒体账号
→ 点击批量检查/同步
→ 系统预检每个账号、窗口、本机环境和互斥状态
→ Desktop 串行调用 Local Agent 检查
→ 每个账号独立回填平台UID、昵称、头像、登录状态和最近检查时间
→ 页面展示批量统计、部分成功、失败原因和失败项重试入口
```

本 CHG 是 M2-B 进入 M2-C 前的最后收口判断，不处理代理写入、Cookie 上号、接码、人工验证码或通用任务中心。

## 2. 当前背景

已完成/继承：

- M2-A 已人工验收通过；
- B1/B2/B5 已完成浏览器窗口扫描、Diff、接受/恢复、真实创建、打开/关闭和停用；
- B3 已完成媒体账号台账与 Profile 绑定；
- B4-1 已完成单个账号检查基础链路；
- B6 已完成媒体账号台账、账号行打开/关闭窗口、单项“检查/同步账号信息”和人工登录后回填入口。

未完成的 M2-B 出口事实：

- 批量账号检查尚未证明；
- 批量部分成功、失败项重试、逐项错误反馈尚未证明；
- M2-B 综合收口矩阵尚未整理。

## 3. 本 CHG 范围

### 包含

- 批量账号检查 Start Gate：
  - 审计是否已有可复用 batch/item 模型；
  - 判断批量账号检查使用专用业务批次，还是首版 Desktop 页面串行逐项同步执行并逐项回填；
  - 明确不使用 Cloud 通用 task 冒充检查完成。
- 批量检查入口：
  - 仅 Desktop 展示；
  - Cloud Web 只查看历史结果；
  - 只允许选择本人授权、业务启用、绑定 active 窗口的账号。
- 逐项执行与回填：
  - 每个账号复用单项检查链路；
  - 同一 Profile 或账号同时只能有一个本地敏感操作；
  - 每项成功/失败独立记录，不因批次失败回滚成功项。
- 批量结果体验：
  - 展示总数、成功、失败、跳过、结果待确认；
  - 展示每项失败原因；
  - 支持失败项精确重试。
- M2-B 综合收口：
  - 汇总 B1-B7 Evidence；
  - 对照 Milestone M2-B 完成标准标记 PASS/DEFER；
  - 明确是否可以进入 M2-C。

### 不包含

- 不写入、更换或解绑代理；
- 不导入、写入、读取或导出 Cookie；
- 不做 CK 上号、接码链接、人工验证码或人工接管；
- 不建设通用任务中心；
- 不点击平台最终发布或互动动作；
- 不清理原窗口 Cookie。

## 4. 关键规则

- 批量检查不能以“批量请求已创建”作为成功；
- 每个账号必须有真实读回结果或明确失败/待确认；
- 结果不确定时不得自动重复检查；
- Cloud Web 不触发 Local Agent 或 BitBrowser；
- Desktop Vue 仍必须通过 Tauri/Rust 调 Local Agent；
- 批量过程不能并发操作同一 Profile 或同一账号。

## 5. 执行任务

### Task 1：Start Gate 与批量模型审计

- 核对 active CHG、Ledger、CURRENT_CONTEXT 和 M2-B milestone；
- 审计现有账号检查、Profile Guard、Desktop service、Agent API 和页面状态；
- 判断批量检查首版模型和最小安全实现边界；
- 记录文件映射、测试计划、风险和阻塞项。

### Task 2：批量检查入口与预检

- Desktop 账号页提供批量检查入口；
- 过滤不可执行账号并展示跳过原因；
- Cloud Web 不展示批量本机操作入口。

### Task 3：逐项串行执行与回填

- 逐项调用单个检查/同步链路；
- 逐项回填 Cloud；
- 捕获失败、跳过和结果待确认。

### Task 4：批量结果、失败项重试和 Evidence

- 展示批量统计和逐项结果；
- 支持失败项精确重试；
- 自动测试覆盖页面边界、状态、失败和重试。

### Task 5：M2-B 综合收口判断

- 汇总 B1-B7 Evidence；
- 对照 M2-B 完成标准输出 PASS/DEFER；
- 如果全部通过，关闭 B7 并进入 M2-C；否则创建下一条最小 CHG。

## 6. 验收标准

- Cloud Web 不展示批量检查入口；
- Desktop 可选择多个账号发起批量检查；
- 不可执行账号被跳过并显示原因；
- 可执行账号逐项串行真实检查并回填；
- 部分成功不会回滚；
- 每项失败原因可见；
- 失败项可精确重试；
- M2-B 综合收口矩阵完成。

## 7. Evidence 要求

完成后在 `evidence/` 中至少提供：

- `start-gate.md`：当前事实、批量模型判断、文件映射；
- `batch-account-check.md`：批量检查逐项执行验证；
- `batch-retry.md`：失败项重试和部分成功验证；
- `m2-b-closure.md`：M2-B 综合收口矩阵；
- `tests.md`：自动测试和构建记录。

## 8. Checkpoint

- Completed：
  - B7 active CHG 已创建；
  - B6 收口判断确认批量账号检查需要独立 CHG；
  - Task 1 Start Gate 与批量模型审计已完成，见 `evidence/start-gate.md`；
  - Task 2 批量检查入口与预检已完成，见 `evidence/batch-account-check.md`；
  - Task 3 逐项串行执行与回填已完成，见 `evidence/batch-account-check.md`；
  - Task 4 批量结果、失败项重试和 Evidence 已完成，见 `evidence/batch-retry.md` 和 `evidence/tests.md`。
  - 人工验收暴露的分组读取、创建提示、比特序号和打开/关闭问题已修复，见 `evidence/manual-acceptance-fixes.md`。
- Current：2026-08-04 登录与环境阻塞复现：环境在跑但 Cloud(启动 08-03 23:45)/Agent(启动 08-03 23:01) 均为**陈旧构建**（早于各自最新提交），系统存在 12 个历史数据库 → 环境非确定性，与"每次登录报错不同"一致；API 层实测 admin/admin123 + `replace_existing:true` 登录成功、CORS for `http://tauri.localhost` 正常、`operator01` 密码未知（错误密码映射 11001「请先登录或凭证已过期」）；打包 App 登录"不进去"的直接原因待用户提供 operator01 密码或经 admin 重置密码后，在最新环境 + 最新 DMG 上端到端复验，见 `evidence/login-blocks.md`。
- Next：① 获取/重置 operator01 密码并验证 API 登录；② 固化 `environment-bring-up` skill（强制停旧进程、最新源码重建、固定唯一 DSN、登录冒烟门），重启 Cloud/Agent 到最新；③ 在打包 App 上完成登录与 M2-B 页面人工验收；④ 治理不一致修复。
- Blockers：operator01 密码未知（需用户提供或授权 admin 重置）。
- Recent verification：`wt-media-workspace/scripts/m2b-local-acceptance.sh all` PASS，已清理旧产物、重建并启动 DMG；Cloud `/api/v1/health` PASS；Cloud CORS preflight from `http://tauri.localhost` PASS；Cloud `POST /api/v1/auth/login` with `operator01` returned unified JSON and `Set-Cookie` PASS；packaged Desktop process verified from `/Volumes/WT Media/WT Media.app/Contents/MacOS/wt-media-desktop-shell`；Agent `/healthz` 和 `/api/v1/status` PASS；BitBrowser `54345` 可用且主账号匹配；真实创建并读回 `m2b-acceptance-20260803-2257` / `9e6c697c69fc467fa5e0829ca4fbebee` PASS；Agent open/close retest PASS；Desktop `.generated/frontend/index.html` present PASS；Agent tests PASS，16 tests；Web `npm test` PASS，10 files / 36 tests；Cloud `go test ./internal/app` PASS；`cargo tauri build --bundles dmg --no-sign` PASS；`wt-media-workspace/scripts/m2b-local-acceptance.sh verify` PASS。

## 9. Pending Questions

None.
