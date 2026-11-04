---
id: CHG-20261105-116
parent: delivery/milestones/M4-content-production.md#m4-l-manual-batches
status: PLANNED
depends_on: ["CHG-20261105-115"]
affected_repos: ["wt-media-cloud"]
risk: H
---

# CHG-20261105-116：人工选材与任务批次工作台

## Change

落地人工新建、受权代选材、使用筛选、任务批次／列表及详情进度和批量恢复。任务仅调整模板开放参数，无增删成片设置；任务尝试吸收人工核实，读取不新增授权。

用户于 2026-11-05 授权自行拆分并连续推进内容生产全量落地、调试与视觉走查；无需每个 CHG 结束再请求启动下一项。各依赖仍须验证、独立提交与合并后再启动，不能用离线原型证据代替运行结果。

## Done When

- 新建任务名称在首项；按负责人工作集或同团队同类目素材库选材，加入／准备与取消的副作用正确。
- 重复制作新建与重放幂等、原任务重试分别验证；我的使用／团队使用不随代办人漂移。
- 批次行仅详情；全批统计不受局部筛选影响；取消与重试按实际范围／权限逐项返回，运行取消不假终态。
- 核实字段合表、旧读取接口收敛与清理逻辑同步；保留受保护恢复写入及两项确认；记录保留且不泄露依据。
- 任务及素材列表服务端分页，公共筛选日期、多选、参数弹窗与执行时间线通过功能／视觉检查。

## References

- 产品：`docs/product/prd/详细文档/第五章_素材生产.md`
- 工程：`docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md`
- 决策：`docs/decisions/0031-content-production-batches-and-manual-reproduction.md`
- 原型：`example/proto/content-operations/index.html`
- 公共规范：`docs/standards/frontend/README.md`

## Constraints

不实现发布领域的执行器／多日编排、不引入 Redis／MQ／工作流、不改变 Agent 与 Desktop 本机授权。正式业务规则已确认，缺失后端能力按本 CHG 实现；真正未确认的业务分叉保留明确阻塞，不通过虚构数据绕过。
