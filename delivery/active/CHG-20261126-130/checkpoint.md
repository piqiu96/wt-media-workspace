# CHG130 执行检查点

- 唯一状态change.md=VERIFYING。128/129依赖已合入，单执行器串行，不启动未来CHG；B站真实公开/两批计划/最终整体验收未完成，不得归档或提前合并。
- 用户授权自主编码/修复/测试/PR/E2E/真实发布，不逐项确认。文案必须素材→正式AI→核对采用→封面，不可任写测试/制作/验收标题。用户确认百度41正常、34正常；34答复后已在原生UI恢复原attempt60并成功发布。
- 数据：固定wt_media_cloud，仅admin/senior01/operator01，密码不改；一级新建选择仅游戏，历史类型仅解析。账号18–21/Profile967–970为1B站/3百度。B站18/#51/UID3706971620379308；百度19/#41/UID6949353902，20/#39/UID4908760199，21/#34/UID6572476037。未删平台作品。
- 新广告file56，策略1016/template12 ad_pip_ending v1；素材195–200/合成75/任务746–751成功，成片145–150。无开头，10–15秒广告PIP、广告声、正片原插入点继续、6秒尾部。画面/客观音轨已核验；主观听音仍无证据。
- 私有证据根目录相邻.local/m2b/chg130-new-data。normal-publication-content.json/normal-prepared-publication-content.json保存145–150正常内容与封面；normal-baidu-regression-*保存146/147正常百度AI、cover96–99、分配/批次启动。四张百度封面已逐张实看。旧18/19测试文案不重试；19正常abandon、20诊断cancel，均有可信未提交/现场关闭。不能SQL改业务状态。

## 真实当前结果

- 百度22/56受理17:02:49，submission1882910900152502022，仍reviewing；原稿核验后停止，提示接口读取需人工核对。不能重复投稿22或伪造公开。黑底缩略图尚需最终质量核对，不能当整片全黑。
- 百度双账号batch12真实结束：target2/created2/published2/shortfall0/verification_required0。23/62投稿17:45:29、受理17:45:35、公开ID8351506294205442839、实际published_at17:45:32，18:09:05完成可信核验。24/60原现场继续后17:37:35受理，公开ID7277548266066867187、实际published_at17:37:33，17:59:13可信核验。两条均published，不再重试。
- 两条公开URL已存私有verified-publications.json，均为 https://mbd.baidu.com/newspage/data/videolanding?nid=sv_<公开ID> 。本次已主动用CUA原生Chrome新标签实看两页正常标题/话题、未登录入口、02:00时长、视频游戏画面，24还实看广告PIP。只关闭本轮新标签，未动其他标签；尾部及主观听音未证明，不能冒称完整看完。
- 原生批次12列表100%/已结束/无待处理，详情公开2、失败0、待处理0、待公开0、差额0，任务/操作记录一致，结束后没有编辑/再次执行动作。计划3/batch10/11未启动，预检can_start=true/issues=[]/零缺口，目标2/公开0。独立B站batch9含20(cancelled诊断)/21，未成功闭环。
- B站21最新attempt64已failed/completed，无submit，not_submitted/scene_closed=true。真实已通过本次File→视频CID绑定、标签、二创、双封面同步、两张封面文件/画布校验。18:15:35两张导出均guard接受、两笔HTTP200、dialog关闭，但receipts0，于18:16:05超时；证据表明本地回执校验误拦截。不能称平台拒绝或已受理。

## 当前源码、包与验证

- Cloud49afaf3运行：已修取消素材投影、操作栏裁切、计划平台硬编码、启动误用百度校验和B站竖封面0加锁。模块及隔离MySQL事务锁回归通过，真实batch9原子建2并同Profile串行。Desktop31fd8e1。
- Agent已提交并SSH推送：5f7e73a稳定百度入口/短暂Passport；9d421ce本次File对象绑定（真实57验证）；d4281f9原CID播放来源与已解码媒体绑定；5e13f70标签真实input（真实58验证）；f9aee0e二创组件状态（真实61验证）；1f98f70网络回执也强制当前文件完成；09bb371固定缓存副本清理（真实22/24目录已清）；fbafd6b原稿核验安全分类；999a2d3双封面同步组件（真实63验证）；e06f18b后台封面响应及固定诊断（真实64确认2次200、无回执接受）。
- 前一运行Agent e06f18b，sidecar SHA256=3438fececc4f2f40b0fe5da4114ab6b6ca80b0c30a58360823d0f35cf6a416fe，Cloud49afaf3/Desktop31fd8e1。原生登录operator01/operator123、环境三项正常。该轮64已安全结束；现新包65在途。
- 最新Agent b6bb028已提交推送：官方上传回执作为封面地址事实源，接受官方客户端支持的数字/字符串零码、有效HTTP(S)/网络路径，不写死旧hdslb CDN；仍逐张绑定本次成功回执并精确核对最终POST。异常地址/凭据/控制字符/片段与错配仍拒绝。正式工程规格已回写，内部平台适配未改Cloud契约。
- b6bb028验证：新CDN/网络路径旧用例先FAIL；990全量PASS（/tmp/chg130-cover-url-unit.log）；15项相关单测PASS（/tmp/chg130-cover-url-after.log，实际此日志旧14+新增1）；2项完整表单浏览器PASS（/tmp/chg130-cover-url-browser.log）、额外新地址贯穿POST用例1项PASS（/tmp/chg130-cover-url-contract-browser.log）。仅最后空白格式调整，无行为变化。build-dmg已完成/tmp/chg130-cover-url-build.log，正常二次launch成功，原生环境三项正常；sidecar SHA256=b0c5f692374bca30273aa8b0240819a7806c0efa401327295ef1fe8a052f949c。21正常retry产生65，18:24上传已完成、正在本轮填表，勿重启。仍不能断言64的实际域名/成功码类型，下一真实日志会给固定形状。
- 早前990之前：999a2d3 30浏览器PASS；首次987单测旧MagicMock未定义evaluate导致1错误，补模拟结构后987全量PASS。e06f18b 988全量/14相关/2浏览器PASS，CI45798921071成功。不要把首轮失败隐去。
- 完整all在5f7e73a时已通过；后续各包均build+挂载源记录+sidecar hash+原生环境复核。首次launch卸载旧mount通常资源忙，正常退出后第二次成功，无强制卸载。Desktop接管后脚本verify因Agent归属门禁失败，不能冒称全绿。启动瞬间环境短暂不可达后自动正常，未修该提示。

## PR、工具与下一步

- 四仓PR均open未合并：Agent21、Desktop20、Workspace72、Cloud59(Draft)。用户回复ok后gh auth status已确认登录恢复，Cloud59已创建；无认证阻塞。Cloud CI45793563267成功（14m13s），Desktop31 CI成功，Workspace264bf24之前CI成功，Agent e06 CI成功；b6最新CI45800454775 success。Agent/Cloud PR正文已更新真实进展，所有Done When完成前不合并。
- 旧PR尾换行/可选Playwright导入、原CID媒体来源、封面URL绑定、网络回执绕过均已修。最新反馈4706058925由1f98f70解决。继续核对新Review和CI，不冒称无人审查已通过。
- 工具：先前CUA拒绝BitBrowser私有平台URL，不临时CDP/Playwright或换工具绕过；正常产品Runner/API继续授权。公开作品是不同的匿名页面，CUA原生Chrome已可查看。IAB连续超时、Chrome browser-provider不可用；原生Chrome键盘导航/AX/截图有效，坐标/滚动偶有windowNotFoundAtPosition。原生起飞控件正常。无接管等待，无待用户登录问题。
- 下一步：等b6包build完成→正常launch（资源忙可正常第二次）→原生登录/环境及sidecar hash→确认64未提交已关闭后正常retry21→据实际封面shape/最终POST继续修。不要重试22/23/24。B站可正常投稿后推进计划3两批，按真实10%规则推进与各批按钮处理；完成原稿/公开读回、逐页/尾部/新包整体验证、PR/CI/merge commit入main、组合重建后再归档。
- 当前Workspace已提交264bf24，自此checkpoint及工程规格尚有自有改动待提交。保留其他会话Cloud web/example及Workspace docs/design六个脏文件，不暂存/还原。

- task23公开页也已用原生Chrome主动打开实看：正常标题/话题、作者白变小灵、02:00游戏视频播放；只关闭本轮标签。两条百度公开页均完成基础实看。
