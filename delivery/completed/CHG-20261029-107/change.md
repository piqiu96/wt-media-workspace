---
id: CHG-20261029-107
parent: none
status: DONE
depends_on: []
affected_repos: ["wt-media-workspace", "wt-media-cloud"]
risk: M
---

# CHG-20261029-107：游戏目录改为扁平业务类目

## Change

把现有只表达游戏的 `operation_games` 收敛为扁平业务类目 `categories`：表 ID 从字符串改为自增 `BIGINT`，增加代码固定的 `type` 一级类型（首批 `game/ai/anime`），类目名称由运营直接维护，例如 `游戏.三角洲`、`AI.代充`、`二次元.原神`。同步把用户范围、社媒账号、内容挖掘和内容生产中的 `game_id/game_ids` 改为 `category_id/category_ids`，不建立层级表、不保留双写兼容字段。

本 CHG 是 [ADR-0028](../../../docs/decisions/0028-flat-business-categories.md) 的唯一落地记录，必须在 CHG-20261028-099 完成前结束。社媒账号允许零个类目，表示尚未分类；内容来源、挖掘策略、合成策略/任务/成片新增时必须选择单个类目。筛选和账号分组条件可不带类目，表示全部类目。系统不假定 `other` 必然存在。

## Done When

- `categories` 使用自增主键和固定 `type`；4 条现有类目全部回填 `type=game` 并完成 ID 映射；7 个依赖 `game_id` 列全部迁移为 `category_id` 且外键/索引有效。
- 用户类目范围、社媒账号类目关系、挖掘策略/内容、合成策略/任务/成片均使用新字段并可正常读写。
- `game_id`、`game_ids`、`GameID`、`game_ids` 不再出现在当前 Cloud API、模型、业务页面和当前文档；历史归档除外。
- 类目管理不再允许维护任意字符串 ID；页面按完整名称展示，不解析“游戏.”等前缀。
- 历史空类目保留为空，不自动创建或回填 `other`；新创建的内容/策略必须由调用方提交类目。
- 社媒账号允许保存零个类目关系，页面显示“—”；不得伪造 `other` 关系。
- 社媒账号选择多个类目时，所选类目必须属于同一 `type`；用户授权范围和筛选条件允许跨类型。
- Cloud Go/前端测试、双入口构建、迁移重放和关键页面读回通过；Workspace 文档及治理校验通过。

## Constraints / Not In Scope

- 不新增一级类型表、`parent_id`、路径或通用标签模型；一级类型只使用 `categories.type` 与代码常量。
- 不迁移历史归档文档正文，不为旧 `game_id` 提供长期兼容接口。
- 不修改 Desktop 原生代码；Desktop 继续消费 Cloud 共用 Web 构建。

## References

- [ADR-0028](../../../docs/decisions/0028-flat-business-categories.md)
- [产品第三章](../../../docs/product/prd/详细文档/第三章_用户与账号管理.md)
- [最终类目迁移计划](plan.md)

## Acceptance

2026-10-29：计划内数据库迁移、Cloud Go/前端、Cloud/Desktop 双入口构建、Workspace 文档与治理检查、API 实测及类目页读回均通过。完整命令、迁移计数和已知的无关 M1 verifier 环境限制见 [verification](evidence/verification.md)。
