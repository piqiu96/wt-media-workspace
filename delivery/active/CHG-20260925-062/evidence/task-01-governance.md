# Evidence: T-01 建 CHG 并激活

- CHG: `CHG-20260925-062`
- Task: `T-01`
- Date: 2026-09-25
- Type: command
- Status: PASS

## Purpose

证明本 CHG 已在治理上真正激活：目录、LEDGER 表行、执行快照三者互指同一 CHG，
且两个治理验证器与 skill 验证器均绿。

## Method

```bash
python3 -B -X pycache_prefix=/tmp/pyc-none scripts/prepare_ai_workspace.py --change CHG-20260925-062
python3 -B -X pycache_prefix=/tmp/pyc-none scripts/verify_delivery_governance.py
python3 -B -X pycache_prefix=/tmp/pyc-none scripts/verify_agent_entry.py
python3 -B -X pycache_prefix=/tmp/pyc-none scripts/verify_skills.py
```

原始输出见 `artifacts/t01-activate.out`、`artifacts/t01-verify-{governance,agent-entry,skills}.out`。

## Expected

- 快照生成器报 `active_change = CHG-20260925-062`、`active_change_status = IMPLEMENTING`、
  `affected_repositories = ["wt-media-workspace"]`；Level S ⇒ `active_milestone = null`。
- `verify_delivery_governance.py` → `ok`，且指名的 active CHG 与快照一致。
- `verify_agent_entry.py` → `0 warning`。
- `verify_skills.py` → `verified 10`。

## Actual

- `prepare_ai_workspace.py` exit 0：`active_change: CHG-20260925-062`、
  `active_change_status: IMPLEMENTING`、`active_milestone: null`、
  `affected_repositories: ["wt-media-workspace"]`。
- `verify_delivery_governance.py` exit 0：`Delivery governance verification ok. Active CHG: CHG-20260925-062`。
- `verify_agent_entry.py` exit 0：`execution snapshot: 1923 characters (~769 tokens, budget 8000 characters)`、
  `Agent entry verification ok. 0 warning(s) need review.`
- `verify_skills.py` exit 0：`verified 10 skill source files`。

## Follow-Up

- **LEDGER 表行必须是裸 id**。本次写的是 `| CHG-20260925-062 | … |`，一次通过；
  写成 markdown 链接会让 `LEDGER_ROW_RE` 匹配不到，两个验证器会同报
  `current context and ledger disagree: CHG-… != none`——CHG-060 踩过这个坑
  （见 `delivery/completed/CHG-20260924-060/evidence/task-01-governance.md`），此处预先规避。
- 归档时（T-05）需把该表行移除并重生成快照为 `none`，否则 `prepare_ai_workspace.py --no-active`
  会以「仍有 active CHG」拒绝。
