---
id: CHG-20261126-129
parent: delivery/milestones/M-publishing-operations.md#广告画中画成片准备
status: IMPLEMENTING
depends_on: ["CHG-20261126-128"]
dependency_merge_commits: {"CHG-20261126-128":{"wt-media-cloud":"eb1355ec1c202eedd4e9cf58d64402ef70d77f08","wt-media-workspace":"134ec829a515d7daee563b58c48945f0cd12ac89"}}
affected_repos: ["wt-media-cloud", "wt-media-workspace"]
risk: H
---

# CHG-20261126-129：广告画中画与片尾合成模式

## Change

交付不含开头引导的“正片前段→广告画中画→正片后段→片尾”完整合成能力。用户已确认：沿现有规则，用插入点起等长源画面作模糊背景，前景播放广告且只播广告声音，结束后正片从原插入点继续，最后接现有片尾。

建议注册独立ad_pip_ending v1，复用现有Resources/Compile、存储、任务快照和FFmpeg执行底座，保留dynamic_pip_ending v1及历史执行语义。已确认执行该模板方案，当前已实施并验证三条真实任务来源；比较、参数、接口、9步任务与验收见[plan.md](plan.md)。不改Agent为视频执行器。

## Done When

- [ ] 模板可用于策略新增/复制/详情与手动/立即/定时创建任务；不要求开头URL，不读取开头资源。
- [ ] 真实FFmpeg、对象存储、成片预览/下载及再次制作闭环通过，画面/声音/插入点/片尾/总时长逐项实测。
- [ ] 新任务重新随机，原任务重试沿冻结种子/资源/时间线；短源、无音轨、竖源、坏广告、片尾池异常及中断恢复明确且无假成片。
- [ ] 编码自测→E2E→浏览器实际播放并听音→新包走查→PR/CI/合入归档；新成片为130真实发布输入。
