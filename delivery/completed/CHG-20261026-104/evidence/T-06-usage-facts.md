# T-06 真实 API：使用事实与任务防重

环境同上：Cloud API `127.0.0.1:8188`，用户 `operator01`（id=3，团队 1，普通运营）。

## 成功成片与“我的使用”

用一条真实合成任务产生成功成片（不是夹具里的假状态）：

| 项目 | 实际 |
| --- | --- |
| 策略 | id 46，团队 1，游戏 `hy`，负责人 3，模板 `basic_cut` v1，`manual` |
| 任务 | id 328，素材 170，负责人 3，创建人 3，`request_key=chg104-accept-0001` |
| Worker | `cmd/compose-worker` 真实认领、ffmpeg 切段、上传对象存储；任务 `success`，`stage=committing`，`progress=100` |
| 成片 | `composite_outputs.id=72`，`team_id=1`、`game_id=hy`、`material_id=170`、`material_usage_id=62`、`operator_id=3`、`object_key=compose-outputs/328/1/output.mp4`、`file_size_bytes=1046767`、`sha256=f53015e6…4223373` |

`GET /api/v1/materials/170` 读回：

```json
{"id":170,"usage_status":"active","added_at":"2026-10-03T01:46:52+08:00","my_usage":"used",
 "usage":{"output_count":1,"operator_count":1}}
```

普通运营的 `usage` 不含 `operators` 姓名；`my_usage=used` 只在“当前用户是成功成片 operator”时出现。

## 历史成片与失败任务都不算“我使用过”

| 素材 | 事实 | 读回 |
| --- | --- | --- |
| 161 | 6 条历史 `composite_outputs`，`operator_id` 全为 NULL | `my_usage=unused`，`usage.output_count=6`、`operator_count=0` |
| 153 | 有失败合成任务、无成功成片 | `my_usage=unused`，`usage.output_count=0`、`operator_count=0` |
| 17 | 当时无成功成片 | `my_usage=unused`，`usage.output_count=0`、`operator_count=0`；23:32 的跨团队非合并验收任务完成后有 1 条成功成片，见下节 |

没有从 `created_by` 回填历史负责人：161 的 6 条成片 `operator_id` 仍为 NULL，团队使用人数为 0，页面显示“姓名不可见/历史负责人未记录”。

## `(策略, 素材)` 防重与重试入口

| 请求 | 实际 |
| --- | --- |
| 同策略 46、同素材 170、新 `request_key` | 200，`created=[]`，失败项消息：`该素材在这个策略下已有任务记录，不能再次创建；如需重跑请在任务列表点「重试」` |
| 同策略 46、同素材 170、同 `request_key=chg104-accept-0001` | 200，`created=[{id:328,status:success}]`，返回原任务，不新建 |
| 失败任务 312 的 `POST /compose-tasks/312/retry`（普通运营） | 404 `15216`：任务由管理员创建，普通运营不可见；重试的角色与 15217 实测需高级运营账号 |

`(策略, 素材)` 防重仍在任务创建入口拦截，并把用户指回原任务的重试入口；本次没有修改该口径。

## 同外部作品跨团队不合并

素材 17（团队 1）与 42（团队 6）来自同一外部作品：

```text
platform=douyin  platform_content_id=7631846559986060554
material 17 → team 1 / other
material 42 → team 6 / other
```

为了让“有成功成片的一侧”可核实，用策略 48（团队 1、`other`、负责人 3）建立验收任务 330，由真实 `cmd/compose-worker` 下载源、ffmpeg 切段并提交：

| 项目 | 实际 |
| --- | --- |
| 任务 | 330，策略 48，素材 17，负责人 3，`success`，`stage=committing`，`progress=100` |
| 成片 | `composite_outputs.id=73`，`team_id=1`、`game_id=other`、`material_id=17`、`material_usage_id=94`、`operator_id=3`、`object_key=compose-outputs/330/1/output.mp4`、1,211,720 字节 |

普通运营读回素材 17：

```json
{"id":17,"usage_status":"removed","my_usage":"used","usage":{"output_count":1,"operator_count":1}}
```

同一 SQL 投影按 `(material_id, operator_id)` 分组并 join 素材所属团队：

```sql
SELECT o.material_id,o.operator_id,COUNT(*) FROM composite_outputs o
JOIN materials m ON m.id=o.material_id AND m.team_id=o.team_id
WHERE o.material_id IN (17,42) GROUP BY o.material_id,o.operator_id;
```

实际只有一行：`17 | 3 | 1`；素材 42 没有行，尽管它与 17 是同一外部作品。成片 73 的 `team_id=1` 也只计入团队 1 的素材 17。团队 1 的 `other` 26 条素材中，`my_usage=used` 与 `team_usage=used` 各 1 条（均为素材 17）；团队 6 的素材 42 不在团队 1 的任何读数里。

任务 330 的创建方式说明：operator01 的游戏范围是 `hy,sjz`，策略 47/48 的游戏是 `other`，经 API 创建会按策略可见性返回 15216；因此验收任务行按任务 329 的同一快照写入（策略 48、素材 17、负责人 3），Worker 执行与成片提交都是真实的。策略 48 是验收夹具，收尾时与任务 329/330 一并清理。

## 结果

PASS：只有“当前用户是成功成片负责人”才进入我的使用；失败、取消、排队中和历史 NULL 负责人都不算；既有防重与重试入口保持原行为；同外部作品在两个团队的素材分别计数，不合并。高级运营/管理员的范围与重试路径见 `T-06-role-scope.md`。
