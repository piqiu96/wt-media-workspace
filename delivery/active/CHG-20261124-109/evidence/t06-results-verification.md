# CHG109 T06 核实与结束验证

2026-11-25，Cloud265ffa9545e6e3784199ecf8798493dfcbb4b826；ef12f354将PlanRecord.id按既有audit_logs改为opaque string，schema12项通过。

本人reviewing沿原resolve四结论，人工仍未知后仍可再核实；管理他人仍只合法published补录。最新manual投影包含uncertain，保留原result/hash/submission/占用，核实先Profile锁。真实matched work逐格计数，错关联不计公开。A15拒绝未处理batch/全部五类未决/任何reviewing/无work/旧revision及旧gap/未达成空原因，原目标不变；达成或保留缺口结束。全plan cancel等未知安全收尾再ended，仍审核可结束终止流程但保留核实入口，迟到公开只事实统计不重开/不改结束说明。

实现方完整Go/tmp/chg109-t06-go-full-final.log PASS；完整repo真隔离MySQL/tmp/chg109-t06-mysql-full-final.log90.216s PASS。首次失败的历史并发barrier要求两方同时过task更新，与新Profile先锁串行冲突；改为确认第二方受Profile阻塞、放行后仅一成功另一旧修订冲突，保留task/attempt/audit单写断言后全重跑，不跳过测试。

新结果专项12.192s；双格A超额不抵B的实际work记录回归1.553s。fixture使用service.NewExecutionStore(s.DB).RecordWork真实事务callback，不stub作品ID。

根独立发布包全PASS及结果专项真MySQL9.966s（/tmp/chg109-t06-root-publish.log、-root-mysql.log），正式schema12项通过。独立审查结果/双格/并发MySQL12.141s通过，无P1/P2。未改真实业务库；受控模型/数据库测试不是实际平台计划E2E，正式UI及本机续编留T07，真实全流程留T08。
