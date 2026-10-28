# ADR-0028：游戏目录改为扁平业务类目

- Status: Accepted
- Date: 2026-10-29
- Scope: 用户类目范围、社媒账号类目关系、内容挖掘、内容生产
- Supersedes: ADR-0011、ADR-0012；ADR-0001 的游戏稳定字符串规则

## Context

现有 `operation_games` 只表达游戏，ID 为非自增字符串。后续业务还需要 AI、二次元等类目。当前数据量很小，继续沿用 `game_id` 会把表名、字段、接口和页面文案长期分裂成两套概念。

## Decision

1. `operation_games` 重命名为 `categories`，ID 改为 `BIGINT UNSIGNED AUTO_INCREMENT`。
2. 类目保持扁平：只保存 `name`、`enabled`、`remark` 和时间字段；不增加 `parent_id`、层级、类型、路径或排序字段。
3. 二级含义直接写入 `name`，例如 `游戏.三角洲`、`AI.代充`、`二次元.原神`。后端不解析点号。
4. `user_game_scopes` 改为 `user_category_scopes`；`media_account_games` 改为 `media_account_categories`；所有 `game_id/game_ids` 改为 `category_id/category_ids`。
5. 内容挖掘、内容生产和媒体账号统一引用 `category_id`；不保留 `game_id` 兼容列或双写字段。
6. 社媒账号允许零个类目，表示尚未分类；列表显示“—”，不创建占位关系，也不进入特殊待处理状态。内容来源、挖掘策略、合成策略/任务/成片新增时必须带单个类目；查询筛选和账号分组条件可以不选，表示全部类目。
7. 系统不假设必然存在 `other`，也不自动创建或回填 `other`。若某环境本身已有 `other`，它只是普通可选类目；历史空类目保留为空，后续编辑时再按对应业务规则补齐。

## Consequences

- 这是一次 Cloud API、数据库、前端文案和契约的同步破坏性改名；不提供新旧字段并行写入。
- 迁移必须覆盖全部 7 个依赖列，但不得假定 `other` 存在。历史空类目保留为空；社媒账号零类目合法，内容/策略历史空值在再次编辑或进入相应执行流程时再补齐。
- 类目只有名称层级，后端无法按父类目结构化查询；如未来确实需要层级，再单独设计，不预留复杂字段。
