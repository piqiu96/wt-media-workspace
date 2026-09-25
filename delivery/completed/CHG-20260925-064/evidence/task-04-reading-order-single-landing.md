# T-04 evidence — 读取顺序单一化、入口文件只留指针、补回两条提交约定

日期：2026-09-25
Task：T-04（依赖 T-03）
提交：见本 Task 的独立 commit

## 1. 改前的落点数（C1 的实测）

读取顺序在改前有 **5 个文本落点 + 1 个代码常量**，且其中三个互相不一致：

| # | 落点（改前） | 内容 | 与 §4 的关系 |
|---|---|---|---|
| 1 | `AGENT-INDEX.md:7` | 「读取顺序：见 §4」 | **已经是指针**（T-03 改的） |
| 2 | `AGENT-INDEX.md:64`（§4） | 8 项清单 | 基准 |
| 3 | `AGENTS.md:16-20` | 5 项清单 | **另一套**（缺 Milestone／CHG） |
| 4 | `CLAUDE.md:22-26` | 5 项清单，措辞又不同 | **第三套** |
| 5 | `MASTER:791-796` | 6 项 Codex 专用清单，**整份不含 `AGENT-INDEX.md`**，第 1 项指向已被删除的执行根 `AGENTS.md` | **第四套** |
| 6 | `scripts/prepare_ai_workspace.py:143-149` | `reading_order` 常量（5 项 + 条件追加） | 生成物来源 |

T-03 删 `conventions` §5 时暴露了两版「第二层」不一致（`conventions` 的清单含 `LEDGER.md` 与 Milestone，`AGENT-INDEX.md` 的没有）——这正是「多落点各自漂移」的现场。

## 2. 收敛结果

| 落点 | 处置 |
|---|---|
| `AGENT-INDEX.md` §4 | **保留为唯一手写清单**；把 T-03 发现的缺口补进第 6–8 项 |
| `AGENT-INDEX.md:7` | 保持指针 |
| `AGENTS.md` / `CLAUDE.md` | 各自清单**删**，改为一句指回 §4 |
| `MASTER:791-796` | 6 项清单**删**，改为一句指回 §4 |
| `scripts/prepare_ai_workspace.py` | 常量**保留**，但显式登记为「§4 的生成物镜像」并加注释说明双向同步义务 |
| `conventions` §5 | 标题「渐进式加载」→「读取顺序」（该节本就只是指路、无清单），并在 §9 耦表**新增「读取顺序」一行**登记双向同步义务 |
| `.ai/CURRENT_CONTEXT.md` | 生成物，不改 |

净结果：**1 处手写 + 1 处生成物**。

实测（分母：全仓 tracked 文件，排除 `delivery/completed/` 与 `docs/superpowers/`；命令与输出见
`evidence/artifacts/t04-gate-readings.out` 与本文 §7）：

```
-- 形如「<序号>. `AGENTS.md`」的清单项 --
.ai/CURRENT_CONTEXT.md:19:1. `AGENTS.md`          <- 生成物
AGENT-INDEX.md:64:1. `AGENTS.md` —— …             <- 唯一手写落点
（MASTER 的第三版已于本 Task 删除；AGENTS.md / CLAUDE.md 的清单同）
```

生成物的三种形态（`build_context`：常量 5 项 + 有 Milestone 时 6 + change 路径 7 + 受影响仓行 8；
`--no-active` 为 5）**全部是 §4 那 8 项的子集**，逐项对上：

| §4 项 | 生成物形态 |
|---|---|
| 1–5 | 常量（`--no-active` 的 5 项） |
| 6 | 有 Milestone 时的第 6 项 |
| 7 | change 路径 |
| 8 | 受影响仓 `AGENT-INDEX.md`/`AGENTS.md`/`CLAUDE.md`/`DIRECTORY_MAP.md` 行 |

当前 CHG 为 Level S（无 Milestone），快照实际渲染 **7 项**——与上表一致。

## 3. 生成物的归属是**被证明**的，不是被假定的（变异对照）

把常量第 1 项 `AGENTS.md` 改为探针串 `ZZ-PROBE.md`，重生成快照：

```
3c3
< - Generated: 2026-09-25T11:43:45Z
---
> - Generated: 2026-09-25T11:46:23Z
19c19
< 1. `AGENTS.md`
---
> 1. `ZZ-PROBE.md`
```

正好 2 行不同（时间戳 + 第 1 项）。还原常量后重生成：**只剩时间戳 1 行不同**，且
`cmp` 证明 `scripts/prepare_ai_workspace.py` 与变异前逐字节相同。
即：快照的读取顺序**确由该常量派生**；变异若无效（第 1 项不变）就说明注释在说谎。

> 说明：上面 `diff` 的退出码读数不可信（`| sed` 吞掉了 `$?`，打印的是 `sed` 的状态）。
> 判据是 **diff 正文的差异行数与内容**，不是那个退出码。

## 4. 入口文件删掉的红线：逐条归属（AC-02）

删了 9 条（`CLAUDE.md` 的 `## 高频红线` 4 条 + `AGENTS.md` 的 `## 最小硬约束` 5 条）。
逐条归属，落点均在 `AGENT-INDEX.md`：

| 被删条目（出处） | 承载的事实 | 落点 |
|---|---|---|
| `CLAUDE.md` 1 | 运行时改动不落本仓、本仓不得被运行时依赖 | §2:1 |
| `CLAUDE.md` 2 | `CURRENT_CONTEXT` 不手工编辑、父层不留副本 | §2:6 |
| `CLAUDE.md` 3 | 讨论／建议／假设不是需求 | §2:3 |
| `CLAUDE.md` 4 | `skills/` 唯一源、生成副本不手改 | §2:7 |
| `AGENTS.md` 1 | 治理中心、不是运行时代码仓 | §2:1、§2:2 |
| `AGENTS.md` 2 | `repository-map.yaml` 为准、不得硬编码或漂移 | §2:5 |
| `AGENTS.md` 3 | 快照由脚本生成、手工编辑无效、父层无副本 | §2:6 |
| `AGENTS.md` 4 | 讨论／建议／假设不是需求 | §2:3 |
| `AGENTS.md` 5 | 结束任务前更新 checkpoint | §9（变更规则与完成检查） |

**9/9 有落点，0 条只存在于被删处。** 阳性对照：`HEAD:AGENTS.md` 的 `最小硬约束` 命中 2 次、
`HEAD:CLAUDE.md` 的 `高频红线` 命中 1 次（证明这个扫描抓得住「复述」这件事），改后两处均为 **0**。

### 4.1 一次真实空转（登记，因为它正是本 CHG 在治的病）

第一遍归属扫描里，我用 **`CLAUDE.md` 的措辞** 当模式去 grep `AGENT-INDEX.md`：

```
AGENT-INDEX hits=0   运行时改动不落在本仓库，本仓库也不得被运行时依赖
AGENT-INDEX hits=0   不手工编辑，执行根父层不留副本
```

两条「0 命中」看着像「事实没了」。**是模式错了**：§2 的原文是「运行时改动**只在对应工程仓库执行**」
与「**禁止**手工编辑，执行根父层**不得出现**副本」。按 §2 的措辞重扫，两条均命中 1。
这与 T-03 的 `降级条款` 是同一形态（`conventions §10`）：**模式对不上就是空转，0 命中的分母必须配阳性对照。**

## 5. 两条提交约定的回迁（AC-03）

T-02 以外科式提交承接的 `CLAUDE.md` 瘦身删掉了 `## 提交约定`，块内三条实测：

| 约定 | `0de87e8:CLAUDE.md` | `HEAD:CLAUDE.md` | 回迁后活落点 |
|---|---|---|---|
| Conventional Commits `<type>(<scope>): <subject>` | 1 | **0** | `AGENT-INDEX.md:143` |
| 纯移动／重命名与改逻辑不同 commit | 1 | **0** | `AGENT-INDEX.md:144` |
| 一仓一 commit | 1 | **0** | `AGENT-INDEX.md:145`（并交叉引用 skill） |

三条都在 `AGENT-INDEX.md` §9「提交纪律」下补齐；第 3 条在 `skills/workspace/executing-wt-media-change/SKILL.md`
本有等价落点，故写成交叉引用而非重复正文。分母＝活文件（排除 `delivery/completed`、`delivery/active`、
`docs/superpowers`）；阳性对照＝`0de87e8:CLAUDE.md` 三条各命中 1，证明模式咬得住、`HEAD` 的 0 是真 0。

## 6. 偏离与自我更正

1. **`MASTER:66` 的残余词汇（本 Task 内自捕）**：`MASTER` 目录树里 `AGENT-INDEX.md  # 跨仓库路由与渐进式加载规则`
   仍是 T-03/T-04 退休的词。本 Task 只改这一个词（→「跨仓库路由与治理规范正文（唯一权威源）」）；
   该树的其余问题（`verifying/` 条目、缺 `tests/`）仍属 T-10。
   *若不改，§5 的「渐进式加载」就还有一个指向未被定义的术语的活落点。*
2. **我自己引入过一个漂移通道并当场拆掉**：两个入口文件的 `## 红线` 初稿写了「红线共 **8 条**」——
   一个会静默过期的可数事实，恰是本 CHG 在治的失败类。已改写为不含计数的指路句。
   （因此本文将 8 条作为 §2 的实测读数报出，而不是写进入口文件。）
3. **`MASTER` 的第三版清单删除后行数变化**归入本 Task 提交（见 §8 提交边界）。

## 7. 未覆盖 / 未决

- `根 \`AGENTS.md\`` 的死指针在 `docs/engineering/architecture/…_V1.md:452` 仍存在——**T-10 的落点**（该文件另有 6 处同族描述）。
- 本次扫描的**分母**是 tracked 文件；`docs/superpowers/` 与 `delivery/completed/` 未扫（历史材料，`AGENT-INDEX.md` §3 已声明不作新开发依据）。
- `AGENT-INDEX.md` §4 的 8 项**没有机检点**（`conventions` §9 耦表已如实登记「入口文件与 `MASTER` 不得再列清单」靠人工复核）——**新增机检点不在本 Task 范围**，如需须独立裁定。
- `.ai/CURRENT_CONTEXT.md` 的时间戳每次重生成都变，故「改动 diff 只有 2 行（时间戳 + 第 7 项）」这一读数只在同一生成周期内可比。

## 8. 提交边界

一个 commit，含：`AGENT-INDEX.md`、`AGENTS.md`、`CLAUDE.md`、`delivery/MASTER_IMPLEMENTATION_PLAN.md`、
`docs/engineering/specs/agent-workspace-conventions.md`、`scripts/prepare_ai_workspace.py`、
`.ai/CURRENT_CONTEXT.md`（生成物）、本 CHG 的 `change.md`／`checkpoint.md`／`evidence/`。三仓零写。

`conventions` 的改动（§5 改名 + §9 耦表新增一行）与 `AGENT-INDEX.md` §4 的改动是同一次收敛的两半，
拆开提交会让任一半单独看起来无因——故合并于本 commit。

## 9. 门禁读数

见 `evidence/artifacts/t04-gate-readings.out`（在**本 Task 最后一次改动之后**重跑）。
