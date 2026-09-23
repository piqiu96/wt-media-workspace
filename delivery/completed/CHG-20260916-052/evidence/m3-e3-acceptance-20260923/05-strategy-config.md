# 阶段 5.5：挖掘策略配置矩阵

> 由 `tools/render-evidence.py` 从 `run-manifest.json` 渲染，每一步可回溯。
> 判定分布：FAIL=2，PASS=11。

| 步骤 | 判定 | 请求 | 期望 | 实际 |
| --- | --- | --- | --- | --- |
| 5.5.1 | PASS | POST /discovery-strategies {"platform": "douyin", "strategy_type": "keyword", "game_id": "other", "status": "disabled", "name": "m3acc0923-合法-keyword-手动-061323", "config": {"keyword": "王者荣耀"}, "schedule": "manual"} | 201，合法 keyword + manual 策略可创建 | HTTP 201 errcode=0 message=success |
| 5.5.2 | PASS | POST /discovery-strategies {"platform": "douyin", "strategy_type": "keyword", "game_id": "other", "status": "disabled", "name": "m3acc0923-非正阈值-061323", "config": {"keyword": "王者荣耀", "auto_material": true, "material_rule": "AND | 400 / 14006：开启自动转素材但两个阈值都非正 | HTTP 400 errcode=14006 message=挖掘参数无效 |
| 5.5.3 | PASS | POST /discovery-strategies {"platform": "douyin", "strategy_type": "keyword", "game_id": "other", "status": "disabled", "name": "m3acc0923-非法规则-061323", "config": {"keyword": "王者荣耀", "auto_material": true, "material_rule": "XOR | 400 / 14006：material_rule 非 AND/OR 必须拒绝 | HTTP 400 errcode=14006 message=挖掘参数无效 |
| 5.5.4 | PASS | POST /discovery-strategies {"platform": "douyin", "strategy_type": "keyword", "game_id": "other", "status": "disabled", "name": "m3acc0923-空关键词-061323", "config": {"keyword": ""}} | 400 / 14006：keyword 为空 | HTTP 400 errcode=14006 message=挖掘参数无效 |
| 5.5.5 | PASS | POST /discovery-strategies {"platform": "bilibili", "strategy_type": "keyword", "game_id": "other", "status": "disabled", "name": "m3acc0923-非抖音-061323", "config": {"keyword": "王者荣耀"}} | 400 / 14006：本期只支持 douyin | HTTP 400 errcode=14006 message=挖掘参数无效 |
| 5.5.6 | PASS | POST /discovery-strategies {"platform": "douyin", "strategy_type": "author", "game_id": "other", "status": "disabled", "name": "m3acc0923-author枚举保留-061323", "config": {"author": "王者荣耀"}} | 201：author 取值保留（实现未删除该枚举） | HTTP 201 errcode=0 message=success |
| 5.5.7 | PASS | POST /discovery-strategies/999999/run | 404 / 14005：策略不存在 | HTTP 404 errcode=14005 message=挖掘策略不存在 |
| 5.5.8 | FAIL | POST /discovery-strategies 同名策略（隔离组内） | 预期 409 / 14007「策略名称已存在」 | HTTP 500 errcode=50000 message=挖掘服务内部错误 |
| 5.5.9 | FAIL | POST /discovery-strategies schedule='garbage' | 预期 400 / 14006：schedule 应有服务端格式校验 | HTTP 201 errcode=0 schedule=garbage |
| 5.5.10 | PASS | POST /discovery-strategies {"platform": "douyin", "strategy_type": "keyword", "game_id": "other", "status": "disabled", "name": "m3acc0923-隔离组策略-061323", "config": {"keyword": "王者荣耀"}} | 201：admin 可跨组建策略 | HTTP 201 errcode=0 message=success |
| 5.5.11 | PASS | POST /discovery-strategies/<id>/status enabled | 200：启用成功 | HTTP 200 errcode=0 message=success |
| 5.5.12 | PASS | 启用后观察 60s | 启用不触发立即执行（schedule=manual） | crawl_tasks(strategy=24) 0 -> 0 |
| 5.5.13 | PASS | POST /discovery-strategies/<disabled>/run | 400 / 14006：停用策略不能创建任务 | HTTP 400 errcode=14006 message=挖掘参数无效 |

## 备注

- **5.5.8**：D1：仓储层 errStrategyDuplicate 未翻译为 service.ErrStrategyDuplicate
- **5.5.9**：D2：createStrategy/updateStrategy 只把空值兜底为 manual，不校验格式
