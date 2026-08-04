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
