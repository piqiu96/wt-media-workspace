# CHG109 T05 启动与推进验证

2026-11-25，Cloud119b7266dc8a96228573fb720808296a748fd451，限定修复c2402e8a4ed7dccebf4d3d13a8c9e95db89f1c74。

共享108显式tx启动内核，plan→按ID全部batch→file/Profile→task/attempt；首启全批冻结确认范围，首批tasks/占用/授权/cursor/receipt原子提交。A09–13/A17与现有worker5秒推进；prefix未决/实时核实/basis、10%自动/20%确认/零skip、manualpause与永久停止分别控制。跨批重复成片拒，未来资源冲突不移交，旧key原回执优先，不重建任务。resource_wait_json仅当前适用位置的等待事实，不是新状态或许可，陈旧探测不覆盖pause/新位置，仍每次重检。

提供方d9f42f6明确已合法终止的下一位置AdvanceResult receipt可null，不伪造建单回执，仍走原零分母skip；schema先改再消费，最终11项schema根验证通过。

实现方fullGo /tmp/chg109-t05-go-full-final.log PASS；完整发布repo隔离MySQL73.298s /tmp/chg109-t05-mysql-full-final.log PASS，包含原108与新Plan10项主测试/阈值子场景。RED缺StartPlan内核日志/tmp/chg109-t05-red.log。父stop围栏单独写入、child cleanup前submitting拒绝和manualpause仍允许当前执行均有真实隔离断言。

根独立TestPlan全9.055s /tmp/chg109-t05-root-mysql.log。独立审查2P2：duplicate定位丢失，锁前时间跨24h仍可推进。c2402e8回退原行为复现RED（/tmp/chg109-t05-reviewfix-red.log），修后actualHTTP409保两批两row、原子rollback；Advance/PlanProgress/RecordWait父锁后新时钟，真MySQL阻塞锁跨逻辑截止拒推进。独立有限复验两项及HTTP错误体通过，无剩余T05阻断。

根最后发布包全通过/tmp/chg109-t05-root-fix-publish.log；限定duplicate/clock/resourcewait MySQL2.120s /tmp/chg109-t05-root-fix-mysql.log；正式schema11项通过。全部数据库验证为既有隔离fixture，未改实际业务数据。

T06最终核实/A15/停止后安全结束、T07正式页面及本机续编和T08真实计划E2E仍待完成，不把当前测试冒称全计划技术交付。
