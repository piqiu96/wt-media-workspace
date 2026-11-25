# 状态与按钮走查

输入：用户三张人工截图、固定Cloud原型930553217cf5a3c8a1750178da4974d5b46dfeac，以及PRD6.2/6.3/6.8。batchLifecycle.js与plan/app.js当前源码对固定SHA无差异。检查共享Vue、正式服务端投影，未改其他会话example/docs-design。

| 位置 | 修改前 | 处理 |
| --- | --- | --- |
| 计划新建底栏（截图1） | 返回、保存本机续编、检查安排、创建计划 | 按原型返回、保存草稿、创建计划；校验并入创建，恢复只创建骨架/零任务占用的确认摘要 |
| 计划编辑 | 保存修改，可能与新建动作混淆 | 按原型保存；现有编辑不另存本机草稿 |
| 批次新建（截图3） | 保存续编 | 保存草稿；仍只保存在本机，未变为Cloud草稿对象 |
| 已结束批次列表（截图2） | 只有复制批次，详情仅可点名称 | 每个状态常驻详情，终态为详情/复制 |
| 批次未开始 | 配置就绪映射成待执行/待配置当作执行状态 | 执行状态统一未开始，配置就绪/待完善单独显示 |
| 批次运行/暂停/待处理 | 发布中或只有查看，控制仅详情可见 | 原型执行中/已暂停/待处理；列表补服务端允许的暂停、继续、结束、终止，走原确认/版本/请求恢复 |
| 批次终态详情 | 页底还有复制批次 | 按原型只读历史；复制保留在列表 |
| 历史失败 | 已结束失败仍算待办 | 已结束/取消的明确失败为历史；未决/待核实仍按实际计数，未知统计不当成0 |
| 计划待执行列表 | 执行条件不足时整个按钮消失 | 本人待执行计划保留禁用执行及先完成全部批次配置的原因；仅服务端允许后启用 |
| 计划列表动作顺序 | 详情总在执行前 | 原型执行/详情/编辑/终止；终态详情/复制 |
| 计划未达成结束 | 保留目标缺口且终态一律绿色 | 未达成结束，只有目标达成使用成功色 |
| 计划批次快捷操作 | 编辑配置、实心执行按钮 | 未配置去配置/已配置继续配置；原确认器以行内文字按钮呈现，命令权限未改 |

## 已核实且无需再询问

- 未开始批次的终止：服务端既有stop允许安全终止保存配置，并明确零正式任务；复用该接口，无新增删除或解锁语义。
- 草稿名称仅界面文案调整；本机保存边界不变。已开始计划仍冻结，无新增批次或补量。
- 正式安全收尾保留停止中及实际阶段，未伪造成已结束；只有可信公开计入成功。
- 本轮不确定业务取舍：目前未发现需要用户重新裁定的项。发现未决时追加原型/规则/影响与推荐，不擅自扩大范围。

## 本次验证

Cloud a254dae / 380cec8。全Web168文件/1244测试通过（最终审阅后/tmp/chg111-reviewed-web-tests-rerun.log，maxWorkers=2）。新增状态/权限用例与列表7状态、本人/其他成员控制矩阵通过；批次、执行、计划、计划编辑、G1、控制、旧请求证明共7组浏览器通过，另changed-revision/abandoned-navigation通过。创建确认初次用共享DialogPlugin缺少可访问名称的测试定位失败；改为原型同类ResourceOverlay摘要弹窗，按真实dialog标题与按钮复验通过，不降低业务断言。

完整11项异常矩阵均通过：changed-revision、abandoned-navigation、rejected-replay、different-start-rejected、different-start、cross-tab、failed-task-actions、senior、manual-publication、late-publication、stopping（/tmp/chg111-*.log）。Cloud生产构建通过。最终环境与合并结果见final-delivery.md，全部范围内验收PASS。

## 实施后复查

- 创建确认恢复原型ResourceOverlay摘要并绑定当次输入；离开页面/路由刷新时清除，校验返回后检查页面代次与输入未变化，取消不创建正式记录。380cec8补清理后计划/计划编辑浏览器重跑PASS。
- 一轮全Web在localSettingsWiring既有动态导入超过5秒；未提高超时或削减断言，限制maxWorkers=2重跑全量168/1244 PASS。
- 新增列表动作继续复用原详情确认器，导航仍绑定batch/revision/epoch/path，changed-revision与abandoned-navigation均PASS；没有在列表点击时直接发控制POST。
- PR：[Cloud54](https://github.com/piqiu96/wt-media-cloud/pull/54)、[Workspace67](https://github.com/piqiu96/wt-media-workspace/pull/67)。Cloud正式审阅触发Codex，但Bot明确提示review额度耗尽，未声明自动review通过；本轮另行逐文件检查权限、未决统计、终态只读、创建与控制请求保护。

## 380cec8安装版实际走查（2026-11-25 19:58）

统一all退出0（/tmp/chg111-environment.log），实际新挂载frontend 0.1.0+380cec8.dirty；operator01原凭据登录通过。本机服务、比特浏览器指定账号、执行凭证均就绪。批次6/5/4/3/2真实列表均显示详情/复制，新建批次底栏返回/保存草稿/下一步；计划新建底栏返回/保存草稿/创建计划，无独立检查安排；计划2仍目标2/公开2/缺口0、批次锁定已结束、详情仅返回。新建均为空白输入，只读核对后返回，没有覆盖本机草稿或创建Cloud记录。

实际旧批次1（已取消）暴露底层phase=ended又渲染出已结束副标题：1b6fd0e限定阶段副标题和停止派发提示仅对活动状态展示；新增浏览器断言已取消不得同时出现已结束。定向领域测试与7状态/跨成员列表回归PASS（/tmp/chg111-terminal-unit.log、/tmp/chg111-terminal-list.log）。该中间包随后由f2ccc1b最终包替代，实际走查通过。

### 终态详情复查

1b6fd0e安装版列表已取消已不再混有已结束，但同一取消记录的详情仍显示无业务作用的执行阶段已结束。f2ccc1b对终态详情一并隐藏瞬时阶段，保留真实执行状态、终止/开始/结束时间与历史结果。浏览器加入取消详情断言，修改前确实失败1≠0（/tmp/chg111-terminal-detail-before.log），修改后7状态/跨成员/终态只读详情及28项领域测试PASS（/tmp/chg111-terminal-detail-fixed.log、/tmp/chg111-terminal-detail-unit.log）。f2ccc1b最终all重建退出0并实测通过，日志/tmp/chg111-final-environment.log。

## 最终安装包PASS（20:08）

最终源码f2ccc1b。`WT_MEDIA_LOGIN_USER=operator01 ... python3 scripts/dev/local_env.py all --force-restart`实际退出0（/tmp/chg111-final-environment.log）。Cloud/各worker/Agent/BitBrowser、双前端入口、生产assets/CORS/登录、签名/DMG校验和挂载全部PASS。新挂载frontend 0.1.0+f2ccc1b.dirty；dirty仅其他会话example，正式运行源码无未提交修改。Agent/Desktop runtime本项无源码变动。

20:08实际登录operator01，列表六条真实批次都有详情/复制；取消批次1只显示已取消，进入其详情没有执行阶段或已结束混显，保留终止时间，底部只有返回。工作环境显示本机服务已连接、比特浏览器指定账号已登录、执行凭证已配置。实际新建页三处footer及计划2终态已在前包复查，最终仅补详情阶段隐藏，受控三角色/全部新建、执行与计划路径均已验证。没有新增Cloud计划、批次或发布任务，没有再次投稿，未覆盖本机草稿。环境保留在已登录批次列表供用户走查。

Workspace220项测试及治理/索引/上下文/文档检查PASS（/tmp/chg111-workspace-tests.log）。Cloud最终CI全部通过且合入main；Workspace归档合并生效，用户签收另行，见final-delivery.md。

最终DMG SHA256：`cfe46fbdf10b6bdda529a66c4ef4b126e5798a9f255cc40eefbeae692844f6f5`。只读数据库核对仍为12条发布任务、6批次、2计划，批次1为cancelled。最终Cloud生产构建日志/tmp/chg111-final-cloud-f2ccc1b.log。
