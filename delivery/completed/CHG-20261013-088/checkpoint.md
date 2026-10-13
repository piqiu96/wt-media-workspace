# CHG-20261013-088 Checkpoint

## Completed

- T-01：Cloud 合同与查询——`created_from`/`created_before`（RFC3339、结束排他）在权限过滤后、`LIMIT 200` 前生效；成片 `source` 按素材 ID 精确或名称包含匹配；详情投影 `started_at`/`finished_at`。定向 Go 测试与 OpenAPI 模式比对通过。证据 `evidence/T-01.md`。
- T-02：两页筛选接线、预览失败保留详情（`feedback.toast.error`）、任务详情补开始／结束时间与执行次数；compose 定向 Vitest 22/22，Cloud/Desktop 双构建通过。证据 `evidence/T-02.md`。
- T-03：Web 全量 553/553、`go build ./...`、diff 范围核对通过；M4-G 服务端缺口结论登记到里程碑。证据 `evidence/T-03.md`。
- Cloud 已独立提交：`b5cdffc`。验收结论见 `change.md` §验收结论，四项全 PASS。

## Current

无——CHG088 实施与验证已完成，准备归档。

## Next

归档 CHG088；后续按里程碑推进 M4-G（服务端执行详情与人工重试能力，独立 CHG）与 M4-H（真实数据 UI 走查与用户签收）。

## Blockers

None.

## Recent verification

- `go -C wt-media-cloud test ./internal/modules/production/...` 全部 `ok`（含新增边界与 SQL 断言用例）。
- `npm --prefix wt-media-cloud/web run test -- src/modules/compose` 22/22；Web 全量 62 文件 553/553 PASS。
- `npm run build:cloud`、`build:desktop`、`go build ./...` 均 PASS；`gofmt -l`（本 CHG 文件）与 `git diff --check` 干净。
- 本机 GUI 走查不可行（见既往结论），真实 UI 签收按 M4-H 由用户执行。
