<!-- governance: class=index default_load=task -->

# 当前设计工作稿

本目录保存正在讨论、评审或等待回写的产品、交互及原型设计工作稿，不是正式 PRD、公共规范或第二套交付状态。通常按业务主题维护一份当前合并稿；区分用户已确认、建议和待讨论内容，不保存聊天全文、逐轮副本或临时截图。

## 当前入口

| 主题 | 工作稿 |
| --- | --- |
| 内容运营整体导航 | [内容运营](content-operations.md) |
| 发布管理、图片库与封面模板库 | [发布管理](publishing.md)：含[三平台字段调研](publishing.md#12-三平台发布字段调研与一次发布可行性2026-11-10)和字段取舍；已按[产品与交互评审](publishing.md#14-产品与交互全面评审及优化建议2026-11-10)完成三轮原型迭代，[结果与证据](publishing.md#15-自主迭代与视觉评审结果2026-11-10)自评 96/100，用户体验验收待进行 |
| 作品观察与爆款复刻 | [作品管理](works.md) |
| 主动互动与评论处理 | [互动管理](interaction.md) |
| 内容挖掘与逐页评审 | [内容挖掘](content-mining.md) |
| 已确认内容生产的阅读入口 | [内容生产导航](content-production.md)（仅导航，不重新打开已确认设计） |

原型源码统一由 [Cloud web/example](https://github.com/piqiu96/wt-media-cloud/tree/main/web/example) 维护。旧原型原样迁移，新原型与正在修改的页面逐步引用正式公共组件。文档与正式产品来源使用本仓相对链接。

## 完成与退出

1. 设计中持续更新当前稿，保留必要的决策来源、理由、原型场景和未决问题。
2. 已确认但尚未回写的内容暂时保留，明确承接位置。用户流程、字段及业务规则进入 [Product](../product/README.md)，公共视觉与交互规则进入 [Standards](../standards/frontend/README.md)，工程边界和取舍进入 [Engineering](../engineering/README.md) 或 [Decisions](../decisions/README.md)。
3. 待实施范围与验收要求由现有 [Delivery](../../delivery/MASTER_IMPLEMENTATION_PLAN.md) 承接，必要确认记录保持可追溯。设计确认、原型可操作、软件已实现和已验收分别表达。
4. 内容承接完成、未决事项已有去处并修复引用后，移除工作稿；有持续导航价值的文件只保留链接。历史由 Git/PR 追溯，不建立永久草稿或 archive 目录，也不必等待全部代码实现后才退出。

## 本地阅读

从 Workspace 运行 `python3 scripts/wt.py dev example`。该入口按 `config/repository-map.yaml` 定位 Cloud，并将当前 Workspace 文档根传给独立预览服务。原型入口为 `http://127.0.0.1:8768/example/`，本目录预览为 `http://127.0.0.1:8768/__docs/workspace/docs/design/README.md`。

预览读取已保存的本地文件，包含未提交修改；刷新后可见。GitHub 链接只展示已推送版本。本地只对已知仓库 main 分支文档链接做路径解析，具体提交或其他分支链接不自动替换。原型、演示数据和文档入口均不成为正式 Cloud/Desktop 的构建或运行依赖。
