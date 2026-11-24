---
id: CHG-20261124-107
parent: delivery/milestones/M7-batch-publishing.md#批次准备与正式创建
status: DONE
depends_on: ["CHG-20261120-106"]
affected_repos: ["wt-media-workspace", "wt-media-cloud", "wt-media-agent", "wt-media-desktop"]
risk: H
merge_commits: {"wt-media-workspace": "34713f7563675803bf572b63118d202361c72ff9", "wt-media-cloud": "60847fdeda19ef4d889de3ded3be2e9521ba6d93", "wt-media-agent": "7c87673ac389ec37f198a384405a7e8ce4dfae03", "wt-media-desktop": "e31e352d028034088985fdcd66d6f6eee11fd0c6"}
---

# CHG-20261124-107：批次配置与内容准备

## Change

运营完成本人账号批次的资源配对、批量文案/封面、四项执行设置和候选编辑，保存到Cloud。保存不创建publication_task、不占用成片；实际启动/建单/占用属于108。

完整业务/API/数据库/步骤/证据见[执行落地清单](plan.md)。2026-11-25用户授权依次完成107→108→109的编码、测试、PR修复、E2E和走查。本项已完成实现、独立审查修复、真实环境及Web/安装版E2E和走查；Cloud PR50、Agent PR18、Desktop PR17已合入main。Workspace以PR63收口归档，技术内容基线34713f7作为可核对祖先提交，PR63最终合并SHA由后继CHG依赖证据记录。状态只在本文件，实际结果在清单与evidence中逐项记录。

## Done When

- 真实资源、批量内容、保存/编辑/复制与续编按批准原型可用，候选增删/替换/重排不误改原目标。
- 保存后batch/config/文件引用一致，正式task/attempt/成片占用增量为0；请求防重/修订冲突和权限经验证。
- 契约/迁移/消费者与Web和安装版定向验收完成，提供方先行合并main且证据可追溯。

2026-11-25执行授权：用户要求107→108→109依次自行完成编码、测试、PR及问题修复、E2E与页面走查，最后统一人工整体验收。分项以真实技术验收和合入证据推进，不提前宣称用户最终验收。前置106已由用户签收归档；本项代码在wt chg start预检通过后开始。

## 技术交付结论（2026-11-25）

107技术验收通过，正式证据见evidence/installed-e2e.json、backend-verification.md与merge-and-verification.md。用户明确要求依次自行完成107→108→109，最终再做整体验收；本项DONE表示独立技术交付收口，为108提供依赖，不冒称用户最终签收。用户补充强调必须以Cloud web/example原型为输入；本项固定dabc473，后继继续遵循。
