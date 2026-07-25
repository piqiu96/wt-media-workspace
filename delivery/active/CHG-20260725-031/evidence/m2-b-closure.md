# M2-B 综合收口矩阵

日期：2026-07-25

## Evidence 链

- B1：`delivery/completed/CHG-20260723-025`，浏览器窗口扫描与 Diff 只读闭环；
- B2：`delivery/completed/CHG-20260723-026`，窗口同步应用、恢复与授权闭环；
- B3：`delivery/completed/CHG-20260724-027`，媒体账号台账与 Profile 真实绑定闭环；
- B4-1：`delivery/completed/CHG-20260724-028`，单个媒体账号检查与身份回填闭环；
- B5：`delivery/completed/CHG-20260724-029`，浏览器窗口真实操作与台账收口；
- B6：`delivery/completed/CHG-20260725-030`，媒体账号操作与检查收口；
- B7：`delivery/active/CHG-20260725-031`，批量账号检查与 M2-B 综合收口。

## 完成标准对照

| M2-B 完成标准 | 状态 | Evidence |
|---|---|---|
| 单个和批量窗口真实创建、逐项读回、部分成功和失败项重试成立 | PASS / 需真实环境人工验收 | B5 `desktop-create-profile.md`、`desktop-open-close.md`；批量窗口创建不在 B7 范围，后续如产品需要专门批量创建体验再独立 CHG。 |
| 自动与手工扫描均只产生 Diff，用户可以接受或恢复且读回一致 | PASS / 需真实环境人工验收 | B1、B2、B5 Evidence。 |
| 浏览器窗口不做真实删除 BitBrowser Profile，只归档 Cloud 镜像 | PASS | B5 `diff-and-archive.md`。 |
| 管理员可分配未授权 Profile；高级运营只查看同组授权范围的 Cloud 状态 | PASS | B2 `authorization-and-binding-summary.md`。 |
| 账号可创建、编辑、绑定、解绑、换绑、加减标签和筛选 | PASS | B3 Evidence，B6 `account-ledger.md`、`account-profile-binding.md`。 |
| 账号台账页面支持列表、详情、搜索、平台/游戏/标签/业务状态/登录状态筛选、分页和备注维护 | PASS | B6 `account-ledger.md`。 |
| 单个/批量账号检查真实回填平台身份、头像、登录状态和最近检查时间 | PASS / 需真实环境人工验收 | B4-1、B6 `account-check-sync.md`、B7 `batch-account-check.md`、`batch-retry.md`。 |
| 页面、Cloud 镜像、Agent 读回和 BitBrowser 实际状态一致 | PASS / 需真实环境人工验收 | B1-B7 Evidence；自动测试证明控制流，真实一致性需要用户在 BitBrowser 环境执行验收。 |
| Cloud Web 与 Desktop 页面边界清晰 | PASS | B1、B5、B6、B7 Evidence。 |

## DEFER 项

- 代理写入、代理读回、窗口代理变化正式闭环属于 M2-C。
- Cookie、CK、接码、人工验证码和 Cookie 导出属于 M2-D。
- 持久化 batch/item、重启恢复和本地执行抽屉属于后续 M2-D/M2-E；B7 首版批量检查为 Desktop 页面串行逐项执行，不创建 Cloud 通用 task。
- 状态枚举数据库迁移暂不做：当前代码保留历史内部枚举，页面提供用户可读映射；如需改成 Milestone 文案枚举，应单独做兼容迁移 CHG。

## 收口结论

从代码、自动测试、Evidence 和边界治理看，M2-B 已具备进入 M2-C 的工程条件。

进入 M2-C 前仍建议由用户完成一次真实 Desktop / Local Agent / BitBrowser 人工验收：

```text
扫描窗口 → 处理 Diff → 新建窗口 → 打开/关闭窗口
→ 新增账号 → 绑定窗口 → 单项检查/同步
→ 多选账号批量检查/同步 → 失败项重试
```

如果人工验收发现真实平台身份读取、BitBrowser 读回或页面结果不一致，应创建 M2-B 修复 CHG；否则可进入 M2-C。
