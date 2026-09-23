# BLOCKED / NOT VERIFIED / ADJUDICATED 清单

本轮**没有 BLOCKED-EXTERNAL**：G4 判定为 REAL-OK，上游全程可达，依赖真实内容的验收项都真跑了。
下面三类是仍然需要明示的「没有证到」的部分。

## 一、NOT VERIFIED（1 项）

> **2026-09-23 更新：本项已补验通过，NOT VERIFIED 清零。**
> 下面的原文保留首轮判定（对冻结修订 `aaf66c5` 生效），**其中给出的技术原因经实测不成立**，
> 已在下文更正。补验证据见 `17-material-failed-injection.md`，判定改判见 `14-verdict.md` 第 6 项。

### 8.8　`material_failed` 无法经公开 API 触发

- 期望：确认 `source_content.processing_status = material_failed` 这一状态可达
- 实际：未能构造
- 原因：~~`materialize` 在 `FOR UPDATE` 下幂等，正常路径不会失败~~ —— **该原因错误**（2026-09-23 实测推翻）
- 结论：~~该状态在本轮未被证实可达也未被证伪~~ —— **已由受控故障注入证实可达**（见下）
- 相关的可证部分：自动转素材**失败不得记为成功**这一要求，已由阶段 7 的逐条谓词复算间接覆盖
  （`stats.auto_materialized` 与库内素材行数在 7 个用例中逐例相等，未出现「统计说成功、库里没有」）。

#### 更正与补验结论（2026-09-23）

- **原因更正**：`SELECT … FOR UPDATE` 的锁**确实会挡住** `materials` 的 INSERT，阻塞到
  `innodb_lock_wait_timeout` 后报 `ERROR 1205`。首轮踩的是探测陷阱——**间隙锁之间互不冲突**，
  用「加锁读」（`FOR UPDATE NOWAIT`）永远测不出写入被挡，必须用**写语句**探。
  本轮最初也踩了同一坑，改用真实 `INSERT … ROLLBACK` 探针才复现 `1205`。
- **补验结果**：以「公开 API 触发策略 + 独立 Worker 执行 + 第二会话持锁」注入，
  任务 94 的 `result_json` 中落 **3 条 `material_failed`**，各带真实
  `failure_reason='Error 1205 (HY000): Lock wait timeout exceeded'`；`materials` 全程恒为 146
  （无半写）；释放锁后 `retry-failed` → 任务 95 `success`、3 条全部 `auto_materialized`、
  `materials` 146 → 149。
- **结论**：**状态可达、失败原因可读、失败项可恢复**，验收项 6 的例外已去除。

## 二、ADJUDICATED（1 项，按用户 2026-09-23 裁定）

### 10.8　只读业务流转视图

- 用户裁定原文：「裁决一：已经完成挖掘策略执行，挖掘任务最后生成内容到内容池，但是你说的任务
  详情执行过程时间线 + 来源追溯 + 跨页深链，这个不好判别，**就当没有**」
- 取证（`raw/p10-flowview-grep.txt`）：
  - Cloud `internal/` 与 `web/src/` 搜 `业务流转|流转视图|工作流视图|全景视图` → **0 命中**
  - Cloud 全仓搜 `流转` → **0 命中**
  - Cloud `docs/` 搜 `流转视图|业务流转` → **0 命中**
  - 前端内容挖掘相关路由只有四个：`content-pool`、`discovery-strategies`、`crawl-tasks`、
    `material-library`（后两者与内容池共用 `ContentPoolPage.vue`）
- 结论：**本期未交付独立的只读业务流转视图**，按裁定移出验收范围，不记为 FAIL。
  基线 §6 相应改写为「本期交付的是功能链路（策略 → crawl_task → Worker 执行 → 结果写入内容池
  并可按规则自动转素材），独立只读流转视图后续版本再评估」。
- 注意：ADR-0013 第 8 条对「**不允许**编排/拖拽/条件分支/任意脚本」的**禁止性**约束不变，
  仍禁止新增工作流能力；被移出的只是「必须提供一个只读视图」这一**交付要求**。

## 三、口径说明（不是 BLOCKED，但读证据时需要注意）

### 3.1　「周期触发」的证据强度

6.2 已证独立调度进程 panic 退出；6.3–6.8 用管理员 `run-due` 端点（**同一 `RunDue` 实现**）
验证了调度语义：窗口键格式、同窗口 `triggered=0`、同 `schedule_key` 仅 1 行、唯一索引存在。

因此：**调度语义 = 已验证**；**无人值守的真实周期触发 = 未交付**（D-scheduler）。
不把后者写成已验证。

> **2026-09-23 更新：本节的「未交付」已由修复 + 无人值守复验推翻。**
> 独立 `cmd/discovery-scheduler` 在**未调用 `run-due`、未启动 HTTP server** 的情况下
> 自行按窗口入队，`interval:N` 与 `daily HH:MM` **两种形态均已覆盖**；验收项 2 已改判通过，
> 并经用户同日裁定闭环。证据见 `15-dscheduler-fix-reverification.md`。

### 3.2　`partial_success` 的构造方式

`partial_success` 需要「至少一项失败且至少一项成功」。人工关键词任务走的是
`import-results`，全部条目要么成功要么整体失败，**无法达到 partial_success**。
本轮唯一可控配方是遗留 `import-url` 传 `[真实数字 ID, invalid-retry-test]`：
前者取到 1 条，后者必然失败 → `scanned=2, found=1, added=1, failed=1`，无顶层错误
→ `partial_success`（8.2 实测，第 1 次尝试即命中）。
这是**真实业务路径**（有真实任务行、真实重试血缘），但需要注意：该入口 UI 不调用（见 D6）。

### 3.3　既有 pending 任务 id 33 的消耗

任务 33（策略 3，`pending`）在本轮开始前就存在。Worker 启动后即被领取并执行完成
（`added=16, found=20, duplicate=4, auto_materialized=8, pending=8`）。
这是既有任务的正常执行，不是本轮产物，但确实消耗了它。此项**无法避免**（Worker 一启动就会领取），
特此声明。

### 3.4　`source_type='link'` 的可达性

本轮通过遗留 `import-url` 真实产出过 `source_type='link'` 的行（id=204），
证明该枚举在库层可用；但 UI 不调用该接口（D6），因此**界面上不存在产生 `link` 来源的操作**。

### 3.5　未做的走查

视觉走查用无头 Chrome 只能截静态页面，**不能点击**。因此以下交互未做视觉取证，
仅由代码与接口层证据支撑：
- 策略编辑弹窗中「作者（维护中）」禁用项的呈现（服务端硬禁用已由 5.6 恒返 400/14006 证实）
- 任务详情抽屉的三个标签页（统计/日志/处理项）
- 审核模式逐条流转（「转素材并下一条 / 忽略并下一条 / 跳过」）

> **2026-09-23 更新：三项交互均已补做视觉取证，本节缺口已关闭；且原描述有一处与实现不符。**
> 补做方式：在 5174 上以**打进 DMG 的前端产物**为静态根起静态服务 + `/api` 反向代理，
> 并注入仅在 `#walk=` 时动作的点击驱动脚本，用无头 Chrome 取图（应用产物逐字节未改）。
> 证据见 `16-desktop-walkthrough.md`，共 11 张截图。
> **更正**：任务详情抽屉实测为**四个**标签页——结果概览 / 发现内容 / 执行过程 / 异常记录，
> 不是本节原先写的「统计 / 日志 / 处理项」。
