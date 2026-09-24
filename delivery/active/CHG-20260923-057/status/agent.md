# CHG-20260923-057 — wt-media-agent 状态

- 2026-09-24：尚未开始改动（工作区干净）。起点测试基线 **253 tests OK**。
- 本仓范围：T-02…T-09。
  - 起点事实（详见 `../change.md` §4.3/§4.4）：`runtime/logging.py` 是唯一接触 logging 配置的模块，
    只有一个 `RotatingFileHandler`（10MB×3）；全仓 `task.log`/`error.log` 字面量零命中；
    无 `extra=`/`LogRecord` 工厂/`Filter` 子类；dev 因 `paths.py:107` 返回 `""` 而**不写文件**；
    `bootstrap/app.py:76` 与 `local_api/server.py:591` 存在**两次** `configure_from`。
- 待办：T-02 测试隔离（含修 `tests/test_storage_migration_paths.py:46` 对真实检出目录的断言）。
