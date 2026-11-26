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
- 27/78于21:41:53视频完整下载后封面地址过期而投稿前失败，58f8102修体积升序，旧过期回归FAIL→19准备/997单测PASS。正确配置完整all后21:51原生重试27/79；22:12三份资源实际大小/SHA全部匹配，随后真实填表第2标签“三角洲行动手游”被平台topic/tag/check内部code=-1拒绝，22:12:59failed/rev11，无提交、现场关闭。官方投稿静态源码tx同时要求checkCustomTag与checkTopicName成功，topic内部非0确实reject，不是程序把正常通过当拒绝。禁止原配置盲重试；22:22原生正常结束计划3，status ended/end_reason unmet，processed2/2/公开0/缺口2、两批均ended，仅复制/详情，失败历史与完整原因保留；不得重试26/27。22:22正常重做此前未投稿素材196/199为新合成752/753，752→151；753因持续广告传输被5分钟上限误截，正常取消后部署4922330修复，再经原有admin权限正常retry成功为152（operator重试403符合既有权限）。两成片均120秒/原广告SHA/无开头/PIP/6秒尾部，时间线与原插入点续播断言通过。真实DeepSeek生成并审阅采用正常标题/简介/常规三角洲行动、射击游戏两标签，正常图片库同素材游戏帧渲染4:3和16:9双封面；首批额外换用70秒清晰游戏帧，标题不变。
- 新Plan4“三角洲·常规内容·两批顺序发布”，目标2，批次14/15各目标1/候选1/缺口0，保存后各正式任务0。23:11安装版逐批确认后仅启动一次，首批14仅建task28/attempt80。23:14:49原尝试正常受理117683378980067，reviewing、无失败；23:14:53系统按原10%规则自动交接14并启动15，仅建task29/attempt81。此时Plan4 running/current15/processed1/公开0，首批尚待公开，不把受理或自动推进计为自动公开PASS。
- 安装版额外配置边界走查13已收口cancelled/rev3：从12复制切B站清资源保留目标→确认零候选/保存13任务0→继续配置平台disabled、目标2改1保存→开始发布明确提示无候选且无提交按钮→正常终止。始终候选0/任务0/无占用，不发布额外内容。明确空态、步骤与按钮已实际检查。

## 源码、运行与构建

- 当前运行Cloud4922330、Agent58f8102、Desktop31fd8e1。正确配置完整all exit0（/tmp/chg130-guide-fixed-environment-all.log），安装版前端4922330.dirty仅保留原型他人改动，sidecarSHA256=441248e9ad2f48a7c24c6fb19479cb3d8f5eec5dbd340ed81f50deb0248b70b1。原运营登录后22:52及23:03三项工作环境正常；Plan4在途期间不重启。
- **本轮环境命令必须保留** `WT_MEDIA_CLOUD_CONFIG_PATH=/tmp/chg130-cloud-config`。私有配置已断言B站enabled=true，不提交或输出配置。21:10漏带时all基础门禁虽通过，但B站默认false，11预览can_start=false，不能当B站验收环境。带配置重建后platform-rules enabled=true、11preview can_start=true。正式默认开关未改。
- Agent6c7023c补公开页面内嵌__playinfo__来源：同官方原稿页aid/BV/UID/title/CID/pubdate/时长全部匹配，仍绑定实际请求/重定向及唯一已解码媒体。旧隔离浏览器FAIL→3项PASS44.677秒、真实同稿proof False→True；996全单测PASS49.074秒、完整43 B站浏览器PASS150.638秒。不是仅凭HTTP200放行。
- Agent4ad42fc对匹配标签内部明确拒绝及时抛结构化安全序号，Runner固定中文提示，不输出上游原文、不删标签。旧浏览器通用超时FAIL→42相关PASS3.720秒、17发布器单测PASS0.496秒。历史26结果不改写。
- 既有9e77ffb上传disabled初始化、b304b7e文件准备3600秒绝对截止/30秒单次网络/关闭现场实证、c424233百度隐藏菜单等修复已包含。52百度浏览器PASS82.770秒，详见evidence。默认3600秒只用于文件准备，浏览器填表仍900，不延长授权或反复重置截止。
- Cloud782e0c3修暂停当前批次仅排队时显示batch_paused，保留在途/未知/核验优先级与推进阻断：旧排队失败→5隔离DB测试PASS5.809秒，发布四包/完整业务模块Go测试PASS。
- Cloudd07fe0d修已有批次平台编辑锁定，复制/新建仍可切；旧2失败→29相关/196发布Vue PASS，现已在13实际走查验证。0f1862a/e7dc60c平台分组审查也已修。
- **最新Cloud4922330已部署**：9a9693b检查结果未到/手动检查中显示中性检查状态，抑制旧失败提示，就绪和调度不变；旧3失败→30定向PASS，172文件1273完整Web PASS20.25秒。070d3ae在任务列表/详情/批次正式表按verification_required补“公开结果需人工核实”，原状态/统计/动作不变，196发布回归PASS7.26秒。
- 含070的新DMG后台构建已成功但未部署，需包含最新资源顺序修复再次构建；旧构建日志（/tmp/chg130-status-hints-build.log），未部署；待27/78安全结束再切换与走查。只build-dmg不会停止当前App。最后还需要main组合新包与整体验证。a009dbb/81e4fa4修交接批次待办/状态/旧下一组时间，真实未决仍保留入口：旧1FAIL→197发布/1274完整WebPASS；Cloud网页已主动实查首批已推进、失败1/待办0/差额1和历史结果。含81新包后台build已成功（/tmp/chg130-handoff-final-package-build.log，sidecarSHA256=580f0d79abd56aadc8b2bd11864ee1fd79aeb32cc808c55496746e20005cbf34），已部署并原生复核，79已安全失败结束。22:20正确配置完整all exit0（/tmp/chg130-handoff-final-environment-all.log）；安装版登录后三项工作环境均正常，原计划失败结束实走。单独verify在登录前没有Agent、登录后因脚本无Sidecar key拒绝BitBrowser读取，不能称两次单独verify通过，也不当作产品运行故障；完整all及原生核实为实际依据。

## PR、治理与工具

- Agent21、Cloud59、Desktop20、Workspace72 open未合并；Cloud59已ready。Agent6c/Cloud d07 CI实际通过，最新Cloud070 CI run45830769360已success；Agent58最新CI已PASS。Cloud81及492最新CI均PASS，492 run45842595801耗时14分钟。Agent八条旧讨论、Cloud三条4707851694/4707918438/4708555461在对应修复与回归后已resolve。没有最新独立审查时不冒称已审。
- Workspace220单测PASS29.468秒、M0配置PASS；最新证据和工程规格已提交至caa7df4，后续原生走查证据7dcf4b8。全部未完成不能标DONE或提前合并。
- 保留Cloud web/example大量他人修改及Workspace docs/design六文件，不暂存、还原或覆盖。只提交本CHG显式路径。无其他Agent并行写入。
- 私有证据根为相邻.local/m2b/chg130-new-data。正常API helper /tmp/chg130_api.py，op.call/stream；8188/api/v1，已有cookie。attempt路径/publication/:id/attempt，历史顺序列表。不要输出凭据/签名URL，不SQL修改业务事实。
- CUA先前拒绝BitBrowser私有平台页面，不能用临时CDP/Playwright/其他私有读取绕过。正常产品Runner/API、隔离测试和全新匿名公开能力测试允许。主动Chrome公开页及起飞原生操作已成功；私有后台完整走查仍未完成，不能伪造。Chrome只创建/关闭自己的独立窗口，保留用户页面；中文用paste，typeText曾只输入数字，提交前均已纠正核实。
- 起飞路径为相邻.local/m2b/desktop-review-mount/起飞.app。CUA活动当前已完成，无接管等待。每段活动后先独立browser-complete再用非CUA工具。用户操作触发changed时重读状态，避免干扰。Git HTTPS push曾停滞，SSH BatchMode/ConnectTimeout成功；不用改全局配置。

## 下一步

1. 跟进Plan4原任务28/80、29/81，不重复授权/投稿/重启。核对两批原稿自动公开、真实计数与作品回链；尚未取得自动公开不能标通过。
2. 安装版已实看第一批28平台审核中/零失败；继续计划当前批次、结果/原稿封面和公开播放PIP/片尾走查，不能把旧人工21/25说成自动回写。
3. 完成剩余浏览器与UI走查、PR/CI收口、最终main merge commit/全新组合重建；未验证的私有平台后台/主观听音如实列明，不能用单测替代。原型/设计他人改动保留。

## 2026-11-27 当前调整接续

用户指定广告95三角洲微光.mp4，已正常admin更新1016顶层和全部输出，ffprobe27.033333秒/8K/音轨，旧快照未改。用户明确新建B站普通固定内容无需标注，声明只读，旧有声明保留；复制属于新建改普通并清来源，旧空草稿通过正常patch补齐，disabled不写。两平台AI加入差异风格与源标题附加标签清理；首轮真实建议仍旧问句/带双子星，不计质量通过，继续强化后重建验证。

Cloud新增f05baae标题检索（审查4709534276已resolve）、ec79164普通/风格及后续副本/清标签提交；隔离MySQL检索7场景和权限PASS，发布四包PASS，完整Web173文件1275项PASS及追加SSR2项PASS。ec首版all exit0，最终新组合重建中。四仓原型/设计非本人修改保留。Plan4原自动公开2/2、差额0、ready_to_finish，原计划未结束不改。当前没有在途发布/合成；后续不需要继续运行旧56广告的验收。

本轮最终Cloud bb9b9e6已推送，标题检索f05baae、普通/风格ec79164均包含。正确配置最终all exit0，/tmp/chg130-weiguang-final-environment-all.log；挂载前端bb9b9e6.dirty，sidecar SHA256=cc65941607c9f6c77094bd0323246780906e9bc218628d47e93a8d7b0c528d94，Agent58f8102/Desktop31fd8e1。完整Web1276项PASS18.83秒，publish四包PASS1.820秒，文档/Delivery/master/M0 PASS。强化后的B站和百度真实生成已核对，不带原活动/赛季标签或互动问句；一次百度item_error未采用、正常明确字数预算后再生成成功，不宣称零错误。最新Cloud CI run45861711942待完成。还需安装版控件实查及后续95广告新成片/普通声明真实发布；不能将已有56广告计划2/2当新广告验收。
