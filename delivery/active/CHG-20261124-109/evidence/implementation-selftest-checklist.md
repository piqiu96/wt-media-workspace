# CHG109 完整编码与自测收口清单

2026-11-25 用户再次明确：当前批次/计划视觉与原型差异大，须参考现有原型实现代码；按 PRD、工程设计及执行清单完成全部编码和自测后，才进行真实 E2E，最后 UI 走查。此前截图/受控浏览器属于开发验证，不是最终 UI 验收。本清单是本 CHG 编码自测证据索引，不新增 Delivery 状态系统。

## 输入与顺序

- PRD 第六章 §6.2/6.3/6.8：字段、状态、业务能力、角色及续编。
- `docs/engineering/specs/publishing-management.md` §1–5及其引用：架构/分层、已有代码复用、提供方契约、事务/并发、原现场及核验、SSE、本机存储。§2.2引用的平台层只影响已确认执行边界，不引入评论/人工最终提交等排除功能。
- 该文引用的 Cloud `web/example/proto/publishing-design`（PlanPage、plan/、BatchManager、BatchDetailContent、PublishComposer）及 `web/example/common`：实际布局和交互实现输入；本轮初始原型 SHA9305532。不以“功能相同”代替视觉一致，不把示例 Runtime 加入正式产物。
- 该文引用的 PRD、social-accounts、operating-resources、content-production、认证 ADR0022及契约 Ownership/Map：按相应能力渐进核对。
- 正式前端规范：AdminUI 页面组织、前端交互、架构/视觉 Token、用户反馈，按所属职责核对。
- 顺序：完整实现/静态与单元/契约/数据库及受控集成自测 → 独立审查修复 → 最新环境真实 E2E → 最后 Web/安装版 UI 走查 → PR/CI问题与技术交付收口。发现问题回到所属实现步骤，不提前宣称验收通过。

## 需求—代码—自测映射

| 业务能力 | 主要实现位置（Cloud 除另标） | 必须证明的自测 | 当前事实与待补 |
| --- | --- | --- | --- |
| 列表、搜索、详情与范围 | publish/service/plan.go、repository/plan_query.go、PublishingPlansPage | 全目标类目授权后count/page；本人、同team高级只读、admin只读、跨范围拒绝 | 已有真MySQL scope断言；9bb0969包含paused、全部goal授权/同goal筛选与count/page已独立真MySQL复验；0968b1a组合browser实际四项查询GET参数及重置通过 |
| 创建/编辑/校验/目标守恒 | model/plan.go、repository/plan.go、PlanWorkbench、planPreparation | 每格守恒、稳定ID/归属、失败回滚、旧revision、原key重放 | 数据层及Service已定向/独审；0968b1a实际失衡拒绝无PUT→修正structure PUT、逐格守恒与stable IDs通过 |
| 本人资源盘点 | 复用BatchResources→PlanWorkbench | 账号/成片/可安排量/asof；known0、短缺、unknown、readfail、越权 | 2fd6cd0已补正式本人资源盘点四态/asof/素材缺口；独立编辑器浏览器通过，容量未知不造假；最终expanded-editor组合已通过（资源四态/守恒/合并拆分排序/固定行） |
| 手工新增/拆分/合并/排序 | PlanWorkbench、planPreparation，对照原型plan/app | A1+B1手动拆两批、目标增删重配、stableID、终止固定行、完整守恒 | 2fd6cd0已补手动新增/分格/A1B1拆分及固定行保护；独立编辑器浏览器及单测通过，AI不是必经 |
| 真实AI建议与采用 | plan_recommendation.go、plan_handler.go、PlanWorkbench | 服务端本人数量；模型非法/截断/取消失败；SSE真实事件；审阅后采用、不自动保存 | Go/受控流已测；真实DeepSeek建议与内容生成均已实测，见real-e2e.json |
| 全批配置准备 | 原PublishingBatchesPage及BatchResourceSetup/CandidateWorkspace | 继承目标只读；候选保存零task/占用；全部待执行批次就绪才首启 | 共享107数据守卫与两批configuration PUT实际受控验证通过；继承目标只读、响应零任务、无start/publication POST；真实DB见T03/T05；G2实际plan1/batch3/4配置零task/占用已读回 |
| 首次原子启动/冻结 | shared startBatchTx、plan_execution.go、Plan命令journal | 一次task/占用/授权/cursor/receipt；全批冻结；跨批重复定位；失败全回滚 | 真MySQL及原回执测试通过；Provider/consumer权威未生效proof、缺字段false/0负例已修并独审关闭 |
| 计划原请求恢复 | plan_command.go、planPreparation、PublishingPlansPage | 原key/原包先receipt；权威false绑定；普通409/读失败未知保留；跨标签CAS | Provider9a01a1f/0e722ce及嵌套回执72e54eb、前端2fa2ca0已独立复验；实际HTTP/15schema/原key矩阵通过，既有原请求browser及相应单测通过，最新全Web165/1235通过 |
| 固定组与原批次执行入口 | 复用108、BatchExecutionControls及父plan投影 | 原N/间隔/异常/容量；同名按钮/权限/确认/API；future/移交不能旁路 | 108及109父锁隔离回归已有；G2真实两批N5→实际组1，原任务及批次详情已读回；复杂异常为隔离验证 |
| 顺序衔接与确认 | planProgress/Advance、worker | 10%auto、20%confirm、0skip、prefix未决、旧basis、锁后实时截止 | 真MySQL已测、独审修复；UI实际请求严验需保持 |
| 暂停/恢复/接管/终止 | ControlPlan、各执行入口父围栏 | pause仅后批；接管不重建单/授权；stop封提交许可；原结果安全收尾 | 真MySQL已有；UI接管/确认范围保持同谓词 |
| 待办与分页 | PlanBatchPage、VerificationRequiredAt | 五类未决+停查/过期无新manual一致；count/page前过滤；manual仍审核清衔接待办不清finish | 8c5e64f已修，独立3项真MySQL2.863s及root3.195s通过，全TestPlan27.386s通过 |
| 人工四结论及再核实 | recovery.go、LatestManualVerification、PublishingRecoveryDialog | 本人reviewing四结论、manager仅pub、unknown再核实、原结果/占用保留 | 0968b1a新增actual四结论dialog/payload、failed缺证据拒发、unknown原attempt再核实、manager仅published通过；0968b1a及310577b独审已关闭 |
| 可信公开与逐格缺口 | matched-work join、plan_result.go、Plan详情/列表 | task/attempt/output/work精确关联；reviewing不算公开；跨格不抵消 | 实际隔离work Service回调已测；G2真实公开work6/7精确关联13/36/137与14/37/138 |
| 最终结束与迟到结果 | FinishPlan/ReconcileStoppedPlan | 未决/审核/错work/旧gap拒；unmet原因；cancel安全收敛；late不重开 | 后端已测；UI枚举unmet已59ef13e，actual请求schema断言已补 |
| 新建续编及Cloud编辑 | Agent publication_draft、Native桥、JS plan类型 | 用户/环境/类型隔离、重启、CAS、明确重开才清、dismiss保留、Cloud edit不另存 | 本机951/Native561+独审；e1efd45三态恢复已修，独立单测/实际browser断言复验关闭，既有draft恢复browser与最终完整Web165/1235通过 |
| 创建明确拒绝与未知 | PublishingPlansPage pendingCreate | 首次明确拒绝后可编辑/退出；未知找回不换key；原form/pending保留 | 2c5b50e已独立复验首次明确拒绝/未知分别处理 |
| 原批次只读Drawer与回跳 | BatchReadonlyBody、ResourceOverlay、from_plan | 视口内header/close、独立滚动；读失败恢复overflow；关闭和配置/处理返回保page/filter/scroll | 顶部开发截图修正；2c5b50e失败出口/plan_scroll已有限复验；0968b1a实际tasks筛选/重置/page2、records page2、Drawer关闭及task→batch→plan原过滤/page/精确scroll返回通过；发现783→623布局时序负例已最小修复，独审已关闭 |
| 原型视觉对齐 | 计划/批次所有生产页面、plan.css、正式Resource组件 | 区块/字段顺序、同排、表格列、宽度、间距、指标/进度、底栏、Drawer与既有原型代码逐页映射 | e480c94按原型源码重组，独立代码映射与开发browser核对通过；G3真实Web与本机走查进行中，整改与最终复查见ui-walkthrough.md，不以过程证据签收 |

## 三道收口门

- [x] G1 编码与自测：上表所有缺口修复；新增负例、实际请求/响应schema、受控数据库/浏览器验证通过；差异和代码映射独立审查，无未关闭P1/P2。受影响完整Go/Web/Agent/Desktop及契约检查结果在最终SHA上可追溯。
- [x] G2 真实E2E：仅G1后重建新环境/DMG、真实本人资源与AI、真实至少两批顺序和公开事实；原目标/唯一任务/占用/attempt/work一致，真实单Profile与受控多Profile分别记载，不伪造资源或结果。
- [ ] G3 最后UI走查：G2后Web与安装版逐页对照原型最终走查，覆盖角色、完整正常及必要异常路径、返回与视口。用户107–109最终统一整体验收仍另行进行。

## 分阶段证据记录

以下“未开始”“待执行”等为对应阶段当时事实；当前结论以顶部三道收口门、checkpoint及最终走查证据为准。

G1曾按以下证据完成并进入G2，真实读取发现未启动计划批次独立start动作投影遗漏，该修复已完成并独审关闭；G2/G3不得预填完成。原型预览、开发截图、fixture及测试总数仅能支持其实际覆盖的自测项。

## T07 原型代码对齐实施映射（独立开发验证通过，非最终视觉验收）

| 页 | 已确认差异 | 使用的原型实现输入与修改范围 |
| --- | --- | --- |
| 计划列表 | 更新时间、ID复制/名称链接、状态/结束结果、进展二行、数量/比例、周期排版缺失或不同 | PlanList.columns及slots，正式ResourceNameLink/Badge/RowActions/EmptyState与分页；保持原shell导航 |
| 计划详情 | 负责人/类目/批次数/创建更新不全，summary自绘，矩阵缺合计/完成率，批次表少结果/待办 | PlanDetail ResourceDescriptions顺序、ResourceStatGrid、Notice action、目标矩阵及九列表结构；真实read投影，不臆造名称 |
| 计划编辑 | 日期/基础信息/目标区组织不同，缺盘点与完整分配dialog | PlanBasicForm/PlanGoalScope/plan/app结构与样式，名称周期同排/备注整行；盘点四态、手工新增分配及三态续编 |
| 批次列表/详情 | tabs拆散原型纵向信息、执行/目标统计位置不同 | BatchManager列与BatchDetailContent纵向分区，正式共用主体供page+Drawer；保留任务过滤/分页/所有既有原操作 |
| 批次配置 | 三段标题、字段同排、summary/底栏不同 | PublishComposer三段代码、common/Token、现有正式Resource组件；不复制AI/执行内核 |

实施者负责以上逐页对齐；根和独立审查者按代码映射与开发验证核对，最终UI走查留G3。不能以现有开发截图的‘基本相同’替代本轮用户指出的视觉差异整改。

自测口径裁定：现有BatchResources只有本人账号/成片及未知数，没有周期额度或最终可安排容量。页面不得自创“每账号1条”的容量公式；展示已知数量/asof/gaps，容量未知明确标待逐批配置核实，目标-可用成片数仅称成片缺口。继续允许超库存目标，不能把未知当0或无限。

最后结构/完整能力审查：e480c94+2fd6cd0独立57项单测、编辑器/三角色受控浏览器通过，未发现手工盘点/分配/固定行/共享Reorder默认兼容新增P1/P2。三处将全部reviewing计待办的P2已由契约7c09ebe、共享投影e7eb30a、消费a914ed8修复并独立关闭；正常审核/最新有效人工仍审核为0，停查或过期未核实为1，unknown仅计uncertain，缺失字段显待刷新。没有新查询或异常上限规则变更。

最新根验证：完整Web165文件1235通过（/tmp/chg109-final-web.log）；完整隔离MySQL repository110.751s通过（/tmp/chg109-root-final-live-repo.log，显式WT_MEDIA_CLOUD_HOME，首个未设路径的尝试未通过且不计PASS）；17项契约通过（/tmp/chg109-root-final-schema.log，专用/tmp/chg109-contract-validation环境，系统Python缺依赖的尝试不计PASS）。实施者完整Go及两端构建通过；独立复审MySQL计数3.465s、原投影/集合查询1.579s、45项Web及五场景三页浏览器、schema17均通过。根此前Workspace repo完整检查通过（/tmp/chg109-root-workspace-checks.log）。

G1最后逐行核对仍补受控页面证据：列表筛选重置、edit PUT守恒、Drawer正式任务过滤/分页与records分页、from_plan返回位置、四结论原dialog操作。另计划关联批次配置页须仅保存并返回计划，隐藏容易误导的独立“开始发布”，保持计划全批确认入口。以上尚未独立闭环，G1/T07不能提前勾选，G2/G3未开始。

0968b1a完成最后受控组合与必要修复：计划关联批次配置仅保存返回，首启仍走计划全批确认；返回计划等待共享布局首帧后精确恢复scroll，disposed/seq守卫防旧加载覆盖。新增组合browser与四结论browser、扩展editor真实操作均通过。最终提交正独立复审，root最终Web165/1235已通过、双端构建收尾，G1暂仍未勾选。

## G1 最终结论（2026-11-25）

- 最终Cloud310577b（生产代码0968b1a），Agent81f6bf8，Desktop2e06487；完整Go通过，完整隔离MySQL repository110.751s通过，17契约通过；root最终Web165文件1235项、Cloud/Desktop两构建均通过（/tmp/chg109-root-g1-final-{web,cloud-build,desktop-build}.log），Workspace完整治理检查通过（/tmp/chg109-root-g1-final-workspace.log）。Agent951、Desktop561通过/6既有ignore的原完整结果在未再修改的对应SHA上有效。
- 独立最终复审：三组新增组合/编辑器/四结论browser实际通过，生产11行与原型实现映射无未关闭P1/P2。首次matrix暴露先点击后监听的测试竞态，不能以重跑偶过掩盖；310577b改为先注册promise后点击，独立新SHA整组通过，原scroll<2px断言未变。
- G1完成依据为实现、数据库/契约/受控页面自测和独立审查；真实AI、真实平台公开及安装版最终走查分别留G2/G3。

G2真实读取反馈：环境310577b/81f6bf8/2e06487全部门禁通过并挂载；真实DeepSeek建议两批1+1，正式重制730/731→新成片137/138成功。计划1与骨架3/4创建、同键重放一致且零正式任务。实际API未启动计划内批次allowed_actions仍含start，与首启必须计划全批确认不一致；暂停真实start，返回G1修只读动作投影。不得用已有fixture通过掩盖此真实遗漏。

真实反馈修复4daf991已独立关闭：计划所属批次start只读投影始终过滤，沿用plan_position_blocked提示统一计划确认；独立批次start、本人edit/合法stop、resume/takeover及内部StartPlan/Preview不变。独立service0.291s、真MySQL1.120s通过；root完整publish模块及隔离repository126.794s通过（/tmp/chg109-root-start-action-publish-live.log）。G1重新关闭，须以4daf991重建环境后继续原计划1的G2，不重新创建或重发。

G2两批实际投稿13/36、14/37成功，自动移交3→4，无人工逐批confirm/finish。均正常reviewing，公开0且finish动作正确不可用；只读progress却显示ready_to_finish，需补全批执行后仍有reviewing时等待平台公开的投影及正式契约。当前回G1修该展示事实；不改变运行中原核验、10%推进或finish写guard，不重发。G3仍未开始。

尾批正常审核展示修复已关闭：正式ede0c83、消费7e43de3、Go a59b793。只读awaiting_finish按全已启动前缀reviewing及noNext投影，保留stop/pause/verification/unknown优先级，既有finish写guard/10%不变；前端明确等待平台公开、当前批次暂停。root单场景真实隔离18.722s、schema18、完整Web165/1236、双build通过；实现者全TestPlan31.084s/fullGo通过，独立schema18/39unit/两browser及真MySQL最终审核+10%/查询25.451s通过，无未关闭P1/P2。G1重新关闭。

真实task13/14已各唯一关联work6/7，原attempt36/37 completed/finished且scene_closed=true；DB publish/check Profile持有共6行全部released，active_profile/slot均NULL，published任务next_check_at均NULL。可安全按a59b793全环境升级，验证重启不重复及最终结束；G2/G3仍未完成。

G2最终通过：a59b793完整all门禁/source挂载通过；重启后仍task13/14、attempt36/37、work6/7，目标2/2且逐格缺口0。实际安装版登录/结束确认成功，API及业务DB读回plan1 ended/achieved/revision6，全部批次ended，各1task/1attempt/1work，计划仅copy动作、pending/verification均0。真实仅1本人Profile，N5→每批实际组1；多Profile/复杂阈值和异常为隔离受控验证，未冒称实机多账号或Windows。完整事实见real-e2e.json。G3最终双端原型走查现在开始，尚未签收。
