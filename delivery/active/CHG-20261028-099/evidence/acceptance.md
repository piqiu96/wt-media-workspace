# CHG099 · 验收状态

当前结论：**自动化、真实 MySQL 和 API/Web 读回通过；真实 BitBrowser 写入与目标网络尚未执行，因此状态保持 VERIFYING，不宣称可发布。**

| 验收项 | 结论 | 证据 |
| --- | --- | --- |
| 前置类目 CHG107 | PASS | 已合入本地主线；4 条历史类目迁移、API/页面读回通过 |
| Cloud 7 张领域表 | PASS | `20261029_079_operating_resources.sql` 在 scratch 与稳定本地库重放成功；旧扫描候选、旧代理、旧账号分组、通用 tasks、sensitive 表均无残留 |
| 列表不读 Cookie 大字段 | PASS | 账号列表 SQL 使用独立 summary 列；真实 API 返回不含 Cookie |
| 单用户单快照 | PASS | `browser_profile_syncs` 唯一用户键；提交、读取、确认、删除链路通过 |
| 代理失败释放与并发 | PASS | 真实 MySQL live test 覆盖同窗口第二目标冲突、两窗口抢最后名额、失败清预留 |
| 代理 Desktop 桥 | PASS（自动构建/单测） | Rust 命令调用 Agent `proxy-mutation`，验证 readback；代理写入不再由 Cloud 访问本机 Agent。动态提取归属仍按本 CHG 明确排除项保持原样 |
| Cloud API 读回 | PASS | 临时空库运行 79 个迁移；登录、账号、同步确认、Cookie 同步、代理预留/成功/释放、PATCH 启停与额度均读回 |
| Web 页面读回 | PASS（浏览器） | 社媒账号、浏览器窗口、代理管理三页在临时 Cloud 环境真实读回 |
| Workspace | PASS | 在四仓分支上下文临时布局中通过 175 tests、M0 config、M2 static matrix 与 product alignment |
| Cloud Go | PASS | `go test ./...` |
| Web | PASS | 90 files / 813 tests；Cloud 与 Desktop 双 build 通过；页面直接使用 `enabled/local_state/protocol/max_profiles/platform_*` |
| Agent | PASS | 652 tests；通用任务执行器、preflight/permit 与 proxy-check 已删除，只保留 file-transfer 循环；Local Agent API 为 `2026.10.29.2` |
| Desktop | PASS | 539 passed / 6 ignored；账号检查/Cookie 使用 `operation_id`，敏感 preflight 已删除 |
| 真实 BitBrowser 开关/编辑/代理应用 | NOT VERIFIED | 需要指定不影响现有运营数据的测试窗口和可达目标网络代理；本轮未擅自改动存量窗口 |
| 真实目标网络 | NOT VERIFIED | 没有授权测试代理目标；Cloud 检测逻辑通过单测，不做 fixture 冒充真实验收 |
| 代码提交 | READY FOR REVIEW | Cloud `c5acb5b`；Agent `d679a3b`；Desktop `772b5bd`；三个工作树 clean |
| 发布 / 合并到远端 | NOT EXECUTED | 本地提交与审核留待用户早上 review；未推送或发布 |
