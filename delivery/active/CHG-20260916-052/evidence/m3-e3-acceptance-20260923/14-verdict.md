# 验收结论：按基线 §8 逐项判定

依据：`docs/product/M3-content-mining-v2.md` §8「最终验收」当前版本。
判定只采用本次真实执行取得的证据（`run-manifest.json` 106 步）。

## 总体结论

| | |
| --- | --- |
| 可判定为通过的验收项 | 5 项（第 1、3、4、5、6 项） |
| 部分通过 | 1 项（第 7 项：Cloud Web 走查通过，Desktop 未走查） |
| **不通过** | **1 项（第 2 项：真实周期触发未交付）** |
| 状态约束 | 第 8 项成立：**未标记 M3 DONE** |

**M3 本期不能判定为验收通过。** 阻断项只有一条：**没有任何进程在执行周期调度**
（D-scheduler，独立 `cmd/discovery-scheduler` 首次 tick 即 panic 退出）。
其余功能面（入口、导入、策略配置、自动转素材、五态与重试、权限与幂等）均有完整真实证据。

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

### 第 2 项　关键词策略真实周期触发 → 任务 → 执行 → 自动入池　→ **不通过**

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

### 第 6 项　统计、失败原因、受控恢复；五态边界含 `partial_success` 与失败项重试　→ **通过（`material_failed` 除外）**

| 证据 | 结果 |
| --- | --- |
| 8.1　状态分布 | `success=54`、`partial_success=2`、`failed=4` —— 五态中四态在库中真实出现 |
| 8.2 / 8.3　`partial_success` | `import-url [真实ID, invalid-retry-test]` → `scanned=2, found=1, added=1, failed=1` → `partial_success`；判定式 `processed>0 且 failed>0` 复核一致 |
| 8.5　重试血缘 | 新任务 `parent_task_id=83`，`snapshot.retry_items` 仅含失败项 |
| 8.6　原任务不可变 | 重试后原任务仍为 `partial_success`，统计未被改写 |
| 8.7　重试只处理失败项 | 重试任务 `scanned=1`，等于 `len(retry_items)` |
| 8.4 / 8.9　负例 | 对非失败任务重试、空选择确认 → 均 `400 / 14008` |
| 8.10　未选择零写入 | `source_contents` 476→476 |
| **8.8　`material_failed`** | **NOT VERIFIED**（无法经公开 API 触发，未注入故障） |

`material_failed` 未被证实可达，是本项唯一的缺口；它不影响其余五态与重试的结论，但
基线 §3 把该状态列为处理状态之一，建议后续单独做受控故障注入验证。

### 第 7 项　三页面沿用 WT UI；权限拒绝、M2 回归、Cloud Web/Desktop 走查　→ **部分通过**

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
| Cloud **Desktop** 走查 | **未做** |

两项保留：
- 「只读流转视图」按裁定移出验收范围（见 `13-blocked-and-adjudicated.md`），不作为本项缺口；
- **Desktop 走查未执行**，故本项只能判「部分通过」。若要求覆盖 Desktop，需另立一次走查。

### 第 8 项　用户最终验收前不得标记 M3 DONE　→ **成立**

`delivery/milestones/M3-content-discovery-v2.md` 的 M3 状态未改动；本轮未激活 CHG-051。
且按本结论，在 D-scheduler 修复前也不具备标记 DONE 的条件。

---

## 建议的下一步

1. **修复 D-scheduler**（`schedulerResourcePlan()` 补 `clientsResource()`）：这是唯一的硬阻断项，
   修复后 6.2 与其下游可直接复验。
2. **修复 D3**（`CreateRun` 传空计划键）以让基线 §5「同发布队不重复排队」成立。
3. **决策 D9**：上游空返回是否应区分为「查无结果」与「上游异常」。
4. **决策 D6 / D2**：来源方式标签失真、`schedule` 无校验。
5. 补齐 Desktop 走查与 `material_failed` 故障注入验证。
6. 处置安全问题 S-1（轮换、停止跟踪、加 `.gitignore`）。
7. 上述完成后，再进入 `CHG-20260915-051`（E3 签收）。

> 本文档只做**验收判定**，不做签收。M3 是否 DONE 由用户裁定。
