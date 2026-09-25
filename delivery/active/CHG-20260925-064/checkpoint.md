# Checkpoint: CHG-20260925-064

- CHG: `CHG-20260925-064`（权威冲突与重复落点处置——按单一落点收口）
- Level: S ／ 仅 `wt-media-workspace` 一仓
- Updated: 2026-09-25

## 状态

`IMPLEMENTING`（2026-09-25 激活）

## Completed

- **T-01 激活**：建本目录（`change.md`、`checkpoint.md`、`evidence/`）；`delivery/LEDGER.md` 表行由占位行改为本 CHG 行；`python3 scripts/prepare_ai_workspace.py --change CHG-20260925-064` 重生成 `.ai/CURRENT_CONTEXT.md`。两门禁 `exit=0`；LEDGER 表行与 `change.md` 的标题／状态／仓库**逐字一致**（`verify_product_master_alignment.py:306-311`）；§7 为字面 `None.`（`:300`）。开工三仓工作区基线已记入 `change.md` §11。

## Current

- T-01 已落，下一步进入 T-02（承接两处未入账工作区编辑）。

## Next

1. **T-02**：把 `M CLAUDE.md`（`/doctor` 瘦身）与 `M conventions:33` 作为一次独立提交入库 → `git show --stat` 证明只含这两个文件 → 六门禁复测。
2. **T-03**：`conventions` 精简保留（按 `change.md` §8.1 逐节处置、重编节号、同步 `AGENT-INDEX.md:198` 与 `verify_m0_config.py:249` 两处节号引用）。
3. **T-04**：读取顺序单一化（收敛到 `AGENT-INDEX.md` §4）＋ 两个入口文件只留指针 ＋ 补回两条被削薄弄丢的提交约定。
4. **T-05 → T-06 → T-07**：状态词汇成文 → 脚本／模板／checkpoint 落点对齐（含新判据的变异对照）→ `planned` 记录状态词就地改写。
5. **T-08／T-09／T-10／T-11**（相互独立，可换序）：FFmpeg 归属／里程碑与交付事实／目录树与死指针／前端源码根与视觉规范合并。
6. **T-12**：归档、LEDGER 同步、快照重生成、两遍失效指针扫描。

## Blocked

- None.

## Recent verification

| 判据 | 读数 |
|---|---|
| `verify_delivery_governance.py` | `exit=0`，`Active CHG: CHG-20260925-064` |
| `verify_agent_entry.py` | `exit=0`，`0 warning(s)`，快照 **1916 字符**（预算 8000） |
| `verify_skills.py` | `exit=0`，`verified 10 skill source files` |
| `verify_m0_config.py` | `exit=0` |
| `verify_product_master_alignment.py` | `exit=0` |
| `verify_m2_acceptance.py` | `exit=0` |
| `python3 -m unittest discover -s tests -q` | `Ran 75 tests` / `OK` |

取数时间 2026-09-25 19:36:11 CST，原始输出 `evidence/artifacts/t01-gate-readings.out`；逐条明细与口径说明见 `evidence/task-01-activate.md`。
