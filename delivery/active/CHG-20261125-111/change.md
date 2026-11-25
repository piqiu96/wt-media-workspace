---
id: CHG-20261125-111
parent: delivery/milestones/M7-batch-publishing.md#页面实施基线
status: VERIFYING
depends_on: []
affected_repos: ["wt-media-cloud", "wt-media-workspace"]
risk: M
---

# CHG-20261125-111：发布状态与按钮原型对齐

## Change

用户人工走查截图指出新建页底部按钮、批次列表操作与状态偏离预期，授权核实现状、明确问题直接修复、不确定业务取舍最终列清单。

固定Cloud原型SHA930553217cf5a3c8a1750178da4974d5b46dfeac；输入为BatchManager.vue、batchLifecycle.js、PublishComposer.vue、plan/app.js、plan/PlanList.vue及PlanDetail.vue；路由/example/operations/publishing/{batches,plans}。参考docs/product/prd/详细文档/第六章_发布管理.md §6.2/6.3/6.8、docs/engineering/specs/publishing-management.md §2/4/6及两个发布里程碑页面基线。

按原框架修复列表详情常驻、状态与配置分离、现有执行控制入口、草稿按钮和计划页底按钮。继续复用服务端allowed_actions、本人权限、修订校验、确认与原请求恢复；不更改任务/占用/冻结/10%推进语义，不触碰其他会话example和docs/design。接口尚不明确的业务取舍保持原样并登记清单，不阻塞明确项。

顺序：核对原型/实际数据及截图→明确项实现/定向自测→受控浏览器状态与角色矩阵→双端构建和新DMG实际走查→PR/CI与交付证据。

## Done When

- [x] 原型/现状/处置表覆盖三张截图以及计划和批次的状态与操作条件。
- [x] 明确差异已修复，角色/终态/未开始/运行/暂停/待处理/请求恢复回归通过。
- [ ] Cloud/Desktop构建与新安装包环境、实际登录及只读走查通过。
- [ ] PR检查及交付收口完成，未决业务取舍用人话列出，不提前认定用户签收。
