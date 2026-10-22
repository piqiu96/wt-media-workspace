---
id: CHG-20261022-100
parent: none
status: IMPLEMENTING
depends_on: []
affected_repos: ["wt-media-workspace", "wt-media-cloud", "wt-media-agent", "wt-media-desktop"]
risk: M
---

# CHG-20261022-100: 存量文档、AI 上下文与知识事实治理

## Change

执行 `docs/standards/文档与知识事实治理规范.md`，处置存量历史噪音与重复事实：清退 `docs/superpowers/`，审计 `delivery/reports/`，压缩当前文档中的轮次/日期/CHG 过程叙述，修正入口与 AI Plan 规则，并按仓清理代码注释中的修改史与旧实现叙述。历史由 Git 承担，`delivery/completed/` 不迁移、不重写。不修改业务逻辑。

## Done When

- 当前正式文档的相对链接全部可解析；`docs/check.py` exit 0，索引数按处置结果更新。
- 没有 Active CHG 或当前文档引用已删除的 `docs/superpowers/`、`delivery/reports/` 文件；归档记录中的追溯链接不回改。
- `SUPERSEDED` 文档在引用迁移后删除，`docs/` 中不再残留 `SUPERSEDED` 指针。
- `.ai/CURRENT_CONTEXT.md` 只含当前 CHG、当前 Milestone 与正式 References，不默认加载 `delivery/completed/`、`delivery/reports/` 或已删除的历史材料。
- 当前文档理解核心规则不依赖 `delivery/completed/`；指向 completed 的链接只作追溯。
- `delivery/LEDGER.md` 与 `delivery/active/` 一致，CHG 状态词与 MASTER §3 一致。
- 代码注释清理未改业务逻辑；各受影响仓通过 compile/lint/定向测试，`git diff` 无无关格式化和业务修改。
- 每仓独立提交，工作树干净；未获授权不推送、不建 PR。

## Constraints

- 不新建 `archive/`，不机械迁移整个历史目录，不把旧文件搬到另一个目录后继续长期保存。
- 不重写 `delivery/completed/` 归档正文，不建立新的生命周期状态机或第二套 Delivery / AI Context。
- 正式事实无法确认时不删除，登记 REVIEW 并说明 Owner 与缺口。
- `delivery/completed/` 保持只读，不参与当前冲突裁定。
- `M4`、`M5` 与第五章 §5.7–5.10 由 CHG-20261015-098 写入；若该 CHG 工作树仍在改这些文件，本轮相应压缩延后并登记 REVIEW。

## Not In Scope

- 业务代码、接口、数据库 Schema 与运行行为。
- 全仓英文注释的中文化或机械删除所有复述型注释。
- 历史 CHG、已完成记录与旧报告的正文重写。

## References

- `docs/standards/文档与知识事实治理规范.md`
- `AGENT-INDEX.md`
- `docs/README.md`
- `delivery/MASTER_IMPLEMENTATION_PLAN.md`
- `delivery/milestones/M4-content-production.md`
- `delivery/milestones/M5-automatic-production.md`
- `docs/product/prd/详细文档/第五章_素材生产.md`
- `docs/devops/服务部署.md`
