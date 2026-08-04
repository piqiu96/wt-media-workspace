# ADR-0009: User Role, Team, and Identifier Model

- Status: Accepted
- Date: 2026-07-22
- Scope: M2及后续全部业务数据权限
- Supersedes: ADR-0001中关于角色命名和用户标识实现的相关假设；游戏范围稳定字符串规则继续有效

## Decision

- `users.id` 使用自增主键，页面称为 UID；全部 `user_id` 外键与Contract同步迁移；
- 固定角色为 `admin`、`senior_operator`、`operator`，原 `technician` 迁移为 `admin`；
- 普通运营和高级运营必须属于一个扁平运营分组，管理员不属于分组；
- 普通运营权限为本人资源与游戏范围的交集；高级运营权限为所属分组与游戏范围的交集；管理员拥有全部Cloud数据权限；
- 运营分组不提供停用；无用户且无历史数据的空分组可删除，有关联数据的分组保留；
- 用户转组后新数据使用新分组，历史数据保留原分组；
- 管理员和高级运营的Cloud权限不能绕过Desktop、Local Agent、BitBrowser身份、Profile授权和本地敏感资源边界。

## Consequences

- 现有字符串用户ID、`technician`枚举和只按游戏范围授权的实现均需要迁移；
- 后续业务对象应保存能够执行对应权限判断的用户、运营分组和游戏归属，但各领域的创建人、所有人和执行人不得被一个含义模糊的字段替代；
- M2-A先完成身份、分组和权限基础，M2-B～M10在各自对象落地时复用并验证该模型。
