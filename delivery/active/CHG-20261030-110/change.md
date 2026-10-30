---
id: CHG-20261030-110
parent: delivery/milestones/M2-account-runtime.md#m2-d3-cookie-batch
status: IMPLEMENTING
depends_on: ["CHG-20261030-109"]
affected_repos: ["wt-media-workspace", "wt-media-cloud", "wt-media-agent", "wt-media-desktop"]
risk: H
---

# CHG-20261030-110：矩阵账号批量 Cookie 接入与结果处理

## Change

复用 109 单项能力，仅新增 media_account_import_batches：content_json 顶层保存批次补充信息，items 数组保存原始行号及单项过程；无独立明细表、K/V 单项结构或逐项 UUID。提供预览/确认、逐项窗口准备与接入、七计数、人工登录后继续、跳过恢复、重复提交与未知核实；完成最终批量入口及旧开户残余清理。

整体落地见[工程设计 §7](../../../docs/engineering/specs/social-accounts.md#7-整体落地方案)，表与接口见同文 §1～4。前置 CHG 完成并合入各仓 main 后再激活；按提供方契约 → 数据/业务 → 本机消费者及页面 → 真实验收推进，同阶段删除替代链路的废弃实现。具体代码拆分、迁移编号和测试由实施 Codex 决定，不预写文件级任务。

## Done When

- 真实小批次包含成功、无效、人工登录、跳过/恢复、重复 UID 与未知结果；每项状态和总计一致，成功不重放，关闭重进进度可读，预览无副作用，最终页面与原型一致。
- request_key 唯一约束、revision 条件更新、固定原行号、attempt 派生操作编号及跨批次窗口占用有反例验证；排序不改变存储身份，重复回报不覆盖新尝试。批次 JSON 容量按真实 Cookie 样本验证，成功项凭证正确转存账号。
- 对应 M2-D 成功事实和禁止假成功条件逐项验证，数据库、真实本机效果、Cloud 投影与页面结果一致。
- 提供方契约、消费者、定向测试与真实验收有证据；独立 review 后按各仓独立提交。
- 不扩入接码自动化、链接换绑、凭证历史产品、审计/审批或永久兼容层。

## References

- Product: `docs/product/prd/详细文档/第三章_用户与账号管理.md`
- Engineering: `docs/engineering/specs/social-accounts.md`
- Decision: `docs/decisions/0030-social-account-rebuild.md`
- UI: `example/proto/social-accounts/index.html`；`docs/standards/frontend/AdminUI页面规范.md`、`前端交互规范.md`、`用户反馈规范.md`。
