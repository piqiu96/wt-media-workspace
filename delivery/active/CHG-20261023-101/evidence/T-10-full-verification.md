# T-10 四仓全量验证与真实回归证据

日期：2026-10-23
CHG：CHG-20261023-101
分支：四仓均为 `chg/CHG-20261023-101`

## 范围

- 四仓全量测试：Cloud（Go + Web）、Agent（Python）、Desktop（Rust + 脚本套件）、Workspace（治理校验）。
- Cloud 068–071 迁移：scratch schema、开发库副本、开发库实跑，从含设备/节点/旧 session/旧任务的 fixture 起跑，读回列、索引、约束、回填与终结行。
- 真实环境回归：真实 Cloud、真实 BitBrowser（54345）、真实 Agent 进程、打包 Desktop；不依赖 Mock 判定结果。
- 断网上报：本机反向代理制造 `/report` 502，第二个 Agent 使用独立 SQLite，验证终态先落盘、重启先补报、不重跑。
- 超额验证：真实 `task-recovery` 扫描（Go 一次性程序，同 bootstrap 配置/数据库）。

## 四仓测试读数

| 仓 | 命令 | 读数 | 结果 |
| --- | --- | --- | --- |
| Cloud | `./scripts/test.sh` | Go 71 个包 `ok`；Web `77 passed (77)` 文件、`710 passed (710)` 用例；`control: 12 passed, 0 failed` | 退出 0 |
| Agent | `./scripts/test.sh` | `Ran 727 tests` → `OK`；`storage migration ok: 4 applied, 4 total` | 退出 0 |
| Desktop | `HTTPS_PROXY=http://127.0.0.1:7897 ./scripts/test.sh` | `536 passed; 0 failed; 6 ignored`；`control: 12 passed, 0 failed`；`release-versions tests: 20 passed, 0 failed`；`package-release-macos.test.sh` 无输出、以 `set -e` 运行 | 退出 0 |
| Workspace | `python3 scripts/docs/check.py`、`scripts/verify/verify_delivery_governance.py`、`verify_product_master_alignment.py`、`verify_m0_config.py`、`verify_skills.py` | 见文末「Workspace 治理校验」 | 退出 0 |

Web 用例由 Cloud 的 `npm test --prefix web` 在 `web/` 下落跑（vitest 不回到仓根）。

## 迁移实测（068–071）

迁移工具与开发库同源（`config/` + `migrations/`），四种起点：

| 起点 | 结果 |
| --- | --- |
| scratch schema（已应用到 067，含设备/节点/旧 session/旧任务 fixture） | 068–071 全部 `applied`，日志 `/tmp/wt-t10-mig/scratch-final.log` |
| 开发库副本（068 已应用） | 069–071 `migration ok: 3 applied, 4 total`，日志 `/tmp/wt-t10-mig/devcopy-post.log` |
| 开发库 | 069–071 `migration ok: 3 applied, 73 total`；068 于 2026-10-22 20:58 已应用（`schema_migrations` 读回） |
| fixture 二次实跑（幂等复核） | 068–071 `migration ok: 4 applied, 4 total`，日志 `/tmp/wt-t10-mig/fixture-post-final.log` |

fixture 起跑前的旧事实与迁移后读回（`probe-before.out` / `probe-after.out`）：

| 项目 | 迁移前 | 迁移后 |
| --- | --- | --- |
| 同用户有效 Desktop 行 | 用户 1 有 2 行 | `active_desktop_dup=0`；旧行 `invalidated_reason=superseded`；全部有效行 `expiry_days=30` |
| 三列 Profile 重复 | 0 | 索引 `uq_browser_profiles_user_main_bit (user_id,main_user_id,bit_profile_id)` 唯一；`idx_browser_profiles_user_main` 非唯一 |
| `tasks` 列 | 13 列，无 owner/attempt | 新增列全部读回；`attempt=1`、`attempt_id=legacy:<task_id>`、`last_report_at` 回填、`execution_timeout_seconds=300` |
| 无 owner 的非终态任务 | 3 行 | 有 payload 归属的回填 `user_id`（1/2）；无归属的 `t10-legacy-orphan` → `failed`、`EXECUTION_INTERRUPTED`、`retryable=1`、`recovery_action=retry`、`settled_by=legacy` |
| `tasks` 索引 | 全局 `uq_idempotency_key` | `uq_tasks_user_idempotency (user_id,idempotency_key)` 唯一；`idx_tasks_user_status_created`、`idx_tasks_status_last_report` 存在 |
| 设备/节点对象 | `users_with_device=1`、`local_agent_nodes=1`、`binding_tickets=1`、`presence=1`、`agent_nodes=1`、`transfer_assigned_node=2`、`sensitive_task_node=1`、`permit_node=1` | `remaining_dropped_tables=0`、`users_device_columns=0`、`sensitive_node_columns=0` |
| `file_transfer_tasks` | `assigned_node_id/assigned_device_id` 存在 | 列读回为 `claimed_by,attempt_id,...`，无 node/device 列；旧 running 行 `claimed_by=node-1` 原样保留为审计标签 |
| 旧主账号 Profile | — | 同一 bit id 在不同 main 下各自成行（100/101/102），旧行不删除、不迁移 |

- 070 在严格模式下会把历史 payload 里的非数字 id 与 `BIGINT` 比较，报 MySQL 1292 并中止整个迁移。开发库副本实际触发后，回填 join 增加 `REGEXP '^[0-9]+$'` + `CAST(... AS UNSIGNED)` 守卫；fixture 用非数字 legacy id 覆盖该分支。
- 071 的删除顺序按 FK 依赖先删子表/列再删父表，`user_device_binding`、`local_agent_node_device_scoped` 等历史迁移在同一 fixture 上重放通过。
- 非事务 DDL 在失败重跑时会撞重复列：开发库副本失败后用备份副本重建再跑，未在真实库上重试到一半。

## 真实环境回归（64 项检查）

环境：Cloud `127.0.0.1:8188`、打包 Desktop sidecar `8765`、Vite `5173/5174`、BitBrowser `127.0.0.1:54345`、独立 Agent `127.0.0.1:18766`（数据目录 `/tmp/wt-t10-run/agent-data`）。脚本 `/tmp/wt-t10-run/scenarios.py`，原始读数 `/tmp/wt-t10-run/results.json`、`scenarios.log`。

`SUMMARY total=64 passed=64 failed=0`。关键读数：

| 场景 | 实际 |
| --- | --- |
| 两个 Web 会话并存 | 有效 web session `8 -> 10`，两个会话 `/me` 均 200 |
| Desktop 冲突 | 409 `DESKTOP_LOGIN_CONFLICT`，`error.details.active_session_id` 为当前有效行 |
| 取消 | session 行数 `11->11`，旧 Desktop 行仍有效 |
| 错误的 `replace_session_id` | 再次 409 `DESKTOP_LOGIN_CONFLICT`，不静默接管 |
| 确认替换 | 旧行 `desktop_replaced`，新行唯一有效；旧 Desktop `/me` → 401 `AUTH_DESKTOP_REPLACED` |
| 旧 Agent Token 严格档 | claim → 401 `AUTH_DESKTOP_REPLACED` |
| 旧 Agent Token 上报档 | 已 claim 任务 report → 200，`settled_by=agent` |
| Token 与 session 同寿命 | `exp=1795334221`，`session_exp=1795334221` |
| 作用域隔离 | Agent Token 调用户 API → 403 `AGENT_SCOPE_FORBIDDEN`；session token 调 Agent API → 401 `AUTH_AGENT_TOKEN_INVALID` |
| 同行走重试 | retry 复用同 task 行；下一次 claim `attempt=2`；旧 attempt 上报 → 409 `STALE_ATTEMPT` |
| 已 claim 任务 Preflight | takeover 后仍 200（按 `attempt_id` 走上报档） |
| 真实首绑 | Agent 实读 main `2c9bc06191effa4e0191f9589996619f`，Cloud `status=bound` |
| 同主验证 | `bound_at` 不变，只刷新 `last_verified_at` |
| 临时不一致 | 409 `BIT_MAIN_USER_MISMATCH`，不自动重绑 |
| Web 展示 | 只返回 `2c9b****619f`（首 4 + `****` + 末 4，长度 > 8） |
| 真实扫描 | Agent 读 BitBrowser 40 个 Profile，Cloud 提交 `201`，确认后 admin 40 行、operator01 40 行、distinct bit id 40 |
| Preflight 失败码 | 他人 Profile 403 `PROFILE_ASSIGNED_TO_OTHER_USER`；未知 Profile 404 `PROFILE_NOT_FOUND`；main 不一致 409 `BIT_MAIN_USER_MISMATCH`；观测过期 409 `BIT_BROWSER_OFFLINE`；未知动作 400 `UNSUPPORTED_TASK_TYPE` |
| 切主账号 | 旧 main 下列表 0、DB 保留 40；切回后列表 40 |
| 真实 Agent 执行 | `t10-real-runner` `succeeded`、`attempt=1`、`settled_by=agent`；SQLite outbox 行 `t10-real-runner|attempt_612e7ab6fb08d02f8e51a105|1`，checkpoint 已清理 |
| 被替换 Desktop 的 Token 收尾 | 已 claim 任务仍 200 |

管理员列表语义已核对：不带筛选的 `GET /api/v1/browser-profiles` 会返回所有用户的行（管理员可见范围），SQL join 再按每个 owner 当前绑定的 main 过滤；`?user_id=1` 时才应用“自己 + 自己绑定 main”的双作用域。切换主账号期间该列表为 0、DB 行保留、切回恢复 40，属于设计行为，不是缺陷。

## 真实断网上报与重启补报

脚本 `/tmp/wt-t10-run/outbox_test.py`，代理 `/tmp/wt-t10-run/proxy.py`（18188 → 8188，标志文件存在时把 `/report` 答成 502）。第二个 Agent 使用独立数据目录 `/tmp/wt-t10-run/agent2-data`。

| 检查 | 实际 |
| --- | --- |
| 终态先落 SQLite | outbox 行 `status=succeeded`、`delivered=0`、`delivery_attempts=1`；checkpoint `report_pending=1` |
| Cloud 未收到终态 | task 仍 `leased`，`settled_by` 为空、`finished_at` 为空，attempt 与 outbox 一致 |
| 重启后先补报 | 重新交给 Agent 同一 Token 后，outbox `delivered=1`；Cloud `succeeded`、`settled_by=agent`、同一 attempt |
| 不重跑 | 该 task 只有 1 行 outbox，Cloud `attempt` 仍为 1 |
| 收口 | 投递后 `mark_delivered` 清理 checkpoint（行不存在即已收口） |

`SUMMARY total=17 passed=17 failed=0`（`/tmp/wt-t10-run/outbox-results.json`）。

### 首次运行暴露的产品缺陷（已修复）

第一次运行只有 `13/17`：Cloud 一直停在 `leased`，但 Agent 把任务记成了 `failed/executor_error`。原因不是执行器，而是传输层分类：

- 代理返回的 502 body 没有 Cloud 信封（无 `errcode`/`data`），`_expect_data` 抛 `ValueError`；
- `DurableTaskReporter._report_progress` 只捕获 `CloudError`/`CloudUnavailableError`，`ValueError` 逃到 `TaskRunner`，被记成 executor 异常；
- 于是一次进度上报失败把正常执行写成了 `executor_error` 终态，并在恢复后上报给 Cloud。

修复：`_expect_data` 把“缺 `data`”归为 `CloudUnavailableError`（与“应答不是 Cloud 信封”同一类），进度上报按设计只记日志。回归用例：

- `test_cloud_agent_client.FailureTest.test_missing_data_is_a_transport_failure`（原用例断言 `ValueError`，随之更新）；
- `test_runner_outbox.RunnerOutboxTestCase.test_a_gateway_error_on_a_progress_report_does_not_fail_the_task`：非信封 502 下 `running` 上报不抛异常，终态仍是 `succeeded`。

修复后重跑 `16/17`；最后一项失败是脚本把“投递后 checkpoint 被删除”误判为未清 `report_pending`，改为接受行不存在后 `17/17`。两次失败都保留了真实读数，未用重跑覆盖。

## 真实 task-recovery 扫描

开发环境只启动 `discovery-worker`/`compose-worker`，不起 `discovery-scheduler`；`task-recovery` 只在该进程注册。用一次性 Go 程序 `wt-media-cloud/.cache/t10-recovery/main.go` 调用 `jobs.RunTaskRecovery`（同一 `bootstrap.InitializeMigration` 配置与数据库），输出 `task-recovery ok`。

| task | 修复前 | 扫描后 |
| --- | --- | --- |
| `t10-real-timeout-noside`（noop，`external_side_effect=0`，`last_report_at` 10 分钟前） | running | `failed`、`EXECUTION_INTERRUPTED`、`retryable=1`、`retry`、`settled_by=timeout` |
| `t10-real-timeout-side`（cookie_write，`external_side_effect=1`） | running | `failed`、`RESULT_UNKNOWN`、`retryable=0`、`check_platform_state`、`settled_by=timeout` |

两行 `finished_at` 均为 `2026-10-23 15:57:15`。当前开发环境没有真实发布/互动任务，`external_side_effect=1` 分支用真实 `tasks` 行验证，不是发布执行器。

## 密钥泄漏扫描

脚本 S7 扫描 Cloud `app.log`、`app.log.wf`、`access.log`、`access.log.wf`、`external.log` 与 Agent `agent.stdout.log`：

- 阳性对照：`module=` 在 `app.log` 命中 694 次、`access.log` 命中 492820 次、Agent 日志 2 次；`app.log.wf` 513 次。证明扫描本身不是空转。
- 6 个 token（2 个 Web session、3 个 Desktop session、3 个 Agent Token 中的 D1/AT1/D2/AT2/D3/AT3）在每个文件中命中均为 0。
- 覆盖边界：`outbox_test.py` 为验证补报临时换发的 Token 只存在于进程内存，用完即丢弃，未纳入这次字符串扫描；对应路径的“不落盘”由 Agent Token 存储实现（内存对象）与本地 API 回读测试覆盖。

## 打包 Desktop

- `bin/control.sh start` 构建并校验：`Desktop assets: PASS (origin http://127.0.0.1:8188 from the packaged config)`、`Desktop dev server: PASS`、`DMG: PASS`、`Login smoke: PASS user=admin`（`/tmp/wt-t10-control-start.log`）。
- DMG 已挂载到 `/Users/aqiuye/Develop/workspace/wt-media/.local/m2b/dmg-mount` 并启动 `起飞.app`，sidecar 占用 `8765`。
- 本机不能程序化驱动或截取 GUI（JXA/AppleScript 不可用），登录、绑定、Preflight、任务链路的判定都来自 API/DB/日志读回；逐屏视觉验收留给用户。

## 已知偏差与未覆盖

- 第二台物理 Desktop 不可得：Desktop 冲突/替换用真实 Tauri Origin（`http://tauri.localhost`）协议请求模拟，不是第二台机器。
- GUI 视觉与交互逐屏未由自动化确认（工具限制），artifact/日志/API 已读回。
- 发布/互动业务仍为 ComingSoon，相关 Preflight 只有 evaluator + 合成/真实事实组合，没有真实发布任务。
- 开发环境不启动 `discovery-scheduler`，超时扫描用一次性程序调用同一 job；未验证常驻调度器的 tick 间隔。
- 真实下载的双机领取、旧 Agent 被抢占后新 Agent 接手没有第二台机器可测；由 Agent Token + 用户范围 claim 的单测覆盖。
- 运行 `./scripts/test.sh` 期间 Cloud 工作树存在与本 CHG 无关的 `internal/modules/production/*` 纯 gofmt 差异（同一秒批量改写，非本 CHG 编辑）；未纳入提交，也未还原，留给工作树所有者处理。
- 第二个系统用户（operator01）的密码未知，真实回归只读其数据，不做登录/改名等写入。

## 环境清理状态（交接）

- 独立 Agent（18766/18767）、代理（18188）均已停止；两份临时数据目录保留在 `/tmp/wt-t10-run/` 供复核。
- 验证期间使用的 Cloud 开发服务（pid 35950，15:49 启动的 go-build 临时二进制）不在 `bin/control.sh` 的 PID 跟踪内；交接前已停止，`8188` 无监听。需要时用 `bin/control.sh start` 重启受管实例。
- 打包 Desktop 已退出：shell 与两个 sidecar（38880/38911/38913）均已终止，`8765` 无监听；DMG 已 `hdiutil detach`，`/Users/aqiuye/Develop/workspace/wt-media/.local/m2b/dmg-mount` 不再挂载。DMG 文件仍在 `target/release/bundle/dmg/`，用户可自行挂载做视觉验收。
- 开发库夹具已清理并读回：`t10-real-%` 任务 0、admin `browser_profiles` 0、admin `profile_sync_scans` 0（含 80 行候选）、`users.bit_main_user_id=NULL`、admin 有效 Desktop session 0。operator01 的 40 个 Profile 未动。
- 保留：admin 的 10 个有效 Web session 由测试登录产生，但无法与用户自己的开发浏览器会话区分，未批量失效；它们按 30 天过期，不影响 Desktop/Agent 边界。

## Workspace 治理校验

使用带 PyYAML 的 venv（`/tmp/wt-verify-venv/bin/python`）：

| 命令 | 读数 |
| --- | --- |
| `python3 scripts/docs/check.py` | `docs governance ok (15 indexes)` |
| `scripts/verify/verify_delivery_governance.py` | `Delivery governance verification ok. Active CHGs: CHG-20261015-098, CHG-20261023-101` |
| `scripts/verify/verify_product_master_alignment.py` | `Product and Master Plan alignment verification ok` |
| `scripts/verify/verify_m0_config.py` | `Workspace config verification ok` |
| `scripts/verify/verify_skills.py` | `verified 10 skill source files` |
| `scripts/verify/verify_m2_acceptance.py` | `M2 static cross-repository acceptance matrix ok`（脚本提示真实 MySQL/BitBrowser 证据需另行记录，即本文件与 T-04/T-06） |

均退出 0。
