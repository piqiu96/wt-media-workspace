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

### 2026-10-30 补充实施范围

窗口缺失保留业务事实，列表默认展示全部；独立“窗口状态”列与可清空筛选仅提供“已找到 / 未找到”两个值，空值显示全部。窗口状态列及筛选均排在运行状态之前。未找到行可查看与核实，单项删除只出现在该行，独立“清理已删除窗口”入口承担批量清理；在可核实主账号的非空比特快照中，未找到的窗口标记缺失，恢复出现时重新激活。同步结果把本次异常与仍未处理的历史缺失分开显示；历史项可核实或删除，不重复计入本次异常，也不触发新的异常提示。当前本机接口只从窗口行提取主账号 ID；零窗口时无法排除切换了比特主账号，故拒绝把所有原记录标记缺失并提示核实。同步预览展示每项比特字段的原值和新值，详情展示真实运营团队。管理员可按团队名称或 ID 输入筛选；其他角色不显示团队筛选。

代理 `proxies.id` 从字符串主键迁为自增整数，`browser_profiles.proxy_id`、`reserved_proxy_id` 及当前代理操作回执同步转为整数；接口、业务 schema、前端 DTO 和搜索统一使用数字 ID。迁移必须先建立旧到新 ID 映射，保留存量窗口正式/预留关系，并通过隔离 MySQL 对含数据场景验证。旧客户端和新接口不混用；发布组合须同步升级。

代理列表保留地区列，供应商仅在代理详情及新增/编辑中展示；列表不再提供供应商筛选。该调整只改变信息呈现，不移除已有供应商数据或服务端查询能力。

### 已裁定：缺失窗口的人工清理与列表入口

“在册”只指 Cloud 有记录且最近一次成功同步时比特可见，不代表实时在线；该术语和“窗口记录”下拉均移除。日常列表默认展示全部，用独立“窗口状态”列和两个可选值查看“已找到 / 未找到”，不增加双标签或可选的“全部”项。只有存在缺失记录时才在列表上方显示“清理已删除窗口（数量）”入口，进入独立清理对话框。入口说明判定依据是最近一次成功同步，删除前要求运营确认窗口确已在比特删除；暂时改绑主账号或权限异常时先恢复访问，不执行清理。

清理清单只展示 `local_missing`，可多选“批量删除”；缺失行、清理清单和同步结果中的单项操作统一为“删除”，普通窗口不出现该操作。按钮默认主文字色、悬停红字浅红底，最终确认红色实心。用户选择直接物理删除，以无凭据审计保留技术追踪；不采用业务归档。每个窗口独立事务校验、结算，批量逐项呈现成功、失败及原因；不因一条失败重做成功项。删除后的窗口若又出现在比特中，只作为新窗口待认领。

删除前展示关联平台账号数量与名称、释放的托管代理名额。确认后，账号本身、平台身份、标签和历史保留，只清空 `browser_profile_id`，将登录/检查结论置为“待重新核验”，旧 Cookie 不自动用于新窗口；运营稍后手动选择新窗口重新绑定，不能自动猜测替代窗口。窗口记录物理删除自然释放 Cloud 托管代理占用，另留不含代理凭据或 Cookie 的审计记录以供技术追踪；存在待确认代理操作时先核实，不能清除预留或假定写入失败。只允许 `local_missing` 且人工确认比特已删除的窗口清理，不对比特执行删除。本人运营及高级运营可清理本人记录；管理员可按权限清理并留痕，成员查看模式不得代做本机动作。

以上是用户对 Q-03 的裁定。实施时先更新正式 Product/Engineering/Contract，使用隔离数据验证，不能为验证而删除现有运营窗口。

截至 2026-10-29，目标 7 表模型、统一命名、单用户单快照、同步 Cookie、Cloud 代理预留/Desktop 执行/Cloud 结算均已落地。Web 适配层和三个页面已改为直接读取 `enabled/local_state/protocol/max_profiles/platform_*`，单窗口同步中遗留的代理变化死分支已删除。Agent 通用任务执行器、preflight/permit、proxy-check 与浏览器 executors 已删除，只保留独立 file-transfer 租约循环；Desktop 账号检查/Cookie 改用 operation id 直达同步接口。真实 MySQL live test 和临时空库全量迁移通过。动态提取已形成 Desktop/Agent 本机提取、Cloud 保存检测候选，旧来源或版本不能覆盖新的运营编辑。获授权测试窗口已在安装包中完成真实同步、开关、代理应用后的未知结果核实、正常解绑、未分组编辑与读回；测试代理通过本机 Cloud 对默认目标的真实连接。在该次验收结束时代理已清理、窗口原配置已恢复；2026-10-30 后续只读复核又发现同名代理及正式绑定，当前状态以 [acceptance.md](evidence/acceptance.md) 为准，未擅自改动。用户决定本轮暂不测试真实供应商提取；完整角色与视觉走查仍需人工评审，CHG 保持 VERIFYING。

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
- `bit_proxy_*` 是最近确认的比特代理配置，可来自窗口同步的实际读取，或比特写入的明确成功回执；结果不确定时不能提前投影。列表和下一次同步均以该确认事实为基准。
- `reserved_proxy_id` 只在进行中的 apply 操作期间占用目标额度，不作为用户可见待确认状态；
- 同一窗口有进行中操作时拒绝再次发起写入；
- 有临时预留引用时禁止修改/停用/删除目标代理；
- 明确成功则在同一事务更新 `proxy_id` 与 `bit_proxy_*`，清除预留；连接快照在开始操作时写入不含密码的当前回执，防止结算时资源变化导致投影错误。明确拒绝按失败处理。写入可能已发送而结果不确定时，保留可恢复事实并先核对实际配置；测试窗口中“写入成功但回执丢失→本机核实→正式关系落库”以及正常解绑回执均已现场验证。
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
- 确认后在当前记录保留最近确认回执供响应丢失时核实；拒绝可删除，下一次扫描覆盖；
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

### 同步窗口视觉对齐 · 2026-10-29评审稿

当前完整入口为[同步窗口原型](../../../example/proto/browser-proxy/index.html)，打开后选择 `w-sync-reading` 场景；19态与恢复动作见[原型说明](../../../example/proto/browser-proxy/README.md#同步窗口--完整评审入口)。沿用原23/24屏的居中结果弹窗、单条汇总和明细层级；补齐扫描、确认、归属冲突、无变化、空扫描、网络/身份/权限异常、快照过期、明确失败、结果未知和列表重载失败。阶段过程不复用七类计数的批量结果容器。新增仍勾选后认领，已有变化按当前服务确认保存；不因视觉修订改跨仓Contract。

候选Cloud页面已使用居中同步弹窗和逐态结果；最新Desktop安装包实看了真实比特 37 窗口的无变化紧凑结果，已确认的三条缺失未重复要求确认。完整19态中的其他异常和归属冲突仍需人工视觉走查；不能把离线原型结构检查当作真实UI验收。

已审批并落地的运行状态规则：进入本人 Desktop 窗口页面或刷新页面时自动读取一次；页面右上角提供唯一“刷新运行状态”，列表表头和逐行均无刷新入口。自动成功静默，手动成功显示读取数量；失败按原因 Toast 提示，不自动重试、不另设重试入口；未知状态禁用打开/关闭。进行中的自动、手动与同步扫描合并，成功同步直接更新运行状态；普通资料重载、筛选和翻页不扫描。切换到他人视图/离开页面后丢弃旧请求结果；Web 与他人资源无本机读取。原先关闭再停用、批量操作的执行前校验保留。缺失窗口的核实入口使用紧凑居中 Dialog，空账号不显示表格。

后续顺序：交付[最终候选验收与走查清单](evidence/acceptance.md)→人工视觉、权限和交互评审。最新重建与无变化同步的真实页面核对已完成。动态供应商现场提取按用户裁定延期。运行状态入口与同步19态候选均已落地；保存响应丢失须核实实际结果，不能用固定成功或盲目重提替代。

- 社媒账号：账号/平台事实、检查结果、Cookie 入口分开；列表不因 Cookie 大字段变慢。
- 窗口：BitBrowser 字段、Cloud 运营备注、正式代理和比特实际代理分开展示。
- 代理：资源启停、到期、检测、额度分开表达；最近检测原因可刷新后保留。
- 异常结果：明确失败显示原因并允许安全重试；结果不确定时先读取并核对，无法核实时保留待处理状态。
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
| 3 | Cloud API 与权限/额度/失败收敛 | 团队范围、临时预留、明确失败释放、未确定结果核对与真实 MySQL 验证 |
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
| 异常结果 | 明确失败可安全重试；超时、断开、中断、异常响应等不确定结果先核对，核对不可用时不能盲目重复写入 |
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
- 用户已确认：正常情况以比特接口明确成功响应为准；写入可能已发送而结果不确定时才读取并核对。Cloud/Desktop/Agent 链路已按此裁决调整，080 隔离迁移和并发回执通过；授权测试窗口的真实比特写入、未知结果核实、正常解绑和本机 Cloud 目标网络均已验收。供应商提取网络与非本机部署出口仍需独立验收。
- Cookie 读取改同步：删除旧异步 `/cookies/read`、Cloud Agent 通用任务接口和 `tasks` 表；保留 Desktop 同步读取并向 Cloud 回报结果的链路。

### 同步确认恢复补齐（2026-10-29）

为落地已确认的“未知结果先核实”，现有 `browser_profile_syncs.snapshot` JSON 保留最近一次已确认回执（状态、确认时间、实际接纳窗口），下一次扫描覆盖；不新增表或历史中心。Cloud 提供方契约兼容增加可选 `sync_id`，新版共用 Vue 必传，用于阻断旧页面确认新的快照。重复确认相同快照返回已保存回执；事务内校验快照编号及状态，确认/扫描并发不得重放旧镜像。旧客户端省略编号暂保留当前快照行为；新版恢复流程先 GET 当前快照，同编号已确认则展示结果，同编号待确认才允许重试，快照被替换则重新比对。消费者无生成SDK，直接更新共用API客户端；Cloud/Desktop共享Vue，不新增Desktop桥。

### 代理未知结果恢复落地

沿用 `browser_profiles`，增加一个不含凭据的当前操作 JSON（编号、动作、目标代理、结果），不新增表。开始操作生成编号并占用额度；结果按相同编号与动作结算，保留最近回执；旧响应不能释放新操作预留。待核实不使用TTL自动释放；关闭/重进从本人窗口恢复。读取恢复接口仅向本人返回必要目标配置，认证只交本机比较，页面不展示或落盘；Agent只返回一致/不一致/不可核实。正常写入采用比特明确成功响应；明确拒绝才结算失败；网络、响应或结算未知保留预留，核实后再结算。存在进行中预留时，同步不得覆盖对应窗口镜像或标记缺失。旧客户端不能结算带编号的新操作，返回明确冲突而非假成功；升级后的客户端可恢复。新Agent比较端点缺失时保持待核实，不降级盲写。

2026-10-30 现场补充：Cloud 已创建预留但安装包内 Agent 缺少写入/核实路由时，页面得到 404 并保留待确认名额。构建必须从选定 CHG099 Agent 源冻结，并校验冻结二进制实际路由；Desktop 在打包前再以 Agent 构建清单检查自身需要的代理路由。代理列表和选择器分别列明正式占用、待确认占用及剩余可分配数。核实时先比较足以判定不一致的非敏感字段；仅可能一致时才要求比特返回完整认证字段，仍不得猜测缺失字段或盲目重写。

2026-10-30 批量设置反馈：比特实际写入成功后，原成功结算只更新 Cloud 的 `proxy_id`，窗口 `bit_proxy_*` 仍为旧镜像。页面即使完成 `reloadAll()`，也会显示“配置不一致”，下一次同步再把同一写入列为地址/端口变化。开始操作时将当次发送给比特的非秘密协议、地址、端口存入当前回执；明确成功或未知结果经读回确认成功时，同一结算事务更新正式关系与这些字段。失败、仍待确认及旧编号不得提前投影；旧格式回执维持兼容。此修复不增加 API、二次读回或人工同步步骤。
