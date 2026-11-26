# CHG130 验证记录

## 当前实测：B站登录与环境

2026-11-26，通过已安装 Desktop 的本人账号列表打开实际 Profile，而非信任历史 `login_status=normal`：

- 账号1 / Profile10 / 比特窗口51：当前创作中心跳转到B站登录页，未发起投稿。已请求账号持有人恢复登录；等待期间继续独立的契约、编码及测试。
- 账号5 / Profile40 / 比特窗口32：创作中心连接失败 `ERR_SOCKS_CONNECTION_FAILED`，不能作为可用并发账号。
- 本次尚无B站稿件受理或公开证据，真实单条、批次、两批计划验收均未通过。

128、129依赖的各仓合并提交已核对；`wt.py chg start`、`chg resume` 已通过。各仓在130分支实施；其他会话的原型与设计工作稿保持原状，不纳入本项提交。

## 登录恢复后的实际字段复核

用户回复窗口51已登录，并确认在投稿页明确协议提示下上传本轮测试成片、继续已授权验收。工程师通过真实比特浏览器页面上传 `/tmp/chg129-output141.mp4`，实际显示“上传完成”，未点击立即投稿，未生成正式发布成功证据。

- 头像个人空间显示“视角：我自己”，当前账号是游戏魔王嘟嘟，UID `3706971620379308`，与Cloud账号1旧UID不同。禁止沿旧账号归属继续发布；后续须正常识别并建立正确关联。
- 标题计数 `/80`、简介 `/2000`；标签最多10个，粘贴21个汉字后实际输入只保留20个。自动带入“短片/原创/剪辑”标签，执行器须清除再填冻结标签，不能保留自动原创主张。
- 声明实际单选：内容无需标注、含AI生成内容、含虚构演绎内容、内容含营销信息、个人观点，仅供参考、内容为转载。转载展开200字来源说明；独立可选权利勾选，不存在旧式必选原创/转载字段。
- 封面制作窗口明确4:3首页推荐和16:9个人空间，双比例同步为可选。当前分区选择“游戏”即关闭，未出现子分区，真实分区ID尚待平台读回。
- 更多设置包含公开/仅自己可见；商业推广另有花火官方合作/其他及行业、品牌等，属于独立业务，不自动选中。本轮核查后已取消商业推广选项，声明恢复内容含营销信息。

界面核查通过；平台受理、公开读回、任务/批次/计划 E2E 尚未执行。代码定向测试当前通过 publish 全模块和 config，后续修改需继续回归。

## 正常账号识别与准备记录

为避免把新登录错误归入旧UID，通过正常账号API创建本轮账号17，保留旧账号1的身份与历史，仅解除其当前Profile10绑定；账号17绑定Profile10。随后在真实安装版“社媒账号”点击账号17的“检查”，Agent实读后，页面显示游戏魔王嘟嘟、UID3706971620379308、正常、刚刚。Cloud GET账号17读回：`identified`、`normal`、`last_check_status=completed`，类目1/4，检查时间2026-11-26 08:40:09 +08:00。不是手工伪造识别回报。

当前窗口51官方公开查询返回既有视频BV135WM6uE4A的`aid=117590282275872`、`tid=17`、`tid_v2=2071`。仅用于核实标识格式，不是本轮发布证据；新页面“游戏”的实际分区标识仍须投稿准备读回，不能用既有稿件推定默认分区。

## Cloud基础实现与自动化验证

提交：`a2089c1`（平台规则、独立B站内容/双封面、冻结资源/引用、准备/计划守恒、AI建议、结果规则、按能力领取）；`a2bf704`（Cloud-Agent契约说明引号修正及契约验证）。B站部署配置缺省关闭，未在真实环境开启。

- `go test ./...`：PASS。
- 发布、作品、Cloud-Agent、config定向测试：PASS；覆盖旧百度JSON保持、B站独立字段/长度/封面、跨平台内容拒绝、幂等、复制不继承成片封面或确认、计划按平台守恒、空间封面证据匹配、原稿AID/URL绑定、AI只建议不采用、旧Agent能力缺省仅百度等。
- `/tmp/chg109-contract-validation/bin/python scripts/verify/test_publication_plan_contract.py`：20项PASS，包含Cloud API和Cloud-Agent两个OpenAPI的正式校验。额外校验发现并修复既有未引号化响应说明的YAML歧义。
- `git diff --check`：PASS。上述结果不替代真实数据库闭环、Agent和页面测试或平台公开验收。

接下来：实现Agent平台发布与原稿核验、共享Vue和Desktop消费，完成编码自测后，强制新环境进行单条/批次/两批计划E2E及主动浏览器走查。未通过的验收项继续保持未勾选。

## 当前接口与封面格式复核

通过窗口51的DevTools Network/Response，读取当前投稿页的 `GET /x/vupre/web/archive/human/type2/list`：`data.type_list` 中游戏为1008，验证不能沿用旧作品分区17。稿件管理实际读取 `GET /x/web/archives?status=is_pubing%2Cpubed%2Cnot_pubed&pn=1&ps=10&coop=1&interactive=1&client_type=1`，响应含 `data.page={pn:1,ps:10,count:2}` 和 `arc_audits[].Archive`，已有公开记录含aid/mid/title、state=0、state_desc=开放浏览、attrs.is_owner=1/no_public=0。两条均为既有稿件，不计为本轮验收。

当前官方投稿静态源码 `https://s1.hdslb.com/bfs/static/creator-monorepo/videoup/static/js/index.42bdcf01.js` 复核：提交端点 `/x/vu/web/add/v3`；正文包含human_type2、creation_statement、copyright/no_reprint、is_only_self、videos.cid/filename、cover/cover43，封面上传在最终提交流程内执行。平台二创默认值可能开启，适配器须显式关闭，不自动接受独立协议。测试上传的自动内容建议会再次改变声明/标签，因此提交前必须重新核对冻结内容，不能相信曾经填入的值。

封面文件输入accept实读为 `image/png, image/jpeg`。Cloud提交 `d3cdd7d` 补齐发布前、准备及批次PNG/JPEG校验和只读规则；`go test ./internal/modules/publish/... -count=1`、20项正式契约测试、diff检查：PASS，百度已有格式/元数据兼容测试通过。

Agent已补准备/独立空间封面、平台内容冻结、只读原稿协议、核验及一次提交保护实现。`PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -p 'test_bilibili*.py'`：19项PASS（含原有3项准备测试），验证精确分页、重复记录拒绝、错误UID/标题、审核/退回/私密、匿名元数据、停止后禁止提交、重复提交拦截、表单与实际POST差异拒绝、PNG/JPEG与文件原字节。尚未运行新适配器的真实投稿；受控浏览器、完整Agent回归、共享页面与真实E2E继续实施。

## 编码与完整自测阶段

Cloud增加真实分区选项（完整目录共30项，1001–1027及1029–1031），由只读平台规则统一提供。批量模板封面沿既有图片域接口增加B站recommendation/space两种规格，分别4:3和16:9；百度landscape/portrait保持原义。修复批量现成图片把比例误传为横/竖分类的问题，按实际比例、格式跨页选择。正式契约增加跨平台规格拒绝用例。

共享Vue在原有单条/批次/计划框架内增加B站字段、草稿与空间封面独立引用、AI审阅采用、列表和详情标题、跨平台目标矩阵；配置默认只应用于新内容，不覆盖保存配置。Desktop只更新Cloud-Agent消费修订，Local Agent API不变。

本轮实际自测：

| 检查 | 实际结果 |
| --- | --- |
| Cloud `go test ./...` | PASS；真实业务数据库闭环留待下面E2E，不以单测替代 |
| Cloud图片全模块测试 | PASS，覆盖平台专用规格及跨平台拒绝 |
| 正式OpenAPI与业务Schema | 21项PASS，含封面接口及旧百度兼容 |
| Agent完整单测 | 970项PASS |
| Agent受控浏览器完整回归 | 52项PASS；包含百度回归及B站实际匿名媒体加载/登录专用媒体拒绝 |
| B站受控浏览器定向 | 6项PASS，两个不同颜色/比例的真实图片、独立空间封面变化拒绝、表单与最后POST篡改拒绝、一次受理及匿名播放证明；不等同真实B站受理 |
| Web完整测试 | 初次并行构建时1项模块导入测试超时；限制到2个Worker后1258项全部PASS，未放宽断言或超时 |
| 发布模块定向 | 184项PASS；最后UTF-16/封面短标题长度对齐后24项相关定向PASS |
| Cloud Web / Desktop前端构建 | 两端PASS |
| Desktop `scripts/test.sh` | Rust 561项PASS、6项既有忽略；打包/控制脚本及Python检查PASS，Windows实际安装未在macOS执行 |
| 治理及文档 | Delivery、产品总计划、配置及文档检查PASS |

以上仍是编码自测阶段。尚未创建本轮正式B站发布任务；平台受理、匿名公开、独立批次、两批计划、最终安装包及真实浏览器逐页走查尚未计为PASS。接下来按已有环境规范强制重建和启动，再执行这些真实验收。

## 新包真实单条首轮（2026-11-26）

- 使用私有验收配置开启B站，固定原数据库；强制重启Cloud、Worker、Compose Worker/Scheduler、Agent及两端前端。新包`0.1.0-local.31fd8e1950`挂载版本记录核对通过，frontend=`0.1.0+45f60b3.dirty`（dirty仅他人原型文件），使用operator01原密码登录。
- 窗口51当前真实账号为游戏魔王嘟嘟（UID 3706971620379308），通过正常账号检查识别后使用账号17；旧账号1的历史身份未改写。
- 单条任务17由新包UI创建，采用129成片141；真实DeepSeek生成标题/简介/标签、逐项采用后按事实修订，首页推荐封面55由模板3和成片缩略图渲染，空间封面47独立保留。声明为内容含营销信息，自制权利未勾选。
- UI执行授权后attempt40进入preparing/ready，随后提交前失败，正式状态failed，`submit_started_at=null`，未取得稿件回执；不计为受理或公开PASS。
- 失败日志中的断开浏览器异常遮蔽原始错误，补充清理失败不遮蔽原异常的定向测试及修复（Agent14c4b24，4项PASS）；Cloud b4372d4修复B站空间封面仍称竖版封面的无障碍名称。正在重建全环境后继续定位。
- PR审查仍未完成：Agent PR21已建立；连接器返回GitHub连接不可用，原生Chrome Cloud对比表单及备用浏览器均响应超时。未将其记为审查通过。
- 额外核对到129归档里“听音”勾选与证据不一致：既有证据仅实际播放和PCM相关性，不能证明主观听音；本轮继承该未满足项，最终不得把数值音轨检测冒充主观听感。

## 真实上传故障与PR整改续验

- attempt41保留原始错误后定位到上传文字点击超时；当前官方投稿源码中该文字属于`upload-btn no-events`，改为唯一视频上传组件`.upload-wrp .upload input[type=file]`，6项受控浏览器用例PASS，提交9b13b70。
- attempt42仍在导航处超时，未进入提交；改为HTTP提交导航成功后等待真实上传控件挂载（单独120秒准备上限），而非等待整个文档资源完成。新增一个故意未完成无关defer资源的真实浏览器用例。
- [Agent PR21](https://github.com/piqiu96/wt-media-agent/pull/21)两条P2均已落实：临时上传副本在成功和异常路径均清理；只接受本次确认双封面保存期间的两笔实际图片上传回执，按4:3/16:9映射，最终POST逐一精确匹配URL，拒绝交换、陈旧或其他同CDN图片。官方源码核实，图片导出在封面“完成”动作内通过`/x/vu/web/cover/up`提交。
- Agent73a3829：全量974项单元测试PASS。完整浏览器55项首次54项通过，新增无关资源测试因Python内建回调不支持Playwright包装而报错；修正为lambda后相关9项全部PASS（含原稿公开2项、最终URL交换/替换拒绝、临时文件清理及异步页面挂载）。日志`/tmp/chg130-agent-review-all.log`、`/tmp/chg130-agent-review-browser-all.log`、`/tmp/chg130-review-cover-final.log`。不将初次完整命令记为全绿。
- Cloud单条页面46项定向回归PASS，日志`/tmp/chg130-final-detail-ui.log`。Desktop PR20已创建：https://github.com/piqiu96/wt-media-desktop/pull/20 。Agent9b13b70对应CI verify为success；新提交CI/独立审查仍待核对。
- 期间本机负载实测超过600，隔离浏览器启动/连接也失败；仅清理本轮`wt-publisher-browser-*`测试进程，不终止其他BitBrowser Profile。负载回落后恢复测试。未把资源异常下的超时记为平台业务通过。
- 当前继续强制重建73a3829组合，尚无真实受理/公开、独立批次、两批计划或最终浏览器验收PASS。

## 当前环境阻断及CI核对（11:09后）

- 最新组合已强制重建并挂载，frontend=`0.1.0+b4372d4.dirty`，Agent源提交73a3829；健康、Worker/Scheduler、两端入口、资源来源、DMG和登录门禁通过，已在新包正常登录。
- task17 / attempt43在`publication_preparation.py:104`的Profile归属扫描处停止，未打开本次执行现场；Cloud保守投影为`uncertain`，没有稿件回执或公开作品。再次读取BitBrowser完整快照：main_user_id仍为`2c9bc06191effa4e0191f9589996619f`，仅剩窗口41/39/34；原窗口51的Bit Profile ID不在列表。已请求恢复原窗口及登录或提供另一个可用本人B站窗口；不盲目重试未知任务。
- 随后浏览器工具明确报告Mac已锁定、自动解锁失败。已请求手动解锁，期间不继续CUA操作或伪造浏览器验收。
- Workspace PR72已由GitHub页面提交并由公开API确认open/非draft：https://github.com/piqiu96/wt-media-workspace/pull/72 。Cloud PR尚未建立，仅准备好表单。
- Agent73a3829自动审查completed且无finding；其CI verify失败于Test Agent步骤。完整日志下载API无认证返回403（要求仓库管理权限），现有连接器不可用。Desktop31fd8e1与Workspace8f98503对应CI均success。
- 为定位CI，创建本轮独立干净工作树`/tmp/chg130-agent-ci`，以已安装Python3.12运行`UV_PYTHON=3.12 scripts/bootstrap.sh`、`scripts/test.sh`：974项PASS，脚本退出0且未污染.local。日志`/tmp/chg130-agent-ci-python312.log`。本机3.12未复现Linux CI失败，未宣称CI已修复或通过；解锁后继续读取Actions完整日志定位。

## 用户指定的干净数据基线（2026-11-26）

- 先停止 Cloud、Worker、Scheduler、Agent、Desktop，再备份固定 `wt_media_cloud` 数据库与两种运行方式的 Agent SQLite/发布目录。备份保存在本机私有 `.local/backups/test-reset-20261126-114026`，不提交任何数据库、凭证或素材备份。
- 事务清空36张旧业务/执行表；保留迁移、技术合成模板、不可变存储校验记录及准入切换标记。仅保留 admin、senior01、operator01 与原密码、默认运营团队和授权；删除其他用户/旧团队。保留游戏子类目火影忍者、绝区零、三角洲，其他一级类型无业务数据。未删除平台已发表作品，未修改比特浏览器实际窗口与登录。对象存储旧资源键已存入私有备份清单，未执行整个共享存储桶清空。
- 源码 Agent 和安装包 Agent 的旧任务日志、待回报结果、发布草稿与发布工作目录均清理，防止已删除任务重放。旧 task17/attempt43不再执行。
- 用正常 Desktop 会话换取 Agent Token，由 Agent 实读并绑定比特主账号，完整扫描→提交扫描→确认4个新镜像；随后逐个正常创建账号、绑定窗口、启动账号检查、Agent实时识别、回报结果。没有复制旧账号身份或伪造检查结果。
- 新窗口：967/51（B站）、968/41、969/39、970/34（百度）；新账号18–21，全部归operator01/三角洲。B站UID3706971620379308（游戏魔王嘟嘟），百度UID6949353902（游戏主播甜甜）、4908760199（平台未返回昵称）、6572476037（你阿邱爷）；4/4登录检查normal。
- 数据库与API读回：users=3，profiles=4，accounts=4（B站1/百度3）；materials/source_contents/operations_files/image_asset/cover_template/compose_strategies/compose_tasks/composite_outputs/publication_plan/publication_batch/publication_task/work均0。当前operator01可见2个已授权游戏类目，管理员目录共3个游戏类目，未擅自扩大用户授权。
- 一级选项只保留游戏；历史AI/二次元类型保留解析兼容，新建请求只允许game。PRD、ADR0028、提供方identity契约已同步。Cloud提交6a366f7。定向identity全包测试PASS，共享类目/字段组件7项PASS；真实admin API创建AI类目返回HTTP400，未产生数据。
- 全流程发布验收改用用户即将提供的新广告切片与新策略；本轮数据重建不等于B站公开、批次/计划或最终UI验收已完成。

- 重建环境复核曾发现compose_worker_capacity基础行被清空，Worker因“sql: no rows”退出；已按迁移20261014_059恢复id=1/max_running=2（基础容量，非业务任务），随后重启并重新验证。首次wt chg verify的Cloud全模块、Agent974项、Desktop及Workspace220项测试阶段已运行，环境阶段因该基础行缺失失败；不将首次总命令标为通过，后续仅复核修正后的环境。
- 新包构建成功，前端来源0.1.0+6a366f7（digest b57ae1f87ac471e87840f0a770a1aec3fe0e4afcb39b8f7b846e61f783c51bf1），DMG位于Desktop target/release/bundle/dmg；未冒充已完成包内UI人工走查。

- 修正基础容量后，local_env.py up --force-restart及verify均退出0；Cloud、文件Worker、合成Worker、合成Scheduler、Agent、BitBrowser、双前端入口、前端来源/新鲜度、DMG与operator01原密码登录烟测全部PASS。日志/tmp/chg130-reset-environment-final.log、/tmp/chg130-reset-final-verify.log。配置治理、Product/Master对齐、Delivery治理检查PASS。已注销临时维护Desktop会话，避免用户登录时被维护会话占用。

- launch-dmg退出0，已从新DMG挂载并打开起飞.app；挂载来源校验读回frontend=0.1.0+6a366f7.dirty（Cloud另有其他会话原型工作区改动，未纳入本次提交）。这证明新包来源，不代表已完成界面走查。

## 新广告与重新抓取素材（2026-11-26）

- 用户指定三角洲_网站.mp4作为新广告；实读32,861,804字节，26.933333秒，1920×1080 H.264/AAC，SHA256 b730c4fa73d280a7389dd66e0d3b53108432f024ce5afc454f55bc7120247c51。通过正常文件上传API写入file56，未复用旧广告。
- 最新源环境与DMG强制重建，local_env.py all --force-restart退出0，日志/tmp/chg130-new-ad-environment.log。CUA已正常打开新包并登录operator01，账号页查询显示4账号/4正常，真实UI访问阻断解除。
- admin创建手动抓取策略44，三角洲类目4、团队1；真实抓取任务96成功：scanned/found/added=20，failed=0。operator01将6条内容转素材189–194。
- 新策略1016：广告画中画＋片尾模板12/v1，负责人operator01，手动执行，一次最多6条，单输出组1份，B站/百度标签；无开头，广告插入10–15秒，前景宽度0.92，转场0.2秒，成片最长120秒。广告引用明确指向新file56。
- 建任务前个人素材归属门禁拒绝未加入个人素材的输入；经正常usages接口传strategy_id=1016/operator_id=3建立关系后，创建合成批次74、任务740–745。未直接写业务数据库或伪造下载/成片。
- 首个源视频实测64分13.83秒、1.4259GB，不适合本轮短片验收；从正常内容搜索接口重新获取三角洲精彩片段，实读CDN元信息和媒体时长选择80.6–243.23秒的6条。导入5条新内容、1条去重，material195–200；创建批次75、任务746–751（创建6/失败0）。长素材相关任务经正常cancel入口取消，保留真实历史，不删除失败证据或冒充完成。
- 已通过浏览器读取Agent CI失败日志（run45746330323/job139663180469）：test_slow_report_of_one_attempt_does_not_block_other_heartbeat在进入停留屏障前就阻塞同attempt心跳，依赖线程时间片。改为停留后再触发阻塞，新增明确blocked_report事件保证实际阻塞发生，再检测另一个任务心跳；不改发布运行逻辑。Agent7257cc9已推送；7项定向、20次重复及scripts/test.sh 974项均PASS。CI结果待新运行核对。
- Chrome在Cloud95文件比较表单上出现原生AX超时；已有表单准备不等于Cloud PR已创建。不会宣称已提交或合并。

- Agent7257cc9 GitHub verify已completed/success：run45752687795/job139683954898。抓取策略44已改为手动短素材关键词“三角洲行动 一分钟 精彩瞬间”。批次74六项已读回cancelled；素材189真实准备成功保留，不用于继续旧投稿。新任务746–751继续正式Worker执行。


## 新切片真实成片及安装包建单（2026-11-26 12:45）

- 新合成批次75的746–751全部success，产出145–150；材料198/197/195/196/199/200分别对应145/146/147/148/149/150。前五条120秒，第六条112.933秒；1280×720，均读取新file56广告快照，before/ad/after/ending四段，插入点10–15秒，广告后正片从插入位置续播，片尾6秒。未将已取消批次74计为成功。
- 下载真实145并核验SHA256 05292c5378f0d18abc232f1462c3f1b8e10900934650deec7357d45e8d113ad4；检查4/20/50/117秒画面，确认正片、广告画中画、续播、片尾实际存在。新包成片详情打开视频链接后，Chrome实际播放新广告画面，音频播放指示可见。广告段与用户广告5秒处的3秒PCM相关性0.999576，零毫秒偏移；这是客观音轨检测，不能替代主观听音。
- 正常创建并发布启用封面模板5/6/7（1200×900、1920×1080、1080×1440），通过实际渲染生成145–150所需封面file70–81。安装包单条建单另外现场生成file82推荐封面，空间封面使用145的file57缩略图。
- 实际走查发现取消准备任务后素材仍显示准备中，Cloud48782b0增加生产域投影修复：仅匹配同团队/素材/用途的已取消准备且无新pending/running任务，恢复not_downloaded；保护ready与新准备记录。真实MySQL会话临时表7种情况PASS，生产/jobs/filetransfer回归PASS，日志/tmp/chg130-cancelled-material-live.log及/tmp/chg130-cancelled-material-regression.log。固定库真实读回190–194恢复待准备，189/195–200仍ready，安装包我的素材页面同步验证。
- 最终本轮组合Cloud48782b0/Agent7257cc9/Desktop31fd8e1重新执行local_env.py all --force-restart，全部环境门禁PASS（/tmp/chg130-new-ad-projection-environment.log）；新DMG挂载来源一致，前端0.1.0+48782b0.dirty（他人原型改动不纳入本次提交）。
- 新包实际从成片145的去发布进入B站快速发布，选择账号18、游戏分区、三项标签、营销信息声明；未勾选自制权利。填写源作者及原链接，现场生成/检查推荐封面并核对空间封面，正式创建新任务18。正常start接口授权后首次attempt44进入running/preparing；尚未取得受理/公开证据。
- 新数据真实DeepSeek生成标题、简介、标签成功（new-ai-content.json），结果保留来源和营销提示，未臆造战绩或授权。当前任务18采用人工核对的事实文案，未将后台生成成功冒充UI逐项采用。
- GitHub原账号正常CLI登录恢复仍等待验证器验证码；页面显示Existing access，不新增权限。Cloud PR表单已准备但尚未提交；其余三PR未合并，不能宣称全流程交付完成。


## 恢复执行、页面遗留修复与未提交视频保护（2026-11-26）

- 正常API建立独立批次9（146/147）、计划3及顺序批次10/11（148/149）；三批均ready/not_started，正式任务0条。新百度任务19使用150、账号19及双封面80/81，attempt45在首页发布入口hover前提交失败，submit_started_at=null；尚无真实公开证据。
- 新包真实走查复现并修复批次列表固定操作栏裁切按钮（Cloud d3ddb1f），采用局部换行；18项批次定向测试PASS。计划详情、列表筛选和资源盘点仍硬编码百家号（Cloud aa1ec14），统一读取真实平台；16项计划定向测试及Desktop前端构建PASS。实际走查时计划批次详情能读回真实账号、成片名和时长；新修复仍需新包最终视觉复验。
- Cloud aa1ec14/Agent1964ca8/Desktop31fd8e1完整重建并挂载，frontend0.1.0+aa1ec14.dirty，日志/tmp/chg130-resumed-environment.log。原密码登录新包成功。正常API读回任务18/attempt44失败且从未进入submit_started后，按原revision重试，未重复建单；新attempt46在浏览器恢复未提交视频时被保护拒绝。日志明确Existing draft分支fill_form:222，submit_started_at仍null，未授权最终POST。
- 两笔preupload观测name_matches/size_matches均false，来自恢复视频过程；不能当作当前145的视频上传证明，也不足以断言首轮44缺失回执的全部根因。保留旧尝试，不删除或覆盖平台恢复的视频。
- 用户再次允许访问BitBrowser；工具层仍曾明确拒绝当前页面，禁止以其他浏览器控制技术绕过。受限页面的真实走查尚未完成；普通源代码、任务API读回、执行日志及无外部平台请求的隔离测试可继续。
- Agent22645f5为恢复视频冲突提供固定、安全、可操作的任务错误消息，仅在能够确认未提交且现场已关闭时使用；未知结果仍走uncertain。任意底层异常文本不出Agent，不泄露URL/凭据。响应读取遇到Playwright关闭异常时保留缺失证明的拒绝行为，不产生异步未处理异常。
- 新增任务结果脱敏及无投稿测试、响应关闭缺失证明测试、真实隔离浏览器保留恢复视频且不上传/不覆盖/不投稿测试。最终scripts/test.sh 976项PASS，B站隔离浏览器10项PASS；日志/tmp/chg130-existing-draft-final-all-tests.log和/tmp/chg130-existing-draft-final-browser-tests.log。隔离浏览器不计为真实平台验收。
- 代码已提交并推送现有Agent PR21；新组合重建日志/tmp/chg130-draft-conflict-environment.log，最终运行结果随后核对。Cloud PR尚无，Agent21/Desktop20/Workspace72未合并；GitHub CLI认证仍待二次验证。CHG维持VERIFYING，不提前归档。

- 最终重建all退出0；Cloud aa1ec14/Agent22645f5/Desktop31fd8e1，frontend0.1.0+aa1ec14.dirty。新包登录operator01后sidecar校验并启动成功（SHA256 bbd217547af9653a47cf4da517777198fd1cbe185c4bf43dc245d9f956283d8d），工作环境UI明确本机服务已连接/比特浏览器已登录指定账号/执行凭证已配置。启动前一次verify因sidecar尚未启动失败；登录后verify的Cloud/Agent/两个Worker/Scheduler通过，在脚本非所属Agent的BitBrowser探测门禁停止，未冒称该命令全绿，改由新包工作环境正式桥读回验证。日志/tmp/chg130-draft-conflict-environment-verify.log。
- 新包最终局部复验：独立批次9的开始发布/继续配置/详情/终止四按钮分两行完整可见；计划列表平台下拉含百家号/B站，选择B站查询保留计划3，详情发布平台现为B站且矩阵一致。未触发批次/计划正式执行，不将局部页面复验计为完整E2E通过。
- Agent22645f5 GitHub verify已completed/success。用户已收到关于窗口51恢复视频是否为可放弃旧测试或需保留稿件的问题，尚未回复；保持原稿，不再次触发投稿。真实平台受理/公开、批次/计划发布、Cloud PR及三运行仓合并和完整最终E2E仍未完成。


## 用户重试故障复核与正常内容流程纠正

- 真实API读回task18最新attempt47、task19最新attempt48均failed且submit_started_at=null。轮转执行日志显示47仍在B站恢复未提交视频分支拒绝，48在百度发布入口video_entry_ready的浏览器求值失败；二者发生于14:48，早于22645f5新包14:58启动。不可称已恢复真实发布，也不以重试替代前置问题处理。
- 用户明确标题、简介按正常发布流程，不使用任意测试文案。本轮通过正式publication/generate逐条重新生成145–150的标题/简介/标签或话题及封面短标题，来源为实际素材标题，随后核对无制作/研发/验收描述、未添加自制授权声明。通过正式cover/render重新渲染双封面，按正常批次configuration及再次确认流程采用到9/10/11；三批读回ready、issues为空，尚未开始执行。
- 任务18/19已有授权和执行历史，正常Edit接口只允许未授权pending任务；本轮不直接改数据库，不篡改历史，也不再沿用其验收文案发起重试。145/150正常新内容及双封面已准备，尚未另建正式任务或发表。原始生成与采用结果在本机私有normal-publication-content.json、normal-prepared-publication-content.json。
- 当前仍未解决的外部条件：窗口51存在归属未核实的恢复视频，相关保留/放弃问题尚未答复；受限浏览器页面不得以其他控制技术绕过。百度真实页面故障及B站上传回执首轮缺失不能仅凭隔离测试宣称修复，真实E2E仍待完成。


## 旧稿提示误拦截的根因修复

- 重新分析本轮已保存的B站官方videoup源码：showEntranceTip渲染“本地浏览器存在…未提交的视频”以及继续编辑/不用了；recovery(true)才从record创建旧视频任务，recovery(false)清除记录。普通上传入口在该提示存在时仍可用，handleChange直接创建新任务。此前仅凭“继续编辑”可见就拒绝属于误拦截；“必须用户先清理旧稿”的既有判断由此纠正，不再作为空白上传入口的前置门禁。
- Agent98a9cc1移除以旧稿提示为依据的全局拒绝，保留当前已加载上传完成视频的保护。空白入口直接上传本次输入，不调用旧稿恢复/丢弃，不放宽UID、视频回执、唯一视频、双封面、固定字段及最终POST屏障。正式工程设计同步说明入口提示和已恢复编辑现场的区别。
- 原“旧稿提示即拒绝”测试改为正常带提示上传及单次提交的受控回归；增加真正载入旧视频时不覆盖的拒绝用例。976项单测、B站隔离浏览器11项全部PASS，日志/tmp/chg130-recovery-banner-unit.log及/tmp/chg130-recovery-banner-browser.log。隔离浏览器不向平台发送请求，不替代真实投稿验收。
- 修复推送现有Agent PR21，安装包重建日志/tmp/chg130-recovery-banner-build.log。尚未以新版本完成真实平台投稿复验，不能把该根因已修复扩大为B站/百度全流程已通过。既有任务18/19继续保留不可变历史，不用旧验收标题重投；待使用已准备正常内容的新流程验证。

- 98a9cc1 GitHub verify已completed/success；新DMG构建及launch-dmg均退出0，已挂载并原密码登录operator01。包内Agent SHA256=2de23246daa4a4e08ebaee3332cdeab3b6d6c573183dcf988cd507c01ef530ed；工作环境UI读回本机服务已连接/比特已登录指定账号/执行凭证已配置。当前运行已切换到误拦截修复包，未使用旧任务验收文案投稿。真实发布复验尚未完成。


## 稳定性复验：启动预检平台错用

- 以真实批次9正常内容执行execution-preview，复现配置ready但两候选均content_incomplete/can_start=false。根因是batch_execution.go及plan_execution.go仍调用固定百家号contentValid，导致B站字段被当作百家号非法输入；既有保存校验使用正确平台，因此出现就绪与启动矛盾。
- Cloud30d5dc0改为使用各批次实际平台contentValidFor，删除无平台的旧包装，避免新调用误用；同步补齐启动时SpaceCoverRender短标题一致性校验。新增真实Service准备任务测试覆盖B站可启动和空间封面过期拒绝；publish Handler/Model/Repository/Service全模块回归PASS。
- 最新Cloud启动后，以同一批次9/revision5及同样候选读回execution-preview：can_start=true，两行ready=true/issues=[]，目标2/可建2/缺口0。未通过削弱规则或跳过检查使其就绪。新组合重建日志/tmp/chg130-stability-platform-environment.log；正式执行及平台结果继续验证，尚未计为通过。

- 新包实际点击批次9开始发布，预检成功后事务返回404“批次或资源不存在/无权限”，读回仍未启动/0任务。正常API同输入复现，Cloud SQL日志定位operations_files id=0的FOR UPDATE；batch_start.go仍直接将PortraitCoverFileID加入锁集合，B站该值为0，且遗漏SpaceCoverFileID。
- Cloud49afaf3复用单条任务已有taskCoverIDs，统一主封面及存在的第二封面锁。发布模块全包PASS；新增隔离MySQL事务回归验证B站锁集合精确为[1,2]并在故意终止后回滚，已实际执行PASS。首次命令因测试工作目录导致migrations路径错误失败，补齐WT_MEDIA_CLOUD_HOME后重跑通过，不掩盖初次失败。没有修改固定运行库的业务状态来使启动成功。
- 新组合完整重建日志/tmp/chg130-stability-cover-environment.log，后续继续同批真实启动验证；此时仍未计为实际投稿成功。

- 新组合Cloud49afaf3/Agent98a9cc1完整重建及原密码登录后，同批次9正常start返回running/revision6，原子创建task20/21，目标2/创建2/缺口0。首次group1仅task20，task21保持pending未授权，实际只有一个Profile时并发5已向下兼容为串行分组。task20/attempt49已由安装包Agent领取preparing。真实投稿结果继续核验，不能计为已公开。

- task20/attempt49已到ready，旧稿提示不再拒绝，实际开始上传；但3笔preupload观测仍name_matches=false/size_matches=false，未获得当前视频匹配回执。尚未确定实际请求差异，不能据此宣称平台上传SDK已兼容。为避免task21重复走相同等待，按正常API暂停batch9并安全取消task20；Cloud读回cancelled/finished、submit_started_at=null，正式Agent结果not_submitted=true/scene_closed=true。此次为明确记录的诊断终止，不计发布成功，不删除失败历史。task21仍pending未执行。
- 回执身份比较改为读取实际request.url而非响应落点，补充请求method、字段存在及响应查询是否一致的脱敏诊断；隔离单测覆盖响应地址无查询但请求正确、其他文件名拒绝，7项定向及11项隔离浏览器PASS。下一次正式执行需先部署该版本并读回真实诊断。


## 百度双入口严格定位故障与上传形状诊断

- 实际task19/attempt48的结构诊断显示#home-statistic-card与.cheetah-popover-inner各有一个可见“发布视频”，原全局get_by_text在后续evaluate触发严格定位错误。Agent159470e改选当前可见展开菜单，兼容唯一入口；没有force点击或随机选first。新增双入口完整填表回归，最终不触发投稿。
- 百度+B站隔离浏览器58项PASS（/tmp/chg130-entry-browser-suite.log）；Agent全量977项PASS（/tmp/chg130-stability-agent-all.log），B站定向7项PASS（/tmp/chg130-upload-shape-unit.log）。这些不计真实平台发布通过。
- 部署49a618a后，正常resume批次9进入task21/attempt50，15:48开始执行，当前running/ready、submit_started_at=null。真实preupload诊断response_query_matches=true，name/size仍不匹配，证明改用request.url并未解决实际回执缺失。159470e补充字段计数、文件/元数据类型及数值字节数诊断，不输出原始文件名、URL或凭据；真实差异仍待新版本核实。
- 新版本只build-dmg（/tmp/chg130-entry-diagnostic-build.log），不为部署打断在途50。task20诊断取消不能计成功；task21及计划3、批次10/11无公开成功，CHG保持VERIFYING。

- 旧百度task19/attempt48正式可信结果为not_submitted/scene_closed=true且从未submit；通过正常abandon保留历史并释放成片150，正常AI内容与双封面93/94新建task22/pending未授权，不复投旧测试标题。
- 原生新包实际读回batch9执行中/第2组、task20已取消、task21执行中/资源核对，任务文案正常且与API一致；Plan3未执行/两批就绪。局部走查不等于最终E2E完成。
- 发现B站_wait把每轮正常_check耗时也延长到deadline，导致真实等待可超过900秒。失败回归证实预算1秒、单次检查2秒时原实现还检查11次；Agent d0fb4b8只扣除真正人工验证等待，回归变为1次即超时，人工120秒仍可从预算排除。9项定向、11项B站隔离浏览器、979项全量单测PASS（/tmp/chg130-wait-budget-*）。新包只构建，等待在途50安全结束后部署。
- 本次wt chg verify已通过Cloud回归及Agent977项，但运行环境verify在Desktop已接管的非脚本Agent BitBrowser门禁退出1（/tmp/chg130-stability-delivery-verify.log），不是全绿；未重启在途任务伪造门禁通过。


## 新包真实复验暴露的菜单挂载竞争

- d0fb4b8新包构建完成后，首次launch-dmg因旧挂载资源忙失败；原应用退出后正常重试挂载成功，无强制覆盖挂载。原密码登录及原生工作环境读回三项正常；包内Agent SHA256=9592d5322866a1425245d905cf836c30c1418d61b7e0f201b5fe4e4d4d591d56。
- task21/attempt50自然结束为failed/completed，submit_started_at=null且not_submitted/scene_closed=true；正常原任务retry进入attempt51，不增加任务数。实际name/size不匹配的一笔声明191033字节，预期视频71987824字节，尚不能说明是主视频响应，不能猜测CID。
- 新正常百度task22/attempt52真实复验仍在video_entry_ready失败，未提交且现场关闭。结构证据显示首页卡片先出现，hover菜单异步挂载；current_entry在菜单出现前把全局同名locator当唯一入口返回，随后变多匹配。e089eb8在首页卡片存在时只等待明确菜单，不提前回退全局；新增延迟挂载回归旧代码确实导航超时，修复通过。首次编写回归误用了仅填字段的helper且断言不存在属性，纠正为完整fill_form后重新跑了失败→成功，未把错误测试当证据。
- Agent全量980项PASS；首次59项隔离浏览器套件有1项封面响应500ms预算超时，f0c3a5b仅把两个正常完整流程用例改为2秒，生产预算未放宽，完整59项重跑PASS（/tmp/chg130-menu-race-browser-final.log）。源码e089eb8/f0c3a5b，当前只build-dmg（/tmp/chg130-menu-race-build.log），未部署，不能说百度已恢复。
- e089eb8还补充preupload所有HTTP状态、是否当前视频，以及200响应的安全数值code/biz_id及URI是否存在诊断；此前只观测HTTP200不足以裁定主视频是否被平台拒绝。增加非200响应不接受CID且不泄露查询值的回归。尚需真实读回。
- 计划批次10/11使用正确row_keys与revision执行正常预检均can_start=true、ready且issues=[]、各目标1/可建1/缺口0。首次省略row_keys请求400属于调用不完整，补齐后通过，不是新服务端缺陷。未启动计划。


## PR与真实入口稳定性继续修复

- GitHub公开API确认Agent PR21 head=f0c3a5b、open且mergeable，CI run45781606151 success；并实际读取Review反馈。封面临时副本和双封面URL绑定旧反馈已有修复；P1可选Playwright导入及P2简介末尾换行在f07b507修复。无Playwright的子进程Cloud bootstrap回归、简介两种段落/空行、保留换行正常提交及删掉原换行拒绝均验证。测试初版未模拟Quill文档而取innerText导致空行翻倍，改为独立的段落文档模型；日志隔离规范要求继承LoggingStateTestCase并调用super.setUp，初次两轮测试规范失败已修。最终982项全量、14项B站浏览器PASS，不掩盖初次失败。
- f0c3a5b真实运行21/attempt53仍在缺少匹配回执后超时，not_submitted/scene_closed=true。HTTP200的两笔无name/size响应均无视频ID，另191033字节请求为frames ZIP，无视频ID；没有看到预期71987824字节主视频证明，不能称已解决或臆测是平台风控。
- 百度22/54在准备后因Passport组件等待人工；用户明确窗口41已登录且正常。通过新包原生“已经处理，继续原尝试”恢复同一54，API读回running/ready，16:42:48真实video_entry_ready完成；随后click超时，结构证据表明悬浮菜单收起。54未提交且现场关闭，不计为真实发布成功，也不把用户账号归为未登录。
- 5f7e73a改优先真实首页视频入口，保留菜单兼容路径并移除成功路径诊断截图；透明、空白Passport组件不进入人工处理，真实持续可见组件继续要求原现场处理，短暂组件给750ms正常稳定。透明/瞬态回归旧代码失败、修复后通过，实际菜单之外的稳定入口仍待新包复验。
- Playwright官方Service Workers文档明确后台请求属于BrowserContext事件：https://playwright.dev/python/docs/service-workers 。本机127.0.0.1真实Worker发起预上传形状请求，Page响应为0、Context为1，Playwright1.58.0验证PASS（/tmp/chg130-worker-real-local-browser.log），没有向平台请求。caa8193增加后台回执读取与去重，仍按本次文件名/大小捕获并在最终POST精确核对CID/文件标识；平台Worker外发投稿同样受最终授权保护，不关闭Worker，不跳过原输入证明。单测拒绝其他文件/其他Worker，非Worker后台也覆盖；这只能证明漏监听能力已补，真实平台根因仍待验证。
- 最新983全量PASS（/tmp/chg130-context-final-all.log）、51项百度浏览器PASS、15项B站浏览器PASS；新组合开始完整all --force-restart（/tmp/chg130-context-entry-environment.log），启动前再次核实无在途任务。未提前计为已部署或真实E2E成功。
- 剩余PR反馈：匿名可播放媒体须关联原CID的实际播放来源，当前实现仅元数据和媒体时长不足，尚未修复，不宣称全部问题清零。
