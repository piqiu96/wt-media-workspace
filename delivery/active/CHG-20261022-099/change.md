---
id: CHG-20261022-099
parent: none
status: VERIFYING
depends_on: []
affected_repos: ["wt-media-workspace"]
risk: M
---

# CHG-20261022-099: AI Coding 工程治理与执行流程收口

## Change

在现有 Workspace 治理上收口 CHG 元数据、多 Active CHG 规则、可再生的当前上下文和薄 `wt` CLI。新 CHG 工作分支统一为 `chg/<CHG-ID>`；稳定版发布从 `main` 创建 `release/<产品Tag>` 后打 Tag，发布前用四个 GitHub Compare 页面 Review 四仓差异。复用原有交付记录、验证脚本与环境入口；不修改业务运行时代码。现有 CHG-20261015-098 继续按旧分支事实执行，新分支/PR 规则从本 CHG 起适用。

## Done When

- 新 CHG 模板只要求最小元数据和 `Change` / `Done When`，现有 CHG 仍可读取。
- 多个独立 Active CHG 可通过一致性校验；一个工作树一次只选定一个执行 CHG，依赖未归档或合并证据不足时不得启动。
- `CURRENT_CONTEXT` 可重新生成且不成为 Git 中的第二状态事实；`wt status/start/resume/verify/dev/test` 复用现有命令。
- 新 CHG 工作分支命名为 `chg/<CHG-ID>`，不写入执行器；旧记录不追溯改名。
- 稳定版产品 Tag 从 `main` 提交并创建同 commit 的 `release/<产品Tag>`；RC 不建发布分支，Tag 仍是唯一发布触发器。
- 稳定版发布前可通过四个 GitHub Compare 页面查看上一稳定版到本次的四仓完整差异。
- 文档生命周期由目录位置表达，不新增长期状态字段；`docs/` 只保留当前事实，`SUPERSEDED` 仅作临时迁移标记。
- 冲突按事实归属裁定，不设产品/工程/实现全局顺序；用户明确裁定必须回写正式事实源。
- 当前文档链接与 `SUPERSEDED` 替代指针有机检；`docs/superpowers/` 不整体视为历史。
- 现有历史目录职责已收敛，不新增 `archive/`。
- 原有治理、Skill、四仓测试入口未被破坏；按用户方案执行指定演练并记录结果。

## Constraints / Not In Scope

- 不创建 Dashboard、调度平台、复杂 DAG、Worktree Manager 或第二套 Delivery/Context/Test 事实源。
- 不新增自研 diff 工具、跨仓聚合页面或 `release/*` 分支的独立 workflow 触发器；发布分支只服务稳定版。
- 不批量迁移或合并历史文档，不删除现有文档，不新增文档状态字段，不引入产品/工程/实现全局优先级。
- 本 CHG 不代签 M4-H2 / M5-AC-13，也不改变 CHG-098 的既有 `main` 提交历史。

## References

- 用户 2026-10-22 提供的《AI Coding 工程治理与执行流程收口》方案与本轮三个边界裁定。
- `AGENT-INDEX.md`、`delivery/MASTER_IMPLEMENTATION_PLAN.md`、`scripts/README.md`、`templates/delivery/`。
