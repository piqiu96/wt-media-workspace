# CHG-20260923-056 Checkpoint

## 2026-09-23

Completed:
- 三仓结构审计（Desktop/Agent/治理），现状事实录入 change.md §4。
- 用户裁定：融合方案一（ADR-0016 目录 + 新方案内容）；本会话仅 CHG-A；模块分工多文件同步回写。
- 治理工件：程序总纲、CHG-056 change.md、planned 057/058/059 登记、LEDGER 同步。
- T-01：四仓 AI 入口文档各自独立提交（desktop `47a6263`、cloud `3b733ff`、workspace `e0444cd`；agent 上一轮 `d3ab02f` 已提交）；配置格式按 D-05 回写为 TOML（`change.md` §6 D-01/§2/§5/§7/§8 + 程序总纲 §2 + planned CHG-059）；测试基线证据按模板规范化。

Current:
- T-02 Agent 结构迁移（纯移动，13 个 commit，每个以 `Ran 85 tests OK` 为闸门）。

Next:
- T-03 Agent runtime/config + paths。

Blocked:
- None.

Recent verification:
- 审计：源码级 grep/阅读，2026-09-23。
- 基线：`bash scripts/test.sh` → `Ran 85 tests in 1.628s` / `OK`（agent `HEAD=99f408c`）；见 `evidence/task-02-baseline.md`。
- TOML 裁定依据实测复核：Cloud `config/` 13 个 TOML / 0 个 YAML；agent `dependencies = []` 且 `uv.lock` 无 YAML 解析器（阳性对照 `grep -c name uv.lock` = 20）；`tomllib` 在 3.12 起为标准库。
