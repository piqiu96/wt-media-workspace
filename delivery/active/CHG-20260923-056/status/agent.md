# CHG-20260923-056 — wt-media-agent 状态

- 2026-09-23：审计完成（config.py/log_setup.py 死代码、5 处 os.getenv、入口空壳、sidecar 硬编码）。待执行 T-02～T-05。
- 2026-09-23 T-01：本仓 AI 入口文档（`AGENT-INDEX.md`/`AGENTS.md`/`CLAUDE.md`/`DIRECTORY_MAP.md`）已于上一轮提交（`d3ab02f`），工作区干净，未在本轮再动。测试基线实测 `Ran 85 tests OK`（`HEAD=99f408c`），见 `evidence/task-02-baseline.md`。配置格式按 D-05 定为 TOML，T-03 据此实施。
- 2026-09-23 T-02 完成（`99f408c` → `b1233cc`，14 个 commit）：目录迁移至 ADR-0016 目标布局。撤销 `runtimes/`、`core/`、`constants.py`、`proxy_check.py`、`runner.py`；新增 `runtime/`、`clients/`、`services/`、`utils/` 与 `runner/` 包。测试从 85 增至 94（新增 `test_storage_sqlite.py` 5 例、`test_utils_time.py` 4 例）；逐 commit 复跑矩阵无一低于基线。冻结导入（`test_runner_session.py`）逐字节未改，冻结路径/符号/console script 全部未动。两条 ADR-0016 层级例外登记为 D-06，待 T-05 白名单收窄到单文件粒度。详见 `evidence/task-02-structure-migration.md`。
- 2026-09-23 T-02 遗留事实（T-04 需接）：当前 PyInstaller 产物的 PYZ 中 `runner`/`executors` 为 0 个模块——`sidecar_main` 只经 `local_api.server`，够不到它们；T-04 让 sidecar 委托 `bootstrap` 后模块集合会变，需重新取证。`cloud_agent_client.py`/`cloud_agent_contract.py` 两个 re-export shim 待 CHG-B/C 退役。
