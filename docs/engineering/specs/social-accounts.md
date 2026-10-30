# 社媒账号：数据、接口与本机执行

产品规则唯一正文为[第三章 §3.3](../../product/prd/详细文档/第三章_用户与账号管理.md#33-社媒账号管理)，交互为[当前原型](../../../example/proto/social-accounts/index.html)，取舍见[ADR-0030](../../decisions/0030-social-account-rebuild.md)。本文定义目标工程设计；实施及验收状态归 Delivery，不以文档存在声明已上线。正式 OpenAPI、Schema 和 DTO 由提供方仓库维护。

## 1. 数据归属与四张领域表

### 1.1 最终表集合

账号领域使用 media_accounts、media_account_categories、media_account_tags、media_account_import_batches 四张表。Cloud 保存业务事实；Agent 不落账号/Cookie/批次业务库；Desktop 只桥接。users、categories、browser_profiles、proxies 继续复用。不保留独立账号组，不新增 Cookie 版本表或接入明细表。

### 1.2 表结构与字段

| 表 | 字段与责任 | 约束/索引 |
| --- | --- | --- |
| media_accounts | 保留现有账号、归属、身份、窗口、启停、备注与登录字段；新增 last_check_status/message/identity、check_operation_id/started_at/profile_id；保留 original_cookie、active_cookie、cookie_status、cookie_updated_at；新增 before_cookie、cookie_update | 保留唯一 user_id+platform+platform_account_id（待识别 UID 为 NULL）、browser_profile_id+platform（未绑定为 NULL），以及归属/窗口外键、原有查询索引 |
| media_account_categories | media_account_id、category_id | 复合主键；同账号多选属于同一 type，关联归属用户可用的已启用类目 |
| media_account_tags | media_account_id、tag_name、created_at | 复合主键；不建全局标签字典 |
| media_account_import_batches | id、user_id、request_key、platform、content_json、revision、created_at、updated_at | id 自增主键；唯一 user_id+request_key；user_id+created_at 索引 |

主键/关联 ID 沿用 BIGINT UNSIGNED 和现有 API ID 表达。request_key/操作编号使用 VARCHAR(64)，platform/状态使用 VARCHAR(32)，说明 VARCHAR(500)，时间 DATETIME(6)。content_json、cookie_update、检查观测为 JSON；revision 为非空 BIGINT UNSIGNED，初始 0。Cookie 字段使用 LONGTEXT，原始输入保留原格式，实时读回和写前值存完整 Cookie 对象的 JSON 文本。

108 新增 last_check_status，默认 never，枚举 never/running/completed/failed；其余检查新增字段可空。last_check_identity 为观测 UID/name/avatar，供身份对照。last_check_at 表示最近取得结论的时间，失败不覆盖历史平台资料与登录结论。结果须匹配当前检查编号、窗口和归属；重复结果返回原结算，迟到结果拒绝，绑定变化使旧检查失效。

资料、标签和类目更新在一个事务完成；检查使用专用带条件更新，不用整行旧记录回写覆盖其他字段。迁移只新增必要字段/表和删除废弃账号组，不预占迁移序号，不改旧建库链。

### 1.3 CK 明细与写前保护

| 保存位置 | 内容 | 说明 |
| --- | --- | --- |
| media_accounts.original_cookie | 首次实际导入的原始输入 | 后续更新不覆盖；人工登录但从未导入时为空 |
| media_accounts.active_cookie | 最近一次实际读回并确认的目标平台 Cookie | 未取得时为空，不用原始输入冒充当前值 |
| media_accounts.before_cookie | 最近一次写入前，从目标窗口实际读取的完整目标平台 Cookie | 内部保留，不是凭证历史产品 |
| media_accounts.cookie_update | 当前更新 request_key、operation_id、目标窗口、status/step、待确认 input_cookie 及必要回执 | 仅保存当前处理和结算，不建立操作历史；未完成或未知时不被下一次更新覆盖 |
| 批次 content_json.items 中的单项 | 接入期间的 input_cookie、before_cookie、目标与必要回执 | 未形成正式账号也有写前值；成功时事务转存到正式账号，批次移除已转存的凭证副本，保留行号和结果关联 |

NULL 表示尚未读取，序列化的空数组表示已读取并确认为空。Cookie 写前值必须从窗口读取，不能以数据库旧 active_cookie 替代；保留完整 domain/path/expires/httpOnly/secure/sameSite 等属性。写前保护失败不写入。明确成功才更新 active_cookie/cookie_updated_at；失败保留原当前值，未知保留输入、写前值、目标与操作编号先核实。更新结束清理不再需要的临时输入，保留必要当前回执，不引入无限历史、定时归档或备份中心。

凭证入口通过 GET /media-accounts/:id/credentials 读取最初输入、当前确认值与时间；写前保留和内部回执不进入运营明细。当前账号表并无平台密码或接码链接字段，本次也不新增。

### 1.4 content_json 与单项标识

content_json 顶层存批次补充信息，items 为数组。分类、标签、备注等非索引批次属性直接放顶层；已有表列不再重复放入 JSON。批次说明有实际需求时直接增加顶层字段，无需改变 items 路径。不增加第二个 options_json 或 items_json 列。

```json
{
  "category_ids": [21],
  "tags": ["测试矩阵"],
  "remark": "",
  "items": [
    {
      "row_number": 1,
      "status": "succeeded",
      "step": "completed",
      "attempt": 1,
      "account_id": 101,
      "browser_profile_id": 501,
      "message": "接入成功"
    },
    {
      "row_number": 3,
      "status": "pending",
      "step": "waiting",
      "attempt": 0,
      "input_cookie": "SESSDATA=demo-input",
      "before_cookie": null,
      "account_id": null,
      "browser_profile_id": null,
      "message": ""
    }
  ]
}
```

示例 Cookie 是占位值。row_number 是输入原始行号，确认时服务端校验正整数、唯一且对应有效行；预览排除无效行后可以不连续。批次创建后行号和存储顺序固定，排序只影响展示，跳过/恢复使用状态，不物理删除或重新编号。修改输入形成新批次；原项重试保留原行号。

单项由 batch_id+row_number 定位；数组下标不作为业务身份，不生成单项 UUID。attempt 在开始实际执行及明确失败后重新执行时递增；操作编号由 Cloud 派生为 import:{batch_id}:{row_number}:{attempt}，无需另存随机 UUID。需要额外保存的外部窗口 ID、创建回执、写前指纹或跳过前状态，仅在相应步骤写入该单项，不建立独立历史或阶段表。

## 2. Cloud API

### 2.1 现有接口收敛

| 现有接口 | 处理 |
| --- | --- |
| 列表/新增/详情/资料 PATCH；绑定 PATCH、解绑 DELETE | 保留路径，按当前 PRD 改字段；解绑已注册但账号 OpenAPI 缺失，实施时补齐 |
| check、check/result | 保留路径，补当前执行结果和编号语义；无已存 Cookie、未分类亦可检查 |
| identify；tags/add、tags/remove | 删除；身份由检查写入，标签并入账号 PATCH |
| cookies/read-sync、cookies/read-sync/result；GET /:id/cookies | 删除旧链路，改为 credentials 与专用 cookie-updates；旧 GET 已注册但账号 OpenAPI 缺失 |
| /account-groups 的 POST/GET、/:group_id 的 PATCH/DELETE、/:group_id/accounts GET | 删除，不补为继续维护的产品 |

契约由提供方维护，修改 OpenAPI/Schema/错误码后同步直接消费者和契约锁。

### 2.2 目标接口目录

所有路径以 /api/v1 为前缀，响应沿用 errcode/message/data/logid。

| 接口 | 请求与结果 |
| --- | --- |
| GET /media-accounts | search/platform/enabled/platform_login_status/category_type/category_ids/tags/tag_match/user_id/team_id/profile_search/page/page_size；按角色收窄；返回归属名称、检查状态及分页 total，无凭证 |
| POST /media-accounts | platform/category_ids/tags/remark；只建本人待识别台账，不含 Cookie 或手填身份 |
| GET /media-accounts/:id | 与列表一致的只读业务投影 |
| PATCH /media-accounts/:id | category_ids/tags/remark，或独立 enabled 请求；未传不改、空数组清空；不接受手填身份/登录结论 |
| PATCH / DELETE /media-accounts/:id/profile | 绑定/解绑本人窗口，校验同平台占用；只改关联，不写或清 Cookie |
| POST /media-accounts/:id/check | 返回 operation_id/browser_profile_id/bit_profile_id/platform/expected_platform_account_id |
| POST /media-accounts/:id/check/result | operation_id、execution_status(completed/failed)、平台观测与 check_items/message；同 UID 刷新，异 UID 保存对照，失败保留旧结论 |
| GET /media-accounts/:id/credentials | 最初输入、当前确认值与更新时间；无值为空，不触发本机读写 |
| POST /media-accounts/:id/cookie-updates | request_key、当前更新编号 expected_operation_id（初次可空）、input_cookie；原子校验目标并保存 cookie_update，返回本次编号与目标 |
| PUT /media-accounts/:id/cookie-updates/:operation_id/snapshot | 目标平台写前值及实际占用；保存 before_cookie 和必要指纹后返回 can_apply=true 与本次编号 |
| PUT /media-accounts/:id/cookie-updates/:operation_id/result | 写入/读回/身份与明确或未知结果；确认成功事务更新账号凭证，失败保留旧值，未知继续保留本次处理 |
| GET /media-accounts/:id/cookie-updates/:operation_id | 返回当前匹配操作的状态/回执；旧操作冲突，不建设更新历史查询 |
| POST /media-account-imports/preview | 平台、分类、标签、逐行输入；只校验并返回原行号和错误，不建正式资源 |
| POST /media-account-imports | request_key、平台、批次属性与确认有效行；一条批次记录保存 content_json，重复提交返回同批次 |
| GET /media-account-imports；GET /media-account-imports/:id | 本人批次摘要和详情；详情为批次属性、items 数组、revision 与七计数；普通投影不回传内部 Cookie |
| POST /media-account-imports/:id/items/:row_number/start | expected_revision；原子领取当前可执行项，返回 attempt/operation_id/step/窗口计划和必要执行输入；重复领取不能再次下发执行 |
| PUT /media-account-imports/:id/items/:row_number/result | expected_revision、attempt、step、结果；按当前步骤结算，重复回报返回已有结果，不接受整份 content_json 覆盖 |
| POST /media-account-imports/:id/items/:row_number/actions | expected_revision、action=skip/restore/retry/reconcile/reuse；复用带 candidate_profile_id 与明确确认；未知只先核实 |

列表标签模式 tag_match=any/all/exclude。normal 检查结论必须有 UID；failed 不要求伪造身份。异 UID 不接管原账号；重复 UID 返回 existing_account_id，不覆盖已有账号的窗口或 Cookie。分类编辑校验同 type，归属名称关联查询，不冗余保存账号表。

Cookie 和批次执行仅本人 Desktop 可用；管理员无凭证/本机入口。写前流程为 Agent prepare → Cloud 持久化并肯定允许 → Agent apply；批次通过单项 result 的 step=prepared 保存同样信息。成功阶段响应不等于整项接入成功。明确失败红色反馈，未知显示待确认；旧编号、目标变化与版本冲突用结构化错误，不解析字符串驱动状态。

## 3. 幂等与并发

- 创建批次前，前端为一次确认意图生成一次 UUID request_key；连续点击和网络重试复用，打开已有批次使用 batch_id。唯一 user_id+request_key 防重复创建。content_json 内保存服务端生成的规范化请求摘要 request_digest，用于拒绝同 key 不同内容；摘要不是业务身份，不进入普通响应。该 UUID 不扩散为逐项 UUID。
- 单账号 cookie_update 保存当前 request_key 与输入摘要，同 key 同内容返回当前处理。新请求须匹配 expected_operation_id 且无未完成/未知操作；过期起始请求不能覆盖新处理。仅保存当前回执，不提供永久幂等历史。
- 单项状态仅 pending/running/succeeded/failed/skipped/uncertain；step 记录目前执行到哪一步。开始领取时在短事务内校验状态并递增 attempt；相同领取的重复请求返回已处理状态，不重新授予执行。已成功项不重放，未知项不递增 attempt，明确失败后的新尝试才递增。
- 服务端按 row_number 查找数组项，校验本次编号、步骤和状态，再以 WHERE id=? AND user_id=? AND revision=? 更新单项 JSON 路径并递增 revision。影响 0 行则重读：已结算返回原结果，否则返回冲突；不能直接重放浏览器操作。数组路径只由服务端生成，不接受客户端路径。正式账号与单项的结算在同一数据库事务内完成。
- revision 防止旧 JSON 覆盖，但不同 key、不同批次仍可能操作同一窗口。109 在共享 browser_profiles 增加可空 cookie_operation_id，短事务内通过条件更新取得目标窗口的 Cookie 操作占用；失败领取不得执行。明确结算才释放，未知保留编号先核实；只读核实取得明确失败结论后可释放占用，不仅凭超时判断失败；窗口关联变更和冲突操作也校验该占用。不建额外锁表或通用任务表，数据库事务不跨浏览器调用持有。
- 每批逐项执行，同批已存在未结算执行时其他页面只查看/核实，不能并行领取下一项。关闭浮层停止发起下一项，已发出项先结算或待确认。JSON 存储不保证外部操作恰好一次；超时后读取真实状态，不能靠重发编号推断安全。
- 此方案用于按批次查看、有限大小且逐项执行的接入。不承诺 JSON 内不同单项独立行锁或所有写入均原地局部更新。实施时根据真实 Cookie 体积验证批次容量及响应大小，不为假设的大规模并行预建明细表、索引或后台队列。

## 4. Agent / Desktop 与批次结果

Agent 只执行本机和平台能力；Cloud browser_profile_id 是数据库 ID，Agent profile_id 是 BitBrowser ID，Cloud 返回 bit_profile_id 显式转换。提供方先定义正式 DTO，再更新 Desktop Rust/命令及 Vue。

| Agent 接口 | 输入与结果 |
| --- | --- |
| POST /api/v1/account-check（保留） | profile_id/platform/expected_platform_account_id；返回实时 UID/name/avatar/login_status/check_items，调用失败与有效平台结论分开，不写 Cookie |
| POST /api/v1/cookie-read（修改） | 增加 platform，按平台域读实时 cookies，source=live；失败不用存量值冒充成功 |
| POST /api/v1/account-cookie/prepare（新增） | 本次编号/窗口/平台/预期身份；返回实际占用、完整 before_cookie 及指纹，情况不明不当空闲 |
| POST /api/v1/account-cookie/apply（新增） | 本次编号/目标/input_cookie、Cloud 已允许的写前指纹；再次比较当前会话，匹配才写目标平台；返回 applied/failed/uncertain 与读回/身份 |
| POST /api/v1/account-cookie/inspect（新增） | 本次编号/目标/预期身份与输入摘要；只读核实，不重新写入 |
| POST /api/v1/bit-browser/profile-create（复用扩展） | 带本次创建标识，沿用返回 id，通过扫描核实超时结果；可靠写入/检索标识须 BitBrowser 实测，不能确认时不重复创建或转复用 |

实际 Cookie 读取使用 CDP；平台识别仍以实时平台响应为准，保存值回退不能冒充实时成功。B站/百度适配保留 Client/Service 分层，不在 Vue 或 Desktop 复制平台逻辑。prepare/apply/inspect 不增加 Agent 业务库或执行历史。

批次成功必须有真实 UID、明确登录结论和正确正式窗口关系；人工登录、待同步、容量不足、身份冲突以 step/message 表达。需要人工登录时继续原项，不重新导入整批。跳过保留原项和必要原状态，恢复后从原步骤处理；未知先核实。检查成功表示取得结论，与接入成功语义不同。

七计数为 total 加 succeeded/failed/skipped/running/pending/uncertain 六个互斥计数，读取 items 聚合，不重复存储。批量检查复用逐项检查 API 和计数投影，不另建长期检查历史。总继续按钮只计可自动继续项。

## 5. 清理与执行边界

- 删除旧 AccountOpeningPage.vue、/account-opening 路由菜单及旧入口专用角色判断；批量入口回归账号模块。
- 删除 /account-groups、模型/Service/Repository/客户端及 media_account_groups 表；后续任务固化账号 ID，不建替代组中心。
- 删除手填 identify、资料更新中的身份/登录状态、批量 tags/add/remove；资料 PATCH 原子更新标签。
- Cookie 更新闭环替换旧 read-sync 与把保存值当实时值的路径，更新直接消费者，不保留长期转发别名。保留 original_cookie/active_cookie，新增必要写前值与当前处理；不建立 Cookie 版本表、版本指针、独立接入明细表或逐项 UUID。
- 历史迁移链不改写；追加迁移只操作 Cloud 数据库，不删除共享资源，不触及外部真实窗口/Cookie。执行前核对目标环境、已有记录和反向引用。
- 当前原型仅 example/proto/social-accounts/index.html；移除冲突当前正文，按治理规范保留有价值的旧决策理由和归档证据，不复制多套 PRD/设计。

## 6. 验证

按 108/109/110 定向验证提供方契约、数据库、Vue 和桥接消费者，不做全仓无差别扫描。覆盖检查失败保留旧结论、异 UID 对照、旧编号拒绝；单次写前保护、完整属性与平台隔离；重复创建、同 key 不同内容、并发 JSON 更新、固定行号/排序、重复领取和回报、失败重试、未知核实与跨批次窗口占用。验证 JSON 批次容量、投影不带内部凭证，以及成功项凭证转存和计数一致。

真实验收先用授权测试账号分别验证人工登录识别、读取、写入及隔离；模拟 HTTP 或原型演示不能代替真实数据库/BitBrowser/平台效果。当前文档更新不代表运行时已完成。


## 7. 整体落地方案

### 7.1 三阶段交付

已有 CHG 按下列顺序交付，不再重复创建同范围 CHG。每阶段完成一个可独立验收的运营闭环；前置完成并合入各仓 main 后再启动下一阶段。CHG 是交付范围和验收源，具体代码拆分、内部函数、测试命名、迁移编号与实现命令由实施时的 Codex 根据目标仓现状决定。

| 阶段 | 运营可见结果 | 数据与接口重点 | 同阶段清理 |
| --- | --- | --- | --- |
| [CHG-108](../../../delivery/completed/CHG-20261030-108/change.md) 日常维护与检查 | 按 V7 新增/编辑、列表与详情；人工登录后检查并同步；同 UID 更新、异 UID 对照 | 账号表补当前检查结果及编号；资料接口收窄，绑定/检查链路明确，无 Cookie 和分类前置 | 旧手填身份、账号组、标签外部接口、独立开户入口及专用实现 |
| [CHG-109](../../../delivery/active/CHG-20261030-109/change.md) 单账号 Cookie | 查看原始/当前 CK；新接入或更新并检查；失败和待确认可处理 | 账号 before_cookie/cookie_update、窗口当前操作占用；Cloud 起始/保留/结算，Agent prepare/apply/inspect | 旧 read-sync/读取客户端及只服务旧链路的实现；保留原始/当前 Cookie 字段 |
| [CHG-110](../../../delivery/planned/CHG-20261030-110/change.md) 批量接入 | 输入预览、逐项接入、七计数、人工处理与关闭重进 | 仅新增批次表；content_json 顶层批次信息+items 数组；固定行号、请求去重、revision 和尝试次数 | 旧批量残余、模拟成功和无消费者代码；补齐最终原型入口 |

108/109 交付期间后续能力如尚不可用，应明确其状态，不以演示成功或旧开户页面代替。全部完成后呈现 V7 的完整操作闭环；不引入旧模块兼容、接码、审计中心或通用任务范围。

### 7.2 跨仓职责与接口交付

| 归属 | 本次落地责任 |
| --- | --- |
| Workspace | 保持 PRD、ADR-0030、本文、原型和 CHG 范围一致；清理冲突当前结论，不保留并行方案 |
| Cloud Backend | 正式数据、角色/归属、检查结算、Cookie 当前处理、批次 JSON 与冲突控制；提供方正式定义 Cloud API/Schema/枚举/错误码 |
| Cloud web | 唯一 Vue 业务源码；两端共用页面，按原型和公共规范实现；Desktop 场景按当前 Cloud 许可调用本机能力并回报结果 |
| Agent | 平台/浏览器真实读取和写入、平台域隔离、创建结果核实；提供方定义 Local API，不保存批次业务库 |
| Desktop | DTO/受控命令与 Agent 通信、运行环境；不复制 Vue 页面、平台识别规则或 Cloud 业务状态机 |

每阶段先确定受影响的提供方契约，再同步直接消费者和契约锁，最后验证该组合。具体路径见 §2、§4；仅变更实际受影响的契约，不为未改动能力提升版本。未上线模块允许协调切换破坏性接口，不保留长期转发或双写。

### 7.3 三条核心链路

1. 人工登录：建台账/绑定窗口 → 用户在浏览器登录 → 检查并同步 → Cloud 保存真实结论；系统检查只读，分类和已存 Cookie 均非前置。
2. 单条 Cookie：确定账号和目标窗口 → 保存本次处理并取得窗口占用 → 本机读取写前值 → Cloud 确认保留 → 本机写入、识别并读回 → Cloud 更新当前凭证/正式关系；明确失败保留旧值，未知保留本次上下文先核实。
3. 批量：预览无资源副作用 → 一次确认创建批次 → 按固定原行号逐项复用单条能力 → 结算账号与 JSON → 聚合展示；创建窗口、写 Cookie 和 Cloud 回报分别识别结果，重复请求不等于允许重复执行。

批量项尚未有账号时，写前值保留在该项；成功后转存账号。不同页面相同提交由 request_key 去重，不同请求仍须校验目标窗口占用。窗口创建不明先核实，不直接重建；Cookie 结果不明先核实，不直接再次覆盖。

### 7.4 清理、发布与验收

清理与替代闭环同阶段完成：先更新受影响接口及直接消费者，再删除废弃入口/代码，不另起全仓翻新。历史顺序迁移保留，新增迁移只修改本次 Cloud 表结构；共享窗口、代理和类目能力继续复用。测试库已有记录按目标环境处理，不触发外部窗口删除或 Cookie 清空。

每阶段以对应 change.md 的可见结果验收，组合验证数据库、契约、两端页面与真实平台效果。重点反例为旧检查结果、异 UID、读写失败、重复/并发请求和结果未知；页面遵循 V7、三角色及公共规范。批次容量用真实 Cookie 体积验证后确定，不用 JSON 结构本身推断容量或并发能力；不预建大规模并行方案。

发布采用 Cloud/Agent/Desktop 已验证的契约组合。异常时停止发起新的外部操作，保留已开始项并核实；数据库或代码回退不自动恢复浏览器会话，不自动回放写前 Cookie。真实平台、页面或容量尚未验证时，明确记录未验收，不以模拟响应或代码存在声明完成。
