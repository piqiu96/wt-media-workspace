---
id: CHG-20261125-113
parent: delivery/milestones/M7-batch-publishing.md#页面实施基线
status: VERIFYING
depends_on: []
affected_repos: ["wt-media-cloud", "wt-media-workspace"]
risk: M
---

# CHG-20261125-113：批次详情内容与阶段呈现修复

## Change

人工截图暴露详情信息组织未按原型落实：空候选仅剩表头，六列原始字段替代原型四列内容表，单类目目标/缺口重复，未启动即取消的批次重复展示执行信息。只读SQL已证实截图批次1原本目标60、候选0、任务0且已取消，不是内容丢失。

固定原型930553217cf5a3c8a1750178da4974d5b46dfeac的BatchDetailContent.vue/BatchContentTable.vue为输入；业务路由/example/operations/publishing/batches。遵守PRD第六章6.3.4及AdminUI详情信息去重/空态规范。沿原框架修复独立详情与计划只读Drawer共用主体：按是否真实开始区分候选与任务；候选内容表复用原型四列、行状态、分页、长文案；明确零配置/读取不完整；目标/缺口单一摘要与必要的多类目明细；未启动取消给出原因，不伪装执行过。不得更改真实目标/任务/占用、权限及112已确认导航。

仅Cloud共用Vue与相关测试、Workspace交付；无DB/Contract/Agent/Desktop业务源码变化。其他会话example/docs-design修改保留。顺序：原型/真实记录审计→先失败的详情状态浏览器→实现与定向自测→独立/Drawer及异常回归→双端构建/新安装版走查→PR/CI/合入与归档。基线Cloud f99119bd、Workspace0ecc5c18，唯一执行器本会话。

## Done When

- [x] 四列只读发布内容、空态、未知读取、长内容/多条分页及多类目数量不重叠；与原型对照验证。
- [x] 未开始、未开始即取消、有候选、已执行及计划Drawer状态矩阵通过，无详情编辑/执行副作用。
- [ ] 受控异常、自测、双端构建和实际安装版核实通过，原批次真实数据保留。
- [ ] PR/CI与交付收口完成；用户整体签收另行。
