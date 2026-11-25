# CHG112 验证

## 数字输入

固定原型9305532的example/common/number-stepper.css此前仅由example/main.ts加载，正式页未采用。正式模块按batch-editor范围采用样式，不引入example运行依赖；沿用TDesign输入、步进、禁用与校验。

新增浏览器断言在修复前失败（高度32而非36，/tmp/chg112-stepper-before.log）；修复后完整批次浏览器脚本PASS（/tmp/chg112-stepper-after.log），连体外框/分段无间距/键盘上下步进验证通过；定向范围内创建请求未知恢复和编辑保存等既有回归同时通过。Cloud数值控件提交见本CHG PR。流程Q-01仍等待用户答复，未提前实现导航变化。
