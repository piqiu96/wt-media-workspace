# Checkpoint — CHG-20260925-062

- 状态：IMPLEMENTING（2026-09-25 激活）。
- 性质：为 2026-09-24 已在会话内完成、却一直没有治理承载的「入口重构」补记录，
  并修掉该重构连带产生的三处陈旧指针。Level S，仅 `wt-media-workspace` 一仓。

## Completed

- 2026-09-25 Start Gate：`delivery/active/` 仅 `.gitkeep`、`LEDGER.md` 无 CHG 表行、快照
  `Active CHG: none` / `Status: NONE`——三者一致。无阻塞 `Q-xx`；Level S 不强制 Milestone 引用。
  工作区 6 个脏文件逐个核实归属：5 个属本 CHG，1 个（`2026-09-24-m4-m5-cloud-content-production.md`
  的尾部空行）与本 CHG 无关。
- 2026-09-25 D-02 执行：上述无关文件 `git checkout --` 还原，与 HEAD `git diff` 为空（逐字一致）。
  还原后工作区只剩 5 个修改文件，且全部落在本 CHG 的 §5 Scope 内。
- 2026-09-25 T-01：建 `delivery/active/CHG-20260925-062/`（`change.md` 十三节、本 `checkpoint.md`、
  `evidence/`），`delivery/LEDGER.md` 加表行，快照经 `prepare_ai_workspace.py --change` 再生成。
  单仓实施，**不建** `status/`。

## Current

- T-01 收尾核对（LEDGER 表行格式与两个验证器读数）。

## Next

- T-02 提交入口重构本体（四文件一个 commit）。
- T-03 修 `docs/engineering/specs/agent-workspace-conventions.md` 的三处陈旧引用。
- T-04 修两个 workspace skill 的第 1 步指针并分发生成副本。
- T-05 收尾：证据、验收矩阵、DONE Gate 签字、归档与失效指针扫描。

## Blockers

- None。

## Recent verification

- 开工前：`verify_agent_entry.py` → `0 warning(s) need review`（快照 1668 字符）；
  `verify_delivery_governance.py` → `ok, Active CHG: none`；`verify_skills.py` → `verified 10`；
  `sync_skills.py check` → `skill outputs are up to date`。
- 开工前测试基线：`python3 -m unittest discover -s tests -q` → **Ran 73 tests / FAILED (failures=4)**。
  4 条红项全在 `verify_product_master_alignment.py`（M2 期望 `IN_PROGRESS` 实为 `DONE`、
  M3 期望 `NOT_STARTED` 实为 `DONE`、M2/M3 能力清单缺项、M10 缺 `FFmpeg/FFprobe 分发`），
  与本 CHG 无关，按 §5 Explicitly Not Doing 保持红——**但关闭时必须重跑并逐条同名比对**（§10 AC-07）。
- 开工前仓状态：HEAD `840ba38`，分支 `main`。

## 执行期间的边界（不得越界）

- **不碰 M4**：CHG-20260924-061 保持 `PLANNED`，不得激活或改动 M4 任何记录。
- **三仓零改动**：`wt-media-cloud`、`wt-media-agent`、`wt-media-desktop` 全程不读不写。
  （已核实 `workspace` skill 分组不投递到这三仓，故 T-04 的同步不会脏化它们——但**关闭前仍要复验**。）
- **不改 `verify_agent_entry.py` 的检查语义**（§4 已证明其 workspace 臂先于本次重构就空转）。
- `.ai/CURRENT_CONTEXT.md` 由脚本生成，**禁手改**；`.claude/skills`、`.codex/skills` 是生成副本，
  **禁手改**——只改 `skills/` 源再跑 `sync_skills.py`。
- 跑校验脚本一律带 `-B -X pycache_prefix=<空目录>`，避免等长改动被旧 `.pyc` 服务。
