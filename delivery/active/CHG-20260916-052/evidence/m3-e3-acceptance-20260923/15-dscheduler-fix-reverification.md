# D-scheduler 修复与进程级复验

- 日期：2026-09-23
- 被验代码：Cloud 工作树修复（`defaultSchedulerDiscoveryService`），基于冻结修订 `aaf66c5` + 本修复
- 关联：`12-defects-and-security.md` 的 D-scheduler；`14-verdict.md` 验收项 2
- 原始证据：`raw/p15-dscheduler-process-observation.txt`、`raw/p15-worker-log-excerpt.txt`

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

## 三、进程级复验（决定性证据）

复验期间**未启动 HTTP server**、**未调用管理员 `run-due` 端点** → 下列任务只可能来自
调度进程自身的 tick，即真正的**无人值守**触发。

| 时刻 | 观测 |
| --- | --- |
| 13:20:23 | 启动 `cmd/discovery-scheduler`（PID 50129）；启动前基线 `max_task_id=84 / total=62 / with_key=3` |
| 13:20:52 | 存活 29 秒；`scheduler.log` **0 字节**（修复前此处 panic 后 exit 2）；首个 tick 即入队 85、86（`interval:5:5967136`，**pending**） |
| 13:22:44 | 存活 2 分 21 秒，跨 **3 个 tick**（`discovery_interval=1m`）；日志仍 0 字节；tick2/tick3 **未新增任何行** → 同窗口防重成立；`HAVING c>1` 为空 |
| 13:25:24 | 窗口推进到 `5967137`，无人干预下再各入队 1 行（87、88） |
| 约 13:25:35 | 由本次复验主动 `pkill` 停止（存活约 5 分 10 秒、跨 ≥6 tick）。背景任务回报的 exit 144 **即此次 pkill**，非进程自身退出；判据是日志全程 0 字节 |
| 13:27:39 起 | 启动独立 `cmd/discovery-worker`：领取 4 个任务，**写入 `started_at`/`finished_at`**，终态全部 `success` |
| 13:29:24 | 收尾；两进程已停止，无残留 |

**统计与库内读回一致（接口统计 == 库内真实行）：**

| task | strategy | schedule_key | scanned/found | added | duplicate | 库内新增行 |
| --- | --- | --- | --- | --- | --- | --- |
| 85 | 29 | `interval:5:5967136` | 20 / 20 | 17 | 3 | 17 |
| 86 | 10 | `interval:5:5967136` | 20 / 20 | 6 | 14 | 6 |
| 87 | 29 | `interval:5:5967137` | 20 / 20 | 2 | 18 | 2 |
| 88 | 10 | `interval:5:5967137` | 20 / 20 | 0 | 20 | 0 |

- `added` 合计 17+6+2+0 = **25**，与按 `crawl_task_id` 聚合的库内行数 **25** 精确一致。
- task 88 的 `added=0 / duplicate=20` 是上游真实全量去重的自然证据（非构造）。
- 本轮新增的 4 条任务**全部带非空 `schedule_key`** → 全部来自调度路径，无手工/HTTP 路径掺入。
- 上游真实性：Worker 日志含真实唯一键冲突（`uq_source_contents_team_platform_content`）与真实
  `platform_content_id`/标题，非 mock（见 `raw/p15-worker-log-excerpt.txt`）。

### 与上一轮 6.2 的对照

| | 上一轮（`aaf66c5`，未修） | 本轮（修复后） |
| --- | --- | --- |
| 6.2 独立调度进程存活 | **存活=False，exit=2**，`panic: douyin: Get called before Initialize` | **存活=True**，跨 ≥6 tick，日志 0 字节 |
| 周期触发执行者 | 不存在（只能靠管理员 `run-due` 顶替） | **存在**：调度进程自身按窗口入队，Worker 领取执行 |

## 四、本轮**未**做（如实声明）

1. **未复跑管理员 `run-due` 的防重子项**（上一轮 6.6/6.7）。理由：该端点需管理员登录，
   而登录会顶替用户浏览器中的既有会话；且其代码路径（`runDue`/`createRun`）本次**未被修改**
   （改动只是「谁来构造 service」），无回归面。**替代证据更强**：本轮以**无人值守路径**证明
   同窗口不重复（tick2/tick3 未新增行、`HAVING c>1` 为空），上一轮用 `run-due` 证明的正是同一条防重逻辑。
2. **未修 D8**（`ErrCrawlerUnavailable` 未在 `writeDiscoveryError` 映射）：按用户裁定保持最小改动，
   仍登记不修。
3. **未做 Desktop 视觉走查**；验收项 7 的「部分通过」结论不受本轮影响。
4. **未修 D1/D2/D3/D6/D9/D10**；未动 `config/credentials/douyin.toml`；未清理 git 历史。

## 五、安全复查（沿用 S-2 纪律）

用**真实凭据值反查**全部证据文件（110 个）：

- `config/credentials/douyin.toml` 的 `api_key`（35 字符）与 `cookie`（6975 字符）：**无任何文件命中**；
- cookie 的前 120 / 后 120 字符片段：**无命中**（排除截断残留）；
- 活会话令牌样式（`wt_media_session=<16+ 位>`）：**无命中**；
- `cookies/` 目录仍不存在。
- 新增的两个原始证据文件亦无凭据值。**结论：证据中不含凭据值。**

## 六、本轮残留登记（不删除，沿用阶段 11 口径）

`11-residue-teardown.md` 是**首轮验收**的渲染产物（基线 3 策略/11 任务/109 来源/26 素材），
此处单独登记本轮复验新增的残留，两者叠加即为当前全量：

| 表 | 本轮新增 |
| --- | --- |
| `crawl_tasks` | 4 行：85、86、87、88（全部带非空 `schedule_key`，全部 `success`） |
| `source_contents` | 25 行：`crawl_task_id ∈ {85,86,87,88}` |
| `discovery_strategies` | 0（复用既有 in-册策略 10、29，**未新增、未修改**） |
| `materials` | 0 |
| `operation_teams` / `users` | 0 |

**不变式**：本轮**未修改、未删除任何既有行**。启动前基线 `max_task_id=84 / total=62 /
with_key=3` 在复验前后一致；既有 62 条任务与 3 条带 key 任务保持原值。
无残留进程：收尾后仅剩复验前即在运行的 Desktop 外壳与 Agent `local_api:8765`。

## 七、对验收项 2 的结论

验收项 2（关键词策略真实周期触发 → 任务 → 执行 → 自动入池）的**唯一阻断点已消除**，
且以**无人值守**路径端到端复现（调度进程入队 → Worker 领取执行 → 内容池真实读回）。

- 判定：**复验通过**（原判定「不通过」基于修复前的 `aaf66c5`，本轮修复后重取证据）。
- 这是**对已执行验收轮的复验补证**，不是重开签收；**M3 状态保持 `IN_PROGRESS`，未标 DONE**。
