# T-09 Contract 与正式文档回写证据

日期：2026-10-23
CHG：CHG-20261023-101
仓库与提交：

| 仓库 | 分支 | 提交 |
| --- | --- | --- |
| `wt-media-cloud` | `chg/CHG-20261023-101` | `3f3b054 docs(contracts): publish the session-bound agent runtime contracts` |
| `wt-media-agent` | `chg/CHG-20261023-101` | `6b67b50 docs(contracts): publish the agent token and BitBrowser bind surface` |
| `wt-media-desktop` | `chg/CHG-20261023-101` | `79e9086 chore(contracts): pin the 2026.10.23.1 contract revision` |
| `wt-media-workspace` | `chg/CHG-20261023-101` | `41f3ed8 docs: write the session-bound runtime facts back into formal docs` |

## Contract 回写

全部正式定义统一到 revision `2026.10.23.1`。

- Cloud：`cloud-api` 的登录冲突/确认替换与 `force-logout`；`cloud-agent-api` 新增 `agent-token`、`execution-preflight`，删除 `runtime-binding`、`registration-heartbeat`；`task-lease`/`task-report` 改为 Bearer Agent Token + `attempt_id` + activity；`sensitive-profile-guard` 的两档鉴权与纯互斥 permit；`task-schemas` 的 10 个任务类型、执行超时与外部副作用默认值；`business-schemas`/`business-enums` 的 session、双作用域和失效原因；`cloud-error-codes` 新增 `execution.yaml` 并重写 identity/agent-runtime/browser-profile/profile-guard。
- Agent：`local-agent-api` 声明 22 个实际实现的操作（含 `POST /api/v1/agent-token`、BitBrowser bind、sensitive preflight/finish、profile CRUD、cookie-read），删除旧 `/bind` 描述；`local-error-codes` 增加 `agent_token` 禁写字段；`REQUIRED_CONTRACT_REVISION` 与 Agent 版本 `0.3.0` 对齐。
- Desktop：`contracts.lock.json` 顶层 `desktop-single-login-20261023.1`，`cloud_agent_api`/`task_schemas`/`local_agent_api` 均锁 `v1@2026.10.23.1`；`agent-compat.json` 对应 Agent `0.3.0`。
- Workspace：`config/contract-map.yaml` 全部 revision 与活源一致；`docs/contracts/contract-map.md` 更新任务定义版本并记录本批修订。

## 正式文档回写

| 文档 | 修改 |
| --- | --- |
| `docs/product/prd/详细文档/第三章_用户与账号管理.md` | §3.2.3 停用即失效；§3.2.4 改为 Web 多会话 + Desktop 单有效会话/冲突确认；§3.2.7 删除设备绑定与换绑，改为个人信息 + BitBrowser 绑定与执行环境；§3.4.2 双作用域；§3.4.3 首绑/重绑/管理员解绑、无手工 `main_user_id`；§3.4.4 统一预检与越界错误码；§3.7.2–3.7.4 异常、日志与验收改为新语义 |
| `docs/product/prd/详细文档/第二章_系统架构.md` | §2.4.4 任务领取记录用户/attempt/活动时间；§2.4.5 超时收敛；§2.4.6 Agent 本地状态去掉设备与心跳；§2.5.2/2.5.5/2.5.7 Agent Token 与活动上报；§2.7.5/2.7.6 attempt 与领取关系；§2.8.4 下载事实改为请求用户与领取审计 |
| `docs/product/prd/详细文档/第五章_素材生产.md` | §5.9.10 云端不再保存目标节点 |
| `docs/product/prd/社媒运营平台_产品需求说明书_V1.md` | Agent 职责由注册/心跳改为凭证签发与活动上报 |
| `delivery/milestones/M2-account-runtime.md` | §6 M2-F 删除设备绑定完成标准与旧实施记录，改为 session-only、Agent Token、双作用域、Preflight、Task 恢复与 outbox 的闭环定义，引用 CHG-101 与 ADR-0022 |
| `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md` | §2.7 会话替换与两档 Agent Token、超时收敛；§2.8 并发；§4.7 Task 用户/attempt 字段；§4.8 `task-recovery`；§5.6 本地 API 凭证；§5.7 outbox 顺序；§8.2 新增第 26–29 条禁止项 |
| `docs/engineering/architecture/社媒运营平台模块分界分层和通信规约.md` | §12.1 统一 Preflight 与 Agent Token；§13 换取凭证、领取/读取、上报档与 attempt、结果先落盘再上报、完整时序；§19 API 来源路径与认证；§20 新增第 11–13 条禁止项 |
| `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md` | 下载任务事实改为请求用户与领取审计 |
| `docs/decisions/README.md`、`0018`、`0019`、`0003` | 已有 ADR-0022 取代指针（T-01 完成，本次核对无遗漏） |

## 治理校验读数

命令均使用带 PyYAML 的 venv：`/tmp/wt-verify-venv/bin/python -B`。

| 校验 | 结果 |
| --- | --- |
| `scripts/docs/check.py` | `docs governance ok (15 indexes)` |
| `scripts/verify/verify_delivery_governance.py` | `Delivery governance verification ok. Active CHGs: CHG-20261015-098, CHG-20261023-101` |
| `scripts/verify/verify_product_master_alignment.py` | `Product and Master Plan alignment verification ok` |
| `scripts/verify/verify_m0_config.py` | `Workspace config verification ok` |
| `scripts/verify/verify_skills.py` | `verified 10 skill source files` |
| `scripts/verify/verify_m2_acceptance.py` | `M2 static cross-repository acceptance matrix ok` |

补充：

- Cloud 契约 YAML 32/32 可解析（PyYAML `safe_load`）。
- Agent `tests/test_contract_docs.py`：`Ran 8 tests ... OK`，README 端点列表与 OpenAPI `paths:` 完全一致。
- Cloud `go test ./internal/modules/cloudagent/service/`：`ok`，兼容性用例含 current、newer、pre-agent-token（拒绝）、older、wrong major、malformed。

## 旧事实扫描

扫描对象仅限当前事实文档（`docs/product`、`docs/engineering`、`docs/contracts`、`delivery/milestones`），历史归档与 ADR 正文按治理保留。

```bash
git grep -c -E '设备绑定|设备解绑|运营电脑绑定|local_agent_nodes|binding_ticket|runtime-report|desktop_login_version|auth_version|节点凭据|节点授权|执行节点' -- docs/product docs/engineering docs/contracts delivery/milestones
```

- 剩余 4 处，全部为合法叙述：
  - `M2-account-runtime.md:573` 取代声明本身；
  - `M2-account-runtime.md:583` 明确写“不提供设备绑定、换绑或解绑入口”；
  - `M4-content-production.md:73` 的“自定义执行节点”指工作流节点，与 Agent 节点模型无关；
  - 架构 §8.2 第 28 条禁止“持久化、记录或回显 Agent Token 或节点凭据”。
- 阳性对照：`git grep -c '设备绑定' -- delivery/completed/CHG-20261001-072/change.md` 返回 `7`，证明模式与路径可用。
- 反向核对：本次替换的设备/节点规则所在章节（第三章 §3.2.4/§3.2.7/§3.4.3、第二章 §2.4.4/§2.4.6、架构 §2.7/§4.7/§8.2、通信规约 §12.1/§13/§19/§20）在改写后不再命中，说明扫描确实覆盖了这些位置而非空转。

## 未覆盖项

- 真实 Agent/BitBrowser/打包 Desktop 回归与四仓全量测试留 T-10。
- 归档记录（`delivery/completed/`）与历史 ADR 正文按治理框架不改写，其中设备/节点叙述不作为当前事实。
- Cloud 仓 `internal/modules/production/*` 的未提交改动不属于本 CHG，未纳入任何提交。
