# 社媒账号：数据、接口与本机执行

产品规则唯一正文为[第三章 §3.3](../../product/prd/详细文档/第三章_用户与账号管理.md#33-社媒账号管理)，交互为[当前原型](../../../example/proto/social-accounts/index.html)，取舍见[ADR-0030](../../decisions/0030-social-account-rebuild.md)。本文定义目标工程设计；实施及验收状态归 Delivery，不以文档存在声明已上线。正式 OpenAPI、Schema 和 DTO 由提供方仓库维护。

## 1. 数据归属与六张领域表

### 1.1 已核实现状与变更方向

2026-10-30 只读核实了 Cloud 的迁移链、账号 OpenAPI / 路由注册及 Agent OpenAPI，并查询本机配置指向的开发库 information_schema；未展开页面、Service 或平台 Client 的实现走查。开发库已有 7 条账号记录，不能据“未正式使用”直接清空；本轮没有执行 DDL、数据修改或浏览器操作。以下为目标设计，不代表当前接口已支持。

| 当前数据库事实 | 最终处理 | 交付 |
| --- | --- | --- |
| media_accounts：BIGINT 主键；UID 可空；enabled 为 tinyint(1)；已有八种登录状态、last_check_at/items、Cookie 双宽字段 | 保留台账；补当前检查结果/编号；Cookie 改为版本引用后删除双宽字段 | 108 检查；109 凭证 |
| media_account_categories：account/category 复合主键；media_account_tags：account/tag 复合主键 | 保留；复用 categories 的 game/ai/anime，不新建类目或标签中心 | 108 |
| media_account_groups：id/user/team/name/filters/sort_order | 删除独立账号组 API 和表；不建设替代组模型 | 108 |
| 版本、接入批次、单项三表均不存在 | 新增 media_account_cookie_versions；再新增 media_account_import_batches/items | 109；110 |

当前已存在唯一索引 `(user_id, platform, platform_account_id)`、`(browser_profile_id, platform)`，以及 users、operation_teams、browser_profiles 和 duplicate_of_account_id 外键；分类/标签引用账号。保留这些关系，变更前核实反向引用。保留本地测试记录的具体方式在迁移执行前按目标环境确定，本设计不安排历史业务迁移项目。

### 1.2 目标表与约束

Cloud 保存正式业务数据，Agent 不落账号/Cookie/批次业务库；Desktop 只桥接。复用 users、categories、browser_profiles、proxies；不新建用户、层级类目、窗口或代理模型。ID 延续现有 BIGINT，API 沿用对应领域的 ID 表达，不额外改名。

| 表 | 核心字段与责任 | 索引/约束 |
| --- | --- | --- |
| media_accounts | id、user_id、team_id、platform、platform_account_id、platform_name、platform_avatar_url、browser_profile_id、enabled、remark；identification_status/duplicate_of_account_id；platform_login_status；last_check_at、last_check_items、last_check_status、last_check_message、last_check_identity；check_operation_id/started_at/profile_id；initial_cookie_version_id/current_cookie_version_id；时间 | 唯一 user_id+platform+platform_account_id（待识别 UID 为 NULL）；唯一 browser_profile_id+platform（未绑定为 NULL）；user_id+platform、team_id 索引 |
| media_account_categories | media_account_id、category_id | 复合主键；关联已启用且适用归属用户的类目，多选同 type；不存冗余一级名称 |
| media_account_tags | media_account_id、tag_name、created_at | 复合主键；不建全局标签字典 |
| media_account_cookie_versions | id、account_id（接入未识别前可空）、import_item_id（可空）、platform、browser_profile_id、operation_id、request_key、previous_version_id、purpose、state、input_cookie、before_cookie、before_fingerprint、confirmed_cookie、created_at/confirmed_at | operation_id 唯一；account_id+request_key 唯一；account_id+id、import_item_id 索引；状态 prepared/applied/confirmed/rejected/uncertain；purpose import/update；凭证值不进入普通账号响应 |
| media_account_import_batches | id、user_id、request_key、platform、category_ids_json、tags_json、remark、created_at/updated_at | 唯一 user_id+request_key；user_id+created_at；统计由 item 聚合，不存七套可漂移计数 |
| media_account_import_items | id、batch_id、row_number、account_id、browser_profile_id、cookie_version_id、status、phase、reason_code/message、operation_id、resume_status、window_plan、reuse_confirmed、created_bit_profile_id、phase_result、updated_at | 唯一 batch_id+row_number；operation_id 唯一；batch_id+status；窗口创建及 Cookie 写入分别记录当前阶段/回执，未知阶段不可重放 |

检查运行状态 never/running/completed/failed；last_check_identity 保存本次观测 UID/name/avatar，供身份对照，不替换正式 UID。last_check_at 表示最近取得结论时间，失败只更新执行状态/原因。check_operation_id 与 check_profile_id 绑定本次目标，结果必须匹配当前编号、归属和窗口；同编号已结算返回现有结果，旧编号拒绝，避免迟到结果覆盖。

账号资料更新、标签替换及类目关系更新在一个 Cloud 事务内完成。检查起始/结算通过 Repository 的专用带条件更新，避免用整行旧记录回写覆盖 Cookie、备注或窗口变更。绑定变化使未结算旧检查失效；移除分类不影响登录检查。

Cookie 版本只服务防误覆盖与本次未完成处理，保留初始、当前、最近写前值和未收敛引用；不向运营开放版本浏览。仅在新结果已确认且无引用时清理被替代中间值；本期不引入定时保留策略、审计报表或备份中心。删除实际存在的 original_cookie/active_cookie；当前账号表并无 login_password、sms_receive_* 等字段，本次也不新增。cookie_status/cookie_updated_at 保留为当前确认版本的摘要，与版本指针在同一事务更新，不作为独立凭证事实。

### 1.3 字段规格与写入边界

- 既有主键/关联 ID 使用 BIGINT UNSIGNED，沿用公共 ID 序列化规则；编号和请求键使用 VARCHAR(64)，platform/状态/阶段/原因使用 VARCHAR(32/64)，说明 VARCHAR(500)，时间 DATETIME(6)，检查观测/阶段回执使用 JSON。Cookie 三个值使用 LONGTEXT，NULL 表示尚未取得；空 Cookie 集合是已读取到空值，两者不能混用。
- 108 新增 last_check_status（非空、默认 never）、last_check_message/identity（可空）、check_operation_id/started_at/profile_id（可空）。检查结果是最近一次投影，不增加长期检查历史表。last_check_identity 的结构为 `{platform_account_id, platform_name, platform_avatar_url}`；未知/失败不清除原台账身份。
- 109 新增两个可空版本引用；版本 account_id/import_item_id/previous_version_id/browser_profile_id 可空（批次尚未准备窗口时），platform、operation_id、request_key、purpose、state、created_at 必填；写前必须已确定 browser_profile_id，before_fingerprint 使用 VARCHAR(64)。prepared 表示已创建待准备版本，不能仅靠该状态判断已有快照。单条接入先建台账并通过公共窗口能力创建/绑定窗口，再创建版本；不依赖 110 批次表。Cookie 版本的 import_item_id 在 110 引入前不建关联约束。未取得写前值不能进入 applied，未完成身份核实和读回不能进入 confirmed；只有 confirmed 可成为 current，首次实际导入输入成为 initial，后续更新不改 initial。
- 110 批次 user_id/request_key/platform 必填；category_ids_json/tags_json 默认为空数组。单项 batch_id/row_number/status（默认 pending）/phase/operation_id/updated_at 必填；账号/窗口/版本及外部创建 ID 可空，phase_result 为本阶段必要回执 JSON。resume_status 只记录跳过前可恢复状态；跳过前若有未知外部结果，恢复后仍先核实。
- 版本与单项的双向引用不建设循环强制外键；由同一 Cloud 事务校验所属关系，版本与账号指针也禁止跨账号/平台关联。按表中唯一键和索引落库，不预建搜索引擎、审计表或通用任务表。
- 旧 Cookie 宽字段只在版本替换及必要测试数据处理完成后删除；迁移不接触外部窗口。实际迁移序号按实施时最新迁移递增，不在计划中预占 082。

## 2. Cloud API 目录

### 2.1 现有接口如何收敛

| 已核实接口 | 结论 |
| --- | --- |
| 列表/新增/详情/资料 PATCH；绑定 PATCH、解绑 DELETE | 保留路径，改为下表字段与约束；解绑当前已注册但账号 OpenAPI 缺失，实施时补齐 |
| check、check/result | 保留路径，增加执行结果与本次编号语义；不要求先有 Cookie 或分类 |
| identify；tags/add、tags/remove | 删除；真实身份由检查写入，标签并入账号 PATCH |
| cookies/read-sync、cookies/read-sync/result；GET /:id/cookies | 删除旧链路；用 credentials 与专用 cookie-updates 替代；旧 GET 当前已注册但未列入账号 OpenAPI |
| /account-groups 的 POST/GET、/:group_id 的 PATCH/DELETE、/:group_id/accounts GET | 删除；路由已有，账号 OpenAPI 未描述，不补成继续维护的产品 |

本轮不改提供方正式契约版本，也不生成消费者 DTO；按 108→109→110 修改对应提供方 OpenAPI/Schema/错误码后，再更新消费者与契约锁。

### 2.2 目标接口

| 接口 | 输入/输出与业务结果 |
| --- | --- |
| GET /api/v1/media-accounts | search、platform、enabled、platform_login_status、category_type、category_ids、标签组合、user_id、team_id、profile_search、page/page_size；服务端按角色收窄；响应含 user_name/team_name（关联查询，不重复存账号表）、当前检查状态及分页 total，不含凭证 |
| POST /api/v1/media-accounts | platform、category_ids、tags、remark；仅建本人待识别台账，不含 Cookie 或手填平台身份 |
| GET /api/v1/media-accounts/:id | 只读账号详情，与列表同一业务投影 |
| PATCH /api/v1/media-accounts/:id | category_ids、tags、remark，或单独 enabled；不能手填 platform_login_status/name/UID；标签全量替换原子保存 |
| PATCH / DELETE /api/v1/media-accounts/:id/profile | 绑定/解绑本人窗口，校验同平台占用；只改关联、不写/清 Cookie；使旧检查失效 |
| POST /api/v1/media-accounts/:id/check | 校验本人 Desktop 可用窗口，保存本次编号及窗口，返回 operation_id、bit_profile_id、platform、expected_platform_account_id |
| POST /api/v1/media-accounts/:id/check/result | operation_id、execution_status(completed/failed)、platform_*、check_items、message；失败不写旧登录结论；同 UID 刷新资料，异 UID 保存对照，不覆盖正式身份 |
| GET /api/v1/media-accounts/:id/credentials | 本人凭证原始输入与当前已确认值；无值返回空，不触发检查或本机读写 |
| POST /api/v1/media-accounts/:id/cookie-updates | input_cookie；校验账号/目标窗口，创建专用版本并返回本次目标，不直接外部写入 |
| PUT /api/v1/media-accounts/:id/cookie-updates/:operation_id/snapshot | 本机读取的目标平台写前值及占用核对；保存可校验的快照，确认后才允许写入；不可覆盖其他账号 |
| PUT /api/v1/media-accounts/:id/cookie-updates/:operation_id/result | 本次写入、身份、读回与明确/未知结果；成功时事务更新版本指针与账号；失败保留原引用，未知保留同一版本待核实 |
| GET /api/v1/media-accounts/:id/cookie-updates/:operation_id | 重新进入或响应丢失时读取本次结果；不得通过再次 POST 自动覆盖 |
| POST /api/v1/media-account-imports/preview | 平台、类目、标签、逐行 Cookie；仅校验并返回原行号、有效行与错误，不建正式资源 |
| POST /api/v1/media-account-imports | 确认有效行和批次属性后保存 batch/item/输入版本；客户端请求键唯一，重复提交返回原批次 |
| GET /api/v1/media-account-imports；GET /:id | 本人批次摘要与单项；七计数从六互斥状态聚合 |
| POST /api/v1/media-account-imports/:id/items/:item_id/start | 服务端决定单项可执行阶段及目标，返回本次编号；优先新建，复用须明确确认；不向旧已执行阶段签发新编号 |
| PUT /api/v1/media-account-imports/:id/items/:item_id/result | 按阶段回报创建窗口、占用核实、写前保留、写入、身份和正式账号保存结果；编号和阶段 CAS，不将创建账号视为成功 |
| POST /api/v1/media-account-imports/:id/items/:item_id/actions | action=skip/restore/retry/reconcile/reuse；只接受对应状态；restore 恢复原项，未知只能先 reconcile，不能直接 retry |

所有接口沿用 errcode/message/data/logid。Cookie 写入与批次为本人 Desktop 操作；管理员无凭证/本机入口。只保留当前必要编号和业务结果，不增加 sensitive permit 或通用 operation API。具体错误码由 Cloud 契约定义，包括 stale_check、identity_mismatch、profile_occupied、cookie_snapshot_failed、result_uncertain；普通错误不解析字符串决定状态。

### 2.3 关键请求、结算与恢复约定

- 列表标签参数统一为 tags 数组与 tag_match=any/all/exclude；未传不筛选。资料 PATCH 的 category_ids/tags 未传表示不变，传空数组表示清空；切换一级由最终二级 ID 集合校验。enabled 使用独立请求，避免编辑资料顺带改启停。新增仅支持 bilibili/baidu，不引入第三种运营接入方式。
- check 起始返回 operation_id、browser_profile_id、bit_profile_id、platform、expected_platform_account_id；回报 completed 时必须有明确平台结论，normal 必须有 UID；failed 只带原因/check_items，不要求伪造 UID。同 UID 更新昵称/头像，异 UID 写观测并返回 identity_mismatch；重复 UID 返回 existing_account_id 供定位，不覆盖已有账号。
- cookie-updates 起始及批次创建都传 request_key，按所属用户和业务目标去重；版本 operation_id 由 Cloud 生成并复用，不用 Cookie 明文作请求键。为版本增加 request_key 和唯一 `(account_id, request_key)`，避免单条提交重复创建。本人单条入口先完成窗口创建/绑定，已有账号更新必须明确该账号，不允许以空闲复用名义覆盖其他身份。
- 写前两阶段：Agent prepare → Cloud snapshot 持久化成功返回 snapshot_id（即该版本 ID）、can_apply=true → Agent apply。批次以 result 的 phase=prepared 回报同样的写前值与占用，Cloud 保存关联版本并返回同样许可字段；未收到该肯定响应不能开始写。result 的其他 phase 为 window_created/applied/verified，必须带 operation_id，Cloud 只接受当前阶段的单向推进，同阶段重复请求返回已有结算。
- 批次 start 返回 operation_id、phase、window_plan(create/reuse)、已知目标及该阶段所需输入。actions/reuse 带 candidate_profile_id 和显式确认，Cloud 与 Agent 分别复核正式关联与实际会话；仅创建明确失败且允许复用时可用。retry 只重试明确未成功的阶段；reconcile 只读核实，不能签发再次写入。人工完成登录后继续调用原项检查和结算。
- preview 每项返回 row_number、valid、reason_code/message；确认创建请求重新携带有效行内容及 request_key，服务端重新校验，不依赖一个长期预览会话。详情返回 item 的状态/阶段/原因/允许动作，以及 total/succeeded/failed/skipped/running/pending/uncertain；不为七计数新增接口。
- 普通成功响应代表本次阶段已完成，不等于整项已接入。uncertain 是业务状态且不显示成功 Toast；明确失败用红色反馈；检查未登录等有效平台结论不当成调用失败。不同窗口或旧编号回报返回冲突错误，不覆盖新结果。

## 3. Agent / Desktop 接口

Agent 提供 POST /api/v1/account-check，输入 profile_id/platform/expected_platform_account_id，返回目标平台实时观测及 check_items，失败用明确错误码，检查不调用 Cookie 写入/清理。

Cookie 执行新增专用 prepare/apply/inspect 本机能力：prepare 读取当前目标平台会话并核实占用；apply 要求已保存快照的本次编号与预期值，保持其他平台 Cookie；inspect 只核实当前实际结果。窗口创建复用现有 Profile 能力，必须可通过本次创建标识核实超时结果；无法确定时返回 uncertain，不能重新创建或转复用。目标路径及最小字段如下，正式契约先在 Agent 提供方落位，再更新 Desktop Rust DTO/命令和 Vue 调用。

| Agent 目标接口 | 最小输入与输出 |
| --- | --- |
| POST /api/v1/account-check（保留） | profile_id 是 BitBrowser ID，platform、expected_platform_account_id；返回现有 UID/name/avatar/login_status/check_items，明确区分平台结论与本机调用失败。Cloud 映射为 completed/failed，不把异常冒充未登录 |
| POST /api/v1/cookie-read（修改） | 增加必填 platform，按平台域读取；返回 cookies、source=live；失败返回错误，不返回存量值 |
| POST /api/v1/account-cookie/prepare（新增） | operation_id/profile_id/platform/expected_platform_account_id；返回实际占用、before_cookie、before_fingerprint。未识别/残留登录不能被当空闲 |
| POST /api/v1/account-cookie/apply（新增） | 本次编号、目标、input_cookie、已保存 snapshot_id/before_fingerprint；重新核对当前值和目标，匹配才写目标平台；返回 applied/failed/uncertain 及实际读回与身份；原会话变化则终止写入 |
| POST /api/v1/account-cookie/inspect（新增） | 本次编号、目标和预期身份/写入摘要；仅读取实际状态并返回核实结论，不重新写入 |
| POST /api/v1/bit-browser/profile-create（复用并扩展） | 公共创建请求增加本次创建标识；沿用返回 id，通过现有扫描能力核实超时结果。是否能可靠写入/检索创建标识须用 BitBrowser 实测，未确认不能宣称安全重试 |

上述编号只关联本次业务，Agent 不建持久化操作库。Cloud browser_profile_id 是数据库 ID，与本机 profile_id 不同，Cloud 起始响应显式提供 bit_profile_id，不由调用方猜测转换。

Cookie 实时读取使用 CDP；读取失败不得静默退回保存值并声称实时成功。可用于身份请求的保存值必须标明来源，实际登录仍以平台响应为准。只读检查不把未经读取验证的 Cookie 入库。B站、百度各自适配保持 Client/Service 分层，不在 Handler、Desktop 或 Vue 复制平台逻辑。

## 4. 批次与一致性

item 状态仅 pending/running/succeeded/failed/skipped/uncertain；人工登录、资料未同步、容量不足、身份冲突等用 phase/reason 表达。批量检查由前端对选中 ID 逐项调用检查接口并使用相同计数投影，但不保存独立长期检查历史表。批量 Cookie 持久化，逐项执行，关闭批量浮层后不再启动下一项，已发出项先结算或标记待确认；成功不重放、跳过可恢复、未知先核实。

同窗口的 Cookie 写入和冲突本机操作串行，执行前再次核对正式绑定与实际目标平台会话，不能仅靠前端禁用判断空闲。新建窗口、写 Cookie、Cloud 结算分阶段，外部不可和数据库共用事务。确认跨端结果后再建立正式关系；读回失败或响应丢失保存未知原因和目标，不释放后让其他项覆盖。

## 5. 清理与数据库执行边界

- 删除旧 AccountOpeningPage.vue、两端 /account-opening 路由和菜单，以及普通/高级运营差异的旧开户专用判断；批量入口回归社媒账号。
- 删除无真实消费者的 /account-groups、模型/Service/Repository/前端客户端和 media_account_groups 表；任务范围保留实际账号 ID，不建替代组中心。
- 删除独立 /identify 手填身份接口、资料更新中的平台身份/登录状态字段；检查结果为唯一识别写入口。标签接口收敛为账号 PATCH 的完整 tags。
- Cookie 版本完成后删除账号宽字段、旧 cookies/read-sync 接口和把保存值当实时值的路径；更新真实消费者，不做永久转发别名。
- 旧迁移是顺序建库链，不改写已执行历史；追加新迁移做字段/索引/表变更。未上线业务无需兼容回填；不以此删除共享 users/categories/browser_profiles/proxies，更不操作真实 BitBrowser。实际执行数据库迁移前核对目标环境与账号行及跨模块引用，不把“未使用”推导为可任意删库。
- 旧原型不复制多版本到仓库；example/proto/social-accounts/index.html 是唯一当前入口。旧决策引用迁移、PRD 重复正文合并后按治理规范清理，已归档证据不改写。

## 6. 验证

每个闭环定向验证 Cloud Repository/Service/Handler 与契约、Vue 行为及构建、Agent 本机响应、Desktop DTO；涉及并发的编号/阶段 CAS、快照保护和批次幂等必须有反例测试。真实验收先使用明确授权测试账号分别验证人工登录识别、只读 Cookie、写入及跨平台隔离，不对任意已有账号执行批量操作。原型测试和模拟 HTTP 不代替真实数据库/BitBrowser/平台验收。
