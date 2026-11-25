# CHG113 详情验收

## 数据与原型差距

2026-11-25只读SQL：批次1为QA CHG107 配置保存1125-015314，已取消、started_at为空、目标三角洲60、candidates_count及JSON候选长度均0、task0；批次2才是目标60/候选1/task1且已结束。截图不是60条内容丢失。

固定原型9305532的BatchDetailContent/BatchContentTable以四列只读内容展示；正式BatchReadonlyBody另写原生六列表，无空态、无分页，额外堆积目标/缺口；取消前未启动也显示执行统计并重复执行设置。按原框架修复这些差异，批次目标、候选和task事实均保留。

新增生产路由浏览器先失败：未开始即取消仍显示执行情况，1!=0（/tmp/chg113-detail-before.log）。修复共享主体用于独立详情及计划Drawer，验证结果收齐后在此记录，不把既有测试数量当作本次详情已验收。

## 自测与受控浏览器

生产详情矩阵12类全部PASS（/tmp/chg113-detail-final.log）：未开始即取消且零内容、未开始零内容、config缺失不伪造0、未完善内容、13条分页及超长名称、多类目守恒明细、占用、资源目录失败、running/paused/stopping/ended。1440与390宽验证只读四列、无变更命令、文本夹行/完整title、空态及执行设置不重复。

计划详情三角色Drawer与返回位置PASS（/tmp/chg113-plan-drawer.log）；G1计划骨架配置/冻结及正式任务回链PASS（/tmp/chg113-plan-g1.log）。完整批次与112向导8组、执行baseline及列表状态/跨成员回归PASS（/tmp/chg113-batch-regression.log、/tmp/chg113-wizard-regression.log、/tmp/chg113-execution-regression.log、/tmp/chg113-list-regression.log）。本次Web168文件1244项PASS（/tmp/chg113-web-tests.log）。

生产源码提交bf6b2d1；新安装包与实际原数据走查正在完成，尚不以受控fixture认定安装版已通过。
