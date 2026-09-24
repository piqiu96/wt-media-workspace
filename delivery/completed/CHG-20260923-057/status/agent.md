# CHG-20260923-057 — wt-media-agent 状态

> 本文件是**开工时**的状态快照（下面每条都写于 T-02 之前，保留原文）。**关闭时的终态**见末行。

- 2026-09-24：尚未开始改动（工作区干净）。起点测试基线 **253 tests OK**。
- 本仓范围：T-02…T-09。
  - 起点事实（详见 `../change.md` §4.3/§4.4）：`runtime/logging.py` 是唯一接触 logging 配置的模块，
    只有一个 `RotatingFileHandler`（10MB×3）；全仓 `task.log`/`error.log` 字面量零命中；
    无 `extra=`/`LogRecord` 工厂/`Filter` 子类；dev 因 `paths.py:107` 返回 `""` 而**不写文件**；
    `bootstrap/app.py:76` 与 `local_api/server.py:591` 存在**两次** `configure_from`。
- 待办：T-02 测试隔离（含修 `tests/test_storage_migration_paths.py:46` 对真实检出目录的断言）。

**终态（2026-09-24 关闭时追加，上文一字未改）**：T-02…T-09 与 T-19/T-20/T-21 全部 DONE；
`bash scripts/test.sh` → **379 tests OK**（起点 253，全程单调不降）；工作树干净，本 CHG 的改动全部落地提交。
起点事实逐条被推翻或落实：`RotatingFileHandler` 换成三文件路由、`configure_from` 由两处收敛为
`bootstrap/app.py` 一处（R11 AST 规则钉着）、dev 现在**真落盘**、`task.log`/`error.log` 不再零命中。
未交付项与未覆盖项见 `../change.md` §7/§10。
