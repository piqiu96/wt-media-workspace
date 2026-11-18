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
