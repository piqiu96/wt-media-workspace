# CHG130 执行检查点

## 当前范围与约束

- change.md唯一状态VERIFYING，128/129已合入；单执行器串行，不启动未来CHG。用户要求编码、自测、PR审查修复、真实E2E、主动浏览器与安装包走查直到交付，不逐项等待确认。当前真实闭环和最终main合并未完成，不能标DONE。
- 正常发布内容必须素材→真实AI→核对采用→双封面；不任写测试标题/简介、不删除原标签规避问题。计划执行后目标、批次及配置冻结。107保存零任务/占用、108启动原子建单/占用/授权、109按10%推进的结论不变。
- 固定数据库wt_media_cloud，用户仅admin/senior01/operator01，密码沿用原值且不入文档。一级类目只提供游戏，历史类型只解析。四账号18–21/Profile967–970：B站18/#51/UID3706971620379308；百度19/#41、20/#39、21/#34。用户已确认51/41/34正常登录，DeepSeek范围与真实上传/发布授权已给，无待确认项。
- 新广告file56来自用户三角洲_网站.mp4，策略1016/template12 ad_pip_ending v1，无开头、10–15秒广告PIP/广告声、原插入点续播、6秒尾部。素材195–200/合成75/任务746–751/成片145–150成功；已核验画面/客观音轨，主观听音与平台全片尾部仍未证明。

## 真实业务结果

- 百度双账号batch12已结束，target2/created2/published2/shortfall0/verification_required0。23/62公开8351506294205442839，24/60公开7277548266066867187；主动Chrome检查两页正常标题/话题/02:00游戏播放，24实看广告PIP。原生列表/详情数量及结束按钮一致。不再重试23/24。
- 百度22/56已受理1882910900152502022，但自动原稿核验停止需人工核实；不能重复投稿或伪造公开。旧18/19已正常abandon，20诊断cancelled，历史保留。不能SQL改业务状态。
- B站21/69真实受理aid117682405968275，19:26后台开放浏览但匿名媒体证明未齐全而停止自动核验。之后工程师主动Chrome独立无痕窗口实看登录入口、原稿标题/作者/营销声明、00:17/02:00、游戏与广告PIP；官方无cookie公开元数据aid/owner/title/state=0逐项匹配。经正常resolve人工补录为published/work12/rev88，平台published_at19:06:31。明确是人工补录，不冒称自动核验通过；不再重试21。batch9已结束：目标2/公开1/诊断取消1/缺口1。原生作品列表查询显示总3/今日3，新增B站作品12关联正确。
- 正常单条25（output145，真实AI/cover83/84）19:09授权产生71；上传就绪等待900秒超时，file-list根节点一直0；无submit/not_submitted/scene_closed=true，failed。已在核实71未提交/关闭后正常retry；25/76已于20:42:31真实受理aid117682791777077，reviewing/rev13，原稿仍处理中，未计公开。
- Plan3原生全批确认已启动，batch10目标1/output148，batch11目标1/output149；首批只建task26，第二批尚未建任务。70/72/73/74均在第5标签等待失败，无submit、已关闭，任务可正常retry；计划按10%停在当前批次，不改变冻结配置。74的约4分钟preparing实查为46MB下载，不能误称死锁。
- 第5标签诊断：index4、observed_count4/expected5、input_empty=true、trim/casefold=false、validation_busy=false；所有匹配tag接口HTTP200/code0/data dict，但尚未看到内部业务状态，不能据外层code0断定业务接受或据此删标签。74已safe failed。75后续900秒下载截止，尚未打开浏览器却回传uncertain；只读BitBrowser /browser/ports两次确认Profile关闭，核对原75仅preparing/无ready/无submit及本地claimed阶段ResourceVerificationError后，正常resolve补录为failed/rev30，保留原结果。随后正常retry26现queued/attempt=None/rev32，单条25/76先执行。不能把这次人工核实称为新修复自动通过。

## 当前源码与运行包

- 当前运行Agent9e77ffb、前端Cloud e7dc60c、Desktop31fd8e1；Go后端仍49afaf3（后续仅前端修改）。新包build/launch均exit0（/tmp/chg130-ready-input-preparation-build.log/-launch.log），实际sidecar SHA256=64349a47b97bbfba7d1498200c6316f0f764abd97f7ee47617065179743dd730。operator01沿用原密码登录，原生环境三项正常。25/76已受理审核中；原生batch10恢复后26/77准备中，勿重启或重复授权。
- Agentbb814a7诊断包含tag schema字段、固定业务标记/错误分类及expected_label_visible；尚未实际读到第5标签内部结果，因为75在下载阶段遇到旧时限。不能假设为平台拒绝或特殊控件，也不能删标签/放松最终POST匹配。
- c424233修百度隐藏菜单项误阻塞可见发布菜单：旧真实浏览器用例FAIL，4定向9.345秒PASS、52完整百度浏览器82.770秒PASS、11单测PASS。首轮修复后1条测试错误地读取跨导航window变量失败，改用测试sessionStorage后重跑通过，未隐去首轮失败。
- b304b7e将文件准备独立绝对时限默认改3600秒，保留30秒单次网络等待/逐次授权核对/三文件同一截止，不延长浏览器填表时限。准备失败尚未返回现场时，只读核实Profile关闭才回报可重试未提交；仍打开/未知保留uncertain且不关闭无归属现场。旧健康20分钟下载和关闭现场失败分类两项FAIL→55相关PASS，995全量46.831秒PASS（/tmp/chg130-resource-preparation-*）；正式工程规格已同步，未改跨仓契约。
- 9e77ffb修上传输入框初始化disabled时程序设置文件丢失：旧隔离浏览器用例FAIL→单项4.662秒PASS、完整39 B站浏览器106.655秒PASS（/tmp/chg130-upload-input-*）。不重选文件、不绕过本次File/CID绑定；实际25是否因此恢复待本次76结果证明。
- 096a4f1匿名播放器未启动时点击一次正常播放按钮，仍要求原CID/实际媒体解码；37浏览器/991单测已通过，但实际自动公开仍需本轮复测，不能把手势认作21实际失败根因。未放松URL/时长/CID检查。原上传、封面及历史PR问题修复详见evidence，不重开隐藏画布作为保存条件。

## PR与验证

- Agent21、Desktop20、Workspace72、Cloud59均open未合并；Cloud59已ready触发正式审查。gh登录已恢复，SSH推送正常。Cloud e7 CI及自动审查均通过，无未解决findings；Agent最新9e CI/审查需继续查。旧百度审查4707967824已由c424233修复。未满足验收前不合并。
- Cloud4707851694修0f1862a：移除平台后重排组号/批次号，影响幸存固定批次则拒绝。4707918438修e7dc60c：切换批次平台时重排、拒绝不连续平台组和改变固定顺序；保存前也同后端校验结构。旧2+3+2相关用例FAIL→24定向PASS、发布模块23文件192测试PASS。e7已随9e安装包部署，主动新建计划只做未保存走查：双平台矩阵/两批→移除百度确认→剩B站一批、目标1/分配1、显示顺序01，返回后计划仍仅原3。没有冒称这次做了真实保存。
- PR4707605028已修169a934，从PATH查FFmpeg；5媒体证明浏览器47.735秒PASS，不冒称实跑Intel。完整all在早前5f7时通过，后来包均独立build/挂载源/hash/原生环境检查；Desktop接管后脚本verify因Agent归属门禁失败，不能称全绿。

## 工具、文件与下一步

- 私有证据根：相邻.local/m2b/chg130-new-data；/tmp/chg130_api.py正常API辅助，op.call/stream，Cloud http://127.0.0.1:8188/api/v1，cookie /tmp/chg130-new-operator01.cookies。不要输出Token/签名URL。/publication/:id/attempt是单数路径且返回按历史顺序列表。
- CUA先前拒绝BitBrowser私有平台URL，不临时CDP/Playwright/其他工具绕过。正常产品Runner/API、隔离测试、公开页面走查可继续。Chrome原生公开页已实际成功；IAB公开页反复30秒超时。只关闭本轮新建窗口/标签，保留用户页面。原生起飞路径为相邻.local/m2b/desktop-review-mount/起飞.app。
- CUA每段活动结束前必须独立输出browser-complete；当前无接管等待。若活动开放，先完成再用非CUA工具。用户操作Chrome会触发状态变化，先重读状态，不干扰其DNF等页面。登录UI沿用会话凭据，不重置密码。
- 保留Cloud web/example大量他人修改及Workspace docs/design六文件，不暂存、还原、覆盖。只提交本CHG自有显式路径。不创建第二套任务/context。
- 当前batch10曾正常暂停时计划3误显示waiting_tasks；20:44已从安装版原批次详情确认继续，26/77正常领取。已修Cloud暂停批次投影（仅排队→batch_paused，在途/核验不被遮蔽），5项隔离DB/发布四包单测PASS；修复782e0c3已推送，后端待在途任务安全结束后部署，不能提前声称UI修复已生效。
- 下一步：跟25/76文件准备/上传与标签实际结果，以及随后26的新诊断。根据真实内部标记/expected_label_visible修适配，不凭推测改文案；完成10/11推进和自动公开、Cloud Web/安装版逐页与平台原稿/公开完整走查、PR/CI/main merge commit/最终组合重建，再收口。75已用正常入口核实，不重复resolve。25/26现已排队/执行，不追加retry，不重启在途进程。仍有私有平台走查与主观听音工具限制，不能冒称完成。
