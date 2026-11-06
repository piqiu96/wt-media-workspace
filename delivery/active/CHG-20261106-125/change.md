---
id: CHG-20261106-125
parent: delivery/milestones/M4-content-production.md#m4-o-resource-composition-cutover
status: VERIFYING
depends_on: ["CHG-20261106-124"]
dependency_merge_commits: {"CHG-20261106-124": {"wt-media-cloud": "464361a51332fea02e1e3401aeeb6061a5bde3cc", "wt-media-workspace": "880b01de43210a3b659a23e21ada0a1927d4dd69"}}
affected_repos: ["wt-media-workspace", "wt-media-cloud"]
risk: H
---

# CHG-20261106-125: 资源合成全链验收及旧模板清理

## Change

用户最新决定：旧数据直接删除，不再复制迁移。先盘点旧存储素材/成片及关联任务/传输依赖，保存本地清理清单后按旧位置谓词清理；保留wt-media新增资产。无法访问的旧bucket对象不宣称已删除；清理后列表/下载不得继续暴露失效旧引用。结束或明确拒绝旧模板在途后清理旧目录数据和执行代码；未落入本次旧引用清理谓词的历史继续只读保留；旧引用关联历史按新授权删除；运营文件URL到切片到策略/任务到成片/Agent下载全链验证。

## Done When

- [ ] 对应M4-O交付项真实结果可读回，失败行为经过验证，不借其他CHG的PASS替代。
- [ ] 修改按所有权提交，相关测试/构建通过，独立Review和PR合并后回写事实。

## References

- docs/product/prd/详细文档/第五章_素材生产.md#510-合成与资源管理增量2026-11-06-用户确认执行
- docs/decisions/0032-compose-resources-and-template-cutover.md
- docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md

## Constraints

按用户要求在原仓库分支执行，不创建worktree；不打印/提交AK/SK。角色与业务事实仍在Cloud，Workspace不承载运行代码。按依赖完成后自行启动后续已授权任务。

## Implementation order

1. 盘点并保存本地旧引用与依赖记录，清理事务须拒绝在途任务和任何新 bucket 资产连带删除。通过实际数据库回滚测试验证保护条件。
2. 下线旧模板目录、策略及执行器，公共入口仅依赖资源计划/编译接口；保留通用生命周期、权限和重试测试。
3. 读回真实任务与成片，验证失败、取消、下载校验；顺序重建环境并完成可操作的桌面验收。
4. 独立 Review、各仓 PR 合并、事实与证据归档。

## Dependency merges

- CHG124 Cloud: `464361a51332fea02e1e3401aeeb6061a5bde3cc`
- CHG124 Workspace: `880b01de43210a3b659a23e21ada0a1927d4dd69`

## Current verification

旧对象盘点已完成：34素材、16成片、20旧任务、7旧策略、3旧模板，关联120传输记录。真实DB外层回滚测试已验证备份失败不删、在途拒绝、新桶对象保护、事务删除及重复空清理。2026-11-07已正式apply并复查旧引用集为空，备份仅保存在本机0600文件。真实任务709因Worker缺少配置初始化在输入检查阶段退出，已修复配置/检查器/共享内容claims；核对旧进程退出和未提交成片后，通过正式uncertain-review恢复同一快照任务。

实际任务709在同一快照下第2次尝试成功，成片128写入新目录，时间线49.166秒、广告11.3194秒开始。首次恢复验证发现成功任务仍携带旧错误投影，已修复正式恢复/成功提交时清空错误，尝试历史仍保留；数据修正migration101仅清理success任务旧错误。

Cloud PR37已合入本地main：`0d161df7580315eb00829ef40398813c01814fa9`，CI PASS（2m38s）；全量Go PASS含模板响应contract投影，Workspace190项测试PASS。最新main全环境重建PASS，DMG挂载及启动成功。桌面工具不能识别隐藏挂载目录，逐文件核对同次构建的两个应用包10个文件完全一致后，使用构建目录中的包正常显示native登录页；登录动作时Mac再次锁定，等待用户解锁。后续独立wt verify的代码测试PASS，环境检查因尚未登录运营账号、Agent未启动而FAIL，不能据此宣称下载已验收。
