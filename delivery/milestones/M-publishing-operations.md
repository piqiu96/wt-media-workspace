# M-publishing-operations：后续平台与三平台整体回归

- 状态：`NOT_STARTED`；Active CHG：None；没有B站/小红书生产发布验收证据。
- 依据：[PRD第六章](../../docs/product/prd/详细文档/第六章_发布管理.md) 6.5、6.8；[发布工程设计](../../docs/engineering/specs/publishing-management.md)。
- 依赖：整体验收依赖[M-publishing-plan](M-publishing-plan.md) `DONE`；B站可在[M7](M7-batch-publishing.md)完成且百度已真实验收开放后先实施，小红书依赖B站真实验收开放。
- 2026-11-20用户确认：图片库、模板制作与渲染等快速发布工具已前移[M6](M6-single-publishing.md)，本阶段只增加后续平台适配和三平台回归，不再承接未完成的百度基础工具。

## 页面实施基线

沿用M6任务/快速发布/详情及图片模板、M7批次、计划阶段的已验收原型；统一源码位于Cloud `web/example/proto/publishing-design/`。工具回归沿用 `ImageLibraryDetail.vue`、`CoverTemplateManager.vue`、`CoverTemplateWorkspace.vue`，业务路由为 `/example/operations/tools/images`、`/example/operations/tools/templates`；具体路由与原型SHA由对应实施CHG固定，访问主机/端口以原型启动输出为准；按[页面基线](README.md#页面实施与验收基线)核对平台字段与实际交互，不另设计一套页面。

公共前端规范：[AdminUI](../../docs/standards/frontend/AdminUI页面规范.md)、[交互](../../docs/standards/frontend/前端交互规范.md)、[视觉与组件](../../docs/standards/frontend/前端架构与视觉规范.md)。源码入口：[Cloud publishing-design](https://github.com/piqiu96/wt-media-cloud/tree/main/web/example/proto/publishing-design)。正式页面须完成实际页面与原型的一致性检查，差异先由产品负责人裁定，再修改固定基线并验收。

## 用既有工具完成三平台发布

| 要回答的问题 | 本阶段交付 |
| --- | --- |
| 用户目标 | 将已完整可用的百度快速发布、批次及计划能力扩展到B站和小红书，各平台结果可信且互不回归 |
| 前置能力 | M6真实图片、模板、AI、续编及完整任务闭环可复用；M7批次已验收；平台有授权账号及必要字段与稿件查询入口 |
| 用户操作 | 选择已开放平台 → 沿原流程配置/确认内容 → 授权自动发布 → 处理人工卡点和未知结果 → 核实公开作品及批次/计划结果 |
| 系统与平台动作 | Cloud按平台能力校验字段及封面输出，Agent逐平台自动上传/填写/最终提交并回传原结果；Cloud核实公开依据并正确关联/统计 |
| 同时成立才算完成 | B站验收开放后再开发并验收小红书；三个平台均有真实公开作品及未知核实证据；任务/批次/计划、图片/模板使用、跨平台共Profile竞争及断网/停止/迟到结果共同回归通过 |
| 必须排除的假成功 | 平台占位适配器、模拟回执或URL格式冒充公开证据；同Profile跨平台并行；仅百度通过即宣称三平台开放；适配新平台破坏已确认图片、模板或任务历史 |

## 候选 CHG 与内部顺序

| 候选 | 工作内容及仓库 | 直接依赖 | 可独立验证的完成条件 |
| --- | --- | --- | --- |
| PLATFORM 三平台发布扩展与回归 | Cloud/Agent/Desktop；B站、小红书依次适配、验收开放及三平台整体回归 | B站依赖M7及百度验收开放；整体验收依赖计划完成 | 三平台均有真实公开作品、异常核实及任务/批次/计划完整回归证据 |

规划一个“三平台发布扩展与回归”CHG，内部按B站真实适配与验收开放 → 小红书真实适配与验收开放 → 三平台任务/批次/计划综合回归推进。逐平台验收门禁保留，内部里程进展不再拆成Cloud/Agent/Desktop技术切片。

平台字段、封面规格与声明按实际平台重新核验；统一使用M6交付的图片与模板工具，不重建工具或执行框架。其他平台未验收前拒绝创建或执行。最终三平台均通过才关闭本阶段。

实时AI底图、关键帧提取、质量等级匹配、通用工作流、模板版本平台、互动及效果采集继续不在本轮范围。
