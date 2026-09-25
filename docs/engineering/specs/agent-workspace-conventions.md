# Agent Workspace 协作规范

本规范描述 WT Media 多仓库在 AI Agent（Claude Code、Codex 等）协作下的入口、上下文加载与校验约定。它补充 `AGENT-INDEX.md` 第 10 节「Agent 入口与执行快照」，并把散落在脚本与 skill 中的隐含约束显式化。

更新：2026-09-25（§1 把「规则正文归口」由治理仓推广到四仓——运行仓各长出一份正文副本正是这条不变量原先只管治理仓的结果；§3 由「并列两条性质」改写为完整的入口文件**形态**规定：角色与边界表、指针文件三条机检、重复的判别句「只允许生成物 ← 其唯一生成器」、运行仓八节模板；§9 新增五行强制点并去掉两处「无强制」；§10 退役 `check_entry_drift` 的恒空登记、改写已知限制；§11 补两条禁止项。载体 CHG-20260925-065）。

## 1. 不变量

1. `wt-media-workspace` 是治理中心与唯一事实源，不是代码执行中心，也永远不能成为运行时依赖。
2. 每个工程仓库自治：自己维护 `AGENT-INDEX.md`、`AGENTS.md`、`CLAUDE.md`、`DIRECTORY_MAP.md`（四者的角色见 §3）。
3. **规则正文归口 `AGENT-INDEX.md`**——治理仓归的是治理规范正文，运行仓归的是本仓规则正文（`## 本仓规则`）。`AGENTS.md` 与 `CLAUDE.md` 只声明权威源与最小硬约束，**不复制正文**。这条不变量原先只写在治理仓上，运行仓因此各自长出了一份正文副本（`wt-media-cloud` 的两个入口文件就是同一套规则的两份互相矛盾且都已过期的副本，见 §3 末）；本版把它**推广到四仓**，不再是治理仓专用。
4. 执行状态快照全项目**只有一份**，位于 `wt-media-workspace/.ai/CURRENT_CONTEXT.md`。
5. 关联工程路径以 `config/repository-map.yaml` 为准，脚本与文档不得另行硬编码，也不得与之漂移。
6. 运行时改动只发生在对应工程仓库；治理仓库不存放业务代码、构建产物或临时文件。

## 2. 父层定位

执行根 `/…/wt-media/` **已经存在**，且会继续存在。它是仓库容器与 skills 分发目标，承载：

- `.claude/skills/`、`.codex/skills/`、`.agents/skills/`：由 `scripts/sync_skills.py` 与 `scripts/prepare_ai_workspace.py` 生成的 skill 副本；
- `wt-media.code-workspace`：编辑器多根工作区定义；
- `wt-media-cloud/`、`wt-media-agent/`、`wt-media-desktop/`、`wt-media-workspace/`：四个独立 git 仓库。

父层**不承载**入口文件、执行快照或任何治理事实源：Agent 的入口与权威一律在 `wt-media-workspace` 仓内（`AGENT-INDEX.md` 与两个薄入口）。

不变量是「**不新增更多中间层**」，而不是「父层不得存在」。父层允许存在容器与分发产物，**不允许**存在第二份执行状态快照或任何治理事实源。

## 3. 入口文件形态

强制项清单见 `AGENT-INDEX.md` 第 10 节「入口文件」（本节不重复该表）。此处规定该表**不表达**的部分：每类文件装什么、不装什么，以及这些性质怎样被机检。

### 角色与边界

| 文件 | 装什么 | **不装什么** |
|---|---|---|
| `AGENT-INDEX.md` | 该仓**全部正式内容**的唯一落点（见下「两个角色」） | 目录树（→ `DIRECTORY_MAP.md`）；禁止扫描区清单（→ `DIRECTORY_MAP.md`）；工作区红线正文；他仓路由 |
| `AGENTS.md` | 一行身份 ＋ 机读键 ＋ `## 权威源` 段（2–4 行，指向 `AGENT-INDEX.md` 与工作区 §2／§4） | **任何规则句**；目录清单；读取顺序清单；工作区红线 |
| `CLAUDE.md` | 同 `AGENTS.md`（措辞按各自 Harness 的实况） | 同上 |
| `DIRECTORY_MAP.md` | 分区目录树＋路径／职责／何时进入；**禁止扫描区及理由** | 规则、理由、未来规划、需求路由表 |
| `README.md` | 职责、构建／测试／运行命令、人向目录概览 | 读取顺序、红线、`## Rules` 式禁令段——**它不得成为任何 Agent 援引的权威** |

`AGENT-INDEX.md` 在四仓**同名两角色**，这是有意的：治理仓是治理规范正文，运行仓是三层索引（读工作区 §4 第 8 项）。运行仓的该文件**八节同序**：依赖 / 定位 / 本仓库拥有 / 本仓库不拥有 / 需求路由 / **本仓规则** / 禁止 / **本仓内加载顺序**。治理仓**豁免**八节检查——它的结构由 `AGENT-INDEX.md` 自己规定。

`DIRECTORY_MAP.md` 是唯一被允许携带一类规则的导航文件（禁止扫描区），因为**排除项本身就是目录事实**，而探索者正是在这个文件里找它。这是**有界例外**，写在规范里正是为了让它可判、而不是模糊。

### 指针文件的机检定义

`AGENTS.md` 与 `CLAUDE.md` 是**指针**。三条 ERROR，逐条都能被变异点亮：

1. **正文声明**：含且只含一行机读键 ``- 正文：`AGENT-INDEX.md` ``，且该目标在本仓存在、不是自身；同仓各指针声明的正文必须**同一**，且正文不再声明正文（杀 `A→B, B→A` 环）。
2. **规则词判据**：**任何命中规则词的非标题行，同一行内必须出现正文文件名**。这是「指针的指令」与「被复述的规则」的判别式——`必须先读 AGENT-INDEX.md` 是合法指针，`不创建 internal/runtime` 是复述的规则。**标题行不计入**：章节名是**命名**而不是**断言**——`## 红线` 指路合法，`## 模块规则` 若不把规则正文写进来也不违规。判据抓的是正文，不是名字。
3. **指针预算**：行数 ≤ 30；字节 ≤ 2000；**H2 ≤ 4**。三项都是**结构性上限**，不是要逐字匹配的模板——预算定在治理仓参照件（1755 B / 28 行 / 3 个 H2）之上，只留措辞余量。**不设 H2 白名单**：白名单会把章节名冻成字符串契约（CHG-20260925-063 的回归模式），而真正要防的「规则段被贴进指针文件」已由第 2 条**按正文**抓死。本条的判据在 CHG-20260925-065 T-03 由「H2 ≤ 1 ＋ 白名单 `权威源`」改成现在这样，理由是原表述**与自己引用的参照件相抵**（参照件 `CLAUDE.md` 有 3 个 H2，按原表述必然报错），且它要防的变异由第 2 条覆盖。

### 重复何时合法

**重复只在一个生成物与它唯一具名的生成器之间存在。** 这是把「像不像重复」变成可判问题的唯一判别句：

- 合法的两种：`.ai/CURRENT_CONTEXT.md` 的读取顺序（生成器 `prepare_ai_workspace.py::build_context` 的 `reading_order` 常量）与它的 Stable Ownership Boundaries 块；`skills/<group>/<name>/SKILL.md` 与 `sync_skills.py` 分发出的副本。**排除在比较集之外，按构造即成立。**
- **指针行同样排除**：同一行内出现正文文件名的行，是**指针的机械部分**，不是规则句。两个指针指向同一份正文，重叠是设计而不是缺陷——不排除的话，`CLAUDE.md` 与 `AGENTS.md` 只要都写得对就必然报重复。
- 其余任何重复都是缺陷：一侧不是生成物，那就有一侧必须死。

⇒ **比较集的构造**：非标题行 ∩ 不含正文文件名 ∩ 不含四个入口文件名 ∩ 命中规则词。三条排除各对应一类「重复是对的」：生成物、指针、以及描述文件角色的表行。

`verify_agent_entry.py` 的重复检查（WARN）按此比较各仓的规则承载文件，并**打印分母**（比较了多少条规则句 / 多少文件 / 多少仓）——0 命中不附分母就是「绿得没有证据」。

### 为什么是两个指针

Claude Code 原生只加载 `CLAUDE.md`；Codex 侧只读 `AGENTS.md`。**两个 Harness 各读一个文件，所以两个指针是必需的**——重复从来不出在「有两个入口」，只出在「正文被写了两遍」。平级不等于内容可以矛盾：当两者的规则冲突时，Agent 会按各自的 Harness 加载到不同结论——**这是本规范最需要防守的失败模式**。工程仓库中若把 `CLAUDE.md` 写成 `AGENTS.md` 的过期副本，即属**违规**（`wt-media-cloud` 在 CHG-20260925-065 之前正是此态）。

**不用 `@` 导入实现指针**：它与「四仓同一形态」不能同时成立，每个会话白付 3–4k est. tokens，且导入在子代理里不展开——主会话与子代理行为不一致，比纯指针更不可预测。指针的确定性来自「正文就是会话本来要读的那个文件」，不来自 Harness 的导入。

## 4. CURRENT_CONTEXT 契约

位置、唯一性、生成方式、内容与禁止写入项见 `AGENT-INDEX.md` 第 10 节「执行状态快照」（本节不重复）。此处只登记该节不表达的三条：

- **版本控制**：该文件入 git（`.gitignore` 不排除 `.ai/`）。因此每次重新生成都是一次可评审的 diff；它也随 `git worktree` 检出一起带走，这正是「快照放在仓库内而非父层」的第二个理由。
- **体积预算**：≤ 8000 字符（中英混排约 2700–4000 token，对应 <3000 token 目标）。脚本按 `字符数 / 2.5` 估算 token 并在校验时输出。
- **两个互斥模式**：`--change` 与 `--no-active` 互斥；`verify_delivery_governance.py` 把「无活动 CHG」当作合法状态，故生成与校验两侧必须同时支持它。

## 5. 读取顺序

读取顺序的**唯一落点是 `AGENT-INDEX.md` 第 4 节**（`.ai/CURRENT_CONTEXT.md` 的 Required Reading Order 是它的生成物镜像）：本节不重复其清单，只登记该节不表达的一条理由——

顺序开头的 `AGENTS.md` 与 `CLAUDE.md` 在治理仓是薄入口，正文与权威仍在 `AGENT-INDEX.md`；顺序之所以固定，是因为它同时约束 `.ai/CURRENT_CONTEXT.md` 生成器与三个工程仓，改动它需要三者同步。

## 6. 多工程并行

「禁止多个 Agent 同时修改 `.ai/CURRENT_CONTEXT.md`」、并行的触发条件、`delivery/active/<change-id>/status/` 的形态与汇总责任见 `AGENT-INDEX.md` 第 11 节（该节是唯一落点），本节不重复。

已知张力：`delivery/active/` 当前只允许存在一个 CHG，而并行诉求在语义上允许 N 个。当前通过「同一时刻只激活一个 CHG」维持两者相容。若将来确需两个真正并行的 active CHG，必须同时修改第 9 节登记的全部强制点，并同步修订 `AGENT-INDEX.md` 第 8 节与第 10 节的单数措辞。

## 7. 配置一致性

`scripts/sync_skills.py` 的**唯一**分发依据是 `config/skills-distribution.yaml`，代码中不再保留目标清单副本。目标的四个字段：

| 字段 | 含义 |
|---|---|
| `path` | 目标目录，相对 workspace 仓库的父目录；`..` 即执行根自身 |
| `groups` | 从 `skills/<group>` 复制哪些 skill |
| `kind` | `repository`（默认）或 `distribution` |
| `commit_generated` | 生成副本是否随该仓提交 |

`kind: repository` 的目标必须同时出现在 `config/repository-map.yaml`；`kind: distribution` 用于非仓库的落点（当前只有 `root`，即执行根——从跨仓工作区启动的 Harness 靠它发现 skill）。

`scripts/verify_agent_entry.py` 强制以下四条，任一不成立即 ERROR：

1. `repository-map.yaml` 的每个仓库都在分发目标中，且 path 完全一致（`../wt-media-cloud` 与 `../wt-media-cloud`）；
2. 每个 `kind: repository` 的目标都在 `repository-map.yaml` 中——**反方向检查**。此前只有正方向，导致 yaml 里多出的目标永远不会被发现；
3. `skills/` 下每个分组都至少被一个目标认领。**否则新增的分组会静默地永不分发**：sync 只遍历配置里列出的内容，会照常报成功；
4. 每个被认领的分组都真实存在。

配置由 `scripts/agent_config.py` 读取（纯标准库，无 PyYAML）。它是**被校验对象之外的独立模块**：校验脚本不得 import 它所校验的工具，否则工具一坏校验也跑不了。该读取器拒绝任何它不理解的写法（行内集合、重复键、Tab 缩进、畸形缩进）并抛出 `ConfigError`，因为此处误读会静默改变哪些仓库收到 skill。

生成副本共 5 处落点：执行根、三个工程仓、以及 **workspace 仓库自身**（`wt-media-workspace/.claude/skills`、`.codex/skills`）。workspace 那份是必要的：Agent 以 workspace 为 cwd 启动时只能从该 cwd 的 `.claude/skills` 发现 skill，父层那份不会被加载。这 5 处副本都随各自仓库提交（`commit_generated: true`），执行根不是 git 仓库，其副本无法提交。

## 8. 初始化脚本语义

`scripts/init-agent-entry.sh`：

- 幂等；**永不覆盖已有文件**，只报告 `exists:` / `created:` / `would create:`；
- **产出的形态必须是 §3 的形态**：运行仓写四件（两个指针 ＋ 八节正文 ＋ `DIRECTORY_MAP.md`），workspace 写三件。跑一次就该得到一棵过得了机的树——生成器与校验器是同一形态的可执行面，两者的分歧就是形态的第二个落点；
- **不得手写 `.ai/CURRENT_CONTEXT.md`**：该文件只有一个生成器 `prepare_ai_workspace.py`；本脚本只打印生成命令。手写版没有反引号，会被 `verify_delivery_governance.py` 的 `CONTEXT_RE` 静默读成 `None`，让指针检查空转；
- 支持 `--dry-run`，不写盘；
- 不创建父目录，不扫描整个系统，不修改未知目录；
- 工程路径从 `config/repository-map.yaml` 解析，不硬编码；
- 目标必须已存在且是 git 仓库，否则拒绝执行。

## 9. 规则—实现耦合点登记

每条规范都应在代码中有唯一的强制点。此表用于回答「改这条规则时必须同步改什么」。

| 规则 | 落点 | 耦合的实现 | 同步要求 |
|---|---|---|---|
| 快照唯一源 | `.ai/CURRENT_CONTEXT.md` | `prepare_ai_workspace.py::write_current_context`、`verify_delivery_governance.py::current_context_path`、`sync_skills.py::execution_root`（根目录探测）、`skills/workspace/executing-wt-media-change/SKILL.md`、`skills/workspace/planning-wt-media-delivery/SKILL.md`、`tests/test_prepare_ai_workspace.py`、`tests/test_verify_delivery_governance.py` | 改位置必须同步改这 7 处；`verify_agent_entry.py` 的单快照检查兜住回归 |
| 仓库路径 | `config/repository-map.yaml` | `init-agent-entry.sh::map_path`、`agent_config.py::read_section` | `verify_agent_entry.py` 双向强制与 `skills-distribution.yaml` 一致 |
| 分发目标 | `config/skills-distribution.yaml` | `sync_skills.py::load_targets`（唯一消费方）、`verify_agent_entry.py::check_config_agreement` | 改目标只改 yaml；代码里不得再出现目标清单 |
| 配置文件语法 | `scripts/agent_config.py` | `sync_skills.py`、`verify_agent_entry.py` 均 import 它 | 语法放宽必须同时改 `tests/test_agent_config.py` |
| 规则正文归口 | 各仓 `AGENT-INDEX.md`（治理仓＝治理规范正文；运行仓＝本仓索引 ＋ `## 本仓规则`） | `verify_agent_entry.py::check_pointer_shape`（ERROR：机读键／规则词判据／指针预算）、`::check_rule_body_consistency`（ERROR：正文同一且无环） | 改规则只改该仓 `AGENT-INDEX.md`；两个入口文件只保留指针。§3 是本条的唯一落点 |
| 入口文件存在性 | 四类入口文件 | `verify_agent_entry.py::check_entry_files`（ERROR：治理仓三件＋快照）、`::check_repo_entry_files`（ERROR：运行仓四件皆存在且非空） | 新增一类入口文件必须同时改 §3／`AGENT-INDEX.md` §10 表与本检查 |
| 入口文件形态 | 运行仓 `AGENT-INDEX.md` 八节同序 | `verify_agent_entry.py::check_layer3_shape`（ERROR：三仓 H2 序列互相相等且长度为 8） | 改节名或增删节必须**同时改三仓**；单仓自行改节即 ERROR。治理仓豁免（同名两角色，见 §3） |
| 本仓内加载顺序 | 各仓 `AGENT-INDEX.md` | `verify_agent_entry.py::check_local_order_scope`（WARN：不得出现 `CURRENT_CONTEXT`／`LEDGER.md`／`delivery/`） | 该节只写本仓内顺序；跨仓顺序的唯一落点是 `AGENT-INDEX.md` §4 |
| 规则句重复 | 各仓 `AGENT-INDEX.md`／`DIRECTORY_MAP.md`／`README.md` | `verify_agent_entry.py::check_rule_text_duplication`（WARN，打印分母） | 重复只允许「生成物 ← 其唯一具名的生成器」（§3）；其余重复要删掉一侧 |
| 读取顺序 | `AGENT-INDEX.md` §4 | `prepare_ai_workspace.py::build_context` 的 `reading_order` 常量（生成物镜像）；`AGENTS.md`／`CLAUDE.md`／`MASTER` §5 只留指针 | 改 §4 必须同步该常量并重生成快照；反之亦然。入口文件与 `MASTER` **不得**再列清单 |
| active 记录成对 | `AGENT-INDEX.md` §8「至少包含 `change.md` 与 `checkpoint.md`」 | `verify_delivery_governance.py::validate_delivery_governance`（active 目录缺 `checkpoint.md` 即报错）；`templates/delivery/checkpoint.md`；`skills/workspace/executing-wt-media-change/SKILL.md` 的 Checkpoints 节 | 改「active 目录至少包含哪些文件」必须同步该检查与模板；checkpoint 的内容**只写 `checkpoint.md`**，不得回写进 `change.md` §12 |
| CHG 状态词 | `MASTER` §3「状态词汇」 | `verify_product_master_alignment.py::validate_active_change` 的接受集 `{IMPLEMENTING, VERIFYING}` 与 `:292` 文案；`templates/delivery/change.md` 的 `- Status:` | 改 §3 中**可处于 `delivery/active/`** 的词必须同步该接受集；该接受集只收这两个词，`DISCUSSION`／`PLANNED` 属 `planned/`，`DONE`／`SUPERSEDED` 是终态 |
| skill 单一源 | `skills/<group>/<name>/SKILL.md` | `sync_skills.py` 分发到 `skills-distribution.yaml` 的 targets | `sync_skills.py check` / `diff`；分组认领由 `verify_agent_entry.py::check_group_coverage` 兜住 |
| 快照由脚本生成 | `prepare_ai_workspace.py` | `planning-wt-media-delivery` skill 第 7 步 | 两者措辞需同时更新 |

## 10. 校验

本地手工执行，本仓库当前**不设 CI**（`.github/workflows/` 已移除）。这不只有一个直接后果：门禁只在有人手工跑时才会被发现已经红，于是「**把红项写进文档**」这种处理方式实际上把它固定了下来——写出「已知红项」的那一刻，也就为它签了长期居留。故本节只写**怎么读**与**怎么控制**，不写读数：

> **当前读数不作文档落点。** 命令清单见 `AGENT-INDEX.md` 第 12 节；跑一下，读出什么就是什么。

需要真实运行实例、不属静态门禁的：`scripts/verify_m1_integration.py`、`scripts/verify_m3_acceptance.py`、`scripts/m2b_local_acceptance.py`；`scripts/verify_m0_local.sh` 在兄弟仓存在时跑静态门禁加三仓的构建与测试。

### 判据的稳定性分层

**跨仓源码字面量不作门禁；契约层与 schema 层判据保留并加固。** 这是 `CHG-20260925-063` 查明的根因：三个脚本长期红，**红的原因不是代码坏了**，而是它们把「源码文本」当判据，而那些文本已被后续 CHG **合法重构**——文件跨目录、跨仓迁移（`compatibility.go` 移到 `cloudagent/service/`）、常量换文件再导出（`REQUIRED_CONTRACT_REVISION` 仍在、值未变）、`main.rs` 被拆成分层模块（CHG-056）。**合法的重构能把门禁打红，这种门禁就在训练读者忽略红灯**，真回归随之被同一个「反正是已知红」掩盖。

| 层 | 例 | 可作为门禁吗 |
|---|---|---|
| 跨仓**源码文本** | `compatibility.go` 里的 Go 常量、`main.rs` 里的字符串 | **否**——重构即漂移。已全部移除，**不得加回** |
| **契约层** | `config/contract-map.yaml`、已发布 openapi/yaml、Desktop `contracts.lock.json` 的 `consumes` | 是——变更本需复核，正是门禁该拦的事 |
| **schema 层** | 已应用的 migration（`used_at` 列 + `token_hash` 唯一键） | **是**——已应用的 migration 是 append-only，其文本冻结 |
| **行为** | 「票据只能消费一次」 | 由**各仓自己的套件**覆盖（Cloud `TestRegisterConsumesTicketOnceAndIssuesHashedCredential`）。本仓不跑别的仓的测试，也不复述其实现 |

### 候选块属于未关闭的里程碑

MASTER 的 `候选 CHG：` 块是**未关闭**里程碑的字段。里程碑转 `DONE` 时候选块随之下线、由闭环记录取代（M2 2026-09-14、M3 2026-09-23 如此；M0/M1 关闭更早，块作为闭环记录保留）。据此校验分层：**已 `DONE` 只校验状态词**（及其既有闭环记录断言），**未 `DONE` 必须有非空候选块**。后者是硬错误，因为**对空块求值会让两类断言坏在相反方向**：`require_all` 恒报缺项（恒定噪音红灯），而 `forbidden in ""` 恒为假 ⇒ 该检查**静默通过**、认证了一个它从未读过的里程碑。

### 报「通过 / 0 命中」前必须证明检查能失败

`CHG-20260925-063` 在同一类错上踩了四次，形态不同、成因相同——**判据自己写错时，输出看起来同样「像量过的」**：

1. `grep -c` 数到了**自己写的删除注释**（被删字符串仍在散文里，命中 1）——改用 **AST** 枚举真断言集合；
2. 变异对照**没有重定向读取路径**，假树从未被读，三条变异全报 0 error——补**阳性对照**证明读取器确在读假树；
3. 测试断言「**存在某标签**」，而该标签由**恒定的噪音红**提供 ⇒ 用例在变异之前就已满足，**它所命名的检查被整条删掉也照样绿**——改为比较**完整错误集合**；
4. 一条 SQL 断言的**阳性对照**缺位时，「改绿」与「改成恒真」读数相同。

故：凡报「0 命中 / 通过 / 无新增」，必须附**阳性对照**并报出**分母**。变异式的「先红」必须是**关掉该判定后用例失败**，不能是 `ImportError`——导入错误什么都证明不了。

### 已知限制（机制，不是读数）

入口形态判据只抓**结构性外溢**：①写在 `## 权威源` 段内的**散文式**规则不被抓；②`AGENT-INDEX.md` 与 `AGENTS.md` 之间的**语义**矛盾不被抓——机检得到的是行级重复（WARN）与结构判据，**不宣称更多**。跨仓源码字面量同理不作判据（见上「判据的稳定性分层」）。

`CHG-20260925-063` §14 登记的 `check_entry_drift` 恒空问题已由本版**退役该检查**收口（原先四条臂中，治理仓那条结构性恒空，其余三臂在本版形态落地后也恒空——指针文件不承载路径事实）。它原有的意图由 `check_pointer_shape` 以更强的 ERROR 级判据顶替。规则不变：形态违规只检测、报告，修正由各仓自行决定（§11）。

## 11. 明确不做

- 不引入 RAG 知识库、自动知识图谱、Agent 调度平台、自动代码路由系统；
- 不引入第二套任务管理系统；
- 不为 `templates/` 建立模板渲染框架；
- 不以脚本自动改写运行时仓库的入口文件（`AGENT-INDEX.md` / `AGENTS.md` / `CLAUDE.md` / `DIRECTORY_MAP.md`）：形态违规只检测、报告，修正由各仓自行决定。`scripts/init-agent-entry.sh` 只做「从零初始化」且**永不覆盖已有文件**，**不得加 `--fix`**；
- 不把 Workspace 的规则**内容**覆盖到运行仓上——Workspace 只提供**形态**（文件角色、机检点、生成器），**内容**由各仓自治（`docs/engineering/architecture/…_V1.md:769`）。
