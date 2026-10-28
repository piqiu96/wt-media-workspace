# CHG107 · 类目迁移执行计划

## 任务理解

把“游戏”统一为扁平业务类目，只改领域命名和主键形态，不建设层级模型。CHG107 完成后，CHG099 才继续运营资源重构。

## 当前事实

- `operation_games` 4 行，字段为 `id/name/status/remark/created_at/updated_at`。
- 当前引用列为 `user_game_scopes.game_id`、`media_account_games.game_id`、`compose_strategies.game_id`、`compose_tasks.game_id`、`composite_outputs.game_id`、`discovery_strategies.game_id`、`source_contents.game_id`。
- `other` 仍被 506 条内容和 27 个挖掘策略引用，不能直接删除。
- 当前 ID 为字符串；`user_game_scopes` 没有目录外键。
- 当前 5 个社媒账号没有类目关系；在新模型下仍是合法的“未分类”账号，不补造关系。

## 目标模型

```text
categories
  id BIGINT AUTO_INCREMENT PK
  type VARCHAR(32)
  name VARCHAR(128) UNIQUE
  enabled TINYINT(1)
  remark VARCHAR(255)
  created_at, updated_at
```

`type` 是代码固定的稳定值，首批为 `game/ai/anime`；页面负责显示中文标签。

依赖收敛：

```text
user_category_scopes(user_id, category_id)
media_account_categories(media_account_id, category_id)
compose_strategies.category_id
compose_tasks.category_id
composite_outputs.category_id
discovery_strategies.category_id
source_contents.category_id
```

## 顺序任务

| Task | 工作 | 验收 |
| --- | --- | --- |
| 1 | 更新 ADR、产品字段和机器契约命名 | `category_id/category_ids` 为唯一正式字段 |
| 2 | 创建 `categories` 与临时旧 ID 映射 | 4 条类目映射完整，名称、启停和 `type=game` 保留 |
| 3 | 增加并回填 7 个 `category_id`，再删除旧列/外键 | 不假定 `other`；历史空值保留；外键和索引有效 |
| 4 | 重命名 `user_game_scopes`、`media_account_games` | 代码和数据读写使用新表名 |
| 5 | 更新 Cloud Go 模型、DTO、Repository、Service、Handler | 全仓无旧 `GameID` 业务字段 |
| 6 | 更新 Cloud/Desktop 共用前端页面和 API client | 页面文案统一“类目”，筛选/表单/列表读回正常 |
| 7 | 清理 `other` 自动默认，落实业务规则 | 账号零类目合法；新增内容/策略必选；筛选可空；不创建占位类目 |
| 8 | 落实一级类型约束 | 业务对象多选同类目只能同 `type`；权限和筛选允许跨类型 |
| 9 | 全量迁移重放和回归 | Cloud tests/build、Workspace docs/governance 通过 |

## 明确不修改

不新增一级类型表、层级、通用标签或父子树；一级类型只使用 `categories.type` 与代码常量。不改历史归档正文；不保留 `game_id` 双写兼容层。
