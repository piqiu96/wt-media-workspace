# 阶段 9：权限与幂等

> 由 `tools/render-evidence.py` 从 `run-manifest.json` 渲染，每一步可回溯。
> 判定分布：PASS=11。

| 步骤 | 判定 | 请求 | 期望 | 实际 |
| --- | --- | --- | --- | --- |
| 9.1 | PASS | POST /discovery-scheduler/run-due（senior_operator） | 403 / 11003 | HTTP 403 errcode=11003 message=没有权限执行调度 |
| 9.2 | PASS | GET /discovery-strategies（senior_operator） | 只返回本团队（team_id=1）策略 | team_ids=['1'] |
| 9.3 | PASS | POST /discovery-strategies/<隔离组策略>/status（senior_operator） | 403 / 11003 | HTTP 403 errcode=11003 message=没有权限访问该团队资源 |
| 9.4 | PASS | POST /discovery-strategies/<隔离组策略>/run（senior_operator） | 403 / 11003 | HTTP 403 errcode=11003 message=没有权限访问该团队资源 |
| 9.5 | PASS | GET /crawl-tasks（senior_operator） | 只返回 team_id=1 的任务 | team_ids=['1'] |
| 9.6 | PASS | GET /crawl-tasks（admin） | admin 可见多团队任务 | team_ids=['1', '10', '11', '13', '14', '15', '16', '17', '18', '19', '2', '20', '3', '4', '5', '6', '7', '8', '9'] |
| 9.7 | PASS | POST /content-pool/batch/status 501 个 id | 400 / 14002：批量上限 500 | HTTP 400 errcode=14002 message=内容参数无效 |
| 9.8 | PASS | 8 线程并发导入同一条目 | 库中只有 1 行，且最多 1 次 imported=1（唯一约束兜底） | imported=1 duplicate=7 库中行数=1 状态码=['200'] |
| 9.9 | PASS | 8 路并发对同一条目转素材 | 只生成 1 个 material，且全库无重复 source_content_id | material 行数=1 全库重复组=[] 并发 errocode=['0'] |
| 9.10 | PASS | POST /content-pool/<material_created>/status pending | 409 / 14003：已转素材不能恢复为待处理 | HTTP 409 errcode=14003 message=已转素材内容不能恢复为待处理 |
| 9.11 | PASS | 重复导入已忽略条目 | 自动发现不恢复 ignored（只有人工恢复才生效） | 重复导入 duplicate=1，库中状态=ignored |
