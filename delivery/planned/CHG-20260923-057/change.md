# CHG-20260923-057：联合工程优化 B——Paths、Logger 和运行目录

- Status: PLANNED
- Level: M
- 锚点：`docs/engineering/specs/2026-09-23-launch-engineering-optimization-program.md` §3 CHG-B；ADR-0016；架构基线 §5.8
- 日期：2026-09-23
- 前置：CHG-20260923-056（A）完成
- 当前仓库：`wt-media-desktop`、`wt-media-agent` 为主；`wt-media-workspace`（治理）为辅

## 独立目标与范围

完成 Desktop/Agent 独立运行目录、日志初始化、真实落盘、轮转、历史清理及脱敏；`operation_id` 日志关联；自动化测试目录隔离；sidecar stdout 持续消费（保留有限最近启动输出，不转存全部 INFO）。

**吸收自 CHG-20260923-053 Task 6**：OS 标准数据目录（内部 `data/ logs/ versions/`，懒创建且失败降级）；Agent 三个 JSON 日志文件 + stderr；`GET /api/v1/health` 聚合健康检查（Agent 版本/Cloud/BitBrowser/Storage 状态，不触发对外写请求）与契约更新，`/healthz` 字段冻结。

关键验收点（来自程序总纲）：
- Desktop 单一日志初始化入口（tracing 或 Tauri Log 插件，二选一不并存）；单文件 20MB / 保留 14 天 / 总占用 100MB 目标有真实测试。
- Agent `runtime/logging/` 补全轮转（RotatingFileHandler）、retention（保留天数与总占用 ~400MB）、redact；日志变量名已由 CHG-A 统一。
- 敏感信息（Cookie/Token/代理密码等）不进日志与诊断输出，双道防护（源头避免 + Logger 脱敏）。
- 多实例不共享写入同一日志/数据文件；测试用独立临时目录。
- Agent 进程管理事件写入 Desktop 日志（`target=agent.supervisor`），不强制第二个日志文件。

## 明确不做

- 不做用户设置 UI 与清理按钮（CHG-C）；不做端口就绪通知与打包校验（CHG-D）。
- 不为日志关联创建新的业务任务体系（operation_id 是本机操作关联，非业务任务）。
