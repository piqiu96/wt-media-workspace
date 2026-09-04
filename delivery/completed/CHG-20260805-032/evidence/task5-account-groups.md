# Task 5 证据：账号组（可保存筛选，PRD 3.3.6）

日期：2026-08-05
CHG：CHG-20260805-032（M2-B 社媒账号收口）
状态：完成

## 目标

用户把一组筛选条件保存为命名账号组，一键应用筛选目标账号；发布/互动（M6/M8）将依赖它筛目标账号。

## 设计要点

- **全新功能**（无现有模型）
- 保存 `AccountFilter` 子集为 **filters JSON**：game_id/platform/business_status/login_status/search/any_tags/all_tags/exclude_tags（均可 null）
- **应用复用** `ListAccounts`：反序列化 filters → AccountFilter，无新查询逻辑
- 组归属 `(user_id, name)` 唯一（私有组）
- **主键一律自增**：`account_groups.id BIGINT UNSIGNED AUTO_INCREMENT`（遵循用户全局约束，不用规则生成字符串），Go 结构 `ID string`（匹配 browser_profiles 先例），store `LastInsertId` 返回

## 交付

- **迁移** `20260805_019_account_groups.sql`（已应用，20 total）
- **service**：CreateAccountGroup/List/Update/Delete/ListAccountsByGroup；权限仅本人（admin 可代管）
- **routes**：`POST/GET/PATCH/DELETE /api/v1/account-groups` + `GET /account-groups/:id/accounts`（应用组筛选返回账号列表）
- **前端** AccountsPage：账号组下拉（选择→应用筛选）、「保存当前筛选」对话框、「删除该组」
- **测试**：CRUD/他人不可改删/应用筛选按组过滤

## 提交

- Cloud `1f26ec0`

## 验证

- Cloud `go test ./internal/...` 全绿；mediaaccount 新增账号组测试通过
- Web 36 tests；构建通过；迁移应用成功
- 账号组：创建→应用→列表按组过滤；改/删→刷新

## 待办

- Task 4（检查 8 项明细 UI + 7/8 判定骨架）——7/8 需真实受限样本（用户暂时无法提供，先做明细 UI 框架 + 判定逻辑骨架）
