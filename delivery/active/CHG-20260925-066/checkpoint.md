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

- **T-02 边界成文 ＋ 可删量实测**：`delivery/completed/README.md` 新建（含机读键 `- 归档边界：\`READ-ONLY\``）；`AGENT-INDEX.md` §8／`MASTER:132`／`README.md:51` 三处消歧并各指唯一落点；判据串**先写后实现**（evidence §1）。**可删量实测只有 42 files / 140,556 B ＝ 1.3%**——删除不是本 CHG 的收益，价值全在边界与写入者；用户据此裁定 D-05（删 1.3%、不碰 CHG-052 包）。两处方法学自纠已登记（粗读/细读差 1 文件；F-01 的 74.1% 是拼装的，实测 74.4%）。

- **T-03 修掉唯一的写入者**：`scripts/verify_m3_acceptance.py` 的**读写两侧一并**移出归档（读点逐条核验后全部读的是本轮产物，§5 的条件不成立），产物改落 `.cache/m3-acceptance/`；P10 缺输入即 `BLOCKED` 而不回退读归档。三层判据：字面量 **0/1810**（阳性对照 2/1798）、19 个写点逐个归属**0 处写归档**、运行三读数（699/699、字节全等、`find -newer` **0**）＋ 影子树两臂对照（旧版写进归档 **2** 文件且 `.cache/` 不存在）。附带删掉 `own_artifacts` 里那个**从未存在过**的 `scripts/m3-acceptance.sh`（CHG-055:91 早已登记为未处理）。两处新实测：**归档区 15.6% 的字节不在版本控制内**（F-08）、**P10 从来不是可重跑的阶段**（F-09）。记录成本两处越界（+12%／+9.5%），已照报。

## Current

T-03 已完成（未提交）；下一项是 T-04（加两条 ERROR 门禁）。

## Next

1. **T-04**：`verify_delivery_governance.py` 加 `check_archive_readonly`（ERROR）与 `check_completed_has_boundary`（ERROR），各做**变异对照**（`ImportError` 计数须为 0）。判据**锚在字符串字面量上**、不锚接收者变量名，且必须真的做「流向写操作」一步——T-03 已把两侧做法与负例（`own_artifacts` 那种过滤器串）实测登记在 §14 第 11 项。
2. **T-05**：按 T-02 清单删这 42 个文件；**排除**全部 PNG、CHG-052 的 `m3-e3-acceptance-20260923/` 包、以及任何被归档 `.md` 引用的产物。注意清单里有 **2 个被忽略的 `.pyc` 与 2 个被忽略的 `.log`**——删它们时 `git diff` 是空的，**唯一记录就是那张清单**（§4 F-08）。
3. **T-06**：归档、LEDGER 同步、快照 `--no-active`、两遍失效指针扫描。

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
| T-02 可删量（分母 698 文件 / 10,736,581 B） | **42 files / 140,556 B ＝ 1.3%**；有引用须保留 158 files / 630,808 B（`artifacts/t02-deletable-measure.out`） |
| T-02 边界落点 | `completed/README.md` 机读键 1 处（阳性对照 0）；`AGENT-INDEX.md`／`MASTER` 各 1 处指针 |
| T-02 六门禁 ＋ 套件 | 全 `exit=0`／`Ran 94 OK`（`artifacts/t02-gate-readings.out`） |
| T-03 归档区写向判据 | 字面量 **0/1810**（阳性对照 2/1798）；19 个写点 **0 处**写归档 |
| T-03 跑前跑后三读数 | 文件数 699→699、字节 10740897→10740897、`find -newer` **0 个**（`artifacts/t03-write-surface.out`） |
| T-03 阳性对照（旧版，基线 `05c2045`） | 影子树归档 0→**2** 文件、`find -newer` **2 个**、`.cache/` 不存在 ⇒ 判据有判别力且**缺陷真实存在过** |
| T-03 归档区跟踪面 | 已跟踪 **687** ＋ 被忽略 **12** ＝ 文件系统 **699**（三个分母闭合，F-08） |
| T-03 记录体量 | `change.md` ＋5,740 B（界 5,120，**越界 +12%**）；本 Task evidence ＋10,095 B（界 9,216，**越界 +9.5%**）；见 `artifacts/t03-record-size.out` |
| T-03 六门禁 ＋ 套件 | 全 `exit=0`／`Ran 94 OK`（`artifacts/t03-gate-readings.out`） |

读数取在**最后一次内容改动之后**；原始输出在 `evidence/artifacts/`。
