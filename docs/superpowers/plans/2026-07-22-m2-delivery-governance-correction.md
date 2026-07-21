# M2 Delivery Governance Correction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish one human-maintained M2 business-closure baseline, retire the giant M2-A～E execution scope, align active context, and reduce WT Media governance to one planning Skill plus the existing execution Skill.

**Architecture:** Preserve the current product, engineering, contract, decision, MASTER PLAN, AI Spec, CHG, and Evidence layers. Add only `delivery/milestones/M2-account-runtime.md`; make CHGs reference one closure card; validate that `.ai/CURRENT_CONTEXT.md`, `delivery/LEDGER.md`, and `delivery/active` agree. All work stays inside `wt-media-workspace` and the root AI context—no Cloud, Agent, or Desktop business code changes.

**Tech Stack:** Markdown governance files, Python 3 standard library validation, repository-local Markdown Skills, Git.

## Global Constraints

- Do not modify `wt-media-cloud`, `wt-media-agent`, or `wt-media-desktop` business code.
- Preserve `docs/superpowers/specs/2026-07-21-m2-completion-design.md` as an AI design/implementation reference.
- Preserve all unrelated dirty files, especially `docs/engineering/.DS_Store`, `delivery/reports/2026-07-21-current-system-assessment.md`, and `docs/superpowers/plans/2026-07-21-m2-completion-program.md`.
- Do not mark M2 `DONE`.
- Do not activate more than one M/L CHG.
- Do not delete existing CHG-020 evidence or implementation history.
- Skill creation and editing must follow `skill-creator` and `superpowers:writing-skills` during execution.
- Every commit stages only files listed in its task.

---

### Task 1: Add a failing governance consistency check

**Files:**
- Create: `scripts/verify_delivery_governance.py`
- Test: `scripts/verify_delivery_governance.py`

**Interfaces:**
- Consumes: root `.ai/CURRENT_CONTEXT.md`, `delivery/LEDGER.md`, `delivery/active/*/change.md`, and milestone references in active CHGs.
- Produces: exit code `0` with a concise PASS summary, or exit code `1` with deterministic error lines.

- [ ] **Step 1: Implement the validator against the intended invariant**

Create a Python standard-library script that:

```python
WORKSPACE = Path(__file__).resolve().parents[1]
ROOT = WORKSPACE.parent
CONTEXT = ROOT / ".ai" / "CURRENT_CONTEXT.md"
LEDGER = WORKSPACE / "delivery" / "LEDGER.md"
ACTIVE = WORKSPACE / "delivery" / "active"
MILESTONES = WORKSPACE / "delivery" / "milestones"
```

It must parse the Active CHG ID from Current Context and Ledger, enumerate active `CHG-*/change.md` records, and report errors when:

- the three Active CHG views disagree;
- Current Context points to a missing change file;
- more than one active M/L CHG exists;
- an active M/L CHG has no `Milestone:` reference;
- the referenced milestone file or anchor does not exist.

Use stable error messages such as:

```text
ERROR current context references missing CHG: CHG-20260715-010
ERROR active CHG has no milestone reference: CHG-20260721-020
```

- [ ] **Step 2: Run the validator and verify the current repository fails**

Run:

```bash
python3 scripts/verify_delivery_governance.py
```

Expected: exit `1`; output identifies the stale `CHG-20260715-010` Current Context and missing milestone link for `CHG-20260721-020`.

- [ ] **Step 3: Verify deterministic Python syntax**

Run:

```bash
python3 -m py_compile scripts/verify_delivery_governance.py
```

Expected: exit `0`.

- [ ] **Step 4: Commit the failing governance gate**

```bash
git add scripts/verify_delivery_governance.py
git commit -m "test: add delivery governance consistency gate"
```

---

### Task 2: Create the human-maintained M2 closure baseline

**Files:**
- Create: `delivery/milestones/README.md`
- Create: `delivery/milestones/M2-account-runtime.md`
- Modify: `delivery/MASTER_IMPLEMENTATION_PLAN.md`

**Interfaces:**
- Consumes: `docs/superpowers/specs/2026-07-21-m2-completion-design.md`, `delivery/active/M2-PLAN-20260716/plan.md`, current M2 reports, and MASTER PLAN.
- Produces: stable anchors `#m2-a`, `#m2-b`, `#m2-c`, `#m2-d`, and `#m2-e` for CHG references.

- [ ] **Step 1: Document the milestone rule**

Create `delivery/milestones/README.md` stating:

```markdown
# Milestone Business Closures

This directory contains the human-maintained business-closure baseline for each M.
It does not replace Product, Engineering, MASTER PLAN, AI Specs, CHGs, or Evidence.

Each closure card contains only:
- user goal;
- prerequisites;
- user operation order;
- system and external actions;
- success facts that must all hold;
- false-success behavior that is forbidden;
- linked CHGs.
```

- [ ] **Step 2: Write the five M2 closure cards in Chinese**

Create `delivery/milestones/M2-account-runtime.md` with the fixed structure:

```markdown
# M2 账号运行环境业务闭环

## M2-A
用户目标：
前置条件：
用户操作：
系统与外部动作：
成功必须同时满足：
失败时不得发生：
涉及 CHG：
```

Repeat for M2-A～E. Derive content from the approved M2 Completion Design, but make each card user-result-oriented and concise. M2-C must explicitly require proxy write plus BitBrowser read-back; M2-D must explicitly require Cookie write/read-back, account check, identity/status projection, partial success, and precise retry; M2-E must require the real Desktop/Sidecar path and final human acceptance.

- [ ] **Step 3: Link M2 from MASTER PLAN without duplicating flow details**

Add one Milestone reference in the M2 section:

```markdown
- Business closure baseline: `delivery/milestones/M2-account-runtime.md`
```

- [ ] **Step 4: Verify anchors and absence of placeholders**

Run:

```bash
rg -n '^## M2-[A-E]$' delivery/milestones/M2-account-runtime.md
rg -n 'TBD|TODO|待补充' delivery/milestones
```

Expected: exactly five closure headings; second command returns no matches.

- [ ] **Step 5: Commit the milestone baseline**

```bash
git add delivery/milestones/README.md delivery/milestones/M2-account-runtime.md delivery/MASTER_IMPLEMENTATION_PLAN.md
git commit -m "docs: establish M2 business closure baseline"
```

---

### Task 3: Audit and close the giant CHG-020 boundary

**Files:**
- Modify: `delivery/active/CHG-20260721-020/change.md`
- Create: `delivery/active/CHG-20260721-020/evidence/governance-scope-audit.md`
- Modify: `delivery/LEDGER.md`
- Modify outside the Workspace Git repository: `../.ai/CURRENT_CONTEXT.md`
- Move after completion: `delivery/active/CHG-20260721-020/` to `delivery/completed/CHG-20260721-020/`

**Interfaces:**
- Consumes: all CHG-020 evidence, commits named by that evidence, current code/test facts, and M2 closure cards.
- Produces: a truthful boundary statement separating verified foundation work from incomplete M2-B～E closures.

- [ ] **Step 1: Build a fact table from existing evidence**

For every CHG-020 Task and checkpoint claim, record in `evidence/governance-scope-audit.md`:

```markdown
| Claim | Evidence file | Commit/diff | Closure card | Result |
|---|---|---|---|---|
```

Use only `PASS`, `PARTIAL`, or `NOT PROVEN`. Code presence without real side effect/read-back is `PARTIAL` or `NOT PROVEN`.

- [ ] **Step 2: Reframe CHG-020 as completed foundation work only**

Update its title, goal, scope, checkpoint, and completion record so it claims only outcomes supported by evidence. Add:

```markdown
- Milestone: `delivery/milestones/M2-account-runtime.md#m2-a`
- Closure effect: foundation and partial implementation only; M2-B～E remain unaccepted.
```

Do not claim any M2 closure that lacks its full milestone success facts.

- [ ] **Step 3: Run the existing acceptance and repository checks referenced by CHG-020**

Run the exact automated commands already recorded in CHG-020 evidence. If a command no longer passes, record the failure and keep CHG-020 active until the governance-only discrepancy is resolved; do not fix runtime business code under this plan.

Expected: the previously claimed governance/test foundation remains reproducible, or the audit explicitly downgrades the claim.

- [ ] **Step 4: Complete and archive CHG-020**

Set status to `DONE`, move the directory to `delivery/completed/CHG-20260721-020`, and remove its row from `delivery/LEDGER.md`. Update `.ai/CURRENT_CONTEXT.md` to state that no M/L CHG is active pending creation of the next M2 closure CHG.

- [ ] **Step 5: Verify the repository has no active M/L CHG**

Run:

```bash
python3 scripts/verify_delivery_governance.py
```

Expected at this intermediate boundary: PASS with `Active CHG: none`, because no new CHG is activated in the same commit.

- [ ] **Step 6: Commit the CHG-020 boundary correction**

```bash
git add delivery/LEDGER.md delivery/active/CHG-20260721-020 delivery/completed/CHG-20260721-020
git commit -m "docs: close oversized M2 foundation change"
```

The root `.ai/CURRENT_CONTEXT.md` update is local workspace context and is verified by the governance script; it is not staged in the `wt-media-workspace` repository.

---

### Task 4: Add the unified planning and correction Skill

**Files:**
- Create: `skills/workspace/planning-wt-media-delivery/SKILL.md`
- Create by synchronization: `../.codex/skills/planning-wt-media-delivery/SKILL.md`
- Create by synchronization: `../.claude/skills/planning-wt-media-delivery/SKILL.md`

**Interfaces:**
- Consumes: Product, Engineering, Contracts, Decisions, MASTER PLAN, AI Specs, Milestones, current code/tests, CHGs, Evidence, and user corrections.
- Produces: impact report, Milestone updates, and one bounded CHG proposal; it never implements runtime code.

- [ ] **Step 1: Read required Skill-authoring guidance**

Before editing, read completely:

```text
/Users/aqiuye/.codex/skills/.system/skill-creator/SKILL.md
/Users/aqiuye/.codex/plugins/cache/openai-curated-remote/superpowers/6.1.1/skills/writing-skills/SKILL.md
```

- [ ] **Step 2: Write the planning Skill with one entry point**

The Skill must cover:

- new M planning from PRD/ARCH;
- MASTER PLAN and AI Spec analysis;
- Milestone creation or correction;
- reverse audit when implementation does not satisfy the M;
- small Bug/field impact classification;
- architecture-change escalation to Decision/Engineering;
- CHG creation/splitting with one active M/L CHG;
- mandatory human input only for user goal, operation order, real success effects, and forbidden false success.

It must explicitly prohibit runtime implementation and prohibit creating a second planning/impact/spec/CHG-planning Skill.

- [ ] **Step 3: Add scenario tests required by writing-skills**

Validate at least these prompts using the Skill test procedure:

```text
1. “账号列表增加 avatar 字段并修复展示错误。”
   Expected: direct small CHG; no Milestone rewrite.
2. “M2 开户完成了但没有写入 BitBrowser Cookie。”
   Expected: classify as closure gap; update M2-D/CHG, not a code-only patch.
3. “Cloud-Agent 通信原则改为推送。”
   Expected: require Decision + Engineering update before Milestone/CHG.
4. “根据 PRD 开始 M3。”
   Expected: analyze AI Spec/current code, produce a concise Milestone and bounded first CHG.
```

- [ ] **Step 4: Run Skill validation and synchronization**

Run:

```bash
python3 scripts/verify_skills.py
python3 scripts/sync_skills.py check --repo root
```

Expected: all Skill metadata and generated outputs are consistent.

- [ ] **Step 5: Commit the planning Skill**

```bash
git add skills/workspace/planning-wt-media-delivery
git commit -m "feat: add WT Media delivery planning skill"
```

The generated root `.codex` and `.claude` copies are verified by the sync checker but are not staged in the `wt-media-workspace` repository.

---

### Task 5: Tighten the existing execution Skill

**Files:**
- Modify: `skills/workspace/executing-wt-media-change/SKILL.md`
- Modify by synchronization: `../.codex/skills/executing-wt-media-change/SKILL.md`
- Modify by synchronization: `../.claude/skills/executing-wt-media-change/SKILL.md`

**Interfaces:**
- Consumes: exactly one active CHG and its referenced Milestone closure.
- Produces: code, tests, Evidence, checkpoint, and independent commits within the CHG scope.

- [ ] **Step 1: Add Milestone-aware authority and Start Gate checks**

Require the executor to report:

```markdown
- Milestone file and closure anchor;
- user-visible vertical result delivered by this CHG;
- inherited real-effect/read-back acceptance conditions;
- Current Context / Ledger / active-directory consistency.
```

Allow direct small Bug CHGs to cite a stable Product/Engineering/Contract requirement instead of a Milestone only when the planning Skill has classified them as not changing a business closure.

- [ ] **Step 2: Add a stop condition for design drift**

Add a rule: if implementation reveals a missing business step, false-success acceptance, architecture conflict, or scope spanning multiple closure cards, stop and return to `planning-wt-media-delivery`; do not infer and patch.

- [ ] **Step 3: Preserve the existing Task Protocol and Completion Gate**

Confirm the diff does not weaken:

- one Task at a time;
- failing verification before implementation;
- Evidence and checkpoint requirements;
- no future-scope implementation;
- independent repository commits.

- [ ] **Step 4: Validate the Skill**

Run:

```bash
python3 scripts/verify_skills.py
python3 scripts/sync_skills.py check --repo root
```

Expected: PASS and no unrelated generated diffs.

- [ ] **Step 5: Commit the execution Skill update**

```bash
git add skills/workspace/executing-wt-media-change/SKILL.md
git commit -m "docs: enforce closure-aware CHG execution"
```

The generated root `.codex` and `.claude` copies are verified by the sync checker but are not staged in the `wt-media-workspace` repository.

---

### Task 6: Activate the next bounded M2 CHG

**Files:**
- Create: `delivery/active/CHG-20260722-021/change.md`
- Modify: `delivery/LEDGER.md`
- Modify outside the Workspace Git repository: `../.ai/CURRENT_CONTEXT.md`

**Interfaces:**
- Consumes: the CHG-020 audit and first incomplete M2 closure card in sequence.
- Produces: one executable CHG with no implementation changes.

- [ ] **Step 1: Select the next closure from evidence, not assumed numbering**

Choose the earliest M2-A～E card whose success facts are not all proven. If M2-A is fully proven by the CHG-020 audit, select M2-B; otherwise create an M2-A completion CHG.

- [ ] **Step 2: Create one bounded `change.md`**

It must contain:

```markdown
- Milestone: one exact anchor from `delivery/milestones/M2-account-runtime.md#m2-a` through `#m2-e`, selected by the evidence audit
- Current proven facts
- Exact remaining gap
- One vertical user result
- Explicitly Not Doing
- Ordered Tasks
- Test and real acceptance method per Task
- Evidence requirements
- Checkpoint
```

Do not include work belonging to a later closure card.

- [ ] **Step 3: Synchronize all active pointers**

Add the CHG to `delivery/LEDGER.md` and update root `.ai/CURRENT_CONTEXT.md` with the same ID, title, status, file path, repositories, and required Skill.

- [ ] **Step 4: Run all governance gates**

Run:

```bash
python3 scripts/verify_delivery_governance.py
python3 scripts/verify_product_master_alignment.py
python3 scripts/verify_skills.py
git diff --check
```

Expected: all commands exit `0`.

- [ ] **Step 5: Commit the next executable CHG**

```bash
git add delivery/LEDGER.md delivery/active/CHG-20260722-021/change.md
git commit -m "docs: activate next bounded M2 closure change"
```

The root `.ai/CURRENT_CONTEXT.md` update is local workspace context and is verified by the governance script; it is not staged in the `wt-media-workspace` repository.

---

### Task 7: Final governance verification and handoff

**Files:**
- Create: `delivery/active/CHG-20260722-021/evidence/governance-start-gate.md`
- Modify: `delivery/active/CHG-20260722-021/change.md`

**Interfaces:**
- Consumes: final governance tree, Skill outputs, and validation commands.
- Produces: a reproducible start gate for executing the next M2 CHG.

- [ ] **Step 1: Record final verification**

The Evidence file must list command, expected result, actual result, PASS/FAIL, and commit references for:

```bash
python3 scripts/verify_delivery_governance.py
python3 scripts/verify_product_master_alignment.py
python3 scripts/verify_skills.py
git status --short
```

- [ ] **Step 2: Update the new CHG checkpoint**

Set:

```markdown
- Completed: governance correction and synchronized start gate.
- Current: no runtime implementation started.
- Next: execute Task 1 using `executing-wt-media-change`.
- Blockers: list actual blockers or `None`.
- Recent verification: exact PASS summaries.
```

- [ ] **Step 3: Confirm scope isolation**

Run:

```bash
git diff --name-only HEAD~1..HEAD
git status --short
```

Expected: only Workspace governance/Skill files and root `.ai/CURRENT_CONTEXT.md` were changed; pre-existing unrelated dirty files remain untouched.

- [ ] **Step 4: Commit the handoff evidence**

```bash
git add delivery/active/CHG-20260722-021/change.md delivery/active/CHG-20260722-021/evidence/governance-start-gate.md
git commit -m "docs: record bounded M2 start gate"
```

- [ ] **Step 5: Stop before business implementation**

Report the activated CHG, its Milestone closure, first implementation Task, real acceptance target, and remaining dirty files. Do not execute the CHG until the user explicitly asks to continue.
