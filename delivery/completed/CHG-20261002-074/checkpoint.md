# CHG-20261002-074 实施进度（2026-10-02）

- Status: DONE
- 关闭：2026-10-03（用户「chg074 可以关闭，基本功能已完成，有些优化项后续在做」；出包与人工走查用户已手动完成，本 CHG 不重打 DMG、不等复验。未逐项给读数的走查项、关闭读数与遗留清单见 `change.md` §8）。**下面各节是关闭前的最后状态，作为历史保持原样**，最终状态以本节末尾「关闭（2026-10-03）」段为准。记录已移入 `delivery/completed/CHG-20261002-074/`。

契约 v2 主线：**阶段 1、2、3 代码全部提交，收尾项完成；走查发现的面板误报已修复（`416489f`）。** DMG 已按本轮改动重打（23:57），并已跑通一条完整下载（见下「打开执行器开关」一节）——实机走查由用户驱动，已由用户签收（见顶部「关闭」行与 `change.md` §8.1）。范围与验收以 [change.md](change.md) 为准。

发布链另有一条既有缺陷已修并**首次端到端跑通**（01:03，`verify-release-macos.sh` 通过），见下「比特浏览器扫描降频」末两条。

## 走查阻断项：登录页自指重定向（2026-10-03，cloud `web/` 未提交）

用户报「当前 web 端一直在跳登录，无法登录」，确认形态为浏览器里的 Cloud Web、点「登录」直接弹回登录页（无 20010、无报错）。

- **根因**：`LoginPage.vue:43` 挂载时探测 `me()`，未登录必然 401；`http.js` 把任何 401（除 `/auth/login`）变成整页跳 `/login?redirect=<encodeURIComponent(当前地址)>` → 登录页重定向到自己、`redirect` 每轮再叠一层编码 → 整页重载 → 再探测 → 再 401。两台 `main.ts` 的守卫都在 `to.path === '/login'` 时直接 `next()`，拦不到。点登录没反应同源：DOM 每 ~90 ms 被换掉，mousedown 的目标在 mouseup 前已销毁，click 根本不产生——所以**服务端一条登录 POST 都没收到**（最后一次仍是 `01:25:08`）。
- **改动**：`web/src/shared/api/http.js` 加一条 `onLoginPage` 判断（已在 `/login` 就不再导航）；**不豁免 `/auth/me`**，那会拆掉内容页「会话失效 → 带 returnUrl 跳登录」的既有兜底（`DashboardPage` 这类只调 `me()` 的页面正靠它）。新增用例 2 条于 `web/src/http.test.js`。
- **读数**：`npx vitest run`（`web/`）**50 文件 / 486 用例通过**（484→486）；变异对照撤守卫 → 恰好那 2 条红；**实机对照（同一无头 Chrome 装置，唯一变量是守卫）**：打开 `/login` 后 20 秒内 `/auth/me` 401 —— **撤掉 71 次 / 带上 1 次**；未登录打开 `/` 仍恰好 2 次后停住（重定向没被关掉）。
- **覆盖边界**：只验证了 Cloud Web dev 栈（5199）+ 无头 Chrome；真实浏览器人工登录与**打包版 app 均未验证**——前端打进包里，**必须重打 DMG**。另记一条失败探法：`--dump-dom` 在两状态下都只读到 1，没有判别力（Chrome dump 完首屏即退出）。
- **同时更正**：`evidence/walkthrough-panel-false-alarm.md` 里「401 风暴来自残留标签页轮询、与本缺陷无关」是误判，已改写。详见 [evidence/login-page-redirect-loop.md](evidence/login-page-redirect-loop.md)。
- **这是走查阻断项，已按关闭裁定落地**：修复 `8a21041` 已合入 main，用户已在重打的包上走查并通过（证据覆盖见 `change.md` §8.1——dev 栈有无头 Chrome 对照，打包版读数来自用户）。

## 比特浏览器扫描降频（2026-10-03，agent / desktop / cloud `web/` 未提交）

用户提出「自动刷新里请求比特浏览器列表的接口频次改成 5 分钟」，并问「做缓存还是整体降时间」。

- **为什么不能整体降频、也不能在胶囊里缓存整份 status**：`/api/v1/status` 的响应是融合的——「本机服务（含`当前任务`）」与「比特浏览器」两行来自同一次调用，整份缓存会连前一行一起冻住；而 Desktop 的 `runtime-report` 用的**就是**这次的 `main_user_id`（`preflight.rs`），云端拿它做执行门比对，「比特账号绑定」也读同一字段。缓存成默认行为 → 换账号后读回旧 id，**会绑错账号、下载被挡**。
- **用户裁定**：只缓后台轮询，本机服务保持鲜活。实现即**默认仍实时扫描，只有胶囊的自动 tick 显式选入复用**：Agent 新增 `GET /api/v1/status?scan=reuse`（缺省 / `scan=live` = 今天的行为），`BitBrowserScanCache` 只存**成功**的扫描、TTL 300 s，且只由 `?scan=reuse` 与显式扫描路由填充。
- **不变量**：不传新参数的调用与今天逐字节相同。绑定流程、`runtime-report`、`ProfilesPage`、`AccountsPage`、`init.js`、个人中心都不传 → 一律实时；Rust 侧 5 个内部调用点（`account.rs` ×2、`bind.rs` ×2、`local_agent_task_status`）显式传 `None` 钉住实时。
- **契约**：`local_agent.openapi.yaml` 的 `/api/v1/status` 加可选 `scan` 参数、`info.version` → `2026.10.03.1`，README 的 revision 同步（`test_contract_docs.py` 会查这一对）；workspace 侧按同一约定把 `config/contract-map.yaml` 的 `local_agent_api.contract_revision` 一并推进到 `2026.10.03.1`，并同步 `scripts/verify_m0_config.py` 里钉住它的期望值（该文件的约定是「合约前进属需复核的变更，故此处是钉子而非引用」；只推 map 不同步钉子会当场多一条红灯，实测见下）。**不新增 path**，按 `docs/contracts/compatibility-policy.md` 属兼容变更，无需 decision record。
- **实机读数（判据 = 打包 sidecar 二进制本身，非 Python 层）**：把 DMG 里的 `wt-media-agent` 单独起在 8799，30 秒一次打 `?scan=reuse`。服务端自己的 `duration_ms`：冷启 **299** → 连续缓存命中 **38/51/50/51/42** → `scan=live` 探针 **333** → 缓存继续 **51/38/53/49/50** → **00:50:37 缓存到期，一次真扫描 333** → 之后回到 **48/50/50/49**。两次真扫描相隔 **5 分 12 秒**（tick 30 秒，到期落在其后第一个 tick）。与改动前对照（旧包 `agent.log`：每 tick 都是 **300–814 ms**）方向与量级都对上。
- **顺带证实**：`scan=live` 探针**不刷新**缓存——它之后那次到期仍落在 00:50:37 而非顺延 5 分钟，与用例 `test_a_live_scan_does_not_satisfy_a_later_reuse` 一致。
- **覆盖边界（未覆盖就说未覆盖）**：**「胶囊每 30 秒真的带上这个参数」未经实机验证**——本环境下打包 app 起不来：WebView 反复重载（`IPC custom protocol failed` 278 次 / `Couldn't find callback id` 122 次），`local_agent_start` 被调 **279** 次（supervisor 逐次答「已在运行，忽略」，计数 279）并在 15000ms 后停止 Agent，胶囊始终没进稳态，`agent.log` 在 00:39:04 后**再无一行**。该路径只由源串断言 + 变异对照覆盖（见下）。
- **读数（最后一次改动之后重跑）**：agent `scripts/test.sh` **688 通过 / 0 失败**；desktop `cargo test` **507 通过 / 0 失败 / 6 ignored**（506→507）；web `vitest run` **50 文件 / 484 用例通过**（49/480→50/484）；cloud `go build ./...` + `go vet ./...` rc=0、`go test -count=1 ./internal/...` **62 ok / 0 FAIL**（本轮未动 Go 码）。
- **变异对照（三处，各自变红后还原）**：agent ①`scan_cache` 无条件注入 → `StatusScanParameterTests` 3 红；②忽略查询串恒取 `reuse` → 3 红；③TTL 判断去掉 → `BitBrowserScanCacheTests` 3 红。web ①tick 去掉 `reuseScan` → 红；②`manualCheck` 加上 `reuseScan` → 红。
- **已修复（2026-10-03，用户裁定「WT Media.app 需要修改掉」）——发布链把 app 名硬编码**。根因先查清再动手：`productName` 由 `WT Media` 改为 `起飞`、窗口标题改为「起飞 · 内容运营平台」、`bundle.icon` 同批加入，都在 `20e00d1`（CHG-072/073 品牌图标，10-01），前端 `title`/`favicon`/`BrandLogo`/登录页同期已换（`0519fa8`），均已合入 main → **`起飞` 是有意的品牌名，脚本才是漏改的那一侧**（符合「基线与实现冲突时回写基线」）。改法：三个脚本改为从 `tauri.conf.json` 读 `productName` 拼 app 名、DMG 名与卷名（`VERSION` 本来就这么读，同一处漂移的另一半），`build-release-macos.sh` 再补一条「没产出 `.app` 就带路径报错退出」——原来的隐身效果来自 `stage-release-config.sh` 在 `set -e` 下对着不存在的路径**零输出**退出 1。同时按用户裁定改客户可见文案：`package-release-macos.sh` 的 README 标题与安装指引、发布目录名（`WT-Media_…` → `起飞_…`）、`sidecar/integrity.rs` ×2 与 `sidecar/mod.rs` ×1 的「请重新安装完整的起飞安装包」、`diagnostic.rs` 的「起飞诊断包（脱敏）」；`repair-macos-signing.sh`/`stage-release-config.sh` 的 usage 串改成中性的 `/path/to/App.app`。**实测判据是整条链跑完，不是分步**：`bash scripts/build-release-macos.sh` 从 `cargo tauri build --bundles app` 一路跑到最后一行 `macOS DMG contains a complete ad-hoc-signed app: …/起飞_0.1.0_aarch64.dmg`（rc=0），中途 `versions ok`、`config-dir … files=2`、`codesign … satisfies its Designated Requirement`、`Agent configuration in the DMG is a 2-file mirror of config_online/`、`versions verified` 全部照常打印——**`verify-release-macos.sh` 首次真的通过**（上一轮那条 DMG 是手工分步打的，它根本没跑到）。`rustfmt --check --config skip_children=true` 对 6 个改动文件全绿；desktop `cargo test` **507 通过 / 0 失败 / 6 ignored**。**有意未改**：Rust 与 Agent 用例里 `/Applications/WT Media.app/…`、`WT Media.app` 这类**样本路径串**（`integrity.rs` ×3、`upgrade.rs` ×1、`test_runtime_config.py` ×1）——它们喂的是「路径形状」函数（`resolve_sidecar`/`inside_a_bundle`/`.app` 布局），与名字无关，改了反而像是在暗示这些用例跟名字耦合。
- **登记 2（`wt-media-desktop/contracts.lock.json` 落后，先于本次改动就存在）**：逐条对比 `config/contract-map.yaml`，5 条里 **2 条陈旧**——`local_agent_api` 钉 `v1@2026.07.14.7`（map 本次已前进到 `2026.10.03.1`，见下），`local_event_schemas` 钉 `profile-guard@2026.07.14.8` 而 map 写 `2026.07.14.9`；其余 3 条一致。该不一致正在让 `test_static_cross_repo_contract_and_security_matrix` 变红（见下面的 workspace 读数）。本次不改，登记待裁定。
- **登记 3（文档索引与死链）**：`docs/standards/` 下两篇前端规范（`前端交互规范.md`、`前端架构与视觉规范.md`）在 `AGENT-INDEX.md` 里 **0 命中**（索引只列 product / engineering/architecture / engineering/specs / contracts / decisions）；`docs/engineering/specs/README.md:12` 与 `docs/decisions/0007-visual-engineering-baseline.md:9` 都链向已删除的 `web-desktop-visual-system.md`（文件实测不存在）。登记待裁定。
- **登记 4（新发现，先于本次改动就存在，不修）**：`scripts/verify_m0_config.py` 的 `cloud_agent_api` 钉子现在是红的——它期望 `contract_revision '2026.07.14.7'`，而 map 写着 `2026.10.01.1`。定位到 `786fdeb docs(chg-069): 任务 21 落档`：那次只推进了 map，没同步这个钉子（钉子最后一次被动是更早的 `6f6c2f0`）。这正是该文件自己注释里说的「钉子过期会产生噪音红灯」，也是 CHG-20260923-059 Q-06 登记过的缺口（钉子只保证「map 没背着人动」，保证不了「这个值还对」，且从不与相邻的定义文件对比）。**不修**：按该门禁的设计，把钉子移过去本身就是那次合约前进的复核动作，属 CHG-069 的账。
- **workspace 读数（本次同时取的基线）**：`python3 -m unittest discover -s tests` **92 用例 / 4 失败**，4 条全部先于本次改动——把我改的两个文件 stash 掉后重跑，读数逐条相同（同样 92/4）：`test_contract_map_matches_m1_cloud_agent_compatibility` 与 `test_contract_map_provider_paths_exist_in_full_workspace`（两条都只含上面那条 `cloud_agent_api`，未提及 `local_agent_api`）、`test_static_cross_repo_contract_and_security_matrix`（即「登记 2」的 `contracts.lock.json` 不一致）、`test_current_product_master_and_governance_are_aligned`（活动 CHG 的待裁定/仓库字段，随 CHG-074 状态变化）。本次一条都没修。
- 变更文件：agent `runtime/constants.py`、`runtime/environment.py`、`local_api/server.py`、契约 yaml + README、两个测试文件；desktop `commands/agent.rs`、`commands/account.rs`、`commands/bind.rs`、`sidecar/mod.rs`、`sidecar/integrity.rs`、`diagnostic.rs`、`scripts/{build-release-macos,verify-release-macos,package-release-macos,repair-macos-signing,stage-release-config}.sh`；cloud `web/src/apps/desktop/features/local-agent/{WorkEnvPill.vue,work-env-status.js,service.js}` 及新增 `web/src/workEnvPillScanReuse.test.js`；workspace `config/contract-map.yaml`、`scripts/verify_m0_config.py`。

## 本地栈 worker 与换节点重指（2026-10-02，未提交）

用户报「下载视频一直在排队」，要求确认 worker 在不在、`control.sh` 会不会带起 worker/scheduler。两条结论：

- **`control.sh` 不带 worker，也不带 scheduler**（改动前 harness 只有 cloud/agent 两个组件）。已在 `scripts/m2b_local_acceptance.py` 补 `start_worker()`（构建二进制，**不用 `go run`**——没有端口可供清扫，`go run` 的子进程必成孤儿）、三行 `status`（worker 用 `health=pid-only url=-`）、`stop` 第三组件、以及可失败的 `verify_worker()`。scheduler 有意不起（定时入队新抓取，与下载链路无关）。
- **「worker 没跑」这个初判是错的**：`ps | grep -i wt-media` 匹配不到 `go run ./cmd/discovery-worker` 及其编译子进程，空集与「确实没跑」长得一样。换 `grep -E "discovery-(worker|scheduler)"` 后现形——用户终端手起的一份（pid 67913/67919）自 Oct 1 13:02 一直在跑，库里领用记录 `cloud-worker:…:67919:…` 可对。
- **排队根因与 worker 无关**：唯一非终态任务 `transfer_d6a52d8b7d65af4fa9000f4c` 是 `local_agent` 维，卡在**节点换代**（`assigned_node_id` 指向 22:09:59 被标 `replaced` 的旧节点，claim 按精确 id 过滤）。修复：`runtimebinding` 的 `saveNode` 事务内在 INSERT 新节点前，把该 user+device 名下 pending/running 的本地用户下载任务重指到新节点（只动 `assigned_node_id`，照抄 `unbindDevice` 的范围形状）。
- **读数**：cloud `go build`/`go vet` rc=0、`go test -count=1 ./internal/...` 62 ok / 0 FAIL（69 包）；变异对照（撤新 UPDATE）用例变红后还原；新谓词对着真库跑 SELECT 恰好命中那 1 行；`bin/control.sh status` 三行 alive、`verify` 全绿、`verify-control.sh` PASS；kill worker 后 `verify` 变红（证明新检查非空转）；`stop` 后无孤儿。详见 [evidence/local-worker-start-and-node-repoint.md](evidence/local-worker-start-and-node-repoint.md)。
- **结论边界（当时）**：worker 起来了，但**本地下载仍不会跑** —— 见下一节：那条结论的后半段（「DMG 缺 manifest」）**只是第一层**，不是根因。
- **裁定（2026-10-03）**：环境类发现（worker 起停 / harness 改动 / 执行器开关 / manifest / report 归属）**继续挂 CHG-074**，不独立成项；手起的重复 worker **收掉**（复查时已自行退出，只剩受管 `22591`）。
- **待裁定**：`sensitive_browser_tasks.node_id` / `browser_profile_runtime_presence.node_id` 的同类搁浅。

## 打开执行器开关 + 操作后刷新（2026-10-02，desktop 与 cloud `web/` 未提交）

用户追问「下载依然没动静」，本轮把它跑到通。

- **根因：安装包里从来没有执行器。** Agent 的领取循环整段挂在 `config.run_runner` 后（`bootstrap/sidecar.py:18`），默认 `false`，而 Desktop 交给 sidecar 的环境变量只有 host/port/token/data_dir 四项——`environment()` 没有这一条，`git log --all -S RUN_RUNNER` 在 desktop 仓任何提交里都是空。随包 config 的注释却写着「The acceptance scripts and Desktop turn it on」：**Desktop 那一半从未实现**。正式安装包从未能执行过任何下载；历史上跑通的每一次都是命令行手起一个带该变量的 Agent。
- **对前一节的更正**：manifest 是**必要不充分**条件。补上记录文件后真 sidecar 确实起来了（pid 23819/23821），claim **仍是零**。另一处误判：`runtime-report` 是 **Desktop 的 Rust 客户端**在发（`preflight.rs:217`），不是 sidecar 心跳——所以「节点 online」只证明 Desktop 活着，不证明 Agent 会干活，这正是前一节所有绿灯都没拦住问题的原因。
- **阳性对照（用未改的 app 做）**：`environment()` 是加入继承环境而非替换，故 `open -n -a <包> --env WT_MEDIA_AGENT_RUN_RUNNER=true` 即让 sidecar 继承 → 10:24:54 后第一笔 claim 出现在 23:44:17 → 23:46:09 success，162200269/162200269 字节，落盘文件大小逐字节相符。改动的效果与继承路径由此可分开归因。
- **产品修复**：`sidecar/mod.rs` 的 `environment()` 加 `WT_MEDIA_AGENT_RUN_RUNNER=true` + 先红后绿断言；重打 DMG 后 launch 即 claim，**无需 export**。边界：python 回退拿到它也不领任务（`local_api.server` 从不调 `start_task_loops`），回退本就是只答状态的降级态。
- **搁浅行未手工改库**：用户自己点了「重取」（先 cancel 再 createDownload），新任务落在当前可信节点——重取路径是通的，缺的自始至终只有执行器。
- **端到端（最终包，无手起 Agent、无 export）**：走 API 发起素材 161 的下载 → `pending` → `running`（`claimed_by_node_id=agent-node_227b8c31…`，即当前节点）字节 19MB→490MB 单调爬升 → **00:07:27 success 495383052/495383052**；落盘 `stat` 恰好 495383052 字节，另一份素材 160 为 162200269 字节，均与 `materials.video_size_bytes` 逐字节相符。**这是本轮唯一能写成「安装包能下载了」的判据**——此前的成功读数都还带着 export 或半途而止。
- **附带修复（用户中途报障「点击取消/下载/重试后页面不刷新」）**：三处独立漏刷——`MyMaterialsPage.download()` 从不重读（而该行状态由使用记录算出）；`DownloadCentreDrawer` 从「历史」再打开时切回「进行中」就 `return`，但那个 watcher 只重估轮询闸门、不取数，闸门又依赖已缓存列表；`MaterialDetailDrawer.cancelDownload` 只重读抽屉自己的 ref，宿主行不跟着变（新增 `cancel` 事件 + `@cancel="load"`）。
- **读数（最后一次改动之后重跑）**：desktop `cargo test` 506 通过（505→506）；web vitest 49 文件 / **480 通过**（476→480）；双构建 `✓ built`；cloud `go build`/`go vet` rc=0、`go test -count=1 ./internal/...` **62 ok / 0 FAIL**（本轮未再动 Go 码，与前一节同）。
- **一次假绿记录在案**：前端变异对照的第一次 `-t` 过滤传的是注释片段而非真用例名，没有用例匹配，检测器把「没跑」读成了绿；换成真名后为红。
- **~~待裁定~~ 已撤回**：上一版此处登记「`sidecar/mod.rs` 同一段注释声称 Desktop 按启动传 `WT_MEDIA_AGENT_ID`」——**该句不成立，撤销登记**。注释原文只说明这些名字由 Agent 的 `runtime/config.py` 字段表声明，全文无此变量名；`git grep` 在 desktop 仓 0 命中（阳性对照 `WT_MEDIA_AGENT_RUN_RUNNER` 2 命中）。如实事实：Desktop 不传它 → 每台机器上由 Desktop 启动的 Agent 都自称 `local-agent-dev`（`runtime/config.py:180` 默认值），**节点身份**则是注册时生成的 `agent-node_<hash>`；实测各节点 `agent_id` 都是该默认值且**无可观察后果**，属诊断显示字段，**不修代码**。
- **手起的重复 worker 已自行消失**：复查只剩受管 `22591`，`67913/67919` 不在进程表（同 pattern 仍能看到 22591，非模式问题）；受管 worker 三个循环齐备，无空档。
- 完整取证（含更正与反例）见 [evidence/local-worker-start-and-node-repoint.md](evidence/local-worker-start-and-node-repoint.md)。

## 走查修复 2（2026-10-02，cloud `web/` 未提交）

- **用户提出**：按钮「以当前环境为准」看不懂、账号相同时仍给绑定入口、弹窗不说后果、右上角胶囊与个人中心数据不一致。
- **改动**：按钮改名「比特账号绑定」并按「账号不一致」收紧可见性（原先页面那个 `bitAccountDiffers` 是**未被引用的死代码**）；弹窗逐条说明窗口归属后果；`bitAccountDiffers` / `maskBitAccountId` 收进 `work-env-status.js` 作为唯一判定源；胶囊取数合并为 `loadWorkEnvInputs`（四项一次读齐），挂载/手动/轮询/重新可见共用，并加冷启动退避 `[2s,5s,10s]`。
- **根因**：胶囊轮询只刷 4 项输入里的 2 项、`cloudUser`/`localDevice` 挂载后永不重读、窗口重新可见不刷新；`local_agent_status` 在 sidecar 起来前返回 Err（`main.ts:29` fire-and-forget），挂载时的检查撞上该窗口。
- **未闭环**：`document.hidden` 在 Tauri WebView 启动时是否为 true 未实测（若为 true，旧代码的 interval 从不建立）。走查时按「不点击等满 30s 胶囊是否自行转绿」判定，读数写回 evidence。
- **读数**：vitest 49 文件 / 476 用例通过（462→476）；双构建通过；两组变异对照各自变红后还原。
- 读数、判定边界与待复验清单见 [evidence/bit-account-binding-and-pill-refresh.md](evidence/bit-account-binding-and-pill-refresh.md)。

## 走查修复（2026-10-02，cloud `416489f` + `9d54203`）

- **走查发现**：DMG 安装版（迁移已应用、Agent/比特浏览器/Cloud 全部健康）面板误报「需检查」：本机服务=未连接执行节点、比特浏览器=未知、blocker 落在比特浏览器条。
- **根因（实证）**：WorkEnvPill 把 snake_case 快照直喂读 camelCase 的页面工厂——真实运行时 camel 键全 undefined；`status` 键两形状同名存活（读到 idle），blocker 才落在比特浏览器条，与截图逐字吻合。单测漏报因夹具手写 camelCase 绕过真实形状边界。
- **修复**：`localAgentStateFromStatus` 唯一映射源（service.js）＋ store/aggregate 复用；三行各说各话（`serviceText`/`bitbrowserText`）；文案白话化（未连接云端/未运行/未检测，blocker 去术语）。
- **走查发现 2（20010 文案 v1 遗留，`9d54203`）**：用户同机重复登录桌面端命中 20010 确认框——条件是「同 client_type 活跃会话存在」（`HasActiveSessionForClientType`，无设备维度；会话无过期机制，旧会话一直挂着），同机再登录也会命中，属阶段 1 设计语义。但两处文案是 v1 遗留：「已在其他位置登录」暗示另一台设备；「旧设备不能继续领取新的本地任务」在凭据解耦后**不成立**（执行由设备绑定决定，会话替换不夺权）。change.md 阶段 1「文案仍成立」的假设被走查证伪。两处文案已按 v2 语义改写。
- **验证**：web vitest 462 用例全绿（净增 5：夹具改真实线格式 + 接线用例 + 行语义用例）；双构建通过；变异对照（撤适配）6 例红证明判别力。读数见 [evidence/walkthrough-panel-false-alarm.md](evidence/walkthrough-panel-false-alarm.md)。
- **待复验**：重打 DMG 后面板应全绿；停比特浏览器应只落比特浏览器条 blocker 且本机服务行仍「已连接」；同机再登录的 20010 确认框显示新文案。

## 收尾（2026-10-02）

- **ADR**：`docs/decisions/0019-node-two-layer-and-device-scoped-credential.md`（node 两层拆分、凭据 = 设备绑定 + 未被取代、单实例互斥、落盘边界、按设备投递；Refines 0018，Supersede 其执行层 active-session 校验语义）。
- **双构建补齐**：`build:desktop` 收尾会话首次补跑通过（8.02s，仅既有 chunk 提示）；与已记录的 `build:cloud` 合为任务 5 的双构建。
- **全量重跑（对 `00028ac` 提交树）**：cloud `go build` + `go vet` + `go test -count=1 ./internal/...` 62 包 ok；web `vitest run` 49 文件 / 457 用例通过。
- **验收 grep 复核（带阳性对照）**：G1 `ClearMainIdentity|clearBitBrowserBinding` 代码 0 命中（对照 `91c58e5` 命中，模式有效；历史 handoff 叙述 1 处按「叙述判留」保留）；G2 `invalidated_at IS NULL` 仅剩 identity 会话层 4 处 + runtimebinding:75 注册票据闸门；G3 执行层 `n.session_id|JOIN user_sessions` 0 命中（对照 `11ce766` 命中 6 处，正是阶段 2 清理的文件）；G4 dedupe 键实测 device 维（`user_download|assetID|userID|deviceID|generation`）。读数详见 [evidence/closing-readings.md](evidence/closing-readings.md)。
- **跨仓提交落地**：cloud 阶段 3 `00028ac`（40 文件，含迁移 048）；阶段 1 `11ce766`、阶段 2 `91c58e5`（cloud）/`75860f7`（desktop）此前已提交；agent 无代码触点。workspace 侧本 checkpoint + ADR + evidence + CURRENT_CONTEXT 快照随收尾提交。
- **CURRENT_CONTEXT**：由 `scripts/prepare_ai_workspace.py` 重新生成（此前快照仍指向已归档的 072）。

## 阶段 3 完成（cloud / 前端，2026-10-02）

- **Item A — dedupe 维度 node→device**：`userDownloadDedupeKey` / `CreateUserDownloadTask` 去重键改为 `user_download|assetID|userID|deviceID|generation`，换设备重投递不再被旧设备去重键吞；latest-success 检查与 generation 计数都按设备算，同设备行为兼容（键哈希进 `CHAR(64)`）。
- **Item B — UnbindDevice 重分配**：解绑时把该设备名下 pending/running 的 `local_agent` 用户下载任务置 `cancelled` + `error_code='device_unbound'`（可重取），不再把文件投到错误机器；`TestUnbindDeviceMarksTheUnboundDevicesInflightDownloadsReclaimable` 钉住。
- **Item C — DownloadCentre 重取**：抽屉打开时取本机持久化 device_id（`local_device_identity`，仅 Desktop 运行时），新增 `canRetake` / `isSuspendedOnDevice` / `isReclaimableAfterUnbind` 纯函数并穿到行对象：
  - 悬置行（`pending` 且 `assigned_device_id` = 本机）→「重取」先取消（pending 无执行器、取消即终态）再走 `materials.createDownload`，去重 generation +1，新任务落在**当前**可信节点；
  - 可重取行（`cancelled` + `device_unbound`）→「重取」直接重新发起，设备维去重把换机后的点击当成新目的地——即验收路径「设备 A 领任务→解绑→设备 B 绑定后可重取」。
  - 重取与重新下载互斥（模板 `v-else-if`）；web 读不到本机，只有可重取一支成立。
- **Item D — profilebinding 用户自助「以当前环境为准」**：`POST /api/v1/bit-browser/main-identity`（`MainIdentityInput{main_user_id, overwrite}`）handler/service/dto/仓库已接线；PersonalInfoPage 设备卡新增「以当前环境为准」入口（读本机 Agent `main_user_id` + `overwrite=true` 确认），替代 admin-only `DELETE /api/v1/users/:user_id/bit-browser-main-identity`；init.js 23002 话术改为指向自助入口。admin 删除入口清理（handler/router/仓库函数 + usersApi/UsersPage 及相关测试）全部完成；`service_test.go` 两条引用旧函数 `ClearMainIdentity` 的测试由用户执行移交命令删除。
- **Item E — 契约 23002/23003**：`browser-profile.yaml`（23002）、`profile-guard.yaml` / `agent-runtime.yaml`（23003）补 `code:` 字段与语义注释；`browser-profiles.openapi.yaml` 补「环境确认」自助语义与 `overwrite` 字段；`file-transfer.openapi.yaml` 补「重投递」语义（设备维去重、解绑可重取、下载中心对悬置任务重取）。
- **验证（本会话，用户删除两条旧测试后全量复核）**：cloud `go build ./...`、`go vet ./internal/modules/profilebinding/...`、`go test -count=1 ./internal/...`（62 包全绿）；web `npx vitest run` 49 文件 / 457 测试通过；`npm run build:cloud` 构建成功（仅 chunk-size 警告）。验收 grep 全清：`ClearMainIdentity`/`clearBitBrowserBinding` 0 命中；执行层 `invalidated_at IS NULL` 仅剩注册闸门 `isSessionActive`（应有语义）；执行层 `session_id` 仅剩 `binding_tickets` 票据表。

## 阶段 2 完成（cloud / desktop / 前端，2026-10-02）

- **node 拆两层（契约 v2 核心）**：`local_agent_nodes` 去掉 `session_id` 列与外键（迁移 `20261002_047`），凭据有效 = device 绑定存在 + 节点在线，与会话无关；注册仍经票据 `session_id` 闸门（`isSessionActive` 保留）。
- **cloud 执行层去会话耦合（逐点枚举，非仅 runtimebinding）**：
  - `runtimebinding`：`authenticateCredential` / `FindTrustedLocalNode` / `CheckLocalTrust` 去掉 `invalidated_at IS NULL` / `IsSessionActive` / `JOIN user_sessions`（上一会话已完成，本轮验证）。
  - `cloudagent` heartbeat：移除「会话失效即 draining/replaced + 11001」的旧 v1 检查；`ErrSessionInvalid`（model/service/handler 三处）已死码删除。该 SQL 引用 `n.session_id`，迁移 047 落列后必炸——删除是正确性要求，不只是语义清理。
  - `profileguard` `acquirePermit`：`JOIN user_sessions` + `s.invalidated_at IS NULL` 移除；新增 sqlmock 阳性对照 `TestAcquirePermitRequiresOnlineNodeButNotALiveSession` 钉死无 session 的完整 SQL。
  - `identity`（`user_sessions` 归属）/ `profilebinding` 对 `local_agent_nodes` 的引用本就不涉 `session_id`，无需改动。
  - 残留 grep 全清：`n.session_id` / `JOIN user_sessions` 在执行层 0 命中；`invalidated_at IS NULL` 仅剩 identity 会话层与注册闸门（均为应有语义）。
- **Desktop 凭据落盘**：`RuntimeBindingState` 新增 `persist`/`restore` + `write_binding`/`read_binding`（temp+rename+0600，复用 device_identity 先例）；bind.rs 落盘、main.rs `.setup()` 恢复、agent.rs 过期注释修正。`RuntimeBinding::node_credential` 安全边界（diagnostic.rs:15）不变——永不进 Vue，0600 落盘与 device_identity.pk8 同级。
- **前端**：WorkEnvPill「重新同步本机环境」过渡入口移除（resync/syncing/按钮/import，死代码 `canBindTrustedNode` 分支不渲染）；`bindTrustedLocalAgent` 本体保留（init.js 预览与 PersonalInfoPage 仍用）。
- **契约**：`runtime-binding.openapi.yaml` 补 node 两层语义（info description），runtime-report 401 由「Node credential or bound session invalid.」改为「Node credential invalid (device unbound or node superseded).」。wire schema 未变，contracts.lock 不 bump（与阶段 1 同判）。
- **验证**：cloud `go build ./...` + vet + `go test`（cloudagent/profileguard/runtimebinding 全绿）；desktop `cargo test` 505 通过（新增 2 条持久化单测：回读 + 0600 权限、缺失/损坏文件视为无绑定）；web `vitest run` 448 通过。
- **待办**：跨仓提交（cloud / desktop / workspace checkpoint）尚未落地；实机走查（迁移 047 应用真库、Desktop 重启凭据存活、会话失效后 authenticate 仍过）待用户执行。

## 阶段 1 完成（wt-media-cloud `11ce766`，2026-10-02）

- `user_sessions` 新增 `client_type` 列（迁移 `20261002_046`，存量会话回填 `web`）。
- client_type 由服务端从 `Origin` 头推断（`tauri.localhost` → desktop，其余 → web），复用既有 `isLocalDesktopOrigin`；落库 `Session.ClientType`，**非客户端自报字段**（浏览器 Origin 为 forbidden header 不可伪造）。
- 登录替换只失效**同类型**旧会话（20010 仅同类型活跃会话存在时触发）；desktop 与 web 会话共存互不挤。
- `Logout` 改为只失效当前会话；用户停用/更新仍全量失效（安全动作，语义与登录替换不同）。
- 契约 `identity.openapi.yaml` 登录接口补充 client_type 推断语义。
- 单测：`go test ./internal/modules/identity/...` 全绿；新增登录矩阵（共存、同类型冲突、跨类型不冲突、Logout 只清自身）。
- 前端零改动（Origin 由 desktop webview 自动携带）。

## 下一步

- **重打 DMG + 面板复验**（先于其余走查）：刷新内嵌前端快照并重新打包安装；健康环境面板应「这台电脑可以工作」（正在这台电脑工作 / 已连接，当前无任务 / 已登录指定账号）；停比特浏览器应只落比特浏览器条 blocker、本机服务行仍「已连接」。
- **实机走查**（用户驱动，DONE 的前置）：迁移 046/047/048 已应用（用户确认）；剩余验 desktop 与 web 双会话共存不互挤、同类型才 20010、会话失效后凭据仍可 authenticate、Desktop 重启凭据仍在；阶段 3 走查「设备 A 领任务→解绑→设备 B 绑定后可重取」与「比特主账号切换后自助确认」、23002/23003 实发。走查结果记入 evidence，用户签收后按完成门关闭并归档。
- **待用户裁定（不阻塞走查）**：Level 级别定级（暂记 `L`）；`contracts.lock.json` 维持不 bump 的判断是否认可（wire schema 未变，见 ADR-0019 后果节）。

## 关闭（2026-10-03）

- **Completed**：阶段 1/2/3 与收尾全部落地并分仓提交——cloud `8a21041`（登录页自指重定向）、`86f4128`（扫描降频 + 胶囊取数/可见性）、`c33859d`（换节点重指）、`9732a07`（操作后刷新）；agent `b369d8f`（契约 `2026.10.03.1`）、`f7b8f11`（关闭期修掉的假红用例）；desktop `758f07e`、`0440d54`、`664f072`（发布链与「起飞」文案）。用户走查签收，未逐项给读数的项按 `change.md` §8.1 逐条标注覆盖。
- **Current**：无。记录已从 `delivery/active/` 与 `delivery/LEDGER.md` 移出，移入 `delivery/completed/CHG-20261002-074/`；`.ai/CURRENT_CONTEXT.md` 由 `prepare_ai_workspace.py` 再生为 `Active CHG: none` / `Status: NONE`。
- **Next**：无（本 CHG 不再有后续动作）。遗留各自归属，见 `change.md` §8.4：(a)(b) 是两处门禁/契约锁的账，与 (c) 一并归 [CHG-20261003-075](../../planned/CHG-20261003-075/change.md)；(d) 属 workspace 里不属本 CHG 的改动，留待归属方；(e) 归档记录的死链按只读边界不回改；(f) Level 定级待用户裁定；(g) 是 §6 两条的裁定结果。
- **Blocked**：无。关闭前登记的走查阻断项（登录页自指重定向）已修复并由用户走查通过；「胶囊每 30 秒真的带上 `scan=reuse`」因本环境打包 app 起不稳而未验，转遗留登记（`change.md` §8.2）。
- **Recent verification**（各仓末次代码改动之后重跑）：cloud `go build ./...` + `go vet ./internal/...` rc 0、`go test -count=1 ./internal/...` **62 包 ok / 0 FAIL**；cloud web `npx vitest run`（cwd `web/`）**50 文件 / 486 用例通过**；agent `bash scripts/test.sh` **Ran 688 tests / OK**；desktop `cargo test` **507 通过 / 0 失败 / 6 ignored**（静置机；改动的 6 个文件 `rustfmt --check --edition 2021` 全绿）；workspace `python3 -m unittest discover -s tests` **92 用例 / 3 红**（3 条均先于本 CHG 存在，逐条见 `change.md` §8.4 (a)/(b)）；`verify_delivery_governance.py` 与 `verify_product_master_alignment.py` **rc 0**。
- **一条假红的根因与修复（记在案）**：`test_reuse_serves_the_first_scan_to_the_second_request` 的原断言比较整个响应体，而 `data.disk.free_megabytes` 逐请求现测；churn 对照 8/8 红 → 修后 8/8 绿、变异对照仍红（详见 `change.md` §8.3）。同类但**未修**的 desktop 用例登记在 075。
