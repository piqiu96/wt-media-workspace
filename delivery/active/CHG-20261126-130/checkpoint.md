# CHG130 执行检查点

## 当前范围与约束

- change.md唯一状态VERIFYING，128/129已合入；单执行器串行。用户要求编码、自测、PR问题修复、真实E2E、主动浏览器/安装包走查直到交付，不逐项等待确认。真实计划收口、最终main合并及最终组合尚未完成，不能标DONE。
- 正常内容必须素材→真实AI→核对采用→双封面，不任写测试标题/简介，不删冻结标签规避平台拒绝。107保存零任务/占用；108启动原子建单/占用/授权；109执行后冻结、按10%推进。用户已授权真实发布、DeepSeek限定内容和B站上传协议，本轮无待确认问题。
- 数据库固定wt_media_cloud，用户仅admin/senior01/operator01，凭据沿用会话原值，不入文档。一级类目新建仅游戏。四账号18–21/Profile967–970：B站18/#51/UID3706971620379308，百度19/#41、20/#39、21/#34。用户确认51/41/34登录正常。
- 广告file56来自用户三角洲_网站.mp4；策略1016/template12 ad_pip_ending，无开头、广告PIP/广告声、原插入点续播、6秒尾部。素材195–200/合成75/任务746–751/成片145–150已成功，客观音轨与本机画面已核对；主观听音未证明；百度24原公开视频已主动检查片尾01:54→01:58/02:00并循环，B站25原稿也实看01:55/02:00片尾。

## 真实业务当前事实

- 百度batch12已结束：target2/created2/published2/shortfall0/verification_required0。23/62公开8351506294205442839，24/60公开7277548266066867187。主动Chrome检查正常内容/02:00游戏播放，24实看广告PIP；原生列表/详情/按钮检查通过。不重试23/24。
- B站21/69受理117682405968275，旧自动核验停止。工程师主动Chrome无痕实看原账号/标题/声明/视频/PIP、公开元数据逐项匹配后，正常人工补录published/work12；不是自动通过，不重试21。batch9已结束：目标2/公开1/诊断取消1/差额1。
- 正常单条25/76受理117682791777077，主动Chrome无痕实看正常标题/简介四标签/账号/声明及00:03→00:28/02:00、新广告画面。旧自动检查20:59停止；修复后同稿产品匿名proof在全新无Cookie浏览器从False变True。21:33经安装版正常人工补录published/work13/rev15，verification_required=false，实际发布时间20:43:03，原停止历史保留。不能称25正式自动回写，不再投稿25。
- 百度22/56已受理1882910900152502022，自动核验停止、待人工核实，未证明公开；不重投。旧18/19已正常放弃，20诊断取消，历史保留；不SQL改业务事实。
- Plan3“三角洲·新广告·两批顺序发布”，目标2，原批次10/11。第一批原任务26/77在第5标签得到匹配内部data.code=-1（外层code0）且UI未保留；未提交、not_submitted/scene_closed均true，failed/rev36。不删冻结标签，不再盲重试。
- 计划正常按10%停waiting_continue。21:14首次人工确认因本次重建漏带B站测试配置而409；原journal/request_key保留。恢复正确配置后21:22从安装版“核对原计划请求”成功：Plan3current11/rev9/processed1，首批失败及目标差额保留，操作审计含完整继续原因；只建task27/attempt78，batch11running/rev6/group1。26已handoff，不得retry26。
- 27/78于21:41:53视频完整下载后封面地址过期而投稿前失败，58f8102修体积升序，旧过期回归FAIL→19准备/997单测PASS。正确配置完整all后21:51原生重试27/79；22:12三份资源实际大小/SHA全部匹配，随后真实填表第2标签“三角洲行动手游”被平台topic/tag/check内部code=-1拒绝，22:12:59failed/rev11，无提交、现场关闭。官方投稿静态源码tx同时要求checkCustomTag与checkTopicName成功，topic内部非0确实reject，不是程序把正常通过当拒绝。禁止原配置盲重试；22:22原生正常结束计划3，status ended/end_reason unmet，processed2/2/公开0/缺口2、两批均ended，仅复制/详情，失败历史与完整原因保留；不得重试26/27。22:22正常重做此前未投稿素材196/199为新合成752/753、batch76/77，沿原1016快照120秒/同广告/尾部，只新随机种子，未复用已公开成片；目前running/validating_input。后台/tmp/chg130-revalidation-ai.py观察后真实AI生成待review，不自动采用；仅常规三角洲行动/射击游戏标签，不活动/赛季/手游专属。
- 安装版额外配置边界走查13已收口cancelled/rev3：从12复制切B站清资源保留目标→确认零候选/保存13任务0→继续配置平台disabled、目标2改1保存→开始发布明确提示无候选且无提交按钮→正常终止。始终候选0/任务0/无占用，不发布额外内容。明确空态、步骤与按钮已实际检查。

## 源码、运行与构建

- 当前运行Agent58f8102、Cloud81e4fa4前端/后端等价070d3ae、Desktop31fd8e1，正确配置强制完整all已exit0（/tmp/chg130-cover-expiry-environment-all.log）。新包sidecarSHA256=6bf6df325d0705f7e1d8ee0dd0d8de83d82e1b45f920045427cf2686ca64947a。原运营登录后环境三项正常，22列表和详情人工核实提示实看。此前运行Agent6c7023c、Cloud d07fe0d。最新配置完整all exit0（/tmp/chg130-bootstrap-environment-configured-all.log），全部基础门禁/登录/挂载通过；原生operator01原凭据登录及环境三项正常。实际挂载sidecar SHA256=f7644145e8a93c116be651ce2de090d8f17cb598ae2f16fc34cb65daab5333ad。
- **本轮环境命令必须保留** `WT_MEDIA_CLOUD_CONFIG_PATH=/tmp/chg130-cloud-config`。私有配置已断言B站enabled=true，不提交或输出配置。21:10漏带时all基础门禁虽通过，但B站默认false，11预览can_start=false，不能当B站验收环境。带配置重建后platform-rules enabled=true、11preview can_start=true。正式默认开关未改。
- Agent6c7023c补公开页面内嵌__playinfo__来源：同官方原稿页aid/BV/UID/title/CID/pubdate/时长全部匹配，仍绑定实际请求/重定向及唯一已解码媒体。旧隔离浏览器FAIL→3项PASS44.677秒、真实同稿proof False→True；996全单测PASS49.074秒、完整43 B站浏览器PASS150.638秒。不是仅凭HTTP200放行。
- Agent4ad42fc对匹配标签内部明确拒绝及时抛结构化安全序号，Runner固定中文提示，不输出上游原文、不删标签。旧浏览器通用超时FAIL→42相关PASS3.720秒、17发布器单测PASS0.496秒。历史26结果不改写。
- 既有9e77ffb上传disabled初始化、b304b7e文件准备3600秒绝对截止/30秒单次网络/关闭现场实证、c424233百度隐藏菜单等修复已包含。52百度浏览器PASS82.770秒，详见evidence。默认3600秒只用于文件准备，浏览器填表仍900，不延长授权或反复重置截止。
- Cloud782e0c3修暂停当前批次仅排队时显示batch_paused，保留在途/未知/核验优先级与推进阻断：旧排队失败→5隔离DB测试PASS5.809秒，发布四包/完整业务模块Go测试PASS。
- Cloudd07fe0d修已有批次平台编辑锁定，复制/新建仍可切；旧2失败→29相关/196发布Vue PASS，现已在13实际走查验证。0f1862a/e7dc60c平台分组审查也已修。
- **最新Cloud源码/运行前端81e4fa4**：9a9693b检查结果未到/手动检查中显示中性检查状态，抑制旧失败提示，就绪和调度不变；旧3失败→30定向PASS，172文件1273完整Web PASS20.25秒。070d3ae在任务列表/详情/批次正式表按verification_required补“公开结果需人工核实”，原状态/统计/动作不变，196发布回归PASS7.26秒。
- 含070的新DMG后台构建已成功但未部署，需包含最新资源顺序修复再次构建；旧构建日志（/tmp/chg130-status-hints-build.log），未部署；待27/78安全结束再切换与走查。只build-dmg不会停止当前App。最后还需要main组合新包与整体验证。a009dbb/81e4fa4修交接批次待办/状态/旧下一组时间，真实未决仍保留入口：旧1FAIL→197发布/1274完整WebPASS；Cloud网页已主动实查首批已推进、失败1/待办0/差额1和历史结果。含81新包后台build已成功（/tmp/chg130-handoff-final-package-build.log，sidecarSHA256=580f0d79abd56aadc8b2bd11864ee1fd79aeb32cc808c55496746e20005cbf34），已部署并原生复核，79已安全失败结束。22:20正确配置完整all exit0（/tmp/chg130-handoff-final-environment-all.log）；安装版登录后三项工作环境均正常，原计划失败结束实走。单独verify在登录前没有Agent、登录后因脚本无Sidecar key拒绝BitBrowser读取，不能称两次单独verify通过，也不当作产品运行故障；完整all及原生核实为实际依据。

## PR、治理与工具

- Agent21、Cloud59、Desktop20、Workspace72 open未合并；Cloud59已ready。Agent6c/Cloud d07 CI实际通过，最新Cloud070 CI run45830769360已success；Agent58最新CI已PASS。Cloud81最新CI跟进（run45835786249）。Agent八条旧讨论、Cloud三条4707851694/4707918438/4708555461在对应修复与回归后已resolve。没有最新独立审查时不冒称已审。
- Workspace220单测PASS29.468秒、M0配置PASS；最新证据和工程规格已提交至caa7df4，后续原生走查证据7dcf4b8。全部未完成不能标DONE或提前合并。
- 保留Cloud web/example大量他人修改及Workspace docs/design六文件，不暂存、还原或覆盖。只提交本CHG显式路径。无其他Agent并行写入。
- 私有证据根为相邻.local/m2b/chg130-new-data。正常API helper /tmp/chg130_api.py，op.call/stream；8188/api/v1，已有cookie。attempt路径/publication/:id/attempt，历史顺序列表。不要输出凭据/签名URL，不SQL修改业务事实。
- CUA先前拒绝BitBrowser私有平台页面，不能用临时CDP/Playwright/其他私有读取绕过。正常产品Runner/API、隔离测试和全新匿名公开能力测试允许。主动Chrome公开页及起飞原生操作已成功；私有后台完整走查仍未完成，不能伪造。Chrome只创建/关闭自己的独立窗口，保留用户页面；中文用paste，typeText曾只输入数字，提交前均已纠正核实。
- 起飞路径为相邻.local/m2b/desktop-review-mount/起飞.app。CUA活动当前已完成，无接管等待。每段活动后先独立browser-complete再用非CUA工具。用户操作触发changed时重读状态，避免干扰。Git HTTPS push曾停滞，SSH BatchMode/ConnectTimeout成功；不用改全局配置。

## 下一步

1. 跟进新合成752/753（正常重做未投稿素材196/199，不改原失败事实），成功后真实AI标题/简介/仅常规标签/封面短标题先review；为新两批计划渲染双封面并全部确认后再启动，完整自动公开仍未通过。
2. 最新81安装版已实看原计划3未达成结束0/2、processed2/2；后续继续新计划正常顺序推进与最终公开数/差额/作品回链，不能把旧人工21/25说成自动回写。
3. 完成剩余浏览器与UI走查、PR/CI收口、最终main merge commit/全新组合重建；未验证的私有平台后台/主观听音如实列明，不能用单测替代。原型/设计他人改动保留。
