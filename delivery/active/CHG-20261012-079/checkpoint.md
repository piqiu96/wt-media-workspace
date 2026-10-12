# Checkpoint: CHG-20261012-079

- CHG: `CHG-20261012-079`（M4-B 合成策略与版本）
- Status: IMPLEMENTING
- Updated: 2026-10-12

## Completed

- CHG070 与 M4-A 的用户签收已记录；M4-C2 范围已从 M4-C3 的任务创建与快照中分开。
- 已核对 Cloud 现状：`production` 仅有 M4-A 素材/使用关系接口，`/compose-strategy` 两端仍为 `ComingSoon.vue`，策略表和合同尚不存在。
- T-01：首个受控模板为 `basic_cut` v1.0，仅允许 16:9 / 9:16 和比例覆盖；字幕、BGM、片尾因没有资源合同而拒绝启用。新增策略当前表和不可变版本表的 Migration。
- T-02：Cloud 发布策略合同与命名错误；实现策略 Repository、Service、Handler。创建和修改在事务里写版本，修改用 `expected_version` 防止覆盖，列表在 SQL 层按团队和游戏过滤；未知请求字段被拒绝。顺手删去所改契约与 wire 测试开头的历史过程注释。
- T-03：新增共用策略页面 `modules/compose/pages/ComposeStrategyPage.vue` 与 API Client `shared/api/compose.js`，替换两端 `/compose-strategy` 的 ComingSoon 占位。高级运营/管理员可创建、编辑（打开时定格 expected_version）、复制（只发名称）与查看版本；普通运营只读。表单选项全部来自模板目录接口，字幕/BGM/片尾呈禁用态；字段级报错用 FormError，15204 冲突具名处理并重拉列表。routerParity 与列表页规范测试同步钉住两端同页。

- T-04（自动化部分）：真实 MySQL 迁移首次应用与幂等重跑 PASS；API 角色矩阵 15 组全部 PASS（创建读回、版本递增与不可变历史、陈旧版本 409、复制独立、普通运营只读与 inactive/范围外不可见、四类非法输入具名 15201、越权 15202/15203）；查库与 API 读回逐字段一致；`go test ./...` 68 包全绿。

## Current

Q-01（blocking）登记后实施暂停。T-04 自动化验收已完成（迁移、15 组 API 矩阵、查库一致、Go 68 包回归全 PASS）；页面走查因模型修正待决而搁置——若按提案移除策略版本记录，走查项 B（版本历史）与 C8（编辑版本递增）将不再存在。

## Next

1. 等用户裁定 Q-01：处置路径（改范围重开本 CHG / 关闭后另开新 CHG）与四个冲突点取舍（版本记录、模板入库、schedule、资产键时序）。
2. 裁定后按 `planning-wt-media-delivery` 更新范围定义（版本记录若移除需回写里程碑 M4-C2），再继续实施与验收。

## Blocked

- Q-01（blocking）：四层模型修正与已交付范围冲突，见 `change.md` §6；实施与走查暂停。
- 首个受控模板参数作为 T-01 的工程设计收口（若 Q-01 裁定模板入库存表，此收口随之重做）。

## Recent verification

| 检查 | 结果 |
| --- | --- |
| M4-A 用户走查 | 2026-10-12 用户确认通过；见 `delivery/reports/2026-10-12-m4-a-signoff.md` |
| CHG070 | 2026-10-12 用户确认走查通过并归档 |
| T-01 单测 | `go test ./internal/modules/production/model ./internal/infra/database/migration -count=1` PASS；其中模板非法参数和 Migration 结构测试先失败后通过 |
| T-01 真实数据库 | 尚未执行，T-04 将用 MySQL 验证首次迁移和再次执行 |
| T-02 单测 | `go test ./internal/modules/production/... ./internal/infra/database/migration -count=1` PASS；权限、非法请求、版本冲突、事务回滚均有定向测试 |
| T-02 合同 | Ruby YAML 解析四份 Cloud 合同 PASS；Go wire 测试对照返回字段 PASS |
| T-03 单测 | web/ 下 `npx vitest run` 全量 58 文件 527 测试 PASS；新增测试先红（模块与页面不存在、parity 指向 ComingSoon）后绿 |
| T-03 构建 | `npm run build:cloud`、`npm run build:desktop` PASS；两端 dist 均含 ComposeStrategyPage 分块并带 API 路径与页面标题 |
| T-04 迁移 | 真实 MySQL：`20261012_049_compose_strategies` 首次应用，重复执行 0 applied；表结构与设计一致 |
| T-04 API 矩阵 | 15 组全部 PASS（读回一致、版本不可变、409/15201/15202/15203 具名拒绝、范围外不可见）；查库与 API 一致 |
| T-04 Go 回归 | `go test ./... -count=1` 68 包 ok / 0 FAIL |
| T-04 页面走查 | 待用户执行（唯一未闭环项） |
