# 阶段 5：内容池入口与导入

> 由 `tools/render-evidence.py` 从 `run-manifest.json` 渲染，每一步可回溯。
> 判定分布：FAIL=2，PASS=15。

| 步骤 | 判定 | 请求 | 期望 | 实际 |
| --- | --- | --- | --- | --- |
| 5.1 | PASS | POST /content-pool/search keyword（同步查询） | errcode=0、返回结果、不创建 crawl_task | errcode=0 items=5 crawl_tasks 41->41 |
| 5.2 | PASS | POST /content-pool/search query=纯ID+video链接（中英文分隔符） | errcode=0 且 ID 与 URL 两种写法都能解析出内容 | errcode=0 items=2 attempts=1 空返回=0 ids=['7688456561111231914', '7688444829000691685'] |
| 5.2b | FAIL | 同一真实 ID 连续 8 次 ID 发现 | 合法 ID 应稳定返回内置内容 | 空返回 2/8 次（errcode 均为 0） |
| 5.3 | PASS | POST /content-pool/search 空 query 与空 keyword | 400 / 14006 | HTTP 400 errcode=14006 message=挖掘参数无效 |
| 5.4 | PASS | POST /content-pool/search 101 个目标（上限 100） | 400 / 14006 | HTTP 400 errcode=14006 message=挖掘参数无效 |
| 5.5 | PASS | POST /content-pool/search 非抖音域 URL | 400 / 14006 | HTTP 400 errcode=14006 message=挖掘参数无效 |
| 5.6 | PASS | POST /content-pool/author-search（服务端硬禁用） | 400 / 14006「博主搜索接口维护中」 | HTTP 400 errcode=14006 message=博主搜索接口维护中 |
| 5.7 | PASS | POST /content-pool/import-results source_type=link | 400 / 14006：只接受 search\|author | HTTP 400 errcode=14006 message=挖掘参数无效 |
| 5.8 | PASS | POST /content-pool/import-results 空 items | 400 / 14006 | HTTP 400 errcode=14006 message=挖掘参数无效 |
| 5.9 | PASS | POST /content-pool/import-results 501 条（上限 100） | 400 / 14006 | HTTP 400 errcode=14006 message=挖掘参数无效 |
| 5.10 | PASS | 只搜索不提交 import-results | 未选择结果不写正式来源 | source_contents 319 -> 319 |
| 5.11 | PASS | POST /content-pool/import-results（选中 2 条，隔离组） | 每条都落成 imported 或 duplicate，无一 failed（重复运行时应全为 duplicate） | imported=1 duplicate=1 failed=0 source_ids=[436] |
| 5.12 | PASS | SQL 读回导入行 | 落库行与请求一致、source_type=search | [["436", "2", "douyin", "search", "pending", "24", "5"]] |
| 5.13 | PASS | POST /content-pool/import-results 重复提交同一批 | duplicate=2、imported=0 | imported=0 duplicate=2 |
| 5.14 | PASS | POST /content-pool/import-url（UI 已不调用的遗留路径） | 201，创建 manual_discovery_task 且 strategy_id 为空 | HTTP 201 task_id=64 task_type=manual_discovery_task crawl_tasks 41->42 |
| 5.15 | FAIL | GET /crawl-tasks/<import-url task>（沿用遗留入口） | Worker 领取并执行，产出 source_type='link' 的来源行 | 尝试 8 次，task_ids=[64, 65, 66, 67, 68, 69, 70, 71]，最后一次 stats={"scanned": 0, "found": 0, "added": 0, "duplicate": 0, "failed": 0, "auto_materialized": 0, "pending": 0}，link 行=[] |
| 5.15b | PASS | 统计「零产物却判成功」的任务数 | 链接导入没拿到任何内容时不应显示成功 | 0/8 次任务为 status=success 且 found=0（上游空返回被如实透传成成功） |

## 备注

- **5.2**：上游批量按 ID 接口间歇返回空集，见缺陷登记 D9
- **5.2b**：D9：上游 /batchDyVideo 以 result=1 + 空 data 间歇返回；Cloud 如实透传为「成功但无结果」，用户无任何错误提示
- **5.14**：该路径是 UI 唯一不再调用、却能产出 source_type='link' 的入口（缺陷 D6 背景）
- **5.15**：该入口 UI 已不调用；它是唯一能产出 source_type='link' 的真实路径（缺陷 D6）
- **5.15b**：D9 同族：上游空返回既不报错也不重试，任务与界面显示为成功
