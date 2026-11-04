---
id: CHG-20261105-117
parent: delivery/milestones/M4-content-production.md#m4-m-output-assets
status: PLANNED
depends_on: ["CHG-20261105-116"]
affected_repos: ["wt-media-cloud"]
risk: H
---

# CHG-20261105-117：成片资产视图与文件信息

## Change

落地按素材 ID 聚合的成片批次和成片列表、稳定快照、视频信息／可用性、下载与再次制作。去发布只交付已确认的统一新建入口边界；尚无发布领域真实能力时明确不可用，不伪造安排或发布结果。

用户于 2026-11-05 授权自行拆分并连续推进内容生产全量落地、调试与视觉走查；无需每个 CHG 结束再请求启动下一项。各依赖仍须验证、独立提交与合并后再启动，不能用离线原型证据代替运行结果。

## Done When

- 权限过滤后聚合／分页，跨策略跨任务批次按素材 ID 汇总，详情围绕实际成片。
- 成片详情无封面占位，ID／状态在基本信息，视频信息展开且文件名可访问，元数据真实，历史配置不漂移。
- 对象核验、视频状态、当前设备下载操作一致；对象丢失不回写合成失败，无冗余可下载文案。
- 再次制作进入新建确认并产生新批次；平台候选来源仅抖音、目标无抖音；发布能力未交付不伪造事实。
- 成片 API／合同、权限／聚合／文件测试、Web／Desktop 构建及页面走查通过。

## References

- 产品：`docs/product/prd/详细文档/第五章_素材生产.md`
- 工程：`docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md`
- 决策：`docs/decisions/0031-content-production-batches-and-manual-reproduction.md`
- 原型：`example/proto/content-operations/index.html`
- 公共规范：`docs/standards/frontend/README.md`

## Constraints

不实现发布领域的执行器／多日编排、不引入 Redis／MQ／工作流、不改变 Agent 与 Desktop 本机授权。正式业务规则已确认，缺失后端能力按本 CHG 实现；真正未确认的业务分叉保留明确阻塞，不通过虚构数据绕过。
