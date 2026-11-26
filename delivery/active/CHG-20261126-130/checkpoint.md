# CHG130 执行检查点

- 唯一状态change.md=VERIFYING；128/129已合入，单执行器串行，不启动未来CHG。真实B站公开与计划闭环未完成，不得归档。
- 用户授权自主修复/测试/PR/E2E/真实发布。文案必须素材→正式AI→核对采用→封面；不得任写测试/制作标题。用户确认百度41已登录、页面正常，不再重复要求处理41。
- 数据基线：固定wt_media_cloud，仅admin/senior01/operator01，密码不改；一级新建选择仅游戏。账号18–21/Profile967–970，B站18/#51/UID3706971620379308；百度19/#41/UID6949353902、20/#39/UID4908760199、21/#34/UID6572476037。未删平台作品。
- 新广告file56，策略1016/template12 ad_pip_ending v1；素材195–200/合成75/任务746–751全部成功，成片145–150。无开头，10–15秒广告画中画、广告声、正片原插入点继续、6秒尾部。画面和客观音轨已核验，129主观听音仍未证明。
- 私有证据根目录相邻.local/m2b/chg130-new-data；normal-publication-content.json与normal-prepared-publication-content.json保存145–150正常内容及封面。18/19旧测试文案不重试；19已正常abandon，20诊断cancel均有未提交/现场关闭证据。不能直接SQL改业务状态。
- Cloud49afaf3运行：已修取消素材投影、操作栏裁切、计划平台硬编码、启动误用百度校验、B站不存在竖封面0加锁；模块及隔离MySQL锁集合回归通过。独立B站batch9创建20/21且同Profile串行；计划3/batch10/11仍未启动，正确预检can_start=true/issues=[]/零缺口。
- 百度22/attempt56真实受理成功：submission1882910900152502022，17:02:42开始提交、17:02:49受理；status=reviewing。稳定首页入口修复有真实效果。后续原稿核验停止，last_check_message提示接口读取需人工核对；尚无可信公开结果，绝不重试22。
- B站21/attempt57证明9d421ce本次File对象与Vue视频行CID/filename绑定成功，上传完成误拦截已解决；57随后标签输入匹配错误。5e13f70修复标签真实input定位，25项套件中的旧24项通过、984单测通过，CI45791667413成功。新包实际部署SHA256=811db5c34af1c4a17b8acc6fb9c2802d921a1ef27070c092a0a49ee5e7d9b3cc，原生工作环境三项正常。
- 21/attempt58在5e新包通过上传及标签后，停在二创checkbox检查。58failed/completed、无submit、not_submitted/scene_closed=true，21 revision36。f9aee0e改用官方VideoRecreate._recreate只读状态、用户控件点击，不依赖内部重复input；隔离复现旧代码失败，新25项浏览器+额外未知控件拒绝2项PASS，984全量PASS。572890e补固定类别诊断，不打印私有异常文本，38项相关单测PASS。
- d4281f9已修PR匿名媒体与原CID播放来源绑定，984全量及30项定向回归PASS；真实B站公开仍未验证，不冒充验收成功。
- 百度双账号回归正常新内容及4张封面已生成、逐张视觉检查通过；batch12保存后零任务，预检零缺口，17:31:39正常启动创建23/24。首次自测调用缺expected_shortfalls返回409、传完整preview多余字段返回400均为调用错误；使用契约category_id/shortfall后成功，不是产品缺陷。23/attempt59在首页菜单hover超时，可信未提交/已关闭；用户确认#34正常后，通过原生“已经处理，继续原尝试”恢复24/60；17:37:35真实受理，submission1882913089029275698，reviewing，不得重复投稿。23/62已成功受理；旧59不重放。
- 572890e包构建完成但未部署；随后完成1f98f70（有网络回执也必须当前File上传完成、提交前强制再查）与09bb371（已结算缓存识别固定封面副本/诊断文件，不放宽未知文件和链接）。三个网络回执绕过用例旧代码均FAIL→修复后PASS；47项浏览器+缓存PASS，986项全量PASS。fbafd6b补原稿核验固定原因/数值状态诊断，42项定向PASS。
- fbafd6b包已部署（sidecar SHA256=b276d4c7854d001517e8c6e6f4cc2614e67f7469fdba3ef254cd48bde37519de），原生环境三项正常；22/24已结算缓存目录实际清理成功，09bb371真实复验PASS。21/61通过二创后在双封面同步原生input数量检查失败，可信未提交/已关闭；23/62已真实受理submission1882913592059779284，reviewing，不再重试23。原生环境检查曾启动瞬间不可达、重新检查三项正常；不能把瞬间提示当任务失败。
- 缓存warning根因已确认：成功百度任务留下cover-upload副本和cover-selection诊断，旧白名单拒绝清理；09bb371及正式工程规格已修，尚待新包真实清理复验。warning未改变受理结果；新包实际缓存清理已成功。
- PR：Agent21/Desktop20/Workspace72、Cloud59(Draft)均已创建未合并。用户回复ok后实际gh auth status验证登录已恢复，Cloud PR59创建成功；不再记录认证阻塞。最新fbafd6b和999a2d3 Agent CI成功，Cloud59 CI45793563267成功，Workspace72 CI成功。新增PR反馈4706058925已由1f98f70修复，仍需最终审查/CI。
- CUA曾拒绝BitBrowser平台URL，不用临时CDP/Playwright或其他工具绕过；正常业务Runner/API继续授权。tauri原生走查可用；无接管等待。主动平台浏览器走查尚缺，不能声称完成。用户#34答复已按原attempt60继续并受理。
- 下一步：完成二创修复真实复测21→修真实后续问题；百度23入口超时及22核验停止诊断→24原现场处理；计划3两批完整执行→公开原稿/作品读回→最终逐页及新包组合复验→PR问题/CI/merge commit入main→满足全部验收后归档。
- 保留其他会话Cloud web/example及Workspace docs/design六个脏文件，不暂存/还原。

- 任务24于17:59:13可信读回published：公开作品7277548266066867187、work_url=https://mbd.baidu.com/newspage/data/videolanding?nid=sv_7277548266066867187，平台实际published_at17:37:33。原稿与UID及匿名可播放媒体匹配。23仍审核中；22核验停止，不伪造结果。
- 主动公开页走查：IAB连续30秒超时，Chrome browser-provider不可用；CUA原生Google Chrome新标签键盘导航成功，实际标题/话题一致、登录入口显示未登录、02:00时长、观察到游戏画面及广告PIP画面。原生坐标点击/滚动曾windowNotFoundAtPosition，但键盘Raise/Home/End可用。只关闭本轮新标签，未操作其他标签；未完成尾部/主观听音，不冒称已全片走查。该公开页与先前被拒的BitBrowser私有后台不同，未绕过私有页面拒绝。
- 999a2d3修双封面同步：官方CoverEditor两个比例控件共享isSyncEnabled，不依赖单个native input；先旧代码复现FAIL→30项B站浏览器PASS。首次987单测有1项旧MagicMock未定义evaluate导致清理测试提前超时，补齐模拟结构后987全量PASS（/tmp/chg130-cover-sync-unit-final.log），不冒称首轮通过。CI45797607182 success。新999a2d3包build完成/tmp/chg130-cover-sync-build.log，launch-dmg正在/tmp/chg130-cover-sync-launch.log，部署后正常retry21。

- 最新运行999a2d3已部署，sidecar SHA256=ce26298581f01603bca33e6482ae436587c7ba43af34602d213d6d285a5814a4，原生环境三项正常。正常retry21产生63，通过同步开关及两张封面文件校验/画布解码，后封面完成等待回执超时（_fill_covers:520），未submit且现场关闭。不要重试已公开23/24。
- e06f18b修补另一条后台事件路径：已由guard绑定的封面请求也从Context.response读取；只读该request的回执，不放宽最终双封面URL校验。增加导出accepted/ratio、响应HTTP及超时exports/receipts/dialog_visible固定诊断。旧context-cover用例FAIL→14项定向PASS、988全量PASS、2项完整表单浏览器PASS。新包正在/tmp/chg130-cover-response-build.log；还未部署，不能断言这就是63真实根因。
- 百度23也可信读回published；batch12执行ended，target2/created2/published2/shortfall0，verification_required0。原生列表100%，详情已发布2/失败0/待处理0/待平台公开0，公开率2/2与操作记录一致，结束后只返回、无编辑/重启执行动作。完成本轮真实批次列表和详情走查；其他页最终走查仍继续。
