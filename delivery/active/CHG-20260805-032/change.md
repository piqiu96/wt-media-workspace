# CHG-20260805-032：M2-B 社媒账号收口

> 日期：2026-08-05
> 状态：ACTIVE
> 所属 Milestone：M2-B 浏览器窗口与媒体账号真实闭环
> 关联闭环：`delivery/milestones/M2-account-runtime.md#M2-B-浏览器窗口与媒体账号真实闭环`
> 当前仓库：`wt-media-workspace`
> 预计影响仓库：`wt-media-cloud`、`wt-media-agent`、`wt-media-desktop`

## 0. 继承与关联

- 前置已完成：M2-A、M2-B 浏览器窗口收口（CHG-20260725-031 DONE，见 `delivery/completed/CHG-20260725-031/`）
- 本 CHG 是 M2-B 的**社媒账号切片**，与 M2-C 代理收口（CHG-20260805-033，PLANNED）串行推进
- 共享前置：Profile 级互斥（E1/M2-E 切片）在本 CHG Task 1 实现，CHG-C 继承复用

## 1. 用户可见目标

普通运营管理自己的媒体账号台账，对已绑定窗口的账号执行单项/批量账号检查，**真实回填平台身份**（UID、昵称、头像、登录状态、最近检查时间），并在检查结果中看到逐项明细。

## 2. 当前背景（继承已完成）

- 账号 CRUD、标签增删/筛选、绑定/解绑/换绑 Profile、分页/搜索/筛选：已实现
- 单项账号检查（Bilibili 控制流）：已实现（StartLocalAccountCheck → Agent account_check → ApplyLocalAccountCheckResult 回填）
- 批量检查控制流 + 失败重试 + 结果面板：已实现（B7）
- 真实回填字段链路（platform_account_id/name/avatar_url/login_status/last_checked_at）：代码就绪
- 敏感任务创建（Profile 敏感操作锁雏形）：已有 `sensitive_browser_tasks`/`sensitive_profile_permits`

## 3. 本 CHG 范围

### 包含

- **共享互斥（E1/M2-E 切片）**：同一 Profile 同时仅一个本地敏感操作（Cloud acquire/release + Agent 守卫），账号检查接入；供 CHG-C 继承
- 账号台账收尾：`business_status` 补 draft=待识别/abnormal=异常（DB CHECK + 服务校验 + 页面统计筛选）；账号详情 Cookie 操作入口（**查看/导出当前 Cookie + 从 Profile 读真实 Cookie**，读回走 Agent 同步）
- **账号—游戏多关系切换**：新建 `media_account_games`、一次性迁移旧单值关联并删除 `media_accounts.game_id`；Cloud API 与账号页面创建/编辑/展示/筛选均使用 `game_ids`；已启用游戏在媒体账号域默认公开可用（Decision 0011）
- 平台身份真实识别：抖音/百家号 Cookie→UID；Bilibili/抖音/百家号昵称与头像真实回填
- 账号检查 8 项明细：保留已完成骨架与展示；7/8（验证码/账号限制）的真实样本校准移至 CHG-20260903-034
- **账号组（可保存筛选，PRD 3.3.6）**：account_groups 模型 + CRUD + 保存/应用筛选；发布/互动（M6/M8）依赖它筛目标账号
- 端到端验收：真实平台账号（Bilibili 单项 → 百家号 → 批量真实回填）及多游戏关系迁移/页面验收

### 不包含（延后/后续）

- 检查项 3/4（代理正常/到期）→ 延后 M2-C（CHG-C 完成后接入）
- CK **写入**/上号（CK 导入/接码/人工验证码）→ M2-D；本 CHG 只做查看/导出/读回
- 代理管理、配额、分配 → M2-C（CHG-C）
- 标签归属用户（前端传 user_id）→ 随标签交互补正（PRD 3.3.6）

## 4. 关键规则

- 检查回填必须真实读回，不能"任务创建=成功"；`result_uncertain` 不自动重查
- 同一 Profile 同时只能一个本地敏感操作（互斥）
- Cookie 为敏感数据，回填/导出遵守 `secret_policy`（不进日志/错误/Evidence）
- 页面、Cloud 镜像、Agent 读回、平台实际状态一致

## 5. 执行任务

### Task 1：共享互斥（E1/M2-E 切片）
- 复用 `sensitive_browser_tasks`/`sensitive_profile_permits`，扩展为通用 Profile 级锁（Cloud acquire/release + Agent 单操作守卫）
- 账号检查接入互斥
- 交付互斥契约，CHG-C 继承复用

### Task 2：账号台账收尾
- B3-2 `business_status` 补 draft=待识别/abnormal=异常（DB CHECK + 服务校验 + 页面统计/筛选）
- B3-1 Cookie 操作入口：账号详情「查看/导出当前 Cookie」+「从 Profile 读真实 Cookie」（Agent 同步读回）；写入/上号归 M2-D

### Task 3：平台身份真实识别
- B4-2 抖音/百家号 Cookie→UID（`_identify_platform_account` 补齐，需各平台 Cookie 样本）
- B4-3 昵称/头像真实回填（Bilibili/抖音/百家号）

### Task 4：账号检查 8 项完整化
- 已实现 1/2/5/6（身份/Profile存在/登录/匹配）
- 7/8 验证码/账号限制（跨平台，需真实受限账号样本）——移至 CHG-20260903-034
- 3/4 代理项 → 延后 M2-C（接代理收口后回接）
- B4-6 检查结果 8 项明细 UI（逐项展示，未实现/延后项标注状态）

### Task 5：账号组（可保存筛选，PRD 3.3.6）
- `account_groups` 模型 + CRUD + 保存/应用筛选条件；发布/互动（M6/M8）依赖

### Task 6：端到端验收与收口
- 真实平台账号：Bilibili 单项 → 抖音/百家号 → 批量真实回填；受限账号验证 7/8
- 更新 M2-B 账号收口矩阵，判定收口 DONE 或创建修复 CHG

### Task 7：社媒账号页 v3 页面收口
- 前端 AccountsPage.vue：加 **Cookie 列**（任意行打开弹窗 + Desktop 从 Profile 读真实 Cookie）；账号信息/窗口弹窗去多余按钮（只留 X/外部关闭 + 打开/关闭窗口）；查看抽屉转 **view-only**（去底部按钮与可编辑表单，保留 8 项检查明细）；编辑弹窗加「账号名称」+「绑定窗口」（bind/unbindProfile）；新增账号弹窗加「账号名称」；标签控件改 **多选 allow-create**（候选=已用标签，回车新建）；删除标签管理（openTagManage/deleteTagFromAll/tagManageVisible）；筛选栏加「窗口绑定」文本模糊匹配
- **信息架构与布局重排（用户最新规格确认）**：统计区一行六项分两组（业务状态：总/启用/停用｜账号健康：正常/异常/待检查，点卡片应用筛选）；主操作区固定 `[新增账号][批量检查][刷新]`（唯一批量入口，批量检查=列表多选勾选账号，无勾选提示）；筛选区两行重排（第一行 搜索+查询+重置，第二行 六个筛选）；**移除批量工具栏**（批量启用/批量停用/取消选择/已选N项 全部删除，行级启用/停用保留）；操作列「检查同步」→「检查」；列宽保证 业务状态/账号状态/最近检查 独立可见；**错误反馈重构**（顶部横幅仅页面级加载失败，单账号检查失败→行状态置「检查失败」+ 打开详情展示失败原因，批量→批量结果面板，其余操作错误就近 MessagePlugin 提示）；**修复分页总条数**（前端 pagination total 绑定，后端全量返回）
- 前端 mediaAccounts.js：list 透传 profile→profile_search；create/update 支持 name
- 后端 mediaaccount：Create/Update 支持 name（Update 已支持 GameID）；ApplyLocalAccountCheckResult 的 name **空才回填**；AccountFilter 加 ProfileSearch（store List 对 browser_profiles.name/seq/bit_profile_id/id 模糊匹配）；routes 透传 name/profile_search
- 测试：service_test +3（Create/Update name、name 空才回填）、store_mysql_test +1（ProfileSearch）、routes_test +1（create/update name）；web mediaAccounts.test 更新边界断言（检查→检查按钮、主操作批量检查、无勾选提示）+ 补 name/profile_search 用例

### Task 8：账号—游戏多关系切换
- 创建 `media_account_games` 关系表，迁移旧 `media_accounts.game_id`，保留账号、标签、Cookie、检查记录与 Profile 绑定并删除旧列/索引
- Cloud 服务/Store/路由以 `game_ids` 为正式字段；旧 `game_id` 仅兼容；创建/更新按完整数组写入或删除关系；按任一游戏筛选不产生重复账号
- Cloud Web 新增、编辑、列表、详情和筛选支持多游戏；已启用游戏默认公开可用，不按 `users.game_ids` 限制本域

## 6. 验收标准

- 单项/批量检查对真实已登录平台账号真实回填 UID/昵称/头像/登录状态/最近检查时间
- 同一 Profile 并发两个本地操作 → 第二个被拒绝/排队
- Cookie 查看/导出入口可用且遵守敏感数据规则
- `business_status` 收敛为两态 `enabled`/`disabled`（迁移 021；健康度由派生「账号状态」承载，见 Decision 0010）
- 检查结果展示 8 项明细
- 多游戏创建、完整替换、清空、按任一游戏筛选和页面展示与 Cloud 关系表读回一致；迁移不删除账号其他关联事实
- 页面、Cloud 镜像、Agent 读回、平台实际状态一致

## 7. Evidence 要求

`evidence/` 提供：互斥契约、平台识别（Cookie→UID 映射）、昵称/头像回填、8 项明细 UI、端到端验收（真实账号）、测试与构建记录。

## 8. Checkpoint

- Completed：
  - CHG 已创建；Start Gate 完成（继承窗口收口 + B7 检查控制流）；
  - **Task 1 共享互斥——验证通过，机制已存在**：Profile 级互斥由 M2-A profileguard 完整实现并在账号检查路径生效（Cloud AcquirePermit 行锁 + OutcomeWaiting 互斥 + Tauri preflight→check→finish 闭环）。Task 1 为验证 + 固化契约，见 `evidence/task1-profile-mutex.md`。CHG-C 需将代理写回接入同一 permit 路径。
  - **Task 2 账号台账收尾——完成**：B3-2 business_status 补 draft/abnormal（语义 draft=待识别、abnormal=异常，迁移 018 + 服务状态流转 + 前端；**后经迁移 021 收敛为 enabled/disabled 两态**，见 Decision 0010）；B3-1 Cookie 操作（查看/导出 + 从 Profile 同步读回，走 Profile 级互斥，写入/上号归 M2-D）。见 `evidence/task2-ledger-cookie.md`。
  - **Task 3 前置发现 + 实施**：
    - 发现：本版 BitBrowser 无 `/browser/cookie` API；**`/browser/detail` 对已登录窗口返回 `cookie` JSON 字段**（正确读取途径，无需 CDP）
    - 资源：百家号 seq46 窗口已登录；B站 接码链接（4208560/217api）已记录，见 `evidence/task3-resources-and-cdp-finding.md`
    - **实施（Agent `bff592c`）**：`read_cookies` 改从 detail cookie 字段解析（修复 B3-1 与账号检查的 Cookie 读取）；`_identify_baijiahao` 服务端调 `image.baidu.com/user/logininfo` 读 UID/昵称/头像
    - **百家号端到端验证通过**：真实 seq46 窗口 → UID `6572476037`、昵称"你阿邱爷"、头像 portrait URL、login_status=normal；73 tests PASS
  - **Task 3 平台识别——完成**：
    - 百家号 ✅（logininfo API，UID 6572476037/你阿邱爷）
    - Bilibili ✅（DedeUserID UID + CDP 页面内 nav 昵称/头像：UID 3706971620379308/游戏魔王嘟嘟/头像/正常）
    - 抖音移除（用户确认不支持管理）
    - **Agent 新增 CDP 能力**（`92fe666`）：实时 Cookie 读取（`/browser/detail` 只含已保存 cookie）+ 页面内 fetch（绕开 B站 bili_ticket/指纹风控）；74 tests PASS
  - **Task 5 账号组——完成**：filters JSON + 应用复用 ListAccounts；主键 BIGINT 自增；CRUD/应用/前端下拉；测试全绿，见 `evidence/task5-account-groups.md`。
  - **Task 4 检查 8 项明细——完成（骨架）**：check_items 持久化 + 前端 8 项展示；7/8 判定为骨架（na，需真实受限样本对齐）。见 `evidence/task4-check-items.md`。
  - **Task 6 端到端验收——通过**：重建环境（内嵌全部代码），真实 B站 窗口 Agent 检查返回 check_items 5-8；Cloud 应用合并 1-4 并持久化 8 项；business_status draft→enabled。见 `evidence/task6-e2e-acceptance.md`。
  - **Task 7 社媒账号页 v3 页面收口——完成（代码 + 自动化验证）**：Cookie 列 + 任意行弹窗/从 Profile 读真实 Cookie；账号信息/窗口弹窗去多余按钮；查看抽屉转 view-only；编辑/新增加「账号名称」+ 编辑加「绑定窗口」；标签多选 allow-create；删标签管理；「窗口绑定」模糊筛选。**布局重排**：统计一行分两组、主操作 [新增账号][批量检查][刷新]、筛选两行、移除批量工具栏、操作列「检查」、错误反馈重构、修复分页总条数。Cloud mediaaccount go test 全绿（含新增 5 用例）、Web 38 tests、Cloud/Web 构建通过。GUI 人工验收**通过**（2026-08-14，含标签跨账号复用修复后点验）。
  - **Task 7 GUI 验收修复——标签跨账号复用丢失（根因在 DB 唯一键，非前端）**：GUI 验收发现「新建账号勾选其他记录已创建的标签 → 保存后标签未落库」。根因：迁移 `20260806_022` 在 `DROP COLUMN media_account_id` 时未先删含该列的复合唯一键，MySQL 自动把 `uq_media_account_tags_owner_account_name` 折叠为 `(user_id, tag_name)`（丢失 `media_account_id`），使同一用户跨账号复用同一标签名被 `store.AddTags` 的 `INSERT IGNORE` 静默丢弃（审计日志有 `tags.add`、表里无行）。修复：新增迁移 `20260814_024` 恢复 `(user_id, media_account_id, tag_name)`，应用 + SQL 复现验证通过。前端 `t-select multiple filterable` 与后端 `AddTags` 契约本身正确，未改。GUI 最终复核**通过**（2026-08-14）。
  - **Decision 0010 两态残留修复**：2026-09-03 审计发现账号页检查条件仍兼容历史 `draft`；增加失败回归断言后删除该分支，当前仅 `enabled` 可检查。目标文件 9 tests、完整 Web 38 tests PASS。
  - **文档口径收口（改口，记录于本变更记录）**：① business_status 收敛两态 `enabled`/`disabled`（迁移 021，健康度由派生「账号状态」承载）；② 账号页 v3 无批量工具栏、标签仅单账号增删（批量标签延后）；③ login_status 对齐 PRD 3.3.9（`unknown`/`normal`/`not_logged_in`/`verification_needed`/`expired`/`restricted`/`account_mismatch`/`environment_error`）。同步回改 milestone 218/219 与 PRD 第三章 3.3.6。
- Current：CHG-A 全部 Task（1-7）代码完成；检查链路 + 8 项明细端到端验证 + v3 页面收口自动化验证通过；**v3 页面 GUI 人工验收通过（2026-08-14）**，标签跨账号复用 DB 唯一键修复（迁移 024）已应用并点验。
- Current：按 Decision 0011 实施 Task 8 账号—游戏多关系切换。
- Current：Task 8 的领域模型子任务完成并已验证：`GameIDs` 规范化、完整替换/清空、启用游戏公开关联、停用游戏拒绝；下一步为 `media_account_games` 迁移与 MySQL 原子读写。
- Current：Task 8 的关系表持久化子任务完成并已验证：迁移 025、事务化关系替换、批量关系读回和 `EXISTS` 任一游戏筛选；下一步发布 `game_ids` API 契约与兼容路由。
- Current：Task 8 的 Cloud API 子任务完成并已验证：`game_ids` 为正式创建/更新/筛选字段，`game_id` 兼容且冲突请求拒绝；下一步更新 Cloud Web 多游戏管理。
- Current：Task 8 的真实 MySQL 切换完成并通过：迁移 025 已记录；6 条关系完整迁移；旧 `media_accounts.game_id` 已移除；标签、Cookie、检查项和 Profile 绑定计数均保持；重复关系被复合主键拒绝。当前源码强制重启后 Cloud/Agent/BitBrowser/Desktop assets/DMG/login smoke 全部 PASS；Cloud 关系层回归与 Cloud Web 40 项测试 PASS。Desktop 生成资产已刷新（`849f244`）。见 `evidence/2026-09-03-multi-game-cutover.md`。
- Current：Task 8 的手工页面业务点验尚未执行：内置浏览器访问本地 Cloud 被 `ERR_BLOCKED_BY_CLIENT` 拦截，未发生登录或账号数据修改；自动化覆盖已通过。待可访问本地页面的交互环境中，以明确的可丢弃账号验证双游戏创建、替换、清空、任一游戏筛选和未绑定游戏执行资格。
- Next：补齐上述手工页面点验后，审计 CHG-032 全部已转移事项并按门禁关闭；7/8 真实样本验收由 CHG-034 承接，代理检查项 3/4 由 CHG-033 回接。
- Blockers/已知：Task 8 仅剩本地页面访问受客户端拦截的手工点验；7/8 真实样本校准由 CHG-034 承接；代理项 3/4 由 CHG-033 回接；自动化接码登录（上号）属 M2-D。
- Recent verification：窗口收口 DONE（CHG-031）；2026-09-03 从当前源代码重新执行 `m2b-local-acceptance.sh all`，Cloud/Agent/BitBrowser/Desktop assets/DMG/login smoke 全部 PASS；Web 38 tests PASS；Cloud mediaaccount + migration tests PASS；Agent 13 项目标 unittest PASS；Desktop 10 tests PASS；迁移 024 已记录且唯一键列顺序验证通过。Cloud 修正提交 `56fc86e`，Desktop 生成资产提交 `95db0e8`。见 `evidence/2026-09-03-current-environment-and-regression.md`。

## 9. Pending Questions

- Q-01（已决）：Decision 0011 已确认多游戏关系和媒体账号域公开游戏规则；Task 8 实施中。
- Q-02（已决）：真实样本校准移至 CHG-20260903-034；当前 CHG 不把 7/8 的 `na` 骨架作为真实通过。
