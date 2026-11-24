# CHG108 实现与独立审查

2026-11-25。本文件记录实现阶段验证；不是实际平台或安装版验收结论。

## 固定输入与契约

- 原型输入：Cloud `web/example/proto/publishing-design` 与 `common`，108 固定提交 `2512d342cc8f81247861347b74aaeadf2091f92a`，预览 `?review=chg108`，逐页映射在原型 README。根已核对启动范围、单 Profile、公开统计与稳定启动弹窗截图。
- 初版Cloud API、Cloud-Agent、发布错误修订 `2026.11.25.2`；Agent 最低新工作版本同修订，Local API 保持 `2026.11.25.1`。消费方 Agent 与 Desktop `ca44cba`、Workspace contract-map 同步。
- 提供方契约独立审查曾发现原键丢响应恢复、明确停车反馈与关闭证据问题，修订至 `0a8eab7` 后关闭。协调升级依据 ADR-0037，旧检查代次不能作为关闭证明。

## Cloud 与共用 Vue

- Go 实现 `7b4f523`。实现方执行 `go test ./... -count=1` 通过；执行 `WT_MEDIA_TEST_LIVE_DB=1 WT_MEDIA_CLOUD_HOME="$PWD" go test ./internal/modules/publish/repository ./internal/modules/image/repository -count=1` 通过，分别约 69.9/43.5 秒。该 MySQL 测试采用隔离 fixture，不代表真实 BitBrowser 或平台。
- 覆盖原子 start 回滚/原键重放、固定组重启、5 自动/10 窗口、可靠停车后独立环境继续、实际 Profile 双向互斥、旧检查切换、原键取消围栏与结算、停止/提交竞争和异常范围确认。
- 独立 Go 源码审查覆盖基线 `60847fd..7b4f523` 的 Go/contracts/migrations/config，未发现可确认 P1/P2；审查者未实现这些代码，未另跑 Go 测试。
- Vue 执行实现 `89f49b6`：164 文件、1,212 测试及 Cloud/Desktop 构建通过。受控 Chromium 验证两标签竞争、原键跨重启、加载中离开、修订变化、慢 GET 收尾和失联后正式占用拒绝可重新预览。
- 前端独立首审及有限复审关闭版本/导航启动意图、未知回执保留、跨标签条件清除、stopping 轮询及结构化业务拒绝。浏览器 fixture 不是正式平台发布证据。

## Agent

- 有界原线程执行和跨 owner 窗口计数 `b79f539`；配置与装配 `f6a8500`；最终修复提交 `0d507e1`。
- 首审 3 P1/5 P2 及限定跟进均已分修：跨 scope 原子 Profile 保护、active 原键 Strict 复核、跨 owner 自动容量、无窗口原包补报、观察 ACK hash、预检后开窗屏障、HTTP read1 慢流截止、人工继续回执只限原现场。
- 后续限定复审也覆盖真实 current 与禁止新开窗的分离、发布自动容量和核验窗口分离、首次明确拒绝归还名额/既有未知仍保留。独立审查者使用实际 Job/Gate/Loop、临时 SQLite 和受控 BitBrowser/Cloud 复现及复验，`0d507e1` 无剩余阻断。
- 根执行 `bash scripts/test.sh`，`091b333` 全套 948 项通过。最终 `0d507e1` 再执行完整 `bash scripts/test.sh`：949 项通过，日志 `/tmp/chg108-agent-final-0d507e1.log`。
- 最后定向：轮询 18、核验 37、装配 19、下载 8、传输 Source 24、消费准入 8 通过。慢流采用实际 HTTPResponse/socketpair，跨 owner 自动容量采用实际 SQLite 和仍阻塞的旧线程；不访问外部平台。

## Desktop 与交付状态

- 根执行 `bash scripts/test.sh`，Rust、Shell、打包环境/版本及 Windows subsystem 静态检查通过。仅协议锁变化，无新原生桥载荷。
- 四仓 PR51/19/18/64已创建；实际旧核验安全切换、新DMG及正式跨仓检查已通过，真实单Profile已公开并关联work5。最终fe741fe重包及双端公开结果读回已通过，当前待最终PR/CI和合入。Windows、其他平台和真实多Profile未由上述测试证明。

- 真实安装版浮层在发布运行时误称“当前无任务”，已窄修 `7ba7844`：只依据传输ID缺失报告“已连接”，保留上报的任务信息。根复核两文件差异，23项定向及双构建通过，重建安装版后再读回。

## 正式全流程检查

在Cloud7ba7844/Agent0d507e1/Desktopca44cba的DMG完成后，执行 `WT_MEDIA_LOGIN_USER=operator01 WT_MEDIA_LOGIN_PASSWORD=<会话提供> python3 scripts/wt.py chg verify CHG-20261124-108`，退出0。日志 `/tmp/chg108-chg-verify-final.log`：Workspace215、Agent949、Desktop560通过/6既有ignore、各仓脚本、环境/DMG/CORS/登录及契约映射通过。此前与DMG重建同时运行的一轮因构建中移除旧DMG报“no dmg”，已在产物稳定后完整重跑；没有跳过失败门禁。


## 验收边界补测

根对照V清单委派补齐此前未单独定位的V05/V08/V10断言。Cloud测试提交8ca5926只新增隔离MySQL测试，四项主测试/六个子场景通过（4.944秒，日志/tmp/chg108-batch-acceptance-final.log）：混合异常按task去重并排除reviewing；paused/stopping/cancelled/ended阻止单任务start/retry；human/uncertain不能finish；准确失败集合结束后仍保留占用且不能retry。根复核新测试diff与通过日志，未发现运行代码缺陷。

真实公开：task12 / attempt35 / output134 → work5，platform_work_id=11733113375672752567；唯一关联作品数1，原attempt保留completed/reviewing投稿事实，由后续公开observation更新task为published。不将历史attempt结果篡改成新的投稿。公开UI刷新问题另由真实走查发现并修复，未用DB改状态绕过。


## PR51自动审查追加

自动审查提出启动恢复不能只凭row_keys、100旧候选阻塞后批两项P2。原回执验证前端b1db714与Provider a02904c已实现；批次候选d466699/b53ff85覆盖100无eligible与100忙Profile旧批。限定复审又发现实际queued下游仍有上限及cancelled时序的普通409误清，已分别修复并独立复审关闭。Provider当前公开Batch API .3，Cloud-Agent与错误码仍.2；Workspace映射已同步。最终前端1220项、完整Go回归、真实HTTP与新包读回均通过。

3fc7f6a完整重建中的DMG verify曾遇macOS临时资源不可用；具体失败临时镜像仍挂载，根按精确image-path匹配仅卸载本次临时disk24。未跳过校验或使用失败产物；后续fe741fe已重新完整all通过。


## 最终修复与验证收口

- PR51原启动回执由原key及完全原包验证；持久化回执8个必需字段/非null/类型校验后才能签发权威false。25个持久化变体及实际HTTP另key409通过；没有暴露winning key/digest。
- 组及实际queued分别keyset翻页，100无eligible/忙Profile/旧单任务混排和205容量边界通过；全局自动/窗口满早停并仍优先原key。
- a5cce77序列化保留批次无操作[]；7649e48浏览器负例覆盖暂停/结束失败不显示重试或放弃，独立任务缺字段兼容不变。
- fe741fe公开核验按(next_check_at,id)翻页越过20失效候选，15项隔离MySQL主测试通过，保留原key/24h/Profile严格复核及窗口满早停。四条GitHub已知thread均经独立限定审查后resolved。
- 最终Cloud完整Go回归、前端164文件1220项、双构建及Chromium通过；Agent949和Desktop560/6ignore未改变。Workspace最终220通过(/tmp/chg108-workspace-final-220.log)。
- 最终fe741fe完整环境和DMG来源核对通过(/tmp/chg108-final-fe741fe-bringup.log)，真实Web/安装版均读回1/60·1.67%、待公开0、原task12/work5；全部验收范围见acceptance-matrix.md与installed-e2e.json。CI/合入单独记录，不等同用户整体验收。

最终交付记录独立只读复核发现两处旧门槛用语，已统一VERIFYING及用户最后整体验收安排，并将M7的实际单Profile向下兼容与多Profile受控验证明确分列；未修改产品多账号能力。
