# CHG-20260925-065: 三个运行仓入口文件形态统一——参考 workspace 的双指针 + 单一正文

## 1. Basic Information

- Level: S
- Status: IMPLEMENTING
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
| T-05 | cloud 四件入口文件收口（正文迁入 `AGENT-INDEX.md` 的 `## 本仓规则`；落实 F-03／F-05／F-07） | TODO | 逐条归属表（改前行数为分母）；门禁 cloud 错误数改前 → 0；阳性对照：写一个不存在的目录，确认报出 |
| T-06 | agent 四件入口文件收口 ＋ F-07 | TODO | 同上 |
| T-07 | desktop 四件入口文件收口 ＋ F-07 ＋ D-04 的范围限定句 | TODO | 同上；desktop 发布链路调用关系**不改** |
| T-08 | workspace 入口文件补机读键过机检（二者已是纯指针，内容不动） | TODO | workspace 臂由红转绿 |
| T-09 | 收尾：归档、LEDGER 同步、快照 `--no-active`、两遍失效指针扫描、§14 登记 | TODO | 六门禁 `exit=0` ＋ `unittest`，**在最后一次改动之后**重测；四仓对账 |

**中间态必然见红**：T-04 落地后、T-07 完成前，三仓门禁是红的。这是预期的，**已在 `checkpoint.md` 说明**——CHG-20260925-063 的教训是「意料外的红会训练读者忽略这个门禁」。**T-09 不得早于 T-07。**

每次改动后跑：`python3 -B -X pycache_prefix=/tmp/pyc-none scripts/verify_*.py` 与 `python3 -B -X pycache_prefix=/tmp/pyc-none -m unittest discover -s tests -q`。

## 9. Repository Checklist

### wt-media-workspace

- [x] `AGENT-INDEX.md` §4／§10、`conventions §3／§9／§11`、`..._V1.md:769／:1801`（T-02）
- [x] `AGENT-INDEX.md` §12 里 `verify_agent_entry.py` 的旧描述（`各仓入口漂移 WARN`）——**T-04 同 commit 改**；按**内容**定位（T-02 的 §10 加行后它由 `:193` 漂到 `:198`，按行号改会改错句）
- [x] `scripts/init-agent-entry.sh`（T-03：全文重写为 §3 形态，停止手写快照）、`conventions §8`（补两条约束）
- [x] `scripts/verify_agent_entry.py`、`tests/test_verify_agent_entry.py`（T-04）
- [ ] `CLAUDE.md`／`AGENTS.md` 机读键
- [ ] `delivery/` 记录与 LEDGER

### wt-media-cloud

- [ ] `AGENT-INDEX.md`（正文增长：吸收原 `AGENTS.md` 规则）
- [ ] `AGENTS.md` → 指针
- [ ] `CLAUDE.md` → 指针（原 168 行规则正文迁出）
- [ ] `DIRECTORY_MAP.md`（接收原 `AGENTS.md` 的目录树）
- [ ] **不写**：任何运行时代码、配置、测试

### wt-media-agent

- [ ] 同上四类（`AGENTS.md` 需与 desktop 对齐形状）

### wt-media-desktop

- [ ] 同上四类 ＋ D-04 的范围限定句
- [ ] **不写**：`src-tauri/tauri.conf.json`、发布链路

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | 四仓 `CLAUDE.md` 与 `AGENTS.md` 皆含机读键 `- 正文：\`AGENT-INDEX.md\``，目标存在 | 新 `check_pointer_shape`；每仓逐条报出 | TODO |
| AC-02 | 四仓指针文件不含被复述的规则句（规则词行的同一行须出现正文文件名） | 同上；阳性对照：把 cloud `AGENTS.md` 的 `## 模块规则` 段贴进 `CLAUDE.md` → 报出 | TODO |
| AC-03 | 四仓指针文件 H2 ≤ 4、行数 ≤ 30、字节 ≤ 2000，规则词判据只作用于非标题行（**T-03 改正后**的 §3 判据——`H2 ≤ 1` ＋ 白名单 `权威源` 与自己引用的参照件相抵，已退役，见 §14 第 7 项） | 同上；变异：灌水到 37 行／超 H2 → 报出 | TODO |
| AC-04 | 运行仓四类入口文件皆存在且非空 | 新 `check_repo_entry_files`；变异：`rm` 任一 → 报出仓名＋文件名 | TODO |
| AC-05 | 同仓各指针声明的正文同一，且正文不再声明正文（无环） | 新 `check_rule_body_consistency`；变异：造 `A→B, B→A` → 报出 | TODO |
| AC-06 | 三仓 `AGENT-INDEX.md` 八 H2 序列互相相等且长度为 8 | 新 `check_layer3_shape`；变异：改名 desktop 的 `## 禁止` → 报出首个分叉位 | TODO |
| AC-07 | 每一条新 ERROR 都被证明能失败（变异式，非 `ImportError`） | `tests/` 用例断言**完整错误集合逐条相等** | **PASS**（T-04）：六条新检查逐一禁用 → 3／7／4／2／2／1 条用例失败，`ImportError` **0**；`Rule Word` 类判据另有注入式阳性对照。读数见 `task-04-gate.md` §3 |
| AC-08 | `check_entry_drift` 及其 2 条用例、描述段落已退役，且同 fixture 由新检查顶替 | 变异对：旧代码＋旧 fixture → 漂移 WARN；新代码＋同一 fixture → `check_pointer_shape` 报出 | **PASS**（T-04）：代码中 `check_entry_drift`／`check_layer3_entries` 命中 0；旧 2 条用例已删；fixture 改为「默认合规」后由 `check_pointer_shape` 等六条顶替，且每条都被变异点亮 |
| AC-09 | cloud 的 F-03 表 6 处分歧逐处消解，两处事实错误按**代码实况**回写 | `internal/infra` 实际目录逐项相符（阳性对照：写一个不存在的目录 → 报出）；模块树含 `router.go` | TODO |
| AC-10 | 每仓逐条归属表覆盖被移走的**每一行**，分母＝改前行数 | 逐文件 `wc -l` 前后对账，无一项落入「未登记」 | TODO |
| AC-11 | 三仓 `AGENT-INDEX.md` 的禁止扫描区清单已换成指向 `DIRECTORY_MAP.md` 的指针 | 字符串扫描：三仓 `AGENT-INDEX.md` 内排除清单命中 0（阳性对照另注入 1 条 → 报出） | TODO |
| AC-12 | F-06 两侧同时改：三仓小节改名＋作用域首行；workspace §4 作用域句 | 逐处复查；`check_local_order_scope` WARN 为 0 | TODO |
| AC-13 | F-08：`init-agent-entry.sh` 产出四件且形态相符；快照只有**一个**生成器 | tmpdir 实跑 ＋ 产出差异表；脚本内无 `.ai/CURRENT_CONTEXT.md` 写入 | **PASS**（T-03）：12 项形态判据 12 PASS；阳性对照 7 类变异全报出；`workspace --dry-run` 对快照只报 `exists:` 不再 `would create:`。读数 **不是门禁**（门禁在 T-04），届时调门禁自己的函数复测 |
| AC-14 | 四仓零运行时代码／配置／测试改动 | `git -C ../wt-media-{cloud,agent,desktop} status --porcelain` 逐仓对账；只允许四类入口文件与 `.claude/skills`／`.codex/skills` 副本 | TODO |
| AC-15 | 六门禁 `exit=0` ＋ 套件全绿，且读数取于**最后一次改动之后** | `evidence/artifacts/t09-gate-readings.out` | TODO |
| AC-16 | 两遍失效指针扫描（字符串 ＋ 相对链接 resolve），各带阳性对照与分母 | 扫描产物入 `evidence/artifacts/` | TODO |

## 11. Evidence

证据落在 `evidence/`，只记事实（命令／动作、期望、实际、结论），不重复需求。文件名与内容**设上限**：单 Task evidence ≤ 3 KB，原始输出进 `evidence/artifacts/`。

- `evidence/task-01-baseline.md`（含四仓 `git status --porcelain` 基线与开工 commit）
- `evidence/task-0x-<topic>.md`
- `evidence/artifacts/`（原始命令输出）

**记录成本上限**：本文件 ≤ **30 KB**；单 Task evidence ≤ **8 KB**。

**本节的原始数字（`change.md` ≤ 25 KB、单 Task ≤ 3 KB）被 T-01～T-04 逐条突破，实测后改正**（不静默改数字）：T-01～T-04 四篇 evidence 实测 4559／4845／6314／6329 B，**每一篇都超过 3 KB**；T-04 收尾时 `change.md` 实测 26477 B，超 25 KB。原数字是**凭印象设的**，不是量出来的——与「计数必须当场量」同一条纪律。改正后的数字以**实测区间上沿**为准，并把总量作真正的界：四篇 evidence 合计 22 KB、`change.md` 26 KB，**合计 57 KB**，对比 CHG-20260925-064 的 `change.md` 单文件 65 KB、`checkpoint.md` 29 KB（该 CHG 12 个 Task）——记录成本降了约一个数量级，这才是本节要防的那件事。**本 CHG 的界是总量不是单篇，故不再逐篇追 3 KB。**

## 12. Current Checkpoint

进度在 `checkpoint.md`（与本文件同级），**不在本文件内联**。活跃 CHG 缺 `checkpoint.md` 即 `verify_delivery_governance.py:121` 报错。

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

## 14. 遗留（只登记、未修，需独立 CHG）

1. **F-09 的政策冲突**：`tauri.conf.json:10` 的 `beforeBuildCommand` 使 desktop 发布包依赖 workspace 检出，与 `..._V1.md:478`／`:1801` 相抵。两条候选：**(a)** 把 `AGENT-INDEX.md:35` 与两行 architecture 的作用域改为「运行期依赖」并记 ADR；**(b)** 把 43 行的 `build-desktop.sh` 移进 `wt-media-desktop/scripts/`（它已只调 desktop 自己的 `release-versions.sh`），红线与两行 architecture 一字不改即重新成立——但连带 `tauri.conf.json`、`m2b_local_acceptance.py:282`、`web-desktop-visual-system.md:326,374,410` 与两份 `environment-bring-up` skill 副本。**用户 2026-09-25 裁定：另立 CHG 裁定。**
2. **三仓拿不到 workspace 组 skill**（F-11）：`config/skills-distribution.yaml` 不分发，cwd 在运行仓的会话磁盘上没有 `executing-wt-media-change`。本 CHG 改善但不修。陷阱见 `delivery/completed/CHG-20260925-064/change.md` §14 第 16 项。
3. **`wt-media-cloud/docs/arch/wt-media-cloud-arch.md:5`** 与 F-05 同类的主张写在非入口文件里，本 CHG 只登记。
4. **workspace `README.md:42-51` 的 4 条独有规则**（无生产密钥；接口定义归提供方仓；不建 `changes/active`；「Remove completed delivery records」）与 `AGENT-INDEX.md` §2、`MASTER:132` 的关系未经裁定。最后一条与 `MASTER:132`「归档记录保持原样、不回改」相抵，且 `delivery/LEDGER.md:5`「Completed delivery records are removed…」是同一主张的第二个落点。**归 CHG-20260925-066 一并裁。**
5. **`AGENT-INDEX.md:71`／`:120` 与 `prepare_ai_workspace.py:172` 点名 `DIRECTORY_MAP.md`，而在此之前无任何脚本查其存在**——本 CHG T-04 补上。
6. **`CLAUDE.md` 里 `## 权威源` 段内的散文式规则不被机检抓得住**——`check_pointer_shape` 只抓结构性外溢。作为已知残余登记，不宣称更多。
7. **§3 指针预算的两处表述在 T-03 被改正**（原登记：若实现中发现判据不可用，回来改 §3 的判据表述，而不是放松门禁）。**已裁定并落地**：`H2 ≤ 1` ＋ 白名单 `权威源` 与自己引用的参照件相抵（参照件 `CLAUDE.md` 有 3 个 H2），且它要防的变异已由规则词判据按**正文**抓死；改为 **H2 ≤ 4、不设白名单**，规则词判据**只作用于非标题行**，并补出重复比较集的构造。**这不是放松**：变异 4（贴 `## 模块规则` 段）在改正前后都被规则词判据抓出，改正后反而多抓了「描述文件角色的表行」这一类。理由与读数见 `evidence/task-03-generator.md` §1／§4。**残余**：「规则词」仍以该节举例为准，未列举穷尽——T-04 实现时以 §3 为准。
8. **`duplication_denominator_is_reported` 在变异下是 `ERROR` 而非 `AssertionError`**（T-04 实测）：禁用 `check_rule_text_duplication` 后，该用例的辅助方法 `next(...)` 抛 `StopIteration`。它是被禁用检查导致的**真实失败**、不是 `ImportError`（六次变异 `ImportError` 计数全为 0），但**不是** `AGENT-INDEX.md:206` 要求的最干净形态。**不修**：为让失败「更好看」去改用例的取值方式，会把判据改成迁就测试的形状；如实登记。
9. **§11 的记录成本数字原为凭印象设定**，T-04 收尾实测后改正（见 §11）——四篇 evidence 逐篇超 3 KB、`change.md` 超 25 KB。登记在此以免下一轮又凭印象设一个数字。
10. **生成器骨架不含规则句**：`check_rule_text_duplication` 在生成器产出上的分母只有 1 条规则句（`artifacts/t04-generator-vs-gate.out`）。⇒ 该判据在**真实文件**上的判别力由 `tests/` 的注入用例与本 CHG 三仓收口时的读数覆盖，不由生成器覆盖。
