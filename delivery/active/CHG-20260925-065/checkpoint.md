# Checkpoint: CHG-20260925-065

- CHG: `CHG-20260925-065`（三个运行仓入口文件形态统一——双指针 + 单一正文）
- Level: S
- Updated: 2026-09-25

## 状态

`IMPLEMENTING`（2026-09-25 激活）

## Completed

- **T-01 激活**：建 `delivery/active/CHG-20260925-065/`（`change.md`、`checkpoint.md`、`evidence/`）；§5 范围**封闭**；§7 `Pending Questions` = `None.`；`LEDGER.md` 表行与归档说明；快照以 `--change CHG-20260925-065` 重生成；四仓 `git status --porcelain` 基线记入 `evidence/task-01-baseline.md`（workspace 净、agent 净、desktop 净、cloud `?? dump.rdb`——他人在途产物，88 字节、mtime 2026-09-24 17:19:16，早于本 CHG 一天，不碰不提交不清理，沿用 CHG-063/064 处置）；开工基线 `bd5df2c`。
- **为什么本 CHG 与四条 S 级先例不同**：那四条都写明「三仓只被读、不被写」，**本 CHG 会写三仓的入口文件**（仅四类入口文件，零运行时代码／配置／测试）。已在 `change.md` §1／§4／§5／§9 各落一次，收尾 T-09 逐仓对账。

## Current

T-01 已完成；下一项是 T-02。

## Next

1. **T-02 规范与落点成文**：`conventions §3` 就地改写为「入口文件形态」（角色表／must／must-not／指针预算／机读键语法／规则词判据／「重复只在生成物与其生成器之间存在」判别句）＋ §9 耦合表新增行 ＋ §11 补；`AGENT-INDEX.md` §10 表加 `DIRECTORY_MAP.md` 行、§4 补作用域句、`:193` 描述同 T-04 commit 改；`..._V1.md:1801` 就地扩写、`:769` 保留并补自洽句。验证：判据串**先写后实现**，读数带前后对照。
2. **T-03 生成器对齐**：`init-agent-entry.sh` heredoc 改双指针 ＋ 八节骨架 ＋ 新增 `DIRECTORY_MAP.md`；`:79-85` 停止手写 `.ai/CURRENT_CONTEXT.md`。
3. **T-04 门禁实现与退役**：`verify_agent_entry.py` 新六条 ＋ 退役 `check_entry_drift`；`tests/` fixture 重写为「默认合规」且断言**完整错误集合逐条相等**。
4. **T-05／T-06／T-07**：cloud／agent／desktop 四件入口文件收口（正文迁入 `AGENT-INDEX.md` 的 `## 本仓规则`），**顺序实施**，各仓独立提交。
5. **T-08**：workspace 入口文件补机读键过机检。**T-09**：收尾归档与对账。

## Blocked

- None.

## 预期中间态见红（不得静默容忍）

T-04 落地后、T-07 完成前，**三个运行仓的门禁是红的**——新检查按设计就是先对现状报错，再由 T-05～T-07 逐个收口。这是**预期内的**，但必须显式说明：CHG-20260925-063 的教训是「意料外的红会训练读者忽略这个门禁」。**T-09 不得早于 T-07**；本 CHG 不得在红的状态下归档。

## Recent verification

T-01 收尾读数（`evidence/artifacts/t01-gate-readings.out`，@ 2026-09-25T14:36:35Z）：

| 判据 | 读数 |
|---|---|
| `verify_m0_config` | `exit=0` |
| `verify_delivery_governance` | `exit=0`，`Active CHG: CHG-20260925-065` |
| `verify_agent_entry` | `exit=0`，0 warning（**尚未加新检查**，故此处 0 warning 只说明旧范围不够，见 `change.md` F-04） |
| `verify_skills` | `exit=0`，verified 10 skill source files |
| `verify_product_master_alignment` | `exit=0` |
| `verify_m2_acceptance` | `exit=0` |
| `unittest discover -s tests -q` | `Ran 79 tests` / `OK` |
| `sync_skills.py check` | `exit=0` |
| 四仓 `git status --porcelain` | workspace 净（＋本 CHG 未跟踪记录）/ cloud `?? dump.rdb` / agent 净 / desktop 净 |
| 开工基线 commit | `bd5df2c` |

**一处激活期实测（登记，不追责）**：第一版 LEDGER 表行的标题被我**缩短**为「…——双指针 + 单一正文」，而 `verify_product_master_alignment.py:311,338` 要求表行逐字等于 `change.md` H1 的标题（`expected_row = f"\| {active_change} \| {title} \| {status} \| {current_repository} \|"`）。实测报 `Ledger is not aligned with active CHG CHG-20260925-065 status 'IMPLEMENTING'`，**且 `unittest` 同时红 1 条**——即该门禁有判别力，不是装饰。改为 H1 全文后两条同时转绿。
