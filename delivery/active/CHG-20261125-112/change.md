---
id: CHG-20261125-112
parent: delivery/milestones/M7-batch-publishing.md#页面实施基线
status: IMPLEMENTING
depends_on: []
affected_repos: ["wt-media-cloud", "wt-media-workspace"]
risk: M
---

# CHG-20261125-112：批次数量输入与资源确认流转

## Change

承接人工验收两张截图：恢复原型连体数字输入框；核实并落实资源确认后步骤边界，覆盖新建、续编、编辑及异常恢复。沿用Cloud原型930553217cf5a3c8a1750178da4974d5b46dfeac中PublishComposer.vue、batchCreation.css和example/common/number-stepper.css；当前其他会话原型修改不纳入。

正式事实入口：M7页面实施基线、PRD第六章6.3、publishing-management.md 2.3/2.4/6。保留107保存配置零task/占用、108启动建单与109首次启动冻结。页面导航限制不擅自变更正式批次首次启动前的编辑权限。

唯一执行器本会话；基线Cloud bbba813c、Workspace29b9bb4均已推送main。其他会话example及docs/design修改保留。范围仅Cloud共用Vue及相关测试、Workspace交付；无DB/Contract/Agent/Desktop运行源码变化，安装包按新Vue重建。

顺序任务：1.原型/截图复现及数值输入定向失败回归→样式修复、自测、提交；2.步骤边界确认→导航及续编异常修复、自测、提交；3.既有E2E与新增异常矩阵、双端构建及安装版走查；4.PR/CI/review问题修复、证据与归档。数量样式任务不依赖下列流程问题。

Q-01（仅阻塞步骤行为）：已询问用户，建议本次新建/草稿资源确认后不回第一步，第二步只处理内容，第三步可回内容；保存后首次启动前仍可从继续配置调整资源。等待裁定，不把UI确认冒充服务端永久冻结。

## Done When

- [ ] 数字输入原型连体边框、焦点、禁用及窄屏布局验证通过，数值键盘/加减/清空语义保留。
- [ ] 资源确认、取消、内容/总览返回、新建/续编/已存编辑边界落实，并明确剩余问题。
- [ ] 缺少范围、零资源、盘点失败、确认中变更、异步迟到、保存失败/未知及修订冲突相关场景E2E通过，实际新安装版走查有证据。
- [ ] PR/CI与交付收口完成，未验证或待人工决定的事项如实说明；用户最终整体签收另行。
