---
id: CHG-20261106-125
parent: delivery/milestones/M4-content-production.md#m4-o-resource-composition-cutover
status: IMPLEMENTING
depends_on: ["CHG-20261106-124"]
dependency_merge_commits: {"CHG-20261106-124": {"wt-media-cloud": "464361a51332fea02e1e3401aeeb6061a5bde3cc", "wt-media-workspace": "880b01de43210a3b659a23e21ada0a1927d4dd69"}}
affected_repos: ["wt-media-workspace", "wt-media-cloud"]
risk: H
---

# CHG-20261106-125: 资源合成全链验收及旧模板清理

## Change

用户最新决定：旧数据直接删除，不再复制迁移。先盘点旧存储素材/成片及关联任务/传输依赖，保存本地清理清单后按旧位置谓词清理；保留wt-media新增资产。无法访问的旧bucket对象不宣称已删除；清理后列表/下载不得继续暴露失效旧引用。结束或明确拒绝旧模板在途后清理旧目录数据和执行代码；历史只读保留；运营文件URL到切片到策略/任务到成片/Agent下载全链验证。

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
