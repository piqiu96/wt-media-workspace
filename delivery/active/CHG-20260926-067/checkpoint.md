# Checkpoint: CHG-20260926-067

- CHG: `CHG-20260926-067`（脚本层分层——四仓 bin 目录、scripts/dev 与 scripts/verify、每仓 scripts/README.md）
- Level: S
- Updated: 2026-09-26

## 状态

`IMPLEMENTING`（2026-09-26 激活；跨四仓）

State words come from §3 of `delivery/MASTER_IMPLEMENTATION_PLAN.md`. A record in
`delivery/active/` may only be `IMPLEMENTING` or `VERIFYING`.

## Completed

- **T-00 激活**：`delivery/active/CHG-20260926-067/` 三件齐备（`change.md`／`checkpoint.md`／`evidence/`）；§5 范围封闭（7 条 Add／11 条 Modify／4 条 Delete／9 条 Explicitly Not Doing）；LEDGER 表行；快照 `--change CHG-20260926-067`；四仓基线落 `artifacts/t00-repo-baseline.out`；脚本层清点与 `bin/` 忽略探针落 `artifacts/t00-script-inventory.out`；六门禁与套件两臂落 `artifacts/t00-gate-before.out`／`t00-gate-after.out`；`MASTER` §3 读数列按实测刷新三项并落 `artifacts/t00-status-words{,-after}.out`（量法**直接 import 门禁自己的 `status_word()`**）。详见 `evidence/task-00-activation.md`。
- **T-00 附带一条自造的红**：LEDGER 表行首版写成 `| [CHG-…](…) |` 且 H1 标题含 `|`，触发三条门禁红 + 套件 1 failure。两条约束（`LEDGER_ROW_RE` 要求 `|` 后紧跟 `CHG-`；`expected_row` 的标题取自 H1，故 H1 不得含 `|`）已登记 §14 第 8 项。

## Current

无。T-00 已完成，下一步是 T-01。

## Next

1. **T-01**（workspace）：建 `scripts/dev/`＋`scripts/verify/` 骨架与 `scripts/README.md`；`verify_delivery_governance.py:130` 扫描面改递归。
2. **T-02**（workspace，**必须早于 T-03**）：`verify_m0_config.py` needle 收敛 ＋ `verify_m0_local.sh` desktop 块收敛。这一步是 desktop 删除的**硬前置**——不先做，desktop 一动这两个门禁当场红。
3. **T-03 → T-04 → T-05 → T-06**：desktop、cloud、workspace 回指、agent，逐仓独立提交。
4. **T-07**：收尾。

## Blocked

- None.

## Recent verification

| 判据 | 读数 |
|---|---|
| 六门禁（激活前） | 六个全 `exit=0`；`sync_skills.py check` `exit=0`；见 `artifacts/t00-gate-before.out` |
| `unittest discover -s tests -q`（激活前） | `Ran 100 tests` / `OK` |
| 四仓 HEAD（激活前） | workspace `71fd32f`／cloud `0db02ab`／agent `6d740fc`／desktop `7c1b0ad`（`artifacts/t00-repo-baseline.out`） |
| 四仓工作树（激活前） | workspace 仅本 CHG 新目录；cloud 仅未跟踪 `dump.rdb`；agent ` M AGENT-INDEX.md`；desktop 干净——**后两条先于本 CHG 存在，不触碰** |
| 脚本层清点（分母＝`git ls-files scripts`） | workspace **18**／cloud **10**／agent **10**／desktop **20**；四仓 `bin/` 均不存在（`artifacts/t00-script-inventory.out`） |
| `bin/` 忽略探针 | **只有 cloud** 报被 `.gitignore:3` 忽略；另外三仓报不被忽略（探针能报出相反结论 ⇒ 否定读数可信） |
| `MASTER` §3 读数列 vs 实测 | **逐词相等**：活列 19／归档列 33／归档 `DONE` 31／分母 41；闭合式 33＋2＋2＋4＝41 ✓（`artifacts/t00-status-words.out`） |
| 里程碑覆盖（分母 5 篇，README 除外） | 脚本层关键词 **0 命中** ⇒ 无可锚里程碑，取 `Level: S` |
| 六门禁 + 套件（激活后） | 六个全 `exit=0`；`sync_skills.py check` `exit=0`；`Ran 100 / OK`（`artifacts/t00-gate-after.out`） |
| LEDGER 表行合 `validate_active_change` | 首版**不合**（表行形态 + H1 含 `|`）→ 三条门禁红 + 1 failure；改后**合**（§14 第 8 项） |
| 本 Task 记录体量 | 见 `artifacts/t00-record-size.out`——**不在此内联**，本表的字节数会随写入而改变 |
