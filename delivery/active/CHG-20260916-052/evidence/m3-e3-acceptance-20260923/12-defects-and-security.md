# 缺陷登记与安全问题登记

> 本轮**只登记不修复**：`CHG-051 Task 4` 要求缺陷回前序 CHG 修复后再验收；验收期间改动
> 运行时代码会使读回归因到错误版本（计划 STOP S6）。
> 所有 `path:line` 均指向冻结修订 `aaf66c51bab68c5fddfd0648e347356e37dcb29e` 的只读观察。

## 一、安全问题（按用户裁定 3：只登记，不改仓库）

### S-1　抖音生产凭据被 git 跟踪

| 项 | 值 |
| --- | --- |
| 文件 | `wt-media-cloud/config/credentials/douyin.toml` |
| 被跟踪起点 | 提交 `3f2f43c` |
| 内容 | 真实 `api_key`（35 字符）与 `cookie`（6975 字符） |
| 对照 | `config_online/credentials/douyin.toml` 为空模板 |
| 违反 | 「凭据不得提交」的既有约束 |

**本轮不做**（用户裁定）：不改仓库、不加 `.gitignore`、不轮换密钥、不重写历史。
**建议后续处置**（留待决策）：轮换 `api_key` 与 cookie → 停止跟踪该文件 → 加 `.gitignore`
与 `*.example` 模板 → 评估历史清理。

**证据中不含任何凭据值**（2026-09-23 复查后成立，复查发现一处并已处置，见下）：

- 用**真实配置值反查**整个证据目录：`config/credentials/douyin.toml` 的 `api_key` 与 `cookie`
  未出现在任何证据文件中；命中的只是 `app.name`、`http_addr`、`douyin.host`、`database` 这类
  **非敏感**配置值。G0.4 只记录文件名、字节数与键名长度；
  `scripts/verify_m3_acceptance.py` 的 `redact()` 会替换凭据字面量与 `wt_media_session=...`。

### S-2　验收工具把活会话令牌写进了证据目录（已处置）

| 项 | 值 |
| --- | --- |
| 位置 | 证据目录下 `cookies/admin.cookies`、`cookies/operator.cookies` |
| 内容 | 各一枚 **有效的 64 字符 `wt_media_session` 令牌**（admin 与 operator 账号） |
| 成因 | `scripts/verify_m3_acceptance.py` 原先把 cookie jar 落点设为 `EVIDENCE/"cookies"`（原 `:47`） |
| 违反 | 「证据工件绝不能包含凭据值」 |

**处置（2026-09-23）**：

1. 删除 `cookies/` 整个目录——两枚令牌**从未提交**（证据目录当时尚未 `git add`），
   无历史可清理；令牌随本轮会话结束失效，`admin` 侧本就因 `replace_existing:true` 登录而被顶替。
2. 脚本落点已改到 **Cloud 仓库 `.cache/m3-acc/`**（`COOKIE_DIR = CLOUD_ROOT / ".cache" / "m3-acc"`）——
   该路径已被 `wt-media-cloud/.gitignore:1` 的 `.cache/` 覆盖，重跑不再把令牌写进证据目录。
3. 该目录不是任何证据文档引用的交付物（已逐文件确认无引用），删除不影响证据完整性。

## 二、缺陷登记（以实测为准）

### D1　策略重名返回 500，而非 409 / 14007　【实测 FAIL 5.5.8】

- 现象：隔离组内用同名创建策略 → `HTTP 500 errcode=50000 "挖掘服务内部错误"`
- 期望：`409 / 14007「策略名称已存在」`
- 根因：仓储层返回**包私有**错误 `errStrategyDuplicate`
  （[discovery_store_mysql.go:27](../../../../../wt-media-cloud/internal/modules/contentpool/repository/discovery_store_mysql.go#L27)、
  [:278](../../../../../wt-media-cloud/internal/modules/contentpool/repository/discovery_store_mysql.go#L278)），
  从未被翻译为 `service.ErrStrategyDuplicate`；而 handler 确实映射了后者
  （`handler.go:538-539` → `409 / 14007`），因此错误落进 `default` 分支变成 500。
- 影响：用户看到「服务内部错误」而不是「名称已存在」，无法自行纠正。

### D2　`schedule` 无服务端格式校验　【实测 FAIL 5.5.9】

- 现象：`schedule="garbage"` 创建成功（`201`），库中 `schedule='garbage'`
- 期望：`400 / 14006`
- 根因：`createStrategy` / `updateStrategy` 只把空值兜底为 `manual`，不校验取值是否属于
  `manual` / `interval:<N>` / `daily HH:MM`
- 影响：非法周期静默入库。UI 会把它原样显示成执行周期「garbage」
  （见 `screenshots/03-discovery-strategies.png` 策略 id=7）。运行时 `scheduleDue` 对无法识别的
  取值恒为 false，即该策略永远不会被触发，且用户得不到任何提示。

### D3　`/run` 可重复排队，违反基线 §5　【实测 FAIL 6.9】

- 现象：对同一策略连调两次 `POST /discovery-strategies/:id/run` → pending 行 `0 → 2`
- 期望：基线 §5「同策略已有 pending/running 任务时不重复排队」
- 根因：`CreateRun` 以空字符串作为计划键
  （[operations.go:49](../../../../../wt-media-cloud/internal/modules/contentpool/service/operations.go#L49)
  → `createRun(actor, strategyID, "")`），落库后 `schedule_key` 为空，
  而唯一索引 `uq_crawl_tasks_strategy_schedule (strategy_id, schedule_key)`
  （`migrations/20260916_031_crawl_task_schedule_key.sql:3`）不拦空值；
  `createRun`（`discovery.go:237-260`）本身也没有「已有在途任务」的前置检查。
- 影响：重复点击「执行」会重复消耗上游配额并重复入池作业。注意周期触发路径
  **不受影响**：它传 `scheduleWindowKey(...)`（`discovery.go:588`），双层防重有效（6.6/6.7 PASS）。

### D4　文档与 `cmd/server` 实际不符（Cloud `scripts/README.md`）

- 该文件末段曾写「the normal Cloud server starts the API Server, Discovery Scheduler, and
  Discovery Worker together」——**该陈述由本项目早前的提交 `aaf66c5` 引入，是错的**。
- 实际：`cmd/server` 只启动 HTTP 引擎；Scheduler 与 Worker 是独立 CMD。
- 正面证据：G2 只起 `cmd/server` 并观察 120 秒，`pending/running` 任务数恒为定值
  （`raw/g2-server-only-observation.txt`，13 个采样点）。
- 处置：属本项目自身引入的错误，在 Cloud 仓库单独提交更正（见 Part B / B5）。

### D5　`WT_MEDIA_DOUYIN_*` / `.env.local` 对 Cloud 运行时无效

- Cloud 运行时只读 `config/`（TOML），全仓零 `os.Getenv`（架构边界测试禁止）。
- 受影响文档：ADR-0015 第 2 条、`CHG-20260916-052/{change.md,checkpoint.md}`、M3 milestone §4。
- 处置：按事实回写文档（Part B / B2、B3）。

### D6　UI 的 ID/链接发现硬编码 `source_type: 'search'`

- 位置：[ContentPoolPage.vue:251](../../../../../wt-media-cloud/web/src/modules/contentpool/pages/ContentPoolPage.vue#L251) —
  手工导入一律传 `source_type: 'search'`，不区分「ID/链接发现」与「关键词发现」。
- 而 `link` 枚举只在**遗留** `POST /content-pool/import-url` 路径产出
  （本轮 5.16 实测产出 `source_type='link'` 的真实行 id=204）；
  该接口在 UI 侧**零调用**：`discovery.js:20` 定义了 `importUrl`，但
  `ContentPoolPage.test.js:49` 明确断言 `not.toContain('discovery.importUrl')`。
- 影响：经「ID/链接发现」入池的行在界面上显示为「关键词发现」，来源方式失真；
  且 `link` 这条真实来源路径实际上不可达。

### D7　同族问题：`errCrawlTaskNotFound` 同样未被翻译

- 仓储层另有包私有错误 `errCrawlTaskNotFound`
  （[discovery_store_mysql.go:167](../../../../../wt-media-cloud/internal/modules/contentpool/repository/discovery_store_mysql.go#L167)、
  [:280](../../../../../wt-media-cloud/internal/modules/contentpool/repository/discovery_store_mysql.go#L280)），
  与 D1 同族；handler 虽映射了 `ErrCrawlTaskNotFound`（→ `404 / 14004`），但该错误到不了那里。
- 本轮未构造出可复现的公开路径，**仅按代码观察登记**，未计入 FAIL。

### D8　`ErrCrawlerUnavailable` 未在 `writeDiscoveryError` 映射

- `writeDiscoveryError`（`handler.go:526-545`）的 case 覆盖
  `ErrDouyinAuthorUnavailable / ErrDiscoveryForbidden / ErrStrategyNotFound /
  ErrCrawlTaskNotFound / ErrDiscoveryInvalid / ErrStrategyDuplicate / ErrDiscoverySelection`，
  **没有** `ErrCrawlerUnavailable`（定义于 `service/discovery_crawler.go:17`）。
- 影响：未配置 crawler 时用户看到 500「挖掘服务内部错误」，而非可解释的配置类错误。
- 本轮未构造该前置（本地 crawler 已配置），**仅按代码观察登记**，未计入 FAIL。

### D9　上游空返回被如实透传为「成功且 0 条发现」　【实测 FAIL 5.2b / 5.15】

- 现象：同一真实 ID 连续 8 次按 ID 发现，`2/8` 次拿到 `errcode=0` 但 `items` 为空；
  `items` 为空时 `errcode` 仍为 `0`，重试即恢复。
- 上游侧：`POST /batchDyVideo` 返回 `result=1` 且 `data` 为空列表——是上游的间歇行为。
- Cloud 侧：忠实呈现为「成功、无结果」，**用户界面不会出现任何错误提示**；
  经 `import-url` 触发时同样落为 `status=success, found=0` 的任务（5.15b 实测）。
- 判定：上游行为不计为 Cloud 缺陷；但「空结果伪装成成功」这一体验问题需要产品决策
  （是否区分「查无结果」与「上游异常」）。本轮只登记。

### D-scheduler　独立调度进程首次 tick 即 panic　【实测 FAIL 6.2，本轮最高severity】

```
panic: douyin: Get called before Initialize
  ← douyin.Get()
  ← newDouyinCrawler()
  ← defaultDiscoveryService()   // service/store_adapter.go:83
  ← RunDue()                    // service/discovery.go 周期触发入口
  ← jobs.RunDiscoverySchedule
  ← bootstrap.runSchedulerProcess.func1
```

- 根因（2026-09-23 修复时更正，原归因有误）：**不是「`schedulerResourcePlan()` 缺 `clientsResource()`」，
  而是未收尾的迁移遗留**。`0699e8a` 把单进程拆成三个 CMD 时，crawler 由「自读配置的
  `NewDouyinCrawlerFromEnv()`」换成「生命周期管理的单例 `douyinclient`」：server 与 worker 的
  资源计划都补了 `clientsResource()`，**唯独调度路径漏补**，同时同一提交又用
  `TestInitializeSchedulerDoesNotInitializeDouyinClient` 把「调度计划不含 clients」锁定为预期。
  `100899d` 删除 `NewDouyinCrawlerFromEnv` 并把 service 构造挪进 job 体内，panic 遂落在首个 tick 的
  裸 goroutine 中。因 `internal/`+`pkg/` 全仓零 `recover()`，整进程退出并带走同进程的 `proxy-expiry`。
  （`serverResourcePlan()` 没有 job 步骤这一点仍属实。）详见 `15-dscheduler-fix-reverification.md`。
- 实测：启动 `cmd/discovery-scheduler` 观察 75 秒 → `存活=False exit=2`。
- **影响（重要）**：本期内**没有任何进程在执行周期调度**。库中所有 `schedule_key` 非空的任务
  都是在验收期间由管理员调用 `POST /discovery-scheduler/run-due` 产生的；
  在此之前，历史上从未有任务拥有非空 `schedule_key`。
  换句话说，**「关键词策略能通过真实周期触发」这一验收项在真实运行中并未交付**，
  验收只能证明其**调度语义正确**（窗口键、双层防重、防重唯一索引），
  不能证明「无人值守的周期触发」可用。见 `14-verdict.md` 的验收项 2。
- 处置（**已修复并复验，2026-09-23**）：按用户裁定「scheduler 只是扫库做任务调度，不需要依赖这些
  额外的 client」，**不给 `schedulerResourcePlan()` 补 `clientsResource()`**，而是让调度路径不再持有
  crawler（Cloud 新增 `defaultSchedulerDiscoveryService()`，`RunDue` 改走它；`RunDue` 只用
  `s.store` 与 `s.createRun`，从不解引用 `s.crawler`）。`schedulerResourcePlan()` 与其测试**原样保留**。
  进程级复验（`interval:N` 形态）：调度进程跨 ≥6 个 tick 存活、日志 0 字节，并在**未调用 `run-due`、
  未启动 HTTP server** 的情况下自行按窗口入队 4 个任务，Worker 领取执行后全部 `success`、
  库内新增 25 行与统计一致。
  **同日追加 `daily HH:MM` 形态补验**（首轮只覆盖了 `interval:N`，而全库 `daily:` 前缀任务历史为
  0 条、在册生产策略 id=2 用的恰是 `daily 09:00`，两者走不同 due 判定）：到期 tick 前 20 秒仍
  0 行、到期那一分钟恰好 1 行（`id=91`、`daily:2026-09-23:13:57`）、同日后续 tick 仍 1 行；
  调度进程存活 8 分 31 秒、跨约 9 个 tick、日志全程 0 字节；Worker 执行后 `success`、
  库内 19 行 == `added` 19。
  详见 `15-dscheduler-fix-reverification.md`（两种形态的覆盖范围见该文第三节）。**验收项 2 由
  「不通过」改判「复验通过」**（`14-verdict.md` 已同步；仍不标记 M3 DONE）。

### D-scheduler-2　`daily HH:MM` 漏 tick 即丢当天　【2026-09-23 复验时新登记，未修】

- 位置：`internal/modules/contentpool/service/discovery.go:761-769`（`scheduleDue` 的 daily 分支）。
- 现象：daily 的到期判定要求 `hour==now.Hour() && minute==now.Minute()`，即 tick 必须**恰好落在
  那一分钟内**；且 `sameScheduleWindow` 以「同一日历日」为窗口，故一旦当天已过该分钟，
  后续 tick **不会补触发**。
- 影响：调度进程若在目标分钟内不在跑（或漏了一次 tick），当天该策略**静默不执行**，
  无告警、无补偿。与 `interval:N` 不同（后者只要进程在跑，窗口到期即触发，天然容忍漏 tick）。
- 定性：**既有设计，非本次修复引入**；本轮复验中亦未观察到实际发生（样本按预期触发）。
- 处置：**本轮只登记，不修**；是否补「当天未跑则补触发」的兜底，交用户裁定
  （已列入 `14-verdict.md` 建议的下一步第 2 条）。

### D10　`scripts/verify_m2_acceptance.py` 指向已迁移的文件路径　【实测 FAIL 10.3】

- 位置：`wt-media-workspace/scripts/verify_m2_acceptance.py:71` 期望
  `internal/modules/cloudagent/compatibility.go`。
- 实际：该文件已于 2026-09-18 的 `bf499d9`「refactor: migrate identity and cloudagent modules」
  迁移为 `internal/modules/cloudagent/service/compatibility.go`（常量值不变，
  `ContractRevision = "2026.07.15.1"` 等仍在）。
- 定性：**验收脚本自身陈旧，不是 M2 功能回归**。M3 窗口内的改动不触及 Agent/cloudagent 路径。
- 佐证：仅修正这一处路径的**临时副本**执行后，M2 静态跨仓矩阵全绿
  （`raw/p10-m2-corrected.log`）；原脚本未被修改，临时副本用后即删。
- 处置：本轮不修（保持「M2 回归」结论来自未改动的脚本）；建议后续单独修正。

## 三、缺陷影响面小结

| 缺陷 | 是否影响基线 §8 验收项 | 说明 |
| --- | --- | --- |
| D-scheduler | **曾是**，验收项 2 | 在冻结修订 `aaf66c5` 上真实周期触发未交付；2026-09-23 修复并复验通过（`interval:N` 与 `daily HH:MM` 两形态均覆盖），验收项 2 已改判（见 `15-dscheduler-fix-reverification.md`） |
| D-scheduler-2 | 否（潜在，非本轮实测失败） | daily 漏 tick 即丢当天且无补偿；影响无人值守可靠性，未构成本轮任何验收项失败 |
| D1 / D2 | 否 | 边界与体验问题，不影响既定验收项成立 |
| D3 | **是**，基线 §5 的「不重复排队」 | 手工 `/run` 路径不达标 |
| D6 | 否 | 来源方式标签失真，不影响入池与去重正确性 |
| D4 / D5 / D10 | 否 | 文档与验收脚本问题 |
| D9 | 否 | 上游行为 + 体验问题 |
| D7 / D8 | 否 | 仅代码观察，未复现 |

**没有任何缺陷影响本次验收结论的取证有效性**：所有 PASS 项都是在真实服务、真实上游与
真实数据库读回下取得的，未使用 mock 替代。
