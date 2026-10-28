# CHG099 · 运营资源重构报告与执行计划

## 任务理解

本次重构覆盖三个核心功能块：社媒账号、浏览器窗口、代理。目标不是给现有实现继续叠状态，而是收敛数据边界、命名、页面信息架构和本机执行链路。

CHG099 依赖 [CHG-20261029-107](../../completed/CHG-20261029-107/change.md)（游戏目录改为扁平业务类目）。类目迁移先完成并合入，之后 CHG099 再修改社媒账号及运营资源页面。

本文件是当前现状、目标态、文档清理和任务顺序的唯一执行报告；ADR 只保留长期取舍，OpenAPI / business schema 只保留机器契约。

## 实施前事实

以下来自 2026-10-29 本机 `wt_media_cloud` 实际结构：

| 表 | 当前行数 | 当前主要问题 |
| --- | ---: | --- |
| `media_accounts` | 7 | `name/avatar_url/login_status` 未体现第三方数据；Cookie 大字段被普通列表查询读取；契约仍残留 `game_id/retired` |
| `browser_profiles` | 40 | 比特镜像、实际代理、正式托管关系和页面状态混名；`remark` 实际是比特备注；进行中操作没有额度预留 |
| `proxy_configs` | 0 | `business_status` 与窗口/账号启停语义不一致；`observed_exit_ip` 从未写入；最近检测原因刷新后丢失 |
| `profile_sync_scans` | 70 | `diff_json` 重复表达；`reject` 不落状态；没有真实 `observed_at` |
| `profile_sync_candidates` | 2711 | 临时快照拆成第二张表，54 次 ready 扫描长期堆积 |

当前关键链路问题：

- Cloud `/proxies/{id}/assign` 由服务端直接访问 `127.0.0.1:8765` 的 Local Agent，生产环境不可依赖；
- Desktop 没有代理 apply / verify / unbind 桥；
- `local_agent_profile_restore` 会顺带写代理字段，可绕过配额和进行中占用；
- 异常结果没有统一按失败收敛，也没有可重试的临时额度预留；
- 配额只算正式关系，不计算进行中的目标；
- 同步发现的代理关系确认没有重查配额；
- 设备、代理、游戏命名形成多个中间态 ADR，当前文档重复且部分已失效。

### 实施前接口面

社媒账号当前 11 个 Cloud 接口：

```text
GET    /media-accounts
POST   /media-accounts
GET    /media-accounts/{account_id}
PATCH  /media-accounts/{account_id}
POST   /media-accounts/{account_id}/identify
POST   /media-accounts/{account_id}/check
POST   /media-accounts/{account_id}/cookies/read
POST   /media-accounts/{account_id}/cookies/read-sync
POST   /media-accounts/tags/add
POST   /media-accounts/tags/remove
PATCH  /media-accounts/{account_id}/profile
```

窗口当前 12 个 Cloud 接口，代理当前 22 个 Cloud 接口。旧代理分配链路包含
`assign/assign-batch/unbind/release/profile-unbind/local-scan/confirm` 六套入口，
状态和额度判断分散；本轮收敛为两个代理操作接口。

Local Agent 已有窗口扫描、创建、打开、关闭、更新、删除、代理提取、代理 mutation 和
proxy assignment；Desktop 已有窗口桥，但没有代理写入桥。接口细节以当前 OpenAPI 为准，
不在本报告复制全部 schema。

## 实施结果

截至 2026-10-29，目标 7 表模型、统一命名、单用户单快照、同步 Cookie、Cloud 代理预留/Desktop 执行/Cloud 结算均已落地。Web 适配层和三个页面已改为直接读取 `enabled/local_state/protocol/max_profiles/platform_*`，单窗口同步中遗留的代理变化死分支已删除。真实 MySQL live test 和临时空库全量迁移通过。真实 BitBrowser 写入与目标网络仍未执行，因此验收保持 VERIFYING；详情见 [acceptance.md](evidence/acceptance.md)。

## 目标数据模型

### 命名规则

- 启停统一 `enabled TINYINT(1)`，API 使用布尔值。
- 比特只读镜像统一 `bit_`。
- 平台账号只读数据统一 `platform_`。
- 检测结果统一 `last_check_`。
- Cloud 自有字段不加第三方前缀。
- 生命周期使用 `*_state`，检测/登录使用 `*_status`，不继续混用 `business_status`。

### Cloud 表

```text
media_accounts
media_account_games -> media_account_categories       (CHG107)
media_account_tags
media_account_groups
browser_profiles
proxies                  (原 proxy_configs)
browser_profile_syncs    (原 profile_sync_scans，单用户单快照)
```

`profile_sync_candidates` 删除。

不新增：代理操作表、连接版本表、检测历史表、敏感任务表、审计事件表。

### `media_accounts`

```text
id, user_id, team_id
platform, platform_account_id, platform_name, platform_avatar_url
browser_profile_id, remark
identification_status, duplicate_of_account_id
enabled, platform_login_status
last_check_at, last_check_items
cookie_status, cookie_updated_at, original_cookie, active_cookie
created_at, updated_at
```

规则：

- `team_id` 保留创建时历史归队；
- 列表/摘要查询不得读取 Cookie 大字段；
- 保留现有账号—类目多对多与标签表；
- `media_account_tags` 收敛为 `(media_account_id, tag_name)`，删除冗余 `id/user_id`；
- `account_groups` 改为 `media_account_groups`，只保存个人筛选预设，不复制业务状态。

### `browser_profiles`

```text
id, user_id, team_id
bit_profile_id, bit_main_user_id, bit_user_id
bit_name, bit_seq, bit_group_id, bit_group_name
bit_profile_status, bit_updated_at, bit_remark
bit_proxy_type, bit_proxy_host, bit_proxy_port
remark, enabled, local_state
proxy_id
reserved_proxy_id, reserved_since
last_synced_at, created_at, updated_at
```

规则：

- `proxy_id` 是 Cloud 正式托管关系；
- `bit_proxy_*` 是比特实际观测；
- `reserved_proxy_id` 只在进行中的 apply 操作期间占用目标额度，不作为用户可见待确认状态；
- 同一窗口有进行中操作时拒绝再次发起写入；
- 有临时预留引用时禁止修改/停用/删除目标代理；
- 结果成功则更新 `proxy_id` 并清预留；拒绝、超时、断开或异常均清预留并按失败返回；
- `proxy_id`、`reserved_proxy_id` 外键使用 `RESTRICT`，不再依赖 `SET NULL` 掩盖错误。

### `proxies`

```text
id, team_id, name
source, protocol, host, port, username, password, extract_url
region, supplier, tags, expires_at
enabled, max_profiles, remark
last_check_at, last_check_result, last_check_message
created_at, updated_at
```

规则：

- 删除 `observed_exit_ip`；
- 保留最近一次检测结果和原因，不建检测历史；
- 正式绑定数和进行中预留数在查询时计算，不落冗余计数字段；
- 正常分配、解绑和直连都走统一代理操作状态。

### `browser_profile_syncs`

```text
id, user_id UNIQUE, bit_main_user_id
snapshot JSON, observed_at, expires_at, created_at
```

规则：

- 每个用户最多一份当前扫描；
- 新扫描覆盖旧快照；
- 确认、拒绝、过期后删除；
- 不保存跨扫描历史、`diff_json` 或候选表；
- 快照只包含非秘密的比特窗口与实际代理字段。

### 依赖关系

```text
users
├── media_accounts ── browser_profiles
│   ├── media_account_categories ── categories
│   └── media_account_tags
├── browser_profiles ── proxies (proxy_id / reserved_proxy_id)
├── browser_profile_syncs
└── media_account_groups

operation_teams
├── users.current_team_id
├── media_accounts.team_id        historical
├── browser_profiles.team_id      historical
└── proxies.team_id               current resource scope
```

## 目标接口与执行边界

### Cloud

- 资源启停统一通过 `PATCH` 写 `enabled`，删除单独 status/quota 端点。
- 扫描使用 `/browser-profiles/sync` 单例：创建、读取、确认、删除。
- 代理写入使用两个接口：
  - `POST /browser-profiles/{id}/proxy-operation`
  - `POST /browser-profiles/{id}/proxy-operation/result`
- 删除 Cloud Web 的 create/open/close 兼容桩。
- 删除 assign、assign-batch、unbind、release、profile-unbind、local-scan/confirm 旧组合。

### Desktop / Agent

- Cloud 只创建意图和收敛结果，不访问运营电脑；
- Desktop 新增 proxy apply / verify / unbind 桥；
- Agent 保留 `proxy-assignment` 明确 ack 与 `proxy-mutation` 解绑读回；
- `proxy-check` 退出正常业务路径，Cloud 负责代理健康检测；
- `local_agent_profile_restore` 不再写代理字段；
- Cookie 读取只保留 `read-sync -> Desktop/Agent 读取 -> result` 链路；删除异步 `cookies/read`、Cloud Agent 通用任务接口和 Cloud `tasks` 表；
- Agent SQLite 不新增表。

## 页面与反馈

- 社媒账号：账号/平台事实、检查结果、Cookie 入口分开；列表不因 Cookie 大字段变慢。
- 窗口：BitBrowser 字段、Cloud 运营备注、正式代理和比特实际代理分开展示。
- 代理：资源启停、到期、检测、额度分开表达；最近检测原因可刷新后保留。
- 异常结果：窗口行和批量结果显示失败原因并允许直接重试；不提供读取后人工确认态。
- 批量：逐项 prepare/result，不建 batch 任务中心；失败仅重试失败项。

## 文档清理

本 CHG 同步执行以下清理，不再保留中间态重复裁决：

- 新增 ADR-0027，合并并取代 ADR-0025/0026；
- 新增 ADR-0028，取代游戏稳定字符串和多游戏过渡裁决 ADR-0011/0012，并局部取代 ADR-0001；
- 删除已被 ADR-0022 完全取代的 ADR-0018/0019；
- ADR-0008 保留账号/Cookie 同步执行原则，并标注浏览器/代理部分由 ADR-0027 收敛；
- M2 历史验收记录保留，但当前执行只引用 ADR-0022/0027，不再复制设备/节点中间模型；
- CHG099 的 `change.md` 只保留范围/验收，`plan.md` 保存现状与执行方案，`checkpoint.md` 只保留交接状态；
- 实现完成后，把最终稳定结论回写一份 Engineering Spec 和 OpenAPI/business schema，不把字段表复制进 PRD。

## 顺序任务

| 步骤 | 工作 | 完成判据 |
| --- | --- | --- |
| 0 | 完成 CHG107 类目 Foundation | 类别迁移与契约合入，旧 `game_id` 清理 |
| 1 | 固化 ADR-0027 与运营资源数据模型 | 无 blocked 产品/架构问题，文档清理完成 |
| 2 | Cloud 迁移与模型收敛 | 7 张领域表落定，旧候选/无字段与 `tasks` 清理，迁移重放通过 |
| 3 | Cloud API 与权限/额度/失败收敛 | 团队范围、临时预留、失败释放、直接重试与真实 MySQL 验证 |
| 4 | Desktop/Agent 本机代理桥 | 明确成功、失败、超时/断开、解绑读回、旧 Agent 边界通过 |
| 5 | 三块页面重构 | 列表/详情/表单/同步/批量/三角色/窄屏/失败恢复符合当前原型与正式前端规范 |
| 6 | 文档与契约收口 | OpenAPI/schema/Engineering Spec 一致，删除过期裁决和重复实现描述 |
| 7 | 真实验收 | 真实比特开关/编辑/代理应用、Cloud 检测、目标网络、Desktop 组合全部有读回 |

## 验收矩阵

| 维度 | 必须覆盖 |
| --- | --- |
| 账号 | 新增/编辑/启停、类目/标签/窗口关系、检查、Cookie 专用读取、三角色 |
| 窗口 | 扫描认领、字段镜像、运营备注、启停、打开/关闭、单/批代理 |
| 代理 | 导入、检测、额度、启用、到期、删除占用、动态提取、凭据边界 |
| 异常结果 | 超时、断开、中断、异常响应均按失败释放临时占用，用户可直接重试 |
| 并发 | 同窗口不同目标、两个窗口抢最后名额、同步确认额度复核 |
| Cookie | 同步读取成功、Agent 拒绝、响应丢失、许可释放；无异步任务创建 |
| 环境 | Cloud Web / Desktop / Local Agent 真实组合；不能以 fixture-only 结论代替 |

## 明确不修改 / 不做

- 不新增通用任务中心、操作历史、审计事件表、检测历史表或敏感许可表；删除旧通用 `tasks` 表。
- 不接入比特标签或窗口业务标签。
- 不恢复窗口分配、远程代操作或父子重试任务。
- 不执行新的存量代理清理迁移。
- 不在 PRD/CHG 中重复完整字段表；字段以机器契约和一份 Engineering Spec 为准。

## 已收敛的判断

- 类目规则：社媒账号允许零个，表示尚未分类；内容来源、挖掘策略、合成策略/任务/成片新增时必须选择一个。只有筛选条件可不选；系统不假定或自动创建 `other`。
- 代理异常结果只在“写入可能已发送，但未得到明确成功”时出现：超时、断线、Agent/Desktop 中断、响应损坏或 Cloud 未收到结果。所有异常统一按本次失败处理，保留旧正式关系，清除临时额度预留，用户直接重试；不做读取后人工确认。
- Cookie 读取改同步：删除旧异步 `/cookies/read`、Cloud Agent 通用任务接口和 `tasks` 表；保留 Desktop 同步读取并向 Cloud 回报结果的链路。
