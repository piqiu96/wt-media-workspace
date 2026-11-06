---
id: CHG-20261106-124
parent: delivery/milestones/M4-content-production.md#m4-o-resource-composition-cutover
status: DONE
depends_on: ["CHG-20261106-123"]
dependency_merge_commits: {"CHG-20261106-123": {"wt-media-workspace": "fdd6652cfc11dc41fe96a3fb18b8cb917036516a", "wt-media-cloud": "9ddfacab5d62802dadd8dfd27d4d55ea271a8593"}}
affected_repos: ["wt-media-workspace", "wt-media-cloud"]
risk: H
---

# CHG-20261106-124: 五段模板和策略公共执行入口

## Change

定义并验证code/version执行器接口、完整策略默认及任务覆盖限制；实际时间线/种子/资源摘要快照；真实FFmpeg和失败/重试/取消；公共Vue参数接入。

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

1. 先以时间线/权限/资源冻结失败测试约束新模板：dynamic_pip_ending v1，按PRD5.10分配默认和权限；选段、广告出现时点、四次重叠和背景不足明确核验。运行默认从Cloud配置读取，策略各组补全默认并独立保存；普通任务只允许起止和缩短上限。
2. 执行器经code/version注册，使用通用资源声明和编译入口，公共领取/租约/重试/取消/上传提交不识别具体模板。原引导执行也接入通用接口；旧执行器最终清理归CHG125，不留新模板硬编码分支。通用资源解析支持平台文件令牌直接读取、私有S3切片索引及已防护的外部HTTPS下载。
3. 任务创建固定随机种子及技术默认快照；准备完成后保存资源位置/摘要/大小、实际时间线，按当前租约条件CAS固定。重试复用原资源及时间线，内容变化拒绝，不重新随机；旧任务不能换模板执行。
4. FFmpeg完成五段动态背景/保比例画中画/阴影/模糊/静音规则、实际转场和片尾淡出；实际解码、音画各自时长、最终上限验证。共用Vue接入URL、默认参数和运营权限，任务详情展示本次时间线。实际样片与失败/重试/取消，相关Go/前端测试和构建，独立Review后分仓合并。

## Current facts and boundaries

Cloud PR36已合并main（464361a51332fea02e1e3401aeeb6061a5bde3cc），公共任务与Runner使用ResourcePlan，执行器负责时间线和FFmpeg；任务覆盖由Schema及策略上限校验，三种创建路径固定技术配置与种子，资源准备按有效租约首次保存manifest。新模板已发布id10；旧模板仅保留临时公共入口适配，最终目录及执行实现清理归CHG125。真实DB、池路径、176.233秒/27.5秒渲染均已验证；平台实际任务709正在使用新桶material185及文件3/4，最终成片/Agent下载归CHG125继续核验。Mac锁定已请求用户解锁；本CHG不宣称native业务闭环完成。

## File mapping and commits

Cloud executor/compose负责计划与渲染；production service/repository/model负责快照、覆盖权限和生命周期；files service提供受令牌限制的内部资源读取；config及config_online放技术/模板默认；provider contracts记录新增任务事实；web/modules/compose提供共用表单/详情。提交按执行器/渲染、任务快照和资源、前端与契约分界；每步保留定向失败测试、实现、读回验证及evidence，最后执行相关回归。
