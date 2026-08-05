# M2-B 综合收口矩阵

日期：2026-07-25（首版）→ **2026-08-05（更新，纳入 8/3–8/5 后期变更）**
CHG：CHG-20260725-031（M2-B7 批量账号检查与 M2-B 综合收口）

## Evidence 链

- B1：`delivery/completed/CHG-20260723-025`，浏览器窗口扫描与 Diff 只读闭环；
- B2：`delivery/completed/CHG-20260723-026`，窗口同步应用、恢复与授权闭环；
- B3：`delivery/completed/CHG-20260724-027`，媒体账号台账与 Profile 真实绑定闭环；
- B4-1：`delivery/completed/CHG-20260724-028`，单个媒体账号检查与身份回填闭环；
- B5：`delivery/completed/CHG-20260724-029`，浏览器窗口真实操作与台账收口；
- B6：`delivery/completed/CHG-20260725-030`，媒体账号操作与检查收口；
- B7：`delivery/active/CHG-20260725-031`，批量账号检查与 M2-B 综合收口。

## 完成标准对照（当前状态）

| M2-B 完成标准 | 状态 | Evidence |
|---|---|---|
| 单个和批量窗口真实创建、逐项读回、部分成功和失败项重试成立 | **PASS**（API/自动验证）；GUI 复验见 B 项 | B5、B7 `manual-acceptance-profile-create-tested.md`、`manual-acceptance-20260803-runtime.md`（真实创建 `9e6c697c…` 读回 seq/group/proxy PASS）、`batch-account-check.md`、`batch-retry.md` |
| 自动与手工扫描均只产生 Diff，用户可以接受或恢复且读回一致 | **部分 PASS**：接受方向（本地变化→Cloud）已确认；**恢复方向（恢复 Cloud 配置/取消变更）DEFER** | `browser-window-product-optimization.md`「Diff 闭环修复批」（用户确认：字段级展示、操作态不入 diff、缺失窗口接受后清理、备注接受生效）；A2 恢复 Cloud 配置尚在验收清单未确认 |
| 浏览器窗口不做真实删除 BitBrowser Profile，只归档 Cloud 镜像 | **PASS（语义已修订）** | Milestone `M2-account-runtime.md` L229（2026-08-04 修订）：窗口退役通过业务状态（启用/停用）管理，存在性以扫描为准；停用+本机已删→同步删除 Cloud 记录；`browser-window-product-optimization.md` 第一轮 |
| 管理员可分配未授权 Profile；高级运营只查看同组授权范围的 Cloud 状态 | PASS | B2 `authorization-and-binding-summary.md` |
| 账号可创建、编辑、绑定、解绑、换绑、加减标签和筛选 | PASS | B3 Evidence、B6 `account-ledger.md`、`account-profile-binding.md` |
| 账号台账页面支持列表、详情、搜索、平台/游戏/标签/业务状态/登录状态筛选、分页和备注维护 | PASS | B6 `account-ledger.md` |
| 单个/批量账号检查真实回填平台身份、头像、登录状态和最近检查时间 | **控制流 PASS；真实回填 DEFER** | B4-1、B6 `account-check-sync.md`、B7 `batch-account-check.md`、`batch-retry.md`（控制流与逐项状态已测）；真实已登录平台账号缺失 → 平台 UID/昵称/头像读回未端到端证明 |
| 页面、Cloud 镜像、Agent 读回和 BitBrowser 实际状态一致 | **部分 PASS**：窗口创建/读回/开/关已读回一致；平台身份一致性 DEFER（同上） | `manual-acceptance-20260803-runtime.md`（profile-create/read-back/open/close 真实读回一致）；真实平台登录态回填待验证 |
| Cloud Web 与 Desktop 页面边界清晰 | PASS | B7 `batch-account-check.md`（Cloud Web 不展示批量入口）、`login-blocks.md`（Desktop 经 Tauri 调 Agent，cloudBaseUrl 指向 127.0.0.1:18080） |

## 8/3–8/5 后期变更验收记录（本批新增）

| 项 | 状态 | Evidence |
|---|---|---|
| 打包 Desktop 登录链路（打包 base URL、CORS tauri.localhost、X-Session-Token、登录冒烟门） | **PASS**（API/打包复验） | `login-blocks.md`、`manual-acceptance-20260803-runtime.md` |
| Diff 闭环修复批（字段级展示、操作态不入 diff、缺失清理、备注接受、友好提示、分页、布局） | **PASS**（用户 GUI 确认） | `browser-window-product-optimization.md`「Diff 闭环修复批」 |
| 窗口业务状态停用（business_status，20260804_016 迁移） | **PASS**（API 实测） | `browser-window-product-optimization.md` 第一轮 |
| browser_profiles 自增主键迁移（20260804_017，含 4 FK 联动、备份恢复） | **PASS**（迁移+API 实测） | `browser-window-product-optimization.md` 第二轮 |
| 批量打开/关闭（表格多选） | **实现完成 + 测试 PASS；待用户 GUI 复验** | `browser-window-product-optimization.md` 第二轮「待用户 GUI 复验」 |
| 新建窗口 GUI 流程 | **API 层 PASS；待用户 GUI 复验** | `manual-acceptance-profile-create-tested.md`、`manual-acceptance-20260803-runtime.md` |

## DEFER 项（未进入 M2-B 完成判定，归口后续）

- **真实平台身份回填端到端**：单项/批量检查真实回填 UID/昵称/头像/登录状态，缺真实已登录 B站/百家号账号 → DEFER，需用户提供测试账号后在 BitBrowser 内登录验证。
- **A2 恢复 Cloud 配置（Diff 反向）**：恢复系统配置→写回 BitBrowser→读回一致未确认 → DEFER。
- **GUI 复验 A3/A4**：新建窗口、批量开/关 的打包 Desktop 人工点击复验 → 待用户执行。
- **Agent 状态页显示问题**（`login-blocks.md` 8/4 待办）：打包 Desktop 登录后 Agent 状态页异常，未确认修复 → DEFER。
- 代理写入/读回、窗口代理变化正式闭环属于 M2-C。
- Cookie、CK、接码、人工验证码和 Cookie 导出属于 M2-D。
- 持久化 batch/item、重启恢复和本地执行抽屉属于后续 M2-D/M2-E；B7 首版批量检查为 Desktop 页面串行逐项执行，不创建 Cloud 通用 task。
- 状态枚举数据库迁移暂不做：当前代码保留历史内部枚举，页面提供用户可读映射；如需改成 Milestone 文案枚举，应单独做兼容迁移 CHG。
- 窗口编辑（Agent update_profile 写回名称/分组/代理）、标签展示/搜索、历史同步记录独立查询 → 后续 CHG。

## 收口结论

M2-B 的**工程实现与自动/API 验证已全部完成**，真实 BitBrowser 窗口创建、读回、打开/关闭、Diff 接受、停用、批量检查控制流均已 PASS，打包 Desktop 登录链路可用，`m2b-local-acceptance.sh all` + `verify` 保持 PASS。

**尚不能判定 M2-B 全部 PASS，不能关闭 CHG-031**，因为以下验收仍依赖用户真实环境操作：

```text
1. 提供真实 B站或百家号账号并在 BitBrowser 正确平台窗口登录
   → 跑单项检查 + 批量检查，确认平台 UID/昵称/头像/登录状态真实回填 Cloud（成功路径）
   → 确认失败/跳过项原因展示与失败项精确重试（失败路径）
2. 打包 Desktop GUI 复验：新建窗口、批量开/关、Diff 恢复 Cloud 配置
3. 确认登录后 Agent 状态页显示正常
4. 修正现有 bilibili 账号↔百家号窗口的平台不匹配数据
```

上述完成后，将本矩阵 DEFER 项逐项更新为 PASS，再关闭 CHG-031。若真实平台身份读取或 BitBrowser 读回发现不一致，应创建 M2-B 修复 CHG，否则进入 M2-C。
