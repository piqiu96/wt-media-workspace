# T-04：策略负责人校验与可见性

原始响应见 `T-04-strategy-operator.json`。

## 可见性

| 角色 | 请求 | 实际 | 结果 |
| --- | --- | --- | --- |
| operator01 | `GET /compose-strategies` | 仅 `[44]`，负责人 pika；历史策略不可见 | PASS |
| operator01 | `GET /compose-strategies/45` | `15212 compose_strategy_not_found` | PASS |
| operator01 | `GET /compose-strategies/44` | 成功，`operator_id=3`、`operator_name=pika` | PASS |
| chg103senior | `GET /compose-strategies` | 9 条团队策略，含 44（pika）、45（CHG103高级）与 7 条历史未记录 | PASS |
| chg103admin | `GET /compose-strategies` | 9 条，跨团队默认可见 | PASS |

## 创建与编辑门禁

| 场景 | 请求 | 实际 | 结果 |
| --- | --- | --- | --- |
| 创建时用管理员账号充负责人 | `POST /compose-strategies`，`operator_id=10`（admin，非运营） | `15210 compose_strategy_invalid`：“operator must be an enabled team operator responsible for the game” | PASS |
| 拒绝无写入 | 同上，拒绝前后 `compose_strategies` 行数 | 9 → 9 | PASS |
| 启用策略改为非法负责人 | `PUT /compose-strategies/45`，`operator_id=10` | `15210`；随后读回负责人仍为 9 | PASS |
| 合法改派 | 同接口 `operator_id=3` | `errcode 0`，读回 pika；任务／成片历史快照不变（见 T-05） | PASS |

- 策略创建必须提交 `operator_id`；负责人必须启用、同团队、角色为运营且负责策略游戏；复制、启用、立即执行共用同一校验函数 `resolveComposeOperator`。
- 单测覆盖创建／更新／复制／启停／执行门禁，位于 `wt-media-cloud/internal/modules/production/service/strategy_test.go`；生产模块包测试全绿（T-02）。
