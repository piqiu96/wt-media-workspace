# CHG109 T03 数据层验证

2026-11-25，Cloud f0f19b32a0c722c4a8b8227ce3e45b42600059a8。

迁移118新增plan及batch关联/冻结选择/移交字段，Task最新人工核实小投影；Task不冗余plan_id。数据层Create/Get/ByRequest/EditStructure与107保存父计划锁、骨架列表过滤。首次创建零task/占用；逐格守恒、稳定归属、目标变化确认失效、终止不复活、双封面引用回滚及修订竞争覆盖。

- RED：缺Plan模型和方法，/tmp/chg109-t03-red.log。
- 实现方`WT_MEDIA_TEST_LIVE_DB=1 WT_MEDIA_CLOUD_HOME="$PWD" go test ./internal/modules/publish/repository -run TestPlan -count=1`，4项3.157s通过，/tmp/chg109-t03-mysql-final.log。
- 完整repo同env去掉-run，最终72.016s通过，/tmp/chg109-t03-mysql-full-final.log。首轮历史pre118迁移fixture因最新Task写入新字段失败，3个原Omit列表仅追加新字段，保留旧schema及原断言后完整重跑，不跳过历史测试。
- `go test ./...`通过，/tmp/chg109-t03-go-full.log。
- 根独立同TestPlan命令4项2.564s通过，/tmp/chg109-t03-root-mysql.log；独立审查者4项2.555s通过，源码限定审查无P1/P2。

采用本仓既有隔离数据库fixture，未修改实际业务DB。迁移体系forward-only，reverse只在TestPlanMigrationKeepsLegacyRowsAndCanReverseInDisposableSchema显式反向DDL验证旧行保留，不新增loader会执行的down.sql。SQL DATE读成RFC3339问题已由真实roundtrip断言发现并修正，API保持YYYY-MM-DD。

T04权限/查询/AI、T05执行推进、T06结果与T07页面仍待完成；不把本次数据验证当运行闭环或真实E2E。
