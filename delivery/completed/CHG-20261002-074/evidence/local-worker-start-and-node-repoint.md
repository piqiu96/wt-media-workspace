# CHG-20261002-074 取证：本地栈 worker 起停与换节点重指（2026-10-02）

起因：用户报「下载视频一直在排队」，要求确认两件事——worker 有没有在跑、`control.sh` 会不会自动带起 worker/scheduler。

## 两个提问的直接答案

1. **`control.sh` 不带 worker，也不带 scheduler。**（改动前实测：`scripts/m2b_local_acceptance.py` 只有 cloud 与 agent 两个组件）。已修 —— 见「改动 1」。
2. **worker 其实一直在跑**，但不是 harness 起的，`control.sh status/stop` 都看不见它。本文第一版取证给出的「worker 没跑」是**错的**；错法与机制记在下一节，因为同一条弯路很容易被下一个人重走。

## 第一次取证为什么得出错答案

用的是 `ps -eo pid,command | grep -i "wt-media"`。这个模式**不可能**匹配 `go run ./cmd/discovery-worker`（命令行里没有 `wt-media` 字样），也匹配不到它编译出的子进程 `/var/folders/…/go-build…/exe/discovery-worker`。换成 `grep -E "discovery-(worker|scheduler)"` 后进程立刻现形：

| 进程 | pid | 启动 | 归属 |
| --- | --- | --- | --- |
| `go run ./cmd/discovery-worker` | 67913 | Thu Oct 1 13:02:29 | 用户终端手起（父） |
| `…/exe/discovery-worker` | 67919 | Thu Oct 1 13:02:31 | 同一份（子，真正干活的） |

它在库里留下领用痕迹：`cloud-worker:aqiuyedeMacBook-Pro.local:67919:…`，最近一条 2026-10-02 10:46:22 —— 正是当时被我当作「最后一条日志」引用、却没往下推结论的那行 `material preparation … outcome=success`。

**可复用的教训**：判断「进程在不在」时，grep 模式要按**会被编译/包装改名的命令行**来写。模式对不上时得到的是空集，而空集看起来与「确实没跑」一模一样，不报错、也不会有墓碑。

## 改动 1：harness 带起 worker（workspace）

`scripts/m2b_local_acceptance.py`（`bin/control.sh` 的真身）：

- 新增 `start_worker()`，接在 `start_cloud()` 之后（`up` 与 `all` 两条序列都加）：先 `go build -o .cache/wt-media-discovery-worker ./cmd/discovery-worker`，再作为受管后台组件启动。
- **必须用构建出的二进制，不能用 `go run`** —— 同一次 `control.sh stop` 的输出就是判据：`cloud: stopped pid 12637 from pid file` 之后又有一行 `cloud: stopped pid 12641 on :18080`。pid 文件里记的是 `go run` 的父进程，真正监听的是它的子进程 12641；cloud 靠端口清扫把子进程补刀。**worker 没有端口**，`stop_started()` 只能按 pid 文件收，`go run` 形态必然漏成孤儿（CHG-20260930-069 已实测过 pid 42569 这种留存）。
- `cmd_status()` 扩成三行；worker 无 HTTP 端点，用 `health=pid-only url=-` 表达「只有 pid 可查」，仍计入总体健康。
- `stop_started()` 组件表加 `worker`，并在端口清扫后复核它真的退出（活着的 worker 会继续空转队列，而没有端口能再找到它）。
- `verify_worker()` 新增，接在 agent 之后；未运行时给出可操作的错误（指向 `bin/control.sh start`）。
- `bin/control.sh` 只动 `stop`/`status` 两行 usage 文字，**不引入任何数值参数**（`scripts/verify-control.sh` 机检这条）。
- **有意的裁剪：不起 `cmd/discovery-scheduler`。** 它按定时器入队新抓取（discovery-schedule 1m、proxy-expiry 6h），对本地下载链路无关，只给验收添噪声。要全量对齐是同一处三行改动。

## 改动 2：换节点时重指搁浅任务（`wt-media-cloud`）

根因（取证时确认，与 worker 无关）：队列里唯一非终态任务 `transfer_d6a52d8b7d65af4fa9000f4c` 是 `execution_scope=local_agent`，归桌面端 Agent 领，cloud worker 从不碰它；素材 160 已 `ready`、`dependency_task_id IS NULL`，也不需要 cloud 侧准备。它卡住是因为**节点换代**：任务 `assigned_node_id=agent-node_bd9f7477…`（20:51:11 注册，22:09:59 被标 `replaced`），在线节点是 `agent-node_227b8c31…`，而 `claimLocalTask` / `nextLocalTask` 都按 `assigned_node_id = <凭据里的节点>` 精确过滤。注册每次都铸新节点 id 并把旧节点标 `replaced`（今天库里已 9 条 replaced）；解绑路径早为这个洞写了注释（"would sit forever with no reachable terminal state"），注册路径没有对应处理。

修复：`internal/modules/runtimebinding/repository/store_mysql.go` 的 `saveNode`，在既有事务里、标 `replaced` 之后、INSERT 新节点之前，加一条 UPDATE，把该 user+device 名下仍在途的本地用户下载任务重指到新节点。范围照抄 `unbindDevice` 那条的形状（`requested_by` ∧ `purpose='user_download'` ∧ `execution_scope='local_agent'` ∧ `status IN ('pending','running')` ∧ 节点属于该 user+device）；**只动 `assigned_node_id`**，status / lease / claimed_by_node_id 一律不碰。

边界（写进注释）：只有 `file_transfer_tasks` 被处理。`sensitive_browser_tasks.node_id` 与 `browser_profile_runtime_presence.node_id` 同样引用节点 id，但那是派发现选节点的短生命周期行，语义不同 —— 本次不动，登记待裁定。

## 实测读数（本会话当场量）

| 项 | 命令 | 读数 | 判定 |
| --- | --- | --- | --- |
| 三行状态 | `bin/control.sh status` | `cloud: pid=18794 alive=yes health=ok` / `agent: pid=18813 alive=yes health=ok` / `worker: pid=18811 alive=yes health=pid-only url=-`，rc=0 | PASS |
| 无孤儿停止 | `bin/control.sh stop` | 受管 worker 17489 `stopped pid … from pid file`；停止后 `ps` 只剩用户手起的 67913/67919（无 pid 文件，本就不归它管） | PASS |
| worker 真在轮询 | 连接归属 + 语句计数 | `information_schema.processlist` 的 528/529/530 ↔ `lsof` 端口 51939/51941/51942 ↔ **pid 18546**；20s 内语句计数 1460→1478、203→215 递增 | PASS |
| `verify_worker` 有判别力 | kill 受管 worker → `bin/control.sh verify` | `ERROR: Cloud worker: not running (pid file …)`，rc=1；重启后 `Cloud worker: PASS pid=18811` | PASS |
| cloud 全量 | `go build ./...` / `go vet ./...` / `go test -count=1 ./internal/...` | build rc=0、vet rc=0；**62 ok / 0 FAIL / 7 no-test-files = 69 包** | PASS |
| 变异对照（撤新 UPDATE） | `go test -run TestRegisteringForADeviceRePointsItsInflightDownloadsAtTheNewNode` | 撤掉 → `FAIL`（INSERT 落到了本该是 UPDATE 的位置）；还原 → `ok` | PASS |
| 新谓词对着真库 | 把新 UPDATE 的 WHERE 原样跑成 SELECT（只读） | 恰好命中 1 行 —— 就是那条搁浅任务 | PASS |
| `bin/control.sh` 入口 | `scripts/verify-control.sh` | `PASS … status wiring (cloud/agent/worker), and no-port-literal` | PASS |

**未达成的一项，说明清楚**：计划里「`job.log` 从停滞开始出新行」这条**不成立**，因为 worker 起来了但库里没有 cloud 维的在途工作（唯一那条是 `local_agent` 维），轮询空转不留行。所以这一段能得出的结论只是「**worker 起来了**」，不是「下载修好了」——本地下载当时仍不会跑，原因见「阻塞 2」。

### 执行器开关与刷新修复之后的读数（同一批命令在**最后一次改动之后**重跑）

| 项 | 命令 | 读数 | 判定 |
| --- | --- | --- | --- |
| Desktop 全量 | `cargo test`（`wt-media-desktop`） | **506 passed / 0 failed / 6 ignored**（改动前 505，+1 = 新断言） | PASS |
| Desktop 格式 | `rustfmt`（**只对改动的单个文件**；该仓不是 rustfmt-clean 的，全仓 `cargo fmt` 会重排 16 个文件） | 无 diff | PASS |
| 前端全量 | `npm run test`（在 `web/` 下跑，仓根跑会把 Vite root 变仓根） | **49 文件 / 480 用例全过**（改动前 476，+4） | PASS |
| 前端双构建 | `npm run build:cloud` / `npm run build:desktop` | 两次 `✓ built` | PASS |
| cloud 重测 | `go build ./...` / `go vet ./...` / `go test -count=1 ./internal/...` | build rc=0、vet rc=0；**62 ok / 0 FAIL**（与本文改动前一致——本轮未再动 Go 码） | PASS |
| 开关真的进包 | 重打后 `launch-dmg`，查 sidecar 进程 env | `WT_MEDIA_AGENT_RUN_RUNNER=true` **且无任何 export** | PASS |
| 变异对照（前端三处） | 逐个撤掉修复 → 跑对应用例 | 撤 → 红；还原 → 绿 | PASS |


## 阻塞 1（已修，但**不是根因**）：DMG 缺 `sidecar-manifest.json`

这个环境里当时**没有本地执行者**：DMG 版拒绝启动自带 sidecar（`Contents/Resources/sidecar-manifest.json` 不存在，而 `integrity.rs` 的判定表里「在 bundle 里 + 有 sidecar + 无记录 = 拒绝」），桌面日志 21:52 起满屏「包内缺少记录文件」；回退的 `python3 -m wt_media_agent.local_api.server` 只起本地 API、不跑任务循环。实测 `file-transfer-tasks/claim` 最后一次出现在 `logs/access.log` 是 **10:24:54**，之后零请求。

### 更正：本文第一版把这一条写成了根因，**错了**

`build_dmg()`（本文档所在会话的后半段）把记录文件补上并重打后，**真 sidecar 确实起来了**（`ps` 显示 `dmg-mount/起飞.app/Contents/MacOS/wt-media-agent`，pid 23819/23821），可 `claim` 计数**仍是零**。所以 manifest 是**必要不充分**条件 —— 补它不是修好了，只是让下一层的原因露出来。修法见「阻塞 2」。

### 更正：`runtime-report` 不是 sidecar 在发

本文第一版写「心跳仍新」时默认那是 Agent 在报活。实际是 **Desktop 的 Rust 客户端**在发（[preflight.rs:217](../../../../../wt-media-desktop/src-tauri/src/preflight.rs#L217) 的 `runtime-report` 调用）；Agent 自己的 `report_runtime` 是死代码。**所以「节点 online」只证明 Desktop 活着，不证明 Agent 会干活** —— 这一条正是本文档前半段所有绿灯都没能拦住问题留在队列里的原因。

## 阻塞 2（根因）：安装包里**从来没有执行器**

Agent 的领取循环整段挂在 `config.run_runner` 后面（[bootstrap/sidecar.py:18](../../../../../wt-media-agent/src/wt_media_agent/bootstrap/sidecar.py#L18) 的 `if config.run_runner: start_task_loops(...)`），该字段默认 `false`（[runtime/config.py:186](../../../../../wt-media-agent/src/wt_media_agent/runtime/config.py#L186)），而 Desktop 交给 sidecar 的环境变量**只有** host/port/token/data_dir 四项 —— `environment()` 里没有这一条，`git log --all -S RUN_RUNNER` 在 desktop 仓**任何提交里都是空**。随包 config 的注释却写着「The acceptance scripts and Desktop turn it on」：**Desktop 那一半从未实现**。

结论：**正式安装包从未能执行过任何下载。** 历史上跑通的每一次都是命令行手起一个带 `WT_MEDIA_AGENT_RUN_RUNNER=true` 的 Agent（CHG-069 checkpoint:57 记的正是这个绕法）。

### 阳性对照（先于产品改动，用**未改**的 app 做）

`environment()` 是**加入**继承环境而非替换（mod.rs 注释明写），所以：

```
open -n -a <未改的包> --env WT_MEDIA_AGENT_RUN_RUNNER=true
```

sidecar 继承该变量 → 10:24:54 之后**第一次** claim 出现在 **23:44:17** → 任务 `transfer_040b010887bb307cc5d64d8b` running（attempt 1）→ **23:46:09 success**，162200269/162200269 字节；落盘 `/tmp/wt-media-m4a-acceptance/20261002/三角洲-160-….mp4` 恰好 162200269 字节。这一读把「变量就是那个开关」钉死，而不是靠改动后「反正好了」。

### 产品改动后（不再 export）

改动在 `wt-media-desktop/src-tauri/src/sidecar/mod.rs` 的 `environment()` 加一对 `WT_MEDIA_AGENT_RUN_RUNNER=true`，并补一条先红后绿的断言（`the_agent_is_told_to_run_its_task_loops`，同文件既有 `vars.len()` 断言 3→4）。重打 DMG 后 `launch-dmg`：sidecar 的 env 里有该变量**而无需任何 export**，claim 每 5s 一次。有界验证：素材 161 的 `transfer_a855af3c7bad3fdbe421383f` 在活节点上跑起来、字节爬到约 81MB 后由 API 取消。

**最终包（含前端刷新修复的那次重打，23:57）**：`launch-dmg` 后 sidecar pid 30941/30944，`WT_MEDIA_AGENT_RUN_RUNNER=true`（只查这一个变量，不打印同进程的凭据）；`claim` 在 `logs/access.log` 连续 200，时间戳 23:59:56 / 00:00:01 / 00:00:06，间隔 5s。同一份 `.generated/frontend` 里也确认了前端修复真的进了包：`MaterialDetailDrawer-*.js` 有 `"cancel"`，`MyMaterialsPage-*.js` 有 `onCancel`（阳性对照 `onGiveUp` 同时在，未绑定的键 0 命中）。

### 最终包上的一条完整端到端（无任何手起 Agent、无 export）

走 API 发起（`POST /api/v1/materials/161/downloads`，登录用 200 返回的 `wt_media_session` HttpOnly cookie），然后只读库：

| 时刻 | 读数 |
| --- | --- |
| 00:01 | `transfer_0b009a09b140281e379d5db0` created，`pending`，`assigned_device_id=9b4f2a3d…` |
| 00:02–00:06 | `running`，`claimed_by_node_id=agent-node_227b8c31…`（**当前**节点），字节 19MB → 490MB 单调爬升 |
| **00:07:27** | **`success` 495383052/495383052** |

落盘 `stat` 复核：`/tmp/wt-media-m4a-acceptance/20261003/三角洲-161-…mp4` 恰好 **495383052** 字节；同目录 23:46 那份素材 160 也是 **162200269** 字节，与 `materials.video_size_bytes` 逐字节相符。

**这一条是本轮唯一能写成「安装包能下载了」的判据** —— 前几条（对照里的 23:44–23:46 成功、有界验证的 81MB 后取消）都还带着 export 或半途而止。

**边界**：`FALLBACK_ARGS` 的 python 回退拿到这个变量也**不会**领任务 —— `local_api.server` 从不调 `start_task_loops`。回退本就是降级态、只服务状态查询，这是对的；写进该函数的注释，免得下一个人以为它被顺手修好了。

## 搁浅行怎么解锁的

那条指向已取代节点的行（`assigned_node_id=agent-node_bd9f7477…`）**没有手工改库**。用户自己在 23:40:40–23:40:56 点了「重取」（先 cancel 再 createDownload），搁浅行被取消、新任务落在**当前**可信节点上 —— 说明重取这条路径是通的，缺的自始至终只有执行器。

## 附带修复：操作后页面不刷新（用户中途报障）

原话：「点击取消 点击下载 重试 等操作，页面不会刷新需要手动刷新才能看到状态更新」。逐条读源后确认是三处**互相独立**的漏刷：

1. [MyMaterialsPage.vue](../../../../../wt-media-cloud/web/src/modules/materials/pages/MyMaterialsPage.vue) 的 `download()` 发完请求**从不重读**——而这一行的「文件状态」和按钮都由使用记录算出，不重读就停在上一帧，看起来像没反应。改为 `await client.createDownload(...)` 后 `await load()`。
2. [DownloadCentreDrawer.vue](../../../../../wt-media-cloud/web/src/modules/transfer/DownloadCentreDrawer.vue) 从「历史」再打开时，原先把 `activeTab` 切回「进行中」就 `return`，理由是「切 Tab 会触发 watcher」——但那个 watcher **只重估轮询闸门、不取数**，闸门又依赖已缓存的列表。于是关闭期间新发起的下载在面板里根本不存在。改为切回后**照样自己 `load()`**。
3. [MaterialDetailDrawer.vue](../../../../../wt-media-cloud/web/src/modules/materials/MaterialDetailDrawer.vue) 的 `cancelDownload` 只重读抽屉自己的几份 ref，宿主列表那一行不跟着变。新增 `cancel` 事件 + 宿主 `@cancel="load"`。

三条各配一条源串断言（本仓既有风格），并做变异对照：撤掉改动 → 用例变红；还原 → 绿。**第一次对照是假绿**：`-t` 过滤传的是注释片段而非真用例名，没有用例匹配，检测器把「没跑」读成了绿；换成真名后为红。测试总数 476 → **480 全过**。

## 未决

- **重复 worker**：已消失，无需处理。复查时进程表里只剩受管的 `22591`（本检出 `.cache/`），用户手起的 `67913`/`67919` 已不在；同一条 pattern 仍能看到 `22591`，所以「没找到」不是模式写错。受管 worker 的 `runWorkerProcess()` 同时注册 `discovery-worker` / `material-prepare-worker` / `transfer-reconcile` 三个循环，手起那份消失后没有留下空档。
- **搁浅任务的兜底**：改动 2 上线后（已编译进当前运行的本地 cloud），下次该设备注册即自动重指。**但它只在「注册」那一刻生效**：Desktop 现在会持久化并恢复节点凭据，重登不再重新注册 —— 所以它修的是「往后每次换代」，修不了**已经**搁浅的行。已在途的仍靠下载中心「重取」（先取消再发起）。**不手工改 `assigned_node_id`**。
- **`sensitive_browser_tasks` / `browser_profile_runtime_presence` 的同类搁浅**：登记待裁定（见改动 2 边界）。
- ~~**同类「文档写了、实现没做」第二例**~~ **已撤回**：上一版此处写「`sidecar/mod.rs` 同一段注释还声称 Desktop 会按启动传 `WT_MEDIA_AGENT_ID`」——**这句话不成立**。该段注释的原话只说这些名字是 Agent 的、由 `runtime/config.py` 的字段表声明，全文没有这个变量名。`git grep WT_MEDIA_AGENT_ID` 在 desktop 仓为 **0 命中**（阳性对照：同一命令查 `WT_MEDIA_AGENT_RUN_RUNNER` 得到 2 命中，所以不是模式写错）。如实的事实是：Desktop 不传它，于是每台机器上由 Desktop 启动的 Agent 都自称 `local-agent-dev`（`runtime/config.py:180` 的字段默认值），而**节点身份**是注册时由 device_id 生成的 `agent-node_<hash>`。实测库里各节点的 `agent_id` 都是该默认值，**无任何可观察后果**，属诊断显示字段。**不修代码**。
- **环境类发现挂在哪**：已裁定——`run_runner` 开关、manifest、report 归属、本条撤回后的结论，全部继续挂在 CHG-074 名下，不另立条目。

## 后续（2026-10-03）：比特浏览器扫描降频

用户的「自动刷新请求比特浏览器列表改成 5 分钟」做成了 **Agent 侧 `?scan=reuse` 缓存（TTL 300 s），默认仍实时**，只给胶囊的后台 tick 用。实机判据、覆盖边界（打包 app 起不来 → 胶囊那条路径未实机验证）与另一处新发现（发布脚本硬编码 `WT Media.app`、与 `productName: 起飞` 不符，整条链跑不出 DMG 且静默失败）见 checkpoint 同名小节。
