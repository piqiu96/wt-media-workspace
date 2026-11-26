# CHG130 执行检查点

- 当前状态以change.md的VERIFYING为准；未达到交付或归档条件。唯一执行器串行推进；128/129依赖已合入。
- 用户授权全流程自主修复、自测、PR、真实发布、E2E及最终原生页面走查。标题/简介必须素材→正式AI生成→核对采用→封面渲染，不使用制作/研发/验收文案。
- 数据重建完成：固定wt_media_cloud，仅admin/senior01/operator01，密码未变；一级类目新建/选择仅游戏。账号18–21、Profile967–970分别为1个B站/3个百度，4/4正常。未删除平台作品。
- 新广告file56，策略1016（template12 ad_pip_ending v1）；短素材195–200，合成批次75/任务746–751全成功，成片145–150。无开头、10–15秒广告画中画、广告音轨、正片从插入点续播、6秒片尾。已核验画面和客观音轨，129主观听音证据仍不足，不能冒充已听音。
- 六条正常AI文案/封面已生成并采用；私有normal-publication-content.json及normal-prepared-publication-content.json保存输入。历史task18/19使用旧文案，冻结不可改，不再用其重试投稿；不改SQL制造状态。
- 已修复并真实验证：Cloud48782b0取消素材准备投影、d3ddb1f操作栏裁切、aa1ec14计划平台硬编码、30d5dc0批次/计划启动误用百度内容校验、49afaf3启动锁不存在的B站竖封面0。publish模块回归及隔离MySQL封面锁事务测试PASS。同批9由不能启动变为正常建单，目标2/建2/缺口0。
- Agent98a9cc1修正“继续编辑”可选旧稿入口提示被误判为已恢复视频；不点恢复/丢弃，空白上传正常推进。官方源码已证明原判断过宽，旧的“需用户确认清理旧稿”问题不再是空白入口的前置条件。仍保护实际已加载旧视频及一次提交/账号/最终字段一致性。
- 正式运行组合Cloud49afaf3/Agent49a618a/Desktop31fd8e1，完整重建日志/tmp/chg130-stability-upload-environment.log；新包原密码登录，工作环境正常。脚本verify在Desktop接管后非所属Agent探测门禁停止，不冒称该命令全绿。
- 真实batch9：15:38 start创建task20/21，同一Profile按组串行。task20/attempt49因上传证明缺失诊断取消，正常API读回cancelled/finished、not_submitted=true/scene_closed=true/submit_started_at=null。15:48按正常resume推进task21/attempt50，目前running/ready且未提交；禁止构建后直接重启打断此在途任务。优先等其自然结束并核实关闭/未提交，再正常重试21。
- Agent49a618a改从request.url校验回执、977单测/11隔离浏览器PASS；真实50诊断显示response_query_matches=true，故响应落点差异不是本次根因。三笔preupload中两笔无name/size，一笔存在但均不匹配，尚未确认差异，不能放宽或猜测CID。
- 最新Agent159470e：百度实际结构诊断证明首页卡片与展开菜单有两个同名“发布视频”，原全局locator strict错误；改限定可见展开菜单，保留单入口兼容。双入口回归、58项百度+B站隔离浏览器及977全量单测PASS。另增加preupload字段计数/类型/字节数脱敏诊断，无原始URL/名称/凭据。新包只构建不启动，日志/tmp/chg130-entry-diagnostic-build.log；尚未部署，不计真实百度恢复。
- Plan3及其批次10/11仍ready/not_started，目标2/公开0；batch9尚无成功发布。真实平台受理、公开作品、两批计划、最终E2E/逐页走查均未完成。
- PR：Agent21、Desktop20、Workspace72 open未合并；Cloud尚无PR。Agent98a9cc1、Desktop31fd8e1及Workspace此前CI通过；最新49a/159 CI未核实。gh凭据无效，旧设备授权二次验证已过期，不提取其他凭据；Chrome留有Cloud比较草稿，不能冒称PR已创建。
- 工具边界：CUA曾明确拒绝BitBrowser平台URL，不能用临时CDP/Playwright绕过；正常产品任务API和自身业务Runner仍按授权测试，本机tauri://原生页面可走查。受限平台人工页面走查未完成，不混淆工具限制与应用错误。无接管等待。
- 下一步：新包构建完成后保留在途50直到自然结束，确认未提交/已关闭；部署159470e、原密码登录，再通过正常动作重试21读取新诊断、按证据修复回执差异。正常新内容验证百度，不用旧task19测试标题。然后真实单条/批次/计划→原稿与公开核实→最终浏览器/新包逐页→PR/CI/合并及组合重建。未经真实公开不标DONE。
- 保留其他会话Cloud web/example及Workspace docs/design六个脏文件，不暂存/还原。私有证据目录为仓库相邻.local/m2b/chg130-new-data；不输出敏感凭据。
