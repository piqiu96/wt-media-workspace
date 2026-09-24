# Checkpoint — CHG-20260923-057

- 状态：IMPLEMENTING（2026-09-24 激活）。
- 性质：联合工程优化 B——Paths、Logger 和运行目录。Level M，跨两仓（agent / desktop）+ 治理回写。
- 权威：用户 2026-09-24《CHG-057 日志治理裁定补充说明》十三节。它**推翻**了本 CHG 草案的三处：
  Agent 日志改「三文件纯文本」而非 JSON、Desktop 后端只用官方 `tracing-subscriber`（无自写降级路径）、
  **不发 `X-Operation-Id`**（跨端 `operation_id` 本轮不交付）。

## Completed

- 2026-09-23：草案建于 `delivery/planned/CHG-20260923-057/`（PLANNED）。
- 2026-09-24 T-01：`git mv` 移入 `delivery/active/`（**不留副本**），改写为十三节执行记录
  （`change.md`、本 `checkpoint.md`、`evidence/`、`status/`），§4 记下实测起点。
- 2026-09-24 T-02：Agent 测试目录隔离（`wt-media-agent` `7382fed`，**test-only，`src/` 零改动**）——
  规则「测试不得把派生根接 `.local`」+ `scripts/test.sh` 前后新增路径守卫 + `isolated_paths()` 隔离助手；
  修掉 `tests/test_storage_migration_paths.py:46` 对真实检出的断言（改注入根，**未删断言**）。
  **先量后改**：实测今天本机与干净克隆都不写 `.local/`，故本 Task 的定位是 **T-03 之前的守卫**，不是修当下泄漏。
  顺带查出 AC-11 被计划高估——「不误连真实外部服务」那半今天**无规则在守**，已拆为 AC-11b 并新增 **T-19**（§7 Q-05）。

## Current

- T-03 待开始（Agent dev/override 真落盘，推翻 `paths.py:107`）。T-02 已使这一步安全。

## Next

- 阶段 1 Agent：T-03 → T-04 → T-05 → T-06 → T-07 → T-08 → T-09（T-02 已完成，是它们的**前置**：
  否则 T-03 让 dev 真落盘后，测试会写进真实检出目录 `.local/`）。
- 新增 **T-19**（AC-11b 的 AST 规则：客户端构造必须注入假 `transport`）排在阶段 1 余项之后，编号排末位以免打乱 T-03…T-18。
- **定向验证命令一律带 `PYTHONPATH=tests`**：`tests/` 无 `__init__.py`，`python -m unittest tests.<模块>` 对
  6 个 import `support` 的模块（5 个是既有的）报 `ModuleNotFoundError`。既有布局属性，本 CHG 不动布局。
- 阶段 2 Desktop：T-10 → T-11 → T-12 → T-13 → T-14 → T-15 → T-16 → T-17。
- 阶段 3：T-18 回写与收尾。

## Blockers

- None。裁定十三节已把草案的待决项全部定下；§7 的 Q-01…Q-04 均为 `Blocking = NO`，已按读数实施。

## Recent verification

- Start Gate（2026-09-24）：四仓工作区干净（governance/agent/desktop/cloud 各 `git status --porcelain` 为空）；
  `delivery/active/` 仅 `.gitkeep`；`LEDGER.md` 无表行；快照 `Active CHG: none`。
- 起点测试基线：Desktop **68**（二进制 crate，`cargo test --lib` 不成立）、Agent **253 tests OK**。
- T-01：见 `evidence/task-01-governance.md`。
- T-02：`bash scripts/test.sh` → **259 tests OK，exit=0**（253 → 259，只增不减）。改前规则**红且恰好 1 处命中**
  （`test_storage_migration_paths.py:46`）；阳性对照两处实跑出红（规则内正则；端到端探针模块报出
  `test_zz_probe_forbidden.py:3`）；变异探针下 `scripts/test.sh` `exit=1` 点名路径**而套件打印 `OK`**
  ⇒ 守卫独立于测试结果。见 `evidence/task-02-isolation.md`。

## 执行期间的边界（不得越界）

- 开发者自己的 BitBrowser `:54345`、Cloud `:18080`、dev Agent `:8765` **全程不碰**；所有启动用 scratch 端口。
- `.ai/CURRENT_CONTEXT.md` 由 `prepare_ai_workspace.py` 生成，**禁手改**。
- 运行仓改动只限 `wt-media-agent` 与 `wt-media-desktop`（本记录 §1 已列）；`wt-media-cloud` 不碰。
- 证据文件一律 `.out` 后缀，不用 `.log`（两仓 `.gitignore` 都有 `*.log`）。
- 一仓一 commit；「移动文件」与「改逻辑」绝不进同一 commit。

## 实测起点里最容易被忽略的三条（施工时反复回看）

1. **dev 今天根本不写日志文件**（`paths.py:107` 对 dev/override 返回 `""`）——磁盘上 `.local/logs/` 是空的。
   「日志有轮转」的直觉在此处不成立。
2. **Agent 只有 3 个 logger 在发记录**（runner / local_api.server / runtime.config），
   `executors/`、`services/`、`clients/`、`storage/` 零日志调用——按名字路由今天只能区分两面。
3. **Desktop 全仓只有 5 处裸 emit**，其中 4 处是 emit（第 5 处是注释）——日志面是从零开始，
   不是「给已有日志加轮转」。
