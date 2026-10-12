# CHG-20261012-081 Checkpoint

## Completed

- 已确认 CHG079 结构和 CHG080 执行器验收完成，`basic_cut` v1 当前仅支持切段。
- 已修正 PRD §5.5 首版参数示例，与已验证执行代码一致。
- T-01 策略 API、请求/响应 schema、错误及枚举合同已定义并通过 YAML 解析；证据见 `evidence/T-01.md`。Cloud commit `b334437`。
- T-02 已从执行器代码发布 `basic_cut` v1 到真实 MySQL；两次发布读回同一模板 ID 3、版本 1、状态 active，schema/执行器与代码一致。证据见 `evidence/T-02.md`。Cloud commit `6ff0331`。
- T-03 已实现策略当前态模型与 MySQL 创建、按 ID 读回、团队/游戏/可用状态过滤；定向数据层测试通过。证据见 `evidence/T-03.md`。Cloud commit `e62ff58`。

## Current

T-04：策略 Service 权限、校验、修改/复制/停用与审计。

## Next

依任务表推进 T-04～T-08。用户要求本 CHG 全部完成后统一走查。

## Blockers

None.

## Recent verification

- CHG080 真实 FFmpeg/Garage 验收已归档；Cloud 工作树开始本 CHG 前干净。
- 四份 Cloud 合同 YAML 使用 `gopkg.in/yaml.v3` 解析通过。
- `go test ./cmd/compose-template-publish ./internal/modules/production/executor ./internal/modules/production/repository -count=1` 通过；真实 MySQL 两次发布同一模板 ID。
- `go test ./internal/modules/production/model ./internal/modules/production/repository -count=1` 与 `git diff --check` 通过。
