# CHG-20260925-065: 三个运行仓入口文件形态统一——参考 workspace 的双指针 + 单一正文

## 1. Basic Information

- Level: S
- Status: DONE
- Created: 2026-09-25
- Current repository: `wt-media-workspace`
- Affected repositories:
  - `wt-media-workspace`
  - `wt-media-cloud`
  - `wt-media-agent`
  - `wt-media-desktop`

**锚点（Level S，按 CHG-060 §3、CHG-20260925-062 §3、CHG-20260925-063 §1、CHG-20260925-064 §1 先例写散文，不引 Milestone）**：`delivery/milestones/` 下 6 篇没有一篇覆盖入口文件形态或治理卫生（与 CHG-063／CHG-064 同一读数，grep 零命中）；`scripts/verify_delivery_governance.py:125` 只对 `Level: M/L` 强制 `- Milestone:`。

**本 CHG 与上述四条 S 级先例的唯一差别，也是最需要被审的一点**：那四条都写明「三个运行仓只被读、不被写」（如 `delivery/completed/CHG-20260925-063/change.md:11`），**本 CHG 会写三个运行仓的入口文件**。已在此声明一次，并在 §4、§5、§9 各落一次，收尾时逐仓对账。写入范围**仅限** `CLAUDE.md`、`AGENTS.md`、`AGENT-INDEX.md`、`DIRECTORY_MAP.md` 四类入口文件与各仓自有的 `.claude/skills`／`.codex/skills` 分发副本；**不写任何运行时代码、配置或测试**。

## 2. Change Goal

把三个运行仓的入口文件收成**用户指定的形态**：参考 `wt-media-workspace`——`CLAUDE.md` 与 `AGENTS.md` 都是**指针**，`AGENT-INDEX.md` 作为**正式内容的唯一落点**；并让该形态**可机检**，使「同一套规则写成两份互相矛盾的副本」这一失败模式在结构上不可能发生。

单一可验收结果：每个仓的四类入口文件各归其位，`scripts/verify_agent_entry.py` 对四仓**零 ERROR**，且该脚本新增的每一条 ERROR 都**被证明能失败**。

## 3. Baseline References

- 治理规范正文：`AGENT-INDEX.md`（§2 红线、§3 知识地图、§4 读取顺序、§5 仓库职责、§8 交付治理、§10 入口文件表、§11 多 Agent 并行、§12 校验）
- 形态规范：`docs/engineering/specs/agent-workspace-conventions.md` §3（本 CHG 就地改写）
- 架构验收：`docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md:769`（入口规则与仓库规则）、`:1801`（仓库 acceptance）
- 交付模板与治理：`templates/delivery/change.md`、`delivery/MASTER_IMPLEMENTATION_PLAN.md` §3／§4／§7
- 参照件（**本 CHG 的形态标准**）：`CLAUDE.md`、`AGENTS.md`
- 上一轮同类处置（先例与边界）：`delivery/completed/CHG-20260925-064/change.md`、`.../CHG-20260925-063/change.md`、`.../CHG-20260925-062/change.md`

## 4. Current Facts

以下全部为本 CHG 开工前实测读数，命令与分母见 `evidence/task-01-baseline.md`。

**F-01 三仓入口文件形态互不相同，且无任何规定约束其内容。**
`AGENT-INDEX.md` 三仓七个 H2 **逐字同序**（依赖／定位／本仓库拥有／本仓库不拥有／需求路由／禁止／上下文加载顺序）——**靠互相模仿，不靠规定**；`AGENTS.md` 在 agent 与 desktop 是同一模板，**cloud 完全不用该模板**；`CLAUDE.md` 有**三种形态**，cloud 的那份是**另一类产物**（168 行规则正文，含 9 个 H1）。体量：`CLAUDE.md` cloud 2715 B/168 行、agent 226 B/10 行、desktop 283 B/12 行；`AGENTS.md` 6046 B/113、3705 B/45、3170 B/39；`AGENT-INDEX.md` 4357 B/60、4668 B/65、8193 B/75；`DIRECTORY_MAP.md` 7449 B/105、9886 B/117、12036 B/90。

**F-02 参照件已经是目标形态。** `wt-media-workspace` 的 `CLAUDE.md` 1755 B/28 行与 `AGENTS.md` 1267 B/22 行**均为纯指针**，正文在 `AGENT-INDEX.md`（12736 B/209 行）。

**F-03 `wt-media-cloud` 的两个入口文件是同一套规则的两份互相矛盾且都已过期的副本，而门禁报 0 warning。** 已实测的分歧 ≥6 处：

| # | `CLAUDE.md` 一侧 | `AGENTS.md` 一侧 | 实况 |
|---|---|---|---|
| 1 | `:76` 基础资源「必须通过 Runtime 获取」 | `:17`「不创建 `internal/runtime`」 | **直接对立** |
| 2 | `:37-42` `internal/infra` 列 `redis` | `:18` 列 `cache`／`storage` | 磁盘实为 `client database logger metrics tracing`——**两份都错** |
| 3 | `:113-121` `time.NewTicker` 绝对禁止 | 仅 `internal/scheduler` 允许 | `AGENTS.md` 一侧较准 |
| 4 | `:129-135` 模块树 `handler/service/repository/model/dto` | 同侧 | 磁盘上有 `router.go`，两份都漏 |
| 5 | `:23` 与 `:27` 同文件内 `## internal/bootstrap` 重复且内容相抵 | — | 文件自身重复 |
| 6 | 9 个 H1，其中 `## 禁止扫描` 是第二个 H1 | 同 | 标题层级不合法 |

`docs/engineering/specs/agent-workspace-conventions.md:34` 亲口把「工程仓库中若把 `CLAUDE.md` 写成 `AGENTS.md` 的过期副本」判为**违规**，并称之为「本规范最需要防守的失败模式」。

**F-04 门禁现状：`scripts/verify_agent_entry.py` exit=0、0 warning，而 F-03 与 F-05～F-07 同时成立。** 已做阳性对照：注入 fixture 后 `check_entry_drift` 报出、删 `AGENT-INDEX.md` 后 `check_layer3_entries` 报出 ⇒ 该 0 是「范围不够」，不是「检查空转」。`check_layer3_entries` 只查 `AGENT-INDEX.md` **是否存在**（WARN 级），并**无任何脚本检查 `DIRECTORY_MAP.md` 是否存在**，尽管 `AGENT-INDEX.md:71`、`:120` 与 `scripts/prepare_ai_workspace.py:172` 三处点名要求它。

**F-05 跨仓强度冲突。** `wt-media-cloud/AGENTS.md:10` 把 `docs/superpowers/specs/2026-09-18-cloud-foundation-convergence-design.md` 称作**完整设计基线**；而 `AGENT-INDEX.md:58` 规定 `docs/superpowers/` 是**分析材料，不作为新开发依据**。同一个事实类在两个入口上强度相反，取决于 harness 加载了哪一个。

**F-06 读取顺序三处重复落点。** `AGENT-INDEX.md:62` 声明 §4 是「全项目唯一落点」，而三个运行仓的 `AGENT-INDEX.md` 各自另有一份 `## 上下文加载顺序`，且都把「本文件」列为第 1 项。CHG-20260925-064 T-04 计的「5 处手写」**未含这三处**。

**F-07 目录事实双重落点。** 「禁止扫描区」在 `AGENT-INDEX.md` 末行与 `DIRECTORY_MAP.md` 各存一份（cloud `:60` ⟷ `DIRECTORY_MAP:98`；agent `:65` ⟷ `:115`；desktop `:75` ⟷ `:86`）。`wt-media-cloud/AGENTS.md:12-21` 的目录树是 `DIRECTORY_MAP.md:15-62` 的第二份，且是 F-03 表 #2／#4 陈旧事实的所在地。

**F-08 生成器写出的形态与六个实际文件一个都不匹配。** `scripts/init-agent-entry.sh:132-160` 产出 `# <repo> Agent Index`／`## Workspace`／`## Rule`（英文正文），且**只写 3 件文件**——今天跑一次就产出一个不合门禁的树。`:79-85` 还**手写** `.ai/CURRENT_CONTEXT.md`（`- Status: ACTIVE`／`- Active CHG: TBD`），而 `verify_delivery_governance.py:12` 的 `CONTEXT_RE` 要求反引号包裹 ⇒ 该文件被静默读成 `None`，`check_delivery_pointers` 空转；这与「该文件只有一个生成器、禁止手写」的教条直接相抵。

**F-09 desktop 的发布链路依赖 workspace 检出（政策冲突，本 CHG 只改措辞）。** `wt-media-desktop/src-tauri/tauri.conf.json:10` 把 `../wt-media-workspace/scripts/build-desktop.sh` 设为 `beforeBuildCommand` ⇒ desktop 发布包**离开 workspace 检出就构建不出来**，与 `..._V1.md:478`「三个运行仓库不得在**编译**或运行时依赖 Workspace」和 `:1801`「三个运行仓库可独立构建」相抵。该安排是有记录的（CHG-20260923-059 D-20），本 CHG **不改机制、不改红线**，只把入口文件里的措辞补上范围限定（D-04）。

**F-10 harness 事实（决定形态可行性）。** 安装版 **2.1.273**：Claude Code 原生只加载 `CLAUDE.md`；`AGENTS.md` 的原生回退**自 2.1.277 起**，且两文件并存时默认被忽略。Codex 侧只读 `AGENTS.md`。⇒ 两个指针是**必需的**，重复只出在「正文被写两遍」。

**F-11 三仓拿不到 workspace 组 skill。** `config/skills-distribution.yaml` 不向 cloud／agent／desktop 分发 `workspace` 组，故 cwd 在运行仓的会话磁盘上没有 `executing-wt-media-change`；其唯一治理指针就是该仓 `AGENT-INDEX.md`。⇒ 正文放在 `AGENT-INDEX.md` 恰好是那个会话必然要读的文件。**本 CHG 不修此项**（见 §5）。

**F-12 `check_entry_drift` 的 workspace 臂早已恒空**（CHG-20260925-063 §14、CHG-20260925-064 §14 均登记为「需独立 CHG」）；本 CHG 把三仓两个入口文件改成指针后，其**其余三臂也会结构上恒空**。

## 5. Scope

本清单在 T-01 **封闭**。T-05～T-07 途中的新发现只登记 §14，**除非**落在已列举的 A／B／D-措辞／E／F 之内。

### Add

- `AGENT-INDEX.md` §10 的 `DIRECTORY_MAP.md` 行（强制＝必须存在（运行仓））＋ 本 CHG 的入口文件角色表指针。
- `docs/engineering/specs/agent-workspace-conventions.md` §3 改写为「入口文件形态」：角色表／must／must-not／指针预算／机读键语法／规则词判据／「重复只在生成物与其生成器之间存在」判别句。
- `scripts/verify_agent_entry.py` 新六条检查（见 §8 T-04）。
- 三个运行仓 `AGENT-INDEX.md` 的 `## 本仓规则` 节（承载原 `AGENTS.md` 的规则正文）。
- `delivery/active/CHG-20260925-065/`（本记录、`checkpoint.md`、`evidence/`）。

### Modify

- `AGENT-INDEX.md`：§4 补「本仓内顺序」作用域句；`:193` 处 `verify_agent_entry.py` 的一句描述同 T-04 commit 改。
- `CLAUDE.md`、`AGENTS.md`（workspace）：补机读键 `- 正文：\`AGENT-INDEX.md\`` 使其过机检（二者已是纯指针，内容不动）。
- 三个运行仓各四类入口文件：重写为形态（见 §8 T-05～T-07）。
- `scripts/init-agent-entry.sh`：heredoc 改双指针 ＋ 八节骨架 ＋ 新增 `DIRECTORY_MAP.md`；`:79-85` 停止手写 `.ai/CURRENT_CONTEXT.md`。
- `docs/engineering/architecture/..._V1.md:1801` 就地扩为五种文件＋形态要求＋点名门禁；`:769` **保留**并补一句使其自洽（Workspace 提供**形态**，运行仓提供**内容**）。
- `delivery/LEDGER.md` 表行与归档说明。

### Delete

- `scripts/verify_agent_entry.py` 的 `check_entry_drift` 与 `tests/` 中对应的 2 条用例（`test_forbidden_path_described_in_claude_md_is_warned`、`test_path_forbidden_in_both_files_is_not_warned`）。
- `conventions §9–§10` 与 `AGENT-INDEX.md` §10 中描述 `check_entry_drift` 的段落。
- 三个运行仓 `AGENT-INDEX.md` 末行的禁止扫描区清单（换成指向 `DIRECTORY_MAP.md` 的指针）与 `AGENTS.md`／`CLAUDE.md` 的规则正文（**迁入** `AGENT-INDEX.md`，逐条归属表见 T-05～T-07 证据）。
- 无内容删除：**本 CHG 不删任何运行时代码、配置、测试，也不删 `delivery/completed/` 的任何内容**。

### Explicitly Not Doing

- **不自动改写运行仓入口文件**（`conventions §11:151`「不以脚本自动改写运行时仓库的 `AGENTS.md`／`CLAUDE.md`：漂移只检测、报告」、`..._V1.md:769`）。生成器只做「从零初始化」，**不加 `--fix`**。
- **不改 `AGENT-INDEX.md:35` 的红线措辞，不改 `..._V1.md:478`／`:1801` 的依赖判定，不动 `build-desktop.sh` 的归属**（F-09；用户 2026-09-25 裁定「只修入口文件措辞，政策另立 CHG」）。只登记，见 §14。
- **不把 cloud 的规则骨架压平**成 agent／desktop 的四节，也不为一致把 agent／desktop 吹到 cloud 的规模——约束的是**角色**，不是章节结构。
- **不判 `AGENT-INDEX.md` 与 `AGENTS.md` 的语义不矛盾**——只能机检行级重复（WARN）。
- **不查 `DIRECTORY_MAP.md` 的内容**，只查存在性。
- **不并进「三仓 skill 分发」**（F-11，独立 closure）。注意 `delivery/completed/CHG-20260925-064/change.md` §14 第 16 项：desktop `.gitignore:10-11` 忽略 `.claude`／`.codex`，加分发有已知陷阱。
- **不建 `delivery/active/<CHG>/status/`**：`AGENT-INDEX.md:184` 规定仅同一 CHG 多工程**并行**实施时才建；本 CHG 三仓是**顺序**实施。
- **不动 `delivery/completed/`**——归档边界与体量属 CHG-20260925-066（用户裁定：先入口文件、后归档边界）。
- **不给「里程碑文件头的状态声明」新增一致性判据**（与 CHG-20260925-063 的判据分层结论相悖）。
- **不动 `MASTER` §3 的读数列**（随每次归档漂移的机制无对策，CHG-20260925-064 §14 第 7 项已登记）。

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | 三仓入口形态**参考 workspace**：`CLAUDE.md` 与 `AGENTS.md` 都是指针，`AGENT-INDEX.md` 作为正式内容。用户 2026-09-25 裁定。 | CONFIRMED |
| D-02 | **不采用 `@AGENT-INDEX.md` 导入**：①偏离 D-01 指定的参照件（其 `CLAUDE.md` 是纯指针，机制已验证）；②破坏四仓形态一致，机检需多一条豁免；③每会话白付 3–4k est. tokens；④上游 #58940 下子代理经 Agent 工具启动时导入不展开，主会话与子代理行为不一致，比纯指针更不可预测。 | CONFIRMED |
| D-03 | Level **S ＋ 散文锚点**，不新建里程碑卡（为满足级别门禁而新造一张没有用户可见成功事实的里程碑卡，正是 CHG-063／CHG-064 一直在剪掉的那类空转产物）。用户 2026-09-25 裁定。 | CONFIRMED |
| D-04 | F-09 的处置：**只改入口文件措辞**（`desktop/AGENTS.md:30` 补范围限定），红线与两行 architecture 不动，政策另立 CHG。用户 2026-09-25 裁定。 | CONFIRMED |
| D-05 | **`check_entry_drift` 在本 CHG 退役**，由形态判据顶替（新形态下其四臂结构上恒空，留着就是一个「绿因为它瞎」的门禁，与 CHG-20260925-063 处置的僵尸门禁同类）。用户 2026-09-25 裁定。 | CONFIRMED |
| D-06 | 冲突取侧：cloud 的分歧**逐处取 `AGENTS.md` 一侧**（它未经 F-03 表 #1 那样的直接对立），但两处事实错误按**代码实况**回写（infra 列实测值、模块树补 `router.go`）——是「按代码回写文档」，不是二选一。 | CONFIRMED |
| D-07 | 读取顺序两侧同时改（F-06）：三仓小节改名 `## 本仓内加载顺序` ＋ 作用域首行；workspace §4 补作用域句。**不删**那三份清单——cwd 在运行仓时它是唯一在上下文里的那份。 | CONFIRMED |
| D-08 | 统一化**只搬家不改义**（D-06 列举的事实错误除外）；逐仓逐条归属表以改前行数为分母，被移走的每一行都能指到目的地。 | CONFIRMED |

## 7. Pending Questions

None.

## 8. Implementation Tasks

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | 激活：建 active 记录、§5 封闭、LEDGER 表行、快照 `--change`、记录四仓基线 | DONE | `verify_delivery_governance.py`／`verify_agent_entry.py` `exit=0`；LEDGER 表行合 `LEDGER_ROW_RE`；四仓 `git status --porcelain` 基线入 evidence |
| T-02 | 规范与落点成文（`conventions §3`／§9／§11；`AGENT-INDEX.md` §4／§10；`..._V1.md:769`／`:1801`） | DONE | 判据串**先写后实现**（代码中 6/6 为新 ≙ 0）；读数带前后对照（锚 `bd5df2c`）；阳性对照 10/10。evidence `task-02-normative.md` |
| T-03 | 生成器对齐（`init-agent-entry.sh` 双指针＋八节骨架＋`DIRECTORY_MAP.md`；停止手写快照）；**并改正 §3 指针预算的自我矛盾** | DONE | 在 tmpdir 实跑，产出四件与形态规定逐项相符（12/12，附差异表）；阳性对照 7 类变异。evidence `task-03-generator.md` |
| T-04 | 门禁实现与退役（新六条 ＋ 退役 `check_entry_drift` ＋ `tests/` fixture 重写为默认合规） | DONE | **六条新检查各做变异对照**：关掉判定 → 各 3／7／4／2／2／1 条用例失败，**`ImportError` 计数 6 次全为 0**；`tests/` 16 → **31** 条，套件 `Ran 79` → **`Ran 94` / OK**；其余五门禁仍 `exit=0`。真树读数 **71 ERROR**（= T-05～T-08 的分母，见 `checkpoint.md`）。evidence `task-04-gate.md` |
| T-05 | cloud 四件入口文件收口（正文迁入 `AGENT-INDEX.md` 的 `## 本仓规则`；落实 F-03／F-05／F-07） | DONE | 逐条归属表分母＝改前非空行数（86／99／45／75，各类加总等于分母）；门禁 cloud **51 → 1**（自身缺陷 0，剩余一条是跨仓序列，T-06／T-07 前不可满足）；阳性对照：注入 `cache` → infra 扫描报出、改前提交 `0346edf:AGENT-INDEX.md` → 排除清单扫描命中 1。提交 `0db02ab`。evidence `task-05-cloud.md` |
| T-06 | agent 四件入口文件收口 ＋ F-07 | DONE | 逐条归属表分母＝改前非空行数（34／6／48／88，四列加总等于分母；`DIRECTORY_MAP.md` 纯增量）；门禁 agent **10 → 0**，四仓合计 **71 → 11**（余 desktop 8／workspace 3）；两处非机械判定已逐条归位（13 行模块树 → `DIRECTORY_MAP.md`；1 行「文件与 FFmpeg 运行时」按代码回写为「尚无实现」）；阳性对照：`24da21b:AGENT-INDEX.md` → 命中 1，**且未改动的 desktop 仍命中 1**；点名路径 25/25 存在（注入假路径 → 报出）；指针 8 链接全 resolve（注入 → 报出）。提交 `6d740fc`。evidence `task-06-agent.md` |
| T-07 | desktop 四件入口文件收口 ＋ F-07 ＋ D-04 的范围限定句 | DONE | 逐条归属表分母＝改前非空行数（28／7／59／68，四列加总等于分母）；门禁 desktop **8 → 0**，四仓合计 **11 → 3**（余 workspace 3）；**跨仓八节相等判据本 Task 转绿**（三仓 `## 本仓规则` 同落位置 6）；12 行模块树迁入 `DIRECTORY_MAP.md`（该图本就有更精确版本，`3 行空壳` 一句另按磁盘复核为四个 `mod.rs` 各 3 行）；D-04 写成两条（工具依赖／产物与运行期不依赖 Workspace）；排除清单里不存在的 `../generated` 按代码回写删除；`tauri.conf.json` 与发布链路未动。提交 `7c1b0ad`。evidence `task-07-desktop.md` |
| T-08 | workspace 入口文件补机读键过机检（二者已是纯指针，内容不动） | DONE | 改前锚 `23eeaa6`。三处改动（5 增 1 删）：两文件各加机读键（`AGENTS.md` **只增不减**）＋ `CLAUDE.md:9` 由规则句改为指针句——该事实的唯一落点本就在 `AGENT-INDEX.md:23` §1 第 6 行，故是**改指针、不是搬家**，删掉的是第二份。门禁 workspace **3 → 0**，**四仓合计 0 ERROR / 0 WARN**（`check_rule_text_duplication` 分母 97 句／11 文件／4 仓，与 T-07 同分母）；阳性对照**两条**：真树上删键 → 报出、还原逐字节相同，另按改前提交还原 → 恰报出那三条 `exit=1`。提交 `50a2417`。evidence `task-08-workspace.md` |
| T-09 | 收尾：归档、LEDGER 同步、快照 `--no-active`、两遍失效指针扫描、§14 登记 | TODO | 六门禁 `exit=0` ＋ `unittest`，**在最后一次改动之后**重测；四仓对账 |

**中间态必然见红**：T-04 落地后、T-07 完成前，三仓门禁是红的。这是预期的，**已在 `checkpoint.md` 说明**——CHG-20260925-063 的教训是「意料外的红会训练读者忽略这个门禁」。**T-09 不得早于 T-07。**

每次改动后跑：`python3 -B -X pycache_prefix=/tmp/pyc-none scripts/verify_*.py` 与 `python3 -B -X pycache_prefix=/tmp/pyc-none -m unittest discover -s tests -q`。

## 9. Repository Checklist

### wt-media-workspace

- [x] `AGENT-INDEX.md` §4／§10、`conventions §3／§9／§11`、`..._V1.md:769／:1801`（T-02）
- [x] `AGENT-INDEX.md` §12 里 `verify_agent_entry.py` 的旧描述（`各仓入口漂移 WARN`）——**T-04 同 commit 改**；按**内容**定位（T-02 的 §10 加行后它由 `:193` 漂到 `:198`，按行号改会改错句）
- [x] `scripts/init-agent-entry.sh`（T-03：全文重写为 §3 形态，停止手写快照）、`conventions §8`（补两条约束）
- [x] `scripts/verify_agent_entry.py`、`tests/test_verify_agent_entry.py`（T-04）
- [x] `CLAUDE.md`／`AGENTS.md` 机读键（T-08）：两文件各 1 行键；`CLAUDE.md:9` 的复述句改为指针（3 处改动、5 增 1 删）；`CLAUDE.md` 30 行／1796 B／3 H2，`AGENTS.md` 24 行／1296 B／2 H2
- [ ] `delivery/` 记录与 LEDGER（T-09）

### wt-media-cloud

- [x] `AGENT-INDEX.md` 60 → 205 行（新增 `## 本仓规则`，吸收原 `AGENTS.md`／`CLAUDE.md` 的规则正文）
- [x] `AGENTS.md` 113 → 11 行（指针）
- [x] `CLAUDE.md` 168 → 11 行（指针，原 168 行规则正文迁出）
- [x] `DIRECTORY_MAP.md` 105 → 106 行（接收 `AGENTS.md` 的 `.gitignore` 扫描范围）
- [x] **未写**：任何运行时代码、配置、测试（`git status --porcelain` 仅 4 个 `M` ＋ 既存 `?? dump.rdb`）
- [x] 提交 `0db02ab`

### wt-media-agent

- [x] `AGENT-INDEX.md` 65 → 92 行（新增 `## 本仓规则`；加载顺序改名＋作用域首行；排除清单换指针）
- [x] `AGENTS.md` 45 → 11 行（指针，原 34 非空行正文迁出）
- [x] `CLAUDE.md` 10 → 11 行（指针）
- [x] `DIRECTORY_MAP.md` 117 → 118 行（补 `local_api/health.py` 行 ＋ `pyproject.toml` 可安装包一句；diff 为纯增量）
- [x] **未写**：任何运行时代码、配置、测试（`git status --porcelain` 仅 4 个 `M`）
- [x] 提交 `6d740fc`

### wt-media-desktop

- [x] `AGENT-INDEX.md` 75 → 99 行（新增 `## 本仓规则` 三节；加载顺序改名＋作用域首行；排除清单换指针）
- [x] `AGENTS.md` 39 → 11 行（指针，原 28 非空行正文迁出）
- [x] `CLAUDE.md` 12 → 11 行（指针）
- [x] `DIRECTORY_MAP.md` 90 → 92 行（禁止扫描区补「唯一落点」说明与 `../generated` 处置）
- [x] D-04 的范围限定句落在 `### 前端产物与 Workspace 依赖`
- [x] **不写**：`src-tauri/tauri.conf.json`、发布链路（实测取值已记入 evidence）
- [x] **未写**：任何运行时代码、配置、测试（`git status --porcelain` 仅 4 个 `M`）

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | 四仓 `CLAUDE.md` 与 `AGENTS.md` 皆含机读键 `- 正文：\`AGENT-INDEX.md\``，目标存在 | 新 `check_pointer_shape`；每仓逐条报出 | **PASS**（T-08）：**8/8** 组合全绿；阳性对照两条——真树删 workspace `AGENTS.md` 的键 → 报出，改前提交 `23eeaa6` 还原 → 恰报出「两文件 no rule body」 |
| AC-02 | 四仓指针文件不含被复述的规则句（规则词行的同一行须出现正文文件名） | 同上；阳性对照：把 cloud `AGENTS.md` 的 `## 模块规则` 段贴进 `CLAUDE.md` → 报出 | **PASS**（T-08）：workspace 两个指针各 1 条规则词行（皆末段红线句，同现正文名）；改前 `CLAUDE.md:9` 的复述句对 `23eeaa6` 报出 ⇒ 判据有判别力 |
| AC-03 | 四仓指针文件 H2 ≤ 4、行数 ≤ 30、字节 ≤ 2000，规则词判据只作用于非标题行（**T-03 改正后**的 §3 判据——`H2 ≤ 1` ＋ 白名单 `权威源` 与自己引用的参照件相抵，已退役，见 §14 第 7 项） | 同上；变异：灌水到 37 行／超 H2 → 报出 | **PASS**（T-08）：三仓各 11 行／656 B／1 H2；workspace `CLAUDE.md` 30 行／1796 B／3 H2、`AGENTS.md` 24 行／1296 B／2 H2——均在界内 |
| AC-04 | 运行仓四类入口文件皆存在且非空 | 新 `check_repo_entry_files`；变异：`rm` 任一 → 报出仓名＋文件名 | **PASS**（T-07）：三仓四件齐备非空；T-04 已做变异对照（`rm` → 报出仓名＋文件名） |
| AC-05 | 同仓各指针声明的正文同一，且正文不再声明正文（无环） | 新 `check_rule_body_consistency`；变异：造 `A→B, B→A` → 报出 | **PASS**（T-07）：门禁 `disagree on the rule body`／`declares itself`／`declares a pointer as the rule body`／`declares an unknown rule body` 四类现均为 0；T-04 已做变异对照 |
| AC-06 | 三仓 `AGENT-INDEX.md` 八 H2 序列互相相等且长度为 8 | 新 `check_layer3_shape`；变异：改名 desktop 的 `## 禁止` → 报出首个分叉位 | **PASS**（T-07）：三仓八 H2 逐字同序、长度 8，门禁不再报分叉（该判据自 T-04 起红至 T-07，其红只能由三仓齐备消） |
| AC-07 | 每一条新 ERROR 都被证明能失败（变异式，非 `ImportError`） | `tests/` 用例断言**完整错误集合逐条相等** | **PASS**（T-04）：六条新检查逐一禁用 → 3／7／4／2／2／1 条用例失败，`ImportError` **0**；`Rule Word` 类判据另有注入式阳性对照。读数见 `task-04-gate.md` §3 |
| AC-08 | `check_entry_drift` 及其 2 条用例、描述段落已退役，且同 fixture 由新检查顶替 | 变异对：旧代码＋旧 fixture → 漂移 WARN；新代码＋同一 fixture → `check_pointer_shape` 报出 | **PASS**（T-04）：代码中 `check_entry_drift`／`check_layer3_entries` 命中 0；旧 2 条用例已删；fixture 改为「默认合规」后由 `check_pointer_shape` 等六条顶替，且每条都被变异点亮 |
| AC-09 | cloud 的 F-03 表 6 处分歧逐处消解，两处事实错误按**代码实况**回写 | `internal/infra` 实际目录逐项相符（阳性对照：写一个不存在的目录 → 报出）；模块树含 `router.go` | **PASS**（T-05，cloud 臂）：infra 枚举 5 项与磁盘相符 missing **none**，注入 `cache` → 报出；模块树取 `AGENTS.md` 侧（已含 `router.go`／`handler.go`），`CLAUDE.md` 那份错误清单不迁移。**但见 §14 第 11 项：判据是我在证据期临时构造的扫描，非门禁** |
| AC-10 | 每仓逐条归属表覆盖被移走的**每一行**，分母＝改前行数 | 逐文件 `wc -l` 前后对账，无一项落入「未登记」 | **三仓全 PASS**：cloud（86／99／45／75）、agent（34／6／48／88，`DIRECTORY_MAP.md` 为纯增量 diff）、desktop（28／7／59／68）——每一列加总等于其分母，无「未登记」项 |
| AC-11 | 三仓 `AGENT-INDEX.md` 的禁止扫描区清单已换成指向 `DIRECTORY_MAP.md` 的指针 | 字符串扫描：命中 0（阳性对照锚**改前提交**，另注入 1 条 → 报出） | **三仓全 PASS**：cloud 命中 **0**（对 `0346edf` 命中 1）、agent 命中 **0**（对 `24da21b` 命中 1）、desktop 命中 **0**（对 `623583d` 命中 1）。**判据收窄过**：只查 `扫描` 在已修好的文件上报 2／3 条全假阳性，故「枚举构建路径」是承重构件（§14 第 15 项） |
| AC-12 | F-06 两侧同时改：三仓小节改名＋作用域首行；workspace §4 作用域句 | 逐处复查；`check_local_order_scope` WARN 为 0 | **PASS**（T-07）：三仓小节均已改名 `## 本仓内加载顺序` 并带作用域首行；`AGENT-INDEX.md` §4 作用域句在 T-02 已落；门禁 WARN **0** |
| AC-13 | F-08：`init-agent-entry.sh` 产出四件且形态相符；快照只有**一个**生成器 | tmpdir 实跑 ＋ 产出差异表；脚本内无 `.ai/CURRENT_CONTEXT.md` 写入 | **PASS**（T-03）：12 项形态判据 12 PASS；阳性对照 7 类变异全报出；`workspace --dry-run` 对快照只报 `exists:` 不再 `would create:`。读数 **不是门禁**（门禁在 T-04），届时调门禁自己的函数复测 |
| AC-14 | 四仓零运行时代码／配置／测试改动 | `git -C ../wt-media-{cloud,agent,desktop} status --porcelain` 逐仓对账；只允许四类入口文件与 `.claude/skills`／`.codex/skills` 副本 | **PASS**（T-09）：逐仓 `diff --stat <改前提交>..HEAD` 各只落在四件入口文件（cloud `0346edf..HEAD`＝4 文件、agent `24da21b..HEAD`＝4、desktop `623583d..HEAD`＝4），**每仓恰一个提交**；工作区 agent／desktop 净、cloud 仅既存 `?? dump.rdb`（他人在途，不碰）。四仓对账读数见 `t09-repo-reconcile.out` |
| AC-15 | 六门禁 `exit=0` ＋ 套件全绿，且读数取于**最后一次改动之后** | `evidence/artifacts/t09-gate-readings.out` | **PASS**（T-09）：六门禁全 `exit=0` / 0 ERROR，`unittest` `Ran 94 / OK`，`sync_skills.py check` `exit=0`；**取于归档与全部记录改动之后** |
| AC-16 | 两遍失效指针扫描（字符串 ＋ 相对链接 resolve），各带阳性对照与分母 | 扫描产物入 `evidence/artifacts/` | **PASS**（T-09）：分母 **477 个已跟踪 `*.md` / 48938 行 / 115 条相对链接**；Pass A 活跃文档命中 **0**（13 处全在本 CHG 自己的记录里，属过去时叙述）、Pass B 未解析 **6**（全在已归档的 CHG-052 记录，少一级 `..`，登记 §14 第 20 项）；**本 CHG 自有死链 0**。对照**双向**做：散文里的缺陷报出、同一缺陷放进代码块则不报（证明"跳过代码"不是把扫描器弄瞎） |

## 11. Evidence

证据落在 `evidence/`，只记事实（命令／动作、期望、实际、结论），不重复需求。文件名与内容**设上限**：单 Task evidence ≤ 3 KB，原始输出进 `evidence/artifacts/`。

- `evidence/task-01-baseline.md`（含四仓 `git status --porcelain` 基线与开工 commit）
- `evidence/task-0x-<topic>.md`
- `evidence/artifacts/`（原始命令输出）

**记录成本上限**：本 CHG 的**全部记录与证据合计 ≤ 80 KB**——`change.md` ＋ `checkpoint.md` ＋ `evidence/*.md` 三者之和，一条命令可量。

**本节曾两次凭印象设数，都被实测推翻，记在此以免第三次**（与「计数必须当场量」同一条纪律）：

| 版本 | 数字 | 实测结果 |
|---|---|---|
| 初稿 | `change.md` ≤ 25 KB、单 Task evidence ≤ 3 KB | T-01～T-04 四篇 evidence 4559／4845／6314／6329 B，**逐篇突破**；T-04 收尾 `change.md` 26477 B，突破 |
| T-04 改 | `change.md` ≤ 30 KB、单 Task ≤ 8 KB | T-05 后 `change.md` 30191 B、`task-04-gate.md` 8749 B，**两个都再次突破** |
| 本轮 | **合计 ≤ 80 KB** | T-05 收尾实测 **75182 B**（≈ 73 KB）。**T-06 时该界已被证伪**：只剩 T-07／T-08／T-09 三篇证据，按实际单篇 4.5–8.7 KB 必然越过 80 KB——界设错了，见下 |
| T-06 改 | **速率界**：`change.md` ≤ 35 KB、`checkpoint.md` ≤ 15 KB、单 Task evidence ≤ 9 KB；**总量只报不设顶**，以 `CHG-20260925-064` 实测的 **213739 B** 为对照基准 | T-06 收尾三条界**全部成立**；**T-07 收尾时前两条被突破**（`change.md` 37701 B＞35840、`checkpoint.md` 15418 B＞15360）。**第五版见下** |
| T-07 改 | **真速率界（增量）**：每个 Task 的记录增量 ≤ `change.md` 5 KB、`checkpoint.md` 4 KB、单 Task evidence 9 KB | T-06／T-07 四段在界内；**T-08 的 `checkpoint.md` 增量越界**（4096 B 界，实测见 `artifacts/t08-record-size.out`）——**界不因越界而改**，原因是 T-08 顺带补上了 T-04～T-07 五行缺失的 `Completed` 条目，替前四个 Task 付了它们的记录成本，见 §14 第 19 项。逐次读数以 `artifacts/t0{6,7,8}-record-size.out` 为准，**本表不内联具体数字**：内联过一次，随后两次改稿就把它变成旧值（§14 第 14 项的同一错法）。绝对值**只报不设顶**；存量见 `artifacts/t08-record-size.out` 末行 |

**第四版依然错了，而且错法与前三版是同一个：我限的都是「存量」。** 35 KB／15 KB 看起来像速率（它带单位、带时限感），实际仍是**对一份累积文档设的绝对上限**——`change.md` 每完成一个 Task 就加 §8 表行、§10 判据行、§14 登记项，`checkpoint.md` 每完成一个 Task 就加一张收尾读数表；**存量由任务数决定，不由我决定**。所以第四版和前三次一样，会在某个 Task 上被突破，而这一次我并不知道会在哪个 Task。**把界改小改大都不是修复；被限制的量选错了。**

⇒ 第五版换成**真正的速率：每个 Task 的增量**。实测四段增量（T-06／T-07 各自的 `change.md` 与 `checkpoint.md`）最大值 `change.md` **4601 B**、`checkpoint.md` **3015 B**，故界设在 **5 KB／4 KB**——留约 8%／30% 余量，且**它是可长期成立的**（判据：连续三个 Task 的增量都不越界）。**存量只报不设顶**，T-09 收尾时报告最终值并与 064 的 213739 B 对比。**界从「文档多大」改成「每写一个 Task 涨多少」——这才是记录成本真正的驱动量。**

前两版错在同一件事：**拿「单篇字节数」当界**。它既拦不住总量增长（每篇各超一点，合计照样膨胀），又会诱使我把证据写得比判据更短——**为迁就一个我自己发明的数字去削证据，比数字被突破更糟**。故第三版改设在**总量**上，且**同一命令量两侧**：`cat change.md checkpoint.md evidence/*.md | wc -c`。CHG-20260925-064 用同一条命令实测 **213739 B**（≈ 209 KB）——此前引用的「94 KB」只算了 `change.md` ＋ `checkpoint.md`，漏了 evidence——**本 CHG 第二次「两个分母混用」**（第一次在 T-05 归属表，把总行数与非空行数当同一个分母；见 `checkpoint.md` 的 T-05 自纠与 `evidence/task-05-cloud.md` §3）。⇒ 本 CHG 比 064 小约 **2.9 倍**（不是先前误写的「一个数量级」）。

**第三版也错了，错法更值得记：总量界的真值不是我写的那个数，是「任务数 × 每篇大小」。** 9 个 Task／16 条 AC／4 个仓，证据随 Task 数线性长；写「≤ 80 KB」时**没有把它乘开**——75182 B 在 T-06 已顶到边，而 T-07～T-09 三篇还没写。⇒ **该界不是「被突破」，是「不成立」**：与任务数无关的常数界，在多 Task 的 CHG 上必然被突破，与纪律无关。

⇒ 第四版改成**速率**：`change.md` ≤ 35 KB、`checkpoint.md` ≤ 15 KB、单 Task evidence ≤ 9 KB；**总量只报不设顶**，以 064 的 213739 B 作基准。**这不是「再放宽一次」，是换了被限制的量**：前三版限存量，存量由任务数决定，不由我决定。

**收尾读数不写在本节**：本节里写的读数一出笔就是旧值（上方 75182 B 即此情形）。四段增量的逐次实测在 `evidence/artifacts/t06-record-size.out` 与 `t07-record-size.out`，**数字以产物文件为准**。

## 12. Current Checkpoint

进度在 `checkpoint.md`（与本文件同级），**不在本文件内联**。活跃 CHG 缺 `checkpoint.md` 即 `verify_delivery_governance.py:121` 报错。

## 13. DONE Gate

- [x] Scope completed. — §5 四小节逐项交付；T-01…T-09 全部 DONE（§8）。
- [x] No blocking `Q-xx`. — §7 为字面 `None.`，全 CHG 未新增 `Q-xx`。
- [x] Acceptance matrix all PASS. — §10 中 AC-01…AC-13 已 PASS；**AC-14／AC-15／AC-16 于 T-09 完成**（逐仓对账、收尾读数、两遍指针扫描），见 §10 与 `evidence/artifacts/t09-*`。
- [x] Automated tests passed or justified. — 六门禁 `exit=0` / 0 ERROR；`unittest` `Ran 94 / OK`；`sync_skills.py check` `exit=0`。**读数取于本 CHG 最后一次改动之后**，见 `evidence/artifacts/t09-gate-readings.out`。
- [x] Manual verification evidence recorded where required. — 三仓的逐条归属表（`task-05/06/07`）、T-08 的两条活体阳性对照、T-09 的双向对照（`t09-pointer-sweep.py --control`）。
- [x] Diff checked for out-of-scope changes. — 四仓逐仓对账见 §9；三仓各自 `diff --stat` 只落在四件入口文件上（cloud 165+/278−、agent 49+/54−、desktop 45+/48−），**零运行时代码、配置、测试**。
- [x] Runtime repositories touched only if listed in scope. — §1 已声明并逐仓对账：三仓各一个提交（cloud `0db02ab`、agent `6d740fc`、desktop `7c1b0ad`），只写四类入口文件。
- [x] Required baselines updated. — 判据落在 `conventions §3／§9／§10／§11`（T-02）、`AGENT-INDEX.md` §4／§10、`..._V1.md:769／:1801`；生成器 `init-agent-entry.sh`（T-03）与门禁 `verify_agent_entry.py`（T-04）与判据同步。
- [x] Affected repositories committed independently. — 四仓各自提交：cloud `0db02ab`、agent `6d740fc`、desktop `7c1b0ad`；workspace 的 T-08 入口文件 `50a2417` 与记录分开提交。

## 14. 遗留（只登记、未修，需独立 CHG）

1. **F-09 的政策冲突**（事实面见 §4 F-09）：两条候选——**(a)** 把 `AGENT-INDEX.md:35` 与两行 architecture 的作用域改为「运行期依赖」并记 ADR；**(b)** 把 43 行 `build-desktop.sh` 移进 `wt-media-desktop/scripts/`（它已只调 desktop 自己的 `release-versions.sh`），红线与两行 architecture 一字不改即重新成立——连带 `tauri.conf.json`、`m2b_local_acceptance.py:282`、`web-desktop-visual-system.md:326,374,410` 与两份 `environment-bring-up` skill 副本。**用户 2026-09-25 裁定：另立 CHG 裁定。**
2. **三仓拿不到 workspace 组 skill**（F-11）：`config/skills-distribution.yaml` 不分发，cwd 在运行仓的会话磁盘上没有 `executing-wt-media-change`。本 CHG 改善但不修。陷阱见 `delivery/completed/CHG-20260925-064/change.md` §14 第 16 项。
3. **`wt-media-cloud/docs/arch/wt-media-cloud-arch.md:5`** 与 F-05 同类的主张写在非入口文件里，本 CHG 只登记。
4. **workspace `README.md:42-51` 的 4 条独有规则**（无生产密钥；接口定义归提供方仓；不建 `changes/active`；「Remove completed delivery records」）与 `AGENT-INDEX.md` §2、`MASTER:132` 的关系未经裁定。最后一条与 `MASTER:132`「归档记录保持原样、不回改」相抵，且 `delivery/LEDGER.md:5`「Completed delivery records are removed…」是同一主张的第二个落点。**归 CHG-20260925-066 一并裁。**
5. **`AGENT-INDEX.md:71`／`:120` 与 `prepare_ai_workspace.py:172` 点名 `DIRECTORY_MAP.md`，而在此之前无任何脚本查其存在**——本 CHG T-04 补上。
6. **`CLAUDE.md` 里 `## 权威源` 段内的散文式规则不被机检抓得住**——`check_pointer_shape` 只抓结构性外溢。作为已知残余登记，不宣称更多。
7. **§3 指针预算的两处表述在 T-03 被改正**（原登记：若实现中发现判据不可用，回来改 §3 的判据表述，而不是放松门禁）。**已裁定并落地**：`H2 ≤ 1` ＋ 白名单 `权威源` 与自己引用的参照件相抵（参照件 `CLAUDE.md` 有 3 个 H2），且它要防的变异已由规则词判据按**正文**抓死；改为 **H2 ≤ 4、不设白名单**，规则词判据**只作用于非标题行**，并补出重复比较集的构造。**这不是放松**：变异 4（贴 `## 模块规则` 段）在改正前后都被规则词判据抓出，改正后反而多抓了「描述文件角色的表行」这一类。理由与读数见 `evidence/task-03-generator.md` §1／§4。**残余**：「规则词」以该节举例为准，未穷尽（T-04 已按 §3 落地）。
8. **`duplication_denominator_is_reported` 在变异下是 `ERROR` 而非 `AssertionError`**（T-04 实测）：禁用该检查后，用例的辅助方法 `next(...)` 抛 `StopIteration`。它是被禁用检查导致的**真实失败**、不是 `ImportError`（六次变异计数全 0），但**不是** `AGENT-INDEX.md:206` 要求的最干净形态。**不修**：为让失败「更好看」去改用例的取值方式，会把判据改成迁就测试的形状。
9. **§11 的记录成本数字原为凭印象设定**，T-04 收尾实测后改正（见 §11）。登记以免下一轮又凭印象设数。
10. **生成器骨架不含规则句**：`check_rule_text_duplication` 在生成器产出上的分母只有 1 条规则句（`artifacts/t04-generator-vs-gate.out`）。⇒ 该判据在**真实文件**上的判别力由 `tests/` 的注入用例与本 CHG 三仓收口时的读数覆盖，不由生成器覆盖。
11. **AC-09 的判据不是门禁**：全仓无任何脚本读 cloud 的 `internal/infra` 列表（`grep -rn 'internal/infra' scripts/ tests/ config/` 零命中），故 T-05 的 infra 相符性判据是**证据期临时构造的扫描**（可重放命令 ＋ 阳性对照）。⇒ 「规则行枚举的目录必须在磁盘存在」这件事**不会在将来失效时报警**。是否值得升为门禁，交后续 CHG 裁；本 CHG 不新增（会与「ERROR 只判存在／声明／计数／相等」的分层结论相抵）。
12. **生成器对非兄弟仓路径产出坏链接**：`init-agent-entry.sh repo <绝对路径>` 把工作区相对路径按 `os.path.relpath` 算出，目标若不在执行根下就写出 `../../../../../../../Users/…` 这样的链接（T-04 复测时实测，见 `artifacts/t04-remeasure.sh` 的产出）。本仓实际用法是 `repo cloud|agent|desktop`，不受影响；**只登记**。
13. **本 CHG 两次「两个分母混用」**（T-05 归属表把总行数与非空行数当同一个分母；§11 引自 CHG-064 的「94 KB」漏算 evidence，实为 213739 B）。两次都不是算错，是**没当场说明在量哪一个分母**——与「计数必须当场量」是同一件事的两面。登记以免后续 Task 重复：**凡报数字，同一句里写清分母是什么。**
14. **阳性对照的锚取 `HEAD` 会在提交瞬间变成镜子**（T-05 cloud 臂、T-06 agent 臂各发生一次）：取证时 `HEAD` 指向改前提交、读数正确为「命中 1」；修复一提交，`HEAD` 就是修复后的文件，**同一命令读数也变成 0——与「扫描无判别力」形状完全相同**，且不会自己冒出来。已在两个脚本里钉为常量（`BASE=0346edf`／`24da21b`）。⇒ **凡以改前状态为对照的可重放命令，一律指向具体提交，不指向 `HEAD`、不指向分支名。** 本 CHG 自身的 T-09 收尾扫描与他人复核同受此约束。**同一族的第三种形态（T-09 实测）：记录本身会改变被记录的量。** 我先把扫描分母（477 个 `*.md`／48938 行／**115** 条相对链接）写进 `LEDGER.md` 的关闭段，而**写这段本身就往 `LEDGER.md` 加了一条链接**——分母随即变成 **116**，前一段落连同它引用的读数一起过期。⇒ **凡「记录行为会改变其读数」的量，一律只报方向与结论、指向产物文件，不内联数字**：本 CHG 的 §11 与 `LEDGER.md` 关闭段据此都改为指向 `artifacts/*.out`。
15. **AC-11 的判据收窄过一次，且收窄是必需的**（T-06）：初版误命中 agent 的锁文件**规则**（`禁止手改`——禁的是手改不是扫描）；收紧为「**扫描** ∧ 枚举具体构建路径」后，松判据在**已修好的**文件上仍报 2（agent）／3（cloud）行，**全为假阳性**（两条指针行含「禁止扫描区」四字、一条是 `go vet` 行）。⇒ **路径词表是承重构件**，去掉它「0 命中」会被污染成噪声。读数见 `evidence/task-06-agent.md` §4。
16. **`initial` 骨架与「按代码回写」的边界**：T-05 改了 cloud 的 infra 列表（两份文档都列了磁盘上不存在的 `redis`／`cache`／`storage`），T-06 改了 agent 的「文件与 FFmpeg 运行时」（代码里只有探测，无运行时）。两处都是**按代码写文档**，属 §5 允许的例外（「A 与 B 列举的事实错误除外」），**不是「只搬家不改义」的破例**。登记此条以明确该例外的实际适用范围仅到「事实错误」为止，不含措辞偏好。
17. **记录成本界改到第五版才选对被限制的量**（T-07）：前三版限单篇、第四版限总量，**四次限的都是「存量」**；而存量由任务数决定、不由我决定，故必然在某个 Task 上被突破（第四版在 T-07 上被突破：`change.md` 37701 B ＞ 35 KB、`checkpoint.md` 15418 B ＞ 15 KB）。第五版改为**每 Task 增量**（`change.md` ≤ 5 KB、`checkpoint.md` ≤ 4 KB、单 Task evidence ≤ 9 KB），实测六段增量最大 4601／3015 B，全部在界内（连续三个 Task）。**登记以免下一轮又去调那个绝对数字**——该调的是被限制的量，不是界的值。
18. **用一份样本的读数去推断另一份样本该多大**（T-08）：开工时我据「三仓指针各 11 行／656 B／1 H2」推断 workspace 的两个指针**也应**同量级，进而以为 T-08 只需补两行机读键。实测不成立——workspace 的指针**本就**是 30／24 行、各 2–3 个 H2，因为它们要解释一件运行仓不存在的事实（同一个 `AGENT-INDEX.md` 在 workspace 是治理正文、在运行仓是三层索引，**同名两角色**）。⇒ T-03 定的形态约束的是**角色**（谁承载正文、谁只做指针），不是**章节结构**；三仓的读数**不是** workspace 的标尺。**登记以免下一轮把「其他仓长这样」当成 workspace 的合规标准**——那正是本 CHG 要消灭的「多落点互相推断」。
19. **「每 Task 增量」这个界有一个已知盲区：替以前的 Task 还债的 Task 会独自越界**（T-08 实测）。`checkpoint.md` 的 `Completed` 一节自 T-04 起就只列到 T-03——T-04～T-07 四个 Task 完成时都没补，缺口是**累积**出来的。T-08 顺手补齐这五行后，它的增量越了 4 KB 界，而这笔字节**不属于 T-08 的内容**，属于前四个 Task 各自欠的。⇒ **界不改**（§14 第 17 项：该调的是被限制的量，不是界的值；越界就报越界）。登记两点：①这是**第五版界仍未覆盖的形态**——它假设每个 Task 只承担自己的记录成本，而一个**补记录**的 Task 会一次性承担多个；②**真正的错在四节记录没在各自的 Task 里写完**，T-08 只是把它暴露出来。修法是**每个 Task 收尾时把 `Completed` 写全**，不是把界放宽到 6 KB。
20. **归档记录里 6 条相对链接少了一级 `..`**（T-09 扫描实测）：全部在 `delivery/completed/CHG-20260916-052/evidence/m3-e3-acceptance-20260923/12-defects-and-security.md`，目标是 `wt-media-cloud` 的三个源文件（`discovery_store_mysql.go` ×4 处、`operations.go`、`ContentPoolPage.vue`）。**成因实测**：该文件在 `delivery/completed/<CHG>/evidence/<pkg>/` 下，从它出发**要 6 级 `..`** 才能到达执行根，写成 5 级即落在 `wt-media-workspace/` 之内——逐级验证：5 级 `exists=no`、6 级 `exists=YES`。**本 CHG 不改**：`MASTER:132`「归档记录保持原样、不回改」，且这属于**已归档记录的历史叙述**（同 CHG-059 Q-08「登记不改」的先例）。**本 CHG 自己拥有的死链：0**。⇒ 登记，供将来若采纳「归档可修链」的政策时一次性处置。**同一类也在本 CHG 自己的记录里**：归档后 `delivery/active/CHG-20260925-065/…` 不再存在，而本记录保留 7 处该串（`change.md:84` 的 §5 范围陈述、`checkpoint.md:13` 与 `task-01-baseline.md:9` 的过去时叙述、`task-01-baseline.md:21` 与 `t01-baseline.out:7` 与 `t08-gate-readings.out` 8 行**原始 `git status` 捕获**）——**一律不改**：原始捕获改了就不是证据，叙述改了就不是当时的事实。**另注**：本 CHG 的扫描器**跳过代码块与行内代码**，故读数（6）小于不做该区分时的读数（14，其中 8 条是记录里引用被注入对照样本的**引文**，不是指针）——见 `artifacts/t09-pointer-sweep.out`。
