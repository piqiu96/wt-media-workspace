---
id: CHG-20261030-109
parent: delivery/milestones/M2-account-runtime.md#m2-d2-cookie-single
status: IMPLEMENTING
depends_on: ["CHG-20261030-108"]
affected_repos: ["wt-media-workspace", "wt-media-cloud", "wt-media-agent", "wt-media-desktop"]
risk: H
---

# CHG-20261030-109：单账号 Cookie 接入、更新与内部保护

## Change

先变更提供方 Cookie 契约，保留账号 original_cookie/active_cookie，增加 before_cookie 与当前 cookie_update JSON，打通单账号接入/更新；复用窗口/代理能力，在现有窗口记录保存当前 Cookie 操作占用，落实写前保留、平台隔离、身份核实和未知先核实。替换旧 read-sync 链路，不新增 Cookie 版本表或版本引用。

整体落地见[工程设计 §7](../../../docs/engineering/specs/social-accounts.md#7-整体落地方案)，表与接口见同文 §1～4。前置 CHG 完成并合入各仓 main 后再激活；按提供方契约 → 数据/业务 → 本机消费者及页面 → 真实验收推进，同阶段删除替代链路的废弃实现。具体代码拆分、迁移编号和测试由实施 Codex 决定，不预写文件级任务。

## Done When

- 一条真实 B站和百度接入/更新闭环通过；原值可核实保留，保护失败不写，跨平台未改，重复/迟到结果不重放；凭证页面区分最初输入与当前确认值，内部写前保留不进入运营操作流程。
- 对应 M2-D 成功事实和禁止假成功条件逐项验证，数据库、真实本机效果、Cloud 投影与页面结果一致。
- 提供方契约、消费者、定向测试与真实验收有证据；独立 review 后按各仓独立提交。
- 不扩入接码自动化、链接换绑、凭证历史产品、审计/审批或永久兼容层。

## References

- Product: `docs/product/prd/详细文档/第三章_用户与账号管理.md`
- Engineering: `docs/engineering/specs/social-accounts.md`
- Decision: `docs/decisions/0030-social-account-rebuild.md`
- UI: `example/proto/social-accounts/index.html`；`docs/standards/frontend/AdminUI页面规范.md`、`前端交互规范.md`、`用户反馈规范.md`。
