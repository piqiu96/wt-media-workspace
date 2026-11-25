# CHG112 验证

## 数字输入

固定原型9305532的example/common/number-stepper.css此前仅由example/main.ts加载，正式页未采用。正式模块按batch-editor范围采用样式，不引入example运行依赖；沿用TDesign输入、步进、禁用与校验。

新增浏览器断言在修复前失败（高度32而非36，/tmp/chg112-stepper-before.log）；修复后完整批次浏览器脚本PASS（/tmp/chg112-stepper-after.log），连体外框/分段无间距/键盘上下步进验证通过；定向范围内创建请求未知恢复和编辑保存等既有回归同时通过。Cloud数值控件提交见本CHG PR。用户随后确认Q-01，按本次配置单向流转、保存后首次启动前可重新编辑的边界实施。

## 资源确认与异常

Cloud1974df4恢复数字控件；后续提交实现确认摘要与单向内容准备，并保持服务端原保存/编辑/启动契约。修改前导航回归因缺少确认资源/预览检查失败（/tmp/chg112-navigation-before.log）；修改后完整批次浏览器PASS（/tmp/chg112-batch-final.log）。

新增生产Vue的隔离浏览器矩阵test-publication-batch-wizard-browser.mjs，8组PASS：新建缺失名称/类目/无效数量、确认取消/缺口；Native草稿保存并重载；旧step1和step2草稿兼容；盘点失败且零候选保存仍保留目标；正式保存拒绝/Native写入失败保留输入；已存批次重新编辑及revision冲突；迟到校验不能覆盖新输入；Web刷新不假装持久化。无task/create或start副作用。Native持久化在受控边界模拟，实际包验证另记。

既有候选事实浏览器的占用提示断言仍使用旧文案，本轮改为已存在的规范化提示“成片已被当前平台任务占用”，未改生产提示或弱化不可用判断；8类候选事实及所选封面不混用缩略图PASS（/tmp/chg112-candidate-facts.log）。

本次全量Web168文件1244项PASS（/tmp/chg112-full-web.log）；Workspace220项PASS（/tmp/chg112-workspace-tests.log）。完整执行异常、计划回归及新安装版后续均完成，实际结果见下文；受控结果不替代真实安装走查。

## 实际安装版闭环

第一轮最终源f9835d9统一all --force-restart退出0：Cloud/worker/scheduler、Agent/BitBrowser、双dev、Desktop资产、CORS/登录及DMG新鲜度/挂载门禁全PASS（/tmp/chg112-environment.log）。operator01/operator123实际登录新挂载安装版。原本机新建草稿为空；仅本轮输入CHG112-步骤与续编验收-勿发布。

实际动作：缺少名称拦截并聚焦；连体目标/类目输入及加减可用；目标参考3、类目2、零候选缺口2明确；确认取消保留输入；确认后内容页无回资源入口；保存实际Native草稿→返回列表仍6批→新建恢复到内容页；总览可返回内容；缺失异常任务上限保存失败保持总览；补3后真实保存Cloud批次7，详情目标2/候选0/task0；继续配置重新进入资源页且目标可编辑。随后从原详情安全终止批次7，状态cancelled且footer仅返回。

只读MySQL核对2计划/7批次/12任务，batch7任务0。无新增投稿、AI调用或成片占用；真实计划/历史结果未变。

实际走查新增发现两项表现缺陷：修正名称后旧错误未清除；总览零候选提示仍引导返回资源。前者新增回归先失败1!=0（/tmp/chg112-installed-issues-before.log），后续修复分别按精确错误清除和总览继承资源确认边界处理，最终回归/新包复核另记。

完整执行baseline、列表动作、11异常受控场景与计划baseline/editor/G1/controls/stale已PASS。首次stopping与统一环境重启重叠导致浏览器关闭，环境完成后单独重跑PASS（/tmp/chg112-execution-stopping.log）；未改断言/超时。1440/1024完整批次浏览器与390宽新增向导矩阵均PASS。

最终生产代码b2bc9b9089aa4f2a887fbe00cf97cef18d8e5147；最终全量Web168/1244再次PASS（/tmp/chg112-full-web-final.log），新增8组矩阵与完整批次再次PASS（/tmp/chg112-wizard-final.log、/tmp/chg112-batch-final2.log）。Cloud PR55：https://github.com/piqiu96/wt-media-cloud/pull/55，全部CI与新安装版最终复核均PASS；无inline代码评论。

## 最终包复核

最终源b2bc9b9的Cloud生产构建PASS（/tmp/chg112-final-cloud-build.log）；统一all --force-restart再次退出0，所有服务/双端资产/登录/DMG新鲜度与挂载门禁PASS（/tmp/chg112-final-environment.log）。frontend0.1.0+b2bc9b9.dirty，dirty仅其他会话example修改，正式生产源码clean；shell0.1.0-local.0764ec2ed7，Agent0.3.0。

本机重新挂载并实际登录operator01：新建草稿为空，证明上轮保存正式配置后已清理续编；名称必填失败后填写名称，旧错误即时消失；连体输入/确认摘要/内容无回资源/总览空态一致，最终总览不再出现“返回资源配置”误导。未保存本轮复核输入，返回出现离开确认，选择离开后批次列表仍7条，工作环境绿色，未新建Cloud记录或草稿；保留该安装版供用户走查。

最终DMG：/Users/aqiuye/Develop/workspace/wt-media/wt-media-desktop/target/release/bundle/dmg/起飞_0.1.0-local.0764ec2ed7_aarch64.dmg。SHA256 f90a6b205dbb23d64498e436861d6ecb3e2f82a3b88fd29d412a297c0c18a487。

本次验证是配置/续编真实闭环加执行异常受控回归；未进行新增平台投稿，不把受控回执算新的真实发布证据。业务待确认项：无。用户最终整体签收仍另行。

两端角色入口补充：test-publication-role-browser.mjs的Cloud/Desktop各admin/operator/senior_operator矩阵PASS（/tmp/chg112-dual-role.log）；管理员保留管理但不能执行，运营与高级运营仅处理本人，查看他人任务不获得执行或草稿能力。

两端独立Vite入口隔离检查PASS，Cloud/Desktop缓存及业务页面互不污染，pageErrors为空、业务写入0（/tmp/chg112-entry-isolation.log）；本机无Playwright自带headless-shell，按脚本既有CHROMIUM_EXECUTABLE参数指定已安装官方Chrome后完成，没有变更测试或下载依赖。

PR55自动Codex审阅在标记ready后返回usage limits；summary虽标failed/has_unresolved_findings，但可见正文为无法完成审阅和额度耗尽，没有inline代码评论或具体缺陷。未将其宣称审阅通过，已逐文件复查新diff与上述业务/异常结果。

官方CHG验证补充：在Desktop已接管Agent端口后直接wt chg verify，Go模块与220项Workspace测试通过，但control verify按设计拒绝用headless凭据检查Desktop的Agent；未当作通过。按既有up流程切换至headless Agent后，正式wt chg verify CHG-20261125-112全部退出0（/tmp/chg112-chg-verify-final.log），覆盖Go模块、Workspace220及control环境/BitBrowser/资产/DMG/登录。随后launch-dmg重新移交Desktop，frontend仍b2bc9b9，DMG SHA256未变（/tmp/chg112-final-relaunch.log）。

Cloud CI run45621665492/job139231141665全部SUCCESS：Cloud/Web1m29s，原型预览21s、原型交互8m25s、迁移10s、双端构建51s及发布脚本均通过。PR55已合并并由GitHub API确认merged=true，merge commit f99119bd5295e9d11c1f2bd4c9faab16b3e3a937；main精确tree等于已验证b2bc9b9，未因合并元数据重建同一源码。
