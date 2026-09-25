# Checkpoint: CHG-20260925-064

- CHG: `CHG-20260925-064`（权威冲突与重复落点处置——按单一落点收口）
- Level: S ／ 仅 `wt-media-workspace` 一仓
- Updated: 2026-09-25

## 状态

`IMPLEMENTING`（2026-09-25 激活）

## Completed

- **T-01 激活**：建本目录（`change.md`、`checkpoint.md`、`evidence/`）；`delivery/LEDGER.md` 表行由占位行改为本 CHG 行；`python3 scripts/prepare_ai_workspace.py --change CHG-20260925-064` 重生成 `.ai/CURRENT_CONTEXT.md`。两门禁 `exit=0`；LEDGER 表行与 `change.md` 的标题／状态／仓库**逐字一致**（`verify_product_master_alignment.py:306-311`）；§7 为字面 `None.`（`:300`）。开工三仓工作区基线已记入 `change.md` §11。
- **T-02 承接工作区编辑**：`M CLAUDE.md`（`/doctor` 瘦身 1 插入 / 55 删除）与 `M conventions:33` 作为一次独立提交入库（`9e9bf39`，只含这两个文件）。三态量测证明这批改动**不是** CHG-062 承接的那次入口重构。净代价：两条提交约定活落点归零，交 T-04 补回。
- **T-03 `conventions` 精简保留**：按用户 2026-09-25 裁定的**保留清单**（保 §1、§7 配置规则、§8、§9、§10 判据、§11）删掉一次性读数与历史叙述：**208 → 148 行、18541 → 14233 字节、节数 11 → 11**。6 类读数／叙述模式（含 `0/8/0`、`Ran 75 / OK`、`1919 字符`）改前 1–7 命中、改后全 0（阳性对照见 evidence §2）；保留下来的规则句与 §9 的 8 个实现落点逐条在位。两处活引用者逐个复核：`AGENT-INDEX.md:198` 改（「校验读数不作文档落点」），`verify_m0_config.py:249` **不改**（节号未变、其断言仍成立）。

- **T-04 读取顺序单一化**：读取顺序由 **5 处手写清单 + 1 个代码常量**（其中 3 处内容互不相同，`MASTER` 那版整份不含 `AGENT-INDEX.md`、第 1 项指向已删的执行根 `AGENTS.md`）收敛为 **1 处手写（`AGENT-INDEX.md` §4）＋ 1 处生成物**。§4 补齐第 6–8 项（T-03 发现的两版「第二层」不一致按 `AGENT-INDEX.md` 为准）；`AGENTS.md` 30→22 行、`CLAUDE.md` 37→28 行（删各自复述的红线与清单，只留指针）；`MASTER:791-796` 6 项清单删为 1 行；`MASTER:66` 的退休词「渐进式加载」就地改写；生成器常量加注释登记为「§4 的生成物镜像」。**变异对照**：常量第 1 项改探针 → 快照正好 2 行不同（时间戳＋第 1 项），还原后只剩时间戳且生成器逐字节相同。**入口红线 9/9 逐条归属**（删掉的 4+5 条全部在 `AGENT-INDEX.md` §2／§9 有落点，阳性对照：`HEAD` 两文件对应小节各命中 1–2）。**两条提交约定回迁**至 `AGENT-INDEX.md` §9「提交纪律」（改前活落点 0，阳性对照 `0de87e8:CLAUDE.md` 各命中 1）。

## Current

- T-04 已落。下一个是 T-05（状态词汇成文）。

## Next

1. **T-05**：把 `MASTER:105-128` 的两套词汇就地覆盖为**实测在用**词汇（分母＝`delivery/planned`＋`active` 的 `Status:` 字段，逐文件提取），并一行声明历史词汇。
2. **T-06**：`verify_product_master_alignment.py:290` 接受集与 `:292` 文案、`templates/delivery/change.md:6` 与 §12、**新增 `templates/delivery/checkpoint.md`**、skill 措辞、**新增「active 目录必须有 `checkpoint.md`」结构检查（带变异对照）**——须在本 CHG 仍 active 时复测（改接受集会打到自己的 LEDGER 表行）。
3. **T-07**：`delivery/planned/*` 的 `Status:` 行就地改写。
4. **T-08／T-09／T-10／T-11**（相互独立，可换序）：FFmpeg 归属／里程碑与交付事实／目录树与死指针／前端源码根与视觉规范合并。
5. **T-12**：归档、LEDGER 同步、快照重生成、两遍失效指针扫描。

## Blocked

- None.

## Recent verification

| 判据 | 读数 |
|---|---|
| `verify_delivery_governance.py` | `exit=0`，`Active CHG: CHG-20260925-064` |
| `verify_agent_entry.py` | `exit=0`，`0 warning(s)`，快照 **1936 字符**（预算 8000；`wc -c` 是 1978 字节——门禁按**字符**判） |
| `verify_skills.py` | `exit=0`，`verified 10 skill source files` |
| `verify_m0_config.py` | `exit=0` |
| `verify_product_master_alignment.py` | `exit=0` |
| `verify_m2_acceptance.py` | `exit=0` |
| `python3 -m unittest discover -s tests -q` | `Ran 75 tests` / `OK`，`exit=0` |
| 三仓工作区基线（AC-15） | `cloud` `?? dump.rdb`；`agent`、`desktop` 空——与 T-01 基线逐条一致 |

取数时间 2026-09-25 19:47:08 CST，原始输出 `evidence/artifacts/t04-gate-readings.out`；逐条明细见 `evidence/task-04-reading-order-single-landing.md`。

该组读数之后本文件又改动过一次。**这不影响它成立**，且此判断是证过的：`git grep -l 'checkpoint' -- scripts tests` 命中 **0** 个文件（同一扫描对 `change.md` 命中 9 个，构成阳性对照）⇒ 没有任何门禁解析 `checkpoint.md`。这也正是 T-06 要补的那条结构检查所针对的缺口。
