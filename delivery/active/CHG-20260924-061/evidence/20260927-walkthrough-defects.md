# 走查三缺陷：修复读数（2026-09-27）

本文件记录用户走查报的三件事（原文：①有些点击下载是灰色，有些点了要绑定、不知道去哪里绑定；②已下载的，改完保存路径后就找不到文件了；③已取消的无法再次点击下载）逐条落到机制后的**修复前读数**与**修复后对照**。

- 判据一律「命令／手动动作 → 期望 → 实际 → PASS/FAIL」，未执行的一律写「未跑」并说明原因，不写成通过。
- 迁移与查找相关的读数以 `<旧目录>`／`<新目录>` 占位；本文件不含凭据、Cookie、签名 URL、本机用户名与绝对路径。
- 修复前读数取自 2026-09-27 走查环境（本 CHG 的构建）；修复后读数取自 2026-09-27 18:19 重建的同一套环境（五个进程都换到修复提交上：Cloud `1503d81`、Desktop `9b85bf2`）。

## 1. 缺陷一：点击下载

### 1a 节点心跳窗口把点击挡在服务端

| 项 | 内容 |
| --- | --- |
| 命令／动作 | 在页面上对任一素材点「下载到本机」（节点已绑定，但距上次上报已超过窗口） |
| 期望 | `202`，并产生云端准备任务 ＋ 依赖它的本机任务 |
| 修复前实际 | 用户走查时得到「本机没有可用的下载节点」提示（`15105`）。同刻 MySQL 读数：节点 `status=online`、`bitbrowser_status=normal`、`reported_main_user_id` 与 `users.bit_main_user_id` 一致、会话未失效，**唯一不满足的条件是 `last_heartbeat_at` 落后 935 秒**（窗口 90 秒）；而 `WithFreshness` 全仓无调用者，写这个心跳的唯一入口是 Desktop 的绑定／刷新按钮（Agent 侧 `report_runtime` 全仓无调用者）。**那次点击是运营浏览器里的动作，其 HTTP 应答本身未被我留证**——判据是「用户看到的提示」＋上列五行读数。 |
| 修复后实际 | **未跑**：需要一次「窗口已过期时点击」。当前节点注册于 18:19:49，改动后的第一次点击发生在 18:20:09（落后 20 秒），**该次点击不能判别**——窗口内的点击在改前也会成功。节点现在已落后数小时，任何一次点击即是判别读数。 |
| PASS/FAIL | **未跑**（测试级证据见下） |

测试级证据（`cb89664`，Cloud 仓）：`FindFreshLocalNode` → `FindTrustedLocalNode`，同一条件集去掉心跳一条。新增 `TestResolveTrustedLocalNodePicksTheNewestBoundDeviceDespiteStaleHeartbeats`（陈旧心跳仍被选中）、`TestResolveTrustedLocalNodeReportsNoBoundNode`、`TestFindTrustedLocalNodeReportsAbsenceForAUserWithNoBoundDevice`、`TestTheHeartbeatWindowSeparatesQueueingFromTrustChecks`（窗口常量仍在、只不再被这条路径使用）。

### 1b 「未准备」的行按钮是灰的（Q-05）

| 项 | 内容 |
| --- | --- |
| 命令／动作 | 对一个 `not_downloaded` 的素材点「下载到本机」（素材 34） |
| 期望 | 服务端 `202`，素材进入准备流转，随后落盘 |
| 修复前实际 | 按钮 `:disabled`：`canDownload` 只放行 `ready`（`labels.js`），四个调用点全部门控——**页面上没有任何入口能对未准备的素材发起下载**，而服务端自 `7c83969` 起是接受 `not_downloaded` 的。 |
| 修复后实际 | `18:20:09.031` `POST /api/v1/materials/34/downloads` → **`202`**；`18:20:09` 建云端 `compose_input_prepare`（`transfer_7e604df5…`）＋依赖它的本机 `user_download`（`transfer_2e39b7a3…`，`execution_scope=local_agent`，`dependency_task_id` 指向前者）；云端准备 `18:21:11.229` `success`，本机下载 `18:21:29.029` `success`；素材 34 投影 `not_downloaded` →(`18:20:09`)→ `18:21:11.224` **`ready`**；文件 `344,809,521` 字节落 `<新目录>`（`18:21`）。 |
| PASS/FAIL | **PASS**（这次点击本身就证明按钮可点：改前的同一行是灰的） |

边界读数：本机 `user_download` 任务里 `file_name` 由执行器回报（成功 7 条全有名字），因此下载中心与迁移候选名单都拿得到名字。`failed` 行是否可点、`failed` 按钮文案（`68a32b2`）由 Web 测试钉住，**页面上的观察未跑**。

### 1c 提示指向不明

| 项 | 内容 |
| --- | --- |
| 命令／动作 | 在无可用节点的情形下点下载，读提示 |
| 期望 | 提示点名要去的地方（本地环境 → Agent 状态） |
| 修复后实际 | `68a32b2`：`local_transfer_node_unavailable` 改指该页；`material_unavailable` 的文案由「云端正在准备」改为「没有可用的来源地址」——**改前那句是假承诺**（Cloud 只在 `source_url` 为空时抛它）。两条各有测试（`names the page that fixes a missing local node`／`does not promise a preparation for a material with no source address`）。 |
| PASS/FAIL | **未跑**（文案只在页面上可见；测试级 PASS） |

## 2. 缺陷二：改了保存位置之后

### 2a 新目录没有推给 Agent

| 项 | 内容 |
| --- | --- |
| 命令／动作 | 读 Agent 本地 store 的 `download.save_directory`，与 Desktop 的 `settings.toml` 对照 |
| 期望 | 两者一致，且下一次下载落在新目录 |
| 修复前实际 | Agent store ＝ `<旧目录>`，而 Desktop 的 `save_dir` ＝ `<新目录>`；`local_push_save_directory` 在 Rust 侧存在并已注册，但 `web/src` 的 **149** 个已跟踪文件里 **0 调用者**（阳性对照：同一次检索认出了 `local_settings_set` 与 `local_open_saved_file`）——即运营换了目录，Agent 还在往旧目录写。 |
| 修复后实际 | Agent store `download.save_directory` ＝ `<新目录>`（`agent_metadata` 写入时间 `2026-09-27T10:18:59Z`，即本机 18:18:59）；此后 18:21 那次下载确实落在 `<新目录>`（`344,809,521` 字节，见 1b）。 |
| PASS/FAIL | **PASS（新下载落新目录这一半）**，**但这次推送来自启动路径**（`offer_stored_choices`，应用 18:19 启动时），**不是页面保存时的那次推送**——`D1` 的「保存后立刻推」这一半 **未跑**（需要在本机设置页按一次保存）。 |

### 2b／2c 已下载的文件找不到（**发现一处计划级缺口**）

| 项 | 内容 |
| --- | --- |
| 命令／动作 | 读 Desktop 的 `settings.toml` ＋ 两个目录的实况 |
| 期望 | 「打开文件」在**已知的保存位置**里按名字找；找不到时说清查过哪些位置 |
| 修复前实际 | 任何地方都没记「这个文件当时写在哪个目录」：Cloud 只有 `file_name`，Agent 的续传记录刻意不含路径，Desktop 只存**当前**一个 `save_dir`。于是「在旧目录」与「被删了」落进同一条分支。实况：素材 27 的文件 `241,823,150` 字节在 `<旧目录>` 里躺着。 |
| 修复后实际 | `settings.toml` 仍是 `schema_version = 1`、**只有一个** `save_dir` ＝ `<新目录>`；升级路径按 v1 语义把「那一个目录」当作全部历史，故**搜索空间 ＝ [`<新目录>`]**。而 `<旧目录>` 里有 5 个文件（4 个素材：`…-27.mp4` `241,823,150`、`…-151.mp4` `173,891,671`、`…-152.mp4` `52,089,181`、`…-153.mp4` 与 `…-153 (2).mp4` 各 `99,242,095`），`<新目录>` 里只有 1 个（素材 34）。Agent store 里那条旧目录记录已在 18:18:59 被启动路径的推送覆盖，所以「从 Agent 那边把旧目录捞回来」这条退路也已经不存在。 |
| PASS/FAIL | **未跑**（需要一次「打开文件」点击），但结论由上面两处读数确定：搜索空间是一个纯函数，`<旧目录>` 不在其中 ⇒ 那 4 个素材的「打开文件」会回答「在已知的保存位置里都没有这个文件」，**而这与「文件被删了」在界面上仍然同形**——这正是本缺陷要消灭的那件事，只是原因从「没记目录」换成了「v1 只记得最后一个目录」。已登记为 Q-11，交用户裁定，**没有用代码补丁掩盖**。 |

### 2d 迁移弹窗（新增能力）

| 项 | 内容 |
| --- | --- |
| 命令／动作 | 在本机设置页换保存位置 → 读弹窗列出的候选与每行的判定 |
| 期望 | 列出「云端任务里记着名字且找得到」的文件，逐行 搬运／删除／保留；空间不足时说明需要多少、目标剩余多少 |
| 修复后实际 | **未跑**（需要一次界面动作）。候选名单的来源是下载中心那个既有接口（`execution_scope=local_agent` ＋ `file_name` 非空 ＋ 去重排序），本机有 7 条成功的本机任务可作候选；但受 2b 影响，这 7 个名字里落在 `<旧目录>` 的会被判为「已不存在」，故**这台机器上弹窗会显示「没有可搬运的文件」**——与 2b 是同一个原因。 |
| PASS/FAIL | **未跑** |

## 3. 缺陷三：取消之后

### 3a 取消后素材卡在「准备中」

| 项 | 内容 |
| --- | --- |
| 命令／动作 | 点一个未准备素材、在 prepare 在飞时取消 |
| 期望 | 素材离开「准备中」，等待它的本机任务落到终态；**再点一次**能重新发起并最终落盘 |
| 修复前实际 | 取消路径一个都不写 `materials`（`cancelTask`／`ReconcileCancelledTasks`／`settleLostLease` 只写任务行），也没有 sweep——两个 reconciler 全仓无调用者，`material_prepare.go` 自己写明「sweep 是本 build 尚未注册的 job」。而 `MarkVideoPreparing` 的守卫是 `video_status IN ('not_downloaded','failed')`，`downloading` 不在其中，**再点也无法重新进入**。素材 29 曾正是这个态，靠 worker 在 15:49 收尾才逃出来；量读数时全库 `0` 个 `downloading`，即这个「永久」态**未在数据里复现**，判据是代码路径。 |
| 修复后实际 | 两处修复：`e6ec78e`（用户取消 prepare 时调既有 `FailDependents` 释放等待者，`TestCancellingAPreparationReleasesTheDownloadsWaitingOnIt`／`…LeavesDependentsAlone`／`…ReportsAFailedWaiterRelease`）与 `ba08851`（worker 侧把被取消准备的素材投影收回，`TestMarkVideoNotPreparedOnlyLeavesTheStateACancelledPreparationLeft`／`…StatementNamesTheOneStateItMayLeave`）。**本臂未跑**——它是 3a 唯一能证明「永久态已消除」的路径，计划里就写明必须真跑，需要一次「点 → 取消 → 再点」的界面动作。 |
| PASS/FAIL | **未跑** |

### 3b 已取消的行没有任何动作

| 项 | 内容 |
| --- | --- |
| 命令／动作 | 看已取消行的动作，点「重新下载」 |
| 期望 | 终态行给出「重新下载」，点击后新建任务并最终落盘 |
| 修复前实际 | `TERMINAL_STATUSES` 含 `cancelled`，而 `canRetry` 只认 `failed`、`canOpen` 只认 `success`、`canCancel` 只认 pending/running ⇒ **已取消行零动作**；服务端重新点击会**新建**一条任务（去重键把 cancelled 算作 finished）。本机现成有 5 条已取消的本机任务（素材 151／152／153 各一条无依赖、素材 29 一条带依赖），全部可用作本臂的被试。 |
| 修复后实际 | `68a32b2`：`canRedownload` 上线，终态行给「重新下载」，走既有的 `createDownload(asset_id)` 而不是 `retryTask`；`已取消／失败行给一条出路`（`gives every terminal material row a way back to a download`／`puts 重新下载 on the rows that were stuck with nothing to do`／`never shows a re-download on an unfinished row`）。**本臂未跑**。 |
| PASS/FAIL | **未跑** |

### 3c 依赖未交付的行「重试」空转

| 项 | 内容 |
| --- | --- |
| 命令／动作 | 对一个依赖从未交付的失败行点「重试」 |
| 期望 | 被具名拒绝，而不是看起来执行了却永远不动 |
| 修复前实际 | `retryTask` 把行改回 `pending` 但不清 `dependency_task_id`，而可领取条件要求 `dependency_task_id IS NULL` ⇒ 该行永远领不到，用户看到「点了没反应」。本机有 6 条这样的失败行（`source_detail_failed` 2、`source_address_missing` 3、`source_fetch_failed` 1），全部带依赖。 |
| 修复后实际 | `bc97628`：`retryTask` 的 WHERE 加 `AND dependency_task_id IS NULL`，命中 0 行时回具名冲突；`TestRetryTaskRefusesADownloadWhosePreparationNeverDelivered`／`TestRetryTaskStillRequeuesADownloadWhoseFactsArrived`。UI 侧由「重新下载」承接。**服务端臂未跑**（需要一次 HTTP 调用，见 §5）。 |
| PASS/FAIL | **未跑**（测试级 PASS） |

## 4. 套件与门禁（在最后一次代码改动之后重跑）

最后一次代码改动是 Desktop 仓 `9b85bf2`（D4）；此后只有本文件与 `checkpoint.md`／`change.md` 的记录改动，未动任何运行时代码。

| 仓 | 命令 | 读数 |
| --- | --- | --- |
| Cloud | `go test -count=1 ./...` | `exit=0`，**67 ok / 0 FAIL** |
| Cloud | `go vet ./...` | `exit=0` |
| Agent | `bash scripts/test.sh` | `exit=0`，`Ran 625 tests … OK` |
| Cloud Web | `npm test` | **40 files / 300 tests**，全绿 |
| Desktop | `cargo test` | **480 passed / 0 failed / 5 ignored**（共 485） |
| workspace | §12 表内六条门禁 | 全部 `exit=0` |
| workspace | `python3 -m unittest discover -s tests -q` | `Ran 106 tests … OK` |

D4（Desktop 新模块 `saved_files.rs` ＋ 四个命令 ＋ 设置历史）的判别力是量出来的，不是推断的：`/tmp/m4a-d4/mutate.py` **23 个变异**逐个施加在同一个实现上、每条只打一个测试，先跑一次基线（**21 个 filter，21 绿**，基线不绿会让变异假红），随后逐个变异要求**诚实变红**——既排除编译错（那是坏编辑而不是被抓住的缺陷），也排除 `running 0 tests`（那是空转的检查）。结论：`23 mutations, 0 not honestly red`。

## 5. 未覆盖（分母在此，逐条点名）

以下臂**没有执行**，原因是**同一个**：能打到这台机器的会话只有一个，而它握在运营手里——本轮用既有凭据登录被 `409` 拒绝（该账号已有活动会话，且我**刻意没有**用 `replace_existing: true`，那会把运营正在走查的会话作废）；节点解析按用户绑定，因此换任何别的账号都到不了那台已绑定的机器。于是需要 HTTP 或界面动作的臂只能由运营的点击来完成。

| 未跑的臂 | 需要什么 | 该臂的期望读数 |
| --- | --- | --- |
| 1a | 一次「节点心跳已过期时」的点击（现在节点已过期数小时，任何一次点击即可） | `202`，不再回 `15105` |
| 1c | 页面上读到两条文案 | 指向「本地环境 → Agent 状态」／说「没有可用的来源地址」 |
| 2a 的第二半 | 在本机设置页换一次目录并按保存 | Agent store 的 `download.save_directory` 立刻变成新目录（不经重启） |
| 2b／2c | 对 `<旧目录>` 里那个 `241,823,150` 字节的已完成行点「打开文件」 | **按当前实现会回答「在已知的保存位置里都没有这个文件」**（原因见 2b，Q-11 待裁定） |
| 2d | 换一次目录并读迁移弹窗 | 列出候选与逐行判定；本机因 2b 会是「没有可搬运的文件」 |
| 3a | 点 → 取消 → 再点 | 离开「准备中」、等待者落终态、再点能落盘 |
| 3b | 对已取消行点「重新下载」 | 新任务 ＋ 最终落盘（被试：素材 151／152／153／29 的 5 条已取消任务） |
| 3c | 对依赖未交付的失败行点「重试」 | 具名拒绝（被试：6 条带依赖的失败行） |

**已覆盖但只到测试级**的（同一分母里点明）：1b 的 `failed` 行可点与文案、1c 的两条文案、3b／3c 的判据函数与 DTO 转换、2d 的候选名单与迁移计划——定位于 Web 与 Rust 的自动化用例，未在页面上观察。
