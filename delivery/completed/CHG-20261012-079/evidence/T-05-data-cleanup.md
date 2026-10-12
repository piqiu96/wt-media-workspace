# T-05 旧模型验收数据清理

- 日期：2026-10-12
- 环境：本机开发库 `wt_media_cloud`

## 清理前核对

- 库中已登记 `20261012_050_compose_templates`；策略表已有 `compose_template_id`、`compose_template_version`，模板表有 `basic_cut` v1。该迁移文件在 Cloud 工作区尚未提交；此状态先于本次清理存在。
- 旧 T-04 验收策略为 ID 1–4，名称均以 `CHG079` 开头；验收账号为 ID 5、6（`chg079_senior`、`chg079_operator`）。
- 外键引用核对：两账号只被这 4 条策略、2 条审计记录、2 条会话、2 条游戏范围记录引用；其他引用表计数均为 0。

## 操作与结果

在一个事务中按上述精确 ID 和名称删除旧策略、关联审计记录、会话、游戏范围及验收账号。随后按 ID、代码、版本以及“无策略引用”条件，删除此前 050 草稿迁移提前插入的 `basic_cut` v1 模板。其他业务数据未改动。

| 项目 | 删除数 | 删除后目标残留 |
| --- | ---: | ---: |
| 旧验收策略 | 4 | 0 |
| 验收账号审计记录 | 2 | — |
| 验收账号会话 | 2 | — |
| 验收账号游戏范围 | 2 | — |
| 验收账号 | 2 | 0 |
| 草稿模板 `basic_cut` v1 | 1 | 0 |

状态：PASS。Cloud 工作区的 050 迁移已修正为只建表、不插入模板；`go test ./internal/infra/database/migration -count=1` PASS，`./scripts/migrate.sh` 在已升级开发库重跑显示 `0 applied, 52 total`。临时隔离 schema 中实际执行 049→050 后确认：模板 0 条、旧版本表不存在、策略新列 2 个、模板唯一索引覆盖 2 列；测试结束后临时 schema 已删除。

## 051 结构对齐（同日补做，Cloud 提交 `3535f86`）

- 背景：休眠的 `compose_strategies` 仍带旧列名 `parameters_json` / `allowed_overrides_json`。ADR-0021 下策略的自身设定是由所绑定模板版本 schema 校验的单一 `config`；可覆盖性已由模板 schema 声明，独立的覆盖清单没有归属方。迁移 `20261012_051_compose_strategy_config.sql`（RENAME parameters_json → config_json；DROP allowed_overrides_json）。
- 先红：`TestComposeStrategyConfigurationHasOneSchemaOwnedSource` 因 051 不存在而失败；实现后绿。
- 开发库：051 首次应用 `1 applied, 53 total`，重跑 `0 applied`；`DESCRIBE compose_strategies` 确认 `config_json` 在、`allowed_overrides_json` / 版本列 / 版本表均不在；模板 0 行、策略 0 行。
- 回归：`go test ./... -count=1` 67 包 ok / 0 FAIL；web 全量 507 测试 PASS；`build:cloud`、`build:desktop` PASS。
