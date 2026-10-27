# 实现与门禁证据

日期：2026-10-28
状态：VERIFYING（待人工审核；未合并、未发布）

## 变更落点

| 仓 | 范围 |
| --- | --- |
| `wt-media-cloud` | `proxy`、`profilebinding`、`mediaaccount`、`identity` 后端；迁移 `20261028_077`；`web` 的窗口 / 代理页与共享组件；`cloud-api` 两个 OpenAPI |
| `wt-media-desktop` | `local_agent_profile_update` 命令、DTO 与注册 |
| `wt-media-agent` | 无代码改动；`profile-update`、`global/ip-check` 等端点与合同在改前已存在 |
| `wt-media-workspace` | 产品第三章、工程分界规约、ADR-0025、合同索引、本 CHG |

## T-01 正式定义回写

| 文件 | 落点 |
| --- | --- |
| `docs/product/prd/详细文档/第三章_用户与账号管理.md` | §3.4.5–§3.4.8 窗口同步 / 差异 / 操作；§3.5.1–§3.5.9 代理团队、导入、字段、模式、配额、分配、冲突、角色、服务端检测 |
| `docs/engineering/architecture/社媒运营平台模块分界分层和通信规约.md` | §12.1 例外改为代理连通性检测归 Cloud；§15.1 职责补检测与结果版本判定 |
| `docs/decisions/0025-proxy-team-scope-and-server-side-health-check.md` | 新建 ADR；记录团队归属、存量清理、Cloud 检测、连接版本、角色分工、配额 / 删除收口与 BitBrowser 标签缺口 |
| `config/contract-map.yaml` | `cloud_api.contract_revision` 2026.10.27.6 → 2026.10.28.1 |
| `docs/contracts/contract-map.md` | 新增「Proxy team scope and window-side write-back」小节 |
| `contracts/cloud-api/v1/proxies.openapi.yaml`（Cloud 仓） | `2026.09.06.1` → `2026.10.28.1`；补全生命周期、检测、批量分配、release、`profile-unbind`；`LocalProxyScanConfirmRequest` 改为 `selected_profile_ids`；补充 `ownership_conflict` / `unregistered` |
| `contracts/cloud-api/v1/browser-profiles.openapi.yaml`（Cloud 仓） | `2026.10.23.1` → `2026.10.28.1`；角色 / 团队范围、确认体 `adopt_bit_profile_ids`、备注与启停更新、停用删除规则、窗口字段 |

合同结构校验（Cloud 仓）：

```text
python3 - <<'PY'  # SafeLoader + 重复键检查
for f in proxies, browser-profiles: yaml.load(..., Loader=Dup)
PY
```

实际：两文件均可解析，无重复键；`proxies` 19 个 path / 19 个 schema，`browser-profiles` 10 个 path。修订号与 `config/contract-map.yaml` 的活源对比由 `verify_m0_config.py` 通过。

## T-02 / T-03 / T-04 代理团队、服务端检测、导入

代码落点：

- 迁移 `migrations/20261028_077_proxy_team_scope.sql`：清空 `proxy_configs`，新增 `team_id`、`name`、`tags_json`、团队索引与外键。
- 服务端：团队范围读写校验、启停、配额锁、删除占用检查、到期现算、连接变更清空检测事实。
- 检测：`internal/modules/proxy/service/probe.go` 在 Cloud 进程内发起 TCP / HTTP 探测，结果分类与连接版本绑定；迟到结果丢弃。
- 导入：预览不落库，提交按勾选行导入并逐行返回 `imported` / `failed` / `skipped`。
- 窗口侧写回：`internal/modules/profilebinding/repository/store_mysql.go` 的 `ClearObservedProxy` 只在 `COALESCE(proxy_id,'') = ''` 时清观测地址。

迁移实测（scratch schema `wt_media_mig077_check`，应用后立即删除）：

```text
mysql -uroot ... wt_media_mig077_check < migrations/20261028_077_proxy_team_scope.sql
proxies=0
profile=bp1,proxy_id=NULL
team_id  bigint unsigned  NO  MUL
name     varchar(128)     NO
tags_json text            YES
CONSTRAINT fk_proxy_configs_team FOREIGN KEY (team_id) REFERENCES operation_teams (id)
```

结论：迁移可执行；存量代理被删除，窗口保留且正式 `proxy_id` 被外键置空。

定向测试：

```text
go test ./internal/modules/proxy/... ./internal/modules/profilebinding/... ./internal/modules/mediaaccount/...
```

实际：15 个包全部 ok，0 失败。新增 `TestClearObservedProxyOnlyClearsUnmanagedWindows`、`TestClearObservedProxyLeavesAssignmentsAlone`、`TestRegisterRoutesBindsProfileProxyUnbind` 均通过。

## T-05 / T-06 窗口、共享现场组件与 Desktop 写回

- `wt-media-cloud/web/src/modules/profiles/pages/ProfilesPage.vue`：角色与环境动作、草稿筛选、停用前置、批量混选、同步两阶段、代理动作、创建不确定态。
- `wt-media-cloud/web/src/modules/proxy/pages/ProxyPage.vue`：团队范围、状态列顺序、批量检测、导入预览与提交、行内启停。
- `OperationProgressDialog.vue`（新增）：进度 / 结果 / 失败重试；处理中不可关闭；强制结束不继续调度。
- `local_agent_profile_update`（Desktop）：调用 Agent `profile-update` 后重扫一次，逐字段返回 `verified` / `unconfirmed`；payload 使用 Agent 既有 `groupId` / `groupName` 字段。
- 公共约定：所有抽屉写 `:close-btn="true"`；筛选下拉占位统一 `全部`。

前端定向 / 全量读数见 T-07。

## T-07 验证读数

最后代码改动之后重跑。

| 命令 | 实际结果 |
| --- | --- |
| `cd wt-media-cloud && go build ./...` | 通过 |
| `cd wt-media-cloud && go test ./...` | 0 个 FAIL |
| `cd wt-media-cloud && gofmt -l <changed go files>` | 无输出 |
| `cd wt-media-cloud/web && npm run test` | 88 文件 / 806 用例通过 |
| `cd wt-media-cloud/web && npm run build` | 通过；`ProfilesPage` chunk 86.87 kB（gzip 23.30 kB） |
| `cd wt-media-desktop/src-tauri && cargo test` | 540 passed / 0 failed / 6 ignored |
| `python3 scripts/wt.py test repo --repo wt-media-workspace` | unittest 175 OK；delivery governance / ai workspace / skills / product alignment / m0 config / docs check / control.sh 全部 ok |
| `python3 scripts/wt.py chg verify CHG-20261028-099` | `repo` 场景通过；`integration` 在 `verify_m1_integration.py` 失败（见下） |

`verify_m1_integration.py` 失败为基线既有：`No module named 'wt_media_agent.cloud_agent_client'`。Agent 仓已删除该模块，本 CHG 未修改 Agent 与该校验脚本；同 CHG-20261026-104 证据记录一致。

## 覆盖边界

已由自动化覆盖：

- 角色 / 团队范围与写权限、窗口与代理动作集合。
- 同步勾选认领、归属冲突、未勾选不写入、两阶段确认。
- 停用前置、批量混选禁用、业务停用预检。
- 代理团队过滤、状态列顺序、批量检测、导入计数与逐行结果。
- 服务端检测分类与迟到结果丢弃、配额锁、删除占用、观测地址清除。
- 迁移在真实 MySQL 语法与外键行为。

待人工走查（本机无法程序化驱动 / 截取 GUI）：

- 桌面端真实比特浏览器中的开窗、关窗、编辑读回与逐字段 `verified` / `unconfirmed` 展示。
- 网页版 / 桌面端两种环境下筛选、分页、抽屉关闭按钮与进度弹窗的实际观感。
- 代理检测在目标网络下的真实耗时与失败文案。
- 同步窗口时比特实际值与系统托管值的并排差异显示。

未覆盖 / 已知缺口：

- BitBrowser 标签未接入 Agent 与 Cloud 合同，本期只在 Cloud 维护代理标签。
- 管理员的桌面端没有「本人窗口」，窗口页只提供查看与备注入口。
- 归属冲突只在扫描时作为证据返回，不落库。
- 动态提取仍在本机执行，Cloud 只负责保存后的检测。

## 提交

| 仓 | 分支 | 提交 |
| --- | --- | --- |
| `wt-media-cloud` | `chg/CHG-20261028-099` | `0a3d212` 后端与迁移、`bc710e2` Web、`b86e65f` 合同 |
| `wt-media-desktop` | `chg/CHG-20261028-099` | `a607773` |
| `wt-media-workspace` | `chg/CHG-20261028-099` | 本记录所在提交 |

均未推送、未合并、未发布。
