# CHG-20261012-081 Checkpoint

## Completed

- 已确认 CHG079 结构和 CHG080 执行器验收完成，`basic_cut` v1 当前仅支持切段。
- 已修正 PRD §5.5 首版参数示例，与已验证执行代码一致。
- T-01 策略 API、请求/响应 schema、错误及枚举合同已定义并通过 YAML 解析；证据见 `evidence/T-01.md`。Cloud commit `b334437`。
- T-02 已从执行器代码发布 `basic_cut` v1 到真实 MySQL；两次发布读回同一模板 ID 3、版本 1、状态 active，schema/执行器与代码一致。证据见 `evidence/T-02.md`。Cloud commit `6ff0331`。
- T-03 已实现策略当前态模型与 MySQL 创建、按 ID 读回、团队/游戏/可用状态过滤；定向数据层测试通过。证据见 `evidence/T-03.md`。Cloud commit `e62ff58`。
- T-04 已实现按角色及团队/游戏授权、按已部署模板版本校验配置、创建/修改/复制/启停和事务内审计；定向测试通过。证据见 `evidence/T-04.md`。Cloud commit `056c0d6`。
- T-05 已注册六条策略路由并接 Service 层；错误映射为合同具名错误，成功走统一信封；旧版本端点保持 404。定向测试、合同⇄路由比对（6=6）和全仓构建通过。证据见 `evidence/T-05.md`。Cloud commit `bc9fa91`。
- T-06 已交付 Cloud Web/Desktop 共用合成策略页面（列表、创建、编辑、复制、启停；普通运营只读）与 compose API 客户端；两端路由指向同一页面，CHG079 占位守卫改写为 parity 守卫。补齐客户端缺失的 `listGames`。vitest 510 例全绿，两端构建通过。证据见 `evidence/T-06.md`。Cloud commit `58bb32a`。
- T-07 真实 MySQL/API 验收完成：模板幂等重发布（id=3 不变）；admin 创建/修改/复制/停用读回一致且绑定版本不漂移；schema 外参数、非法区间、非法状态均 400 且零写入；临时账号实测普通运营只读+越权 403/404、高级运营范围内可写+越团队 403；页面路由 200。验收数据与临时账号/团队已精确清零，模板未动。证据见 `evidence/T-07.md`。基于 Cloud `58bb32a`，无代码改动。

## Current

T-08：全量回归、证据和交付收口。

## Next

T-08 全量回归（Go、Web、两端构建）后收口；用户要求本 CHG 全部完成后统一走查（GUI 级页面走查在此时补）。

## Blockers

None.

## Recent verification

- CHG080 真实 FFmpeg/Garage 验收已归档；Cloud 工作树开始本 CHG 前干净。
- 四份 Cloud 合同 YAML 使用 `gopkg.in/yaml.v3` 解析通过。
- `go test ./cmd/compose-template-publish ./internal/modules/production/executor ./internal/modules/production/repository -count=1` 通过；真实 MySQL 两次发布同一模板 ID。
- `go test ./internal/modules/production/model ./internal/modules/production/repository -count=1` 与 `git diff --check` 通过。
- `go test ./internal/modules/production/repository ./internal/modules/production/service -count=1` 通过。
- `go test ./internal/modules/production/... -count=1` 与 `go build ./...` 通过；合同 YAML 与注册路由 6 条精确相等。
