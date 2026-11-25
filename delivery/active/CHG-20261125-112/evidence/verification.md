# CHG112 验证

## 数字输入

固定原型9305532的example/common/number-stepper.css此前仅由example/main.ts加载，正式页未采用。正式模块按batch-editor范围采用样式，不引入example运行依赖；沿用TDesign输入、步进、禁用与校验。

新增浏览器断言在修复前失败（高度32而非36，/tmp/chg112-stepper-before.log）；修复后完整批次浏览器脚本PASS（/tmp/chg112-stepper-after.log），连体外框/分段无间距/键盘上下步进验证通过；定向范围内创建请求未知恢复和编辑保存等既有回归同时通过。Cloud数值控件提交见本CHG PR。用户随后确认Q-01，按本次配置单向流转、保存后首次启动前可重新编辑的边界实施。

## 资源确认与异常

Cloud1974df4恢复数字控件；后续提交实现确认摘要与单向内容准备，并保持服务端原保存/编辑/启动契约。修改前导航回归因缺少确认资源/预览检查失败（/tmp/chg112-navigation-before.log）；修改后完整批次浏览器PASS（/tmp/chg112-batch-final.log）。

新增生产Vue的隔离浏览器矩阵test-publication-batch-wizard-browser.mjs，8组PASS：新建缺失名称/类目/无效数量、确认取消/缺口；Native草稿保存并重载；旧step1和step2草稿兼容；盘点失败且零候选保存仍保留目标；正式保存拒绝/Native写入失败保留输入；已存批次重新编辑及revision冲突；迟到校验不能覆盖新输入；Web刷新不假装持久化。无task/create或start副作用。Native持久化在受控边界模拟，实际包验证另记。

既有候选事实浏览器的占用提示断言仍使用旧文案，本轮改为已存在的规范化提示“成片已被当前平台任务占用”，未改生产提示或弱化不可用判断；8类候选事实及所选封面不混用缩略图PASS（/tmp/chg112-candidate-facts.log）。

本次全量Web168文件1244项PASS（/tmp/chg112-full-web.log）；Workspace220项PASS（/tmp/chg112-workspace-tests.log）。完整执行异常、计划回归及新安装版仍待完成，不能以这些受控结果替代真实安装走查。
