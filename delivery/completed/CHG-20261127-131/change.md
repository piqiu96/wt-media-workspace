---
id: CHG-20261127-131
parent: delivery/milestones/M-publishing-operations.md#B站作品指标
status: DONE
depends_on: []
affected_repos: ["wt-media-cloud", "wt-media-agent", "wt-media-desktop", "wt-media-workspace"]
risk: M
merge_commits: {"wt-media-cloud":"ca49da81bd99fef6417cc098b8452e4074692bb1","wt-media-agent":"e7889f98eaa11ee5aaeeea7a0ff5d267fd659a84","wt-media-desktop":"5753a81e9d47d9ade493a08bcc988b4767517e65","wt-media-workspace":"521d2edcf95b15593366207baab29f543d4bd0b6"}
---

# CHG-20261127-131：B站作品六项指标

## Change

用户2026-11-27确认执行：作品列表/详情展示B站播放、点赞、收藏、投币、评论、弹幕累计值，定时更新、手动刷新、最后更新时间；未知显示“—”，真实零显示0，失败保留旧值且不影响发布结果。独立于130发布验收，从各仓origin/main独立工作树实施，不修改原工作树原型。已有作品模型/鉴权不依赖130；已有B站作品用于真实只读验收。

Desktop仅同步兼容新增的契约版本锁，不复制业务源码。

Agent通过固定公开详情API采集，不读取CK、不操作浏览器；Cloud保留最新指标与历史快照。Cloud提供owner-scoped领取/回报，公开API也核对aid与UID。领取租约避免多Agent重复，过期可重领、旧回报不能覆盖新值。首次及手动请求排队，正常每小时更新，失败退避；仅运行中的Local Agent定时采集，离线保留旧值并显示等待。普通操作者仅本人、同团队高级操作者按既有类目范围读；执行仅本人作品。可读管理角色可发出刷新请求，由作品负责人Agent执行。

不含分享、百度、综合看板、互动操作、开放平台申请；不修改发布证明/成功率。接口为兼容新增，提供方先定义契约。

顺序：1定义契约/迁移；2 Cloud存取、权限、领取回报；3 Agent HTTP采集及Local/Sidecar轮询；4 共享Vue列表/详情与刷新等待/失败；5 单测、隔离MySQL、真实API及浏览器走查；6提交PR和验证证据。

原型输入：Cloud原工作树 `web/example/proto/publishing-design/works/WorksPage.vue`（核心指标紧凑列、详情统计卡片）；原型新增/复刻/观察周期不在本次范围。

References: [发布工程](../../../docs/engineering/specs/publishing-management.md)、[Contract ownership](../../../docs/contracts/ownership.md)。

## Done When

- [x] 六项最新值和更新时间在列表/详情可见，真实0与未知有区别。
- [x] 手动刷新和自动到期由Agent真实API采集并读回，原aid/UID一致，原发布事实不变。
- [x] 失败/限流/错误UID/字段缺失不写假0，保留最后成功值；重试退避。
- [x] 角色/类目范围、多领取竞争、租约过期及迟到回报验证通过，历史快照可追溯。
- [x] 定向Go/Python/Vue测试、真实HTTP到Cloud到浏览器全流程、独立PR及CI证据完成；不以mock代替真实验收。

技术交付完成：Cloud PR60、Agent PR22、Desktop PR21已merge commit合入main并本地main核对；Workspace PR73随本记录收口。最终Cloud CI45877466848成功，最新8c0b121自动Code Review无新发现；正式Sidecar/安装版/浏览器和组合测试均通过。CHG130的整体发布签收不由本项代替，用户最终整体验收仍保留。
