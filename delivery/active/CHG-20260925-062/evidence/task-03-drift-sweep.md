# Evidence: T-03 修 `agent-workspace-conventions.md` 的三处陈旧引用

- CHG: `CHG-20260925-062`
- Task: `T-03`
- Date: 2026-09-25
- Type: command
- Status: PASS

## Purpose

证明这次入口重构在 `agent-workspace-conventions.md` 里留下的三处陈旧引用确实存在（先红），
修掉后归零，且新指向的**目标真实存在**（正向 resolve，不能只靠「旧串 0 命中」）。

## Method

先红、修、复扫，两遍判据不同：

```bash
grep -rn "第 13 节" docs/                       # 先红
grep -n "^## " AGENT-INDEX.md                   # 对照实际节号
python3 -B -X pycache_prefix=/tmp/pyc-none scripts/verify_agent_entry.py   # 取 WARN 实测
grep -rn "第 13 节" docs/                       # 复扫
grep -o '第 [0-9]* 节' docs/engineering/specs/agent-workspace-conventions.md | sort | uniq -c
```

原始输出：`artifacts/t03-red-section13.out`、`artifacts/t03-postfix-sweep.out`、
`artifacts/t03-verify_product_master_alignment*.out`。

## Expected / Actual

**① 「第 13 节」不存在。**

- 期望（先红）：`grep -rn "第 13 节" docs/` 命中 **2** 处（第 3 行、第 72 行），且 `AGENT-INDEX.md`
  里没有第 13 节。
- 实际：命中 **2** 处，逐字如下；`AGENT-INDEX.md` 实测只有 **12** 节（`grep -n "^## "`），
  `Agent 入口与执行快照` 在第 **10** 节（`:143`）。**红成立。**
  - `:3` 它补充 `AGENT-INDEX.md` 第 13 节「Agent 入口与执行快照」
  - `:72` 同步修订 `AGENT-INDEX.md` 第 8 节与第 13 节的单数措辞
- 修后复扫：**0 命中**。
- **正向 resolve**（更关键的一半）：
  - 规范里引用的是「第 10 节「Agent 入口与执行快照」」 ↔ `AGENT-INDEX.md:143 ## 10. Agent 入口与执行快照` —— 标题逐字吻合。
  - 同一句里的「第 8 节」↔ `AGENT-INDEX.md:125 ## 8. 交付治理` —— 该节确实含 CHG 创建规则，引用成立。
  - 文内残留的节号引用共 4 处：第 10 节 ×2、第 8 节 ×1（均指 `AGENT-INDEX.md`）、
    第 9 节 ×1（本文自指 §9 规则—实现耦合点登记）。**无其它悬空节号。**

**② §10 表里 `verify_agent_entry.py` 的 WARN 读数。**

- 原文写「绿（0 ERROR；1 个 WARN 为待复核项，见下）」。
- 实测：`0 warning(s) need review`。**读数与表不符，红成立。**已按实测改写。
- 成因**已查明且不是本次重构**：那条 WARN 原为云仓 `AGENTS.md` 禁止 `internal/runtime` 而
  云仓 `CLAUDE.md` 仍把它描述为资源所有者。云仓自己改了——`CLAUDE.md:31` 现为
  「禁止创建全局单例和 `internal/runtime`」，即提及落在**禁止句**内，而漂移检查的判据正是
  「禁止句里的提及不算描述」，命中因此消失。修它的是云仓提交
  `f21bbcb docs: align Cloud agent boundary with ADR-0017`。

## 主动扩大范围（如实登记）

建 CHG 时 §8 的 T-03 只列了「三处陈旧引用」，其中读数列只点了 `verify_agent_entry.py` **一行**。
执行时发现**整个 §10 校验表的计数都是过期的**，于是把 §10 从「改一行」扩为「整节按实测重写」。
理由是：在同一张表里，改掉我知道是假的一行、留下另外三行我刚测出来也是假的，正是本 CHG
要防的「静默省略」。扩大后的实测如下（四支校验器全部实跑，均为静态只读）：

| 校验 | 旧读数 | 实测（2026-09-25） |
| --- | --- | --- |
| `verify_delivery_governance.py` | 绿 | 绿 |
| `verify_agent_entry.py` | 绿（1 WARN） | 绿，**0 WARN** |
| `verify_skills.py` | 绿（10） | 绿（10） |
| `verify_m0_config.py` | 红 3 项 | 红 3 项（一致） |
| `verify_product_master_alignment.py` | 红 9 项 | **红 8 项** |
| `verify_m2_acceptance.py` | 红 1 项 | **红 5 项** |
| `unittest discover -s tests -q` | 69 项中 4 项 | **73 项中 4 项** |

三处变化的成因逐条查明，**没有一处是本次重构引入的**：

1. `verify_agent_entry.py` 1 → 0 WARN：云仓自己修的（见上）。
2. `verify_product_master_alignment.py` 9 → 8：**组成也变了**。旧读数的 9 项里含
   「active CHG 缺 current repository」与「active CHG 不得有待决问题」各 1 项——这两条
   **只在存在 active CHG 时触发**，无 active CHG 时天然不出现；旧表又把 M10 的
   `FFmpeg/FFprobe 分发` 漏计。实测 8 项 = M2/M3 状态词 2 + 候选关键词 5 + M10 1。
3. `verify_m2_acceptance.py` 1 → 5：**校验器期望值过期，非代码缺陷**。逐条查证：
   - `compatibility.go` 已移到 `.../cloudagent/service/compatibility.go`（这一条旧读数就对）。
   - `cloud_agent_contract.py` 里 `REQUIRED_CONTRACT_REVISION` 已迁出，该文件只导入再导出
     （`:10` 导入、`:18` 进 `__all__`），故没有字面量赋值可匹配。
   - `desktop/src-tauri/src/main.rs` 里 `wt-media-agent` 实测 **0 命中**——`main.rs` 已由
     CHG-056 拆为分层模块。
   - `desktop/src-tauri/src/local_agent/mod.rs` 里 `consume_binding_ticket(` 与
     `pub fn bind_session<T: BindingTransport>(` 实测各 **0 命中**——已改名或迁走。

   即：这是静态校验器以「文件内容字面量」为判据，而那些文件已被后续 CHG 合法重构。
   **本次只登记、不改**——改它属跨仓校验器维护，需独立开 CHG。

## 一处诊断顺带修正了我自己先前的一个判断

开工前我曾判断「`check_entry_drift` 的 workspace 臂因本次重构而失明」。**实测否证了它**：
逐仓复算 forbidden ∩ described，workspace 在 **HEAD 版** `AGENTS.md` 上同样是 0 命中——
这条臂在重构**之前**就是空的，不是本次造成的。该判断已在 `change.md` §4 按实测改写，
并未据此改动任何代码。**登记以免后人把它当成本次的回归。**

## Follow-Up

- `verify_m2_acceptance.py` 的 4 条过期期望（见上第 3 条）需独立 CHG 处置；本 CHG 只在
  §10 登记了它们的准确内容，未改校验器。
- `verify_m0_config.py` 的 3 项与 `verify_product_master_alignment.py` 的 8 项同样是既知红，
  不在本 CHG 范围。
