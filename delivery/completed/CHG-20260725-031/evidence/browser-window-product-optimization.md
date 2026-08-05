# 浏览器窗口页产品优化记录（M2-B 验收）

日期：2026-08-04
CHG：CHG-20260725-031（M2-B7 批量账号检查与 M2-B 综合收口）

## 用户产品反馈与决策

1. 菜单"浏览器用户"→"浏览器窗口"（里程碑要求"页面使用浏览器窗口"）。
2. 系统 ID 用自增主键倒序；支持按比特 ID 排序。
3. 停用功能：经产品评审废弃"停用/归档"（与"扫描反映 BitBrowser 真实"冲突、不持久）；改为**窗口业务状态（启用/停用）**——仅作社媒账号匹配筛选标志、可筛选、不被扫描覆盖；停用窗口打开/关闭不可用、账号绑定候选排除；窗口存在性仍由扫描决定。停用+本机仍存在→无 diff 保留镜像；停用+本机已删除→diff 扫出缺失→可同步删除 Cloud 记录。
4. 搜索拆分为独立字段（系统ID/名称/分组/Bit ID/备注）。
5. 缺失功能：编辑窗口（Cloud 备注）、状态分列、详情补充本次实现；标签因无 tags 列记为后续 CHG。

## 实现

### 后端（wt-media-cloud）
- 迁移 `20260804_016_browser_profiles_business_status.sql`：`browser_profiles` 加 `business_status`（enabled/disabled，默认 enabled）。
- `profilebinding/service.go`：`ProfileBusinessStatus` 常量；`BrowserProfile.BusinessStatus` 字段；`UpdateProfile`（remark + business_status）；`DeleteProfile` 改为同步删除（需 disabled + 无依赖）；`ErrProfileNotDisabled`。
- `profilebinding/store_mysql.go`：`ListProfiles`/`ListAllProfiles` 改 `ORDER BY id DESC`；扫描 upsert **不覆盖** business_status（ON DUPLICATE KEY UPDATE 排除）；`DeleteProfile` 事务清理 runtime_presence 后删除；`ProfileHasDependencies`（media_accounts/sensitive_browser_tasks/sensitive_profile_permits 引用保护）；`UpdateProfile`。
- `profilebinding/routes.go`：PATCH 实现（remark/business_status）；DELETE 用同步删除；错误映射 `ErrProfileNotDisabled`（20011）。
- 测试更新：同步删除（disabled+无依赖→删除；enabled→拒绝；有依赖→拒绝）、UpdateProfile、排序。

### 前端（wt-media-cloud/web）
- `AppLayout.vue` + desktop/cloud router：菜单/路由改名"浏览器窗口"/`browser-windows`。
- `ProfilesPage.vue`：搜索拆分（系统ID/名称/分组/Bit ID/备注 + 业务筛选）；id/bit_profile_id 列 sortable；业务状态列 + 启用/停用切换；Cloud 状态 + BitBrowser 状态分列；编辑（Cloud 备注）弹窗；详情补充字段；diff 缺失 tab 对停用+缺失窗口提供"同步删除"；间距。
- `AccountsPage.vue`：绑定窗口候选排除停用窗口；账号执行资格判断加入窗口停用检查。

### 里程碑
- `M2-account-runtime.md` L229：删除→归档 语义修正为"窗口退役通过业务状态（启用/停用）管理；窗口存在性以扫描为准；停用+本机已删→同步删除 Cloud 记录"。

## 验证
- `go test ./internal/...` 全绿；`npm test` 36 PASS；dist-desktop/dist-cloud 构建通过。
- 迁移应用（41 窗口默认 enabled）。
- API 实测：列表 id DESC 排序 ✓、business_status ✓、PATCH 备注/停用/启用 ✓、同步删除（disabled+无依赖→200 删除；有依赖→拒绝）✓。
- DMG 重建（cargo clean）并内嵌新前端，无 JS 错误。

## 后续
- BitBrowser 侧窗口编辑（Agent update_profile 写回名称/分组/代理）——后续 CHG。
- 标签展示/搜索（需扩 browser_profiles 表）——后续 CHG。
- 详情"历史同步/检查记录"独立查询——后续评估。

# 第二轮产品优化（2026-08-05）

## 用户 10 点反馈与决策
1. confirm 500（ApplyScan INSERT 占位符 bug，21 列 20 `?`）→ 修复；停用+本机缺失窗口**同步自动清理**（接受本地变化时删除 Cloud 记录），移除缺失 tab 逐项同步删除按钮。
2. **browser_profiles.id 从字符串全量迁移为自增主键**（违反里程碑 L206）；默认按比特序号排序；第一列自增ID、第二列比特序号。标识符语义确认：`profile_id`/`browser_profile_id`（FK 列）= 记录 ID，`bit_profile_id` = BitBrowser ID。
3. 授权用户列显示用户名。
4. 运行状态**本地跟踪**（打开/关闭后记录）；已打开只显示关闭、已关闭只显示打开。
5. 操作按钮加配色。
6. 详情抽屉放大（560px）+ 只留关闭样式。
7. 备注**拆分两字段**：`remark`=BitBrowser备注（扫描写入不可改）+ `cloud_remark`=桌面端可编辑追加，一列双标记。
8. 分页总数修复（v-model 与 :pagination 冲突 → watcher 设 total）。
9. 批量打开/关闭（表格多选 + 顶部按钮）。
10. seq/自增ID 列可点击排序。

## 实现
- **迁移 `20260804_017_browser_profiles_auto_increment_pk.sql`**：id varchar→BIGINT AUTO_INCREMENT；4 张 FK 表（media_accounts/runtime_presence/sensitive_tasks/permits）对应列→bigint + 数据映射 + 索引先删后建（首次尝试因 `uq_media_accounts_profile_platform` 保留在 platform 上失败，从备份恢复后修正重试）；加 `cloud_remark`。`uq_browser_profiles_user_bit_profile` 保留。
- 后端：ApplyScan INSERT 改 `id=NULL`（自增）+ 21 占位符 + 新增 cloud_remark；upsert 靠已有 `uq(user_id, bit_profile_id)`；同步自动清理"停用+本机缺失"（事务删 runtime_presence + browser_profiles）；PATCH 改更新 `cloud_remark`（remark 保持 BitBrowser 来源）。
- 前端 ProfilesPage：自增ID/seq 列排序、默认 seq 倒序、运行状态列（本地跟踪）、批量打开/关闭（多选）、操作按钮配色、详情抽屉 560px 无 footer、备注双标记 `[B]`/`[C]`、用户名标签、分页 total watcher、移除缺失 tab 同步删除。
- 测试：ApplyScan 占位符/自动清理/cloud_remark、UpdateProfile、索引 mock 更新。

## 验证
- `go test ./internal/...` 全绿；`npm test` 36 PASS；双端构建通过。
- 迁移应用并验证：id 自增数字、FK 引用完整、索引重建、cloud_remark 列存在。
- API 实测：列表数字 id、PATCH cloud_remark 生效且比特备注保留。
- DMG 重建（cargo clean）内嵌新前端，无 JS 错误。

## 待用户 GUI 复验
自增ID 第一列/seq 第二列排序、批量开/关、运行状态、备注双标记、用户名、配色、详情抽屉、分页总数、confirm 不再报错、停用+本机已删扫描确认后自动删除。

# 第三轮展示优化（2026-08-05）

## 用户 10 点反馈与决策
1. 列名"自增ID"→"ID"。
2. Bit ID 移出列表，仅详情展示。
3. 备注两字段不同颜色（BitBrowser 灰色 / Cloud 品牌色）+ 换行隔开。
4. 授权用户列从列表移除（配合第 8 点做筛选项）。
5. 代理列宽度缩小。
6. 同步列显示完整时间 YYYY-MM-DD HH:mm，列名"同步时间"。
7. 筛选支持打开/关闭（本地运行状态）。
8. 授权用户筛选项（主要云端用）。
9. 菜单栏固定，仅列表区横向滚动。
10. 业务列→"状态"；移除"Cloud状态"列（放详情抽屉）。

## 实现（纯前端）
- `ProfilesPage.vue`：列调整为 ID/seq/名称/分组/代理(窄)/备注/状态/运行/同步时间/操作；详情抽屉含 Bit ID/授权用户/Cloud状态/备注；formatTime 完整格式；备注模板双色双行；过滤区加"运行"（打开/关闭）与"授权用户"筛选；表格 `:scroll="{ x: 'max-content' }"` 横向滚动。
- `AppLayout.vue`：根布局 `height:100vh`，侧栏 sticky 固定，content-area `overflow:auto` 滚动。

## 验证
`npm test` 36 PASS、双端构建通过、DMG 重建内嵌新前端无 JS 错误。待用户 GUI 复验。

# Diff 闭环修复批（2026-08-05）

## 修复项（均已 GUI 确认）
1. **Diff 字段级展示**：变更栏新增"变更字段"列显示 `字段: 旧值 → 新值`（名称/分组/代理/备注）；缺失/新增栏从 Cloud 窗口列表回查字段值，不再显示 "-"。
2. **操作态不入 diff**：`bit_status`（打开/关闭）与 `bit_updated_at`（更新时间）从 changedFields 移除——打开/关闭窗口不再误判为窗口变更。仅配置字段（name/seq/group/proxy/remark/身份）算 diff。
3. **缺失窗口接受后清理**：ApplyScan 接受本地变化时，删除"已从 BitBrowser 删除且无媒体账号引用"的 Cloud 记录；有引用的保留为 local_missing。修复多表 DELETE 关联子查询导致的 FK 错误（用一次性库验证：无引用删、有引用保留）。
4. **备注接受生效**：ON DUPLICATE KEY UPDATE 增加 `remark = VALUES(remark)`——接受本地变化时 BitBrowser 备注更新到 Cloud；`cloud_remark`（桌面可编辑）保持不动。接受文案更新。
5. **未可信扫描友好提示**：`refreshRuntimeWithCooldown` 刷新失败时返回本地状态，由 triggerScan 的 node_id 检查给出"请先绑定可信环境"提示（不再无提示/抛原始错误）。
6. **窗口缩小自适应**：内容区子元素 `min-width:0; max-width:100%`；表格横向滚动由包装层承担。
7. **分页修复**：手动分页（pagedProfiles 切片 + 独立 t-pagination，10/20/50/100 默认20）；操作按钮顺序：详情→打开/关闭→编辑→停用。

## 已确认
用户确认以上修复全部正常。

## 布局修复（标准管理后台 Shell，彻底）
TDesign `.t-layout__content { flex: auto }` 默认撑大页面导致整页滚动。最终方案：
- 全局 `web/src/shared/styles/layout.css`：`html,body,#app{height:100%;margin:0}` + `body{overflow:hidden}`（body 不滚动）。
- AppLayout：根 `.app-shell{height:100%}`、侧栏 `.app-aside{height:100%;overflow-y:auto;flex-shrink:0}`、内层 `.app-main{height:100%;min-width:0;overflow:hidden}`、顶栏 `.topbar{flex-shrink:0}`、内容区 `.content-area{flex:1;overflow:auto;min-width:0;min-height:0}`（唯一滚动区）。
- 关键：`min-height:0`+`overflow:auto` 使 flex 子项可收缩滚动；`overflow:hidden` 只在内层 `.app-main`；表格横向滚动由 `.table-scroll-wrap{overflow-x:auto}` 承担。
- 前两次失败根因规避：`overflow:hidden` 不放根、内容区设 `min-height:0`、html/body 约束。desktop+cloud 双入口均 import layout.css。待用户 GUI 复验菜单/顶栏固定、内容区独立滚动。
