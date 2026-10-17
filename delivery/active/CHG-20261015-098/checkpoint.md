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

## Current

- 2026-10-17 T-10 已完成全链与页面走查，**待用户签收**（不代签、不归档）。本轮手工起的 `.cache/m5c7b-compose-scheduler`(79707) 与 `m5c7b-compose-worker`(79709) 走查后已停；旧 DMG 挂载实例与其 sidecar 已结束并卸载，新 DMG 为 03:23 构建。开发库残留：策略 36/38/39 `enabled` 且 `next_run_at` 在 2026-10-18 02:32～02:35，37/42 `disabled`；任务 10 / 成片 7 / run 13 原样保留作证据。
- 2026-10-16 用户提交合成任务页面走查整改结论；T-05 已完成代码、自动验证和本机 migration 063/环境重建，待真实页面复查及 M5-AC-13/M4-H2 同场签收。详见 `evidence/T-05.md`。
- 2026-10-16 第二轮整改 T-06 已完成机器腿与 Cloud Web 页面走查；“本机实测缺文件 → 重新下载”一格只在本机打包 Desktop 里出现，登记为未验事实。
- 2026-10-16 第三轮整改 T-07 已完成机器腿与 Cloud Web 页面走查，待用户按同样流程复查并签收。
- 2026-10-16 第四轮整改 T-08 已完成机器腿、真实库并发实测与 Cloud Web 页面走查；Cloud 以新代码在 17:19 重启（PID 53220），Vite 5173 未动，走查用的临时任务行与临时会话已清理。待用户复查签收。
- 2026-10-16 第五轮整改 T-09 已完成机器腿、真实库重试三连与创建守卫三态实测、Cloud Web 页面走查；Cloud 以本轮代码在 18:51 经 `bin/control.sh start` 重启（PID 61770，旧进程是 17:34 的过时二进制，已先停），手工起的 compose-worker 在走查结束后已停掉（用户要再看它跑需再起一次）；走查用的临时会话 `r5-t09-admin` 已删。待用户复查签收。

## Next

1. 用户按真实计划流程走查并签收 M5-AC-13 与 M4-H2：Cloud Web 与 03:23 的新 DMG 上复查策略页（状态/执行方式/条件/额度/启停/执行反馈）、任务页（触发方式筛选与实体追溯）、我的成片（预览/下载/来源追溯）、下载中心；打包 Desktop 的视觉逐屏只能由用户肉眼确认（本机无法程序化驱动/截取 GUI）。
2. 第五轮合成任务三处体验（候选排序、已使用过只读、重试确认措辞）继续由用户 review；打包 Desktop 上“已下载且本机缺文件 → 重新下载”也待补验。
3. 用户签收且 M5-AC-01～13 全绿后，更新验收矩阵并归档本 CHG。
4. 待裁定：调度跳过原因合并为 `previously_run` 后不再区分「上次成功/上次失败/在途」（历史 run 仍按旧 key 渲染）；人工重试后执行编号不回退（要回到从 1 重数需要新列或清 attempt 表 = 新迁移）；重试确认框与 `compose_task_not_retryable` 的中文措辞。
5. 待裁定：`web/src/shared/styles/tokens.css` 的 `--wt-status-*` 语义表从未被任何入口引入（全历史零命中），接上会把 TDesign 的 success 色从 `#2ba471` 换成 `#00a870`，属全站换色，需用户决定接不接。
6. 待裁定：OpenAPI 把「改策略状态」写成 `put:`，实际路由是 PATCH（Web 也用 PATCH），按契约生成的客户端会 404；本轮只登记未改契约。
7. 未验事实：Linux 发布链路（`build-release-linux.sh`/`package_release_linux.py`）本机跑不了，compose-worker 清单修复的证据止于静态一致性 + 交叉编译 + 单测变异。

## Blockers

- None.（页面可视走查必须由用户完成，属于签收步骤而非阻塞。）

## Recent verification

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
