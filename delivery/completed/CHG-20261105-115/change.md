---
id: CHG-20261105-115
parent: delivery/milestones/M4-content-production.md#m4-k-multiset-strategies
status: DONE
depends_on: []
affected_repos: ["wt-media-cloud"]
risk: H
merge_commits: {"wt-media-cloud": "73e8d067ffe8fea8f7784b58c6e860ec818281be"}
---

# CHG-20261105-115：多组成片策略与真实执行批次

## Change

将策略成片设置、固定模板参数权限、先排除再选入、只读立即执行预览、真实批次及多组多份创建接到 Cloud 现有 Worker。扩展提供方合同及策略共用页面，保留 /api/v1；MySQL 并发不换 Redis。

用户于 2026-11-05 授权自行拆分并连续推进内容生产全量落地、调试与视觉走查；无需每个 CHG 结束再请求启动下一项。各依赖仍须验证、独立提交与合并后再启动，不能用离线原型证据代替运行结果。

## Done When

- 策略可保存／读回独立组及模板参数；固定参数服务端拒绝覆盖，旧执行器继续读取最终快照。
- 立即执行预览只读、给逐条选材依据；确认时重验状态／额度，重复提交不重复建批次；零任务有运行记录无空批次。
- 真实 MySQL 多组多份展开及任务租约原子性验证；按素材计额、手动无每日限额，定时／立即使用相同判定。
- 提供方 OpenAPI／业务 Schema、相关单元测试、Web／Desktop 构建及策略页面走查通过。

## References

- 产品：`docs/product/prd/详细文档/第五章_素材生产.md`
- 工程：`docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md`
- 决策：`docs/decisions/0031-content-production-batches-and-manual-reproduction.md`
- 原型：`example/proto/content-operations/index.html`
- 公共规范：`docs/standards/frontend/README.md`

## Constraints

不实现发布领域的执行器／多日编排、不引入 Redis／MQ／工作流、不改变 Agent 与 Desktop 本机授权。正式业务规则已确认，缺失后端能力按本 CHG 实现；真正未确认的业务分叉保留明确阻塞，不通过虚构数据绕过。
