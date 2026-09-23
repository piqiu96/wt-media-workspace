# D-scheduler 修复与进程级复验

- 日期：2026-09-23
- 被验代码：Cloud 修复提交 `b7f13c3`（`defaultSchedulerDiscoveryService`），基于冻结修订 `aaf66c5` + 本修复
- 关联：`12-defects-and-security.md` 的 D-scheduler；`14-verdict.md` 验收项 2
- 原始证据：`raw/p15-dscheduler-process-observation.txt`（interval 形态）、`raw/p16-daily-schedule-observation.txt`（daily 形态）、`raw/p15-worker-log-excerpt.txt`

## 一、根因（由 git 历史确认：未收尾的迁移遗留）

| 阶段 | 提交 | 内容 |
| --- | --- | --- |
| 拆分前 | `0699e8a^` | **单进程**：`internal/app/app.go:96-98` 同时起 HTTP 与 `scheduler.StartDiscoveryScheduler(...)`，用的是 `NewDouyinCrawlerFromEnv()` |
| ↓ | `4720fc5` / `d514000` | 该 crawler **自带字段**（`base`/`apiKey`/`cookie`），从配置自读，**完全不碰 `douyinclient` 全局**。原始源码注释即设计意图：「Credentials are deliberately absent: adapters read them only from the server runtime.」 |
| **拆成 3 个 CMD** | `0699e8a` | 引入全局单例生命周期（`Initialize`/`Get`/`Close`）。**同一提交内自相矛盾**：① `schedulerResourcePlan()` 不含 clients，并新增 `TestInitializeSchedulerDoesNotInitializeDouyinClient` 把它**锁定为预期**；② `runSchedulerProcess` 却用全局版 `NewDouyinCrawler()` 构造 service。worker 的 plan **补了** `clientsResource("douyin")`，调度这份**没补** |
| 收尾 | `100899d` | **删除** `NewDouyinCrawlerFromEnv`，把 service 构造从进程启动挪进 job 体内（`jobs.RunDiscoverySchedule(ctx)` → `service.RunDue` → `defaultDiscoveryService()`）。panic 由「启动即崩」变为「首个 tick 在裸 goroutine 内崩」 |

**定性：不是「漏了一行」，是把「自读配置的 crawler」换成「生命周期管理的单例 client」时，
server 与 worker 都补上了 `clientsResource()`，唯独调度路径漏补**；而漏掉的那半在同一提交里
被一个测试认证为「本来就该没有 client」。两边从未对齐，故该 CMD 自诞生起**一次都没成功运行过**
——与上一轮验收发现「历史上从未有任务拥有非空 `schedule_key`」一致。

### `douyinclient.Get()` 为何 panic

`Get()`（`internal/infra/client/platforms/douyin/client.go:68-76`）签名是 `func Get() *Client`，
**无 error 可返回**，因此「生命周期未跑」这一编程错误只能以 `panic` 表达
（`panic("douyin: Get called before Initialize")` 在 `:73`）。`Initialize`（`:55-64`）把客户端发布到
包级全局，`Close`（`:79-85`）清空；**`Initialize` 对空凭据不报错**，故空凭据不是 panic 原因。

致命点在于它是 `defaultDiscoveryService()` 的**实参**（`store_adapter.go:83`），panic 落在
**构造期**，早于任何 error 返回；再叠加 `internal/`+`pkg/` 全仓**零 `recover()`**，
且 `scheduler.runPeriodically`（`internal/scheduler/scheduler.go:63`）以 `_ = item.run(ctx)`
在裸 goroutine 中调用 → 整进程退出，并带走同进程的 `proxy-expiry` job。

### 爆炸半径（已全仓排查）

- `cmd/discovery-scheduler` 只注册 `discovery-schedule`（panic）与 `proxy-expiry` 两个 job。
  `proxy-expiry` → `proxy/service.MarkExpiringProxies` 全程只触碰 `database.DB()` 与 `logger`，
  两者都在 scheduler 计划内 → **该进程内只有这一处 panic，无第二颗同型雷**。
- 代码库本就预期「无 crawler 的 service」：`runDue` 从不解引用 `s.crawler`；`runNext` 已有 nil 守卫
  （`discovery.go:289`）；`douyinCrawler.Discover` 已防御性返回 `ErrCrawlerUnavailable`；
  `TestRunDueUsesStrategyTimezone` 构造 service 时不传 crawler 并断言 `calls == 0`。
  即：唯一致命点是构造期那一次急切的 `Get()`，它让这些防御全成死代码。

## 二、修法（用户 2026-09-23 裁定）

用户裁定：「**scheduler 只是扫库做任务调度，不需要依赖这些额外的 client**」。
故**不采纳**上一轮验收报告建议的「给 `schedulerResourcePlan()` 补 `clientsResource()`」
（那会与 ADR-0015 第 3 条及 `4720fc5` 的原始设计意图相悖），改为让调度路径不再持有 crawler。

Cloud 改动（3 行生产代码 + 测试）：

| 文件 | 改动 |
| --- | --- |
| `internal/modules/contentpool/service/store_adapter.go` | 新增 `defaultSchedulerDiscoveryService()`：以 `nil` crawler 构造 |
| `internal/modules/contentpool/service/operations.go:61` | `RunDue` 改走该工厂（`RunNext` 及其余包装函数不动） |
| `internal/modules/contentpool/service/discovery_test.go` | 新增 `TestSchedulerDiscoveryServiceCarriesNoCrawler`、`TestRunDueNeverCrawls` |
| `internal/bootstrap/bootstrap_test.go` | 在既有测试上补注释，指明两处不变量必须同时成立 |

**明确保留**：`schedulerResourcePlan()` 与其测试原样不动——它们表达的正是上述原则。

### 修复可证性

- 在**同一个测试二进制**内验证：修复前的接线 `defaultDiscoveryService()` 确实 panic
  （`recovered: douyin: Get called before Initialize`）——该临时探针用后即删，未留在仓库。
- `go build ./...` 通过；`go test ./...` **57 包 ok、0 FAIL**；
  触及包 `contentpool/service`、`bootstrap`、`jobs` 全通过。

## 三、进程级复验

两次复验**均未启动 HTTP server**、**均未调用管理员 `run-due` 端点** → 下列任务只可能来自
调度进程自身的 tick，即真正的**无人值守**触发。

### 三.1 `interval:N` 形态（`raw/p15-*.txt`）

| 时刻 | 观测 |
| --- | --- |
| 13:20:23 | 启动 `cmd/discovery-scheduler`（PID 50129）；启动前基线 `max_task_id=84 / total=62 / with_key=3` |
| 13:20:52 | 存活 29 秒；`scheduler.log` **0 字节**（修复前此处 panic 后 exit 2）；首个 tick 即入队 85、86（`interval:5:5967136`，**pending**） |
| 13:22:44 | 存活 2 分 21 秒，跨 **3 个 tick**（`discovery_interval=1m`）；日志仍 0 字节；tick2/tick3 **未新增任何行**（距上次不足 5 分钟）→ 同窗口防重成立；`HAVING c>1` 为空 |
| 13:25:24 | 距上次满 5 分钟，无人干预下再各入队 1 行（87、88） |
| 约 13:25:35 | 由本次复验主动 `pkill` 停止（存活约 5 分 10 秒、跨 ≥6 tick）。背景任务回报的 exit 144 **即此次 pkill**，非进程自身退出；判据是日志全程 0 字节 |
| 13:27:39 起 | 启动独立 `cmd/discovery-worker`：领取 4 个任务，**写入 `started_at`/`finished_at`**，终态全部 `success` |
| 13:29:24 | 收尾；两进程已停止，无残留 |

### 三.2 `daily HH:MM` 形态（`raw/p16-*.txt`，同日追加补验）

**为什么要补**：三.1 只覆盖 `interval:N`。回查发现全库 `schedule_key LIKE 'daily:%'` 历史为
**0 条**（p15 轮次产生的 3 条也全是 `interval:`），而**在册生产策略 id=2「三角洲热点」用的正是
`daily 09:00`**。两者走**不同的 due 判定**（`discovery.go:752-783`），interval 的证据覆盖不到 daily：

| schedule | `scheduleDue` | `sameScheduleWindow` | 实际生效条件 |
| --- | --- | --- | --- |
| `interval:N` | 恒 `true` | `now-created < N min` → 跳过 | 距上次满 N 分钟 |
| `daily HH:MM` | 仅 `hour==now.Hour() && minute==now.Minute()` 那一分钟为 `true` | 同一日历日 → 跳过 | tick 恰好落进那一分钟，且当天未跑过 |

**样本**：镜像既有验收策略 id=10 的字段形状，插入 1 条 `id=37`、`schedule='daily 13:57'`、
`timezone='Asia/Shanghai'`、`enabled` 的 keyword 策略（本地库仅插入，属授权内）。
本机本地时区 = CST+0800 = `Asia/Shanghai`，shell 时刻与策略时区同一参照。

tick 网格锚定进程启动秒 `:50` → 到期 tick = **13:57:50**。

| 时刻 | 观测 |
| --- | --- |
| 13:52:38 | 基线：`daily:` 前缀任务 **0 条**；`max_id=88 / total=66 / with_key=7` |
| 13:52:50 | 启动调度进程（PID 52372） |
| 13:56:47 | 存活 3:57，已跨约 4 tick；**策略 37 行数 = 0**；日志 0 字节 |
| **13:57:30** | **到期 tick 前 20 秒**：策略 37 **仍为 0 行** → 「没到点不插」成立，且非「先插后回滚」 |
| 13:58:10 | 到期 tick（13:57:50）之后：**恰好 1 行** —— `id=91`、`schedule_key='daily:2026-09-23:13:57'`、`pending`、`created_at=13:57:51.824909` |
| 14:01:00 | 同日后续 tick（含跨入下一分钟/下一窗口）：**仍为 1 行** → daily 的「同一日历日」窗口防重成立 |
| 14:01:21 | 存活 **8 分 31 秒**、跨约 **9 个 tick**、日志全程 **0 字节**；由本次复验主动 `pkill` 冻结现场 |
| 14:01:29 起 | 启动独立 worker，5 条待执行任务在 29 秒内排空 |
| 14:02:03 | 任务 91 终态 `success`，`started_at=14:01:39.675`/`finished_at=14:01:46.092` 由 worker 写入；`stats_json.added=19` 与库内 19 行**精确一致** |
| 14:02:11 | 收尾；两进程已停止，无残留 |

**同一次扫描的旁证**：该 tick 内 `id=91`（daily）的创建时刻 `13:57:51.824909` 夹在
`id=92`（interval，`.880008`）与 `id=93`（interval，`.916081`）之间 → daily 与 interval 是在
**同一次 `runDue` 扫描**中被判定的，daily 未走旁路。

**上游真实性**：worker 日志 1021807 字节，含 70 处真实唯一键冲突
（`uq_source_contents_team_platform_content`，如 `2-douyin-7688444829000691685`）与真实标题
（如「S44赛季定榜之夜… #王者荣耀」）→ 19 行为真实上游读回，非构造数据。

### 三.3 覆盖范围声明（本轮两种形态各自被什么证据覆盖）

| schedule 形态 | 证据 | 覆盖内容 |
| --- | --- | --- |
| `interval:N` | 三.1 / `p15` | 到期 tick 入队、未到期不重复入队、跨窗口再触发、Worker 执行与内容池读回 |
| `daily HH:MM` | 三.2 / `p16` | 到期前不插、到期那一分钟恰好插 1 行、`schedule_key` 形态正确、同日不再重复入队、Worker 执行与内容池读回 |
| `manual` | 不在调度范围（`scheduleDue` 恒 false），由人工「立即执行」入口覆盖，非本轮对象 | — |
| 非法 `schedule`（如 `garbage`） | 不在本轮范围；`scheduleDue` 返回 false，另见缺陷 **D2**（无服务端校验） | — |

即：**两种周期触发形态（`interval:N`、`daily HH:MM`）在无人值守路径上均已端到端成立**。

### 三.4 与上一轮 6.2 的对照

| | 上一轮（`aaf66c5`，未修） | 本轮（修复后） |
| --- | --- | --- |
| 6.2 独立调度进程存活 | **存活=False，exit=2**，`panic: douyin: Get called before Initialize` | **存活=True**，跨 ≥6 tick（p15）/ ≥9 tick（p16），日志全程 0 字节 |
| 周期触发执行者 | 不存在（只能靠管理员 `run-due` 顶替） | **存在**：调度进程自身按窗口入队，Worker 领取执行 |
| `interval:N` 无人值守触发 | 未交付 | 成立（85–88） |
| `daily HH:MM` 无人值守触发 | 未交付（历史 0 条） | 成立（91） |

## 四、本轮**未**做（如实声明）

1. **未复跑管理员 `run-due` 的防重子项**（上一轮 6.6/6.7）。理由：该端点需管理员登录，
   而登录会顶替用户浏览器中的既有会话；且其代码路径（`runDue`/`createRun`）本次**未被修改**
   （改动只是「谁来构造 service」），无回归面。**替代证据更强**：本轮以**无人值守路径**证明了
   两种形态的防重（interval 同窗口不重复、daily 同日不重复），上一轮用 `run-due` 证明的正是同一条防重逻辑。
2. **未修 D8**（`ErrCrawlerUnavailable` 未在 `writeDiscoveryError` 映射）：按用户裁定保持最小改动，
   仍登记不修。
3. **未做 Desktop 视觉走查**；验收项 7 的「部分通过」结论不受本轮影响。
4. **未修 D1/D2/D3/D6/D9/D10**；未动 `config/credentials/douyin.toml`；未清理 git 历史。

### 本轮新登记（只登记，不修，交用户裁定）

- **daily 漏 tick 即丢当天**：`scheduleDue` 要求 tick 落在 `HH:MM` 那一分钟内，且该形态无补偿机制
  —— 调度进程若在该分钟不在跑（或漏了一次 tick），当天即无任务，且不会在后续 tick 补触发。
  这是既有设计、非本次修复引入；是否补一个「当天未跑则补触发」的兜底，另立处置。
- **样本策略 id=37 是补验用的一次性样本**，未删除（沿用阶段 11「残留不删除」口径），见第六节。

## 五、安全复查（沿用 S-2 纪律）

用**真实凭据值反查**全部证据文件：

- `config/credentials/douyin.toml` 的 `api_key`（35 字符）与 `cookie`（6975 字符）：**无任何文件命中**；
- cookie 的前 120 / 后 120 字符片段：**无命中**（排除截断残留）；
- 活会话令牌样式（`wt_media_session=<16+ 位>`）：**无命中**；
- `cookies/` 目录仍不存在。
- 本轮新增的 `p16` 原始证据与 `15`/`12`/`14` 回写同样无凭据值。**结论：证据中不含凭据值。**

## 六、残留登记（不删除，沿用阶段 11 口径）

`11-residue-teardown.md` 是**首轮验收**的渲染产物（基线 3 策略/11 任务/109 来源/26 素材）。
以下为两轮复验新增的残留，叠加即为当前全量：

| 表 | p15 轮新增 | p16 轮新增 | 合计 |
| --- | --- | --- | --- |
| `crawl_tasks` | 4 行：85、86、87、88（带 key，全 `success`） | 5 行：89、90、91、92、93（带 key，全 `success`） | 9 行 |
| `source_contents` | 25 行（task 85–88） | 30 行（task 89–93） | 55 行 |
| `discovery_strategies` | 0（复用既有策略 10、29） | **1 行：id=37**（daily 补验样本） | 1 行 |
| `materials` | 0 | 0 | 0 |
| `operation_teams` / `users` | 0 | 0 | 0 |

**不变式**：两轮复验**均未修改、未删除任何既有行**。
`WHERE id<=88` 的 66 条任务（含 7 条带 key）在 p16 轮前后一致；p15 轮的启动前基线
`max_task_id=84 / total=62 / with_key=3` 亦保持不变。全库现状：`total=71 max_id=93
daily_rows=1 interval_rows=11`。
无残留进程：收尾后仅剩复验前即在运行的 Desktop 外壳与 Agent `local_api:8765`。

**残留周期策略已于同日停用（2026-09-23，见第八节）**：上表 `discovery_strategies` 的 1 行
（id=37）与更早验收遗留的 id=9、10、29 一并由 `enabled` 改为 `disabled`；行本身未删除。

## 七、对验收项 2 的结论

验收项 2（关键词策略真实周期触发 → 任务 → 执行 → 自动入池）的**唯一阻断点已消除**，
且以**无人值守**路径端到端复现，**两种周期触发形态均被覆盖**：

| 形态 | 无人值守入队 | Worker 执行 | 内容池真实读回 | 防重 |
| --- | --- | --- | --- | --- |
| `interval:N` | 85、86（13:20:23）、87、88（13:25:24） | 全部 `success` | 25 行 == `added` 合计 25 | 同窗口不重复（tick2/3 无新增） |
| `daily HH:MM` | 91（13:57:51，`daily:2026-09-23:13:57`） | `success` | 19 行 == `added` 19 | 同日不重复（14:01:00 仍 1 行） |

- 判定：**复验通过**（原判定「不通过」基于修复前的 `aaf66c5`，本轮修复后重取证据）。
- **覆盖范围**：`interval:N` 与 `daily HH:MM` 成立；`manual` 不在调度范围；非法 `schedule`
  的服务端校验缺失另属缺陷 D2，不影响本项判定。
- 这是**对已执行验收轮的复验补证**，不是重开签收；**M3 状态保持 `IN_PROGRESS`，未标 DONE**。

## 八、收尾确认（2026-09-23，用户裁定闭环）

用户 2026-09-23 裁定：**「直接都停用，当前我可以收尾认为 scheduler 修复已完成」**。

### 8.1 停用残留周期策略

停用前的判定依据：**`status='enabled'` 且 `schedule <> 'manual'`** 的策略才会真正被调度触发
（`discovery.go:581` 以 `strategy.Status != model.StrategyEnabled` 短路，`scheduleDue` 对
`manual` 恒返回 false）。该集合共 5 条：

| id | team | name | schedule | 定性 | 处置 |
| --- | --- | --- | --- | --- | --- |
| 2 | 1 | 三角洲热点 | `daily 09:00` | **真实业务策略** | **未改动**（保留 enabled） |
| 9 | 2 | m3acc0923-周期触发-daily 05:33 | `daily 05:33` | 验收残留 | → `disabled` |
| 10 | 2 | m3acc0923-周期调度-interval5 | `interval:5` | 验收残留 | → `disabled` |
| 29 | 2 | m3acc0923-周期调度-interval5-061451 | `interval:5` | 验收残留 | → `disabled` |
| 37 | 2 | m3acc0923-周期触发-daily1357 | `daily 13:57` | 本轮补验样本 | → `disabled` |

执行：`UPDATE ... SET status='disabled' WHERE id IN (9,10,29,37) AND status='enabled'
AND name LIKE 'm3acc0923-%'`（行未删除，沿用阶段 11「残留不删除」口径）。
**id=2 未被触及**（`updated_at` 仍为 2026-09-22 20:27:08，早于本次操作，可作佐证）。

> 注：首轮汇报残留时只列了 10、29、37，**漏报了同为残留且会触发的 id=9**（`daily 05:33`）。
> 本轮按同一口径一并停用。此处如实记录该遗漏。

### 8.2 停用生效的进程级确认

以同一调度二进制再起一次，确认停用后不再产生任务：

| 时刻 | 观测 |
| --- | --- |
| 14:11:11 | 基线 `max_id=93 / total=71`；启动调度进程（PID 53652） |
| 14:12:34 | 存活 **1 分 23 秒**、跨 ≥2 个 tick、`scheduler2.log` **0 字节** |
| 14:12:34 | `max_id=93 / total=71`，**`id>93` 计数 = 0** → 无任何新增任务 |
| 14:12:35 | 主动 `pkill` 停止，无残留进程 |

即：残留策略停用后，调度进程照常存活但**不再入队**（`status != enabled` 被短路）；
在册唯一还会周期触发的是真实业务策略 id=2。

### 8.3 闭环判定

- **D-scheduler：已修复、已复验（`interval:N` + `daily HH:MM`）、残留已停用 → 用户确认闭环。**
- **D-scheduler-2（daily 漏 tick 即丢当天）：仍为「已登记、未修」**，闭环不覆盖该项；
  是否补「当天未跑则补触发」的兜底仍待用户裁定。
- 本闭环**不构成 M3 签收**：`M3` 保持 `IN_PROGRESS`，`CHG-20260915-051` 未激活。
