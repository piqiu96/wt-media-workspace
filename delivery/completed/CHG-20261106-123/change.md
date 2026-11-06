---
id: CHG-20261106-123
parent: delivery/milestones/M4-content-production.md#m4-o-resource-composition-cutover
status: DONE
depends_on: ["CHG-20261106-122"]
dependency_merge_commits: {"CHG-20261106-122": {"wt-media-workspace": "1d0057b4709b8f8877086513c5085b78016ebc4d", "wt-media-cloud": "2043fe1933061938dd857d210ec44f24f60af9be"}}
affected_repos: ["wt-media-workspace", "wt-media-cloud"]
risk: H
---

# CHG-20261106-123: build-slice-video 自动切片库

## Change

Cloud候选抓取/本地检查/裁剪/上传/索引脚本与Skill源；一次简单适用判断；有限候选、去重、同源稳定命名、并发索引保护；实际抓取切片入库。

## Done When

- [x] 对应M4-O交付项真实结果可读回，失败行为经过验证，不借其他CHG的PASS替代。
- [x] 修改按所有权提交，相关测试/构建通过，独立Review和PR合并后回写事实。

## References

- docs/product/prd/详细文档/第五章_素材生产.md#510-合成与资源管理增量2026-11-06-用户确认执行
- docs/decisions/0032-compose-resources-and-template-cutover.md
- docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md

## Constraints

按用户要求在原仓库分支执行，不创建worktree；不打印/提交AK/SK。角色与业务事实仍在Cloud，Workspace不承载运行代码。按依赖完成后自行启动后续已授权任务。

## Execution details

1. Cloud CLI `slice-video prepare`复用抖音关键词/ID/URL客户端，限制候选数、下载大小及执行时间，下载到独立本地任务目录；校验可解码、连续时长和音轨，生成分布采样画面与音频供一次适用判断，失败自动跳过。
2. `publish`读取Skill的真实适用判断JSON；不适用删除本地候选并继续，适用按短标题、序号裁剪带原声片段，完整解码/摘要校验后不可变上传。数据库保存同源名称与参数，专用连接的库级锁保护名称和index更新；已验证源/片段可恢复，不引入常驻模型服务。
3. Workspace Skill在有限目标/候选预算内自动编排prepare→判断→publish；源码在skills/cloud/build-slice-video，分发后不复制运行代码。实际抖音抓取、拒绝与可用切片入库/读回；相关单测、迁移、Review与独立合并。

## Current facts and verification

CHG122两仓已合并，文件ID3保留给后续合成。Cloud拥有现成抖音客户端、来源下载、ffprobe与不可变存储；随机片尾池为空。只读取低层关键词/详情接口，不开启已暂停的作者发现产品。运行参数置于Cloud配置及线上模板；名称和索引是Cloud事实，模型只决定适用与短标题。每步按测试/实际读回记录evidence；提交边界为运行工具与持久化、Skill与治理、验收记录。

## Acceptance

Cloud PR35 CI与实际切片入库/读回、同源重试、并发锁和命名归属验证PASS，已合并并更新本地main：`9ddfacab5d62802dadd8dfd27d4d55ea271a8593`。Skill校验/分发、独立前向测试修复及Workspace190项测试PASS；真实新增两条6秒配乐切片已在wt-media可读，详见evidence/slice-library-verification.md。本轮本地原片、采样和裁剪临时目录已清理，判断和报告保留本机临时报告。
