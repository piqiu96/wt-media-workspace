# 阶段 8：五态、重试与确认

> 由 `tools/render-evidence.py` 从 `run-manifest.json` 渲染，每一步可回溯。
> 判定分布：INFO=1，NOT VERIFIED=1，PASS=8。
>
> **2026-09-23 更新：8.8 已由受控故障注入补验通过，本阶段 NOT VERIFIED 清零。**
> 补验不重渲染本表（本表如实记录冻结修订 `aaf66c5` 的当轮执行），
> 结论与证据见 `17-material-failed-injection.md` 与 `14-verdict.md` 第 6 项。

| 步骤 | 判定 | 请求 | 期望 | 实际 |
| --- | --- | --- | --- | --- |
| 8.1 | INFO | SQL crawl_tasks 状态分布 | 五态枚举在库中真实出现过 | [["success", "54"], ["partial_success", "2"], ["failed", "4"]] |
| 8.2 | PASS | POST /content-pool/import-url 真实数字 ID + 必然失败目标 | status=partial_success：processed>0 且 failed>0 | 尝试 1 次 task_id=83 status=partial_success stats={"scanned": 2, "found": 1, "added": 1, "duplicate": 0, "failed": 1, "auto_materialized": 0, "pending": 1} |
| 8.3 | PASS | partial_success 的判定式复核 | processed = added+duplicate+pending+auto_materialized > 0 且 failed > 0 | processed=2 failed=1 |
| 8.4 | PASS | POST /crawl-tasks/<success>/retry-failed | 400 / 14008：非失败/部分成功任务不可重试 | HTTP 400 errcode=14008 message=请选择可入池的搜索结果 |
| 8.5 | PASS | POST /crawl-tasks/83/retry-failed | 新建任务 parent_task_id 指向原任务，snapshot.retry_items 仅含失败项 | HTTP 200 new_task=84 parent_task_id=83 retry_items=[{"id": null, "processing_status": "failed"}] |
| 8.6 | PASS | SQL 原任务不可变 | 原任务终态与统计不被重试改写 | status=partial_success stats={"added": 1, "found": 1, "failed": 1, "pending": 1, "scanned": 2, "duplicate": 0, "auto_materialized": 0} |
| 8.7 | PASS | Worker 领取重试任务 | 重试任务只处理失败项：scanned == len(retry_items) | status=failed scanned=1 retry_items=1 stats={"scanned": 1, "found": 1, "added": 0, "duplicate": 0, "failed": 1, "auto_materialized": 0, "pending": 0} |
| 8.8 | NOT VERIFIED | material_failed 触发路径排查 | materialize 在 FOR UPDATE 下幂等，公开 API 无法制造失败 | 无法经公开 API 触发，且本轮不注入故障 |
| 8.9 | PASS | POST /crawl-tasks/<id>/confirm ids=[] | 400 / 14008：未选择不可确认 | HTTP 400 errcode=14008 message=请选择可入池的搜索结果 |
| 8.10 | PASS | 只搜索不确认 | 未选择结果不写正式来源 | source_contents 476 -> 476 |
