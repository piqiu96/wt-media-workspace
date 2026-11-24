# CHG108执行落地清单：批次启动、分组发布与结果

## 交付结果与范围

依赖[107](../../completed/CHG-20261124-107/plan.md)。本人批次开始发布时才生成正式任务、取得成片占用并授权；按组并行，组内不加间隔，组自动处理结束后等待发布间隔再安排下一组。支持组间处理【自动继续、异常暂停】、异常任务上限，以及人工继续/终止。真实公开统计与待办分开。

## 执行约定

本文件是2026-11-25最新实施review稿，与change.md配套；状态只在change.md，用户已授权全流程执行，当前技术交付DONE，107四仓main基线已确认。任务按顺序执行，勾选表示已完成并有证据的交付项。依赖CHG归档、各仓合入main、范围review及CHG预检满足后才开始运行代码。路径由config/repository-map.yaml定位。

产品以PRD第六章、对应Milestone及本次已确认裁定为准；页面继承Cloud既有publishing-design原型，公共布局/行为/Token分别遵循AdminUI、交互和视觉规范。原型输入为Cloud main60847fdeda19ef4d889de3ded3be2e9521ba6d93下web/example/proto/publishing-design（BatchManager、BatchDetailContent、PublishComposer、batchLifecycle等）及web/example/common；用户再次明确必须参考example。T01先核对组间/异常/终止与最新启动语义，固定108原型SHA后再实施正式页面，不从零另造交互。

Cloud内部按Handler→Service→Repository落位，跨模块复用所属Service；共用Vue只在Cloud维护，Agent管本机，Desktop管桥。正式OpenAPI/枚举/错误码由提供方维护，本稿API字段是定版输入，不是第二份可写契约。接口省略/api/v1；session/AgentToken/本地受信身份按调用链区分。ID/revision字符串、RFC3339时间，沿用errcode/message/data/logid；查询先授权再分页聚合。保存用revision，创建/启动用请求键与服务端摘要防重，同键异输入拒绝；结果未知先查询原结果，不换键重试。

每步交付填写：修改文件/对应功能与API/实际验证命令和结果/PR或commit/未验收边界。多仓提供方先行，消费生成及Desktop契约锁同步；净差异review通过再按CHG独立PR合入main，完成技术交付后归档，用户按已授权安排在107–109后统一整体验收。文档检查不代替运行测试，模拟不代替真实平台验收。

## 1. 业务与API对应

| 功能 | 用户结果 | API |
| --- | --- | --- |
| E01 最终检查/启动 | 逐行冲突/缺口明确确认，一次形成正式任务；失败仍保留配置 | A01/02 |
| E02 分组发布 | 每组最多N个本人不同账号，组间等待；最后不足N也运行 | A08/09/10 |
| E03 异常处理 | 先跑可自动处理任务；组间策略和异常上限控制暂停 | A03/04，A09/10 |
| E04 共享环境 | 同UID串行，同实际Profile跨平台/批次互斥，忙则等待 | A08；107详情/任务A07 |
| E05 集中处理 | 原现场人工继续、核实原稿、安全重试或放弃 | A11–17、L01/02 |
| E06 终止/结束 | 停新派发、在途收尾；失败可决定重试或结束本批，未知不强改终态 | A05/06 |
| E07 可信结果 | task/attempt/作品对应，审核不算公开成功 | A07/18/19及107详情/记录 |

新建“创建并发布”在页面一次点击编排107保存→本CHGstart；编辑“开始发布”保存最新修改后启动，复用原batch ID。保存成功、start失败明确显示已保存未开始，不能重复创建或宣称已执行。启动后整批候选结构固定，单任务合法内容编辑仍沿M6状态条件。

## 2. API实施清单

| 编号/变更 | 方法/路径 | 输入→输出；关键副作用 |
| --- | --- | --- |
| A01 新增 | POST /publication-batch/{id}/execution-preview | expected_revision/拟包含row_keys→逐行资源/内容/本人环境问题、缺口；只读 |
| A02 新增 | POST /publication-batch/{id}/start | request_key/expected_revision/included_row_keys/excluded_row_keys/allow_shortfall/expected_shortfalls→task_ids/控制/首次时间/新revision；首次一次事务建task/占用/授权，重试同键找回 |
| A03 新增 | POST /publication-batch/{id}/pause | expected_revision/reason→暂停状态；人工暂停后续派发，已开始仍收尾 |
| A04 新增 | POST /publication-batch/{id}/resume | request_key/expected_revision/expected_pause_id/acknowledged_exception_ids及修订→继续或实际阻断；确认当前问题，不清历史 |
| A05 新增 | POST /publication-batch/{id}/stop | expected_revision/reason→停止围栏/在途与未领数量；执行前无task可终止batch，执行后未领取消并保留占用 |
| A06 review动作 | POST /publication-batch/{id}/finish | expected_revision/失败任务集合修订/reason→结束摘要；无未决执行，保留failed和占用、关闭本批重试，不自动abandon |
| A07 新增 | GET /publication-batch/{id}/task | 账号/状态/搜索/分页→正式任务/阶段/阻断；未启动返回正式task为空，候选从batch详情读取 |
| A08 扩展 | POST /cloud-agent/publication-task/claim | 原领取键/Token→原task/attempt/文件授权；同事务检查父级/当前组/用户容量/UID/Profile |
| A09 扩展 | POST /cloud-agent/publication-task/{id}/report | 原attempt/seq/阶段或心跳→停止/提交许可/状态；保活不改业务revision，停止后不授新提交 |
| A10 扩展 | POST /cloud-agent/publication-task/{id}/complete | 原attempt/seq/result_hash/result/evidence→原结果确认；去重结算，不重开已停/结束批次 |
| A11 扩展 | POST /publication/{id}/retry | 既有原attempt/revision→原任务合法重试；只本人、父批/计划允许、安全旧执行结束 |
| A12 复用并补父级 | POST /publication/{id}/resolve | 原attempt/revision/结论/依据，公开需真实作品与时间→状态/作品；原结果不覆写 |
| A13 复用 | POST /publication/{id}/abandon | 原attempt/revision/无发布可能且现场结束依据→安全释放；不把失败自动放弃 |
| A14 复用 | GET /cloud-agent/publication-task/{id}/attempt/{attempt_id}/scene | 受权本人原attempt→原现场资格；不打开替代窗口 |
| A15 扩展 | POST /cloud-agent/publication-task/{id}/resume | 原attempt/revision→原调用继续；重获自动执行名额、复查批次控制，不新建attempt |
| A16 复用并协同互斥 | POST /cloud-agent/publication-task/check/claim | 原核验领取→指定原稿/revision/generation；浏览器核验同Profile互斥 |
| A17 复用 | POST /cloud-agent/publication-task/{id}/check | 原代次/attempt/观察→核验确认；observation/公开作品/任务/审计同事务 |
| A18 复用 | GET /publication/{id} | 原任务详情/允许动作/阻断 |
| A19 复用 | GET /publication/{id}/attempt | 原尝试及固定输入/结果；旧attempt只可追溯，不覆盖当前 |
| A20 扩展 | PUT /publication/{id}/content | 原修订/content/not_before→合法单任务内容修改；未授权pending且父级允许；109接入后，所属计划已启动禁止修改内容/时间 |
| A21 扩展 | POST /publication/{id}/start | 原修订→任务授权；不能绕过批次当前组/暂停/停止/计划位置 |
| A22 扩展 | POST /publication/{id}/cancel | 原修订/reason→原任务取消或安全停止请求；保留既有安全边界 |
| L01/02 复用 | POST /publication-run/{attempt_id}/scene、/resume | Desktop受控原现场展示/继续；绑定本人/原attempt/修订 |

作品查看复用GET /work、/work/summary、/work/{id}；原attempt读取与文件续签沿现有ReportSafe/快照授权接口。批次统计复用107详情/record，不另建可写成功数API。系统组间/上限暂停由内部Service调用，与人工pause/resume共用业务内核。

## 3. 数据、分组与安全边界

- 本CHG迁移task.batch_id/task_order及稳定row_key关联，快速任务batch_id=NULL；UNIQUE(batch_id,task_order)，(batch_id,status,id)索引。排序从107冻结候选写入，只代表优先安排，不保证网络下完成顺序。
- batch补first_started_at、当前execution_group_no/当前组任务集合、group_ended_at/next_group_at、paused状态/pause_id/原因/已确认异常范围、永久停止/结束依据。并发、间隔、策略/上限读取107保存的一份设置，首次成功启动冻结。
- task/attempt记录执行组号便于重启恢复与重试追溯；组间隔按当前组自动操作全部结束或可靠挂起后计算，不按相邻领取时间。组内选不同UID/Profile的就绪任务，资源等待不凑满死等、不提前占attempt。
- 首次start：事务外核实外部文件/内容→事务内固定顺序复查batch revision/本人资源/封面/缺口→全部task/正式引用/成片唯一占用/授权/审计一次提交。循环调用独立事务的单任务Create不允许。后续重放返回原任务集合，不再次建单。
- 失败/安全结束后的reviewing可结束本轮自动步骤；awaiting_human需证实原控制已挂起才退出自动执行组，但task仍待人工、Profile仍占用。失联且旧执行可能运行时不能当作已挂起，也不能靠超时释放。
- 自动执行名额与环境占位分开：可靠挂起不继续自动操作，可让其他独立环境运行；仍存活的人工窗口/未知现场计入有限本机容量，容量满则明确等待。Cloud用户slot生成列与Agent控制要共同改造，不能只把3改5或仅凭task状态释放。具体名额与窗口容量初值在实现实测后配置，不增加运营必须理解的内部参数。
- 108共同技术定义：发布域新增实际Profile使用记录（BitBrowser主账号+实际Profile唯一），持有人是原attempt或原核验代次；与领取同事务，不靠TTL释放。核验领取增加原请求键找回，正常观察过期时仍能仅以原身份和可信关闭证明释放本代占位，不改旧任务/作品、不释放后继占位。旧活动尝试保守回填自动名额及窗口，不因awaiting_human文字释放。
- 可靠挂起信号绑定原attempt/序号和提交前原控制等待点；本机登记原活现场并停止业务动作后报告，Cloud确认后才释放自动名额。自动并行5/保留窗口10仅为本轮受控验证初值，两端部署/本机配置共同收窄，真实少于N按现有Profile运行；不新增运营表单参数。
- 人工继续原attempt先原子取得自动执行名额、检查父级/本人/现场/输入再恢复原调用；不能把挂起视为已提交/已失败，也不重新上传。浏览器核验也纳入同一实际Profile互斥，不能依赖旧串行循环偶然避免冲突。
- 异常任务=当前failed/awaiting_human/uncertain按task去重，reviewing不计。每组结束按策略检查，达到上限立即封后续派发，不粗暴终止已开始任务。人工继续确认pause_id/异常范围，不清历史；同一已确认范围不重复触发，新异常或异常依据变化重新检查，旧确认不可放行新问题。
- UID/Profile跨批全局互斥，账号/环境占用直到有证据安全释放；成片占用独立，取消/停止仍保留，仅合法安全放弃释放。原attempt/observation/work事实复用，不在本CHG删核验表。
- 全批自动跑过但仍有人工/未知时显示待处理，不显示业务已全部完成；失败可重试或明确结束本批，未决不能强行结束。暂停可继续；终止不可恢复，原结果仍可补报/核实。

## 4. 执行落地步骤

- [x] T01 产品/Workspace：更新分组、异常暂停/继续、失败结束和本人范围的PRD/M7/原型动作；冻结视觉SHA，明确组号非计划批次号。
- [x] T02 Cloud提供方：定版启动/暂停/继续/停止和原执行接口扩展；增加paused枚举/错误，发布契约，消费生成与Desktop锁同步。
- [x] T03 Cloud迁移/repository：task关联、组状态、暂停依据、执行名额与Profile占位分离；验证旧未决记录不被静默释放。
- [x] T04 Cloud Service：start一次建单/占用/授权，组候选选择、间隔、策略/上限、暂停与人工继续；所有单任务入口受父级控制。
- [x] T05 Agent runner：单阻塞run改有界独立执行，分组领取；心跳/补报/停止独立，SQLite/Playwright上下文不跨不支持的线程共享。
- [x] T06 Agent场景：可靠挂起与恢复准入、慢代理/上传阶段截止、核验协调；代理失败不自动直连，不无限开窗或重放点击。
- [x] T07 共用Vue/Desktop：接107一次点击保存后启动、组进度/待办、固定配置文案、暂停原因和继续/终止；本机桥有字段变化才扩展。
- [x] T08 联调：按V清单跑正常/故障/并发，并按当前本人Profile向下兼容完成真实发布；跨平台互斥定向证据与开放平台实发分别记录。
- [x] T09 独立review与交付：净差异、各仓PR/main merge与技术交付证据；用户已指定107–109后统一整体验收，不在此逐项重复要求签收。完成后为109提供依赖。

## 5. 验收与证据

- [x] V01 保存零任务/零占用，首次start一次生成N条，重复/并发/响应丢失同键找回；一条冲突全回滚并保留配置。
- [x] V02 每组并发N不同账号，组内无额外间隔；组处理结束后等待配置间隔；重启不提前启动下一组。
- [x] V03 同UID多窗口、跨批/跨平台同Profile争用只一方执行；等待不生成空attempt，其他独立环境可运行。
- [x] V04 慢启动/上传、可靠人工挂起与未知失联分别测试；挂起后其他环境继续，未证明停止不释放；全部容量占满正确等待。
- [x] V05 自动继续/异常暂停两模式，60条达到上限暂停；失败/人工/未知按task去重，reviewing不计，attempt不增数量。
- [x] V06 继续旧pause_id/旧修订/新增异常竞争拒绝；历史不清、同一已确认异常不反复暂停，终止不恢复原队列。
- [x] V07 人工继续仍原attempt/输入/现场；场景丢失或提交后不重新开窗/上传，必须先重获名额。
- [x] V08 停止与领取/提交许可竞争，原结果outbox重启/迟到补报去重；单任务start/retry不能绕过暂停/停止或计划位置。
- [x] V09 本人账号正例/他人负例；真实公开task/attempt/work一致，30目标/28task/24公开=80%，审核不算公开。
- [x] V10 失败重试/明确结束、取消保留占用、安全放弃才释放；未知/人工不能当失败强制结束。
- [x] V11 固定原型、三角色、Web与安装版；真实公开/故障模拟/未开放平台证据分别说明，实际出口与容量未经验证不宣称通过。

## 事实源

- [PRD第六章](../../../docs/product/prd/详细文档/第六章_发布管理.md)
- [发布工程设计](../../../docs/engineering/specs/publishing-management.md)
- [前端规范](../../../docs/standards/frontend/README.md)
- [设计入口](../../../docs/design/publishing.md)

T01原型已固定2512d342，逐页映射在Cloud web/example/proto/publishing-design/README.md。T02提供方初稿c930789与限定修复1113f8d已提交；协调升级按ADR-0037执行，原键仅结算/取消围栏、明确scene_parked反馈及一致关闭证据纳入正式契约。Cloud实现7b4f523通过Go全套与隔离MySQL发布/图片回归，Go独立源码审查无P1/P2；共用Vue修复至89f49b6、1212项通过，有限复审已关闭。Agent并发和恢复已实现，0d507e1完整949项与独立限定复审通过；实际旧核验安全切换及最新完整wt chg verify通过。真实本人单Profile已完成一次投稿并由原核验公开为work5，实际发现的ended后统计刷新已修并独立复审；最终fe741fe新包与Web均已读回1/60·1.67%、待公开0和原任务。V01–V11证据范围与受控/实际差别见evidence/acceptance-matrix.md。


## 当前可用环境与证据口径

用户已确认不足配置N时按现有Profile向下兼容。本机现有可用本人百度账号及独立Profile为1；真实发布验收按配置并发5、实际group1成员1执行，不能表述为真实5账号并发。多Profile、60任务、慢流、原线程停车/恢复及停止竞争使用隔离MySQL/SQLite/真实线程与socket受控验证，分别标识。未开放平台与Windows不记为实际通过；三角色界面以受控角色场景、本人运营以实际两端验证。最终验收表须逐项列明这一区别，不将模拟请求或目标60当成60次真实投稿。


PR51复审补义：A02恢复必须通过原key和完全原包取得immutable首启回执，不能凭当前row_keys推定原请求已成功。CloudAPI 2026.11.25.3仅在持久另一first-start key与完整合法回执证明本请求未获执行时，提供`start_request_applied:false`；其他409不具备该证明。Cloud-Agent和错误码仍2026.11.25.2。派发候选和实际queued领取均须越过无可选工作的旧候选，不能让固定扫描上限阻塞后续独立环境，继续由原事务裁决Profile和容量。
