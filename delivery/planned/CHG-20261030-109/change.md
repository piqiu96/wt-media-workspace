---
id: CHG-20261030-109
parent: delivery/milestones/M2-account-runtime.md#m2-d2-cookie-single
status: PLANNED
depends_on: ["CHG-20261030-108"]
affected_repos: ["wt-media-workspace", "wt-media-cloud", "wt-media-agent", "wt-media-desktop"]
risk: H
---

# CHG-20261030-109：单账号 Cookie 接入、更新与内部保护

## Change

先变更提供方 Cookie 契约与 Cloud 版本存储，打通一个账号的新建优先接入和已有账号更新；复用窗口/代理能力，落实占用、写前保留、平台隔离、身份核实、结果未知先核实；删除旧 Cookie 宽字段与 read-sync 链路。

按工程设计中的完整表/接口/清理目录交付本闭环；前置 CHG 合并后才能激活。执行顺序：提供方契约与迁移 → Cloud 业务 → Agent 执行 → Desktop 桥与 Vue → 真实验证及旧实现删除。每一任务先反例验证，再实现和定向回归；新迁移不修改旧建库链。

## Done When

- 一条真实 B站和百度接入/更新闭环通过；原值可核实保留，保护失败不写，跨平台未改，重复/迟到结果不重放；凭证页面只展示确认值，内部版本不进入运营流程。
- 对应 M2-D 成功事实和禁止假成功条件逐项验证，数据库、真实本机效果、Cloud 投影与页面结果一致。
- 提供方契约、消费者、定向测试与真实验收有证据；独立 review 后按各仓独立提交。
- 不扩入接码自动化、链接换绑、凭证历史产品、审计/审批或永久兼容层。

## References

- Product: `docs/product/prd/详细文档/第三章_用户与账号管理.md`
- Engineering: `docs/engineering/specs/social-accounts.md`
- Decision: `docs/decisions/0030-social-account-rebuild.md`
- UI: `example/proto/social-accounts/index.html`；`docs/standards/frontend/AdminUI页面规范.md`、`前端交互规范.md`、`用户反馈规范.md`。
