# CHG113 详情验收

## 数据与原型差距

2026-11-25只读SQL：批次1为QA CHG107 配置保存1125-015314，已取消、started_at为空、目标三角洲60、candidates_count及JSON候选长度均0、task0；批次2才是目标60/候选1/task1且已结束。截图不是60条内容丢失。

固定原型9305532的BatchDetailContent/BatchContentTable以四列只读内容展示；正式BatchReadonlyBody另写原生六列表，无空态、无分页，额外堆积目标/缺口；取消前未启动也显示执行统计并重复执行设置。按原框架修复这些差异，批次目标、候选和task事实均保留。

新增生产路由浏览器先失败：未开始即取消仍显示执行情况，1!=0（/tmp/chg113-detail-before.log）。修复共享主体用于独立详情及计划Drawer，验证结果收齐后在此记录，不把既有测试数量当作本次详情已验收。
