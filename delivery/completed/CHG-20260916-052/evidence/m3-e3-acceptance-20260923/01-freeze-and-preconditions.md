# 阶段 G0-G3：静态冻结与前置门禁

> 由 `tools/render-evidence.py` 从 `run-manifest.json` 渲染，每一步可回溯。
> 判定分布：INFO=7，PASS=10。

| 步骤 | 判定 | 请求 | 期望 | 实际 |
| --- | --- | --- | --- | --- |
| G0.1 | PASS | git rev-parse/status | Cloud 干净；Workspace 只允许本轮验收产物 | cloud=aaf66c51bab6 clean=True \| workspace=4f44ffd16016 dirty_entries=2 非本轮产物=0 |
| G0.2 | INFO | toolchain versions | 记录工具链版本 | {"go": "go version go1.26.5 darwin/arm64", "node": "v26.8.1", "mysql": "mysql  Ver 8.4.10 for macos26.4 on arm64 (Homebrew)", "python": "Python 3.14.6"} |
| G0.3 | INFO | lsof -iTCP:18080 | 18080 上只有本轮启动的进程 | COMMAND     PID   USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME wt-media- 27020 aqiuye    8u  IPv4 0xf257ef499c305321      0t0  TCP 127.0.0.1:18080 (LISTEN) wt-media- 27020 aqiuye    9u  IPv4 0xf257ef499c305321      0t0  TCP 127.0.0.1:18080 (LISTEN) |
| G0.4 | INFO | config/credentials/*.toml 元数据 | 只记键名与字节长度，不记值 | [{"file": "config/credentials/agent.toml", "bytes": 16, "git_tracked": true, "keys": [["auth_token", 0]]}, {"file": "config/credentials/douyin.toml", "bytes": 7078, "git_tracked": true, "keys": [["api_key", 35], ["cookie", 6975], ["headers.User-Agent", 16]]}] |
| G0.5 | INFO | 端口占用表 | 记录 5173/5174/8765/8899 现状 | node        112 aqiuye   21u  IPv4 0x90fd640854a62a2b      0t0  TCP 127.0.0.1:5173 (LISTEN) node       3121 aqiuye   21u  IPv4 0x50acdda8afe13794      0t0  TCP 127.0.0.1:5174 (LISTEN) python3.1 15233 aqiuye    3u  IPv4 0xa558e89d3e4f970b      0t0  TCP 127.0.0.1:8765 (LISTEN) wt-media- 27020 aqiuye    8u  IPv4 0xf257ef499c305321      0t0  TCP 127.0.0.1:18080 (LISTEN) wt-media- 27020 aqiuye    9u  I |
| G1.1 | PASS | information_schema + schema_migrations | 表与迁移齐备 | tables=26 migrations_total=39 tail=20260922_038_audit_fields@2026-09-22 13:48:19.689398; 20260922_037_user_nickname@2026-09-22 13:30:34.950405; 20260922_036_content_game_default@2026-09-22 12:27:14.521474 |
| G1.2 | PASS | users / operation_teams | admin 与至少一个运营组存在 | users=[['1', 'admin', 'admin', 'NULL', 'enabled'], ['2', 'senior01', 'senior_operator', '1', 'enabled'], ['3', 'operator01', 'operator', '1', 'enabled']] teams=[['1', '默认运营组'], ['2', 'M3验收-隔离组-20260923'], ['3', 'm3acc0923-自动转素材探测-158733'], ['4', 'm3acc0923-自动转素材探测-188327'], ['5', 'm3acc0923-转素材-关闭-196427'], ['6', 'm3acc0923-转素材-AND命中与未命中-200496'], ['7', 'm3acc0923-转素材-OR非正阈值被跳过-204573'], ['8', 'm3 |
| G1.3 | INFO | 基线计数 | 冻结既有行数 | {"captured_at": "2026-09-22T21:51:00Z", "tables": 26, "discovery_strategies": {"count": 17, "max_id": 18}, "crawl_tasks": {"count": 41, "max_id": 63, "pending": 0}, "source_contents": {"count": 319, "max_id": 434}, "materials": {"count": 87, "max_id": 87}, "users": 3, "operation_teams": 12} |
| G1.4 | PASS | TCP api.itfaba.com:443 | 上游可达 | reachable |
| G2.1 | PASS | scripts/start.sh -> cmd/server | 只有 API Server 在跑 | pid=27020 lstart=Wed Sep 23 05:50:16 2026 |
| G2.2 | INFO | 仅 API Server 观察窗口 | pending/running 不变 | scheduler/worker 已在运行，跳过（pid=[23308]） |
| G2.3 | PASS | 启动 cmd/discovery-scheduler 与 cmd/discovery-worker | 两个独立进程，无 flag，间隔取 config/scheduler/scheduler.toml | {"discovery-scheduler": {"pid": 27302, "lstart": "Wed Sep 23 05:51:01 2026"}, "discovery-worker": {"pid": 23308, "lstart": "Wed Sep 23 05:17:25 2026"}} |
| G3.1-admin | PASS | POST /auth/login admin | errcode=0 且能读到身份 | HTTP 200 errcode=0 message=success |
| G3.2-admin | PASS | GET /auth/me | 会话可读回身份 | {"id": 1, "username": "admin", "role": "admin", "status": "enabled", "team_id": null, "team_name": "", "game_ids": null} |
| G3.1-operator | PASS | POST /auth/login senior01 | errcode=0 且能读到身份 | HTTP 200 errcode=0 message=success |
| G3.2-operator | PASS | GET /auth/me | 会话可读回身份 | {"id": 2, "username": "senior01", "role": "senior_operator", "status": "enabled", "team_id": 1, "team_name": "默认运营组", "game_ids": ["other"]} |
| G3.4 | INFO | 隔离组 id | 用于跨组权限负例 | isolated_team_id=2 operator_team_id=1 |

## 备注

- **G0.1**：Cloud 未提交改动=''；Workspace 越界改动=[]；本轮产物=['?? delivery/active/CHG-20260916-052/evidence/m3-e3-acceptance-20260923/', '?? scripts/verify_m3_acceptance.py']
- **G0.4**：安全问题登记项：见 B6/D-安全-1
- **G1.2**：需要 admin 才能登录；不通过则 STOP S3
- **G1.3**：后续断言一律按「本次新建 id」过滤，不与既有 109 来源混算
- **G1.4**：不可达则 G5 起进入 EXTERNAL-BLOCKED 分支
- **G3.1-admin**：登录成功即建立会话 cookie
- **G3.1-operator**：登录成功即建立会话 cookie
- **G3.4**：复用已建的隔离组
