# T-10 evidence — 目录树、死指针、执行根入口描述

日期：2026-09-25
Task：T-10（独立，无前置）
判据（AC-07）：`verifying/` 不再是任何目录树的条目；树的每个条目都存在；`根 \`AGENTS.md\`` → 0

原始输出：`artifacts/t10-verifying-and-entry-sweep.out`、`artifacts/t10-dead-pointer-sweep.out`、`artifacts/t10-tree-entry-check.out`（脚本 `artifacts/t10-tree-entries-check.py`）。

## 1. 改动面（`git diff --stat` 原样）

```
 AGENT-INDEX.md                                     |  2 +-
 README.md                                          |  2 +-
 delivery/MASTER_IMPLEMENTATION_PLAN.md             |  4 +-
 docs/README.md                                     |  2 +-
 docs/decisions/0007-visual-engineering-baseline.md |  2 +-
 ...\206\345\261\202\350\256\276\350\256\241_V1.md" | 60 ++++++++--------------
 docs/product/README.md                             |  2 +-
 7 files changed, 28 insertions(+), 46 deletions(-)
```

（`numstat`：架构文档 `+21/-39`，其余六个文件各 `+1/-1`，`MASTER` `+2/-2`。）

## 2. 计划落点 vs 实际落点

| 计划写的 | 实际 | 说明 |
|---|---|---|
| `MASTER:28` 删 `verifying/` + 补 `tests/` | 实测 `verifying/` 在 `MASTER:54`（`delivery/` 子项末行），`tests/` 补在 `:61` | 行号随 T-05／T-07 位移，落点本身一致 |
| `arch:1964` 删 `verifying/`；`:1988` 的 `tests/` **不动** | `verifying/` 在 A.2 的 `delivery/` 块末行；`tests/` 本就存在 | 一致；`:1988` 那条确认无需动 |
| `0007:9` 删 `docs/视觉/…` 半句 | 一致 | 半句连同 `(also mirrored at …)` 一起收敛为唯一的 `docs/engineering/specs/web-desktop-visual-system.md` |
| `conventions:18-20` 就地改写 | **本条已是 verify-only**：T-03 已把它改成「父层**不承载**入口文件…」 | 计划写这条时还没跑 T-03；T-03 落地后本 Task 只复测，未再改该文件 |
| 架构文档 `:422-423,452,725,765-766,781-782,1934-1935` 7 处 | 逐处确认并改写（§3.1 树、§3.2 承载清单、§3.10 启动流程、§3.12 标题与正文、A.1 树） | 行号位移，落点数一致 |
| `docs/README.md:14`、`docs/product/README.md:9` 改指 workspace `docs/` | 一致 | 见 §4 |

**两处计划外落点（本 Task 自己扫出来的，如实登记）**：`README.md:48` 与 `AGENT-INDEX.md:58` 同样写着反引号包裹的 `` `../docs` ``（＝执行根的 `docs/`，实测不存在）。它们是同一类死指针，与计划点名的 `docs/README.md:14` 逐字同义。**一并就地改写**——不然本 Task 就要在「修死指针」的提交里留下两条同类未修的死指针。判据 P1 的阳性对照（读 `HEAD`）报出 3 处，正是这三处。

## 3. 判据 A：`verifying/`（原始输出 §A）

| 口径 | 分母 | 命中 |
|---|---|---|
| 全仓 | `git ls-files` = **793** 文件 | **7** |
| 活文件（排除 `delivery/completed/`、`delivery/reports/`） | **200** 文件 | **6** |
| 再剔除本 CHG 自身记录 | 200 文件 | **0** |

7 条 = 历史归档 1（`completed/CHG-20260925-063/change.md:264` 的 G-9 叙述）+ 本 CHG 自身记录 6（`change.md` 5 处、`task-04` evidence 1 处），**全部是「这个条目不存在」的记述本身**。

⇒ 计划的判据写的是「只余历史归档」。实测是「历史归档 1 + 本记录自述 6」，**不是只有历史归档**。差别不掩盖：本记录自述的 6 条会在 T-12 归档后一起落进 `completed/`，届时按归档后口径重跑。

**阳性对照**：同一 `git grep` 读 `HEAD` 的同一批文件，报出 2 处（`MASTER:54`、`arch A.2` 各 1 条 `│   └── verifying/`）⇒ 工作区那两棵树的 0 不是空转。

## 4. 判据 C：死指针（原始输出 §P1/P2/P3）

**第一遍的模式抄错了，这里如实留证**：我先用 `\.\./docs` 去扫，得到 9 条命中——但其中 8 条是 `delivery/*` 指向**本仓自己** `docs/` 的合法相对链接 `../../docs/product/…`，与执行根的 `../docs` 无关。**该模式对目标没有判别力**（记进 `archive-sweep-*` 那条教训：模式对不上就是空转）。改用反引号包裹的字面量后才有下面的读数。

| 模式 | 工作区 | 阳性对照（读 `HEAD`） | 处置 |
|---|---:|---:|---|
| `` `../docs` ``（反引号字面） | **0** | **3**（`README.md:48`、`AGENT-INDEX.md:58`、`docs/README.md:14`） | 三处全部就地改写 |
| `垃圾桶` | **0** | **1**（`docs/product/README.md:9`） | 就地改写 |
| `docs/视觉` | **2** | **3** | 改前 3 处中 `0007:9` 已改；余下 2 处是本 CHG 记录与 2026-07 历史归档的**过去时叙述**，判留 |

目标路径存在性（同一脚本、两种结果都出现，不存在不是空转）：

```
ABSENT  docs/视觉
ABSENT  ../docs                              （执行根的 docs/）
EXISTS  docs/superpowers
EXISTS  docs/engineering/specs/web-desktop-visual-system.md
```

**逐处处置**：

| 落点 | 改后 |
|---|---|
| `docs/decisions/0007:9` | `A comprehensive visual proposal exists at \`docs/engineering/specs/web-desktop-visual-system.md\`.`（删掉死路径那一份，只留存活件） |
| `docs/README.md:14` | `This tree is the only documentation location. The execution root \`wt-media/\` carries no \`docs/\` directory of its own, so there is no second copy to fall back to: when a document here is wrong or stale, fix it here.` |
| `docs/product/README.md:9` | `- Do not keep a legacy PRD copy outside this tree: the PRD lives under \`prd/\` below, and the execution root \`wt-media/\` carries no \`docs/\` directory of its own.`（原句禁的是 `../docs/prd/**/垃圾桶/**`，而 `垃圾桶` 全仓 0 命中、无此目录——规则的对象已不存在，故改写为指向真实位置的同类禁令，**不是删规则**） |
| `README.md:48` | `- Do not use a \`docs/\` tree outside this repository as the source of truth for new implementation decisions; the execution root \`wt-media/\` carries none.` |
| `AGENT-INDEX.md:58` | 删掉「执行根 `../docs`」这一项，补一句「执行根 `wt-media/` 不承载 `docs/`，不存在第二份文档树。」 |

## 5. 判据 B：执行根入口文件描述（原始输出 §B）

架构文档有 **7 处**（含 `A.1`）断言执行根承载自动生成的入口文件；实测这四样里只有一样在：

| 文件 | 执行根 | cloud | agent | desktop | workspace |
|---|---:|---:|---:|---:|---:|
| `AGENTS.md` | **无** | 有 | 有 | 有 | 有 |
| `CLAUDE.md` | **无** | 有 | 有 | 有 | 有 |
| `.skill-sync.lock.json` | **无** | 有 | 有 | 有 | **无** |
| `wt-media.code-workspace` | 有 | — | — | — | — |

7 处的改写要点：§3.1 树去掉三行、§3.2 承载清单改为「承载 `wt-media.code-workspace`（多根工作区定义；**它不是本仓脚本的产物**）」并补「父层**不承载**入口文件、执行快照或任何治理事实源」、§3.10 的启动流程从 5 步（含「生成根 `AGENTS.md` 和 `CLAUDE.md`」「生成 `wt-media.code-workspace`」「写入同步 Lock」「校验 Hash」）收敛为实际的两段式、§3.12 标题 `根规则与仓库规则` → `入口规则与仓库规则`、`A.1` 树去掉三行。

**三仓的树一律不动**：`arch:838/1033/1348/1983/2012/2032` 的 `.skill-sync.lock.json` 与各仓的 `AGENTS.md`/`CLAUDE.md` 是**真实存在**的（上表），属于「各代码仓库各自保存」，改动它们才是错的。

**判据**：`根 \`AGENTS.md\`` 活文件命中 **0**（分母 793 / 活文件 200）；阳性对照：同一模式读 `HEAD` 版架构文档报出 1 处（`452`）。

## 6. 判据 D：四棵目录树逐条存在性（原始输出 §D）

脚本 `t10-tree-entries-check.py` 解析 MASTER §2、arch §3.1、arch A.1、arch A.2 四棵树的每个条目，按树根选基址后逐条 `isdir`/`exists`。

| | 读数 |
|---|---|
| 声明条目 | **98**（不含树根行） |
| 模板占位跳过 | 4（`delivery/active/CHG-YYYYMMDD-NNN/…`） |
| 实际核对 | **94** |
| 缺失 | **0** |
| 阳性对照（每棵树注入 1 个必然不存在的条目） | 注入 4，**全部报 MISS** |

**脚本自己先红过两次，都记下来**：首轮把根名 `wt-media/` 又拼一个斜杠，四棵树全部落进「未知根，跳过整棵树」，合计报 0——**脚本拒绝出结论而不是报 0 命中**；次轮没剥掉路径里的树根名，94 条全报 MISS，连 `wt-media-cloud` 都报缺——**同一脚本对存在的东西也报缺，说明它当时没有判别力**。修好之后才有上表。

**一处已知不对称（登记不改）**：`MASTER §2` 的 `docs/` 只列 `product`／`engineering`／`contracts`／`decisions`，未列同样存在的 `docs/superpowers/`；arch A.2 列了。AC-07 只要求「条目都存在」，不要求「存在的都列」，故本条不动它。

## 7. 机制读数：执行根入口这套机制确已终结

| 断言 | 读数 |
|---|---|
| 没有任何脚本生成/校验 `.skill-sync.lock.json` 或 `wt-media.code-workspace` | 在 `scripts/ tests/ config/ skills/ templates/`（分母 **48** 文件）中对 `skill-sync`／`code-workspace` 全文扫描：**1** 命中，且是 `scripts/m2b_local_acceptance.py:361` 一句注释里的 "a skill-sync commit"，不是读写者 ⇒ 净 0 |
| 同上阳性对照 | 同一模式读全仓：**14** 命中（架构文档自己的树、`conventions:21`、本 CHG 记录）⇒ 模式能报出 |
| 快照是否受本次改动影响 | 重跑 `prepare_ai_workspace.py --change CHG-20260925-064`：**只有 `Generated:` 时间戳一行不同**，正文逐字相同；已 `git checkout` 还原，故本 Task 未把时间戳噪声带进提交 |

## 8. 新增遗留（只登记，写进 `change.md` §14）

1. **`wt-media.code-workspace` 没有生成器**：架构文档 §3.2 现在明写「它不是本仓脚本的产物」，但全仓也没有任何脚本产生它——它是一份**无源的手工文件**，缺了没有任何检查会报。属「约定存在、无人守」。
2. **`.skill-sync.lock.json` 三仓各有一份、无人读写**：三个运行仓库各有一份，workspace 仓与执行根没有；而 `scripts/` 里没有任何代码写它或读它。§3.11 为它规定了格式（Schema 版本／修订版本／源树 Hash／两侧目录 Hash／目标仓库标识），**这份 Lock 没有任何读者**。要区分清楚：**生成副本本身**是有校验的（`sync_skills.py check` → `skill outputs are up to date`，见 §1 之外的收盘读数 `t10-gate-readings.out`），缺的只是「以 Lock 为介质的校验」。这是「格式写在文档、实现缺失」的又一例，需独立 CHG 定去留。

## 9. 未覆盖与明确不改

- **架构文档 `_V1.md` 未做全篇审计**：本 Task 只处置被点名的三类（目录树 `verifying/`、执行根入口描述、死指针）与 `A.1`/`A.2` 两棵树。全文 2000+ 行的其余陈旧点仍在 `change.md` §14 第 4 项。
- **`MASTER §2` 树未补 `docs/superpowers/`**：见 §6，属「补落点」不是「修错」，不改。
- **历史归档里的 `docs/视觉` 引用不动**：`completed/CHG-20260715-010/change.md:21` 是 2026-07 的过去时记录（同 `archive-sweep-*`：路径判修、叙述判留）。
- **`conventions` 本 Task 未改**：计划点名的那三行 T-03 已处置，本 Task 只复测（§2）。
