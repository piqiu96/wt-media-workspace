# CHG130 执行检查点

## 当前范围与约束

- change.md唯一状态VERIFYING，128/129已合入；单执行器串行。用户要求编码、自测、PR问题修复、真实E2E、主动浏览器/安装包走查直到交付，不逐项等待确认。真实计划收口、最终main合并及最终组合尚未完成，不能标DONE。
- 正常内容必须素材→真实AI→核对采用→双封面，不任写测试标题/简介，不删冻结标签规避平台拒绝。107保存零任务/占用；108启动原子建单/占用/授权；109执行后冻结、按10%推进。用户已授权真实发布、DeepSeek限定内容和B站上传协议，本轮无待确认问题。
- 数据库固定wt_media_cloud，用户仅admin/senior01/operator01，凭据沿用会话原值，不入文档。一级类目新建仅游戏。四账号18–21/Profile967–970：B站18/#51/UID3706971620379308，百度19/#41、20/#39、21/#34。用户确认51/41/34登录正常。
- 广告file56来自用户三角洲_网站.mp4；策略1016/template12 ad_pip_ending，无开头、广告PIP/广告声、原插入点续播、6秒尾部。素材195–200/合成75/任务746–751/成片145–150已成功，客观音轨与本机画面已核对；主观听音未证明；百度24原公开视频已主动检查片尾01:54→01:58/02:00并循环。

## 真实业务当前事实

- 百度batch12已结束：target2/created2/published2/shortfall0/verification_required0。23/62公开8351506294205442839，24/60公开7277548266066867187。主动Chrome检查正常内容/02:00游戏播放，24实看广告PIP；原生列表/详情/按钮检查通过。不重试23/24。
- B站21/69受理117682405968275，旧自动核验停止。工程师主动Chrome无痕实看原账号/标题/声明/视频/PIP、公开元数据逐项匹配后，正常人工补录published/work12；不是自动通过，不重试21。batch9已结束：目标2/公开1/诊断取消1/差额1。
- 正常单条25/76受理117682791777077，主动Chrome无痕实看正常标题/简介四标签/账号/声明及00:03→00:28/02:00、新广告画面。旧自动检查20:59停止；修复后同稿产品匿名proof在全新无Cookie浏览器从False变True。21:33经安装版正常人工补录published/work13/rev15，verification_required=false，实际发布时间20:43:03，原停止历史保留。不能称25正式自动回写，不再投稿25。
- 百度22/56已受理1882910900152502022，自动核验停止、待人工核实，未证明公开；不重投。旧18/19已正常放弃，20诊断取消，历史保留；不SQL改业务事实。
- Plan3“三角洲·新广告·两批顺序发布”，目标2，原批次10/11。第一批原任务26/77在第5标签得到匹配内部data.code=-1（外层code0）且UI未保留；未提交、not_submitted/scene_closed均true，failed/rev36。不删冻结标签，不再盲重试。
- 计划正常按10%停waiting_continue。21:14首次人工确认因本次重建漏带B站测试配置而409；原journal/request_key保留。恢复正确配置后21:22从安装版“核对原计划请求”成功：Plan3current11/rev9/processed1，首批失败及目标差额保留，操作审计含完整继续原因；只建task27/attempt78，batch11running/rev6/group1。26已handoff，不得retry26。
- **27/78于21:41:53投稿前失败，无提交/现场关闭已证实。** video.mp4大小/SHA均与冻结一致，视频约19分钟后才请求封面超过15分钟签名有效期；58f8102已修复按冻结体积小资源先下：旧过期用例失败→19准备测试及997全单测PASS46.252秒；已推送，正在正确配置完整all重建，再正常原任务重试。计划ready_to_finish/0公开/缺口2，暂不结束，第二批正常AI四标签未改。
- 安装版额外配置边界走查13已收口cancelled/rev3：从12复制切B站清资源保留目标→确认零候选/保存13任务0→继续配置平台disabled、目标2改1保存→开始发布明确提示无候选且无提交按钮→正常终止。始终候选0/任务0/无占用，不发布额外内容。明确空态、步骤与按钮已实际检查。

## 源码、运行与构建

- 当前正在强制完整重建Agent58f8102、Cloud070d3ae、Desktop31fd8e1；此前运行Agent6c7023c、Cloud d07fe0d。最新配置完整all exit0（/tmp/chg130-bootstrap-environment-configured-all.log），全部基础门禁/登录/挂载通过；原生operator01原凭据登录及环境三项正常。实际挂载sidecar SHA256=f7644145e8a93c116be651ce2de090d8f17cb598ae2f16fc34cb65daab5333ad。
- **本轮环境命令必须保留** `WT_MEDIA_CLOUD_CONFIG_PATH=/tmp/chg130-cloud-config`。私有配置已断言B站enabled=true，不提交或输出配置。21:10漏带时all基础门禁虽通过，但B站默认false，11预览can_start=false，不能当B站验收环境。带配置重建后platform-rules enabled=true、11preview can_start=true。正式默认开关未改。
- Agent6c7023c补公开页面内嵌__playinfo__来源：同官方原稿页aid/BV/UID/title/CID/pubdate/时长全部匹配，仍绑定实际请求/重定向及唯一已解码媒体。旧隔离浏览器FAIL→3项PASS44.677秒、真实同稿proof False→True；996全单测PASS49.074秒、完整43 B站浏览器PASS150.638秒。不是仅凭HTTP200放行。
- Agent4ad42fc对匹配标签内部明确拒绝及时抛结构化安全序号，Runner固定中文提示，不输出上游原文、不删标签。旧浏览器通用超时FAIL→42相关PASS3.720秒、17发布器单测PASS0.496秒。历史26结果不改写。
- 既有9e77ffb上传disabled初始化、b304b7e文件准备3600秒绝对截止/30秒单次网络/关闭现场实证、c424233百度隐藏菜单等修复已包含。52百度浏览器PASS82.770秒，详见evidence。默认3600秒只用于文件准备，浏览器填表仍900，不延长授权或反复重置截止。
- Cloud782e0c3修暂停当前批次仅排队时显示batch_paused，保留在途/未知/核验优先级与推进阻断：旧排队失败→5隔离DB测试PASS5.809秒，发布四包/完整业务模块Go测试PASS。
- Cloudd07fe0d修已有批次平台编辑锁定，复制/新建仍可切；旧2失败→29相关/196发布Vue PASS，现已在13实际走查验证。0f1862a/e7dc60c平台分组审查也已修。
- **最新Cloud源码070d3ae，运行前端尚未更新**：9a9693b检查结果未到/手动检查中显示中性检查状态，抑制旧失败提示，就绪和调度不变；旧3失败→30定向PASS，172文件1273完整Web PASS20.25秒。070d3ae在任务列表/详情/批次正式表按verification_required补“公开结果需人工核实”，原状态/统计/动作不变，196发布回归PASS7.26秒。
- 含070的新DMG后台构建已成功但未部署，需包含最新资源顺序修复再次构建；旧构建日志（/tmp/chg130-status-hints-build.log），未部署；待27/78安全结束再切换与走查。只build-dmg不会停止当前App。最后还需要main组合新包与整体验证。

## PR、治理与工具

- Agent21、Cloud59、Desktop20、Workspace72 open未合并；Cloud59已ready。Agent6c/Cloud d07 CI实际通过，最新Cloud070需跟进。Agent八条旧讨论、Cloud三条4707851694/4707918438/4708555461在对应修复与回归后已resolve。没有最新独立审查时不冒称已审。
- Workspace220单测PASS29.468秒、M0配置PASS；最新证据和工程规格已提交至caa7df4，后续原生走查证据7dcf4b8。全部未完成不能标DONE或提前合并。
- 保留Cloud web/example大量他人修改及Workspace docs/design六文件，不暂存、还原或覆盖。只提交本CHG显式路径。无其他Agent并行写入。
- 私有证据根为相邻.local/m2b/chg130-new-data。正常API helper /tmp/chg130_api.py，op.call/stream；8188/api/v1，已有cookie。attempt路径/publication/:id/attempt，历史顺序列表。不要输出凭据/签名URL，不SQL修改业务事实。
- CUA先前拒绝BitBrowser私有平台页面，不能用临时CDP/Playwright/其他私有读取绕过。正常产品Runner/API、隔离测试和全新匿名公开能力测试允许。主动Chrome公开页及起飞原生操作已成功；私有后台完整走查仍未完成，不能伪造。Chrome只创建/关闭自己的独立窗口，保留用户页面；中文用paste，typeText曾只输入数字，提交前均已纠正核实。
- 起飞路径为相邻.local/m2b/desktop-review-mount/起飞.app。CUA活动当前已完成，无接管等待。每段活动后先独立browser-complete再用非CUA工具。用户操作触发changed时重读状态，避免干扰。Git HTTPS push曾停滞，SSH BatchMode/ConnectTimeout成功；不用改全局配置。

## 下一步

1. 跟进27/78下载→正常表单/一次提交→新6c完整自动公开，发现真实问题继续修，不改正常AI内容。
2. 27安全结束后切换070最新包，实际验证检查中状态和22待核实提示；核对计划末批审核/公开/差额/结束及作品列表，保留首批平台拒绝事实。
3. 完成剩余浏览器与UI走查、PR/CI收口、最终main merge commit/全新组合重建；未验证的私有平台后台/主观听音应如实列明，不能用单测替代。
