---
id: CHG-20261030-110
parent: delivery/milestones/M2-account-runtime.md#m2-d3-cookie-batch
status: PLANNED
depends_on: ["CHG-20261030-109"]
affected_repos: ["wt-media-workspace", "wt-media-cloud", "wt-media-agent", "wt-media-desktop"]
risk: H
---

# CHG-20261030-110：矩阵账号批量 Cookie 接入与结果处理

## Change

复用 109 单项能力，提供预览/确认、Cloud batch/item、逐项窗口计划与接入、七计数、人工登录后继续、跳过恢复、重复提交与未知核实；完成最终批量入口及旧开户残余清理。

按工程设计中的完整表/接口/清理目录交付本闭环；前置 CHG 合并后才能激活。执行顺序：提供方契约与迁移 → Cloud 业务 → Agent 执行 → Desktop 桥与 Vue → 真实验证及旧实现删除。每一任务先反例验证，再实现和定向回归；新迁移不修改旧建库链。

## Done When

- 真实小批次包含成功、无效、人工登录、跳过/恢复、重复 UID 与未知结果；每项状态和总计一致，成功不重放，关闭重进进度可读，预览无副作用，最终页面与原型一致。
- 对应 M2-D 成功事实和禁止假成功条件逐项验证，数据库、真实本机效果、Cloud 投影与页面结果一致。
- 提供方契约、消费者、定向测试与真实验收有证据；独立 review 后按各仓独立提交。
- 不扩入接码自动化、链接换绑、凭证历史产品、审计/审批或永久兼容层。

## References

- Product: `docs/product/prd/详细文档/第三章_用户与账号管理.md`
- Engineering: `docs/engineering/specs/social-accounts.md`
- Decision: `docs/decisions/0030-social-account-rebuild.md`
- UI: `example/proto/social-accounts/index.html`；`docs/standards/frontend/AdminUI页面规范.md`、`前端交互规范.md`、`用户反馈规范.md`。
