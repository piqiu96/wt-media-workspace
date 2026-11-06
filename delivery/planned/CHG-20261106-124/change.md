---
id: CHG-20261106-124
parent: delivery/milestones/M4-content-production.md#m4-o-resource-composition-cutover
status: PLANNED
depends_on: ["CHG-20261106-123"]
affected_repos: ["wt-media-workspace", "wt-media-cloud"]
risk: H
---

# CHG-20261106-124: 五段模板和策略公共执行入口

## Change

定义并验证code/version执行器接口、完整策略默认及任务覆盖限制；实际时间线/种子/资源摘要快照；真实FFmpeg和失败/重试/取消；公共Vue参数接入。

## Done When

- [ ] 对应M4-O交付项真实结果可读回，失败行为经过验证，不借其他CHG的PASS替代。
- [ ] 修改按所有权提交，相关测试/构建通过，独立Review和PR合并后回写事实。

## References

- docs/product/prd/详细文档/第五章_素材生产.md#510-合成与资源管理增量2026-11-06-用户确认执行
- docs/decisions/0032-compose-resources-and-template-cutover.md
- docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md

## Constraints

按用户要求在原仓库分支执行，不创建worktree；不打印/提交AK/SK。角色与业务事实仍在Cloud，Workspace不承载运行代码。按依赖完成后自行启动后续已授权任务。
