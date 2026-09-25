# Evidence: T-05 文档同步

- CHG: `CHG-20260925-063`
- Task: `T-05`
- Date: 2026-09-25
- Type: document
- Status: PASS
- 提交：`3204f91`

## Purpose

三处文档与实测对齐：`README.md` §Verification、`docs/engineering/specs/agent-workspace-conventions.md` §10、
`AGENT-INDEX.md` §12。其中 §12 一处**关闭 CHG-062 遗留第 2 项**。

## 逐处改动

### 1. `README.md` §Verification

| 改前 | 改后 |
|---|---|
| 一个「Known open failures」段落，列出三个脚本的红项及其成因 | **删除**，并留一句显式禁令：不要加回这一段，因为「红项一旦被写进文档就固定不动」正是它们红了数月的机制 |
| 校验清单只有 4 个脚本 | 补齐为**全部 6 个静态门禁 + unittest**；注明 `verify_m2_acceptance.py` 需三个兄弟仓在检出中 |

**顺带查出一处自身不一致**：原清单只列 4 个脚本，却在紧接着的一段里讨论**另外两个**脚本的红项——
即清单本身也漏项。补全后两段合并。

### 2. `conventions §10`

标题由「校验与已知红项」→「**校验**」。全表按 2026-09-25 实测重写：六个门禁 + 套件**全绿**
（`Ran 75 / OK`），快照字符数由 1923 更正为**实测 1919**，并给每行补上「它守什么」。
新增四节：判据稳定性分层（D-01）、候选块属于未关闭的里程碑、报「通过 / 0 命中」前必须证明检查能失败、
以及已知 WARN（仍为 0，含一处新登记的**结构性空转**，见下）。

改前本节以「已知红项」为核心，并写着「上述红项不在 Agent 入口工作范围内…在它们转绿之前，不要假定
本仓库门禁整体是绿的」——该段落已不成立，整体删除；三处计数变化的成因（云仓自己关掉 WARN 等）
压缩为要点，详细成因指向 `CHG-20260925-063` 记录本体。

### 3. `AGENT-INDEX.md` §12

原只列 `verify_agent_entry.py`，**未列真正约束 CHG 的 `verify_delivery_governance.py`**——
即 CHG-062 遗留第 2 项。现列全部校验命令（**只列命令**），并写入 D-01 分层与「先证明检查能失败」两条硬约束。

**有意只列命令、不复述状态与理由**：状态、分层表、控制方法与限制的**唯一落点仍是 conventions §10**，
此处显式写明这一点。理由是本 CHG 的诊断结论——**同一事实的多个落点会各自漂移**；把「校验命令清单」
和「校验状态」分成两个落点，是为了不让同一批判据在两个文件里各写一遍。

## 新查明并纠正一处既有诊断（本轮实测，非转述）

先前的诊断（本会话 B-6⑧ 与 G-10）说：`verify_agent_entry.py` 的 workspace 臂**结构上恒空转**，
成因是「该正则要求末段不含点号，而红线已迁到 `AGENT-INDEX.md`、那里的路径全带扩展名」。
**后半句经我自己重跑后不成立**：`AGENT-INDEX.md` 的 17 个 path token 里，**10 个可以通过**点号规则
（`docs/engineering/specs`、`delivery/active`、`claude/skills` 等都是无点号的目录路径），只有 7 个不行
（`config/repository-map.yaml`、`ai/CURRENT_CONTEXT.md`、`LEDGER/active` 等）。

**结构恒空转这一结论仍然成立，但机制要说准**：`check_entry_drift` 只从各仓 **`AGENTS.md`** 取禁止词，
**根本不读 `AGENT-INDEX.md`**；而本仓 `AGENTS.md` 现为薄入口，其仅有的两条禁止句带的是
**含扩展名**的路径，两条都被点号规则滤掉 ⇒ forbidden 集合恒为空集。

逐条实测（`python3` 直调该模块，我自己跑的）：

```
workspace  forbidden=0  described=3  cross=0     <- forbidden 为空集，0 是结构性的
cloud      forbidden=6  described=7  cross=0
desktop    forbidden=2  described=1  cross=0
agent      forbidden=0  described=0  cross=0
```

（`described` 是**工作区读数**，含尚未提交的 `/doctor` 编辑，故只在此登记、不写入文档。）

**未修该脚本**（属独立 CHG，见 `change.md` §14），只在 §10 的 WARN 段与 §14 如实登记，
并写明「本仓的 0 是结构性的，不是无漂移的证据」。**记这一条的目的**：避免 §10 把一个结构性空转
记成一个干净的绿——那正是本节旧版本犯过的同一类错。

## Method

```bash
for s in verify_delivery_governance verify_agent_entry verify_skills \
         verify_product_master_alignment verify_m2_acceptance verify_m0_config; do
  python3 -B -X pycache_prefix=/tmp/pyc-none scripts/$s.py
done
python3 -B -X pycache_prefix=/tmp/pyc-none -m unittest discover -s tests -q
```

读数：六个门禁全部 `exit=0`；套件 `Ran 75 / OK`（`artifacts/t05-gate-readings.out`）。

## 引用解析（AC-13 的两遍扫描）

**第一遍：字符串扫描**——三份文档已无「Known open failures / 已知红项」这类**现行**断言。
唯一命中在 conventions §10，是**描述该机制的历史叙述**（"本节的旧版本曾以「已知红项」为核心"），
属应当保留的叙述，非指称。**阳性对照**：同一模式在该文件另有 4 处「已知」命中 ⇒ 扫描确实能命中。

**第二遍：相对引用 resolve**——把三份文档的全部 inline-code 引用**按形态分类**后逐条解析：

| 形态 | 原始 | 去重 | 处理 |
|---|---|---|---|
| link 形态（首段是仓内顶层目录 + 有扩展名） | 68 | **46** | **逐条 resolve，0 条指不到东西** |
| 散名（`main.rs`、`verify_agent_entry.py` 等散文用名） | 99 | 25 | 非路径，不解析 |
| 兄弟仓路径（`wt-media-cloud/...`） | 73 | 64 | 基点不在本仓，不解析 |
| 其他（命令、占位符等） | 82 | 69 | 不解析 |

46 条里 3 条报「未命中」，逐条核对后**全部是占位符**（`delivery/active/<change-id>/change.md`、
`skills/<group>/<name>/SKILL.md`），不是缺失文件。**阳性对照**：把一个确实不存在的路径喂给同一解析器，
它报 `False` ⇒ 解析器能报出缺失，故「0 条指不到」不是空转。

### 一处自我纠正（登记）

**首版分类器把 27 个散名误判为链接**并全部报「MISS」——因为我把「含 `/` 或含点号的 inline-code」
一律当成仓根相对路径，于是 `compatibility.go`、`verify_agent_entry.py`、`wt-media-workspace/.ai/...`
这类**散文用名**全被算成待解析的链接。修正是改为按「首段是否为仓内顶层目录」判定，
并显式分出散名 / 兄弟仓 / 其他三类。**这是同一类错的第五次**：判据自己写错时，输出看起来同样「像量过的」——
27 条 MISS 里 27 条都是分类错误。故本文件的每个计数都附了分分母。

## 与「不提交他人工作区改动」的处置（值得单列）

`docs/engineering/specs/agent-workspace-conventions.md` 开工前**已有一处未提交的 `/doctor` 编辑**
（第 33 行，`CLAUDE.md` 的角色描述随同文件瘦身而更新）。本任务要改的正是同一个文件，
而 `/doctor` 的规则要求那处编辑**由用户自行在 `git diff` 中审阅、不由我提交**。

处置：先保存完整工作副本，把该行**临时还原为 HEAD 文本**，确认 `git diff` 只剩本任务的改动后
`git add` 并提交，**再把该行改回**。核对读数：

- 提交前 `git diff --stat` 该文件 = `2 +-`（1 增 1 删，仅本任务改动），全文不含该 doctor 行；
- `git show HEAD:<file> | grep -c '权威源与最小硬约束'` = **2**（均为原有行：`:11`、`:32`）；
- 恢复后工作区同模式计数 = **3** ⇒ 该行已回到工作区、且**未进入任何提交**。
