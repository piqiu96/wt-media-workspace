# CHG-20260924-060 — wt-media-agent 状态

- 2026-09-24 T-01：未开始。
- 2026-09-24 T-04（删占位包，commit `c33680f`，3 处改动：删 2 个 `__init__.py` + 收紧常量与注释）：
  删 `src/wt_media_agent/{modes,generated}/`（各只有一行 docstring 的 `__init__.py`）；
  `tests/test_dependency_boundaries.py:80` 的 `PLACEHOLDER_PACKAGES` 由三者收紧为 `{"adapters"}`，注释同批改写。
  - **该删的依据（逐字核过）**：架构基线 §5.2 `:1040` 明写不保留 `modes/`、`generated/`，
    且该名单**不含** `adapters/` ⇒ 删除是让代码满足基线，**基线无需回写**。
    ADR-0016 不改：其 Decision 从未点名这三个包，`Context:15` 提它们只是决策时的状态快照。
  - **删之前零引用**（grep 两向都做），不留悬空导入。
  - **先失败**：删后 R1 **恰好红两条**，一条一个包（`… must stay a placeholder, found []`）——
    这同时是 R1 的阳性对照。收紧常量后 **253 tests OK**（计数不变，两个包零测试）。
  - **副作用（已量）**：`len(self.files)` 65 → 63，对 `>= 60` 的余量由 5 缩到 3，仍绿，故不调阈值。
  - 文档悬空引用（`DIRECTORY_MAP.md:98/102/104/117`、`AGENTS.md:27/36`、`CLAUDE.md:9`、
    `AGENT-INDEX.md:64`）归 T-05；`adapters/` 保留（基线未撤销，且 R1 拿它当对照宿主）。
