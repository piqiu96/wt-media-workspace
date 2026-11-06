---
id: CHG-20261106-121
parent: delivery/milestones/M4-content-production.md#m4-o-resource-composition-cutover
status: DONE
depends_on: []
affected_repos: ["wt-media-workspace", "wt-media-cloud"]
risk: H
---

# CHG-20261106-121: 存储位置与迁移基础

## Change

1. 存储层位置解析：新引用包含存储标识和完整key，旧key按legacy配置读取；测试新旧签名/跨目录/无效位置。配置default与online同步，凭据不入库。
2. 新素材直接上传正式ID键并校验，拒绝不同内容覆盖；成片上传前分配ID，直接写正式ID键，成功事务保持原语义。测试重复/并发/取消/未知提交不假成功。
3. Cloud迁移CLI及repository：盘点material/composite_output/compose_task/file_transfer引用，先复制逐项核验再CAS切换，缺失冲突报告，可重跑；不修改历史快照或删除旧对象。
4. 验证新bucket读写、幂等和跨客户端并发冲突；执行历史盘点与迁移预检，相关Go回归、构建和独立审查。历史复制/引用切换及下载验收归CHG125，须取得旧bucket读取权限后完成，不以工具实现代替迁移成功。

## Done When

- [x] 新位置和写入保护真实读回，迁移工具及失败不切换行为通过验证；旧bucket权限问题及移交CHG125的实际迁移明确记录。
- [x] 修改按所有权提交，相关测试/构建通过，独立Review和PR合并后回写事实。

## References

- docs/product/prd/详细文档/第五章_素材生产.md#510-合成与资源管理增量2026-11-06-用户确认执行
- docs/decisions/0032-compose-resources-and-template-cutover.md
- docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md

## Constraints

按用户要求在原仓库分支执行，不创建worktree；不打印/提交AK/SK。角色与业务事实仍在Cloud，Workspace不承载运行代码。按依赖完成后自行启动后续已授权任务。

## Checkpoint

- 位置解析与不可变上传已实现，Cloud提交见Git；已有字段编码s3存储标识/完整key，旧逻辑key保留legacy读取。
- 素材ID直接上传、成片ID独立分配后上传已实现；输出写入与任务成功仍在原事务。
- `go test ./internal/infra/storage ./internal/config ./internal/jobs ./internal/modules/production/service ./internal/modules/production/repository` 各包通过；位置/冲突/分配守卫测试先失败再通过。
- 下一项：迁移盘点/复制/核验/CAS工具，真实对象与历史引用验证，完整回归和独立review。
- 用户授权整体自动继续；不建立额外任务账本、不使用worktree。

## Scope clarification

实际预检发现当前AK/SK可访问wt-media，但读取旧data全部AccessDenied。未切换118处引用；历史迁移及历史下载验收明确移至CHG125，不宣称迁移成功。本CHG先交付经真实验证的新写入边界和可重跑工具，使独立文件管理/切片/模板实现继续。整体用户授权范围不变，CHG125仍必须完成旧数据复制核验和引用切换。

## Acceptance

新bucket全字节读回、同内容幂等、不同内容并发拒绝、缺少共享保护拒绝写入、迁移摘要/冲突/不切换失败引用均通过；完整Go回归、190项Workspace测试、治理检查及恢复后的环境门禁通过。独立Review无阻断问题。Cloud PR33已合并，merge 58d409e0843b05b1cec71ca6652065bcd8eabe50；Workspace定义与证据随本收口PR合并。

本CHG不等于历史迁移完成。118处引用未切换，53个旧位置待有效来源；此项及桌面实际业务全链验收已经明确移交CHG125。
