<!-- governance: class=historical default_load=never -->

# Historical Reports

This directory holds stage audit and special-check reports that retain independent value. It is not a status source and is not loaded by default.

## How to use it

- Read a report only when a task explicitly names it as historical context.
- Current delivery state lives in [the Ledger](../LEDGER.md), `delivery/active/`, and `delivery/milestones/`.
- A report's conclusion must be written back to the owning CHG, milestone, or stable fact source; the report is not the fact.
- After the conclusion is written back, delete the report when it has no continuing audit or evidence value. Do not keep it only because it might be useful later.
- Do not rewrite a report that is retained. If a conclusion becomes current, update the owning fact source instead.
