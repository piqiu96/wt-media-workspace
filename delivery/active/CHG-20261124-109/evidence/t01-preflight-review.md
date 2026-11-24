# CHG109 定义与实现落点预审

2026-11-25。本阶段只读核对正式产品、工程、109清单与现有108源码，未调用真实平台、未写业务数据库。

- 依赖：108 Cloud/Agent/Desktop分别合并0d5667c、dc6451a、b623b3c，Workspace实际合并bf190c9；四仓本地main已核对。109官方start退出0且四仓切换独立chg/CHG-20261124-109，当前唯一Active。
- 输入：用户已确认的计划简化规则；PRD6.2、工程2.3/4、既有Cloud web/example计划与批次原型。用户要求必须参考example，原型完成后固定本轮SHA，正式Vue不依赖example Runtime。
- 独立预审4P1/2P2与实现方只读调查相互核对后收敛：首次确认逐批冻结完整选择和缺口、跨批同平台重复成片拒绝；全部已启动前缀真实未决；全计划停止覆盖提交许可；共享事务与统一锁序；10%可直接移交而不额外要求人工结束批；正常审核/停查待核实/已核实未公开可判定。
- 最小技术方案：108提取接收同一tx的start内核；plan外层先锁plan及按ID全部batch，同事务提交首批task/占用/授权/游标。外部文件/模型仍事务外。无workflow、租约或第二执行器。
- 确认采用服务端basis摘要，包含全部前缀任务、位置、核验及最新人工事实和按当前时间判定的verification_required；事务内重算且重跑所有门槛，不因plan revision未变放行旧确认。
- 原任务resolve四种结论复用，最小补齐本人reviewing核实；管理他人仍仅合法公开补录。最新人工投影与原审计保留，未公开失败必须可信关闭/no_publishable_work/真实依据，不把超时或备注当失败。原submission/attempt/occupation均保留。
- 后端调查结论：契约在Cloud新增publication-plan.openapi.yaml；数据新plan/batch关联和冻结选择，Task不冗余plan_id；Scheduler接现有worker。Local plan续编由Agent提供方扩展，Desktop消费。当前无阻断业务疑问。

本记录为定义/源码审查结果，不是实现完成、测试通过或真实E2E证据。各实现Task仍按清单顺序执行。

## 原型基线完成

Cloud固定930553217cf5a3c8a1750178da4974d5b46dfeac，22文件仅web/example。沿既有PlanPage/PlanList/PlanDetail/PublishComposer/BatchManager/BatchDetailContent/common，隔离review=chg109，默认/107/108保留。页面映射在Cloud原型README。

实现方：366领域单测、34旧计划、21 example、16 Chromium（109专项3+旧五文件13）、example构建通过。根独立执行`npm run test:publishing-prototype`退出0，30文件366通过，日志/tmp/chg109-t01-prototype-root.log；逐张查看/private/tmp/wt-chg109-review的准备、首启、推进表、只读Drawer、10%/20%、零分母、人工未知/暂停、停查核实、重复成片、审核阻结束/缺口结束及两角色列表截图，布局/关键按钮与本轮规则相符。

CUA原型连接连续超时，未通过CUA点击fixture；已结束活动。采用上述实际Chromium截图独立审阅及浏览器交互断言，不冒称根做过失败的CUA交互。原型全部数据为演示，不代替T08真实发布/E2E。
