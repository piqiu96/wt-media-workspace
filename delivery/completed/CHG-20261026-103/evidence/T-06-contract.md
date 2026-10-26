# T-06：OpenAPI 与 contract-map 同步

| 项目 | 实际 |
| --- | --- |
| Cloud 合同 | `wt-media-cloud/contracts/cloud-api/v1/content-production.openapi.yaml`，`version: 2026.10.26.1`（提交 `54c0e87`） |
| 新端点 | `GET /api/v1/compose-operators`，参数 `team_id`、`game_id`，响应运营选项 |
| 新字段 | 策略／任务／成片均登记 `operator_id`（历史可为 null）与只读 `operator_name`；策略创建／更新登记 `operator_id` 必填／可改派；任务创建登记可选 `operator_id` 回显约束 |
| 新筛选 | 任务与成片列表登记 `team_id`、`operator_id`、`operator_scope`（`mine`／`team`／`all`） |
| Workspace 映射 | `config/contract-map.yaml` 的 `cloud_api.contract_revision` 同为 `2026.10.26.1`（工作区提交 `f00e4d7`） |

```text
$ grep -n "2026.10.26.1" config/contract-map.yaml
16:    # 2026.10.26.1：content-production 增加策略/任务/成片 operator_id 与负责人
18:    contract_revision: "2026.10.26.1"

$ grep -n "^  version:" wt-media-cloud/contracts/cloud-api/v1/content-production.openapi.yaml
4:  version: 2026.10.26.1
```

合同键、修订值与定义目录的一致性由 Workspace `verify_m0_config.py` 校验，收尾全量门禁读数见 T-09。
