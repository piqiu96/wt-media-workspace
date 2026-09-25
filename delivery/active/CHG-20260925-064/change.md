# CHG-20260925-064: 权威冲突与重复落点处置——按单一落点收口

## 1. Basic Information

- Level: S
- Status: IMPLEMENTING
- Created: 2026-09-25
- Current repository: `wt-media-workspace`
- Affected repositories:
  - `wt-media-workspace`
- 锚点（Level S，按 CHG-20260924-060 §3、CHG-20260925-062 §3、CHG-20260925-063 §1 先例写散文，不引 Milestone）：本 CHG 处置治理仓自身的权威冲突与重复落点，**不挂任何 Milestone**——`delivery/milestones/` 下 6 篇没有一篇覆盖治理卫生（CHG-063 已实测 grep 零命中）。`verify_delivery_governance.py:119` 只对 `Level: M/L` 强制 `- Milestone:`。

三个运行仓（cloud / agent / desktop）**只被读、不被写**：本 CHG 只引用它们当前的真实形态作为事实依据（源码根、构建脚本、tauri 配置），不修改它们任何一个。

## 2. Change Goal

把「同一事实存在多个落点、且没有任何机制在其中一个改变时去改其余的」这一**机制**收口：

- 每个可收口的权威事实**只留一个落点**（读取顺序、状态词汇、前端源码根、checkpoint 位置、视觉基线、执行根入口）；
- 收不掉的落点在 `AGENT-INDEX.md` 或本记录里**明示无强制点**，不再让读者以为它受保护；
- **易失读数不再作文档落点**（读什么由实跑给出），从根上消掉「覆盖赶不上过期」这一类；
- 单篇规范按内容形态**精简**（保留规则、去掉过程叙述与一次性读数），不删文件。

## 3. Baseline References

- 权威源：`AGENT-INDEX.md`（§2 红线、§4 上下文加载、§8 交付治理、§10 入口与快照、§12 校验）
- 工程规范：`docs/engineering/specs/agent-workspace-conventions.md`
- 计划与状态：`delivery/MASTER_IMPLEMENTATION_PLAN.md`、`delivery/LEDGER.md`
- 决策：`docs/decisions/0007`、`0015`、`0017`
- 诊断来源：2026-09-25 本次会话的 `/doctor` 报告 B-6⑦（8 条权威冲突）、B-5／N3（执行根入口描述）、G-9；CHG-062 遗留第 4 项；CHG-063 §14 的 G-9 条目

## 4. Current Facts

全部为 2026-09-25 实测，逐条命令与原始输出见 §11 与 `evidence/`。

### 4.1 运行环境（本 CHG 的取数前提）

| 事实 | 读数 |
|---|---|
| 执行根 `wt-media/` 现无 `AGENTS.md`／`CLAUDE.md` | `ls -la` 两处 `No such file or directory`；内容物只有 `.agents`、`.claude`、`.codex`、`wt-media.code-workspace` + 四仓。**用户确认是其本人删除**（2026-09-25 裁定） |
| `delivery/active/` | 只有 `.gitkeep` |
| 开工工作区状态 | `M CLAUDE.md`、`M docs/engineering/specs/agent-workspace-conventions.md`（2026-09-24 入口重构期间 `/doctor` 落地、此后一直未提交）。用户裁定**不为其单独开 CHG**，由本 CHG 承接 |
| conventions 的活引用者 | **2 处**：`AGENT-INDEX.md:198`、`scripts/verify_m0_config.py:249`（docstring）。其余命中全在 `delivery/` 历史记录 |

### 4.2 冲突与重复落点的清点

| 组 | 条目 | 现状 |
|---|---|---|
| C1 | 读取顺序 | **两版并存**：`AGENT-INDEX.md:7,:64`（入口 → 正文）与 `AGENTS.md:16-20`、`CLAUDE.md:22-26`（正文 → 快照 → CHG）；`MASTER:791-796` 还有第三版（Codex 专用，**整份不含 `AGENT-INDEX.md`**，第 1 项指向已被删除的根 `AGENTS.md`） |
| C2 | FFmpeg 归属 | `docs/decisions/0015-*.md:6,:27` 判给 Agent；`0017-*.md:28,:40` 判给 Cloud（明确「均不执行视频合成」「FFmpeg 属于 Cloud 部署组件」），且 0017 的 `Supersedes` 清单**未含** FFmpeg。全仓其余落点（MASTER、架构文档、第二章、M2 里程碑）**一致判给 Cloud** |
| C3 | CHG／里程碑状态词汇 | `MASTER:105-128` 写 `TODO → IMPLEMENTED → VERIFIED → CLOSED`；`verify_product_master_alignment.py:290` 只接受 `{IN_PROGRESS, IMPLEMENTING, VERIFYING, ACTIVE}`（**两套零重叠**）；模板 `templates/delivery/change.md:6` 用 `DISCUSSION`；实测在用的还有 `PLANNED`、`SUPERSEDED`，**两者在任何权威源里都没有定义** |
| C4 | 前端源码根 | `docs/engineering/specs/web-desktop-visual-system.md` **9 处**写 `wt-media-cloud/frontend`（实测不存在），并称其为「唯一前端源码来源」；另行号 284-287、407 的 `frontend` 是 **JSON 字段名／脚本名**，不是目录名 |
| C5 | 两个入口文件的硬约束集不一致 | `AGENTS.md:27` 的 `config/repository-map.yaml` 红线在 `CLAUDE.md` 里**没有**；`CLAUDE.md:35-38` 的红线在 `AGENTS.md` 里**没有** |
| C6 | `delivery/milestones/README.md:7` | 写「E3 未开始」，与 `M3-content-discovery-v2.md:3-4`（第 1～7 项全部通过、用户已于 2026-09-23 签收、M3 转 `DONE`）**结论相反** |
| C7 | `delivery/verifying/` | `MASTER:28` 与 `arch:1964` 的目录树画了它，**实测不存在** |
| B-2 | checkpoint 落点 | `AGENT-INDEX.md:127` 与 `MASTER:48` 要求 active 目录含 `checkpoint.md`，模板却把 `## 12. Current Checkpoint` 放在 `change.md` 内，且 `verify_delivery_governance.py:96` **只 glob `change.md`** ⇒ `checkpoint.md` **零强制点**；`templates/delivery/` 里也没有它的模板 |
| B-3／N1 | 里程碑与计划的过期结论 | `M3-content-discovery-v2.md:35`、`MASTER:158` 各留一条当天稍后即被推翻的结论 |
| B-4 | `conventions` 自相矛盾 | `commit_generated` 一行前后句互相否定（root=false，其余 4 个 true） |
| B-5／N3 | 执行根入口文件的描述 | `conventions:18-20` 与架构文档 7 处描述「执行根承载自动生成的根 `AGENTS.md`／`CLAUDE.md` 与 `.skill-sync.lock.json`」；实测三样**都不存在**，且 `prepare_ai_workspace.py` 从不生成根入口文件 |
| B-6 | 会过期的读数 | `conventions:199` 的漂移计数 `0/8/0`——工作区 `CLAUDE.md` 削薄后实测为 `0/3/0`，即该数**今天已经过期**，且没有任何东西会提醒重测 |
| B-7 | ADR-0007 的死指针 | `0007:9` 的 `docs/视觉/…`（实测该目录不存在，全仓零命中） |
| N2 | 瘦身造成的净事实损失 | 工作区 `CLAUDE.md` 删掉的 `## 提交约定` 含三条；实测活落点：**Conventional Commits** 与**「纯移动与改逻辑不同 commit」零落点**（只在 `delivery/completed/` 历史里） |
| N4 | 视觉规范整篇与实测不符 | `web-desktop-visual-system.md` 的目录结构（`apps/console`、`packages/*`）、包管理器（`pnpm`）、构建脚本（`build:web`、`dev:web`）、产物名（`dist-web`）、开发端口（5173）**全错**；实测为 `npm`、`build:cloud`、`dist-cloud`、5174 |
| N5 | 视觉规范多落点 | `specs/` 下两篇「视觉规范」并存，`specs/README.md:9` **只索引 6 篇中的 1 篇** |

**视觉两篇的实测画像**（T-11 的输入）：`web-desktop-visual-system.md` 1230 行／24,114 B，无任何头部元信息，62 段里视觉 24／架构 21／功能 7／其他 10，引用者 **1 处**（`docs/decisions/0007:9`）；`前端框架视觉规范v2.md` 873 行／20,276 B，有版本头（V1.1／2026-08-06／项目级视觉与交互基线），72 段里视觉 **51**／架构 8／功能 1／其他 12，事实核对**无一处错**，引用者 **0 处**。

### 4.3 实测读数（带分母，供 §10 判据引用）

| 项 | 读数 |
|---|---|
| 状态词（分母＝`delivery/planned`＋`delivery/active` 各 `change.md` 的 status 行） | `DISCUSSION` 7、`PLANNED` 5、`SUPERSEDED` 7；`TODO`／`IMPLEMENTED`／`VERIFIED`／`CLOSED` **0**（执行时按同一分母复测并报出） |
| 架构文档目录树 | `arch:1988` **有** `tests/`；**原诊断「两棵树都漏画 `tests/`」过宽**——只有 `MASTER:28` 那棵缺，`arch` 那棵不缺 |
| 两篇视觉规范体量 | 见 4.2 末段（`docs/engineering/specs/` 共 6 篇） |
| `templates/delivery/` | 只有 `change.md`、`evidence-record.md` |

### 4.4 开工时的三仓基线（记下来，避免 CHG-063 AC-12 那样的缺口）

`git status --porcelain` 于 T-01 记录，见 §11。本 CHG 对三仓零写，收尾时按同一命令复测。

## 5. Scope

### Add

- `delivery/active/CHG-20260925-064/`（`change.md`、`checkpoint.md`、`evidence/`）
- `templates/delivery/checkpoint.md`（T-06）
- `verify_delivery_governance.py` 的一条结构检查：active CHG 目录必须含 `checkpoint.md`（T-06）
- `AGENT-INDEX.md` 里两条被削薄弄丢的提交约定（Conventional Commits、纯移动与改逻辑不同 commit）（T-04）

### Modify

- `docs/engineering/specs/agent-workspace-conventions.md`（T-03 精简、T-10 执行根段）
- `AGENT-INDEX.md`（T-04 读取顺序与入口职责、T-05 前不涉及）
- `AGENTS.md`、`CLAUDE.md`（T-04 去复述，只留指针）
- `scripts/prepare_ai_workspace.py`（T-04 `reading_order` 常量）
- `delivery/MASTER_IMPLEMENTATION_PLAN.md`（T-04 读取顺序、T-05 状态词汇、T-09 过期结论、T-10 目录树）
- `delivery/milestones/README.md`、`delivery/milestones/M3-content-discovery-v2.md`（T-09）
- `docs/decisions/0015-*.md`（T-08）、`docs/decisions/0007-*.md`（T-10）
- `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md`（T-10 目录树与执行根段）
- `docs/README.md`、`docs/product/README.md`（T-10 外层 `docs` 指针）
- `scripts/verify_product_master_alignment.py`、`templates/delivery/change.md`、两个 workspace skill（T-06）
- `delivery/planned/*/change.md`、`delivery/planned/README.md`（T-07）
- `docs/engineering/specs/web-desktop-visual-system.md`、`docs/engineering/specs/README.md`（T-11）

### Delete

- `docs/engineering/specs/前端框架视觉规范v2.md`（T-11：视觉内容并入存活件后删除；**用户 2026-09-25 裁定「两份视觉方案合并」**）
- `MASTER:28`、`arch:1964` 目录树里的 `verifying/` 条目（T-10）

### Explicitly Not Doing

- **不为「里程碑文件头的状态声明」新增一致性判据**：会把文件头格式冻成契约（M2 与 M3 的头格式已不同），与 CHG-063 的判据稳定性分层结论相悖。
- **不删除 `agent-workspace-conventions.md`、不把它并入 `AGENT-INDEX.md`**（用户裁定「精简保留」）。
- **不改 `0017` 的 `Supersedes` 清单**（用户政策：调整历史直接覆盖旧的，不留取代注记；变更理由记在本记录 §4.2 C2 与本记录内）。
- **不动权限**（沿用用户 2026-09-25 早先的裁定）。
- **不做架构文档 `_V1.md` 的全篇审计**：只处置被点名的三处（目录树 `verifying/`、执行根入口段、前端源码根），其余陈旧点登记为遗留。
- **不碰 M4**（`CHG-20260924-061` 仍在 `planned`）。

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | `agent-workspace-conventions.md` **精简保留**：去过程叙述与一次性读数，保留规则（用户 2026-09-25 裁定） | CONFIRMED |
| D-02 | ADR-0015:6/:27 的 FFmpeg 归属**就地改写那句**（整句重写，不删词、不加取代注记） | CONFIRMED |
| D-03 | 两篇视觉规范**合并**：`web-desktop-visual-system.md` 去掉功能描述，只保留视觉与架构描述；存活件见 T-11（用户 2026-09-25 裁定） | CONFIRMED |
| D-04 | `checkpoint` **保留独立 `checkpoint.md`**（不收进 `change.md` §12）（用户 2026-09-25 裁定） | CONFIRMED |
| D-05 | 调整历史**直接覆盖旧的**，不留取代注记；变更理由记在本记录内。只有真正属于用户的删除/取舍才提请确认（用户 2026-09-25 政策） | CONFIRMED |
| D-06 | 2026-09-24 入口重构遗留的两处未提交工作区编辑（`CLAUDE.md` 瘦身、`conventions:33`）由本 CHG 承接，**不单独开 CHG**（用户 2026-09-25 裁定） | CONFIRMED |
| D-07 | 执行根已无 `AGENTS.md`／`CLAUDE.md` 系**用户本人删除** ⇒ 描述「执行根承载自动生成入口文件」的落点按机制终结改写（用户 2026-09-25 陈述） | CONFIRMED |

## 7. Pending Questions

None.

## 8. Implementation Tasks

一 Task 一提交；依赖见末列。

| Task | Goal | Status | Verification | 依赖 |
|---|---|---|---|---|
| T-01 | 激活：建 active 记录、`LEDGER.md` 表行、重生成快照 | DONE | 两门禁 `exit=0`；LEDGER 表行逐字等于 `\| <CHG> \| <title> \| <status> \| <repo> \|`；§7 为字面 `None.` | — |
| T-02 | 承接两处未入账工作区编辑（`CLAUDE.md`、`conventions:33`） | DONE | `git show --stat` 只含这两个文件；六门禁复测 | T-01 |
| T-03 | `conventions` 精简保留（按用户裁定的保留清单：删读数与历史叙述；逐节复核 2 处引用） | DONE | 见 §8.1；208→148 行、节数 11→11；两处引用改 1 留 1（留的理由见 evidence §5） | T-02 |
| T-04 | 读取顺序单一化 + 入口文件只留指针 + 补回两条提交约定 | DONE | 见 §8.2；落点由 5 处手写＋1 常量收敛为 **1 处手写＋1 生成物**；入口红线 9/9 逐条归属；变异对照证明快照确由该常量派生 | T-03 |
| T-05 | 状态词汇成文（`MASTER:105-128` 就地覆盖为实测在用词汇＋一行历史词汇） | DONE | 见 §8.3；CHG 六词、里程碑四词、退役词与分母逐项报出；阳性对照 `CLOSED` 2／`HANDOFF` 2 | T-04 |
| T-06 | 脚本／模板／checkpoint 落点对齐（接受集、文案、模板、新增结构检查） | DONE | 见 §8.4；六门禁 `exit=0` ＋ `Ran 79 tests`；**新判据两条均做变异对照**（失红后还原经 `cmp` 逐字节）；**在本 CHG 仍 active 时复测**（接受集正打在自己的 LEDGER 表行上） | T-05 |
| T-07 | `planned` 记录状态词就地改写 | TODO | 逐文件 `git diff` 只改状态词一行；两遍词汇统计 | T-06 |
| T-08 | FFmpeg 归属（ADR-0015 就地改写） | TODO | 全仓归属落点复扫＝Cloud；阳性对照 | 独立 |
| T-09 | 里程碑与交付事实（C6／B-3／N1） | TODO | 该 grep 改前 ≥3、改后 0；四处逐字一致 | 独立 |
| T-10 | 目录树、死指针、执行根入口描述、外层 `docs` 指针 | TODO | `verifying/` 只余历史归档；树内条目逐条 `ls`；`根 \`AGENTS.md\`` → 0 | 独立 |
| T-11 | 前端源码根 + 两篇视觉规范合并 | TODO | `wt-media-cloud/frontend` → 0；索引数与实际篇数一致；删除前逐节对照 | 独立 |
| T-12 | 收尾：归档、LEDGER 同步、快照重生成、evidence 汇总 | TODO | 六门禁 + `unittest` 在**最后一次改动之后**重测；两遍失效指针扫描（各带阳性对照与分母） | 全部 |

### 8.1 `conventions` 逐节处置（T-03）

| 节 | 处置 |
|---|---|
| §1 不变量 6 条 | **保留**（用户裁定的保留清单）。与 `AGENT-INDEX.md` §2 红线局部重叠，按裁定不去重，登记为 §14 第 9 项 |
| §2 父层定位 | 前半（列执行根入口文件）随执行根删除改写为「父层不承载入口文件、执行快照或任何治理事实源」；后半「父层允许存在容器与分发产物、不允许第二份快照」保留（全文独有） |
| §3 入口文件表 | 删表并改为指路（`AGENT-INDEX.md` §10 有同义表）；「两个 harness 各自加载到不同结论——本规范最需要防守的失败模式」保留（是 T-04 修复的依据）；第三层降级句删（`AGENT-INDEX.md:78` 有） |
| §4 执行快照 | 保留「入 git 的两个理由」「8000 字符预算」「`--change`／`--no-active` 互斥且两侧必须同时支持」；位置／唯一性／生成方式／内容／禁止写入／Milestone 决策六项与 `AGENT-INDEX.md:158-164` 重复，删并改为指路 |
| §5 渐进式加载 | 改为一行指路（`AGENT-INDEX.md` §4 是唯一落点），三层清单不重复。**删时发现两版「第二层」不一致**（本节有 `LEDGER.md` 与 Milestone，`AGENT-INDEX.md:63` 没有），交 T-04 裁定 |
| §6 多工程并行 | 前三条去重并入指路句（`AGENT-INDEX.md:171-174` 有）；「只允许一个 active CHG vs 语义上允许 N 个」这条已知张力保留 |
| §7 配置 | **保留**（用户裁定的保留清单）：四个字段表、`kind: distribution` 的用途、四条强制点、`agent_config.py` 不得被校验脚本 import、5 处落点。四条强制点是全文独有（`AGENT-INDEX.md:166-168` 未枚举） |
| §8 初始化脚本语义 | 保留（幂等／永不覆盖／`--dry-run`／不硬编码路径／目标须是 git 仓） |
| §9 规则—实现耦合点表 | **原样保留**（全文独有，回答「改这条规则必须同步改什么」） |
| §10 | 删实测读数表、全部 WARN 计数（含 `0/8/0`）与两条已关闭 WARN 段；保留判据稳定性分层表、候选块段、「报『通过／0 命中』前必须证明检查能失败」四条、`check_entry_drift` 的机制登记、`不设 CI ⇒ 不把红项写进文档` 的规则。同时把 `AGENT-INDEX.md:198` 的「该节是校验状态的唯一落点」改为「**校验读数不作文档落点**」 |
| §11 明确不做 | 保留 |

### 8.2 读取顺序落点收敛（T-04）

改前 **5 处手写清单**（`AGENT-INDEX.md:7`、`AGENT-INDEX.md` §4、`AGENTS.md`、`CLAUDE.md`、`MASTER:791-796`，
后三者内容互不相同）＋ **1 处代码常量**；改后 **1 处手写（`AGENT-INDEX.md` §4）＋ 1 处生成物**
（`.ai/CURRENT_CONTEXT.md`，由 `prepare_ai_workspace.py::build_context` 的 `reading_order` 渲染）。

| 改动 | 落点 |
|---|---|
| §4 补齐第 6–8 项（T-03 删 `conventions §5` 时发现的两版不一致） | `AGENT-INDEX.md` §4 |
| 入口两文件删自己的清单，改指回 §4；删各自复述的 4+5 条红线，改指回 §2 | `AGENTS.md`（30→22 行）、`CLAUDE.md`（37→28 行） |
| 删 Codex 6 项清单（整份不含 `AGENT-INDEX.md`，第 1 项指向已删的执行根 `AGENTS.md`） | `MASTER:791-796` → 1 行 |
| 常量加注释登记「§4 的生成物镜像」与双向同步义务 | `scripts/prepare_ai_workspace.py:143-147` |
| `conventions` §5 标题「渐进式加载」→「读取顺序」（该节本就只是指路，无清单；改名消掉已退休的术语），并在 §9 耦表**新增「读取顺序」一行**登记双向同步义务 | `docs/engineering/specs/agent-workspace-conventions.md` |
| 退休词「渐进式加载」在目录树里的残余（本 Task 内自捕） | `MASTER:66` |
| 补回被瘦身丢掉的两条提交约定 | `AGENT-INDEX.md` §9「提交纪律」 |

细节读数、变异对照与逐条归属表见 `evidence/task-04-reading-order-single-landing.md`。

### 8.3 状态词汇成文（T-05）

`MASTER` §3 由「两套词 ＋ 状态定义表」就地覆盖为 `### 状态词汇`：

| 项 | 改前 | 改后 |
|---|---|---|
| CHG 词 | `TODO → IMPLEMENTED → VERIFIED → CLOSED` | `DISCUSSION → PLANNED → IMPLEMENTING → VERIFYING → DONE`（＋`SUPERSEDED`） |
| 该组词与实测的关系 | `TODO`／`IMPLEMENTED`／状态值 `VERIFIED` **零记录使用**；真在用的 `DISCUSSION`／`PLANNED`／`SUPERSEDED` **一个字都没有** | 六个词全部为实测在用的值，读数列逐词给出 |
| 里程碑词 | 四个词，无现状列 | 同四词，第三列直接写「当前处于该态的里程碑」 |
| 与校验脚本接受集的关系 | 两套**交集为零** | 表成文；脚本接受集与文案的对齐是 **T-06** |
| 子项状态 | 未区分 | 明写「里程碑内部子项（如 M2-D 的 `DEFERRED`）不占上表」 |

`MASTER` §6 的 `### CHG 门禁 — CLOSED` 与正文、以及 `:289`／`:336` 两处 `CLOSED` 一并改为 `DONE`——
`CLOSED` 退役后，§6 是它的第二个落点。

**一次取舍已记依据**：实施中词取 `IMPLEMENTING`（模板教的词、测试夹具默认值、脚本接受集成员、
056～064 全链在用），退 `IN_PROGRESS`（仅旧归档 4 处 ＋ 1 篇 `planned`）；里程碑层仍用 `IN_PROGRESS`。

细节与分母见 `evidence/task-05-status-vocab.md`。

### 8.4 脚本／模板与 `checkpoint.md` 落点对齐（T-06）

| 项 | 改前 | 改后 |
|---|---|---|
| 「active 目录必须有 `checkpoint.md`」 | 规则写在 `AGENT-INDEX.md` §8，但 `git grep -i checkpoint -- scripts tests` 命中 **0** 个文件（阳性对照 `change.md` 9 个）⇒ 只写成 `change.md` 的 active CHG 能过全部门禁 | `verify_delivery_governance.py` 报 `active CHG is missing checkpoint.md: <id>`；活树阳性对照：把本 CHG 的 `checkpoint.md` 改名 → 真门禁 `exit=1`，还原后 `sha256` 相同 |
| 模板 | `templates/delivery/` 只有 `change.md`、`evidence-record.md`；checkpoint **内联**在 `change.md` §12 | 新增 `templates/delivery/checkpoint.md`；§12 改为指针 |
| skill 落点 | `SKILL.md:95`「Update the active **`change.md`** checkpoint」 | 改为 `checkpoint.md`，并注明它是**必需文件** |
| 状态接受集 | `{IN_PROGRESS, IMPLEMENTING, VERIFYING, ACTIVE}`（与 §3 交集为零；含已退役的 `IN_PROGRESS` 与幻影词 `ACTIVE`） | **`{IMPLEMENTING, VERIFYING}`**——记录落在 `active/` 即意味着在执行，其余四词均属别处或终态 |
| 带注状态行 | `(\S+)\s*$` 要求整行只有那个词，带注行**一个都匹配不上** ⇒ `status=None`；`CHG-20260923-059` 的 active 期状态行正是带注形式，它自己的门禁输出里留着 `… got None`——**点了一个该记录从未有过的状态** | 抽出 `status_word()` 先剥 `**` 再剥 `（…）`／`(…)`；`HEAD` 版上的红**是行为性的**（在测试里复现出 059 那条 `got None` 报文），新脚本下 `OK` |

连带：剥注后 LEDGER 表行比对由**被跳过**变为**真的执行**（口径收紧）；`MASTER` §3 的 `ACTIVE` 括号作废（改为「0 处」＋一句活态词）与 `TODO` 的轴限定（任务表仍在用，本 CHG §8 自己就有 18 行）；`conventions` §9 加「active 记录成对」「CHG 状态词」两行耦合。两个新用例各带变异对照，`unittest` 由 75 增至 **79**。

细节见 `evidence/task-06-script-template-checkpoint.md`。

## 9. Repository Checklist

### wt-media-workspace

- [x] 本 CHG 的全部改动都落在本仓
- [x] `AGENT-INDEX.md` 与两个入口文件在 T-04 后只剩单落点
- [ ] 六个静态门禁 + `unittest discover -s tests -q` 在收尾后全绿（T-12）

### wt-media-cloud

- [ ] Not affected（只被读：源码根与构建脚本作为事实依据）

### wt-media-agent

- [ ] Not affected

### wt-media-desktop

- [ ] Not affected（只被读：`src-tauri/tauri.conf.json` 作为事实依据）

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | 读取顺序在全仓只剩 1 个落点（`AGENT-INDEX.md`）＋生成物；两个入口文件与 `MASTER` 的第三版都改为指回它 | T-04 的 grep 读数（含阳性对照） | **PASS** |
| AC-02 | 两个入口文件不再逐字复述 `AGENT-INDEX.md` §2 的红线；每条被删条目都有归属依据 | T-04 的逐条归属表 | **PASS** |
| AC-03 | 被削薄弄丢的两条提交约定在 `AGENT-INDEX.md` 有活落点 | T-04 的 grep（改前 0 命中留证） | **PASS** |
| AC-04 | CHG／里程碑状态词汇只剩一套，且**实测在用的每个词都被定义**；脚本接受集与成文一致 | T-05＋T-06＋T-07 的词汇统计逐词相等 | TODO（T-05 成文、T-06 接受集已收口；T-07 后逐词复算） |
| AC-05 | `checkpoint.md` 有唯一权威落点、有模板、且有强制点（缺失会红） | T-06 的变异对照 | **PASS**（落点＝`AGENT-INDEX.md` §8／§9；模板＝`templates/delivery/checkpoint.md`；强制点＝`verify_delivery_governance.py`，失红并经活树阳性对照） |
| AC-06 | 视图中「E3 未开始」等与事实相反的结论为 0 | T-09 的 grep 改前 ≥3／改后 0 | TODO |
| AC-07 | `verifying/` 不再是任何目录树的条目；树的每个条目都存在 | T-10 的逐条 `ls`（含阳性对照） | TODO |
| AC-08 | ADR-0015 与 ADR-0017 不再对 FFmpeg 归属给出相反答案；全仓该归属只有 Cloud 一个结论 | T-08 的复扫（含阳性对照） | TODO |
| AC-09 | `wt-media-cloud/frontend` 全仓 0 命中；被改的 `frontend` 只限目录名（字段名／脚本名不动） | T-11 的 grep＋逐处分类表 | TODO |
| AC-10 | 视觉规范只剩一篇，且它自述为当前基线；其功能描述已去除、视觉与架构描述保留 | T-11 的逐节对照表 | TODO |
| AC-11 | `conventions` 只剩规则与「为什么」，无一次性读数（6 类读数／叙述模式改前 1–7 命中、改后全 0）；两处活引用者**逐个复核**——改 1 处、留 1 处并给出留的理由 | T-03 的阳性对照读数（`evidence/task-03-conventions-slim.md`） | **PASS** |
| AC-12 | `specs/README.md` 的索引条目数与该目录实际篇数一致 | T-11 的计数比对 | TODO |
| AC-13 | 六个静态门禁 `exit=0`、`unittest` 全绿，且在**本 CHG 最后一次改动之后**重测 | T-12 的收尾读数 | TODO |
| AC-14 | 归档后无失效指针（字符串扫描＋相对链接 resolve，各带阳性对照与分母） | T-12 的两遍扫描 | TODO |
| AC-15 | 本 CHG 对三个运行仓零写 | 收尾 `git status --porcelain` 与开工基线逐条一致 | TODO |

## 11. Evidence

Evidence 落在 `evidence/`，记事实不重复需求：命令／动作、期望、实际、结论、相关 commit。

- `evidence/task-01-activate.md`
- `evidence/task-02-adopt-working-tree-edits.md`
- `evidence/task-03-conventions-slim.md`
- `evidence/task-04-reading-order-single-landing.md`
- `evidence/task-05-status-vocab.md`
- `evidence/task-06-script-template-checkpoint.md`
- `evidence/artifacts/`：原始输出（`t01-`、`t03-`、`t04-`、`t05-`、`t06-gate-readings.out`）
- 后续每个 Task 一份 `evidence/task-xx-<topic>.md`

**开工三仓基线**（T-01 记录，收尾按同一命令复测）：

```
$ git -C ../wt-media-cloud status --porcelain
?? dump.rdb
$ git -C ../wt-media-agent status --porcelain
（空）
$ git -C ../wt-media-desktop status --porcelain
（空）
```

## 12. Current Checkpoint

见同目录 `checkpoint.md`（本 CHG 起，活动状态以该文件为唯一落点）。

## 13. DONE Gate

- [ ] Scope completed.
- [ ] No blocking `Q-xx`.
- [ ] Acceptance matrix all PASS.
- [ ] Automated tests passed or justified.
- [ ] Manual verification evidence recorded where required.
- [ ] Diff checked for out-of-scope changes.
- [ ] Runtime repositories touched only if listed in scope.
- [ ] Required baselines updated.
- [ ] Affected repositories committed independently.

## 14. 遗留（只登记，需独立 CHG 处置）

| # | 条目 | 为什么本 CHG 不处置 |
|---|---|---|
| 1 | `verify_agent_entry.py` 的 `check_entry_drift` workspace 臂恒空 | 它不改变 exit code，只制造「绿得没有证据」；把它塞进 `errors` 会让启发式措辞变化打红门禁。CHG-063 已登记，独立 CHG |
| 2 | `MASTER:155` 与 `:355` 的里程碑状态双落点 | 今天两处一致故无活冲突；让前者进判据属扩大判据，与 CHG-063 的判据分层结论相悖 |
| 3 | `AGENT-INDEX.md` §5 表未写前端源码根 | 属「补落点」而非「消冲突」 |
| 4 | 架构文档 `_V1.md` 其余未扫的陈旧点 | 该文 2000+ 行，全篇审计会使本 CHG 范围失控 |
| 5 | M0／M1 已 `DONE` 却仍留候选 CHG 块 | CHG-063 已登记 |
| 6 | `LEDGER.md:21` 的「见上表」不可达 | CHG-062 遗留第 8 项；属 LEDGER 的历史叙述 |
| 7 | `AGENT-INDEX.md:198` 曾把 `conventions §10` 定为「校验状态的唯一落点」，而 §10 承载的是易失读数 | **T-03 已取消该落点**（改为「校验读数不作文档落点」）；但「易失内容该不该有文档落点」这一机制尚无可机检的通用对策，登记 |
| 8 | B-6⑨ 余项：`docs/superpowers/`（23 篇中 21 篇无人引用）、`delivery/planned/` 的 9 个 `SUPERSEDED` + 6 个「已实施却仍挂 planned」、`completed/CHG-20260916-052` 单条占归档 74% | 属诊断 G-5／G-6，需独立 CHG 与用户裁定 |
| 9 | `conventions §1`（6 条不变量）与 `§7` 开头同 `AGENT-INDEX.md` §2／§10 局部重叠：T-03 按用户裁定的保留清单**未去重** | 去重须先裁定「规范文件可否复述红线」，属用户取舍。本 CHG 只登记「落点未减」这一事实 |
| 10 | `AGENT-INDEX.md` §4 作为读取顺序的**唯一**落点，**没有机检点**（`conventions` §9 耦表已如实登记「入口文件与 `MASTER` 不得再列清单」靠人工复核） | T-04 把落点降下来了，但「唯一」目前只由本 CHG 的一次性扫描证明。为它新增机检点会把 §4 的条目文本冻成契约（措辞一变就红），与 CHG-063 的判据分层结论相悖，须独立裁定 |
| 11 | 里程碑文件头的状态写法四种并存：`- Milestone status:`（M4／M5）、散文（M2）、`> 实施状态：`（M3）、`- 状态：**已完成**`（M-launch-engineering） | T-05 只成文**词表**、不统一**写法**：为四种既有格式新增一致性判据会把它们冻成契约，与 §5 Explicitly Not Doing 的既有声明相悖。现状如实登记在 `MASTER` §3 表下 |
| 12 | `CHG-044`／`CHG-052` 归档写的 `HANDOFF` 是否改判 `DONE` | 该裁定已由 `LEDGER.md:31` 专段登记并写明「属治理口径决定，本次不动」。T-05 只把 `HANDOFF` 列为退役词，不回改归档记录 |
| 13 | **任务表**状态词（`TODO`／`DONE`）无门禁、无成文词表 | 它是与 CHG 状态**不同的轴**（T-06 已把 `MASTER` §3 的措辞限定到 CHG 轴）。为任务表新增判据会把 `templates/delivery/change.md:76` 的那一列文本冻成契约，属「补落点」，须独立裁定 |
| 14 | 58 篇记录里 **9 篇**的状态行带注（`（…）`／`(…)`／`**WORD（…）**`）；机器现已能读，但「状态行该不该带注」**无成文规则** | T-06 把脚本改成先剥注再判（不剥就会读成 `None`，`CHG-20260923-059` 实例），**属把已有的书写习惯接住，不是给它立规**；立规会与「就地覆盖、不追加注记」的用户政策相互牵扯，须用户裁定 |
