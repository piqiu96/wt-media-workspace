---
id: CHG-20261105-118
parent: delivery/milestones/M4-content-production.md#m4-n-production-acceptance
status: PLANNED
depends_on: ["CHG-20261105-117"]
affected_repos: ["wt-media-cloud"]
risk: H
---

# CHG-20261105-118：内容生产全链调试与视觉验收准备

## Change

从最新源代码启动 Cloud、Worker、Scheduler、Web、Agent 与 Desktop，完成三角色、真实输入／输出、失败恢复及全页面视觉检查，修复验收范围内问题，保留供次日人工走查的入口。

用户于 2026-11-05 授权自行拆分并连续推进内容生产全量落地、调试与视觉走查；无需每个 CHG 结束再请求启动下一项。各依赖仍须验证、独立提交与合并后再启动，不能用离线原型证据代替运行结果。

## Done When

- 使用固定开发数据库和最新构建通过环境新鲜度验证；未通过项如实阻塞而不冒充完成。
- 真实视频经多组／多份、策略立即／定时与人工任务形成成片，按存储／数据库／API／页面对账。
- 重放、并发、额度、越权、取消／失败／核实恢复及下载文件完整性通过实际检查。
- 素材库、我的素材、策略、任务批次／列表、成片批次／列表在典型及窄屏走查，公共规范一致。
- 自审、差异、构建与相关回归完成，记录准确入口及未验证边界；用户次日人工签收保持待验收。

## References

- 产品：`docs/product/prd/详细文档/第五章_素材生产.md`
- 工程：`docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md`
- 决策：`docs/decisions/0031-content-production-batches-and-manual-reproduction.md`
- 原型：`example/proto/content-operations/index.html`
- 公共规范：`docs/standards/frontend/README.md`

## Constraints

不实现发布领域的执行器／多日编排、不引入 Redis／MQ／工作流、不改变 Agent 与 Desktop 本机授权。正式业务规则已确认，缺失后端能力按本 CHG 实现；真正未确认的业务分叉保留明确阻塞，不通过虚构数据绕过。
