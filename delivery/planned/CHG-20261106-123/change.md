---
id: CHG-20261106-123
parent: delivery/milestones/M4-content-production.md#m4-o-resource-composition-cutover
status: PLANNED
depends_on: ["CHG-20261106-122"]
affected_repos: ["wt-media-workspace", "wt-media-cloud"]
risk: H
---

# CHG-20261106-123: build-slice-video 自动切片库

## Change

Cloud候选抓取/本地检查/裁剪/上传/索引脚本与Skill源；一次简单适用判断；有限候选、去重、同源稳定命名、并发索引保护；实际抓取切片入库。

## Done When

- [ ] 对应M4-O交付项真实结果可读回，失败行为经过验证，不借其他CHG的PASS替代。
- [ ] 修改按所有权提交，相关测试/构建通过，独立Review和PR合并后回写事实。

## References

- docs/product/prd/详细文档/第五章_素材生产.md#510-合成与资源管理增量2026-11-06-用户确认执行
- docs/decisions/0032-compose-resources-and-template-cutover.md
- docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md

## Constraints

按用户要求在原仓库分支执行，不创建worktree；不打印/提交AK/SK。角色与业务事实仍在Cloud，Workspace不承载运行代码。按依赖完成后自行启动后续已授权任务。
