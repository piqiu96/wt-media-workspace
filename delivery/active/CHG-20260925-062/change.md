# CHG-20260925-062：2026-09-24 入口重构的治理补记与三处指针修正

## 1. Basic Information

- Level: S
- Status: IMPLEMENTING
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
- **三仓并非全空，但都不是本 CHG 造成的**（T-04 复验时发现，按 mtime 归属）：`wt-media-desktop`
  的 `src-tauri/src/` 下 **13** 个 `.rs` 是脏的（11 个 mtime = 2026-09-24 22:32:20，另 3 个为
  2026-09-25 09:57 / 10:34 / 10:38），`wt-media-cloud` 有一个未跟踪的 `dump.rdb`
  （2026-09-24 17:19:16）。**全部早于本会话**（本会话约 13:5x 起，本 CHG 的写入为 14:08–14:09）。
  `wt-media-agent` 干净。本 CHG 对三仓零读写；这些在途改动**不碰、不提交、不清理**。
  故 §10 AC-12 的判据按实测收窄为「本 CHG 对三仓零读写」，**不写「三仓工作区全空」**。
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
| T-01 | 建本 CHG 并激活（change.md/checkpoint.md/evidence/、LEDGER 裸 id 表行、快照重生成、两个验证器绿）。 | TODO | `prepare_ai_workspace.py --change CHG-20260925-062`；`verify_delivery_governance.py` 与 `verify_agent_entry.py` 绿。 |
| T-02 | 提交入口重构本体（AGENT-INDEX/AGENTS/CLAUDE/README 四文件，一个 commit）。 | TODO | 提交前后行数与 `--numstat` 对照 §4 的实测表；diff 无夹带。 |
| T-03 | 修 `agent-workspace-conventions.md` 三处陈旧引用（第 13 节 ×2、§10 WARN 读数）。 | TODO | **先** `grep -rn "第 13 节" docs/` 命中 2 处留证；**再**重跑 `verify_agent_entry.py` 得 0 warning 与表内文字对照；修后复扫 0 命中，且第 10 节标题真实存在。 |
| T-04 | 修两个 workspace skill 的第 1 步指针并分发生成副本。 | TODO | **先** `sync_skills.py check` 红（源与副本已不一致）与 `grep` 命中留证；改源 → `sync_skills.py` → `check` 绿 + `verify_skills.py` 绿；并**读生成副本确认内容真的变了**（不只信 check）。 |
| T-05 | 收尾：证据、验收矩阵、DONE Gate 签字、归档与失效指针扫描。 | TODO | 三个验证器 + `unittest` 读数；归档后快照 `none` 且三者互指一致；扫描带分母与阳性对照。 |

## 9. Repository Checklist

### wt-media-workspace

- [ ] 本记录 + `checkpoint.md` + `evidence/`。
- [ ] `delivery/LEDGER.md` 加**裸 id** 表行（`| CHG-20260925-062 |`，不加 markdown 链接），关闭时移除。
- [ ] `.ai/CURRENT_CONTEXT.md` 由脚本再生成（禁手改）。
- [ ] 入口重构四文件提交；`agent-workspace-conventions.md` 三处引用修正；两个 skill 源 + 生成副本。
- [ ] 归档后主动扫描并分类处置失效指针。

### wt-media-cloud

- [ ] Not affected.

### wt-media-agent

- [ ] Not affected.

### wt-media-desktop

- [ ] Not affected.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | 治理规范正文只存在于 `AGENT-INDEX.md`；两个入口文件不含正文副本。 | 读 `AGENTS.md`（30 行）与 `CLAUDE.md`：二者均只声明权威源、给指针，无职责边界表 / 无需求路由表 / 无上下文加载规则正文。 | TODO |
| AC-02 | 两个入口文件都**真实指向** `AGENT-INDEX.md`，且路径可解析。 | 正向解析：两文件内的 `AGENT-INDEX.md` 链接在仓根确实存在（不是只做字符串 grep）。 | TODO |
| AC-03 | `agent-workspace-conventions.md` 的「第 13 节」全部改为真实存在的第 10 节。 | 修前 `grep -rn "第 13 节" docs/` 命中 **2** 处；修后 **0** 命中；并核对 `AGENT-INDEX.md` §10 标题逐字为「Agent 入口与执行快照」。 | TODO |
| AC-04 | §10 校验表里 `verify_agent_entry.py` 的 WARN 读数与实测一致。 | 实跑 `verify_agent_entry.py` 取数，与表内文字逐条比对；表内注明重测日期。 | TODO |
| AC-05 | 两个 skill 的第 1 步指向 `AGENT-INDEX.md`，且**生成副本同步**。 | 源：`grep -rn "Root \`AGENTS.md\`" skills/` → 0 命中；副本：`.claude/skills` 与 `.codex/skills` 下同名文件内容与源一致；`sync_skills.py check` 绿。 | TODO |
| AC-06 | 生成副本确实随源改变（不是「check 绿」就够）。 | 变异式对照：改源前记录副本第 1 步文本，同步后重读副本确认已变；并证明 `check` 在源改、副本未同步时**会红**。 | TODO |
| AC-07 | 既有测试基线不回归。 | `python3 -m unittest discover -s tests -q`：变更前后均为 **73 tests / 4 红**，且 4 条红项**逐条同名**。 | TODO |
| AC-08 | 三个验证器全绿。 | `verify_delivery_governance.py`（`Active CHG: CHG-20260925-062`）、`verify_agent_entry.py`（0 warning）、`verify_skills.py`（verified 10）。 | TODO |
| AC-09 | 治理一致：快照、LEDGER、`delivery/active` 互指同一 CHG（关闭后同指 `none`）。 | 两个治理验证器 + 逐处读文件核对。 | TODO |
| AC-10 | 无主脏文件已按裁定处置，工作区只含本 CHG 的预期改动。 | `git status --porcelain` 逐文件对照 §5 Scope；`2026-09-24-m4-m5-cloud-content-production.md` 与 HEAD 逐字一致。 | TODO |
| AC-11 | 只登记的项**未被静默修掉**。 | 读 `verify_agent_entry.py:241` 与原样、`AGENT-INDEX.md` §12 校验清单原样；diff 显示二者未被改动。 | TODO |
| AC-12 | **本 CHG 对三仓零读写**。注意判据已按实测收窄：不能写「三仓工作区全空」，因为 desktop 与 cloud **先于本会话**就已脏（见 §4 末条）。 | 逐仓 `git status --porcelain -uall` + **逐文件 mtime 归属**：三仓的 `.claude/skills`/`.codex/skills` 均未出现在 status 中；desktop 的 13 个 `.rs` 与 cloud 的 `dump.rdb` 的 mtime 全部早于本会话。 | TODO |

## 11. Evidence

Evidence files live in `evidence/` and must record facts, not repeat requirements.

计划落盘的（建 CHG 时的清单，实际以本节末的最终清单为准）：

- `evidence/task-01-governance.md`：建 CHG 与激活；LEDGER 表行、快照再生成、两个验证器读数。
- `evidence/task-02-entry-refactor.md`：重构本体的逐文件差量、diff 无夹带的核对、还原尾部空行的复核。
- `evidence/task-03-drift-sweep.md`：三处引用的**先红后绿**（含一次真实的「修前命中 2 / 修后 0」）、
  §10 读数的重测对照。
- `evidence/task-04-skills-pointer.md`：源改前 `sync_skills.py check` 的红、同步后的绿、
  生成副本内容确实改变的读数。
- `evidence/task-05-close.md`：验收矩阵逐条判据、门禁读数、归档与指针扫描（分母 + 阳性对照）。
- `evidence/artifacts/`：原始输出。

（最终落盘清单在 T-05 收尾时按实际改写本节。）

## 12. Current Checkpoint

Completed:
- Start Gate：`active`/`LEDGER`/快照三者一致指向 `none`；无阻塞 `Q-xx`；Level S 不强制 Milestone。
  工作区 6 个脏文件已核实归属（其中 5 个是本 CHG 的对象，1 个是无关的尾部空行）。
- D-02 已执行：`2026-09-24-m4-m5-cloud-content-production.md` 还原，与 HEAD 逐字一致。

Current:
- T-01 建本记录并激活。

Next:
- T-02 提交入口重构本体 → T-03 修 conventions 引用 → T-04 修 skill 指针 → T-05 收尾。

Blocked:
- None.

Recent verification:
- `git status --porcelain -uall` → 5 个修改文件（`AGENT-INDEX.md`、`AGENTS.md`、`CLAUDE.md`、`README.md`、
  `agent-workspace-conventions.md`），无新增未跟踪文件。
- `verify_agent_entry.py` / `verify_delivery_governance.py` / `verify_skills.py` 开工前均绿；
  `unittest discover -s tests -q` → **Ran 73 tests / FAILED (failures=4)**（那 4 条既知红项，见 §10 AC-07）。

## 13. DONE Gate

逐项签字（判据写在签字行里，勿只读勾）：

- [ ] **Scope completed.**
- [ ] **No blocking `Q-xx`.**
- [ ] **Acceptance matrix all PASS.**
- [ ] **Automated tests passed or justified.**
- [ ] **Manual verification evidence recorded where required.**
- [ ] **Diff checked for out-of-scope changes.**
- [ ] **Runtime repositories touched only if listed in scope.**
- [ ] **Required baselines updated.**
- [ ] **Affected repositories committed independently.**
