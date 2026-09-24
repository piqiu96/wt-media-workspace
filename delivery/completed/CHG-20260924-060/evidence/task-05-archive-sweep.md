# T-05 收尾：归档与失效指针扫描

本文件记录 T-05 的文档回写、归档动作与**主动**失效指针扫描。扫描是这次归档的验收项之一
（计划原文：「修掉归档连带产生的失效指针（**这次要主动扫**）」），故必须先定清「什么算失效指针」。

## 1. 分类规则（先定规则，再报数字）

CHG-056 归档时留下了一条可援引的先例，它把两类混在一起的东西分开了：

- 056 的 `change.md:619` 保留了 `「记录由 `delivery/active/CHG-20260923-056/` 移入 `delivery/completed/`」`
  ——**描述归档动作本身**的过去时叙述，**未修**；
- 056 同时修掉了 **5 处**「原先都指向 `delivery/active/CHG-20260923-056/`」的外部指针
  （`planned/README.md` 2 处、`planned/CHG-20260923-053/change.md`、程序总纲 2 处）。

据此本轮的判定规则：

| 形态 | 判 | 理由 |
|---|---|---|
| 读者**照着做**的路径（可重放的命令、可点开的链接） | **修** | 指不到东西就是坏指针，归档的连带责任 |
| **过去时叙述**归档动作/当时状态的路径 | **留** | 改写它等于改写历史，056 已立此例 |
| 只提 **CHG id**、不提路径（代码注释、登记表、关闭说明） | **留** | id 是全局单调标识，不随目录迁移失效 |

## 2. 扫描与阳性对照

**覆盖面（枚举，不是「我搜过了」）**：

| 范围 | 在册文件数 | 命中 `delivery/active/CHG-20260924-060` |
|---|---|---|
| `wt-media-workspace` 全仓（`*.md` `*.txt` `*.json` `*.py` `*.sh`） | **509** | 2 |
| `wt-media-desktop` | 90 | 0（1 处仅引 id） |
| `wt-media-agent` | 145 | 0 |
| `wt-media-cloud` | 485 | 0 |

**阳性对照（否定结论必须先证明检查能失败）**：

- 模式类 `delivery/active/CHG-<id>` 在本仓**可命中**：对已归档的 056 同一模式得 **3** 处
  （`completed/CHG-20260923-056/change.md` ×2、`ac05-run5.log` ×1）。故 060 的命中数是真数，不是空转。
- 运行仓的模式也可命中：`CHG-20260923-056` 在 desktop **2** 个文件、agent **2** 个文件中被引。
  故 desktop 的 1、agent/cloud 的 0 是真数。cloud 对 056 也是 0，故 cloud 的 0 佐证力较弱——
  但 cloud **不在本 CHG 的授权仓清单内**（`Affected repositories` 为 desktop/agent/workspace），
  本就不应有任何 060 痕迹，0 与预期一致。

**首次扫描的 2 处命中，逐条处置**：

1. `completed/CHG-20260924-060/evidence/task-02-csp.md:29` —— 第 3 步真实启动取证的可重放命令
   `python3 delivery/active/CHG-20260924-060/evidence/tools/t02_csp_shipped_value_launch.py`。
   属**修**类：读者照抄会 `No such file`。已改为 `delivery/completed/…`，**命令其余一字未改**，
   并在上一行加注「路径在归档后由 active/ 改为 completed/」以免被读成证据被事后重写。
   已验证：脚本在**新路径**处存在（5893 字节），且脚本自身**不含**任何 `active/` 字面量（自足，非仅路径看起来对）。
2. `completed/CHG-20260924-060/checkpoint.md:8` —— `「2026-09-24 T-01：建 `delivery/active/CHG-20260924-060/`」`。
   属**留**类（056 `:619` 同型，是 T-01 当时做了什么的事实陈述）。

**修后复扫**：同分母、同阳性对照，残留 **1** 处 = 上表第 2 条（已判定为应留）。0 处**修**类残留。

## 3. 计划预判的两处「连带引用」实测不成立（如实登记）

计划 §T-05 写：「修掉归档连带产生的失效指针（**这次要主动扫**：项 1/2/3 的裁定会被 056 的归档记录、
`planned/README.md`、程序总纲引用）」。逐项实测：

- **056 的归档记录**：已有处置去向（`change.md:630`、`:644` 的「上述四项遗留的裁定与处置（2026-09-24 追加，
  由 `CHG-20260924-060` 承接）」）。它在 T-05 前一轮就已写入，本轮**只核不改**。
- **`planned/README.md`**：`3` 处提 056 的归档、`11`～`14` 是程序 A/B/C/D 的登记表。
  **060 不在该表内、也不该在**——它是 Level-S 的遗留处置 CHG，不是联合工程优化程序的阶段。
  056 当初改 `planned/README.md`，改的是**它自己的程序行**（A 行由 PLANNED 改 DONE）；060 无对应行，
  故无行可改。其 `:3` 的「**当前无 active CHG**」在本轮归档后**仍然成立**，不构成失效指针。
- **程序总纲**（`docs/engineering/specs/2026-09-23-launch-engineering-optimization-program.md`，69 行）：
  对 `ipc|CSP|csp|no_proxy|代理|占位|modes|generated|noop_task|待裁定|遗留` 的扫描**只命中 1 行**——
  `:63` 的「代理密码」敏感信息规则，与四项裁定无关。**该文档从未涉及这三项裁定的主题**，
  故没有可被裁定结果改写的内容。（它另在 `:6`/`:44` 引 056 的 `completed/` 路径，已是归档后形态。）

结论：计划对这三处的预判**不成立**，不是「查到 0 所以没事」，而是**这些文档里本就没有相应内容**——
056 之所以要改 5 处，是因为程序链条上有文件预先指向了它的 active 路径；060 是旁支 CHG，
除记录自身外**没有任何文档曾指向它**，故连带失效面为空集。

## 4. 收尾动作与验证

- `change.md` `Status: IMPLEMENTING` → `DONE`。
- `git mv delivery/active/CHG-20260924-060 delivery/completed/CHG-20260924-060`；`delivery/active/` 复为仅 `.gitkeep`。
- `delivery/LEDGER.md`：活动表行移除，表留表头（照 `95f9487` 先例），补 060 的关闭说明段。
- 冷启动重生成快照：`prepare_ai_workspace.py --no-active`（该模式由 CHG-055 关闭时补上）。
  `verify_agent_entry.py` → `execution snapshot: 1668 characters`，`Agent entry verification ok. 0 warning(s)`；
  `verify_delivery_governance.py` → `ok. Active CHG: none`。快照 `Active CHG: none` / `Status: NONE`，
  与 `delivery/active/`、`LEDGER.md` 三者一致。
- **桌面仓的 1 处 id 引用不动**：`src-tauri/src/bootstrap.rs:259` 的
  「CHG-20260924-060 added, so it is no longer a byte-for-byte copy of that」是代码注释里的 id 说明，
  属上表第三类（引 id 不引路径），随 T-02 的提交 `9945f58` 已入库。
