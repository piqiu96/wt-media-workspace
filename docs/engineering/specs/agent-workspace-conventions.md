# Agent Workspace 协作规范

本规范描述 WT Media 多仓库在 AI Agent（Claude Code、Codex 等）协作下的入口、上下文加载与校验约定。它补充 `AGENT-INDEX.md` 第 10 节「Agent 入口与执行快照」，并把散落在脚本与 skill 中的隐含约束显式化。

更新：2026-09-25（精简：删除一次性读数与历史叙述，读数改由实跑给出；父层一节按执行根现状改写。规则本身不变）。

## 1. 不变量

1. `wt-media-workspace` 是治理中心与唯一事实源，不是代码执行中心，也永远不能成为运行时依赖。
2. 每个工程仓库自治：自己维护 `AGENTS.md`、`CLAUDE.md`、`AGENT-INDEX.md`。
3. 治理规范正文归口 `AGENT-INDEX.md`；`AGENTS.md` 与 `CLAUDE.md` 只声明权威源与最小硬约束，不复制正文。
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

## 3. 入口文件

入口文件清单、角色与强制项见 `AGENT-INDEX.md` 第 10 节「入口文件」（本节不重复该表）。此处只登记两条该表不表达的性质：

`AGENTS.md` 与 `CLAUDE.md` 是**平级入口**，不允许互相软链或互相替代。

平级不等于内容可以矛盾。当两者的规则冲突时，Agent 会按 Harness 各自加载到不同结论——**这是本规范最需要防守的失败模式**。工程仓库中若把 `CLAUDE.md` 写成 `AGENTS.md` 的过期副本，即属违规；正确做法是两者各自独立、内容一致、或由 `CLAUDE.md` 明确声明权威源并**不重复**内容。`wt-media-workspace` 采用第三种做法：规范正文只存在于 `AGENT-INDEX.md`，两个入口文件都指向它并声明其权威性。

## 4. CURRENT_CONTEXT 契约

位置、唯一性、生成方式、内容与禁止写入项见 `AGENT-INDEX.md` 第 10 节「执行状态快照」（本节不重复）。此处只登记该节不表达的三条：

- **版本控制**：该文件入 git（`.gitignore` 不排除 `.ai/`）。因此每次重新生成都是一次可评审的 diff；它也随 `git worktree` 检出一起带走，这正是「快照放在仓库内而非父层」的第二个理由。
- **体积预算**：≤ 8000 字符（中英混排约 2700–4000 token，对应 <3000 token 目标）。脚本按 `字符数 / 2.5` 估算 token 并在校验时输出。
- **两个互斥模式**：`--change` 与 `--no-active` 互斥；`verify_delivery_governance.py` 把「无活动 CHG」当作合法状态，故生成与校验两侧必须同时支持它。

## 5. 渐进式加载

读取顺序与三层加载的**唯一落点是 `AGENT-INDEX.md` 第 4 节**：本节不重复其清单，只登记该节不表达的一条理由——

第一层里 `AGENTS.md` 与 `CLAUDE.md` 在治理仓是薄入口，正文与权威仍在 `AGENT-INDEX.md`；顺序之所以固定，是因为它同时约束 `.ai/CURRENT_CONTEXT.md` 生成器与三个工程仓，改动它需要三者同步。

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
| 规范正文归口 | `wt-media-workspace/AGENT-INDEX.md` | 无强制（`verify_agent_entry.py` 只强制入口文件存在性） | 改治理规范只改 `AGENT-INDEX.md`；`AGENTS.md` / `CLAUDE.md` 只保留指针，指针漂移靠人工复核 |
| 入口文件平级 | 各仓 `AGENTS.md` / `CLAUDE.md` | 无强制 | `verify_agent_entry.py` 的漂移检查产出 WARN 供人工复核 |
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

`verify_agent_entry.py::check_entry_drift` 只从各仓 **`AGENTS.md`** 取「被禁止的路径词」，而本仓红线正文在 `AGENT-INDEX.md`、`AGENTS.md` 是薄入口，且 `DRIFT_TOKEN_RE` 要求首段之后的每一段都不含点号 ⇒ **本仓的 forbidden 集合恒为空集**，它那条「0」是**结构性**的，不是「无漂移」的证据。三个工程仓不受此影响。**属既有实现缺口，需独立 CHG**（`CHG-20260925-063` §14）。规则不变：漂移只检测、报告，修正由各仓自行决定（§11）。

## 11. 明确不做

- 不引入 RAG 知识库、自动知识图谱、Agent 调度平台、自动代码路由系统；
- 不引入第二套任务管理系统；
- 不为 `templates/` 建立模板渲染框架；
- 不以脚本自动改写运行时仓库的 `AGENTS.md` / `CLAUDE.md`：漂移只检测、报告，修正由各仓自行决定。
