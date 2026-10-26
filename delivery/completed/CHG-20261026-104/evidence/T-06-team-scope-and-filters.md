# T-06 真实 API：团队范围、加入关系与筛选（普通运营）

环境：Cloud API `127.0.0.1:8188`（pid 36043，CHG-104 代码），MySQL `wt_media_cloud`，登录用户 `operator01`（id=3，普通运营，团队 1，负责游戏 `hy`、`sjz`）。

## 团队范围

团队 1 的素材按游戏分布（`materials m JOIN source_contents sc`，2026-10-26 实测）：

| 游戏 | 素材数 |
| --- | --- |
| `hy` | 14 |
| `sjz` | 19 |
| `other` | 26 |
| 合计 | 59 |

普通运营 `GET /api/v1/materials` 读回 59 条，未按负责游戏收窄；`game_ids=hy`、`game_ids=sjz`、`game_ids=other` 分别读回 14、19、26 条，游戏只做筛选。

| 请求 | 期望 | 实际 |
| --- | --- | --- |
| `GET /materials?team_id=8` | 跨团队拒绝 | 403 `15002` 没有权限访问该素材 |
| `GET /materials/42`（团队 6） | 跨团队拒绝 | 403 `15002` |
| `POST /materials/42/usages`（团队 6） | 跨团队拒绝 | 403 `15002` |
| `POST /materials/1/usages`（团队 1，`other`） | 允许加入 | 201，usage id 92 |

本次 API 抓取原文保存在 `/tmp/chg104-api/op-team8.json`、`op-cross.json`、`op-cross-add.json` 等文件，errcode 均为 `15002`。

## 加入 / 移出 / 恢复

| 操作 | 请求 | 实际 |
| --- | --- | --- |
| 加入素材 1 | `POST /materials/1/usages` | 201，usage 92 `active` |
| 移出 | `DELETE /material-usages/92` | 204，读回 `usage_status=removed` |
| 恢复 | `POST /material-usages/92/restore` | 204，读回 `usage_status=active` |
| 加入素材 2 | `POST /materials/2/usages` | 201，usage 93 `active` |
| 加入素材 17 | `POST /materials/17/usages` | 201，usage 94 `active`；后续移出（见 T-06 成片与 Worker） |

恢复只改当前用户的关系行，没有删除或重建素材；`material_usages` 同一 `(user_id, material_id)` 始终只有一行（`status` 在 `active`/`removed` 间切换）。

## 三个使用筛选（团队 1，`game_ids=hy,sjz`）

| 筛选 | 期望 | 实际条数 | 命中 |
| --- | --- | --- | --- |
| `joined=joined` | 当前用户有效关系 | 32 | 170、172、174…（含 161） |
| `joined=not_joined` | 无有效关系（含 removed） | 1 | 33 |
| `my_usage=used` | 本人为成功成片负责人 | 1 | 170 |
| `my_usage=unused` | 其余 | 32 | 含 161（6 条历史成片、负责人 NULL）与 153（失败任务） |
| `team_usage=used` | 团队有已知负责人成片 | 1 | 170 |
| `team_usage=unused` | 其余 | 32 | 含 161（有成片但负责人未知） |

非法参数 `joined=maybe` 返回 400 `15001`。列表响应中普通运营的 `usage` 只有 `output_count` 与 `operator_count`，没有 `operators` 姓名字段（32 条结果中带 `operators` 的条数为 0）。

## 结果

PASS：普通运营可查看、加入本团队其他游戏素材，不能跨团队；游戏只影响筛选；加入/移出/恢复只改变当前用户关系；三个使用维度按成功成片与已知负责人区分。
