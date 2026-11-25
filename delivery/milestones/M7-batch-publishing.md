# M7：多任务批次真实发布

- 状态：`IN_PROGRESS`；Active CHG：CHG-20261125-112；原型修复：[CHG-20261125-110](../completed/CHG-20261125-110/change.md)；107/108技术交付DONE，真实可用Profile下兼容实发与双端结果验证完成；用户整体最终验收待109后。
- Evidence：[107配置准备实际双端E2E](../completed/CHG-20261124-107/evidence/installed-e2e.json)；[108执行验收](../completed/CHG-20261124-108/evidence/acceptance-matrix.md)、[真实双端E2E](../completed/CHG-20261124-108/evidence/installed-e2e.json)及[合入证据](../completed/CHG-20261124-108/evidence/merge-and-verification.md)。
- 依据：[PRD 第六章](../../docs/product/prd/详细文档/第六章_发布管理.md) 6.3、6.5、6.8；[发布工程设计](../../docs/engineering/specs/publishing-management.md) §2.1—2.5、§4—6。
- 依赖：[M6](M6-single-publishing.md) `DONE`；在百度（百家号）验证批次，按 [PRD 批次规则](../../docs/product/prd/详细文档/第六章_发布管理.md#632-新建批次)真实可用本人Profile不足配置N时向下兼容；多账号分组及跨批Profile互斥另列受控证据。

## 页面实施基线

业务路由：`/example/operations/publishing/batches`。先启动 Cloud 原型服务，使用启动输出中的实际访问地址打开上述路由；主机和端口以本次启动结果为准。源码及业务路由是校验依据。

已验收原型：批次列表、资源/内容配置、结果总览及详情。源码：[Cloud publishing-design](https://github.com/piqiu96/wt-media-cloud/tree/main/web/example/proto/publishing-design) 的 `BatchManager.vue`、`BatchWorkbench.vue`、`BatchContentWorkspace.vue`、`BatchDetailContent.vue`。

公共前端规范：[AdminUI](../../docs/standards/frontend/AdminUI页面规范.md)、[交互](../../docs/standards/frontend/前端交互规范.md)、[视觉与组件](../../docs/standards/frontend/前端架构与视觉规范.md)。

页面布局、交互和视觉继承上述原型。涉及正式页面的 CHG 按[页面实施与验收要求](README.md#页面实施与验收基线)引用具体原型入口，验收包含实际页面与原型的一致性检查；原型代码直接作为正式页面框架，接口差异由研发修复或适配，新增技术信息在原区域补充；普通实现差异不再交由产品负责人裁定，只有改变业务规则的事项才需确认。不另行设计一套界面。

## 从一组资源到批次结果

| 要回答的问题 | 本阶段交付 |
| --- | --- |
| 用户目标 | 先准备并灵活修改，再一次启动发布，异常集中处理 |
| 前置能力 | M6可信任务/结果、真实本人资源、UID/Profile互斥与文件服务 |
| 用户操作 | 三段配置→保存或创建并发布→分组执行→按异常策略集中处理→可信公开结果 |
| 系统与平台动作 | 保存只写候选；首次start一次生成全部确认任务/占用/授权；本人Agent按组执行 |
| 同时成立才算完成 | 保存零task/占用，启动原子；本人可用Profile下兼容真实发布，多账号/跨批互斥受控验证，组间处理和上限可控、双端真实公开验收 |
| 必须排除的假成功 | 保存冒充发布、少发下调目标、未知重发、超时释放在途Profile、审核算公开 |

## 候选 CHG 与内部顺序

| CHG | 工作内容及仓库 | 直接依赖 | 可独立验证的完成条件 |
| --- | --- | --- | --- |
| [107](../completed/CHG-20261124-107/change.md)／[落地清单](../completed/CHG-20261124-107/plan.md) | Cloud/Agent/Desktop；本人资源、批量内容、候选保存 | M6 DONE | 保存零task/占用，整体编辑与双端可用 |
| [108](../completed/CHG-20261124-108/change.md)／[落地清单](../completed/CHG-20261124-108/plan.md) | Cloud/Agent/Desktop；启动建单、分组、异常控制与公开 | 107 DONE | 原子启动、互斥受控验证、可用本人Profile下兼容实发与双端闭环 |

### 批次准备与正式创建

该既有锚点由107引用；当前交付是创建Cloud批次配置，不是创建正式task。执行顺序：正式事实/固定原型→契约→batch迁移/文件引用事务→本人资源与配对→批量AI/封面→共用页面/新建续编→零任务零占用及双端验收→PR/main证据。

### 批次执行与真实结果

执行顺序：批次start/控制契约→task关联/组与暂停依据→一次建单/占用/授权事务→组间调度和全局互斥→Agent有界并行/可靠挂起/独立补报→异常策略/上限→原稿结果与公开统计→可用本人Profile下兼容实发/双端验收与受控多账号验证→PR/main证据。

配置为并发数、组间发布间隔、组间处理【自动继续、异常暂停】、异常任务上限。慢任务不挡组内其他账号；可靠挂起可留待处理，未知在途不伪造结束。暂停可继续，终止不可恢复。目标30/task28/公开28仍目标30、缺口2、成功率约93.33%。

## 启动条件

当前112修复IMPLEMENTING，107/108技术交付已完成；相关事实已按2026-11-25裁定回写。启动前完成新原型review及固定SHA、提供方正式契约/容量参数、失败结束动作review、依赖归档与各仓main合并检查，再按CHG预检。其他平台真实发布在对应阶段开放验收。

2026-11-25用户授权107→108→109全流程执行，106已签收归档；107技术交付已归档，108已合入运行仓并技术归档，Workspace关闭PR收口。109可按已完成技术依赖及用户授权继续，M7最终用户签收不提前宣称。用户最终整体验收在三项技术交付后统一进行。

2026-11-25用户整体review指出正式批次仍偏离原型，110负责一致性修复、完整受控及真实E2E、全新安装包与运营走查。此前技术验收记录保留；不将其解读为当前视觉整体签收。

110已完成原型框架修复、完整受控回归、本轮真实两批2/2公开与结束、合并main新DMG运营走查；[最终证据](../completed/CHG-20261125-110/evidence/final-delivery.md)。Cloud PR53已合并，Workspace归档随PR66合入生效；本里程碑仍VERIFYING，等待用户整体签收。

111承接用户人工走查：列表始终可见详情，批次状态与配置就绪分开表达，已结束仅列表复制；新建沿原型保存草稿与创建/下一步，常规界面不新增独立检查按钮。执行操作复用正式命令与权限；不确定业务语义最终汇总。

[111状态与按钮走查修复](../completed/CHG-20261125-111/evidence/final-delivery.md)已完成，范围内自测、受控回归与最终新包实际验证PASS；Cloud PR54已合入，Workspace关闭随PR67合并生效。无业务待确认项；里程碑整体仍待用户签收。

112承接数量输入与步骤导航验收：数量控件沿固定原型恢复连体样式，资源确认后的回退与续编边界待本轮核实；验证包含异常E2E和实际安装版走查。
