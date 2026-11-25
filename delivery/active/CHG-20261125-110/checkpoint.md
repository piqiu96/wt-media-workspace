# CHG110 checkpoint — 2026-11-25

## 已完成

- 已按用户最新授权启动110；Workspace start预检通过，生成CURRENT_CONTEXT；Cloud/Workspace均chg/CHG-20261125-110。继承本地b84de4b、1b31e79、db6109e。
- 用户明确：原型为直接代码框架，接口差异自行解决，技术补充嵌入原区域；只有改变业务语义才需确认。已回写M7/M-plan及milestone README，旧归档不改。
- 新修复：原型目标数量/显式推荐（原型纯算法移植，正式allocate读回容量、未知/空资源不改原目标）；推荐参考只存本机草稿不传API。资源表行内本人账号/更换成片/移出沿原配对校验；封面可预览真实图片；计划01—04分区；标题编号aria-hidden修复。
- 全Web167文件1242测试已两轮通过；Cloud构建通过。最终完整自测仍1242通过；Cloud d659a34已提交，正在all强制重建。
- 受控浏览器7组主流程全部至少一次通过。完整异常11组中10组直接通过；stopping修复测试请求等待后重跑通过。计划标题编号导致两个旧heading定位失败，aria-hidden修复，plan/plan-editor均已重跑通过。
- 测试仍证明fixture流程，不证明真实发布；本次没有创建Cloud批次/计划/正式任务，没有运行AI/发布。DB目前plan1 ended、batch1cancelled/2-4ended（旧107-109证据）。

## 当前工作与下一步（持续执行，不等用户确认）

1. 已完成最终受控批次回归，修复slot旧行对象导致账号换后不能换回的问题。最终日志/tmp/chg110-batch-fixed.log、/tmp/chg110-web-final.log。完整环境执行session60558，日志/tmp/chg110-environment.log；继续检查全部门禁与安装版。
2. 受控脚本web/scripts/test-publication-{batch,batch-execution,plan,plan-editor,plan-g1-matrix,plan-controls,plan-stale}-browser.mjs；批次执行矩阵WT_MEDIA_BATCH_REVIEW=changed-revision,abandoned-navigation,rejected-replay,different-start-rejected,different-start,cross-tab,failed-task-actions,senior,manual-publication,late-publication,stopping。历史日志/tmp/chg110-execution-*.log，重跑/tmp/chg110-rerun-*.log。最新整体脚本定位已改原型checkbox/弹窗/查询/编辑，不降低断言。
3. 记录证据，提交Cloud仅本项源文件及脚本；不要git add整个web/example。Workspace有无关原型工作：Cloud preparationPreview.js与works/（近期可能继续扩大）不是本项，不覆盖/提交。固定原型SHA930553217cf5a3c8a1750178da4974d5b46dfeac。
4. 先保护当前安装版未提交的本机草稿（若需要保存只用本机续编，不点Cloud保存）。使用environment-bring-up重新all --force-restart、operator01密码使用会话已给值，禁止按skill重置。固定DB wt_media_cloud，DMG mount为../.local/m2b/desktop-review-mount/起飞.app（旧dmg-mount不可用）。读skill后运行正式harness，所有门禁PASS后真实E2E。
5. 真实本人资源预备、批次保存零任务/占用、编辑/续编/批量内容、真实AI授权范围内、计划两批准备/顺序推进/公开核实/结束、10%边界用受控矩阵与原事实。本人只有一个Profile按已确认向下兼容；需要可用新成片应通过compose正式流程生产，不改库造资源。outputs133—138 raw publish_status仍pending但不代表可用，必须查正式publication/output占用和video事实。
6. Web及新安装版以相同viewport逐屏对照example（含列表/新建三段/编辑/弹窗/详情/计划Drawer/返回/只读），完整运营视角记录实际与未覆盖，不再报告局部即整体通过。
7. SSH已验证可用！HTTPS push与gh token无效，但GIT_SSH_COMMAND='ssh -o BatchMode=yes -o ConnectTimeout=10' git ls-remote git@github.com:piqiu96/wt-media-cloud.git HEAD成功。后续可直接SSH push已授权分支，不改用户remote配置；PR可用已登录Chrome GitHub页面创建（gh无效不能用作阻塞全部交付）。完成PR/CI/问题修复再收口。

## CUA注意

- 全部真实UI操作只能cua_repl。IAB曾可用，当前getTab/createBrowserTab连续timeout，kernel重置。回退native Chrome可用。
- 原生Chrome getApp常选用户全屏B站窗口，不能直接发快捷键会发错窗口。先窗口菜单选择WT Media原型窗口，再对目标标准窗口执行performSecondaryAction(index,'Raise')，然后地址栏点击/粘贴/Return。这个Raise解决之前看到旧页面/键盘落错窗口的问题。
- Native既有独立Chrome窗两tab：prototype8768与正式localhost5173。实际页不保存业务；旧HMR多次堆积复制确认，应明确重载自己的测试tab而不清用户draft。
- CUA结束与非CUA边界先单独commentary browser-complete。无待人工takeover。
- 正式Web5173、desktopdev5174、Cloud8188；prototype8768存活。不要用old app当新包。

## 记录与禁止假成功

当前Cloud未提交修改均为本项运行时修复与脚本，另有用户原型变更需保留。尚未推送/建110 PR；尚未重建110安装包；尚未真实E2E；最终整体签收仍属于用户。不要再用旧109PASS、本轮单元/fixturePASS冒充本次完整交付。
