# Agent Workspace 协作规范

本规范描述 WT Media 多仓库在 AI Agent（Claude Code、Codex 等）协作下的入口、上下文加载与校验约定。它补充 `AGENTS.md` 第十二章，并把散落在脚本与 skill 中的隐含约束显式化。

更新：2026-09-23。

## 1. 不变量

1. `wt-media-workspace` 是治理中心与唯一事实源，不是代码执行中心，也永远不能成为运行时依赖。
2. 每个工程仓库自治：自己维护 `AGENTS.md`、`CLAUDE.md`、`AGENT-INDEX.md`。
3. 执行状态快照全项目**只有一份**，位于 `wt-media-workspace/.ai/CURRENT_CONTEXT.md`。
4. 关联工程路径以 `config/repository-map.yaml` 为准，脚本与文档不得另行硬编码，也不得与之漂移。
5. 运行时改动只发生在对应工程仓库；治理仓库不存放业务代码、构建产物或临时文件。

## 2. 父层定位

执行根 `/…/wt-media/` **已经存在**，且会继续存在。它是仓库容器与 skills 分发目标，承载：

- `AGENTS.md`、`CLAUDE.md`：执行根级别的边界与扫描规则；
- `.claude/skills/`、`.codex/skills/`、`.agents/skills/`：由 `scripts/sync_skills.py` 与 `scripts/prepare_ai_workspace.py` 生成的 skill 副本；
- `wt-media.code-workspace`：编辑器多根工作区定义；
- `wt-media-cloud/`、`wt-media-agent/`、`wt-media-desktop/`、`wt-media-workspace/`：四个独立 git 仓库。

不变量是「**不新增更多中间层**」，而不是「父层不得存在」。父层允许存在容器与分发产物，**不允许**存在第二份执行状态快照或任何治理事实源。

## 3. 入口文件

| 文件 | 作用 | 强制 |
|---|---|---|
| `AGENTS.md` | Codex / OpenAI Harness 入口，同时是治理规范的规范文本 | 必须存在 |
| `CLAUDE.md` | Claude Code 入口 | 必须存在 |
| `AGENT-INDEX.md` | 统一路由：仓库职责、关联仓库、上下文加载规则 | 必须存在 |
| `.ai/CURRENT_CONTEXT.md` | 执行状态快照 | 必须存在，且唯一 |

`AGENTS.md` 与 `CLAUDE.md` 是**平级入口**，不允许互相软链或互相替代。

平级不等于内容可以矛盾。当两者的规则冲突时，Agent 会按 Harness 各自加载到不同结论——这是本规范最需要防守的失败模式。工程仓库中若把 `CLAUDE.md` 写成 `AGENTS.md` 的过期副本，即属违规；正确做法是两者各自独立、内容一致、或由 `CLAUDE.md` 明确声明权威源并**不重复**内容。

`AGENT-INDEX.md` 的第三层要求进入工程后读取该仓 `AGENT-INDEX.md`。若目标仓尚无该文件：不得凭空创建，回退为「本文件 + 该仓 `AGENTS.md`」，并在当前 CHG 中登记该缺口。

## 4. CURRENT_CONTEXT 契约

- **位置**：`wt-media-workspace/.ai/CURRENT_CONTEXT.md`。父层不得存在副本。
- **唯一性**：全项目唯一。`scripts/verify_agent_entry.py` 在父层重新出现副本时直接判错。
- **版本控制**：该文件入 git（`.gitignore` 不排除 `.ai/`）。因此每次重新生成都是一次可评审的 diff；它也随 `git worktree` 检出一起带走，这正是「快照放在仓库内而非父层」的第二个理由。
- **生成方式**：`python3 scripts/prepare_ai_workspace.py --change <CHG>`。禁止手工编辑。
- **体积预算**：≤ 8000 字符（中英混排约 2700–4000 token，对应 <3000 token 目标）。脚本按 `字符数 / 2.5` 估算 token 并在校验时输出。
- **内容**：当前 Milestone、当前 CHG、状态、必读文件顺序、受影响仓库、稳定基线路径、稳定职责边界。
- **禁止写入**：历史记录、完整决策库、历史 spec、临时验证内容。
- **Milestone 专属决策不复制进快照**。快照只保留长期稳定的职责边界；具体决策由当前 CHG 指明其依赖的 Decision 记录，需要时读原文。这样快照不会随 Milestone 更替而漂移。

## 5. 渐进式加载

**第一层（固定）**：`AGENTS.md` → `CLAUDE.md` → `AGENT-INDEX.md` → `.ai/CURRENT_CONTEXT.md`。

**第二层（当前任务）**：`delivery/LEDGER.md`、快照指明的 Milestone、`delivery/active/<change-id>/change.md` 及其 plan/spec/checkpoint。

**第三层（目标工程）**：进入工程仓库后读其 `AGENT-INDEX.md`、`AGENTS.md`、`CLAUDE.md`，再进入代码与测试。

**默认禁止加载**：`delivery/completed`、旧 evidence、历史 decisions、历史 specs、临时实验目录。仅当当前任务明确需要时才加载。

## 6. 多工程并行

- 禁止多个 Agent 同时修改 `.ai/CURRENT_CONTEXT.md`。
- **仅当同一个 CHG 需要多个工程并行实施时**，才建立 `delivery/active/<change-id>/status/`，按 `<repo>.md` 逐仓记录：当前状态、修改内容、验证结果。单仓实施的 CHG 不建该目录。
- 由 workspace 统一汇总，不引入第二套任务管理系统。

已知张力：`delivery/active/` 当前只允许存在一个 CHG，而本节的并行诉求在语义上允许 N 个。当前通过「同一时刻只激活一个 CHG」维持两者相容。若将来确需两个真正并行的 active CHG，必须同时修改第 9 节登记的全部强制点，并同步修订 `AGENTS.md` 第十二章的单数措辞。

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
| 入口文件平级 | 各仓 `AGENTS.md` / `CLAUDE.md` | 无强制 | `verify_agent_entry.py` 的漂移检查产出 WARN 供人工复核 |
| skill 单一源 | `skills/<group>/<name>/SKILL.md` | `sync_skills.py` 分发到 `skills-distribution.yaml` 的 targets | `sync_skills.py check` / `diff`；分组认领由 `verify_agent_entry.py::check_group_coverage` 兜住 |
| 快照由脚本生成 | `prepare_ai_workspace.py` | `planning-wt-media-delivery` skill 第 7 步 | 两者措辞需同时更新 |

## 10. 校验与已知红项

本地手工执行，本仓库当前**不设 CI**（`.github/workflows/` 已移除）。

| 校验 | 状态 |
|---|---|
| `scripts/verify_delivery_governance.py` | 绿 |
| `scripts/verify_agent_entry.py` | 绿（0 ERROR；1 个 WARN 为待复核项，见下） |
| `scripts/verify_skills.py` | 绿（10 个 skill 源文件） |
| `scripts/verify_m0_config.py` | **红 3 项**：`cloud_api` 与 `local_agent_api` 的 `contract_revision` 期望值落后于 `config/contract-map.yaml`；缺失 `.github/workflows/m0-workspace.yml` |
| `scripts/verify_product_master_alignment.py` | **红 9 项**：M2/M3 状态词漂移 2 项、M2/M3 候选关键词缺失 5 项、以及「active CHG 缺 current repository」「active CHG 不得有待决问题」各 1 项 |
| `scripts/verify_m2_acceptance.py` | **红 1 项**：`wt-media-cloud/internal/modules/cloudagent/compatibility.go` 在云仓已不存在 |
| `python3 -m unittest discover -s tests -q` | 45 项中 4 项失败，全部来自上面三个脚本；修完即转绿 |

上述红项**不在 Agent 入口工作范围内**，需各自独立开 CHG 处理。在它们转绿之前，不要假定本仓库门禁整体是绿的。

其中两项与入口工作相邻，值得单独说明：

- `verify_product_master_alignment.py` 的「active CHG current repository is missing」和「must have no pending questions」来自 `CHG-20260916-052` 的记录形状：它使用中文 `- 当前仓库：` 而非 `- Current repository:`，且没有 Pending Questions 节。快照生成器已同时兼容两种仓库写法，但这个校验脚本没有。修正方向是统一记录形状或扩展该校验，未在本次范围内实施。
- 该脚本的 M2/M3 状态词与关键词期望值同样写在脚本里、与当前产品基线脱节，属于同一类「校验脚本内嵌的期望值漂移」问题。这类漂移应通过把期望值迁到可读配置来根治，而不是继续硬编码。

当前已知 WARN：

1. `wt-media-cloud`：`AGENTS.md` 明确不创建 `internal/runtime`，而 `CLAUDE.md` 仍把它描述为资源所有者。云仓自己的规范冲突，修正属于云仓范围，不在治理仓库代改。这是本校验脚本要长期盯住的唯一一条漂移。

已关闭的 WARN（2026-09-23）：`wt-media-cloud`、`wt-media-agent`、`wt-media-desktop` 原先都没有 `AGENT-INDEX.md`，第三层加载规则处于降级状态。三个文件已由 `scripts/init-agent-entry.sh repo <name>` 生成并分别提交到各仓（各仓一次独立提交，只含该文件）；校验脚本的「无 AGENT-INDEX.md」WARN 随之消失。降级条款本身保留，用于将来新增仓库时的缺口登记。

## 11. 明确不做

- 不引入 RAG 知识库、自动知识图谱、Agent 调度平台、自动代码路由系统；
- 不引入第二套任务管理系统；
- 不为 `templates/` 建立模板渲染框架；
- 不以脚本自动改写运行时仓库的 `AGENTS.md` / `CLAUDE.md`：漂移只检测、报告，修正由各仓自行决定。
