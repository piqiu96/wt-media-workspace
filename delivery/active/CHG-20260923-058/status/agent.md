# CHG-20260923-058 — wt-media-agent 状态

- 2026-09-24：尚未开始改动（工作区干净）。起点测试基线 **379 tests OK**（`bash scripts/test.sh`）。
- 本仓范围：T-02 的 Agent 半边（轮转换代 + `LogBudget` 收敛 + 配置键收敛 + 测试同步）。
- 起点事实（详见 `../change.md` §4.6）：四个界各自有明确住处——
  日期翻档与归档命名在 `BoundedFileHandler._roll_if_needed`/`_free_name`（`runtime/logging.py:696-717`）、
  单条截断在 `_bounded`（`:658-680`，**保留**）、总量上限与按天保留都在 `LogBudget.prune`（`:549-567`）。
  归档家族正则是**运行时拼的**（`LogBudget.register:513-520`），故**写侧与读侧要同时改**。
  数字三层：`constants.py:48-50` → `config.py:199-201` → dataclass `:225-227`，交叉校验在 `:346-350`。
- **测试锚点**（不改就是「改代码没改测试」）：`tests/test_log_rollover.py` 的 **21** 处旧归档名断言、
  `tests/test_runtime_logging.py:151` 的 `kinds.count("BoundedFileHandler") == 3`、
  `BoundedFileHandler` 全仓 **8 命中**（src 2 / tests 6）。
- 待办：T-02 换用标准库 `TimedRotatingFileHandler(when="H", suffix="%Y-%m-%d-%H", backupCount=0)`，
  **按天删除仍由 `LogBudget` 负责**（有意的不对称，见 `../change.md` Q-07）。
