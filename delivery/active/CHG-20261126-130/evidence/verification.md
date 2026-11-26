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
