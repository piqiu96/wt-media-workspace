# T-03：团队运营目录 API

接口：`GET /api/v1/compose-operators?team_id=&game_id=`。原始响应摘录见 `T-03-operator-directory.json`。

| 角色 | 请求 | 期望 | 实际 | 结果 |
| --- | --- | --- | --- | --- |
| 普通运营 operator01 | `team_id=1&game_id=hy` | 拒绝 | HTTP 403，`15221 compose_operator_forbidden` | PASS |
| 高级运营 chg103senior | 不传团队 | 本团队全部可选负责人 | `errcode 0`：CHG103高级、pika、senior01 | PASS |
| 高级运营 | `team_id=2&game_id=hy` | 拒绝跨团队 | `15221 compose_operator_forbidden` | PASS |
| 管理员 chg103admin | 不传团队 | 必须显式指定目标团队 | `15220 compose_operator_invalid`，`team_id is required` | PASS |
| 管理员 | `team_id=1&game_id=hy` | 本团队且负责该游戏 | `errcode 0`：CHG103高级、pika；senior01 不在列表 | PASS |
| 管理员 | `team_id=1`（不按游戏） | 团队全部运营 | `errcode 0`：CHG103高级、pika、senior01 | PASS |
| 管理员 | `team_id=2` | 空目录，不越权读取其他团队用户 | `errcode 0`，`[]` | PASS |

- 游戏过滤是正向可区分的：senior01 属于团队 1，但不负责 `hy`，因此只在“团队全部”出现、在 `game_id=hy` 被排除。
- 目录只返回启用中的 `operator`／`senior_operator`；本 CHG 未改动身份模块 `GET /users` 的权限与合同。
- 单测在 `wt-media-cloud/internal/modules/production/service/operator_test.go`、`operator_handler_test.go`；`go test ./internal/modules/production/...` 全绿（T-02）。
