# 阶段 11：残留登记与收尾

> 由 `tools/render-evidence.py` 从 `run-manifest.json` 渲染，每一步可回溯。
> 判定分布：INFO=2，PASS=8。

| 步骤 | 判定 | 请求 | 期望 | 实际 |
| --- | --- | --- | --- | --- |
| 11.1 | INFO | SQL operation_teams 本轮新建 | 登记（不删除） | 1 个：[["2", "M3验收-隔离组-20260923"]] |
| 11.2.discovery_strategies | PASS | SQL discovery_strategies 相对基线快照的增量 | 既有行逐项未被修改/删除，只登记新增 | 基线 3 行(max_id=3) → 现 29 行，新增 26：4,5,7,8,9,10,11,12,13,14,15,16 … |
| 11.2.crawl_tasks | PASS | SQL crawl_tasks 相对基线快照的增量 | 既有行逐项未被修改/删除，只登记新增 | 基线 11 行(max_id=33) → 现 62 行，新增 51：34,35,36,37,38,39,40,41,42,43,44,45 … |
| 11.2.source_contents | PASS | SQL source_contents 相对基线快照的增量 | 既有行逐项未被修改/删除，只登记新增 | 基线 109 行(max_id=165) → 现 478 行，新增 369：166,167,168,169,170,171,172,174,176,177,179,180 … |
| 11.2.materials | PASS | SQL materials 相对基线快照的增量 | 既有行逐项未被修改/删除，只登记新增 | 基线 26 行(max_id=26) → 现 146 行，新增 120：27,28,29,30,31,32,33,34,35,36,37,38 … |
| 11.3.discovery_strategies | PASS | SQL discovery_strategies 基线区间行数复核 | 基线区间内行数不变（既有 3 策略/11 任务/109 来源/26 素材未被删除） | id<=3 的行数=3，基线 count=3 |
| 11.3.crawl_tasks | PASS | SQL crawl_tasks 基线区间行数复核 | 基线区间内行数不变（既有 3 策略/11 任务/109 来源/26 素材未被删除） | id<=33 的行数=11，基线 count=11 |
| 11.3.source_contents | PASS | SQL source_contents 基线区间行数复核 | 基线区间内行数不变（既有 3 策略/11 任务/109 来源/26 素材未被删除） | id<=165 的行数=109，基线 count=109 |
| 11.3.materials | PASS | SQL materials 基线区间行数复核 | 基线区间内行数不变（既有 3 策略/11 任务/109 来源/26 素材未被删除） | id<=26 的行数=26，基线 count=26 |
| 11.4 | INFO | 停止 scheduler/worker/Vite/代理 + scripts/stop.sh | 进程退出、两端工作区干净 | 见 11-teardown 与 shell 收尾结果 |
