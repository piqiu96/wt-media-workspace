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
| 列表、搜索、详情与范围 | publish/service/plan.go、repository/plan_query.go、PublishingPlansPage | 全目标类目授权后count/page；本人、同team高级只读、admin只读、跨范围拒绝 | 已有真MySQL scope断言；最终UI全部筛选/重置待统一核对 |
| 创建/编辑/校验/目标守恒 | model/plan.go、repository/plan.go、PlanWorkbench、planPreparation | 每格守恒、稳定ID/归属、失败回滚、旧revision、原key重放 | 数据层及Service已定向/独审；完整手工操作待补 |
| 本人资源盘点 | 复用BatchResources→PlanWorkbench | 账号/成片/可安排量/asof；known0、短缺、unknown、readfail、越权 | **发现缺实现，已分配补齐**；目标可超库存不静默降低 |
| 手工新增/拆分/合并/排序 | PlanWorkbench、planPreparation，对照原型plan/app | A1+B1手动拆两批、目标增删重配、stableID、终止固定行、完整守恒 | **发现缺手工闭环，已分配补齐**；AI不能成为必经路径 |
| 真实AI建议与采用 | plan_recommendation.go、plan_handler.go、PlanWorkbench | 服务端本人数量；模型非法/截断/取消失败；SSE真实事件；审阅后采用、不自动保存 | Go/受控流已测；真实DeepSeek留最后E2E |
| 全批配置准备 | 原PublishingBatchesPage及BatchResourceSetup/CandidateWorkspace | 继承目标只读；候选保存零task/占用；全部待执行批次就绪才首启 | 共享107数据守卫已有；完整页面与原型对齐待完成 |
| 首次原子启动/冻结 | shared startBatchTx、plan_execution.go、Plan命令journal | 一次task/占用/授权/cursor/receipt；全批冻结；跨批重复定位；失败全回滚 | 真MySQL及原回执测试已测；原请求明确未生效恢复仍修复中 |
| 计划原请求恢复 | plan_command.go、planPreparation、PublishingPlansPage | 原key/原包先receipt；权威false绑定；普通409/读失败未知保留；跨标签CAS | **已知P2修复中**，前后端及真实HTTP/schema须一致 |
| 固定组与原批次执行入口 | 复用108、BatchExecutionControls及父plan投影 | 原N/间隔/异常/容量；同名按钮/权限/确认/API；future/移交不能旁路 | 108及109父锁隔离回归已有；最终真实联调后验收 |
| 顺序衔接与确认 | planProgress/Advance、worker | 10%auto、20%confirm、0skip、prefix未决、旧basis、锁后实时截止 | 真MySQL已测、独审修复；UI实际请求严验需保持 |
| 暂停/恢复/接管/终止 | ControlPlan、各执行入口父围栏 | pause仅后批；接管不重建单/授权；stop封提交许可；原结果安全收尾 | 真MySQL已有；UI接管/确认范围保持同谓词 |
| 待办与分页 | PlanBatchPage、VerificationRequiredAt | 五类未决+停查/过期无新manual一致；count/page前过滤；manual仍审核清衔接待办不清finish | **发现A07口径不一致，已分配单独修复** |
| 人工四结论及再核实 | recovery.go、LatestManualVerification、PublishingRecoveryDialog | 本人reviewing四结论、manager仅pub、unknown再核实、原结果/占用保留 | 后端/原dialog接线已测；全部UI流程待独审闭环 |
| 可信公开与逐格缺口 | matched-work join、plan_result.go、Plan详情/列表 | task/attempt/output/work精确关联；reviewing不算公开；跨格不抵消 | 实际隔离work Service回调已测；真实平台留E2E |
| 最终结束与迟到结果 | FinishPlan/ReconcileStoppedPlan | 未决/审核/错work/旧gap拒；unmet原因；cancel安全收敛；late不重开 | 后端已测；UI枚举unmet已59ef13e，actual请求schema断言已补 |
| 新建续编及Cloud编辑 | Agent publication_draft、Native桥、JS plan类型 | 用户/环境/类型隔离、重启、CAS、明确重开才清、dismiss保留、Cloud edit不另存 | 本机951/Native561+独审；**三态恢复缺口已分配补齐** |
| 创建明确拒绝与未知 | PublishingPlansPage pendingCreate | 首次明确拒绝后可编辑/退出；未知找回不换key；原form/pending保留 | **已知P2修复中** |
| 原批次只读Drawer与回跳 | BatchReadonlyBody、ResourceOverlay、from_plan | 视口内header/close、独立滚动；读失败恢复overflow；关闭和配置/处理返回保page/filter/scroll | 顶部开发截图修正；**失败出口/plan_scroll仍修复中** |
| 原型视觉对齐 | 计划/批次所有生产页面、plan.css、正式Resource组件 | 区块/字段顺序、同排、表格列、宽度、间距、指标/进度、底栏、Drawer与既有原型代码逐页映射 | **用户指出不符合，尚未通过；重新逐页对齐，不能以旧截图标完成** |

## 三道收口门

- [ ] G1 编码与自测：上表所有缺口修复；新增负例、实际请求/响应schema、受控数据库/浏览器验证通过；差异和代码映射独立审查，无未关闭P1/P2。受影响完整Go/Web/Agent/Desktop及契约检查结果在最终SHA上可追溯。
- [ ] G2 真实E2E：仅G1后重建新环境/DMG、真实本人资源与AI、真实至少两批顺序和公开事实；原目标/唯一任务/占用/attempt/work一致，真实单Profile与受控多Profile分别记载，不伪造资源或结果。
- [ ] G3 最后UI走查：G2后Web与安装版逐页对照原型最终走查，覆盖角色、完整正常及必要异常路径、返回与视口。用户107–109最终统一整体验收仍另行进行。

当前不得将G1/G2/G3标记完成。原型预览、开发截图、fixture及测试总数仅能支持其实际覆盖的自测项。

## T07 原型代码对齐实施映射（待独立验证，非视觉验收）

| 页 | 已确认差异 | 使用的原型实现输入与修改范围 |
| --- | --- | --- |
| 计划列表 | 更新时间、ID复制/名称链接、状态/结束结果、进展二行、数量/比例、周期排版缺失或不同 | PlanList.columns及slots，正式ResourceNameLink/Badge/RowActions/EmptyState与分页；保持原shell导航 |
| 计划详情 | 负责人/类目/批次数/创建更新不全，summary自绘，矩阵缺合计/完成率，批次表少结果/待办 | PlanDetail ResourceDescriptions顺序、ResourceStatGrid、Notice action、目标矩阵及九列表结构；真实read投影，不臆造名称 |
| 计划编辑 | 日期/基础信息/目标区组织不同，缺盘点与完整分配dialog | PlanBasicForm/PlanGoalScope/plan/app结构与样式，名称周期同排/备注整行；盘点四态、手工新增分配及三态续编 |
| 批次列表/详情 | tabs拆散原型纵向信息、执行/目标统计位置不同 | BatchManager列与BatchDetailContent纵向分区，正式共用主体供page+Drawer；保留任务过滤/分页/所有既有原操作 |
| 批次配置 | 三段标题、字段同排、summary/底栏不同 | PublishComposer三段代码、common/Token、现有正式Resource组件；不复制AI/执行内核 |

实施者负责以上逐页对齐；根和独立审查者按代码映射与开发验证核对，最终UI走查留G3。不能以现有开发截图的‘基本相同’替代本轮用户指出的视觉差异整改。
