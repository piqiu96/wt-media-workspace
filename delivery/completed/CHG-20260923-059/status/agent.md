# CHG-20260923-059 — wt-media-agent 状态

> 本文件是**开工时**的状态快照（下面每条都写于 T-01 之前，保留原文，一字未改）。**关闭时的终态**见末行。

- 起点（2026-09-25 激活时实测）：`bash scripts/test.sh` = **377 tests OK**。
- 本仓范围：T-03 的 Agent 一半（SIGTERM 处理与在飞任务收尾）、T-05（`build_desktop_sidecar.py`
  的 `config_online → 产物/config` 整目录替换）、T-09（`AGENTS.md`/`README.md`/`contracts/*/README.md` 同步）、
  T-10 的 Q-01 过期注释回写（`config_online/agent.toml:17-21`）。
- **不动的既有结论**：按天保留由 `LogBudget` 负责、轮转由标准库 `TimedRotatingFileHandler` 负责——
  这是 C 定型的**有意不对称**（Desktop 侧由 `file-rotate` 一并承担），见 `change.md` §6 D-10。
  本 CHG 只在**退出路径**上动写入者的生命周期，不动轮转与保留规则。
- 起点缺陷（**既有，不是本次引入**）：`local_api/server.py:630` 只捕 `KeyboardInterrupt`，
  SIGTERM 到不了任何清理路径——这正是 T-03 要关的那条。

## 关闭时的终态（2026-09-25）

- T-03（`local_api/server.py` 的 SIGTERM 与在飞收尾，`70a1647`）、T-05（`build_desktop_sidecar.py`
  的 `--config-dir` 整目录替换 + `runtime/config.py` 的冻结侧推导）、T-09（入口文档与契约文档判据，
  `2b26808`）均已交付；本 CHG 该仓**未改任何业务实现**，改动集中在退出路径、配置装载与文档。
- T-10 的 D-08 落点：`config_online/agent.toml` 与 `config_online/README.md` 的过期 Q-01 陈述改写为
  「已裁定：保持回环（2026-09-25）」；判据是 `tomllib` **解析后叶子 12 条全等**（阳性对照改一个值报 False）
  ⇒ 配置值一个字节未动。新增判据 `tests/test_config_shipping.py` 的两条（`Ran 12 tests / OK`）。
- 计数：**377 → 409 OK**（只增不减，本 CHG 无下降项）。T-09 之后是 407，T-10 为 D-08 新增 2 条判据（`tests/test_config_shipping.py`）⇒ 409（`evidence/task-10-agent-suite.out`）。
- **一条既存的间歇红**（`SigtermTests.test_a_request_in_flight_when_the_signal_arrives_is_waited_for`，
  原树 1/20、与本次改动无关）按 D-27／Q-07 登记，**未修**：机制未确证前不加 `sleep` 糊过去。
