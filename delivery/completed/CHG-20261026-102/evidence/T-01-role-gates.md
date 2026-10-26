# T-01：服务端角色与团队门禁

## 环境

- Cloud 检出 `wt-media-cloud`，分支 `chg/CHG-20261026-102`，HEAD `1f54e42`（T-01～T-04 已提交）。
- `bin/control.sh start` 启动 API（pid 93232），`GET /healthz` → 200。
- `go run ./cmd/migrate` → `1 applied, 75 total`；本次应用 `20261026_073_ensure_other_game`。
- 真实账号（密码不记录）：admin(id 1, admin)、senior01(id 2, senior_operator, team 1)、operator01(id 3, operator, team 1, games hy+sjz)。

## 拒绝矩阵：operator01 真实请求

所有请求由 operator01 的 Web 会话发出；期望均为 `errcode=11003`（403 没有权限访问该团队资源）。

| 入口 | 请求 | 实际 | 结果 |
| --- | --- | --- | --- |
| 创建策略 | `POST /api/v1/discovery-strategies` | HTTP 403，11003 | PASS |
| 编辑策略 | `PUT /api/v1/discovery-strategies/1` | 11003 | PASS |
| 启停策略 | `POST /api/v1/discovery-strategies/1/status` | 11003 | PASS |
| 删除策略 | `DELETE /api/v1/discovery-strategies/1` | 11003 | PASS |
| 执行策略 | `POST /api/v1/discovery-strategies/1/run` | 11003 | PASS |
| 重试任务 | `POST /api/v1/crawl-tasks/1/retry-failed` | 11003 | PASS |
| 确认任务结果 | `POST /api/v1/crawl-tasks/1/confirm` | 11003 | PASS |

拒绝前后数据库计数（直接 SQL，不经 API 投影）：

| 表 | 拒绝前 | 拒绝后 |
| --- | --- | --- |
| `discovery_strategies`（team 1） | 4 | 4 |
| `crawl_tasks` | 73 | 73 |
| `source_contents` | 664 | 664 |

## 正向路径

| 场景 | 实际 | 结果 |
| --- | --- | --- |
| senior01 创建策略，不带 team_id / game_id | team_id=1，game_id=`other` | PASS |
| senior01 指定 team_id=2 创建 | 11003 | PASS |
| senior01 列表指定 team_id=2 | 11003 | PASS |
| admin 创建策略不带 team_id | HTTP 400，errcode 14009「请选择目标团队」 | PASS |
| admin 指定 team_id=2、game_id=hy 创建 | team_id=2，game_id=hy | PASS |
| admin 列表 team_id=2 | 13 行，与 `SELECT COUNT(*) ... WHERE team_id=2` 一致 | PASS |
| operator01 忽略/恢复内容 906 | `pending → ignored → pending`；每次 API 后直接读库一致 | PASS |
| 清理本次创建的策略 | senior/admin 删除均 HTTP 200；team 1 策略数回到 4 | PASS |

## 自动门禁

- T-01 提交 `e014cfb` 的独立快照（`git archive` 到临时目录）运行 `go test ./internal/modules/contentpool/...` → `model` / `repository` / `service` 全部 ok，证明该提交本身可构建、可测。
- 最终 HEAD 全量 `go test ./... -count=1` → 72 包 ok、0 FAIL、11 个无测试文件包。

## 说明

- 任务列表里的「执行策略」是 `POST /discovery-strategies/:id/run`；人工 ID／链接／关键词发现走独立入口，未受角色门禁影响。
- 调度器内部创建任务使用合成 admin 身份（`RunDue`），角色门禁不会阻断定时调度。
