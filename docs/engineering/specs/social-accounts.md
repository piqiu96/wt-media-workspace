# 社媒账号：数据、接口与本机执行

产品规则唯一正文为[第三章 §3.3](../../product/prd/详细文档/第三章_用户与账号管理.md#33-社媒账号管理)，交互为[当前原型](../../../example/proto/social-accounts/index.html)，取舍见[ADR-0030](../../decisions/0030-social-account-rebuild.md)。本文定义目标工程设计；实施及验收状态归 Delivery，不以文档存在声明已上线。正式 OpenAPI、Schema 和 DTO 由提供方仓库维护。

## 1. 数据归属与六张领域表

Cloud 保存正式业务数据，Agent 不落账号/Cookie/批次业务库；Desktop 只桥接。复用 users、categories、browser_profiles、proxies；不新建用户、层级类目、窗口或代理模型。ID 延续现有 BIGINT，API 沿用对应领域的 ID 表达，不额外改名。

| 表 | 核心字段与责任 | 索引/约束 |
| --- | --- | --- |
| media_accounts | id、user_id、team_id、platform、platform_account_id/name/avatar_url、browser_profile_id、enabled、remark；identification_status/duplicate_of_account_id；platform_login_status；last_check_at/items/status/message/identity；check_operation_id/started_at/profile_id；initial_cookie_version_id/current_cookie_version_id；时间 | 唯一 user_id+platform+platform_account_id（待识别 UID 为 NULL）；唯一 browser_profile_id+platform（未绑定为 NULL）；user_id+platform、team_id 索引 |
| media_account_categories | media_account_id、category_id | 复合主键；关联已启用且适用归属用户的类目，多选同 type；不存冗余一级名称 |
| media_account_tags | media_account_id、tag_name、created_at | 复合主键；不建全局标签字典 |
| media_account_cookie_versions | id、account_id（接入未识别前可空）、import_item_id（可空）、platform、browser_profile_id、operation_id、previous_version_id、purpose、state、input_cookie、before_cookie、confirmed_cookie、created_at/confirmed_at | operation_id 唯一；account_id+id、import_item_id 索引；状态 prepared/applied/confirmed/rejected/uncertain；purpose import/update/readback；凭证值不进入普通账号响应 |
| media_account_import_batches | id、user_id、request_key、platform、category_ids_json、tags_json、remark、created_at/updated_at | 唯一 user_id+request_key；user_id+created_at；统计由 item 聚合，不存七套可漂移计数 |
| media_account_import_items | id、batch_id、row_number、account_id、browser_profile_id、cookie_version_id、status、phase、reason_code/message、operation_id、resume_status、window_plan、reuse_confirmed、created_bit_profile_id、updated_at | 唯一 batch_id+row_number；operation_id 唯一；batch_id+status；窗口创建及 Cookie 写入分别记录当前阶段/回执，未知阶段不可重放 |

检查运行状态 never/running/completed/failed；last_check_identity 保存本次观测 UID/name/avatar，供身份对照，不替换正式 UID。last_check_at 表示最近取得结论时间，失败只更新执行状态/原因。check_operation_id 与 check_profile_id 绑定本次目标，结果必须匹配当前编号、归属和窗口；同编号已结算返回现有结果，旧编号拒绝，避免迟到结果覆盖。

账号资料更新、标签替换及类目关系更新在一个 Cloud 事务内完成。检查起始/结算通过 Repository 的专用带条件更新，避免用整行旧记录回写覆盖 Cookie、备注或窗口变更。绑定变化使未结算旧检查失效；移除分类不影响登录检查。

Cookie 版本只服务防误覆盖与本次未完成处理，保留初始、当前、最近写前值和未收敛引用；不向运营开放版本浏览。仅在新结果已确认且无引用时清理被替代中间值；本期不引入定时保留策略、审计报表或备份中心。账号表不再保存 original_cookie/active_cookie/login_password/sms_receive_* 等旧流程字段。

## 2. Cloud API 目录

| 接口 | 输入/输出与业务结果 |
| --- | --- |
| GET /api/v1/media-accounts | search、platform、enabled、platform_login_status、category_type、category_ids、标签组合、user_id、team_id、profile_search；服务端按角色收窄；响应含归属名称与当前检查状态，不含凭证 |
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

## 3. Agent / Desktop 接口

Agent 提供 POST /api/v1/account-check，输入 profile_id/platform/expected_platform_account_id，返回目标平台实时观测及 check_items，失败用明确错误码，检查不调用 Cookie 写入/清理。

Cookie 执行新增专用 prepare/apply/inspect 本机能力：prepare 读取当前目标平台会话并核实占用；apply 要求已保存快照的本次编号与预期值，保持其他平台 Cookie；inspect 只核实当前实际结果。窗口创建复用现有 Profile 能力，必须可通过本次创建标识核实超时结果；无法确定时返回 uncertain，不能重新创建或转复用。正式路径、DTO、错误码在 Agent 提供方契约先定义，再更新 Desktop Rust DTO/命令和 Vue 调用。

Cookie 实时读取使用 CDP；读取失败不得静默退回保存值并声称实时成功。可用于身份请求的保存值必须标明来源，实际登录仍以平台响应为准。只读检查不把未经读取验证的 Cookie 入库。B站、百度各自适配保持 Client/Service 分层，不在 Handler、Desktop 或 Vue 复制平台逻辑。

## 4. 批次与一致性

item 状态仅 pending/running/succeeded/failed/skipped/uncertain；人工登录、资料未同步、容量不足、身份冲突等用 phase/reason 表达。检查批量使用相同计数投影，但不保存独立长期检查历史表。批量 Cookie 持久化，逐项执行，关闭窗口可暂停；成功不重放、跳过可恢复、未知先核实。

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
