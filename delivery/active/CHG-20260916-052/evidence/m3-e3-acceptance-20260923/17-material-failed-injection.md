# 补验：`material_failed` 受控故障注入与受控恢复

- 日期：2026-09-23
- 覆盖验收项：`14-verdict.md` 第 6 项（五态边界与失败项重试）之 8.8
- 原始记录：`raw/p17-material-failed-injection.txt`（带时点的 T0–T5 全过程）
- 首轮状态：**NOT VERIFIED** —— 见 `13-blocked-and-adjudicated.md` 第一节
- 本轮结论：**已证实可达，8.8 由 NOT VERIFIED 改判通过**

## 一、为什么首轮是 NOT VERIFIED

首轮验收把 8.8 记为「无法经公开 API 触发」，并给了一个技术解释：

> `materialize` 在 `FOR UPDATE` 下幂等，正常路径不会失败；要触发它必须注入数据库故障或违反约束。

**这个解释是错的**，本轮实测推翻：`SELECT … FOR UPDATE` 持有的锁**确实会挡住** `materials` 的
INSERT，阻塞到 `innodb_lock_wait_timeout` 后报 `ERROR 1205`。

错因值得记录，因为它是一个可复现的**探测陷阱**：间隙锁之间**互不冲突**，因此用「加锁读」
（`SELECT … FOR UPDATE NOWAIT`）永远探测不到锁冲突，会被误读为「锁不住写入」。
本轮最初也踩了同一坑（见 `raw/p17` T0.2），改用**真实 INSERT 语句 + `ROLLBACK`** 才得到
`ERROR 1205`。结论：**判断锁是否挡住写，必须用写语句探，不能用读语句探。**

## 二、注入手法（不碰运行时代码、不碰表结构）

| 维度 | 做法 |
| --- | --- |
| 触发路径 | **公开 API**：`POST /discovery-strategies/38/run`，再启动独立 `cmd/discovery-worker` |
| 策略 | 走 `POST /discovery-strategies` 真实创建（未直接 INSERT），`auto_material:true`、`material_rule:"OR"`、`like_threshold:60000` |
| 故障注入 | 第二个 MySQL 会话持有 `materials` 全表 X 锁（含唯一二级索引的 next-key/supremum 锁） |
| 判据 | 插入阻塞 → `materialize` 返回错误 → `projectDiscoveredItem` 落 `material_failed` |
| 未使用 | 未改任何 Go 源码、未改 DDL、未 mock crawler、未改配置、未绕过鉴权 |

选「锁等待」而不是「改表结构 / 加非法约束」的理由：它是**纯运行时、可逆、无残留**的注入——
释放锁即恢复，不留 schema 变更；且失败由数据库真实抛出，`failure_reason` 是上游真实错误文本，
不是构造出来的字符串。

## 三、结果：状态可达

任务 94（`discovery_task`，策略 38，team 1）

```
status        = partial_success
started_at    = 2026-09-23 14:39:14.987   （Worker 写入）
finished_at   = 2026-09-23 14:41:50.301   （耗时 155.3s ≈ 3 × innodb_lock_wait_timeout(50s)）
stats_json    = {"added":19,"found":20,"failed":3,"pending":19,"scanned":20,
                 "duplicate":1,"auto_materialized":0}
```

`result_json` 20 条的 `processing_status` 分布：`pending=16`、**`material_failed=3`**、`duplicate=1`。

三条 `material_failed` 逐条（`like_count` 均 ≥ 60000，即**确实走到了 `materialize`**）：

| platform_content_id | like | favorite | source_content_id | failure_reason |
| --- | --- | --- | --- | --- |
| 7658590066154949929 | 81282 | 10003 | 857 | `Error 1205 (HY000): Lock wait timeout exceeded; try restarting transaction` |
| 7642658407740083507 | 66706 | 34225 | 864 | 同上 |
| 7463510597309664566 | 72313 | 15676 | 873 | 同上 |

四项交叉校验，使「这三条是被正确归类，而不是被误标」：

1. **阈值语义**：16 条 `pending` 的 `like_count` 最大值为 58916 < 60000，三条命中者最小 66706
   ≥ 60000 —— 命中/未命中与 `shouldAutoMaterialize`（`discovery.go:535`）逐条复算一致。
2. **计数自洽**：`failed=3` 且 `pending=19`，正是 `material_failed` 分支同时
   `Stats.Failed++` 与 `Stats.Pending++` 的结果（`discovery.go:400-404`），
   `19 = 16（未命中阈值）+ 3（转素材失败）`。
3. **半写检查**：`materials` 全程恒为 **146**，三次失败**未留下任何素材行**——
   「转素材失败」没有变成「写了一半」。
4. **终态自洽**：`processed>0 且 failed>0 → partial_success`，与既有判定式一致。

因此 `material_failed` **是一条真实可达、且统计与状态机自洽的处理状态**；基线 §3 把它列为
处理状态之一有实现依据，不是纸面枚举。

## 四、受控恢复：`retry-failed` 真的能把失败项救回来

释放锁后对任务 94 调用 `POST /crawl-tasks/94/retry-failed`：

| 项 | 值 |
| --- | --- |
| 新任务 | `id=95`，`task_type=retry_failed_task`，`parent_task_id=94`，`snapshot.retry_items` **仅含 3 条 `material_failed` 项** |
| 终态 | `success`，`started_at=14:42:30.345` → `finished_at=14:42:30.378`（33ms） |
| 统计 | `{"scanned":3,"found":3,"auto_materialized":3,"failed":0,"pending":0,"duplicate":0,"added":0}` |
| 三条结果 | 全部 `auto_materialized`，`material_id` = 151 / 152 / 153，`failure_reason` 已被移除 |
| 素材库读回 | `materials` **146 → 149**，新行 `source_content_id` = 857 / 864 / 873，与三条一一对应 |
| 原任务 | 任务 94 仍为 `partial_success`，统计未被改写（血缘与不可变性同时成立） |

值得单独指出的一点：**重试没有重建来源行**。`executeRetryClaimed` 对 `material_failed` 走的是
`s.content.get(sourceID)` 取既有 source 再直接 `materialize`（`discovery.go:463-479`），
**不重新 `createSource`**。实测 `source_contents WHERE crawl_task_id=95` = **0 行**证实了这一点。

这条设计是必要的：若重试重走 `createSource`，唯一键 `(team_id, platform, platform_content_id)`
会判重，条目会退化成 `duplicate` 而**永远转不成素材**——即失败项无法恢复。实测证明该路径正确。

## 五、对基线 §8 第 6 项的判定影响

第 6 项要求「统计、失败原因、受控恢复；五态边界含 `partial_success` 与失败项重试」。
补验前，该项因 8.8 无法证实而**只能判「通过（`material_failed` 除外）」**。补验后：

| 子项 | 补验前 | 补验后 |
| --- | --- | --- |
| 五态中 `success` / `partial_success` / `failed` / `pending` | 已有真实库证据 | 不变 |
| `material_failed` 可达 | NOT VERIFIED | **通过**（本文件第三节） |
| 失败原因可读 | 仅 `failed` 项有 | **`material_failed` 也带真实 `failure_reason`**（本文件第三节） |
| 失败项受控恢复 | 仅 `failed` 项验过 | **`material_failed` 项重试恢复为 `auto_materialized`**（本文件第四节） |

→ **第 6 项改判为「通过」，不再带例外**（`14-verdict.md` 已同步）。

## 六、覆盖范围与未覆盖（逐项枚举，不用同一实现外推）

**已覆盖**：

- `material_failed` 的**可达性**与 `failure_reason` 写入 —— 真实 Worker 进程、真实 MySQL 错误。
- `material_failed` 的**统计语义**（`failed` 与 `pending` 同时 +1）。
- 失败项的**重试恢复**（`retry_failed_task` → `auto_materialized` → 素材库 +3）。
- 重试**不重建来源行**（`source_contents` +0）。
- 失败**不产生半写素材行**（`materials` 全程 146）。
- 服务端交叉核对：内容池 `material_created 34→37`、`pending 91→107`、总计 `125→144`。

**未覆盖**（据此**不**外推为已验证）：

1. **非基础设施类的 `materialize` 失败**：本轮失败原因只有 `1205 锁等待超时`一类。
   源内容被删除、素材唯一键冲突等业务性失败的错误文案与呈现，**未验证**。
2. **重试后仍持续失败**：即重试任务自身再次落 `failed` 的分支，**未构造**。
3. **同一任务内 `material_failed` 与 `auto_materialized` 并存**：本轮锁使**所有**命中项都失败
   （`auto_materialized=0`），混合样本**未构造**。第 6 项要求的「不假成功」在单任务内
   缺少混合分布的直证；既有的逐条谓词复算（阶段 7，7 个用例）覆盖的是另一条路径。
4. **界面呈现**：本轮只读回接口与库。素材库页只呈现已入库素材，`material_failed` 项在界面上
   的可见位置、文案与重试入口**未做视觉取证**。
5. **并发下的注入**：单 Worker 串行执行，未覆盖多 Worker 并发时的失败计数竞争。

第 2、3 条不构成第 6 项的缺口（基线只要求状态可达、失败原因可读、失败项可重试，三者均已证），
但按「证据覆盖面要枚举」的纪律如实列出，供后续需要时单独补验。

## 七、残留登记

本轮新增行**只登记不删除**（与既有验收纪律一致）：

| 表 | 新增 | 说明 |
| --- | --- | --- |
| `discovery_strategies` | +1 | `id=38`，已由 `enabled` 改为 **`disabled`**（行保留） |
| `crawl_tasks` | +2 | `id=94`（`partial_success`）、`id=95`（`success`） |
| `source_contents` | +19 | 全部由 `crawl_task_id=94` 产生；`task 95` 新增 0 |
| `materials` | +3 | `id=151/152/153`（自增号 147–150 因失败尝试与探针消耗未落行） |

既有行未被修改或删除：`materials id<=146` 仍为 146 行、`crawl_tasks id<=93` 仍为 71 行、
无遗留非终态任务、既有策略状态（含生产在册的 `id=2`「三角洲热点」）未改动。

收尾：`cmd/discovery-worker` 已 `pkill`，持锁会话已释放，两者残留检查均为空。

安全：全程未使用 mock 凭据；数据库口令从 `config/database/primary.toml` 读入环境变量，
未落盘、未打印；本文件与 `raw/p17` **不含任何凭据值**（无 Cookie、无 api_key）。
