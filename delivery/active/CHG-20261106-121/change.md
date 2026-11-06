---
id: CHG-20261106-121
parent: delivery/milestones/M4-content-production.md#m4-o-resource-composition-cutover
status: IMPLEMENTING
depends_on: []
affected_repos: ["wt-media-workspace", "wt-media-cloud"]
risk: H
---

# CHG-20261106-121: 存储位置与历史读取迁移

## Change

1. 存储层位置解析：新引用包含存储标识和完整key，旧key按legacy配置读取；测试新旧签名/跨目录/无效位置。配置default与online同步，凭据不入库。
2. 新素材直接上传正式ID键并校验，拒绝不同内容覆盖；成片上传前分配ID，直接写正式ID键，成功事务保持原语义。测试重复/并发/取消/未知提交不假成功。
3. Cloud迁移CLI及repository：盘点material/composite_output/compose_task/file_transfer引用，先复制逐项核验再CAS切换，缺失冲突报告，可重跑；不修改历史快照或删除旧对象。
4. 实际环境执行迁移并验证历史与新增的签名读取及摘要，相关Go回归、构建和独立审查，按存储边界/写入/迁移分别提交。

## Done When

- [ ] 对应M4-O交付项真实结果可读回，失败行为经过验证，不借其他CHG的PASS替代。
- [ ] 修改按所有权提交，相关测试/构建通过，独立Review和PR合并后回写事实。

## References

- docs/product/prd/详细文档/第五章_素材生产.md#510-合成与资源管理增量2026-11-06-用户确认执行
- docs/decisions/0032-compose-resources-and-template-cutover.md
- docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md

## Constraints

按用户要求在原仓库分支执行，不创建worktree；不打印/提交AK/SK。角色与业务事实仍在Cloud，Workspace不承载运行代码。按依赖完成后自行启动后续已授权任务。
