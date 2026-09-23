# M3 内容挖掘全量功能验收：运行说明与结论

- 执行日期：2026-09-23（UTC 记录窗口 2026-09-22T21:50:59Z → 2026-09-22T22:18:17Z）
- 执行者：Claude Code（用户指令「你自行启动服务对功能进行一次全量验收」）
- 落点：`wt-media-workspace/delivery/active/CHG-20260916-052/evidence/m3-e3-acceptance-20260923/`
  （当前 active 的 CHG 是 052；`delivery/active/` 的单 active 硬校验不允许本轮另开 CHG-051）
- 执行脚本：`wt-media-workspace/scripts/verify_m3_acceptance.py`（仅标准库，可重复执行）
- 渲染脚本：`tools/render-evidence.py`（把 `run-manifest.json` 渲染成各阶段证据文件）
- 视觉走查工具：`tools/cookie-proxy.py`（注入会话 cookie 的本地反向代理）

## 1. 冻结的修订

| 仓库 | 冻结 HEAD | 收尾时是否一致 |
| --- | --- | --- |
| wt-media-cloud | `aaf66c51bab68c5fddfd0648e347356e37dcb29e` | 一致（收尾复核） |
| wt-media-workspace | `4f44ffd16016752d53f923614614b2d7dc3afae5` | 一致 |
| wt-media-agent / wt-media-desktop | 未改动（`git status --porcelain` 为空） | 一致 |

验收全程 **未修改任何运行时源码或配置**。Cloud 仓库在验收前后 `git status --porcelain` 均为空。

## 2. 判定总览

清单共 **106 步**（`run-manifest.json`）：

| 判定 | 步数 | 含义 |
| --- | --- | --- |
| PASS | 87 | 期望与实际一致 |
| FAIL | 7 | 实现或文档缺陷，全部登记在 `12-defects-and-security.md` |
| NOT VERIFIED | 1 | 8.8 `material_failed` 无法经公开 API 触发，且本轮不注入故障 |
| ADJUDICATED | 1 | 10.8 只读业务流转视图，按用户裁定移出验收范围 |
| INFO | 10 | 环境、基线、残留等事实记录，不含通过与否判定 |

7 条 FAIL **全部**是已登记缺陷的实测证据，不是验收执行失败：

| 步骤 | 缺陷 | 现象 |
| --- | --- | --- |
| 5.2b / 5.15 | D9 | 上游 `/batchDyVideo` 间歇性 `result=1` 空 `data`，Cloud 如实透传为「成功且无结果」 |
| 5.5.8 | D1 | 策略重名返回 HTTP 500 / 50000，而非 409 / 14007 |
| 5.5.9 | D2 | `schedule="garbage"` 被接受（201），无服务端格式校验 |
| 6.2 | D-scheduler | 独立 `cmd/discovery-scheduler` 首次 tick 即 panic 退出 |
| 6.9 | D3 | `POST /discovery-strategies/:id/run` 连调两次产生 2 条 pending，违反基线 §5「不重复排队」 |
| 10.3 | D10 | `scripts/verify_m2_acceptance.py:71` 指向已迁移的文件路径 |

详细登记见 [12-defects-and-security.md](12-defects-and-security.md)。

## 3. 外部依赖分支：REAL-OK

G4 用真实请求判定，结论为 **REAL-OK**（见 [03-external-reachability.md](03-external-reachability.md)）：
抖音上游 `api.itfaba.com` 在全程可达，关键词搜索返回真实内容，且搜索是同步只读、对
`source_contents` 零写入（319 → 319）。因此阶段 5–9 走的是完整分支，未使用任何 mock 或夹具替代真实业务读回。

同时如实记录 D9：上游 `/batchDyVideo`（按 ID 取详情）**间歇性**返回 `result=1` 且 `data` 为空，
实测 8 次里 2 次空返回，重试可恢复。这是上游行为，不是 Cloud 的缺陷；但 Cloud 把它透传为
「成功、0 条发现」，用户侧看不到任何错误提示，这一用户体验问题计入 D9。

## 4. 既有数据未被破坏

首轮基线快照冻结于 2026-09-22T21:14:30Z：3 策略 / 11 任务 / 109 来源 / 26 素材。
验收结束后，基线区间内的行**逐项一致**（`run-manifest.json` 的 11.3.* 四步均 PASS）：

```
discovery_strategies  id<=3   → 3 行（基线 3）
crawl_tasks           id<=33  → 11 行（基线 11）
source_contents       id<=165 → 109 行（基线 109）
materials             id<=26  → 26 行（基线 26）
```

本轮新增行全部登记、**未做任何删除**，见 [11-residue-teardown.md](11-residue-teardown.md)。

## 5. 需要说明的两处执行瑕疵（已在脚本中修复）

如实披露，因为它们影响证据的读法：

1. **清单拼装缺陷（已修）**：`main()` 原先在阶段抛异常时会把「只装了一半新结果」的清单
   写回文件，导致首轮已完成的 G0–P6 记录被覆盖。发现后已改为「新结果先写入独立列表，
   阶段成功才与原清单合并」，并**重跑了 G0–P11 全量**。当前清单的 106 步全部来自这次
   完整重跑，同一 Cloud HEAD、同一环境，结论与首轮一致（阶段 6/7/8/9 的关键判定逐条复现）。
2. **基线快照被重跑覆盖（已还原）**：重跑 G1 时 `02-baseline-snapshot.md` 被中途快照覆盖。
   原始 SQL 快照 `02-baseline-snapshot.sql.txt`（05:11 落盘）未被覆盖；据此按冻结的
   `max_id` 重建了 `02-baseline-snapshot.md`，重建后行数与基线逐项吻合（11 / 109）。
   被覆盖的那份另存为 `02b-midrun-snapshot-20260923T055100Z.md`。G1 已改为基线只冻结一次。

另需说明：**既有 pending 任务 id 33（策略 3）在本轮开始前就存在**，Worker 一启动即被领取并执行完成
（`added=16, found=20, duplicate=4, auto_materialized=8, pending=8`）。这是既有任务的正常执行，
**不是本轮验收的产物**，但确实消耗了它，特此标注。

## 6. 环境与范围

- MySQL 8.4.10 @ 127.0.0.1:3306，库 `wt_media_cloud`（26 表 / 39 条迁移，最新 `20260922_038`）
- Cloud API `http://127.0.0.1:18080`；Cloud Web 走 Vite `127.0.0.1:5180`
- 账号：`admin/admin123`（跨团队）、`senior01/senior123`（`senior_operator`，团队 1）
- 隔离组：`M3验收-隔离组-20260923`（team_id=2）
- 上游：`api.itfaba.com:443`（真实抖音数据接口）
- 凭据：全程只记录键名与字节长度，**证据中不含任何凭据值**（脱敏在 `redact()` 中统一处理）

**未做**：不改运行时代码、不标 M3 DONE、不激活 CHG-051、不动
`config/credentials/douyin.toml`、不清理 git 历史、不碰 CHG-053。

## 7. 文件索引

| 文件 | 内容 |
| --- | --- |
| `01-freeze-and-preconditions.md` | G0–G3 冻结、环境、登录与样本 |
| `02-baseline-snapshot.md` | 首轮冻结基线（含重建说明） |
| `02b-midrun-snapshot-*.md` | 重跑 G1 时的中途快照（另存，非基线） |
| `03-external-reachability.md` | G4 外部可达性决策 |
| `04-entries-and-import.md` | 内容池入口、导入、负例 |
| `05-strategy-config.md` | 策略配置矩阵与负例 |
| `06-scheduling.md` | 周期触发、窗口键、双层防重 |
| `07-auto-material.md` | 自动转素材规则矩阵（含逐条谓词复算） |
| `08-five-states-retry.md` | 五态、`partial_success`、失败项重试 |
| `09-permissions-idempotency.md` | 权限拒绝与并发幂等 |
| `10-regression-walkthrough.md` | go test / vitest / M2 回归 / 视觉走查 |
| `11-residue-teardown.md` | 残留登记与进程收尾 |
| `12-defects-and-security.md` | 缺陷登记与安全问题登记 |
| `13-blocked-and-adjudicated.md` | BLOCKED / NOT VERIFIED / ADJUDICATED 清单 |
| `14-verdict.md` | 按基线 §8 逐项给出验收结论 |
| `run-manifest.json` | 106 步的机器可读清单 |
| `raw/` | 原始响应（脱敏）、日志、grep 取证 |
| `screenshots/` | 四个页面的无头 Chrome 截图 |
| `tools/` | 走查代理与渲染脚本 |
