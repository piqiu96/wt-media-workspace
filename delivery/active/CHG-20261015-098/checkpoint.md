# CHG-20261015-098 Checkpoint

## Completed

- M5-C1～C6 已归档，M5-C7 §6/§7/§8 是当前唯一未闭环阶段；Workspace、Cloud、Agent、Desktop 起点均为干净工作区。
- 已建立 M5-C7 单一全链验收 CHG，沿用 Cloud 合成、Agent 下载、Desktop 壳的现有职责。
- T-01：强制停止旧进程、迁移并重建 Cloud/Agent/Web/打包 Desktop，健康、BitBrowser、产物新鲜、登录及 DMG 启动 gate 全部 PASS；证据见 `evidence/T-01.md`。
- T-02：独立 Compose Scheduler/Worker 真实到点、容量与候选跳过、双 Scheduler 同槽去重、真实混合批次、成片对象 SHA256 与 FFprobe 对账通过；见 `evidence/T-02.md`。
- T-03：operator01 人工任务 252 → 真实 Worker 成片 42 → 打包 Desktop sidecar 经 `transfer_02cfdc38…` 实际落盘，声明 SHA = 校验 SHA = 本地 SHA，FFprobe 1.000s；自动成片 40/41 与人工成片 42 同表同链路读回；见 `evidence/T-03.md`。
- T-04：`production_rule`/`compose_pool_item` 三仓零命中（带阳性对照）、Agent 执行器仅下载、Desktop 无合成执行；T-02 临时关系 82/83/85 清理、策略全部停用、无残留进程；M5-AC-01～12 已收口 PASS；见 `evidence/T-04.md`。
- T-06：创建入口集中到合成任务页、我的素材净删除、关联实体编号全站去 `#`、已下载行按本机文件分支；Cloud Web 67 文件/602 测试、production 6 包 Go 测试、双端构建全 PASS；开发库 18 行空名称回填为 0 且未写迁移；真实页面走查沿新入口真实创建任务 256（排队中）；见 `evidence/T-06.md`。
- T-07：第三轮 7 条整改（参数顺序/预填/提交前拦截、素材按游戏与名称筛选、详情生成结果收口与失败原因、执行过程步骤记录、创建时任务名称与批量序号）；Cloud Web 70 文件/638 测试、production 6 包 Go 测试、双端构建全 PASS；migration 064 在开发库应用并读回；真实页面走查含 Worker 真跑 257/258（成片 43/44）与 256 失败样本的步骤记录；见 `evidence/T-07.md`。
- T-08：第四轮 4 条整改（素材按 (策略,素材) 分「未使用过/已使用过」+ 一个使用情况下拉、同对在途创建由服务端权威拒绝、筛选栏 合成策略-触发方式-状态-创建时间、失败详情补「为什么没有重试」）；Cloud Web 72 文件/668 测试、production 6 包 Go 测试、双端构建全 PASS；migration 065 在开发库应用并读回；真实库并发（6 键同抢 1 条落地、重放不冲突、无死锁）与真实页面走查（两窗同抢一条素材得到中文冲突提示）全 PASS；见 `evidence/T-08.md`。
- T-09：第五轮 5 条整改（一条 (策略,素材) 只跑一次、候选默认发布时间倒序可切点赞倒序、候选行与「我的素材」补点赞/收藏、已取消可重试且人工重试重定基配额、手工跑 compose-worker）；Cloud Web 72 文件/678 测试、production 6 包 + migration 包 Go 测试、双端构建全 PASS；真实库重试三连与创建守卫三态实测、真实页面走查（抽屉/任务页/我的素材）、worker 真跑 25 条积压（pending 25→0，success 12→16、failed 5→27）全 PASS；未新增迁移；见 `evidence/T-09.md`。
- T-10：第六轮按用户裁定完成——策略模型纠偏（`enabled/disabled`、`manual/scheduled`、优先级规则组、单次/每日额度、同一选材引擎、单项失败隔离）、migration 066/067、compose-worker 发布清单缺口修复；机器腿（Web 72 文件/679 测试、Go 85 包行 0 FAIL、双端构建、DMG 03:23:18）、真实独立 Scheduler/Worker 全链（到点 run、额度边界、过滤取反、启停 A/B、双进程防重、单项失败隔离）、M4 抽屉与 Local Agent 真实下载、Cloud Web 38 项走查（含两个先红后绿的缺陷修复）全部 PASS；M5-AC-01/01a/02/03/04/09/10/11 按新模型翻回 PASS；见 `evidence/T-10.md`。
- T-11：素材文件缺失自愈（2026-10-21 走查任务 319/320/321 失败）——合成消费前 `Stat`、每 claim 一次重新准备、`ready` 受控回退（key + `video_prepared_at`）、用户下载/预览预检、准备临时地址重试一次、成功挂接与周期对账、Content-MD5 上传校验、清理边界；Cloud 提交 `c2e3261`，Go 85 包行 0 FAIL、Web 77 文件/721 测试、双端构建 PASS；真实环境重试 319/320/321 全部成功（成片 63/65/64），Garage 错 MD5 400 `InvalidDigest`、正确 MD5 200，三次自愈各只新增 1 条准备任务且暂存对象 0 残留；用户下载端到端与真实并发未在本机复现；见 `evidence/T-11-source-self-heal.md`。

## Current

- 2026-10-22 用户完成 M4–M5 基础功能第一轮走查，反馈基础功能正常；重点产品边界能力仍待下一轮核查。此为阶段性结论，M4-H2 与 M5-AC-13 未最终签收，CHG 保持 `IMPLEMENTING`。见 `evidence/2026-10-22-m4-m5-walkthrough-round-1.md`。
- 2026-10-21 用户反馈合成任务 316～319 持续排队：本地启动脚本只启动 Discovery Worker，遗漏 Compose Worker，且原 `verify/status` 未检查它。已补构建、启动、状态/验收、停止链路；当前托管进程 PID 91351。316/318 已成功，317 正在执行长视频 FFmpeg，319～321 已领取但因源对象不存在而 `input_missing` 失败；单节点/全局/数据库上限均为 2。证据见 `evidence/T-01-compose-worker-followup.md`。
- 2026-10-22 上述失败已按 T-11 自愈闭环：重启 Cloud/Discovery Worker/Compose Worker 后重试 319/320/321，三条均以 attempt 2 成功（成片 63/65/64），素材 154/159/160 的正式对象已重新准备；320 的重试同时恢复了为 stale-ready 预览测试删除的对象。headless 环境无新鲜受信 Local Agent 节点，用户下载在「对象缺失 → 建依赖」之后无法在本机继续，返回 409 `local_transfer_node_unavailable`；该端到端仍待新打包 Desktop 走查。证据见 `evidence/T-11-source-self-heal.md`。
- 2026-10-21 本地未提交工作已收尾：Cloud 的列表筛选、策略运行记录分页、素材规则与成片管理页面改动提交为 `43d3779`；Desktop 的公开读域名 CSP 提交为 `1726433`；Workspace 前端规范归位及产品页面裁定提交为 `2e764d3`。自动验证见下方；这些代码变动尚未经过当前源码的真实页面和打包 Desktop 走查，不能据此将 M5-AC-13 或 M4-H2 签收。
- CHG 保持 `IMPLEMENTING`。T-01～T-10 的历史证据有效，但 2026-10-17 03:23 的 DMG 早于本轮 Cloud Web 与 Desktop 改动，不能用它验收本轮界面和视频读取行为。

## Next

1. 从当前已提交源码重新打包 Desktop，并与 Cloud Web 同场走查合成策略的概览/运行记录、合成任务、成片管理、来源追溯、预览与下载中心；用户签收 M5-AC-13 与 M4-H2 后才能更新验收矩阵和归档 CHG。
2. 对本轮跨页面增量做真实数据走查：Cloud 列表筛选（团队/用户、Profile、内容池、素材、代理和合成策略）、策略运行记录的真实总数与分页、成片管理的下载状态与批量下载。自动测试和构建通过不替代这些页面及 API 读回。
3. 在新打包 Desktop 上核对公开读域名的视频播放与 CSP，以及「已下载但本机缺文件 → 重新下载」；本轮只验证了 URL 转换、Rust CSP 测试和双端 Web 构建，尚无新安装包的可视与真实文件证据。
4. 在新打包 Desktop（有新鲜受信 Local Agent 节点）上补验 T-11 的用户下载 stale-ready 端到端：删一条可丢弃素材的云端对象 → 点「下载原视频」应创建一次云端准备并挂到下载任务 → 准备完成后运营电脑直连下载；同时确认预览返回「暂不可用」而不是 404 页面。
5. Linux 发布链路（`build-release-linux.sh` / `package_release_linux.py`）仍未在 Linux 环境执行；compose-worker 清单修复的既有证据止于静态一致性、交叉编译和单测变异。
6. 保留待裁定项：调度跳过原因合并为 `previously_run` 后不再区分上次成功/失败/在途；人工重试的执行编号不回退；重试确认框与 `compose_task_not_retryable` 的中文措辞；`tokens.css` 的 `--wt-status-*` 是否全站接入；OpenAPI「改策略状态」的 `put:` 与实际 PATCH 路由不一致（生成客户端可能 404）。这些未在本轮顺手改动。
7. 若后续走查包含自动定时触发，需独立启动 `compose-scheduler` 并复核进程与到点 run；本地 M2-B 启动脚本目前只托管人工任务消费所需的 `compose-worker`。
8. 任务 319/320/321 已于 2026-10-22 全部重试成功（成片 63/65/64），素材 154/160/159 的正式对象已恢复；317 的长视频合成结果此前已成功（`success/committing`），成片对象读回仍可补做。

## Blockers

- None.（页面可视走查必须由用户完成，属于签收步骤而非阻塞。）

## Recent verification

- 2026-10-21 合成队列启动补验：`status` 在未启动 Compose Worker 时 exit 1，启动后 exit 0；MySQL 读回 316/317 同时领取，316 成功后 318 接替；配置与 `compose_worker_capacity.max_running` 均为 2。Workspace 生命周期单测、全套测试与治理校验结果见 `evidence/T-01-compose-worker-followup.md`。
- 2026-10-21 本地收尾：Cloud `go test ./...` exit 0；Web `npm test -- --maxWorkers 2` 77 文件/720 测试 PASS；`npm run build:cloud` 与 `npm run build:desktop` 均 exit 0；Desktop `cargo test --manifest-path src-tauri/Cargo.toml` 529 PASS、6 ignored、0 failed。Web 首次默认并行运行的 `localSettingsWiring.test.js` import 扫描超过 5 秒，单独运行 9/9 PASS（扫描约 0.9 秒），限制 worker 后全套通过；未据此宣称实机验收。Workspace 规范相关 8 个 Markdown 文件的本地链接检查 0 缺失；五个治理脚本 exit 0；临时 venv 装 PyYAML 后 Workspace 118 项单测 PASS（系统 `python3` 缺该依赖，首次直接运行在导入阶段报 3 个错误）。
- T-03：`transfer_02cfdc38af2b573063ab72de` success，278362/278362 字节；三方 SHA 闭合 `39025ff4…ca600`；FFprobe 1.000000 秒；重复下载幂等单行。
- T-04：三仓 `production_rule`/`compose_pool_item` 0 命中（阳性对照命中）；`compose_tasks` running=0；策略 23/24/25 `next_run_at=NULL`。
- 治理与产品主计划对齐校验在提交时随脚本复跑。
- T-05：Cloud `go test ./...`、Web `npm test`（569/569）、`npm run build:cloud`、`npm run build:desktop`、Workspace delivery governance 均通过；未把自动测试当作用户签收。
- T-05：`scripts/m2b-local-acceptance.sh all --force-restart` 通过；migration 063 在首次运行应用，第二次读回 0 待应用；Cloud 旧 PID 2464 停止，新监听 PID 11545 于 01:50:40 启动；Cloud/Agent/BitBrowser/Web/Desktop/DMG/登录 gate 全部 PASS。
- T-06：`#`/编号扫描带 HEAD 阳性对照（38→8、25→0，剩余命中全部可枚举且都在测试反向断言或页内锚点里；扫描加 `--untracked`，因为 Cloud 工作区有 7 个新文件未跟踪）；开发库回填两处兜底分支 0 次触发、标题超限 0 次，已如实登记，未把单测覆盖当成数据覆盖。
- T-07：migration 064 开发库读回 `steps_json json YES NULL`（07:02:35 应用）；任务 257/258 各 4 步步骤日志、256 为 1 步失败日志、250（`steps_json` 为 NULL）页面显示「该次执行没有步骤记录。」；步骤 JSON 只含白名单四类 metrics，零对象键/路径。
- T-07：失败原因实机计算色 `rgb(220, 38, 38)`（与「失败」徽标同色、字重 500）；根因是 `tokens.css` 未被任何入口引入，非 scoped 样式；三处失败态改用 `--wt-danger`，并补一条会失败的「引用到的变量必须由已加载样式表定义」用例（变异验证可红）。
- T-08：migration 065 开发库读回 `Non_unique=1`、两列 `(compose_strategy_id, material_id)`（09:11:09 应用，重跑 0 待应用）。
- T-08：真实库并发——对同一 (策略,素材)、6 个不同 `request_key` 同时 POST：恰好 1 条落地、5 条 `15219 compose_task_conflict`（中文唯一）、库中该对在途 1 行、6 个响应全部有归属且日志无死锁；对在途任务 264 的 `request_key` 重放 → `created=[264]`、`failed=[]`、该键仍 1 行。「恰好一条」不是「恰好两条里赢一条」：响应数、任务行数、在途行数三个都在同一断言里对过。
- T-08：四个筛选项各筛一次的请求与总数对账（`trigger_type=manual`→22、`status=failed`→6 与库里 failed=6 一致、`compose_strategy_id=25`→3、日期区间 →`created_from/before` 为本地日界且该区间库里正好 27 条），重置回到 27。
- T-08：新断言逐个做变异/阳性对照（分片 200→500、去掉去重、删掉「已生成 N 版」、筛选顺序、`UNIQUE` 负向断言），红在各自的那一条上；旧验收脚本 2966 行内 `compose` 零命中并带阳性对照（同模式在 `router.go` 命中 25 处）。
- T-09：真实库三连（任务 247）——`failed/input_missing`（`ac=1`）→ retry 200 → `pending`、错误码清空、`ma=4`；cancel → `cancelled`，占位行 `attempt=2` 转 `cancelled`；**再 retry 200（不是 1062）**，同一条占位行重开 `pending`。任务 25（取消态带残留 `storage_error`，`ac=2`）→ 200、`ma=5`（取消态不看错误码）。任务 248 临时置 `execution_uncertain` → 409 `15217 compose_task_not_retryable`、行未动（已还原）。
- T-09：创建守卫三态实测——`(25,153) failed` / `(25,157) success` / `(25,161) pending` 逐个提交全部 `15219`「该素材在这个策略下已有任务记录…」，每次创建后该对记录数仍是 1；阳性对照 `(25,161)` 无记录时 200 且 `created=[284]`；(11,27) 先撞 15214「素材不在我的素材或已移出」（守卫之前的一层），已换合法候选重做。
- T-09：调度真库用例 `TestLiveComposeScheduleDueAndRepeatScan` PASS，`skipped=[{1 other_game} {157 previously_run} {161 previously_run}]`，事务内 success/failed/cancelled/pending 四种状态都判 `previously_run`。
- T-09：worker 真跑前后 `pending 25→0`、`success 12→16`、`failed 5→27`、`cancelled 2→1`；UI 重试出的任务 20 被执行成 `attempt 1 | source=manual | outcome=success`；worker stdout 为空（执行事实只落库）。
- T-09：新断言变异（`isUsed` 去掉 `cancelled_count` → 8 条红；去掉排序调用 → 5 条红；重试守卫缩回白名单 → 红；`max_attempts = attempt_count + ?` 换成自增 → 红；均还原后绿）；旧验收脚本 `m2b_local_acceptance.py`（945 行）`compose` 零命中，阳性对照 27 处。
- T-10：真实独立 Scheduler/Worker（`.cache/m5c7b-*`，02:27 构建）——策略 36 到点 run `45cf3855`（slot 02:32:00，落库 02:32:05，候选 5 / 创建 2 / 跳过 other_game:1、filtered:153、filtered:157）→ 任务 299（154，failed/input_missing）与 300（161，success → 成片 49）；额度和过滤边界（37=1/1、38=1/10、39 过滤不动额度）、停用不触发/启用不立即触发（`next_run_at=now+2min`）均真库读回；`TestLiveComposeSchedulerProcessesDeduplicate` PASS（双进程 + 重启各 1 run/1 task）。
- T-10：单项失败隔离——预置 `request_key` 后到点 run `d338c176`（策略 42，slot 02:55:42）`created_count=2`：任务 312（153，failed）与 314（161，success → 成片 58）都在，157 的插入撞 `uq_compose_tasks_request_key`（1062）只回滚自己，任务 id 312→314 缺 313 即 SAVEPOINT 回滚的 AUTO_INCREMENT 空洞；探针行事后已删。
- T-10：成片三方闭合——49/50/51/52/53/58 逐条对象 Stat + 预签名 GET sha256 + ffprobe；例：161 的 4s 成片 69,142 B `4d802de9…beacd`、157 的 4s 成片 717,031 B `f0d22816…707c`，`size_match`/`sha256_match`/`duration=4.000000` 全部一致。
- T-10：M4 抽屉与下载——任务 306（`schedule_slot NULL`）真跑成片 53，同 `request_key` 重放返回 306、换 key 同对提交得 15219 中文冲突；`schedule_slot IS NOT NULL` 当天仅 1 条 → 抽屉任务不吃每日额度；operator01 任务 315 → 成片 59 → `transfer_75b40509…` 由打包 sidecar 领取，finished 03:01:24.735、69,142 字节，落盘 `wt-media-download/20261017/三角洲-59-成片-59.mp4`，SHA 与对象/库三方一致。
- T-10：页面走查 38/38 断言通过、0 pageError（`/private/tmp/wt-t10/walk2.{cjs,json}`、20 张截图）；两个缺陷先红后绿：`structuredClone` 搬 Vue 代理使「编辑」无反应、`t-select` 的 `<t-option>` 插槽缓存使用户第一个条件的运算符不随字段变化。
- T-10：migration 067 于 2026-10-16 18:25:17 应用，读回 `status DEFAULT 'disabled'` 与检查约束 `enabled|disabled`；`TestServiceProcessCheckCoversReleaseManifest` 在删掉打包器进程清单里的 `compose-worker` 后红、还原后绿。
- T-10：收尾重测（最后一次改动之后）——`go test -count=1 ./...` 85 个包行（72 ok + 13 no test files）0 FAIL、exit 0；`vitest run` 72 文件/679 测试、exit 0；`npm run build:cloud` exit 0；DMG `起飞_0.1.0_aarch64.dmg` 03:23:18（22,953,983 B），ZIP 44,931,472 B，shell 二进制内嵌 `/assets/ComposeStrategyPage-DEwUR_yX.js` 与 03:22 新构建的同名 chunk 逐字符一致。
- T-10：治理收口——五个 workspace 校验脚本（delivery governance / product master / ai workspace / skills / m0 config）全部 OK；`config/contract-map.yaml` 五条 Cloud 修订对齐活源；Desktop `contracts.lock.json` 的 `cloud_agent_api` 对齐 `v1@2026.10.13.1`（自 Cloud `88aa46a` 起滞后）；workspace `tests` 118 项 OK（临时 venv 装 PyYAML；默认 python3 缺该依赖）。
- T-11：`go build ./...` exit 0；`go test ./... -count=1` 85 包行（73 `ok` + 12 `no test files`）、0 FAIL、exit 0（最后一次 `gofmt -w` 之后整套复跑，读数不变）；Web `npm test -- --maxWorkers 2` 77 文件/721 测试 PASS；`npm run build:cloud`、`npm run build:desktop` 均 exit 0。
- T-11：Garage dev 桶 Content-MD5 双向对照——错 MD5 PUT → 400 `InvalidDigest`（`MD5 checksum verification failed (from content-md5)`）；同字节正确 MD5 → 200；探针对象 DELETE 204。没有只测失败侧。
- T-11：真实自愈三次——319/154：`transfer_9654…` 71,962,320 B → 成片 63 `compose-outputs/319/2/output.mp4` 2,211,882 B SHA `6b7a5248…d668e62`（下载复算一致）；321/159：`transfer_e40b…` 73,342,566 B → 成片 64 126,508,784 B；320/160：`transfer_dc2c…` 162,200,269 B → 成片 65 250,546,703 B。三条 attempt 2 全 success，`staging_cleaned_at` 均非空。
- T-11：清理读回——`compose-staging/319|320|321/` 与 `materials/154|159|160/.staging/` 的 KeyCount 全部 0；正式素材与成片对象各 1 个；每个自愈事件只新增 1 条 `compose_input_prepare`。
- T-11：stale-ready 预览——删对象后 `GET /materials/160/video-url` → 409 `15005 material_unavailable`；恢复后同一请求 → 200 且返回预签名 URL。用户下载 `POST /materials/160/downloads` 因本机无新鲜受信 Local Agent 节点返回 409 `15105 local_transfer_node_unavailable`，该端到端未复现，已登记 Next。
- T-11：重启后 `status`——cloud pid 2054、worker 2078、compose-worker 2098、agent 2106、web-dev 2118、desktop-dev 2142 全部 alive；BitBrowser via Agent PASS。
