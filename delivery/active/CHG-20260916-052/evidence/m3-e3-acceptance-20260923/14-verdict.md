# 验收结论：按基线 §8 逐项判定

依据：`docs/product/M3-content-mining-v2.md` §8「最终验收」当前版本。
判定只采用本次真实执行取得的证据（`run-manifest.json` 106 步）。

## 总体结论

| | |
| --- | --- |
| 可判定为通过的验收项 | **7 项（第 1–7 项）** |
| 原不通过、**2026-09-23 复验改判通过** | 1 项（第 2 项：真实周期触发，D-scheduler 修复后复验；`interval:N` 与 `daily HH:MM` 两形态均覆盖） |
| 原带例外、**2026-09-23 补验后去例外** | 2 项（第 6 项：`material_failed` 受控故障注入，见 `17-material-failed-injection.md`；第 7 项：Desktop 走查，见 `16-desktop-walkthrough.md`） |
| 状态约束 | 第 8 项成立：**未标记 M3 DONE** |

> **本轮补验（2026-09-23）**：首轮验收的两处缺口已分别补齐——
> 第 6 项以**受控故障注入**证实 `material_failed` 可达且失败项可重试恢复；
> 第 7 项完成 **Cloud Desktop 走查**。两者均以真实服务、真实上游、真实数据库读回取得，
> 未使用 mock 替代。补验结论见 `16-`、`17-` 两份文件。
> **补验不构成签收**：M3 仍为 `IN_PROGRESS`，签收属用户裁定。

> **本文档保留 2026-09-23 首轮验收的原始判定**（其结论对当时的冻结修订 `aaf66c5` 生效）。
> 第 2 项在原判定下**不通过**，唯一阻断是 **D-scheduler**：独立 `cmd/discovery-scheduler`
> 首次 tick 即 panic 退出，**本期内没有任何进程在执行周期调度**。
> D-scheduler 已于同日修复并按无人值守路径复验通过，**第 2 项改判通过**（见该节「复验改判」）。
> 其余功能面（入口、导入、策略配置、自动转素材、五态与重试、权限与幂等）均有完整真实证据。
> **M3 状态仍为 `IN_PROGRESS`，未标 DONE** —— 签收属用户裁定。

---

## 逐项判定

### 第 1 项　链接、关键词搜索真实入池；未选结果零写入　→ **通过**

| 证据 | 结果 |
| --- | --- |
| 5.1 关键词搜索 | `errcode=0 items=5`，`crawl_tasks` 41→41（搜索不建任务） |
| 5.2 / 5.2b ID/链接发现（`query` 模式） | 真实返回；8 次中 2 次上游空返回（D9） |
| 5.10 只搜索不导入 | `source_contents` 319→319，零写入 |
| 5.11 / 5.12 / 5.13 选中导入 | `imported=1 duplicate=1`，SQL 读回真实行（id=436, `source_type='search'`）；重复导入 `imported=0 duplicate=2` |
| 5.3–5.9 负例 | 空 `query`、101 个目标、`author-search`、`source_type:"link"`、非抖音域等一律 `400 / 14006` |
| 5.16 遗留 `import-url` | 真实产出 `source_type='link'` 行（id=204）——UI 不调用该入口（D6） |

博主搜索：5.6 实测恒 `400 / 14006「博主搜索接口维护中」`，与服务端硬禁用一致，符合「已暂停」。

### 第 2 项　关键词策略真实周期触发 → 任务 → 执行 → 自动入池　→ **不通过**（**2026-09-23 复验改判：通过**）

| 证据 | 结果 |
| --- | --- |
| 6.1 建 `interval:5` 且启用 | `201 id=29` |
| **6.2 独立调度进程存活** | **存活=False exit=2，panic: douyin: Get called before Initialize** |
| 6.3–6.5 经 `run-due` 端点 | `triggered=2`；`schedule_key=interval:5:5967051`、`task_type=discovery_task`；Worker 写入 `started_at/finished_at`，终态 `success` |
| 6.6 / 6.7 / 6.8 防重 | 同窗口 `triggered=0`；同 `schedule_key` 仅 1 行；唯一索引存在 |
| 5.5.12 启用不立即执行 | `crawl_tasks(strategy=24)` 0→0 |

**调度语义已证实，周期触发的执行者不存在。** 6.3–6.5 走的是管理员 `run-due` 端点——它与
周期 tick 共用 `RunDue` 实现，但**不是**无人值守触发。基线明确写「只创建配置或任务列表不算完成」，
故本项判不通过。修复 D-scheduler 后可复验（6.3–6.8 的步骤可直接复用）。

#### 复验改判（2026-09-23，修复后）

D-scheduler 已按下述修法修复（**不给 `schedulerResourcePlan()` 补 clients**，而是让调度路径不再
持有 crawler；详见 `15-dscheduler-fix-reverification.md`），并以**无人值守**路径端到端复现：

| 复验证据 | 结果 |
| --- | --- |
| 独立调度进程存活 | 跨 ≥6 个 tick（13:20:23 → 约 13:25:35），日志**全程 0 字节**，无 panic |
| 无人值守触发 | **未调用 `run-due`、未启动 HTTP server** 的情况下，调度进程自行按窗口入队 87/88 等共 4 个任务 |
| 窗口键与防重 | `schedule_key='interval:5:5967136/5967137'` 非空；tick2/tick3 未新增行，`HAVING c>1` 为空 |
| Worker 执行 | 独立 Worker 写入 `started_at`/`finished_at`，4 个任务终态全部 `success` |
| 自动入池读回 | 库内新增 25 行 == 统计 `added` 合计 25（17+6+2+0）；task 88 自然呈现 `added=0/duplicate=20` |

同日追加**第二种形态**的补验（`daily HH:MM`）——首轮复验只覆盖了 `interval:N`，而回查发现
全库 `daily:` 前缀任务历史为 **0 条**，在册生产策略 id=2「三角洲热点」用的却正是 `daily 09:00`；
两者走不同的 due 判定（`discovery.go:752-783`），故单独补验：

| 复验证据（daily） | 结果 |
| --- | --- |
| 到期前 | 到期 tick（13:57:50）前 20 秒实测**仍为 0 行** → 「没到点不插」，非先插后回滚 |
| 到期那一分钟 | 恰好 1 行：`id=91`、`schedule_key='daily:2026-09-23:13:57'`、`created_at=13:57:51.824909` |
| 同一次扫描旁证 | `id=91` 创建时刻夹在 interval 的 92/93 之间 → daily 未走旁路 |
| 同日防重 | 14:01:00 实测**仍为 1 行** → 「同一日历日」窗口防重成立 |
| 进程存活 | 存活 8 分 31 秒、跨约 9 个 tick，日志**全程 0 字节** |
| Worker 执行与读回 | `success`；`started_at/finished_at` 由 Worker 写入；库内 19 行 == `added` 19 |

- **判定：复验通过。** 原「不通过」基于修复前的冻结修订 `aaf66c5`，结论对当时生效。
- **覆盖范围**：`interval:N`（85–88）与 `daily HH:MM`（91）两种周期触发形态在无人值守路径上均成立；
  `manual` 不在调度范围；非法 `schedule` 的服务端校验缺失另属缺陷 D2，不影响本项判定。
- 这是**对已执行验收轮的复验补证**，不是重开签收；**M3 仍保持 `IN_PROGRESS`**。
- 未复跑管理员 `run-due` 的防重子项（6.6/6.7）：该端点需管理员登录，会顶替用户既有会话；
  且其代码路径本次未被修改。以无人值守路径证明同一条防重逻辑，证据更强（理由见
  `15-dscheduler-fix-reverification.md` 第四节）。

### 第 3 项　各入口同一来源身份；重复与并发不重复建素材　→ **通过**

| 证据 | 结果 |
| --- | --- |
| 9.8　8 线程并发导入同一条目 | `imported=1 duplicate=7`，库中**只有 1 行** |
| 9.9　8 路并发对同一条目转素材 | material **1 行**；全库 `GROUP BY source_content_id HAVING c>1` **为空** |
| 9.10　`material_created → pending` | `409 / 14003` |
| 9.11　已忽略条目被再次发现 | 库中状态仍为 `ignored`（自动发现不复活） |
| 5.13 重复导入 | `imported=0 duplicate=2` |

身份与去重由数据库约束兜底：`unique(team_id, platform, platform_content_id)`、
`unique(material.source_content_id)`。

### 第 4 项　自动转素材 OFF / ON / 人工读回 / 不假成功　→ **通过**

| 证据 | 结果 |
| --- | --- |
| 7.1　`auto_material` 关闭 | `auto_materialized=0`，`pending=20`，库内素材 0 行 |
| 7.2　开启 + AND | `auto_materialized=12`，`pending=8`，库内素材 12 行 |
| 7.6　无关条件不参与 | 与 7.2 同值（`published_within_days` / `min_duration` 不参与判定） |
| 逐条谓词复算 | 7 个用例中**每一例**都满足「接口统计 == 库内素材行数 == 按配置复算的谓词结果」 |
| 人工转素材可读回 | 9.9 经公开接口生成 material 并读回；素材库页面走查可见（`screenshots/02-material-library.png`） |

「不假成功」由逐条复算覆盖：未出现「统计说成功、库中没有对应素材行」的情况。

### 第 5 项　规则命中/未命中均有真实证据；全非正阈值不得视为全命中　→ **通过**

| 证据 | 结果 |
| --- | --- |
| 7.3　OR + 一个阈值=0 + 另一个不可达正阈值 | `auto_materialized=0`，`pending=20` —— **证明 ≤0 是被跳过，而不是当作「全部命中」** |
| 7.4　AND + `like=0` + `favorite≥1` | `auto_materialized=17` —— 只按收藏命中 |
| 7.5　OR + `like` 不可达 + `favorite≥1` | `auto_materialized=17` —— OR 语义成立 |
| 7.0 / 7.0.1 | 命中与未命中出现在**同一任务**内（`like` 分布跨 3…186399，中位数 658） |
| 5.5.2　`auto_material:true` 且两阈值均为 0 | `400 / 14006` 创建期即拒 |
| 5.5.3　`material_rule:"XOR"` | `400 / 14006` 拒绝，未猜测降级 |

策略页走查可见三种规则的真实渲染：`赞≥2.3千`（AND）、`赞≥200000万 或 藏≥1`（OR）、`关闭`
（`screenshots/03-discovery-strategies.png`）。

### 第 6 项　统计、失败原因、受控恢复；五态边界含 `partial_success` 与失败项重试　→ **通过**

| 证据 | 结果 |
| --- | --- |
| 8.1　状态分布 | `success=54`、`partial_success=2`、`failed=4` —— 五态中四态在库中真实出现 |
| 8.2 / 8.3　`partial_success` | `import-url [真实ID, invalid-retry-test]` → `scanned=2, found=1, added=1, failed=1` → `partial_success`；判定式 `processed>0 且 failed>0` 复核一致 |
| 8.5　重试血缘 | 新任务 `parent_task_id=83`，`snapshot.retry_items` 仅含失败项 |
| 8.6　原任务不可变 | 重试后原任务仍为 `partial_success`，统计未被改写 |
| 8.7　重试只处理失败项 | 重试任务 `scanned=1`，等于 `len(retry_items)` |
| 8.4 / 8.9　负例 | 对非失败任务重试、空选择确认 → 均 `400 / 14008` |
| 8.10　未选择零写入 | `source_contents` 476→476 |
| **8.8　`material_failed`** | **首轮 NOT VERIFIED → 2026-09-23 补验通过**（受控故障注入，见下） |

#### 补验改判（2026-09-23，受控故障注入）

首轮把 8.8 记为「无法经公开 API 触发」，理由写的是「`materialize` 在 `FOR UPDATE` 下幂等」。
**该理由不成立**：本轮实测 `SELECT … FOR UPDATE` 的锁**确实挡住** `materials` 的 INSERT，
阻塞到 `innodb_lock_wait_timeout` 后报 `ERROR 1205`。首轮踩的是「用加锁读探锁」的陷阱——
**间隙锁之间互不冲突**，读探针永远测不出写入被挡，必须用写语句探（详见 `17-` 第一节）。

| 补验证据 | 结果 |
| --- | --- |
| 状态可达 | 任务 94 的 `result_json` 中 **3 条** `processing_status='material_failed'`，各带真实 `failure_reason='Error 1205 (HY000): Lock wait timeout exceeded'` |
| 非误标 | 3 条命中者 `like` = 81282 / 66706 / 72313 均 ≥ 阈值 60000；16 条 `pending` 最大 `like` = 58916 < 阈值 —— 与 `shouldAutoMaterialize` 逐条复算一致 |
| 统计自洽 | `failed=3` 且 `pending=19`，正是该分支同时 `Failed++`/`Pending++` 的结果（`19 = 16 + 3`）；终态 `partial_success` 合于 `processed>0 且 failed>0` |
| 无半写 | `materials` 全程恒为 **146**，三次失败**未留下素材行** |
| 失败原因可读 | `failure_reason` 为数据库真实错误文本，非构造串 |
| 受控恢复 | 释放锁后 `POST /crawl-tasks/94/retry-failed` → 任务 95 `success`、`auto_materialized=3`、`failure_reason` 被移除；`materials` **146 → 149**（id=151/152/153，`source_content_id` 857/864/873 一一对应） |
| 重试不重建来源 | `source_contents WHERE crawl_task_id=95` = **0** —— 走 `s.content.get()` 直接 `materialize`，故不会因唯一键判重退化为 `duplicate` 而永远转不成素材 |
| 服务端交叉核对 | 内容池 `material_created 34→37`、`pending 91→107`、总计 `125→144`，与 19 条新增来源自洽 |

- **判定：通过。** 五态中 `material_failed` 已被证实**可达、可读因、可恢复**，
  第 6 项不再带例外。
- **覆盖范围**：已覆盖可达性、`failure_reason` 写入、统计语义、失败项重试恢复、
  无半写、重试不重建来源；**未覆盖**非基础设施类失败（业务性报错）文案、
  重试后仍持续失败的分支、同一任务内 `material_failed` 与 `auto_materialized` 并存、
  以及该状态在界面上的呈现——逐项列于 `17-` 第六节，**不据此外推**。

### 第 7 项　三页面沿用 WT UI；权限拒绝、M2 回归、Cloud Web/Desktop 走查　→ **通过**

| 证据 | 结果 |
| --- | --- |
| 9.1　operator 调 `run-due` | `403 / 11003` |
| 9.2 / 9.5　operator 策略/任务列表 | `team_ids=['1']`（只见本团队） |
| 9.3 / 9.4　operator 跨组改/跑策略 | `403 / 11003` |
| 9.6　admin 任务列表 | 19 个团队可见（跨团队） |
| 9.7　批量 501 个 id | `400 / 14002` |
| 10.1　`go test ./...` | 57 个包 ok，0 FAIL |
| 10.2　vitest | 20 个文件 / 87 个用例全通过 |
| 10.3　M2 静态矩阵（原样） | FAIL —— 脚本陈旧路径（D10），非功能回归 |
| 10.4　M2 静态矩阵（仅修该路径的临时副本） | 全绿 |
| 10.5 / 10.6　M2-B 本地 | Cloud/Agent 健康通过；BitBrowser 腿经 Agent 自身代码连真实比特浏览器得 `bitbrowser_status=normal`、40 profiles |
| 10.7　**Cloud Web 视觉走查** | 四页截图，真实登录态、真实数据（内容池 319/231/87/1） |
| Cloud **Desktop** 走查 | **首轮未做 → 2026-09-23 补做**（见下） |

#### 补验改判（2026-09-23，Desktop 走查）

首轮因 Desktop 走查未执行而只能判「部分通过」。本轮以端到端脚本 `scripts/local-control.sh start`
起全链路（各检查点 PASS，DMG 构建于 14:27），对**打进 DMG 的前端产物**完成走查：

| 补验证据 | 结果 |
| --- | --- |
| 覆盖页面 | 四页在打包产物上真实渲染、真实登录态、真实数据：内容池、素材库、挖掘策略、挖掘任务 |
| 交互 1 | 策略编辑弹窗中「作者（维护中）」**禁用态**可见（`05-strategy-edit-author-disabled.png`） |
| 交互 2 | 任务详情抽屉四个标签页：结果概览 / 发现内容 / 执行过程 / 异常记录（4 张截图） |
| 交互 3 | 审核模式四按钮可见，点「跳过」后流转**真实推进**：`当前 1/91 → 2/91` |
| 界面↔接口一致 | 内容池 125 = `material_created 34 + pending 91`，审核分母 91 = pending 数，逐项相符 |
| 只读性 | 全程**零服务端写入**：打开弹窗未保存；标签页均为 GET；「跳过」在 `ContentPoolPage.vue:351-354` 于任何 `client.*` 调用前即 `return`，仅改本地索引。会写库的「转素材并下一条 / 忽略并下一条 / 保存」均未点击 |
| 新增产品事实 | Desktop **拒绝管理员与高级运营**登录（界面提示「当前角色不能登录 Desktop，请使用 Cloud Web 管理。」），只允许运营角色——非缺陷，是既有规则 |

- **判定：通过。** 首轮「Desktop 走查未做」的缺口已补齐；「只读流转视图」仍按裁定移出范围
  （见 `13-blocked-and-adjudicated.md`），不作为本项缺口。
- **覆盖范围**：已覆盖四个页面渲染、三项点击交互、运营角色全链路、界面与接口一致、只读性。
  **未覆盖**原生 Tauri 窗口取图（本环境无屏幕录制权限，取图对象是打进 DMG 的前端产物在
  Chromium 中的渲染）、Desktop 上的写操作、审核模式其余两个分支、异常态界面、多分辨率——
  逐项列于 `16-desktop-walkthrough.md` 第七节，**不据此外推**。

### 第 8 项　用户最终验收前不得标记 M3 DONE　→ **成立**

`delivery/milestones/M3-content-discovery-v2.md` 的 M3 状态未改动；本轮未激活 CHG-051。
且按本结论，在 D-scheduler 修复前也不具备标记 DONE 的条件。

2026-09-23 复验后本项**仍然成立**：D-scheduler 修复并不构成用户签收，
M3 保持 `IN_PROGRESS`，`CHG-20260915-051` 未被激活。

---

## 建议的下一步

1. ~~**修复 D-scheduler**（`schedulerResourcePlan()` 补 `clientsResource()`）~~ —— **已按更正确的修法完成
   （2026-09-23）**：不补 clients，改为让调度路径不再持有 crawler（`defaultSchedulerDiscoveryService()`）。
   理由与复验证据见 `15-dscheduler-fix-reverification.md`；`interval:N` 与 `daily HH:MM` 两种形态
   均已无人值守复验通过；残留周期策略（id=9、10、29、37）已停用并确认 0 新增任务。
   **用户 2026-09-23 裁定「scheduler 修复已完成」，此项闭环。**
2. ~~补齐 Desktop 走查与 `material_failed` 故障注入验证~~ —— **已完成（2026-09-23）**：
   Desktop 走查见 `16-desktop-walkthrough.md`；`material_failed` 受控注入与重试恢复见
   `17-material-failed-injection.md`。**验收项 6、7 的例外均已去除。**
3. **决策：daily 漏 tick 即丢当天**（2026-09-23 复验时新登记）。`daily HH:MM` 要求 tick 落在
   `HH:MM` 那一分钟内且无补偿机制：调度进程若在该分钟不在跑（或漏一次 tick），当天即无任务，
   后续 tick 不会补触发。既有设计、非本次修复引入；是否补「当天未跑则补触发」由用户裁定。
4. **修复 D3**（`CreateRun` 传空计划键）以让基线 §5「同发布队不重复排队」成立。
5. **决策 D9**：上游空返回是否应区分为「查无结果」与「上游异常」。
6. **决策 D6 / D2**：来源方式标签失真、`schedule` 无校验。
7. 处置安全问题 S-1（轮换、停止跟踪、加 `.gitignore`）。
8. 上述完成后，再进入 `CHG-20260915-051`（E3 签收）。

> 第 3–7 条（缺陷与安全问题）按用户 2026-09-23 裁定**移入 planned、另立后续 CHG**，
> 不在本 CHG 内修复；登记见 `delivery/planned/CHG-20260923-054/`。

> 本文档只做**验收判定**，不做签收。M3 是否 DONE 由用户裁定。
