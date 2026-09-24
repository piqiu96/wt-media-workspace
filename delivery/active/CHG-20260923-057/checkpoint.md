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

## Current

- T-02 待开始（Agent 测试目录隔离）。

## Next

- T-01 收尾：`delivery/LEDGER.md` 加**裸 id** 表行（markdown 链接会让验证器读成 `none`）+
  `delivery/planned/README.md` 的 B 行改 ACTIVE；`prepare_ai_workspace.py --change CHG-20260923-057`；
  两个验证器绿；快照 `Active CHG: CHG-20260923-057`。
- 阶段 1 Agent：T-02 → T-03 → T-04 → T-05 → T-06 → T-07 → T-08 → T-09（**顺序有依赖**：T-02 必须先行，
  否则 T-03 让 dev 真落盘后，测试会写进真实检出目录 `.local/`）。
- 阶段 2 Desktop：T-10 → T-11 → T-12 → T-13 → T-14 → T-15 → T-16 → T-17。
- 阶段 3：T-18 回写与收尾。

## Blockers

- None。裁定十三节已把草案的待决项全部定下；§7 的 Q-01…Q-04 均为 `Blocking = NO`，已按读数实施。

## Recent verification

- Start Gate（2026-09-24）：四仓工作区干净（governance/agent/desktop/cloud 各 `git status --porcelain` 为空）；
  `delivery/active/` 仅 `.gitkeep`；`LEDGER.md` 无表行；快照 `Active CHG: none`。
- 起点测试基线：Desktop **68**（二进制 crate，`cargo test --lib` 不成立）、Agent **253 tests OK**。
- T-01：见 `evidence/task-01-governance.md`。

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
