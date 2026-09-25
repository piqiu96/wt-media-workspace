# CHG-20260925-062：2026-09-24 入口重构的治理补记与三处指针修正

## 1. Basic Information

- Level: S
- Status: DONE
- Created: 2026-09-25
- Current repository: `wt-media-workspace`
- Affected repositories:
  - `wt-media-workspace`

## 2. Change Goal

本记录是**补记，不是新开工**。2026-09-24 的一次「入口重构」已在会话内改完并一直留在工作区，
却没有任何治理承载；本 CHG 为它补上归属，并把这次重构连带产生的三处陈旧指针修掉。达成三个可观测结果：

1. **权威落点唯一**：治理规范正文只存在于 `AGENT-INDEX.md`；`AGENTS.md` 与 `CLAUDE.md` 是薄入口，
   只声明权威源与最小硬约束，不含正文副本。
2. **改动有主**：这批改动进入 `delivery/` 的正式记录（本 `change.md` + LEDGER 表行 + 快照），
   并分次提交；工作区回到干净状态。
3. **指针不再悬空**：重构后产生的三处陈旧引用被修正——`agent-workspace-conventions.md` 里指向不存在小节的
   「第 13 节」、同文件 §10 里过期的验证器读数、以及两个 workspace skill 第 1 步指向已失效的
   「Root `AGENTS.md`」为规则正文。

本 CHG **不是业务变更**：不改任何用户可见闭环，不触碰任何运行时代码。成功判据是工程可观测行为
（文件内容、门禁红绿、扫描命中数）。

## 3. Baseline References

- 锚点（Level S，按 CHG-20260924-060 §3 先例写散文，不引 Milestone）：本 CHG 处置的是
  一次**已完成但未入账**的治理仓改动，其唯一治理痕迹是 `agent-workspace-conventions.md` 第 5 行的
  「更新：2026-09-24（入口重构…）」——该文件本身也是这批未提交改动的一部分。
- Engineering baseline：`docs/engineering/specs/agent-workspace-conventions.md`
  （§1 不变量 3、§3 入口文件表、§5 渐进式加载、§9 规则—实现耦合点登记、§10 校验与已知红项）。
- 上游记录（两处「既有脏文件」的登记，证明它从 2026-09-24 起就悬着、且被后续 CHG 主动绕开）：
  - `delivery/completed/CHG-20260923-058/evidence/task-01-activation.md:70`
  - `delivery/completed/CHG-20260923-059/evidence/task-08-m2-regression.md:152`、`evidence/task-10-writeback-and-close.md:221`
- Decisions：不涉及。入口归口的规范落点已是 `agent-workspace-conventions.md` §1.3，
  属工程规范而非耐久架构决策，**不为此新立 ADR**（理由见 §6 D-03）。
- Contract governance：不涉及（无 contract 变更）。
- 程序总纲：不涉及。本 CHG 不属
  `docs/engineering/specs/2026-09-23-launch-engineering-optimization-program.md`，
  该程序的 A/B/C/D 四阶段（CHG-056/057/058/059）已全部归档 `DONE`，本 CHG 是其后的一次独立治理收尾。

## 4. Current Facts

- **开工时的仓状态**：HEAD `840ba38`，分支 `main`，工作区 6 个未提交文件（见下）。
  快照 `Active CHG: none` / `Status: NONE`；`delivery/active/` 仅 `.gitkeep`；`LEDGER.md` 表内无 CHG 行
  （占位行 `| — | 当前没有 active CHG… | — | — |`）。三者一致，符合「最多一项 active」。
- **这批改动的实测差量**（行数按 HEAD → 工作区，插入/删除按 `git diff --numstat`）：

  | 文件 | 行数 | +/− |
  | --- | --- | --- |
  | `AGENTS.md` | 387 → 30 | +21 / −378 |
  | `AGENT-INDEX.md` | 109 → 178 | +128 / −59 |
  | `CLAUDE.md` | 24 → 91 | +80 / −13 |
  | `README.md` | 81 → 82 | +2 / −1 |
  | `docs/engineering/specs/agent-workspace-conventions.md` | 153 → 155 | +13 / −11 |

  改动实质是**搬家**：旧 `AGENTS.md` 的 387 行治理正文（章节、职责边界表、需求路由表、上下文加载规则）
  整体迁入 `AGENT-INDEX.md` 并重新编号为 12 节；`AGENTS.md` 缩为 30 行指针；`CLAUDE.md` 从 24 行英文
  扩为 91 行中文（项目概览 / 权威源 / 常用命令 / 目录结构 / 工作流 / 提交约定 / 高频红线）。
- **无治理承载**：`git grep` 全仓确认——`delivery/` 下无任何 CHG 记录、ADR 或 planned 草案提及这次重构；
  唯一的文字痕迹就是 `agent-workspace-conventions.md` 第 5 行那句更新说明。CHG-058 与 CHG-059
  都把它当作**别人的既有脏文件**主动绕开、未提交。
- **新 `AGENT-INDEX.md` 只有 12 节**（已逐节 `grep "^## "` 核对）：`Agent 入口与执行快照` 是**第 10 节**。
  而 `agent-workspace-conventions.md` 在**两处**（第 3 行、第 72 行）称自己「补充 `AGENT-INDEX.md` 第 13 节」
  ——该小节不存在。第 72 行同时引用的「第 8 节」是对的（§8 交付治理确实含 CHG 创建规则）。
- **验证器实跑读数**：`verify_agent_entry.py` 报 `0 warning(s) need review`（快照 1668 字符）；
  而 `agent-workspace-conventions.md` §10 校验表把该行写成「1 个 WARN 为待复核项」。读数与表不符。
- **skill 第 1 步指向错位**：`skills/workspace/executing-wt-media-change/SKILL.md:14` 与
  `skills/workspace/planning-wt-media-delivery/SKILL.md:14` 的第 1 步写「Root `AGENTS.md`」——
  在治理仓它现在只是 30 行指针，规则正文在 `AGENT-INDEX.md`。分发面已核实：`workspace` 分组
  （`config/skills-distribution.yaml`）只投递到**执行根 `..`（非 git 仓）**与**本仓自身**，
  故修它**不会脏化** cloud/agent/desktop 三仓。
- `2026-09-24-m4-m5-cloud-content-production.md` 当时也脏，但只多一个**尾部空行**，与本次重构无关 ⇒
  按用户 2026-09-25 裁定**还原**（见 §6 D-02），不并进本 CHG 的提交。
- **三仓并非全空，但都不是本 CHG 造成的**（T-04 复验时发现，收尾时逐文件 `stat` 重测）：
  `wt-media-desktop` 的 `src-tauri/src/` 下 **13** 个 `.rs` 是脏的——**10** 个 mtime =
  2026-09-24 22:32:20，另 3 个为 **09:57:13 / 10:34:48 / 10:38:13**；`wt-media-cloud` 有一个
  未跟踪的 `dump.rdb`（2026-09-24 17:19:16）。**全部早于本会话**（本会话首个证据文件
  `checkpoint.md` 的 mtime = **2026-09-25 14:05:43**，以上均早于它）。`wt-media-agent` 干净。
  本 CHG 对三仓零读写；这些在途改动**不碰、不提交、不清理**。
  故 §10 AC-12 的判据按实测收窄为「本 CHG 对三仓零读写」，**不写「三仓工作区全空」**。
  （**此处曾写错并已改正**：初稿记「11 个 22:32:20 + 3 个」，11+3=14 与本行总数 13 自相矛盾；
  重测为 10+3。成因与同一 CHG 内另一处「8 处」写错同源——凭印象写数而未逐个量，见 T-05 证据。）
- **`verify_agent_entry.py::check_entry_drift` 在 workspace 上早已空转**（**先于本次重构**，非本次引入）：
  它只从 `repo/AGENTS.md` 取「被禁止的路径」token，而禁止规则现在搬到了 `AGENT-INDEX.md`。
  复算 HEAD 版 `AGENTS.md`：`forbidden ∩ described` 同样为 **0**——即该臂在重构**之前**就是空的。
  故本次只登记、不改其语义（见 §5 Explicitly Not Doing 与 §7）。

## 5. Scope

### Add

- `wt-media-workspace/delivery/active/CHG-20260925-062/`：本记录、`checkpoint.md`、`evidence/`。
  （单仓实施，**不建** `status/`。）

### Modify

- `wt-media-workspace/AGENT-INDEX.md`、`AGENTS.md`、`CLAUDE.md`、`README.md`：**本次重构本体**，
  内容不改写，只是把已在工作区的状态提交入账。
- `wt-media-workspace/docs/engineering/specs/agent-workspace-conventions.md`：
  ①第 3 行与第 72 行的「第 13 节」→「第 10 节」；②§10 校验表里 `verify_agent_entry.py` 那行
  的 WARN 读数按实测重写并注明重测日期。
- `wt-media-workspace/skills/workspace/executing-wt-media-change/SKILL.md`、
  `skills/workspace/planning-wt-media-delivery/SKILL.md`：第 1 步读取指针改指 `AGENT-INDEX.md`。
- `wt-media-workspace/.claude/skills/`、`.codex/skills/`：由 `scripts/sync_skills.py` **生成**，
  随源改动同步（禁手改）。
- `wt-media-workspace/delivery/LEDGER.md`、`.ai/CURRENT_CONTEXT.md`：登记与快照，关闭时移除/重生成。

### Delete

- None.

### Explicitly Not Doing

- **不改 `scripts/verify_agent_entry.py` 的检查语义**：`check_entry_drift` 的 workspace 臂早已空转
  （§4 已复算证明其先于本次重构），修它等于改一个校验器的语义，属另一类变更。**只登记。**
- **不给 `AGENT-INDEX.md` §12 补 `verify_delivery_governance.py`**：该节校验清单只列了
  `verify_agent_entry.py`，未列真正约束 CHG 记录的那个脚本。是缺陷，但超出用户裁定的
  「修两处该修的」范围。**只登记。**
- **不修 `verify_m2_acceptance.py` 的 4 条过期期望**：T-03 实跑该静态校验器得**红 5 项**
  （旧读数记「红 1 项」），多出的 4 条是校验器以**文件内容字面量**为判据、而那些文件已被后续
  CHG 合法重构（`compatibility.go` 迁到 `service/`、`REQUIRED_CONTRACT_REVISION` 改为导入再导出、
  `main.rs` 随 CHG-056 拆分后不再含 `wt-media-agent`、`local_agent/mod.rs` 里两个函数名已不存在）。
  改它属跨仓校验器维护，需独立开 CHG。准确内容已登记在
  `docs/engineering/specs/agent-workspace-conventions.md` §10。
- **不还原、不改写那次重构的任何内容**：只提交、只修它带出的指针，不重新设计入口文件结构。
- **不动那 4 条既知红项**：`verify_product_master_alignment.py` 的 M2/M3 状态与能力对齐红项
  与本 CHG 无关，保持红。
- **不激活、不改动 CHG-20260924-061（M4-A）或 M4 任何记录**（用户明确「先不碰 M4」）。
- **不碰任何运行时代码**：`wt-media-cloud`、`wt-media-agent`、`wt-media-desktop` 三仓**零改动**。
- **不新立 ADR**：见 §6 D-03。
- **不合并 `CLAUDE.md` 的 `## 高频红线` 与 `AGENT-INDEX.md` §2**：收尾复核（AC-01）发现前者是后者
  8 条红线中**取 4 条**的改写复述，构成正文的局部第二份文本。该小节自带「完整规则与例外见
  `AGENT-INDEX.md`」，是有意的常见错误速查；但属与本次重构同源的漂移风险。按「不还原、不改写
  那次重构的任何内容」与用户裁定的范围，**只登记不改**，见 §14 遗留。

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | 这次入口重构以 **Level S CHG 事后补记**的形式入账，而非直接 `docs` 提交了事、也不是回退改动。理由：它重排了治理仓的**规范正文归属**（正文从 `AGENTS.md` 整体迁到 `AGENT-INDEX.md`）并改了工程规范基线文件，超出「小修改可直接执行：文档修正」的量级。记录须**如实写明是补记**，不装作正常排期。**用户 2026-09-25 裁定「先补治理记录再提交」**。 | CONFIRMED |
| D-02 | `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md` 那个**孤立的尾部空行**（+1/−0，与重构无关、无配套改动）**还原**，不并进重构提交、也不单开 chore 提交。已在开工后第一步执行并核对与 HEAD 逐字一致。**用户 2026-09-25 裁定「还原它」**。 | CONFIRMED |
| D-03 | 本 CHG 取 **Level S、不引 Milestone、不立 ADR**。层级理由：纯治理仓改动、不挂任何 Milestone，而 `verify_delivery_governance.py` 只对 `Level: M/L` 强制 `- Milestone:`。不立 ADR 理由：入口归口的规范落点已是 `agent-workspace-conventions.md` §1 不变量 3，属可修订的工程规范，未构成需要耐久锁定的架构取舍。 | CONFIRMED |
| D-04 | 只修用户裁定的**两处**漂移（conventions 的陈旧引用与读数、两个 skill 的第 1 步指针），另两处（`check_entry_drift` 空转、§12 漏列验证器）**只登记不改**。**用户 2026-09-25 裁定「记录 + 修两处该修的」**。 | CONFIRMED |

## 7. Pending Questions

None.

（开工前需用户裁定的「尾部空行如何处置」已由用户 2026-09-25 当场裁定，落为 §6 D-02，
故未留 Q 编号。执行期间若出现新的决定需求，停下并新增 `Q-xx`，不自行推断。
§4 末两条登记项**不需裁定**：它们已明确判为「不属于本次范围、只登记」，处置去向写在
§5 Explicitly Not Doing 与 §14 遗留小节。）

## 8. Implementation Tasks

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | 建本 CHG 并激活（change.md/checkpoint.md/evidence/、LEDGER 裸 id 表行、快照重生成、两个验证器绿）。 | DONE | `prepare_ai_workspace.py --change CHG-20260925-062`；`verify_delivery_governance.py` 与 `verify_agent_entry.py` 绿。 |
| T-02 | 提交入口重构本体（AGENT-INDEX/AGENTS/CLAUDE/README 四文件，一个 commit）。 | DONE | 提交前后行数与 `--numstat` 对照 §4 的实测表；diff 无夹带。 |
| T-03 | 修 `agent-workspace-conventions.md` 三处陈旧引用（第 13 节 ×2、§10 WARN 读数）。 | DONE | **先** `grep -rn "第 13 节" docs/` 命中 2 处留证；**再**重跑 `verify_agent_entry.py` 得 0 warning 与表内文字对照；修后复扫 0 命中，且第 10 节标题真实存在。 |
| T-04 | 修两个 workspace skill 的第 1 步指针并分发生成副本。 | DONE | **先** `sync_skills.py check` 红（源与副本已不一致）与 `grep` 命中留证；改源 → `sync_skills.py` → `check` 绿 + `verify_skills.py` 绿；并**读生成副本确认内容真的变了**（不只信 check）。 |
| T-05 | 收尾：证据、验收矩阵、DONE Gate 签字、归档与失效指针扫描。 | DONE | 三个验证器 + `unittest` 读数；归档后快照 `none` 且三者互指一致；扫描带分母与阳性对照。 |

## 9. Repository Checklist

### wt-media-workspace

- [x] 本记录 + `checkpoint.md` + `evidence/`。
- [x] `delivery/LEDGER.md` 加**裸 id** 表行（`| CHG-20260925-062 |`，不加 markdown 链接），关闭时移除。
- [x] `.ai/CURRENT_CONTEXT.md` 由脚本再生成（禁手改）。
- [x] 入口重构四文件提交；`agent-workspace-conventions.md` 三处引用修正；两个 skill 源 + 生成副本。
- [x] 归档后主动扫描并分类处置失效指针。

### wt-media-cloud

- [ ] Not affected.

### wt-media-agent

- [ ] Not affected.

### wt-media-desktop

- [ ] Not affected.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | 治理规范正文只存在于 `AGENT-INDEX.md`；两个入口文件不含正文副本。 | 判别性判据：`AGENT-INDEX.md` 的 **12 个 `##` 正文标题**无一出现在两个入口文件里；`AGENTS.md` 30 行 2 节、`CLAUDE.md` 91 行 8 节，均无职责边界表 / 需求路由表 / 上下文加载规则正文。**判据已收窄**：`CLAUDE.md` 的 `## 高频红线` 是 §2 红线 8 条中取 4 条的**局部复述**，属既有重复，不在本 CHG 范围，见 §14 遗留。 | **PASS**（判据收窄，局部重复单列登记） |
| AC-02 | 两个入口文件都**真实指向** `AGENT-INDEX.md`，且路径可解析。 | 正向解析：`AGENTS.md`→`AGENT-INDEX.md` ✓；`CLAUDE.md`→`AGENT-INDEX.md` / `README.md` / `agent-workspace-conventions.md` ✓。**4/4 存在，0 MISS**。 | PASS |
| AC-03 | `agent-workspace-conventions.md` 的「第 13 节」全部改为真实存在的第 10 节。 | 修前命中 **2**（`:3`、`:72`，见 T-03 证据）；现在 **0**（分母 66 个 `.md`）。正向：`AGENT-INDEX.md:143 ## 10. Agent 入口与执行快照` 逐字吻合。 | PASS |
| AC-04 | §10 校验表里 `verify_agent_entry.py` 的 WARN 读数与实测一致。 | 实跑得 `0 warning(s) need review`；§10 `:133` 现写「绿，**0 WARN**（快照 1923 字符）」，并注明重测日期 2026-09-25。 | PASS |
| AC-05 | 两个 skill 的第 1 步指向 `AGENT-INDEX.md`，且**生成副本同步**。 | `grep -rni`（**大小写不敏感**，分母 5 个目录）→ **0 命中**；`sync_skills.py check` → up to date；`verify_skills.py` → verified 10。 | PASS |
| AC-06 | 生成副本确实随源改变（不是「check 绿」就够）。 | 变异式对照：改源未同步时 `check` **红 8 行**（exit 1），同步后绿；逐文件读副本确认第 1 步已变。阳性对照 `root \`AGENT-INDEX.md\`` 现 **10** 处命中。 | PASS |
| AC-07 | 既有测试基线不回归。 | 基线以 **840ba38 兄弟位 worktree** 实测（**不是 `/tmp`**，见 T-05 证据）：`Ran 73 / failures=4`；当前同为 `Ran 73 / failures=4`；红项名字 **diff 为空**。 | PASS |
| AC-08 | 三个验证器全绿。 | `verify_delivery_governance.py` → ok / `Active CHG: CHG-20260925-062`；`verify_agent_entry.py` → ok / 0 warning；`verify_skills.py` → verified 10。均 exit 0。 | PASS |
| AC-09 | 治理一致：快照、LEDGER、`delivery/active` 互指同一 CHG（关闭后同指 `none`）。 | 关闭前：三者同指 `CHG-20260925-062`。关闭后：快照 `Active CHG: none`、LEDGER 回占位行、`active/` 仅 `.gitkeep`——三者同指 `none`（读取数见 §14 关闭记录）。 | PASS |
| AC-10 | 无主脏文件已按裁定处置，工作区只含本 CHG 的预期改动。 | `git status --porcelain -uall` 于 T-05 提交前仅 7 个 `t05-*` 未跟踪产物（本任务产物），无越界文件；`2026-09-24-m4-m5-cloud-content-production.md` 与 HEAD 的 `git diff` = **0 行**。 | PASS |
| AC-11 | 只登记的项**未被静默修掉**。 | `scripts/verify_agent_entry.py` 在 `840ba38..HEAD` **diff 0 行**；`check_entry_drift` 仍在 `:240`、`:241` docstring 仍写 "forbidden by AGENTS.md"；`AGENT-INDEX.md` §12 对 `verify_delivery_governance` 命中 **0**。 | PASS |
| AC-12 | **本 CHG 对三仓零读写**。注意判据已按实测收窄：不能写「三仓工作区全空」，因为 desktop 与 cloud **先于本会话**就已脏（见 §4 末条）。 | 三仓 status 中 `skills` 相关 **0 条**（本 CHG 的写入面不含三仓）；desktop 13 个 `.rs`、cloud `dump.rdb` **逐文件 `stat`**，mtime 全部早于本会话首个证据文件（`checkpoint.md` = 2026-09-25 14:05:43）。 | PASS |

## 11. Evidence

Evidence files live in `evidence/` and must record facts, not repeat requirements.

最终落盘清单（T-05 收尾按实际改写）：

- `evidence/task-01-governance.md`：建 CHG 与激活；LEDGER 表行、快照再生成、两个验证器读数。
- `evidence/task-02-entry-refactor.md`：重构本体的逐文件差量、diff 无夹带的核对、还原尾部空行的复核。
- `evidence/task-03-drift-sweep.md`：三处引用的**先红后绿**（含一次真实的「修前命中 2 / 修后 0」）、
  §10 读数的重测对照，以及 §10 整表按实测重写的理由。
- `evidence/task-04-skills-pointer.md`：源改前 `sync_skills.py check` 的红、同步后的绿、
  生成副本内容确实改变的读数；**含我自己两处写错的计数及其更正**。
- `evidence/task-05-close.md`：12 条 AC 的逐条判据、四支校验器 + `unittest` 的读数、
  兄弟位 worktree 的基线测量、以及「基线不能建在 `/tmp`」那个坑。
- `evidence/artifacts/`：原始输出（`t01-*`、`t03-*`、`t04-*`、`t05-*`）。

## 12. Current Checkpoint

Completed:
- Start Gate：`active`/`LEDGER`/快照三者一致指向 `none`；无阻塞 `Q-xx`；Level S 不强制 Milestone。
  工作区 6 个脏文件已核实归属（其中 5 个是本 CHG 的对象，1 个是无关的尾部空行）。
- D-02 已执行：`2026-09-24-m4-m5-cloud-content-production.md` 还原，与 HEAD 逐字一致。
- T-01 建本记录并激活（`50b0c79`）：LEDGER 裸 id 表行 + 快照再生成 + 两个验证器绿。
- T-02 入口重构本体入账（`a394ecf`）：`AGENT-INDEX.md`/`AGENTS.md`/`CLAUDE.md`/`README.md` 一个 commit，
  逐文件差量对照 §4 实测表，diff 无夹带。
- T-03 修 conventions 陈旧引用（`2f5fc53`）：「第 13 节」2 → 0，§10 整表按实测重写。
- T-04 修两个 skill 第 1 步指针并分发副本（`087e440`）：源 + 4 处生成副本同步，check 绿。
- T-05 收尾：12 条 AC 全部 PASS（AC-01 判据收窄并单列登记）、§13 九项签字、归档与两遍指针扫描。

Current:
- 无。本 CHG 已完成，正在执行关闭序列（改 Status → 归档移动 → 快照 `--no-active`）。

Next:
- 无。完成后建议的下一项仍停在 `delivery/planned` 的 M4-A（`CHG-20260924-061`），按用户裁定本 CHG 不碰。

Blocked:
- None.

Recent verification:
- 四支校验器全绿：`verify_delivery_governance.py`（ok / `Active CHG: CHG-20260925-062`）、
  `verify_agent_entry.py`（ok / 0 warning）、`verify_skills.py`（verified 10）、
  `sync_skills.py check`（up to date）。
- `unittest discover -s tests -q` → **Ran 73 tests / FAILED (failures=4)**；以 840ba38 兄弟位 worktree
  实测的基线同为 73/4，红项名字 diff 为空（逐条同名）。
- 漂移扫描两遍：`第 13 节` 在 66 个 `.md` 中 **0**；`root \`AGENTS.md\`` 在 5 个目录中 **0**（大小写不敏感），
  阳性对照 `root \`AGENT-INDEX.md\`` **10** 处命中。

## 13. DONE Gate

逐项签字（判据写在签字行里，勿只读勾）：

- [x] **Scope completed.** —— §5 Add/Modify 逐条落地：记录与证据齐备（T-01/T-05）；重构四文件已入账
  （T-02，`a394ecf`）；`agent-workspace-conventions.md` 引用已修（T-03，`2f5fc53`）；两个 skill 源与
  4 处生成副本已同步（T-04，`087e440`）；LEDGER 与快照按脚本处理。Delete 为 `None`，无删除动作。
- [x] **No blocking `Q-xx`.** —— §7 `Pending Questions: None.`；开工前需裁定的「尾部空行」已由用户
  当场裁定并入 §6 D-02，未留 Q 编号；执行期间未出现新的裁定需求（无新增 Q）。
- [x] **Acceptance matrix all PASS.** —— §10 的 AC-01…AC-12 **全部 PASS**。其中 **AC-01 的判据已收窄**
  （`CLAUDE.md` 的高频红线对 §2 的局部复述单列登记，不计入掩盖），理由与登记见 T-05 证据。
- [x] **Automated tests passed or justified.** —— `unittest` 为 **73 tests / 4 红**，**不绿但是既有基线**：
  以 840ba38 兄弟位 worktree 实测同一读数与同名红项（diff 为空），即本 CHG 未引入新红、也未修掉旧红。
  4 条红项的归属已在 §5「只登记」与 T-03 证据逐条说明（`verify_m0_config` ×2、`verify_m2_acceptance` ×1、
  `verify_product_master_alignment` ×1）。
- [x] **Manual verification evidence recorded where required.** —— 本 CHG 为纯治理仓改动、无业务闭环，
  无「必须人工验证的外部副作用」。人工判据（正文字节、链接 resolve、节点标题）均以命令输出留证于
  `evidence/artifacts/`；无凭印象的读数（两处曾凭印象写错者已在 T-04/T-05 证据登记并改为实测）。
- [x] **Diff checked for out-of-scope changes.** —— 本仓 `git status --porcelain -uall` 逐文件对照 §5；
  唯一未跟踪项是本任务自己的 7 个 `t05-*` 产物。T-02 提交前亦逐文件核对无夹带；被裁定还原的
  `2026-09-24-m4-m5-cloud-content-production.md` 与 HEAD `git diff` 为 **0 行**。
- [x] **Runtime repositories touched only if listed in scope.** —— §5 与 §9 均列为 `Not affected`；
  本 CHG 对三仓**零读写**（写入面只有执行根与本仓）。三仓的脏文件先于本会话，见 §4 末条与 AC-12。
- [x] **Required baselines updated.** —— `docs/engineering/specs/agent-workspace-conventions.md` 已更新
  （「第 13 节」→「第 10 节」×2、§10 校验表按实测重写并注明重测日期、§9 登记表含「规范正文归口」行）。
  入口重构把正文归口到 `AGENT-INDEX.md` 本身也属基线更新。无需新 ADR（§6 D-03）。
- [x] **Affected repositories committed independently.** —— 一仓一 commit，纯移动与改逻辑分开：本 CHG
  4 个 commit 全在 `wt-media-workspace`（`50b0c79` / `a394ecf` / `2f5fc53` / `087e440`），三仓零提交。

## 14. Close Record

- **关闭日期**：2026-09-25
- **提交序列（均在 `wt-media-workspace`，分支 `main`）**：

  | Commit | 内容 |
  | --- | --- |
  | `50b0c79` | T-01 激活本 CHG（记录 + LEDGER 裸 id 行 + 快照再生成） |
  | `a394ecf` | T-02 入口重构本体入账（`AGENT-INDEX.md`/`AGENTS.md`/`CLAUDE.md`/`README.md`） |
  | `2f5fc53` | T-03 修 `agent-workspace-conventions.md` 陈旧引用，§10 校验表按实测重写 |
  | `087e440` | T-04 修两个 skill 第 1 步指针并分发生成副本（含一次 `--amend` 更正 commit message 里的计数） |
  | 见 git log | T-05 证据、验收矩阵、关闭与归档移动 |

- **关闭时的门禁读数**：`verify_delivery_governance.py` → `Active CHG: none`；
  `verify_agent_entry.py` → ok / 0 warning；`verify_skills.py` → verified 10；
  `sync_skills.py check` → up to date；`unittest` → 73 tests / failures=4（既有基线）。
- **归档后失效指针扫描**（两遍，判据不同）：字符串扫描证明旧指针为 0；链接 resolve 证明新指针真通。
  分母、阳性对照与命中数见 T-05 证据末节。

### 遗留（只登记，未修）

| # | 遗留项 | 为什么不在本 CHG | 处置去向 |
| --- | --- | --- | --- |
| 1 | `check_entry_drift` 的 workspace 臂早已空转（只从 `AGENTS.md` 取禁止路径，而禁止规则已搬到 `AGENT-INDEX.md`） | **先于本次重构**即如此（§4 已复算 HEAD 版证明），改它等于改校验器语义 | 需独立 CHG |
| 2 | `AGENT-INDEX.md` §12 校验清单只列 `verify_agent_entry.py`，未列真正约束 CHG 的 `verify_delivery_governance.py` | 超出用户裁定的「修两处该修的」 | 需独立 CHG |
| 3 | `verify_m2_acceptance.py` 的 4 条过期期望（以文件内容字面量为判据，而目标文件已被后续 CHG 合法重构） | 属跨仓校验器维护 | 需独立 CHG；准确内容已登记在 conventions §10 |
| 4 | `CLAUDE.md` 的 `## 高频红线` 是 `AGENT-INDEX.md` §2 红线 8 条中取 4 条的局部复述 | 属本次重构内容，用户裁定不还原、不改写 | 需独立 CHG |
| 5 | `executing-wt-media-change/SKILL.md` Authority Order 第 6 项仍写「Affected repository `AGENTS.md` files」 | 用户裁定的范围是「第 1 步读取指针」，第 6 项不在内（且该措辞不算错，层三本来就读该仓三件） | 需独立 CHG（措辞精确化） |
| 6 | desktop 13 个 `.rs`、cloud `dump.rdb` 为**他人/他任务**的在途改动 | 先于本会话，非本 CHG 造成 | 不碰、不提交、不清理；后续 CHG 以它们为基线前需先确认归属 |
| 7 | `verify_m0_config.py` 3 项、`verify_product_master_alignment.py` 的既知红项 | 与本 CHG 无关 | 保持红 |
| 8 | `delivery/LEDGER.md` 里「**D（CHG-059）已于 2026-09-25 激活**（见上表）」一句已陈旧——059 已关闭归档、表行已移除，故「见上表」不再可达 | 与本 CHG 无关（写于 059 激活当时，此后未随其关闭更新）；改动它会把本 CHG 的范围扩到 LEDGER 的历史叙述 | 需独立 CHG（同属「归档后遗留指针」，与本 CHG 修的三处同类） |
