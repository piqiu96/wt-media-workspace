# CHG108 验收证据映射

2026-11-25。用户已确认可用 Profile 不足配置 N 时向下兼容。本轮真实本人可用百度 Profile 为1，配置并发5，实际第1组运行1条；没有把目标60或受控60条当作60次真实投稿。并发/故障受控验证与实际发布分别列出，Windows和未开放平台未记为实际通过。

| 项 | 受控验证（不等同真实多账号实发） | 本轮实际证据与当前结论 |
| --- | --- | --- |
| V01 | `TestBatchFirstStartRollsBackEveryTaskAndReplaysOriginalReceipt`；原键/并发登记和重启不进浏览器测试 | 原生batch2显式确认60目标/1候选/59缺口，只创建task12/attempt35；重启不增加任务或attempt。原回执恢复已通过原键回执与权威false修复及独立复验，真实HTTP另键拒绝不变task集合。PASS。 |
| V02 | `TestFixedGroupDoesNotRefillAndWaitsAcrossStoreRestart`；`test_group_dispatch_has_no_per_task_poll_delay` | 实际按唯一可用Profile下兼容，group1成员1，未为填满5等待；多成员/第二组间隔及组间重启由受控测试证明。100旧失败、100忙Profile与100旧单条queued混排均通过隔离MySQL修复/独立复审；真实多Profile未跑。PASS。 |
| V03 | `TestLiveExecutionProfileRaceAndLostHeartbeatKeepScene`；`TestPublishAndOriginalCheckDoNotShareAnActualProfile`；跨scope SQLite竞争只一方登记 | 真实发布和后续核验使用原本人Profile，未双开；跨批/跨平台竞争证据为隔离事务/本机受控记录，未宣称跨平台实发。独立资源准入及全局满早停已复验通过。PASS（技术边界）。 |
| V04 | `TestParkedAttemptsKeepWindowButReturnAutomaticSlot`；5停手/10窗口线程、旧owner未知容量、真实HTTPResponse慢字节截止 | 正常真实准备/上传/核验成功；慢流、失联、满容量和多人工现场为受控演练。PASS（技术边界）。 |
| V05 | `TestBatchExceptionLimitAndPauseAcknowledgementWithSixtyTasks`；`TestBatchMixedExceptionsCountTasksNotReviewingOrAttemptHistory` | 隔离MySQL覆盖两种策略、60任务、failed/human/uncertain去重、排除reviewing、同task第二attempt不增加异常。实际目标60/候选1未冒充60执行。PASS。 |
| V06 | 上述60任务暂停/新异常/旧修订确认测试；停车ACK负例 | 实际Web要求原因后终止batch1为cancelled，零任务，无恢复入口；异常暂停确认竞争为受控测试。PASS。 |
| V07 | 两个原场景/原线程继续；丢ACK同identity重用；跨owner自动容量及明确拒绝归还 | 实际正常路径未出现人工卡点，不宣称真实现场手工恢复；控制原attempt、输入和提交前边界由SQLite/线程/Cloud事务测试证明。PASS（技术边界）。 |
| V08 | `TestBatchStopAndSubmitCompeteWithoutReplayedPermission`；`TestBatchParentFencesSingleTaskStartAndRetry`；原结果包及满窗口补报 | 真实重建后task总数7→8、attempt34→35，task12仍一次attempt35；父paused/stopping/cancelled/ended防旁路由新专项验证。PASS。 |
| V09 | 本人/他人边界、公开work原子写、30/28/24=80%统计fixture | 真实task12→generation2 published observation（work_matched/publicly_accessible/scene_closed均true）→唯一work5，原attempt35/output134。旧UI汇总刷新问题已修并独立复审，最终fe741fe新包与Web均读回1/60·1.67%、待公开0、行已发布，关联work5/原task12/attempt35。PASS。 |
| V10 | `TestBatchFinishRejectsHumanAndUnknownWithoutChangingTheirHold`；`TestBatchFinishRequiresExactFailuresAndKeepsOccupancyAfterEnd`；原attempt安全放弃测试 | 隔离MySQL拒绝未决finish/错误失败集合，成功结束后保留占用且不能retry。真实batch1只证明未启动终止，不当作失败结束。PASS（技术边界）。 |
| V11 | 原型2512d342；production浏览器operator/admin/senior_operator合成权限和回跳；late-publication/stopping专项 | 实际macOS安装版与Web、1024宽度无全页溢出、原任务返回、开始后冻结、复制占用提示、真实投稿与核验已做；最终fe741fe源新包挂载校验通过，Web/安装版均完成公开统计及原任务读回；视口恢复默认。PASS（上述实际范围）。 |

## 关键来源

- Cloud运行实现7b4f523，原型/共用Vue沿用既有example，最后统计修复3fc7f6a；新增验收负例8ca5926为tests only，四项/六子场景隔离MySQL通过（日志`/tmp/chg108-batch-acceptance-final.log`）。根复核新测试与断言，未改变真实业务DB。
- Agent0d507e1全套949项和独立审查通过，Desktop ca44cba的560项通过/6既有ignore及打包检查通过；正式跨仓verify成功记录见implementation-review.md。
- 真实操作和数量见[安装版与Web记录](installed-e2e.json)；升级前后实际闭窗与门禁读回见[安全切换](legacy-cutover.md)。原型/三角色合成场景不能替代真实账号或平台事实。
- 三项CHG的用户最终整体验收仍按原授权在107–109技术交付后统一进行。


最终PR新增边界：a5cce77实际JSON保留批次空操作数组，7649e48 Chrome验证暂停/结束的失败任务隐藏重试/放弃而独立任务仍兼容；fe741fe隔离MySQL验证20 disabled/rebound旧核验之后第21有效项、原键优先、满窗口不扫描与24h截止，15项主测试通过，独立限定审查关闭。GitHub四条已知thread均在修复与复审后resolved。合并/CI为交付步骤，用户最后整体签收尚未发生。
