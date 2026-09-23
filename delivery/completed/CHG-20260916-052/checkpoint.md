# Checkpoint

- Completed：按 ADR-0015 将 M3 discovery 执行边界纠偏为 Cloud-owned Crawler；Cloud 不再创建/分配 discovery Agent task，Agent 中的 M3 遗留 adapter/executor 已清理；搜索结果仍采用“任务结果→人工选择→内容池”两步语义。修复抖音 `/dyRank` 搜索必须传 `ck` 表单字段的问题（Cloud `0548b22`），并提供管理员受控调度入口（Cloud `e18a2b1`；会话替换可配置，Workspace `fdd9e66`）。2026-09-23 按用户确认与实施事实回写自动转素材（产品基线 §4、ADR-0013 第 3 条）与 `partial_success`（产品基线 §5、ADR-0013 第 7 条），并将 M3 产品基线落回 `docs/product/`。
- Current：ACTIVE；Cloud Crawler、Cloud Scheduler、Web 入口和治理记录已同步，自动化验证通过。2026-09-23 已按 Cloud 仓库实施结果同步 M3 阶段状态（`delivery/milestones/M3-content-discovery-v2.md` 第 2.1 节）：A～E1 有真实证据，C2/E2 已暂停；**E3 综合验收已于本 CHG 内执行并经同日补验收口——验收矩阵第 1～7 项全部通过，无 FAIL、无 NOT VERIFIED**（`evidence/m3-e3-acceptance-20260923/14-verdict.md`）。M3 仍为 `IN_PROGRESS`，**签收属用户裁定，未标 DONE**。
- Next：进入 E3（CHG-20260915-051）综合验收与用户签收；C2/E2 已暂停，不再作为 E3 前置。关键词链路的真实外部读回需先具备 Cloud Douyin 凭据/接口环境；凭据以 `config/credentials/douyin.toml` 形式提供给 Cloud（2026-09-23 更正：Cloud 运行时只读 `config/` 下的 TOML，架构边界测试禁止 `os.Getenv`；`WT_MEDIA_DOUYIN_*` 环境变量与 `wt-media-cloud/.env.local` 对其无效）。定时调度入口为 Cloud `cmd/discovery-scheduler`，Worker 为 `cmd/discovery-worker`（原 `scripts/run-discovery-scheduler.sh`、`scripts/run-discovery-worker.sh` 已在 Cloud `36a7cfe` 删除，云仓 `scripts/README.md` 已于 Cloud `aaf66c5` 更正）。
- Blockers：真实 Douyin 凭据/接口可用性不在仓库内，需以 `config/credentials/douyin.toml` 形式提供给 Cloud（2026-09-23 更正：Cloud 运行时只读 `config/` 下的 TOML，环境变量对其无效）后才能做真实外部读回。不以 BitBrowser/Agent mock 替代。
- Verification：Cloud `go test ./...` PASS（含团队权限、选择入池、批量链接、时区调度、Crawler 映射、`ck` 搜索字段、受控调度入口和 discovery task 禁用测试）；Agent `./scripts/test.sh` PASS（85 tests，M2 回归）；Web Vitest PASS（20 files/76 tests），Cloud/Desktop builds PASS（仅既有 chunk size/dynamic import warnings）；最新 `scripts/m2b-local-acceptance.sh up --force-restart` + `verify` PASS，Cloud `18080`、Agent `8765`、脱敏 BitBrowser mock、Desktop assets/DMG、admin 登录 smoke 均通过。配置真实凭据后，运营账号关键词搜索任务已返回 `status=success`、`errcode=0`；本地调度脚本返回 `triggered=0`，运营账号调用被拒绝 `HTTP 403`，禁用会话替换时已有管理员会话返回 `HTTP 409`（本地门禁不作为 M3 真实 Douyin 外部验收）。

## 2026-09-23 M3 全量验收结论

- 验收在 Cloud `aaf66c5` 上完成：`run-manifest.json` 共 106 步，87 PASS / 7 FAIL / 1 NOT VERIFIED / 1 ADJUDICATED。
- 唯一硬阻断是 D-scheduler：独立 `cmd/discovery-scheduler` 首次 tick 即 panic 退出，**无人值守的真实周期触发本期未交付**（管理员 `run-due` 受控端点与周期 tick 共用实现，但不等于无人值守触发）。
- **D-scheduler 已于同日修复并复验通过**（用户裁定：scheduler 只扫库调度，不依赖额外 client；修法是让调度路径不再持有 crawler，而非给 `schedulerResourcePlan()` 补 `clientsResource()`）。复验以**无人值守**路径端到端成立，**两种周期触发形态均已覆盖**：`interval:N`——调度进程跨 ≥6 tick 存活、日志 0 字节，未调 `run-due`、未启 HTTP server 即自行按窗口入队 4 个任务（85–88），Worker 领取执行后全部 `success`，库内新增 25 行与统计 `added` 合计一致；`daily HH:MM`——同日追加补验，到期 tick 前 20 秒仍 0 行、到期那一分钟恰好 1 行（`id=91`、`daily:2026-09-23:13:57`）、同日后续 tick 仍 1 行，进程存活 8 分 31 秒跨约 9 tick、日志全程 0 字节，库内 19 行 == `added` 19。**验收项 2 由「不通过」改判「复验通过」**。详见 `evidence/m3-e3-acceptance-20260923/15-dscheduler-fix-reverification.md`（覆盖范围见其第三节）。
- **D-scheduler 已按用户 2026-09-23 裁定闭环**：「scheduler 修复已完成」。收尾动作：残留周期策略 id=9、10、29、37（均 `m3acc0923-*`）由 `enabled` 改为 `disabled`（**行未删除**；真实业务策略 id=2「三角洲热点」`daily 09:00` 未改动）；停用后再起调度进程 80 秒，**0 新增任务**。闭环范围**不含** D-scheduler-2，亦**不构成 M3 签收**。详见该文第八节。
- 其他缺陷仍未修：D1 策略重名返回 500、D2 `schedule` 无服务端校验、D3 `/run` 可重复排队、D9 上游空返回透传为成功、D8 `ErrCrawlerUnavailable` 未映射、D6 来源方式标签失真、D7 同族错误未翻译、D10 M2 验收脚本路径陈旧。**`material_failed` 已由受控故障注入补验通过**（原 NOT VERIFIED 清零；见下第 3 条）。
- **新增登记（2026-09-23 复验时，只登记不修）**：D-scheduler-2 —— `daily HH:MM` 要求 tick 恰好落在那一分钟内且无补偿机制，漏 tick 即丢当天；既有设计、非本次引入，是否补兜底交用户裁定。另：两轮复验新增残留 `crawl_tasks` 9 行（85–93）、`source_contents` 55 行、`discovery_strategies` 1 行（id=37，daily 补验样本），既有行未修改未删除（该策略已于同日停用，见上）。
- 独立的只读业务流转视图按用户 2026-09-23 裁定移出验收范围（ADJUDICATED），不作为缺口；ADR-0013 第 8 条的禁止性约束不变。

### 同日补验（两处覆盖缺口，按用户裁定「先只补 Desktop 走查」「`material_failed` 本轮一并补验」）

1. **Desktop 走查已执行**（原判「未做」，验收项 7 因此只能部分通过）。以端到端脚本
   `scripts/local-control.sh start` 起全链路（各检查点 PASS，DMG 14:27），对**打进 DMG 的前端产物**
   完成四页走查 + 三项点击交互（策略编辑「作者（维护中）」禁用态；任务详情抽屉**四个**标签页；
   审核模式 `1/91 → 2/91` 流转推进），共 11 张截图。全程**零服务端写入**已逐动作论证。
   另发现两项产品事实：Desktop **拒绝管理员与高级运营**登录（只允许运营角色）；任务详情实为
   **四个**标签页而非首轮记录的三个。**验收项 7 改判通过**。详见
   `evidence/m3-e3-acceptance-20260923/16-desktop-walkthrough.md`。
2. **`material_failed` 已由受控故障注入证实可达**（原 NOT VERIFIED）。以「公开 API 触发策略 +
   独立 Worker 执行 + 第二会话持 `materials` 全表锁」注入：任务 94 落 **3 条 `material_failed`**，
   各带真实 `failure_reason='Error 1205 … Lock wait timeout exceeded'`；`materials` 全程恒为 146
   （**无半写**）；释放锁后 `retry-failed` → 任务 95 `success`、3 条全部 `auto_materialized`、
   `materials` 146 → 149（且重试**不重建来源行**，`source_contents` +0）。
   **首轮给出的「`materialize` 在 FOR UPDATE 下幂等」解释经实测推翻**——锁确实挡住写入，首轮踩的是
   「间隙锁互不冲突、加锁读探不出写阻塞」的探测陷阱。**验收项 6 的例外已去除，改判通过**。详见
   `evidence/m3-e3-acceptance-20260923/17-material-failed-injection.md`。
3. **缺陷处置去向**（用户裁定「移入 planned，另立后续 CHG」）：D1、D2、D3、D6、D7、D8、D9、D10、
   D-scheduler-2 与安全问题 S-1 已登记为 `delivery/planned/CHG-20260923-054`，**不在本 CHG 内修复**。
   其中 **D3 是唯一影响验收项的缺陷**（基线 §5「不重复排队」）；D9、D-scheduler-2、S-1 需先有用户裁定
   才能定验收标准。**S-1 现状不变**：`config/credentials/douyin.toml` 仍被 git 跟踪，本轮未做任何
   仓库动作（未轮换、未停跟踪、未加 `.gitignore`、未重写历史）。
4. 本轮补验新增残留 `crawl_tasks` 2 行（94、95）、`source_contents` 19 行（全部由任务 94 产生）、
   `materials` 3 行（id=151/152/153）、`discovery_strategies` 1 行（id=38，已由 `enabled` 改为
   `disabled`，行未删除）。既有行未修改未删除（`materials id<=146` 仍 146 行、无遗留非终态任务）。

- 结论：**验收矩阵第 1～7 项全部通过，无 FAIL、无 NOT VERIFIED**；**仍未标记 M3 DONE**，M3 保持
  `IN_PROGRESS`（验收通过不构成用户签收，`CHG-20260915-051` 未激活）。详细证据见
  `evidence/m3-e3-acceptance-20260923/`（判定见 `14-verdict.md`，缺陷与安全问题见
  `12-defects-and-security.md`，两份补验见 `16-`、`17-`）。

## 2026-09-23 收尾：`Status: HANDOFF`（未写 DONE）

- **为何以 HANDOFF 归档**：M3 签收属用户裁定，本 CHG 不宣称完成。照 `CHG-20260915-044` 先例，
  归档为 `HANDOFF` 而非 `DONE`；**M3 保持 `IN_PROGRESS`**，`CHG-20260915-051` 仍未激活。
- **E3 验收结论不变**：第 1～7 项全部通过、无 FAIL、无 NOT VERIFIED。
- **验收之后新发现的缺陷已切出**：用户在生产形态 DMG 原生应用上报出内容池封面不加载与标题折行撑高行，
  经定位为两条独立根因（CSP 无 `img-src`；标题省略号漏了 `<a>` 渲染分支），
  移交 `CHG-20260923-055` 修复，**不在本 CHG 内处置**。
- **覆盖声明已收窄**：`evidence/m3-e3-acceptance-20260923/16-desktop-walkthrough.md` 第七节已改写，
  写明该走查未附加应用 CSP（结构性看不到封面被拦），且其自身截图里已含标题折行与行高参差的现象。
  即：验收项 7 的「通过」不能支撑「Desktop 渲染无问题」的结论。
