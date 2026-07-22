# M2 Milestone Refinement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 暂停 `CHG-20260722-021` 的执行，先基于现有产品、工程、M2 设计、代码事实和差距报告形成可供用户纠正的 M2 对照稿；用户确认后，才修订唯一 Milestone 基线并同步收敛 CHG。

**Architecture:** 保持现有治理分层，不新增第二套 Design 或状态体系。`docs/product` 与 `docs/engineering` 继续分别保存产品和工程事实，`docs/superpowers/specs` 继续作为 AI 分析材料，`delivery/milestones/M2-account-runtime.md` 是 M2 唯一业务闭环基线，`delivery/active/CHG-20260722-021/change.md` 只描述当前闭环的执行范围。此次工作分为“暂停、对照、人工确认、基线修订、CHG 对齐”五段，人工确认是强制门禁。

**Tech Stack:** Markdown、Python 3、现有 Workspace 治理校验脚本、Git。

**Global Constraints:** 不修改 Cloud、Agent、Desktop 业务代码；不要求用户重写 PRD；不在 CHG 中复制完整 Milestone；不把旧差距矩阵的状态直接当成当前代码事实；不新增 Milestone 状态枚举；不触碰用户现有未提交文件。

---

### Task 1: 暂停 CHG-20260722-021，锁定本轮输入

**Files:**
- Modify: `delivery/active/CHG-20260722-021/change.md`
- Read: `.ai/CURRENT_CONTEXT.md`
- Read: `delivery/LEDGER.md`
- Read: `delivery/MASTER_IMPLEMENTATION_PLAN.md`

- [ ] **Step 1: 记录暂停原因，不创造新状态**

在 `change.md` 的 Checkpoint 中明确：运行时执行暂停在 Task 1 之前，原因是 M2 Milestone 正在重新细化；保留现有 `IN_PROGRESS`，避免引入 `PAUSED` 等新的状态来源。

- [ ] **Step 2: 明确暂停边界**

写明暂停期间不得执行三角色验收、修改运行时代码、创建 M2-B～E CHG 或把 M2-A 标记完成；允许的工作仅为读取事实源、形成对照稿和治理文档校正。

- [ ] **Step 3: 核对唯一 Active CHG 指向**

确认 `.ai/CURRENT_CONTEXT.md`、`delivery/LEDGER.md` 和 `change.md` 都仍指向 `CHG-20260722-021`，只记录“执行暂停”，不创建并行 Active CHG。

- [ ] **Step 4: 验证无业务代码改动**

Run: `git status --short`

Expected: 仅出现本次治理文件以及工作开始前已存在的用户修改；Cloud、Agent、Desktop 仓库没有本计划产生的改动。

### Task 2: 建立 M2 逐条事实映射

**Files:**
- Read: `docs/product/prd/详细文档/第三章_用户与账号管理.md`
- Read: `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md`
- Read: `docs/engineering/architecture/社媒运营平台模块分界分层和通信规约.md`
- Read: `docs/contracts/contract-map.md`
- Read: `docs/decisions/0001-identity-bootstrap-and-game-scope.md`
- Read: `docs/decisions/0002-bitbrowser-profile-identity-normalization.md`
- Read: `docs/decisions/0003-local-agent-session-binding.md`
- Read: `docs/decisions/0004-sensitive-profile-task-locking.md`
- Read: `docs/superpowers/specs/2026-07-21-m2-completion-design.md`
- Read: `delivery/milestones/M2-account-runtime.md`
- Read: `delivery/reports/2026-07-21-m2-module-business-flow-current-state.md`
- Read: `delivery/reports/M2-prd-chapter3-gap-matrix.md`
- Read: `delivery/completed/CHG-20260721-020/evidence/governance-scope-audit.md`
- Inspect: `../wt-media-cloud`
- Inspect: `../wt-media-agent`
- Inspect: `../wt-media-desktop`

- [ ] **Step 1: 为 M2 总目标及 M2-A～E 建立来源清单**

每一项只记录原文位置和事实摘要，不复制整段 PRD。来源至少区分：产品要求、工程约束、Decision/Contract 约束、AI Spec 建议、当前代码事实、历史报告判断。

- [ ] **Step 2: 复核报告中的代码事实**

用 `rg` 定位对应页面、API、服务、任务类型、Agent executor、Desktop 命令和测试。凡报告与当前代码不一致，以当前代码和可运行测试为准，并在对照稿标为“报告已过期”，不得静默沿用。

- [ ] **Step 3: 区分四类缺口**

为每个缺口标记为：

1. PRD 已明确但 Milestone 遗漏；
2. PRD 表述宽泛，需要用户确认业务取舍；
3. Milestone 已定义但操作顺序、外部副作用或失败边界不够明确；
4. Milestone 已明确，只是代码尚未实现，不属于本轮设计修订。

- [ ] **Step 4: 不把实现缺失误写成新需求**

例如“页面没有按钮”“接口未接入”应作为当前事实或后续 CHG 工作，不自动扩写成新的产品规则。

### Task 3: 生成供用户纠正的 M2 对照稿

**Files:**
- Create: `delivery/reports/2026-07-22-m2-milestone-refinement-comparison.md`

- [ ] **Step 1: 写总体对照表**

文件先列 M2 总目标、范围、A～E 顺序和总验收，固定列为：

```markdown
| 对照项 | 现有定义 | PRD依据 | ARCH/Decision约束 | 当前代码与报告事实 | 遗漏或歧义 | 建议修订 | 需要用户确认 |
```

- [ ] **Step 2: 为 M2-A～E 分别写对照表**

每个子阶段按以下业务维度逐条对照，而不是写长篇说明：用户目标、前置条件、用户操作顺序、Cloud/Agent/Desktop/外部系统动作、数据与外部副作用、成功判定、失败与恢复、不允许情况、与前后阶段的依赖。

- [ ] **Step 3: 将用户确认项收敛为短清单**

只把无法从 PRD、ARCH、Decision、代码事实推导的业务取舍交给用户。每项包含“当前理解、建议选择、选择后的影响”，不要求用户重新描述完整需求。

- [ ] **Step 4: 给出 Milestone 修订预览**

对照稿末尾附上修订后的章节目录，但不直接修改 `delivery/milestones/M2-account-runtime.md`。

- [ ] **Step 5: 自检来源完整性**

Run: `rg -n "现有定义|PRD依据|遗漏或歧义|建议修订|需要用户确认" delivery/reports/2026-07-22-m2-milestone-refinement-comparison.md`

Expected: 总体及 M2-A～E 均包含完整对照字段。

### Task 4: 人工纠正与确认门禁

**Files:**
- Review: `delivery/reports/2026-07-22-m2-milestone-refinement-comparison.md`

- [ ] **Step 1: 向用户展示中文对照稿**

按 M2 总体、M2-A、M2-B、M2-C、M2-D、M2-E 的顺序展示结论。优先突出会改变真实操作结果的差异，不让用户审核文件路径和技术实现细节。

- [ ] **Step 2: 等待用户纠正**

在用户明确确认前停止，不修改 Milestone，不调整 CHG 范围，不生成 M2-B～E CHG。

- [ ] **Step 3: 记录用户确认结果**

把用户的纠正直接合并进对照稿“确认结论”章节；不引入 DRAFT、REVIEWING、APPROVED 等文档状态。

### Task 5: 按确认结果细化唯一 M2 Milestone

**Files:**
- Modify: `delivery/milestones/M2-account-runtime.md`
- Modify: `delivery/MASTER_IMPLEMENTATION_PLAN.md` only if the confirmed M2 goal, ordering, dependency, or total exit condition changes

- [ ] **Step 1: 使用确认后的固定结构重写 Milestone**

采用用户提出的“目标—范围—子阶段—总验收”结构，并为每个 M2-A～E 固定使用：

```markdown
### 用户目标
### 前置条件
### 核心流程
### 系统要求
### 完成标准
### 异常与恢复
### 不允许情况
### 依据与关联 CHG
```

- [ ] **Step 2: 把完成标准写成可观察事实**

每个子阶段同时覆盖：用户页面结果、Cloud 正式数据、Agent/外部系统真实副作用、读回验证、失败结果。禁止使用“接口已存在”“任务已创建”“页面已完成”作为单独完成标准。

- [ ] **Step 3: 明确范围外内容**

在 Milestone 范围中增加“不包含范围”，阻止 CHG 为了方便提前实现 M3 以后能力。

- [ ] **Step 4: 删除 Milestone 内的可变状态枚举**

不加入 `TODO / DEVELOPING / VERIFYING / DONE` 字段。M2 当前状态继续由 `MASTER_IMPLEMENTATION_PLAN.md` 和 `delivery/LEDGER.md` 管理，Milestone 只定义“完成判定”。

- [ ] **Step 5: 控制重复内容**

PRD 和 ARCH 仅通过路径及章节引用；Milestone 只写业务闭环和完成事实；AI Spec 中的技术展开不复制进 Milestone。

### Task 6: 为 Milestone 结构增加轻量治理校验

**Files:**
- Modify: `scripts/verify_delivery_governance.py`
- Test: `tests/test_delivery_governance.py`

- [ ] **Step 1: 先增加失败测试**

新增测试，验证 M2 Milestone 缺少 M2-A～E 任一节、缺少固定子标题或 CHG 引用不存在时，治理校验明确失败。

- [ ] **Step 2: 运行目标测试确认失败**

Run: `python3 -m unittest tests.test_delivery_governance -v`

Expected: 新增用例因校验逻辑尚未实现而失败。

- [ ] **Step 3: 最小实现校验**

在现有治理脚本中增加 Milestone 结构检查，不解析自然语言内容，不建立新的状态机，不要求所有历史 M 立即迁移。

- [ ] **Step 4: 运行目标测试确认通过**

Run: `python3 -m unittest tests.test_delivery_governance -v`

Expected: 新增及既有治理测试全部通过。

### Task 7: 用户确认后同步调整 CHG-20260722-021

**Files:**
- Modify: `delivery/active/CHG-20260722-021/change.md`
- Modify: `delivery/LEDGER.md` only if the confirmed active scope or checkpoint changes
- Modify: `.ai/CURRENT_CONTEXT.md` only if its active-scope summary becomes inaccurate

- [ ] **Step 1: 逐项比较 M2-A 与 CHG-021**

生成“保留、删除、补充、移交后续 CHG”清单。只有属于确认后 M2-A 闭环的内容保留在 CHG-021。

- [ ] **Step 2: 调整 CHG 而不复制 Milestone**

CHG 保留 Milestone 锚点、当前代码差距、本次范围、任务、验收方法和 Evidence 要求；核心业务流程直接引用 Milestone 对应章节。

- [ ] **Step 3: 解除执行暂停**

更新 Checkpoint：记录 Milestone 已由用户确认、CHG 已完成对齐、下一步恢复到哪个具体 Task。若确认结果使 CHG-021 不再成立，则先给出关闭/替换建议并再次取得用户确认，不自行销毁 Active CHG。

- [ ] **Step 4: 不提前创建 M2-B～E Active CHG**

后续闭环只保留在 Milestone 的关联说明或候选映射中；仍坚持一次只激活一个 CHG。

### Task 8: 全量治理验证与提交

**Files:**
- Verify: `delivery/milestones/M2-account-runtime.md`
- Verify: `delivery/active/CHG-20260722-021/change.md`
- Verify: `delivery/reports/2026-07-22-m2-milestone-refinement-comparison.md`
- Verify: `scripts/verify_delivery_governance.py`
- Verify: `tests/test_delivery_governance.py`

- [ ] **Step 1: 运行 Workspace 验证**

Run:

```bash
python3 scripts/verify_delivery_governance.py
python3 scripts/verify_product_master_alignment.py
python3 scripts/verify_skills.py
python3 -m unittest discover -s tests -v
git diff --check
```

Expected: 所有命令通过；如果已有环境性跳过，必须原样记录原因，不能写成 PASS。

- [ ] **Step 2: 检查变更范围**

Run: `git status --short`

Expected: 不包含 Cloud、Agent、Desktop 业务代码变更；不覆盖工作开始前已有的 `.DS_Store` 和未跟踪用户文件。

- [ ] **Step 3: 提交治理变更**

仅暂存本计划涉及的 Workspace 文件并提交：

```bash
git add docs/superpowers/plans/2026-07-22-m2-milestone-refinement.md delivery/reports/2026-07-22-m2-milestone-refinement-comparison.md delivery/milestones/M2-account-runtime.md delivery/active/CHG-20260722-021/change.md delivery/LEDGER.md .ai/CURRENT_CONTEXT.md scripts/verify_delivery_governance.py tests/test_delivery_governance.py
git commit -m "docs: refine M2 milestone baseline"
```

提交前移除实际未修改的路径，避免把无关文件带入提交。

## Self-Review

- 计划先暂停执行，再生成对照稿，符合用户要求的人工确认门禁。
- Milestone 格式保留用户提出的四层主体，并补充前置条件、异常恢复、依据引用和范围外内容。
- Milestone 不保存执行状态，避免与 Master Plan、Ledger 和 CHG 形成重复事实源。
- AI Spec 被保留为输入材料，但不能覆盖 PRD、ARCH、Decision、当前代码和用户确认。
- CHG 只在用户确认 Milestone 后调整，且一次仍只允许一个 Active CHG。
- 本计划不修改任何运行时代码，也不要求用户重写需求。

