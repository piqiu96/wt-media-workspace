# CHG-20261015-097 实施计划

1. 先更新 Cloud 提供方 OpenAPI，明确管理员处置是受保护的显式声明，保留原有 `/retry` 对 `execution_uncertain` 的拒绝；新增接口为兼容增量。
2. 按先红后绿补 Repository 与 Service：以任务当前状态和成片不存在为事务守卫，记录管理员、原尝试和依据，原子打开下一条人工尝试；二次请求无额外尝试。
3. 新增详情的处置事实和脱敏诊断读回，Cloud 共用 Vue 页面展示待处置与管理员操作，普通运营只读安全摘要。
4. 真库、API、Vue 回归核对统计和任务状态；逐 Task 更新证据与 checkpoint，分别提交 Cloud 和 Workspace。
