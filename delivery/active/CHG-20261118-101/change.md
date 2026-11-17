---
id: CHG-20261118-101
parent: delivery/milestones/M6-single-publishing.md#单任务从内容准备到真实作品
status: VERIFYING
depends_on: []
affected_repos: ["wt-media-workspace", "wt-media-cloud"]
risk: H
---

# CHG-20261118-101: M6-A 正式任务与文件安全

## Change

把单任务快速发布从原型接入正式 Cloud / Desktop 共用页面：选择真实百度账号、成片和现成图片，确认内容后创建未执行任务，支持查询与待执行内容修改。创建取得同平台成片占用，以请求键防重，以修订号防止覆盖编辑，保留操作者和资源快照。

实际表单联调发现新上传文件被写入空删除状态，已修复上传初始化，并用增量迁移修正空值和约束合法状态；不恢复删除中的文件。

文件删除按 Engineering Spec §4.6 改为锁行确认引用、标记删除、事务外物理删除、最终结算；失败可重试，已标记文件不能再被选用或签发地址。当前任务引用与删除互斥；同时保护已有生产策略、批次与任务 JSON 保存的文件引用，并在相应写入事务中锁文件行。只交付本单元需要的数据表、提供方接口和消费页面，不提前建立批次、计划或模板设施。

实际联调发现现有抖音素材的规范长链接被错误作为短链传给详情服务，阻断同类目真实成片准备。本 CHG 只修复规范长链接使用已有视频 ID 查询协议；保留短链协议，不调整素材、生产或账号的业务规则。

执行顺序：先验证文件删除与任务防重/权限失败场景，再实现数据库和接口，最后接入共用页面并实际浏览器走查。迁移在隔离数据库验证，现有账号和成片只读选择；创建任务不授权 Agent、不产生浏览器投稿。平台公开开放仍等待 M6 真实验收。

本次用户已授权单一执行器串行推进，并允许后续已验证单元通过堆叠分支/PR 临时依赖未 Review 变更；各仓独立 PR，明确合并顺序，不自动合并，不修改长期治理规则。本单元从最新 main 开始，无未合并依赖。

## Done When

- 共用页面用真实可用账号、成片和图片创建一条 pending 任务；列表与详情可读回内容、资源和占用，任务尚未执行且无投稿副作用。
- 同键同输入返回原任务；异输入、同平台成片重复占用、越权及无效资源明确拒绝；并发创建只保留一个任务。
- 仅未领取 pending 任务可按 expected_revision 修改内容；冲突不能覆盖已有输入，资源身份不能被修改。
- 文件在正式任务引用期间无法删除；并发引用与删除不会留下不可读任务；物理删除失败保留 deleting 状态并能安全重试，不重新暴露已删除对象。
- 新迁移、接口/权限/并发测试、前端检查和实际浏览器表单提交有可复现证据；PR 引用本 CHG，等待 Review。M6 不标记 DONE。

## References

- [M6 业务验收](../../milestones/M6-single-publishing.md#单任务从内容准备到真实作品)
- [PRD 第六章](../../../docs/product/prd/详细文档/第六章_发布管理.md)：6.4、6.5、6.8。
- [发布工程设计](../../../docs/engineering/specs/publishing-management.md)：3.4、4.1、4.6、5、6。
- [AdminUI](../../../docs/standards/frontend/AdminUI页面规范.md)、[交互](../../../docs/standards/frontend/前端交互规范.md)、[视觉与组件](../../../docs/standards/frontend/前端架构与视觉规范.md)。
- [Cloud 原型基线 9f132dd](https://github.com/piqiu96/wt-media-cloud/tree/9f132dd375477c116809b48507f6fd7a8b28d567/web/example/proto/publishing-design)：QuickPublish.vue、TaskDetail.vue、PublishingTaskPage.vue；入口 `/example/operations/publishing/tasks` 与 `/example/operations/production/outputs`。正式页面需实际核对布局、交互与公共规范；原型演示不作为生产验收。
