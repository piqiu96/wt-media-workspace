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
- 正常单条25（output145，真实AI/cover83/84）19:09授权产生71；上传就绪等待900秒超时，file-list根节点一直0；无submit/not_submitted/scene_closed=true，failed。尚未重试25，上传未开始原因仍待解决。
- Plan3原生全批确认已启动，batch10目标1/output148，batch11目标1/output149；首批只建task26，第二批尚未建任务。70/72/73/74均在第5标签等待失败，无submit、已关闭，任务可正常retry；计划按10%停在当前批次，不改变冻结配置。74的约4分钟preparing实查为46MB下载，不能误称死锁。
- 第5标签诊断：index4、observed_count4/expected5、input_empty=true、trim/casefold=false、validation_busy=false；所有匹配tag接口HTTP200/code0/data dict，但尚未看到内部业务状态，不能据外层code0断定业务接受或据此删标签。74已failed/rev24左右，以API实时读取为准。

## 当前源码与运行包

- Cloud源码e7dc60c，运行Go49afaf3（后端未改），Desktop31fd8e1。Agent源码bb814a7，已提交推送。Agent6f834ea的38完整浏览器150.229秒PASS，17标签诊断定向PASS，最新992全量49.182秒PASS；详见evidence/verification.md。
- 当前运行包是Agent6b55005/前端0f1862a，sidecar SHA256=fb2aa147ddb0af182b2338fcd2962834668007a540b581164dbd24b60925d4a8。原生登录和三项环境正常；启动瞬间误报未运行数秒后恢复，尚未修该提示。
- 最新bb814a7/e7dc60c组合build已exit0（/tmp/chg130-tag-business-build.log），正在launch（/tmp/chg130-tag-business-launch.log）。若旧review mount资源忙，正常第二次launch，不强制卸载。部署后核对实际版本/hash、原生登录/三项环境，再仅正常retry原26一次诊断，不重试已受理/公开任务。
- bb814a7只增加安全诊断：tag返回体schema字段、固定数值标记、重复/长度/无效/活动分类及预期标签在可见标签区是否出现，不输出正文/地址/标签。旧隐私用例FAIL→17PASS，992全量PASS。接下来根据业务标记/expected_label_visible判断平台拒绝还是特殊控件，禁止盲改文案或放松最终POST绑定。
- 096a4f1已经包含于新运行包：匿名播放器未启动时点击一次正常播放按钮，仍要求原CID/实际媒体解码；旧需手势用例FAIL→37浏览器112.545秒/991全量46.398秒PASS，实际自动公开仍需复测。匿名Chrome确实可播21，但未证明原自动失败就是这个原因；没有放松URL、时长或CID绑定。
- 原B站上传身份、标签输入、二创、双封面同步/回执、非旧CDN、CSS保存预览、异步标签、缓存清理及PR旧问题已修，过程失败与回归见evidence，不重开额外隐藏画布作为保存条件。当前真实第5标签问题仍未关闭。

## PR与验证

- Agent21、Desktop20、Workspace72、Cloud59均open未合并；Cloud59已ready触发正式审查。gh登录已恢复，SSH推送正常。Agent6f审查completed/无未解决findings，bb最新CI成功；Cloud e7 CI/新审查在途。未满足验收前不合并。
- Cloud4707851694修0f1862a：移除平台后重排组号/批次号，影响幸存固定批次则拒绝。4707918438修e7dc60c：切换批次平台时重排、拒绝不连续平台组和改变固定顺序；保存前也同后端校验结构。旧2+3+2相关用例FAIL→24定向PASS、发布模块23文件192测试PASS。最新组合尚待安装版复核。
- PR4707605028已修169a934，从PATH查FFmpeg；5媒体证明浏览器47.735秒PASS，不冒称实跑Intel。完整all在早前5f7时通过，后来包均独立build/挂载源/hash/原生环境检查；Desktop接管后脚本verify因Agent归属门禁失败，不能称全绿。

## 工具、文件与下一步

- 私有证据根：相邻.local/m2b/chg130-new-data；/tmp/chg130_api.py正常API辅助，op.call/stream，Cloud http://127.0.0.1:8188/api/v1，cookie /tmp/chg130-new-operator01.cookies。不要输出Token/签名URL。/publication/:id/attempt是单数路径且返回按历史顺序列表。
- CUA先前拒绝BitBrowser私有平台URL，不临时CDP/Playwright/其他工具绕过。正常产品Runner/API、隔离测试、公开页面走查可继续。Chrome原生公开页已实际成功；IAB公开页反复30秒超时。只关闭本轮新建窗口/标签，保留用户页面。原生起飞路径为相邻.local/m2b/desktop-review-mount/起飞.app。
- CUA每段活动结束前必须独立输出browser-complete；当前无接管等待。若活动开放，先完成再用非CUA工具。用户操作Chrome会触发状态变化，先重读状态，不干扰其DNF等页面。登录UI沿用会话凭据，不重置密码。
- 保留Cloud web/example大量他人修改及Workspace docs/design六文件，不暂存、还原、覆盖。只提交本CHG自有显式路径。不创建第二套任务/context。
- 下一步：完成bb/e7组合launch与原生环境核对→26一次诊断复测→按实际业务标记/控件证据修复→正常单条25→计划10/11顺序与自动公开→Cloud Web和安装包逐页/平台原稿与公开完整走查→PR审查/CI/main merge commit/最终组合重建→完成后再收口。仍有真实私有平台走查与主观听音工具限制，不能冒称已完成。
