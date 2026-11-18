# Playwright 发布器与执行接入验证

2026-11-18，CHG-105 相对 `codex/CHG-20261118-104` 的增量。实现 Python Playwright `BrowserSession`、`Publisher` 协议、`BaiduPublisher` 和 Local/Sidecar 串行执行；没有修改 Cloud、Desktop 业务源码、Contract 或数据库。真实投稿验收尚未通过，CHG 为 `VERIFYING`，M6 为 `IN_PROGRESS`。

验证的 Agent 代码提交：`bf8735f7ee4a36d84df5f4dd018945bd54944563`；Cloud `55fa6fc8753d26b7554793b7275da5ffaa78d48e`、Desktop `577146e797ec7ae3950ed2cf6f14967f0f3bb5bf` 均保持 CHG-104。安装包在上述 Agent 源码修改完成后重建，未将旧包作为本轮产物。

## 自动检查

| 检查与复现入口 | 预期及实际结果 |
| --- | --- |
| Workspace `python3 scripts/wt.py chg verify CHG-20261118-105` | PASS，退出 0；Workspace 211 项、Agent 739 项，本地服务、开发入口、登录、DMG 新鲜度及配置检查通过。不是全仓 Cloud/桌面 Rust 重测或真实投稿验收 |
| Agent `bash scripts/test.sh`（聚合入口调用） | PASS 739 项，包含 33 项架构约束；保留网络隔离、SQLite、防重及子进程恢复检查 |
| Agent `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/browser -p 'test_*.py'` | PASS 7 项，实际独立 Chrome 页面；正文、声明、两个封面、停止/被改写内容拒绝、上传未完成拒绝、图片解码失败、一次最终请求及精确回执解析。全部外网请求被拦截，回执为测试夹具，不能证明百家号投稿成功 |
| Agent `bash scripts/build.sh` | PASS，wheel 和 sdist 构建完成；Local extra 固定 Playwright 1.58.0，不安装另一套 Chromium |
| Workspace `python3 scripts/dev/local_env.py up --force-restart` | PASS，重建并启动当前本地 Cloud、Agent、Worker、调度及共用开发前端；测试未使无 Token 的 Agent 领取任务 |
| Workspace `python3 scripts/dev/local_env.py build-dmg` | PASS，重建 macOS arm64 DMG，内含当前 Sidecar；Windows、Intel Mac 和安装后完整发布流程未验证 |
| Agent `.venv/bin/python scripts/verify/smoke_frozen_sidecar.py --binary <实际 app 内 Sidecar>` | PASS，冻结进程启动及带鉴权 healthz 通过 |
| Agent `PYTHONPATH=src .venv/bin/python scripts/verify/smoke_frozen_browser.py --binary <实际 app 内 Sidecar>` | PASS，从安装产物提取的 368 个驱动文件可直接启动，版本为 Playwright 1.58.0；不依赖开发机 Node |

首次包含包内驱动的检查失败：Node 在 hardened runtime 下不能分配 JIT 代码内存。复现后，仅增加 `com.apple.security.cs.allow-jit` 签名权限，保留 hardened runtime；精确签名参数及权限测试先失败、修复后通过，重新构建的同一探针通过。没有增加调试、跳过库校验等权限。

一次标准测试与 PyInstaller 重签名构建同时运行时，7 项子进程检查遭 SIGKILL；没有降低断言。构建结束后串行运行上述正式聚合，739 项全部通过。最终结果不使用那次失败日志冒充通过。

## 大文件与包内驱动

实际 BitBrowser 130.0.6723.70，使用启动返回的本机 CDP 地址及 `is_local=True`。测试生成有效 H.264 MP4，再追加合法 MP4 `free` box 至 67,108,864 字节；`ffprobe` 读回 1 秒视频。只在独立、全网络拦截的文件输入页选择文件，浏览器读取的完整文件 SHA-256 与本机一致。没有把文件上传百家号，也没有压缩至 50 MiB 以下替代此项检查。

随后使用实际 app 内提取的 Playwright 驱动，连接同一 BitBrowser，在独立隔离页读取相同大小文件，通过：`bundled_browser_connection=true`、`file_bytes=67108864`、`platform_submit=false`。复现命令为 Agent `PYTHONPATH=src .venv/bin/python scripts/verify/smoke_frozen_browser.py --binary <实际 app 内 Sidecar> --endpoint <本次启动返回地址> --file <有效大于 50 MiB 的测试视频>`。该检查只证明包内驱动、连接和路径传文件，不等于冻结 Python 发布循环、平台转码或最终投稿验收通过。

## 实际页面和原任务

用户完成百家号安全验证后，实读账号 UID 与任务快照一致；逐页核对全部 103 篇稿件，没有对应标题，草稿 0 篇。平台列表实际响应为 `errno=0`，未使用首屏加载中的空列表作依据。但是重新打开视频编辑器后，仍恢复上次上传的视频及部分文字；页面未提供已经核实可安全放弃的操作。因此不能将原任务判为失败、释放占用或重新入队，也未删除浏览器缓存来绕过核实。

Cloud 任务 3 当前 attempt 4、status `uncertain`、revision 15、attempt_count 3。本轮未执行核实结论写入、安全重试、再次上传或最终提交；不以无同名作品、空草稿或测试回执证明未发布。

Cloud 和 Desktop 开发入口分别运行现有 `web/scripts/test-publication-recovery-browser.mjs`：实际打开任务详情、核实弹窗，取消后任务不变，缺少依据不能保存，原结果保留；页面错误 0、无横向溢出。[脱敏读回](readback.json)。沿用 Cloud `web/example/proto/publishing-design/PublishingTaskPage.vue`、`TaskDetail.vue`、`TaskActionDialog.vue` 和公共组件，没有另行设计页面。该项是浏览器开发入口走查，不是原生安装包视觉验收。

复现页面检查时，使用当前启动输出提供 `WT_MEDIA_BROWSER_BASE_URL`、本机授权会话 `WT_MEDIA_BROWSER_STATE`、输出目录 `WT_MEDIA_BROWSER_EVIDENCE` 及 `WT_MEDIA_BROWSER_TASK_ID=3`；不设置 resolve/retry 写入选项。账号主页、Cookie、Token、CDP 地址、完整响应和原始运营截图只留本机，不进证据库。

## 未通过的验收与 Review 顺序

- 未验证真实空白编辑器完整填写、平台实际视频处理完成、最终自动提交和本次可信稿件回执。旧编辑现场未安全处置前不执行新尝试；人工继续、公开作品核实与补录属于后续 M6-C。
- 未验证超过 50 MiB 文件在百家号完成上传和处理，也未验证安装包内完整发布流程；上述本机文件与驱动检查不能替代它们。
- CHG-101～104 前置 PR 链先合并；随后 [Agent #12](https://github.com/piqiu96/wt-media-agent/pull/12) → Workspace CHG-105。各自以 `codex/CHG-20261118-104` 为 base，保留独立差异，不自动合并。
- 当前堆叠 base 不触发既有 main-only workflow；以上为实际本地验证，不宣称远端 CI 通过。


## 本轮 46 号窗口适配增量

Agent 本地提交 `856dbdffad35a1570622e373d49565817ac3ed10`，在原 CHG-105 分支上修正现有 Playwright 发布器；没有推送、合并、重建安装包或更改 Cloud 任务状态。

真实页面观察：新建发布页面仍恢复旧视频和文案。封面弹窗在上传控件之外同时产生多张视频抽帧 blob 缩略图。原判定扫描弹窗全部图片，会把这些缩略图误认为本地封面已成功解码。现在只读取本次文件输入控件中的新图片，要求 blob 地址、解码完成及非零自然宽度。视频上传状态限定到实际 `#cover-tabs-container`，提交前再次确认；正文及预览中的百分比和“上传中”文字不再被当作上传进度。

| 检查 | 本轮实际结果 |
| --- | --- |
| Agent `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/browser -p 'test_*.py'` | PASS，11 项。新增封面解码失败但出现视频缩略图、填写后重新上传阻止最终点击、恢复现场不得再上传，以及包含“上传中”和“25%”的正常文案仍可完成一次模拟提交与匹配回执 |
| Agent `bash scripts/test.sh` | PASS，739 项；最终状态区域修正后再次执行，29.593 秒、退出 0 |
| Agent / Workspace `git diff --check` | PASS |
| Workspace `python3 scripts/verify/verify_delivery_governance.py`、`python3 scripts/verify/verify_product_master_alignment.py` | PASS，Active 集合及产品/主计划一致；本轮未运行全套环境、契约和包体验收 |
| 独立代码审查 | 首次发现整页进度检查会误认正常文案，补测试实际复现失败后修正；最终只读复核未发现新增实质缺陷 |
| 46 号真实页面控件探测 | PASS，视频上传区域唯一；选取本机既有 1200×900 PNG 后，目标上传控件出现新的 blob 图片、解码完成、自然尺寸 1200×900。未把其它视频缩略图作为依据；取消封面弹窗并关闭探测页，原编辑页文案保持不变 |

新增封面误判与重新上传用例均先在未修复生产代码上观察到失败。恢复现场用例首次因夹具初始化早于脚本定义而失败，修正为页面脚本加载后恢复现场；该用例验证已有保护，不算新增生产缺陷。审查发现的正文误判另行先复现错误，再修正并取得上述最终 11 项 PASS。

本轮未上传新视频、未完整填写新的真实投稿、未最终提交，也没有本次平台稿件回执。旧任务 3 / attempt 4 的 uncertain 事实和既有回执均未改动，仍需核实旧现场。保留 CHG `VERIFYING` 和 M6 `IN_PROGRESS`；模拟提交及本机封面解码不替代真实投稿验收。未重新验证更新后的冻结 Sidecar / DMG。


## 用户确认后的一次真实投稿

用户随后明确确认“没有成功，确实一直停留在旧的未正常发布的作品上”，并已授权从成片任取视频、按素材填写及发布。此次通过 46 号平台界面的“更换”控件上传不同于旧任务 3 的本机标准成片，旧重复编辑页已关闭；未点击旧视频的最终提交，也未对任务 3 执行核实写入、重试或补录。

最终素材文件为 `火影忍者-128-三角洲本地选段 · 五段合成验收 · 标准成片.mp4`，11,119,320 字节，1280×720、49.166 秒，本机 SHA-256 `2108ec50d268aceacbeb57e42cf7ea5fba4c3557158add79d950f6001533f0ce`。平台投稿响应中的 videoName 与该文件一致。文案为“手游段位名场面，五段精彩片段一次看！ #手游 #游戏精彩时刻”，声明“无需声明”；双封面使用该视频本机提取的既有画面，未生成或杜撰封面。

真实新视频先渲染两个 `select-cover` 控件而非 `cover-preview`，原代码会一直等候已有封面。补充空封面用例先观察失败，再允许两种控件并沿用最终图片读回。首次填写过程中竖版预览未就绪，校验失败且未点击发布；平台处理完成后，重新校验同一条未提交新视频的字段及两个封面，成功进入提交阶段。没有重放最终点击。

真实调用当前 Agent `BaiduPublisher.fill_fields` 完成描述、声明及两个本地封面，`submit` 只点击一次发布。平台在发出投稿请求前出现“作品描述中存在未匹配的话题/@内容”确认框；当时 request_count=0，未假定已接收或再次点击发布。随后用 Playwright 点击该原确认框的“不处理”保留原文，并只允许一个 publish POST；调用生产 `accepted_receipt` 验证请求标题、HTTP 状态、errno 与稿件 ID。响应 `errno=0`、`article_id=1882173445914373676`；平台跳转结果页，显示“提交成功，正在审核中”。未宣称已公开。

确认动作随后补入 `BaiduPublisher.submit`：只匹配精确提示，重新验证描述、声明、封面、上传与停止状态，仅允许这一个可见确认框，继续原点击。模拟真实确认及正文被改两项用例均先失败、修复后通过。为避免重复投稿，没有用第二条真实稿件重跑修改后的完整 `submit`；相同真实控件动作已在上述一次投稿中分段验证。

最终 Agent 提交 `da35caf90f49db9d474195065e9f0e67cbf10090`（前序修复为 `856dbdf`）。Agent 标准检查 739 项 PASS（30.236 秒），隔离浏览器 14 项 PASS（13.914 秒），独立静态复核未发现新增实质问题，`git diff --check` PASS。本轮没有重建冻结 Sidecar 或 DMG。

本次直接使用当前 Agent 源码验证平台适配器，**没有**从 Cloud 正式领取新任务、取得 Cloud 提交前许可或回写正式业务状态；本地只保存一次操作的证据，不创建第二套任务状态。故这次真实回执不能冒充旧任务 3 的成功或 M6 单任务闭环验收。CHG 仍 `VERIFYING`，M6 仍 `IN_PROGRESS`。原始页面、完整平台响应及凭据仅留本机，仓内只保存以下脱敏读回。


最后一次只读检查：点击结果页“查看发布状态”，等待作品管理页实际加载并定位本次完整标题。列表从原 103 篇变为 104 篇，本次标题对应行显示 `2026-11-18 13:41:37`、“已发布”，并有“作品仅主页可见，查看详情”提示。已保存本机截图 `wt46-publication-status.png`。此为平台列表读回；没有把主页可见冒充全量推荐，也未执行 M6-C 的公开作品核实、Cloud 关联或补录。
