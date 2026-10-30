---
id: CHG-20261030-108
parent: delivery/milestones/M2-account-runtime.md#m2-d1-maintenance
status: PLANNED
depends_on: []
affected_repos: ["wt-media-workspace", "wt-media-cloud", "wt-media-agent", "wt-media-desktop"]
risk: H
---

# CHG-20261030-108：矩阵账号维护与人工登录后检查同步

## Change

交付 M2-D1：最终账号维护页面及人工登录后真实平台识别，检查不写浏览器 Cookie。同步回写 PRD、ADR、工程设计并固定已批准原型。旧账号模块未使用，不建设兼容层；保留外部真实窗口与会话。

数据库、接口和整体落地方案已确认；运行时实施未启动，进入实施阶段时再激活。

当前差距：账号表尚无本次检查结果与编号字段；现有资料接口仍可写平台身份/登录状态，identify、账号组与旧 Cookie 接口需要收敛，部分路由缺少 OpenAPI 描述。数据库与接口核对及目标清理目录见工程设计。

### 落地顺序

1. 确定提供方资料/检查契约，补账号当前检查字段与按编号结算。
2. 打通 Agent 实时只读识别、Desktop 桥及共享 Vue 最终维护页面。
3. 同阶段删除手填身份、账号组、旧开户入口和无消费者实现。
4. 按原型、角色、数据库和真实 B站/百度效果验收，完成契约组合交付。

整体方案见[工程设计 §7](../../../docs/engineering/specs/social-accounts.md#7-整体落地方案)；表结构与 API 见同文 §1～4。具体实现文件、内部函数和验证命令由实施 Codex 按目标仓规范决定，不在此预写代码级步骤。

## Done When

- 普通/高级/管理员的账号可见范围和本机动作符合 PRD；资料只改类目、标签、备注，启停独立确认；详情 800px 只读。
- 无已存 Cookie、未分类的本人账号可绑定已有登录窗口并手动检查；B站/百度 UID/昵称/头像/登录状态真实回填。
- 同 UID 更新资料，异 UID 不覆盖原身份且可直接对照；失败保留历史结论；旧编号、窗口变化、重复结果有定向验证。
- 新增迁移可在目标测试库顺序执行；检查结算不覆盖并行修改的账号资料；无通用 operation 表或工作流。
- 旧 identify/账号组/开户流程及无消费者代码已清理；公共窗口、代理、类目和真实 Cookie 未因清理受损。
- 定向测试、两种 Vue 构建及契约消费者检查通过，真实平台与页面验证记录 PASS 或明确未验收；未完成真实验收不标 DONE。

## Not In Scope

Cookie 写入、写前保留和批量接入属于后续 109/110；不提前实现其业务对象。不恢复接码、链接换绑、自动全量检查、审批或审计中心。不将后续尚未实现能力伪装成功入口。

## References

- Product: `docs/product/prd/详细文档/第三章_用户与账号管理.md`
- Engineering: `docs/engineering/specs/social-accounts.md`
- Decision: `docs/decisions/0030-social-account-rebuild.md`
- UI: `example/proto/social-accounts/index.html`；`docs/standards/frontend/AdminUI页面规范.md`、`前端交互规范.md`、`用户反馈规范.md`。
