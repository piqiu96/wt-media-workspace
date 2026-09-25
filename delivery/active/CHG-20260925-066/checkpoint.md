# Checkpoint: CHG-20260925-066

- CHG: `CHG-20260925-066`（归档边界冻结与纯过程产物清理）
- Level: S
- Updated: 2026-09-25

## 状态

`IMPLEMENTING`（2026-09-25 激活；仅 `wt-media-workspace` 一仓）

State words come from §3 of `delivery/MASTER_IMPLEMENTATION_PLAN.md`. A record in
`delivery/active/` may only be `IMPLEMENTING` or `VERIFYING`.

## Completed

- **T-01 激活**：`delivery/active/CHG-20260925-066/` 三件齐备（`change.md`／`checkpoint.md`／`evidence/`）；§5 范围封闭；LEDGER 表行；`MASTER` §3 读数列按 §4 的 F-05 实测刷新（归档记录 39 → **40**、归档 `DONE` 29 → **30**、归档列 31 → **32**、活跃 `IMPLEMENTING` 0 → **1**、`active/` 0 → **1** 篇、活记录 19 → **20**）；快照 `--change`；四仓基线落 `artifacts/t01-repo-baseline.out`。逐词比对 15 项全部相等（`artifacts/t01-status-words.out`，量法调门禁自己的 `status_word()`）。
- **T-01 附带处置两处实测发现**：①**F-07 证毕**——`completed/` 整目录移走后六门禁与套件读数与移走前逐字相同（两臂 `exit=0` / `Ran 94 OK`），故改 `change.md` §4 F-07 的措辞为「没有门禁因它的存在而改变结论」，**不主张**「从不读取」；②**记录成本界第二次越界并如实登记**——T-01 的 `change.md` 增量 **16,605 B** 对界 5,120 B，越界 3.2 倍，成因是激活 Task 一次性写完整份计划（`change.md` 此后只增补），已登记为 §14 第 4 项，**界不改**。

## Current

T-01 已完成并提交；下一项是 T-02（边界成文 ＋ 实测可删量）。

## Next

1. **T-02**：`delivery/completed/README.md`（新建，边界唯一落点）＋ `AGENT-INDEX.md` §8 ＋ `MASTER:132` ＋ `README.md:51` 消歧；并**逐类实测**可删量并落痕（分母＝ §4 F-01 的 698 文件 / 10,736,581 B）。判据串**先写后实现**。
2. **T-03**：`scripts/verify_m3_acceptance.py` 的写入面移出归档。范围以 §4 F-03 的表为准（`:304`／`:310`／`:1739` 的 mkdir、`:306`／`:311` 的 state 与 manifest、**`:376` 的 `proc-<component>.log`**、`:522-523` 的基线快照、`:1059` 的 scheduler 日志），不只移 `state.json`。
3. **T-04**：`verify_delivery_governance.py` 加 `check_archive_readonly`（ERROR）与 `check_completed_has_boundary`（ERROR），各做**变异对照**（`ImportError` 计数须为 0）。
4. **T-05**：按 T-02 清单删纯过程产物；**排除**全部 PNG 与 CHG-052 的 `m3-e3-acceptance-20260923/` 包。
5. **T-06**：归档、LEDGER 同步、快照 `--no-active`、两遍失效指针扫描。

## Blocked

- None.

## Recent verification

| 判据 | 读数 |
|---|---|
| 六门禁（激活前，无活动 CHG） | 全部 `exit=0`；见 `artifacts/t01-gate-before.out` |
| 六门禁（激活后） | 全部 `exit=0`，`Active CHG: CHG-20260925-066`；见 `artifacts/t01-gate-after.out` |
| `unittest discover -s tests -q`（激活前／后） | 两臂皆 `Ran 94 tests` / `OK` |
| `sync_skills.py check`（激活前／后） | 两臂皆 `exit=0` |
| `MASTER` §3 读数列 vs 实测 | 15 项逐词全等；活列 20＝20、归档列 40＝40（`artifacts/t01-status-words.out`） |
| F-07：`completed/` 移走 vs 在树 | 两臂六门禁与套件读数逐字相同（`artifacts/t01-f07-completed-moved.out`） |
| 四仓工作树（激活前） | workspace／agent／desktop 干净；cloud 只有未跟踪的 `dump.rdb`（他人在途产物，不碰） |
| 归档体量（删除决策的分母） | 698 文件 / `10,736,581 B`；按类分解见 `change.md` §4 F-01 |
| `completed/` 曾被删除的提交数 | `0`（同一命令对 `docs/` 为 `3`，阳性对照） |
| 本 Task 记录体量 | **`change.md` 越界**（界 5,120 B／Task）；三个量的收尾读数见 `artifacts/t01-record-size.out`——**不在此内联**，本表的字节数会随写入而改变 |

读数取在**最后一次内容改动之后**；原始输出在 `evidence/artifacts/`。
