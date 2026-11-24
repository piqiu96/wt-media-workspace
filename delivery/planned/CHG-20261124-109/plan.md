# CHG109执行落地清单：发布计划推进与结束

## 交付结果与范围

依赖[108](../CHG-20261124-108/plan.md)，复用[107配置](../../completed/CHG-20261124-107/plan.md)。计划设置平台×类目目标并拆有序批次，创建只保存计划/批次骨架，零任务零占用；全部待执行批次准备完成后首次明确启动计划，同时冻结计划及全部批次配置；后续按顺序对冻结配置调用108创建任务/占用/执行。首期百度，后续平台按开放能力验收。

批次只选本人账号，不建设跨用户授权接口或审批系统。本人计划范围仍按既有review边界；如要求团队共同执行，须另明确产品范围，不能以管理身份远程授权。计划不追加批次、不提供补量，执行后的缺口保留，追加发布另建独立批次或新计划。计划10%衔接规则仍按现有PRD；批内自动继续不等于计划可以绕过人工/未知进入下一批。

## 执行约定

本文件是2026-11-25最新实施review稿，与change.md配套；状态只在change.md，用户已授权全流程执行，当前PLANNED，按依赖逐项激活。任务按顺序执行，勾选表示需检查的交付项，不预填完成事实。依赖CHG归档、各仓合入main、范围review及CHG预检满足后才开始运行代码。路径由config/repository-map.yaml定位。

产品以PRD第六章、对应Milestone及本次已确认裁定为准；页面继承Cloud既有publishing-design原型，公共布局/行为/Token分别遵循AdminUI、交互和视觉规范。原型查阅基线ac29c1a7cefaace40501c61a10bb618309b39002尚不是本轮视觉签收；补齐新场景、review并固定SHA后再实施正式页面。

Cloud内部按Handler→Service→Repository落位，跨模块复用所属Service；共用Vue只在Cloud维护，Agent管本机，Desktop管桥。正式OpenAPI/枚举/错误码由提供方维护，本稿API字段是定版输入，不是第二份可写契约。接口省略/api/v1；session/AgentToken/本地受信身份按调用链区分。ID/revision字符串、RFC3339时间，沿用errcode/message/data/logid；查询先授权再分页聚合。保存用revision，创建/启动用请求键与服务端摘要防重，同键异输入拒绝；结果未知先查询原结果，不换键重试。

每步交付填写：修改文件/对应功能与API/实际验证命令和结果/PR或commit/未验收边界。多仓提供方先行，消费生成及Desktop契约锁同步；净差异review通过再按CHG独立PR合入main，用户验收后才关闭。文档检查不代替运行测试，模拟不代替真实平台验收。

## 1. 业务、页面与API对应

| 功能 | 页面/用户结果 | API |
| --- | --- | --- |
| P01 列表/复制/保存 | PlanList/Workbench；名称/周期/备注与可搜索平台类目 | A01/02/03/04/16 |
| P02 目标与拆批 | PlanGoalScope；平台×类目矩阵，手工拆合排序或AI建议 | A04/05/06 |
| P03 启动前准备 | 去配置复用107，全部待执行批次准备完整，继承目标只读，保存不占用 | 107 A02/A10及资源/工具接口 |
| P04 首次启动 | 全部待执行批次配置完整，当前合法首批可启动；成功同时冻结计划及全部批次配置 | A09 |
| P05 顺序推进 | 计划详情显示当前位置、资源/异常/阈值等待原因 | A02/07/08、内部Scheduler |
| P06 暂停/恢复/接管 | 暂停后续批、恢复重检；当前批合法接管 | A10/11/13 |
| P07 阈值/跳过 | 超10%确认继续，零明确结果确认跳过 | A12 |
| P08 最终核实 | 原任务核实，按平台×类目展示真实公开数与缺口，不在原计划补量 | 108核实接口及A02/15 |
| P09 结束/终止 | 达成或说明未达成原因结束；终止全计划安全收尾 | A15/17 |

计划详情分基础信息、目标矩阵、批次推进、待办、记录；只读批次Drawer铺满内容区但保留菜单/顶栏，关闭恢复位置。每个批次提供与独立批次相同的快捷操作按钮，名称/权限/状态条件/确认及API共用；受计划冻结/位置约束，不能绕过计划。任务处置进入原批次/任务，不复制第二套表单。处理后仍按10%/零分母/未决及人工暂停等原规则推进，不要求无异常批次逐批人工确认。新建/编辑/复制不新增“确认批次”；候选没有正式任务身份，不能用旧task IDs做计划授权。

## 2. API实施清单

| 编号/变更 | 方法/路径 | 输入→返回；副作用/限制 |
| --- | --- | --- |
| A01 新增 | GET /publication-plan | 搜索/状态/平台/类目/分页或request_key→列表/精确找回 |
| A02 新增 | GET /publication-plan/{id} | id→基础/目标矩阵/当前进展/批次汇总/待办/允许动作/revision |
| A03 新增 | POST /publication-plan | request_key/name/周期/note/goals/batches→plan/骨架IDs/revision；一次事务零task/占用 |
| A04 新增 | PUT /publication-plan/{id}/structure | expected_revision/基础/goals/稳定批次ID及顺序→新revision/骨架；仅计划首次启动前逐格守恒，继承目标改变时受影响内容重新检查；启动后禁止新增/删除/重排/修改 |
| A05 新增 | POST /publication-plan/recommend | goals/授权资源事实/现有安排/本次要求→SSE真实AI拆批建议；不自动保存，不以算法冒充AI |
| A06 新增 | POST /publication-plan/validate | 完整新建或拟编辑结构/revision→守恒/合法顺序/逐格问题；只读 |
| A07 新增 | GET /publication-plan/{id}/batch | 状态/待办/分页→有序骨架/配置批次/正式批次及对应allowed_actions/action_blockers |
| A08 新增 | GET /publication-plan/{id}/record | 分页→人工/系统操作与推进依据 |
| A09 新增 | POST /publication-plan/{id}/start | request_key/expected_revision/合法首批/全部待执行批次expected_revision及明确范围与缺口→计划位置/首批tasks/控制；复查全部配置后冻结，内部调用108同一启动器 |
| A10 新增 | POST /publication-plan/{id}/pause | expected_revision/reason→人工暂停后续批，当前批已授权执行继续 |
| A11 新增 | POST /publication-plan/{id}/resume | expected_revision→实际控制/进展/阻断；重新检查，不默默解除批次自身异常暂停 |
| A12 新增 | POST /publication-plan/{id}/confirm-next | request_key/expected_revision/当前批/下一批/continue或skip/reason→位置/修订；未决执行、位置变化、下一批资源冲突拒绝 |
| A13 新增 | POST /publication-plan/{id}/takeover | expected_revision/current_batch_id/expected_batch_revision/reason→计划暂停/本批合法授权；只本人当前合法位置 |
| A15 新增 | POST /publication-plan/{id}/finish | expected_revision/逐格缺口/end_reason/end_note→ended/真实结果；未达成须说明，结束后不重开 |
| A16 新增 | GET /publication-plan/{id}/copy | expected_revision→目标/拆批等白名单；新周期/资源重查，新键，无任务/占用/授权继承 |
| A17 新增 | POST /publication-plan/{id}/cancel | expected_revision/reason→全计划停止围栏/影响范围/收尾状态；覆盖骨架与全部批次 |
| L01/02/03 扩展 | GET/PUT/DELETE /publication-draft/plan | 受信本人/expected_revision/未提交payload→原输入/新revision；沿已有本地续编，无新Cloud草稿表 |

复用107保存配置、108start/pause/resume/stop/核实。撤除补量A14及旧稿独立resource/confirm、batch/confirm、跨成员authorize等新增接口意图，不更改任何已在用的既有路由。自动推进只调用内部Service，不设公共自动推进API。

## 3. 数据、推进与一致性

- 新建publication_plan：身份/团队/本人owner与created_by、名称/周期/备注、goals_json、status/pause_reason/current_batch_id、首次启动/停止/结束时间、end_reason/note、revision、request_key/hash。UNIQUE(created_by,request_key)，team/owner+时间、status+id索引。
- 先建plan再扩batch.plan_id/FK、平台组/批次顺序、handoff依据；不建补量类型/轮次/请求关联。旧独立batch保持plan_id=NULL；task不冗余plan_id，通过batch关联。
- 创建plan/全部骨架/审计同事务，无task/占用。启动调用108统一事务：当前plan及全部所属batch按固定顺序锁定，复查全部待执行批次配置及修订并冻结；首批候选定版、全部task/占用/授权、首次时间/当前位置和审计同一事务提交。不可先授权任务再写计划游标。
- 首次启动后计划目标/结构及全部所属批次候选、资源、内容、时间与执行设置固定，暂停不解锁；107 configuration及任务content写入口均校验父计划冻结，不因本批尚未启动而开放编辑。保留原批次的继续/安全重试/核实/终止等执行处理。计划内顺序启动；批内分组并发；不同计划/批次共用全局UID/Profile/用户容量。
- 推进检查：停止/结束→人工暂停→当前批未决与失败处置→零明确结果跳过确认→超10%继续确认→下一批配置/资源/本人条件→原子调用108启动并推进。等待原资源恢复仍running；不自动换视频或降低目标，不跳过不就绪批。
- 10%计算沿PRD：failed*10 <= published+reviewing+failed可自动衔接；取消/放弃不计分母，审核只参与明确结果不计公开目标。失败明确接受结束后仍failed保留分子；未知/人工不能靠确认绕过。原批handoff后不能再次retry回头发稿。
- 全计划终止先持久化父级永久围栏，所有批次/单任务start/retry/claim立即受限，再安全取消未领取和收尾在途；单批终止不误停整个计划。
- 全部既有批次处理完、最终公开结果核实后，按平台×类目展示逐格公开数与缺口；平台A超额不能抵消B缺口。原目标不变，不向原计划追加批次或补量。
- finish用计划锁/当前revision/真实未决及公开聚合，达成结束或填写原因未达成结束。迟到公开只更新统计/提示合法处置，不静默删正式任务、不重开结束计划。

## 4. 执行落地步骤

- [ ] T01 产品/Workspace：确认本人计划范围、全部批次启动前准备/启动后冻结、不追加补量、保留10%推进及批次同名快捷操作与最终结束边界，回写正式事实和固定原型SHA；团队协作若提出则独立明确，不能隐式扩权。
- [ ] T02 Cloud契约：定版A01–13、A15–17与plan续编类型（A14补量草案撤除，其他编号不重排）；去除旧confirm/跨成员authorize意图，公布版本/消费生成/锁同步。
- [ ] T03 Cloud迁移：plan表→batch关联/顺序/配置冻结；旧独立批次/快速任务兼容。产物：真MySQL迁移/守恒/原子骨架证据。
- [ ] T04 Cloud Service：目标校验、真实AI建议、结构编辑/查询/复制；复用107候选准备，未启动不占成片。
- [ ] T05 Cloud推进Service/Scheduler：复用108启动事务与本人权限，首次启动/按序推进/暂停恢复/确认接管/终止；多实例不重复。
- [ ] T06 Cloud结果Service：最终核实/逐格缺口/结束原因及迟到结果；不新建统计事实表。
- [ ] T07 共用Vue/Agent/Desktop：计划页面、批次同名快捷操作/只读Drawer和上下文返回、本机plan新建续编；不复制浏览器执行器，不另造授权系统。
- [ ] T08 联调/独立review：真实多批顺序、资源竞争、阈值/暂停/配置冻结/结束，Web和安装版固定原型验收。
- [ ] T09 各仓交付：真实命令/结果、PR/main merge证据、用户签收后归档；计划阶段不能宣称其他平台已开放。

## 5. 验收与证据

- [ ] V01 目标逐格守恒、创建仅plan/batch、零task/占用；编辑保存与同键响应丢失不遗留半计划。
- [ ] V02 任一待执行批次配置不完整禁止启动；成功同时冻结计划及全部批次，暂停仍禁止改配置/增删重排；首批资源冲突全回滚，后续批资源被占则等待，不自动少发/替换。
- [ ] V03 9成功+1失败=10%、8成功+2失败=20%、零分母/人工/未知边界；审核不计公开目标。
- [ ] V04 批内自动继续不越过计划未决门槛；计划恢复不解除批次异常暂停，资源恢复不解除人工暂停；无异常且满足阈值批次自动推进，不逐批人工确认。
- [ ] V05 自动/人工/重复确认/多实例重启只推进一次，旧位置/旧revision拒绝；已移交批不能旁路retry。
- [ ] V06 单批停止与全计划终止作用范围准确；全部骨架受围栏，已提交按真实结果收尾。
- [ ] V07 本人账号与其他用户负例；session替换保ReportSafe，不新增工作；无跨用户授权接口。
- [ ] V08 逐格缺口、原目标不变；无计划内补量API/数据字段/入口，不能通过结构或配置写入口旁路追加；迟到公开不重开/重复推进。
- [ ] V09 达成、未达成原因结束、终止结束可查；公开/失败/待办与task/attempt/作品可核对。
- [ ] V10 固定原型、目标矩阵、批次快捷按钮与独立批次名称/权限/条件/API一致、只读批次Drawer、返回/筛选/滚动、三角色与Web/安装版，记录真实场景证据。

## 事实源

- [PRD第六章](../../../docs/product/prd/详细文档/第六章_发布管理.md)
- [发布工程设计](../../../docs/engineering/specs/publishing-management.md)
- [前端规范](../../../docs/standards/frontend/README.md)
- [设计入口](../../../docs/design/publishing.md)
