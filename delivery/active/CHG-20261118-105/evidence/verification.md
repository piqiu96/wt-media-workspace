# Playwright 自动投稿验收

2026-11-18，最新 DMG 内 Sidecar 已对 Cloud 任务 3 / attempt 8 完成正式领取、真实上传填写、提交前许可、一次自动投稿及结果回写。真实稿件号为 `1882178508377049639`，Cloud 为 `reviewing`，现场已关闭。这表示平台已接收，尚未核实公开作品。CHG 保持 `VERIFYING`，M6 保持 `IN_PROGRESS`，等待堆叠 PR Review / 合并及后续 M6-C。

## 版本与安装产物

| 项目 | 验证版本 |
| --- | --- |
| Agent | `89cfa1a1f7c7624a658eb15c6e05aa32562e2f67` |
| Cloud | `55fa6fc8753d26b7554793b7275da5ffaa78d48e`，源码及契约未改 |
| Desktop | `577146e797ec7ae3950ed2cf6f14967f0f3bb5bf`，业务源码未改；重建 Sidecar / DMG |
| Playwright / BitBrowser | 1.58.0 / 130.0.6723.70，连接已有 Profile，不另装 Chromium |
| macOS arm64 Sidecar SHA-256 | `403f5b2ca77dc4a7ce5d65166fe9b8cab722dced3f980215fc7a09710a841aa1` |
| DMG SHA-256 | `89eb17e601dc16985f3cc6a644d418a59ab0793640bb5be326c621d13bbb0445` |

按环境 Skill 从当前源码执行 `python3 scripts/dev/local_env.py up --force-restart`、`build-dmg`，聚合通过后执行 `launch-dmg`，挂载并启动最新“起飞”安装包。Cloud 使用固定本机数据库 `wt_media_cloud`，临时验收配置启用既有百度执行开关，默认配置及提供方契约未变。所属用户通过正常 Desktop 登录和会话接管取得权限；凭据及 Token 只在内存传递，没有重置密码或提交凭据。

## 检查结果

| 检查与复现入口 | 实际结果 |
| --- | --- |
| Workspace `python3 scripts/wt.py chg verify CHG-20261118-105` | PASS、退出 0。Workspace 211 项、Agent 743 项；Cloud / Worker / Compose Scheduler / BitBrowser、本地接口、双开发入口、登录、配置和 DMG 新鲜度通过 |
| Agent `bash scripts/test.sh` | PASS，743 项，含所属用户、会话和 UID 变化、停止、提交屏障、原结果补报、Profile 互斥及架构约束 |
| Agent `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/browser -p 'test_*.py'` | PASS，20 项真实独立 Chrome 测试；全部外网隔离。覆盖导航、上传、封面异步替换和缺失、停止、字段变化、话题确认、重复请求阻断及回执 |
| Agent `bash scripts/build.sh` | PASS，wheel / sdist 构建完成 |
| Agent `python3 scripts/verify/smoke_frozen_sidecar.py --binary <挂载 app 中 Sidecar>` | PASS，实际冻结进程和带鉴权 healthz |
| Agent `PYTHONPATH=src .venv/bin/python scripts/verify/smoke_frozen_browser.py --binary <Sidecar> --endpoint <本次地址> --file <本机视频>` | PASS，包内 368 个驱动文件、版本 1.58.0、真实 BitBrowser 连接、62,988,854 字节本地路径读取，关闭现场已确认 |
| 独立代码审查与 `git diff --check` | 最终发布器及打包增量未发现实质问题，差异检查通过 |

大文件检查使用有效视频和全网络阻断的文件输入页，不等于百家号完成大文件上传处理。此前 64 MiB 有效 MP4 的浏览器完整 SHA-256 与本机一致检查也通过；最终包另用本机既有 60 MiB 成片复验。打包期间发现的 hardened runtime JIT 权限及签名原地改写 Python 动态库问题已修复；保留 hardened runtime，仅增加必要的 allow-jit，在副本上签名并原子替换，保留原映射 inode 和符号链接。回归测试及构建后 venv 启动通过。

## 正式投稿读回

验证器通过正常 Desktop 登录、Agent Token 签发和本地凭据交接接口启动挂载 DMG 内原始 Sidecar，轮询业务结果；浏览器上传与最终点击均由实际发布循环执行，没有替代运行时代码或直接写数据库。

- 任务 3、原成片 130、新 attempt 8、attempt_count 7、revision 31；所属账号与真实 UID / Profile 匹配，提交前再次实读平台身份。
- 视频 13,683,509 字节，SHA-256 `121734561ce9b445236c5cb1f1e3a0428de9cc570c7ee7619ee63fad31816c55`；封面 85,779 字节，SHA-256 `e60608d814bc3940c83888845bc2029dc4f87a96c94cbe10e38be1900131a98c`。下载字节与冻结快照匹配。
- 描述“学会架点了吧宝宝～超简单的！三角洲新手教学 · 已核对”，话题“#三角洲行动 #两端内容核对”，声明“无需声明”，双封面实际上传并读回，未替换确认内容。
- 实际进度为 `preparing(seq1) → ready(seq2) → ready(seq3) → submitting(seq4)`；两次 ready 分别对应资源准备完成和上传前检查。持久化提交阶段并取得新鲜 `allow_submit=true` / `stop_requested=false` 后只点击一次发布；精确处理未匹配话题确认，保留原文，不再次点击发布。
- 唯一匹配的 publish POST 标题与确认内容相同，HTTP 200、`errno=0`，稿件号 **`1882178508377049639`**，平台跳转结果页。未执行公开作品查询、关联或补录。
- Profile 关闭已验证；先持久化原结果再回报 Cloud。结果哈希 `4aea15f26932fa09579a671d21ee5840eda16611b6d8cd862ead923858d28c8e` 与本机 packet 一致，`report_pending=false`、本机阶段 `settled`。Cloud 为 `reviewing`，不重新领取或重放点击。
- 全部历史尝试的原 `result_hash` / `evidence` 未变；未使用此前独立适配投稿的回执。

[脱敏读回](readback.json)保存版本、资源摘要、任务、回执和检查结论。会话、Cookie、Token、CDP、授权下载地址、完整平台响应及运营截图只留本机，不进仓。

## 旧现场处置与修复

用户明确确认原视频未正常发布。沿用 CHG-104 正式核实入口，在核对原账号、原记录、未提交现场与安全关闭后，将 attempt 4 记录为未发布，再单独确认重试；保留原 packet/hash，不以无同名作品或空草稿单独作为失败依据。

| 尝试 | 结果与对应修复 |
| --- | --- |
| 5 | 首页视频入口藏在折叠菜单，上传前中止；增加悬停 `#home-publish-btn` 和停止检查 |
| 6 | 竖版预览缺失时陷入 Locator 隐式等待，填写阶段中止；改为非阻塞查询，由总预算轮询并检查停止 |
| 7 | 旧缩略图暂时仍已解码，被过早记录；最终字段复核中止。实测第一张记录 URL 与最终预览不同；改为在对应封面槽位等待新 URL 的已解码图片 |
| 8 | 最终安装包完成正式自动投稿和结果回写 |

尝试 5～7 均未进入 `submitting`、`submit_started_at` 为空、未点击发布；每次结合实际中止原因和现场，通过正式核实入口记录失败，再确认新增尝试，原结果不变。新增关键用例先失败再修复；“旧图不变”仍拒绝继续，最终一致性检查未放宽。

平台返回首页仍恢复失败的临时编辑缓存。仅对已核实未提交、与本任务文案和文件相符的唯一缓存做本机备份、定点移除，再确认新建页为空、Cloud 任务不变及现场关闭。未清空登录、其他缓存或作品。这是验收现场处置，运行时仍拒绝恢复旧编辑器，不宣称实现了 M6-C 人工继续或自动续编。

另一次用户直接授权的适配投稿使用不同成片 128，稿件号 `1882173445914373676`；后续平台列表显示已发布、仅主页可见。它不属于 Cloud 正式任务链路，未回填任务 3，不替代 attempt 8 的回执，也不构成公开作品闭环验收。

## 页面、限制与交付

Cloud 和 Desktop 开发入口实际打开任务详情，均显示“平台审核中”和“平台已接收，正在审核；尚未确认为公开作品”，无重试入口，页面错误 0、无横向溢出，截图已检查。继承既有原型及公共组件，无新增 UI。本轮未重新验收原生 Desktop 视觉登录流程；已验证最新安装产物中的完整 Sidecar 发布循环。

Windows / Intel Mac、超过 50 MiB 的平台实际上传处理、公开作品链接和关联未验证。M6-C 与生产开放未完成，M6 不标记 DONE。

交付为 [Agent #12](https://github.com/piqiu96/wt-media-agent/pull/12)、[Workspace #56](https://github.com/piqiu96/wt-media-workspace/pull/56)，均以 `codex/CHG-20261118-104` 为 base。按用户临时授权串行实施，不自动合并；先 Review / 合并 CHG-101～104 前置链，再处理本 CHG。既有 main-only workflow 不触发堆叠 base，上述为本地检查，不宣称远端 CI 通过。


## 2026-11-19 Review 后的平台能力职责重整

当前实现：Agent `5172dca0e2ff57adadf0ff3c8aa1f1c2fc43507d`。修改前重新 fetch 两仓 main；Agent `b8c2b259ec06e68eaac304bad753acf131fce598`、Workspace `afc76c498e3caa1715b4935febc27b7c0e776f31` 均已包含于现有 CHG-105 分支，无须再次合入。不新建 CHG，不合并任何 PR，保留其他任务未提交走查记录。

### 最终结构和执行边界

- `platforms/publish.py` 提供 Publisher、不可变载荷、回执和必填执行控制；`platforms/baidu/publisher.py` 同文件包含 BaiduPublisher 与 BrowserPublisher。公共接口不含 Page/Token/Cloud 任务或 SQLite；一期 method 默认并显式 browser，非法方式在发布动作前拒绝。没有 workflow、API 投稿占位、浏览器子目录或用户选择字段。
- BrowserSession 原样迁至 `services/browser/session.py`。基础身份 API 保留 clients；身份组合与浏览器发布归平台能力。原下载逻辑迁到文件校验服务，通过现有基础下载客户端读字节，不增加网络或投稿重试。`image_upload_file` 的函数内容逐字比对保持一致，不改原图片字节、不新增尺寸或解码校验。
- 初次实读 UID 通过后回调协调器落盘 prepared 并报告 ready，原有两个 ready 报告及序号次序保留。上传后再次核对 UID，提交前回调先落盘阶段、取得 Cloud 新鲜许可及记录 click_started；再次检查停止后只提交一次。释放 Playwright 连接后，协调器独立核实 Profile 关闭，再保存和补报原结果。
- 同时包含前轮恢复修复 `38961c5` 与公共常量整改 `3f9033a`；缺失结果和人工处置早于补报的本地解除逻辑、已有 packet/hash、未投递历史标记与旧尝试屏障保持。详见 [CHG-102 补充证据](../../CHG-20261118-102/evidence/verification.md#2026-11-19-异常退出后的人工处置衔接)。它们属于当前后续分支，不是 PR #9/CHG-104 独立差异。

### 本轮实际验证

| 检查 | 结果 |
| --- | --- |
| 先复现后实现 | 独立发布入口首先因缺失 platforms 模块失败，落地后 9 项入口控制测试通过；新平台边界扫描先因缺失规则失败，随后正反例通过 |
| Agent 标准回归 | PASS：`PYTHONDONTWRITEBYTECODE=1 bash scripts/test.sh`，766 项，基于前轮 750 项增加 16 项；原存储故障、停止、身份变化、许可丢失及补报断言保留 |
| 隔离浏览器 | PASS：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/browser`，20 项；临时 Chrome Profile，外部请求由 fixture 拦截；不是实际平台发布证据 |
| 独立审查 | 无待修问题；独立复验公开入口、协调器、准备、下载及依赖检查共 80 项通过 |
| wheel / sdist | PASS：离线 uv build，两种归档都包含新平台模块、公共会话和文件校验服务，旧客户端发布模块已移除 |
| 原生 Sidecar | PASS：macOS arm64 PyInstaller 构建、固定本地 API 路由比对、带鉴权 healthz；包内 Playwright 1.58.0 驱动 368 个文件可运行 |
| 冻结包大文件探针 | PASS：隔离且禁止外网的 Chrome 页面读取 62,914,560 字节本地测试文件，`platform_submit=false` |
| 文档与治理 | PASS：docs/check.py、verify_delivery_governance.py、verify_product_master_alignment.py、Agent/共享目录规则生成同步、差异检查 |
| Workspace 全套 | 执行 211 项，26 项失败，与本轮之前记录一致：现有未提交 Milestone 引用未复制到测试副本的 CHG101 `app-walkthrough-fixes.md`；Cloud 本地提供方 2026.11.19.2 与主线 map 2026.11.19.1 不一致。没有修改该走查记录、提供方或降低断言，不将整体记为通过 |

本轮临时 Sidecar SHA256：`8d509f9ce4587145f62334e2a27550fea35b6930442c8b38757ea23ed0d61465`。构建和日志位于执行机临时目录，不提交可执行文件、凭据、签名下载地址或原始平台响应。

本轮没有重建/安装 DMG，没有真实账号或平台写操作，也没有验证 API 投稿。此前 DMG 与稿件证据仍只对应原提交，不用其替代本轮重构后的真实平台验收。交付使用现有 [Agent #12](https://github.com/piqiu96/wt-media-agent/pull/12) 和 [Workspace #56](https://github.com/piqiu96/wt-media-workspace/pull/56)，先 Review CHG-104 再 Review 当前 CHG-105；状态保持 VERIFYING，更新后再次交用户 Review，禁止自动合并。


## 2026-11-19 用户批准合并

用户明确回复“同意pr通过并且合入”，解除上一轮对 Agent #12 / Workspace #56 的暂不合并要求。本次仅合并上述两个已 Review 的 PR，使用 merge commit，目标保持现有 `codex/CHG-20261118-104`。CHG-102～104 前置 PR 仍单独待 Review，不将本次授权扩大为整链 main 合并。GitHub PR 的 MERGED 状态及 merge commit 为实际合入凭据。

CHG 保持 VERIFYING，M6 保持 IN_PROGRESS；前置链集成、重构后的完整安装包/真实发布以及公开作品验收限制均继续保留。其他 CHG101/UI 未提交文件不纳入提交。
