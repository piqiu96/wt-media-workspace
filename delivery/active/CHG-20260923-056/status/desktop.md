# CHG-20260923-056 — wt-media-desktop 状态

- 2026-09-23：审计完成（main.rs 1570 行、模块空壳、无日志/配置、端口写死、sidecar stdout 丢弃）。待执行 T-06～T-07。
- 2026-09-23 T-01：AI 入口文档独立提交 `47a6263`（`AGENT-INDEX.md`/`AGENTS.md`/`CLAUDE.md` 改动 + 新增 `DIRECTORY_MAP.md`）。注意 `DIRECTORY_MAP.md` 描述的是**重构后的目标布局**（当前 `commands/` 等仍是空壳、17 个命令仍在 `main.rs`），T-10 按其实际落位回写。
- 2026-09-24 T-06：拆分完成，`c03d244` → `4b3a7b4` 共 11 个 commit。`main.rs` **1570 → 89 行**（AC-04）；测试 **11 → 42**，逐 commit 单调不减；`generate_handler!` 17/17 逐字同序；9 条既有测试逐字不变、17 命令的 7 处改动逐条归因到计划内改动（3 条 sidecar 委托 + 4 条 preflight 去重）。新增 `config.rs`、`paths.rs`、`state.rs`、`http/`、`sidecar/`、`preflight.rs`、`dto/`、`commands/`。
  - **中间态（T-07 接线后消除）**：bin target 27 条告警里 23 条是 `config.rs`(16) + `paths.rs`(7) 的「从未使用」——两个模块已就位但还没有消费者。
  - **未落地，归 T-07**：计划 T-06 目标树列的 `bootstrap.rs`、`dto/config.rs`、`commands/public_config.rs` 其内容实际是 T-07 的；`8765` 字面量与 CSP 字面量仍在（T-07）。
  - **覆盖缺口（登记）**：被删的 2 条 `local_agent` 测试里，`empty_binding_ticket_is_rejected_before_transport` 是「空票据在发请求前被拒绝」的唯一测试；活规则在 `commands/bind.rs:48-50`，但从未被覆盖——规则没丢，验证丢了。
  - **仓库级发现（登记）**：M0 时期的整套 Node 工具链（CI workflow + 6 个 `npm` shell script + 2 个 mjs）引用的 `package.json` 不存在，**该 CI workflow 在任何分支上都不可能通过**。本 CHG 只改了被授权的 `scripts/test.sh`。
