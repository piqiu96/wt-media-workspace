# T-02：内容池游戏多选与默认游戏

## 环境

- 同 T-01：Cloud `chg/CHG-20261026-102` HEAD `1f54e42`，API 8188，开发库 `wt_media_cloud`。
- 迁移 `20261026_073_ensure_other_game` 已应用（`1 applied, 75 total`）。
- 数据底座（直接 SQL）：team 1 内容 hy=30、other=109、sjz=117，合计 256；`operation_games` 启用 3 个（hy/other/sjz）。

## 筛选矩阵（operator01 真实请求，期望均带团队边界）

| 场景 | 请求 | 期望 | 实际 | 结果 |
| --- | --- | --- | --- | --- |
| 默认本人游戏 | `GET /content-pool?game_ids=hy,sjz` | 147 行，仅 hy/sjz | 147 行，games=`hy,sjz` | PASS |
| 选择非本人负责游戏 | `GET /content-pool?game_ids=other` | 109 行 | 109 行 | PASS |
| 重复游戏 ID | `GET /content-pool?game_ids=hy,hy,sjz` | 与 hy+sjz 相同 | 147 行 | PASS |
| 不带筛选 | `GET /content-pool` | 团队全部 256 行 | 256 行 | PASS |
| 伪造 team_id 借游戏筛选 | `GET /content-pool?game_ids=hy&team_id=2` | 403/11003 | 11003 | PASS |
| 管理员跨团队 + 游戏 | `GET /content-pool?team_id=1&game_ids=hy` | 30 行 | 30 行 | PASS |
| 非法长列表 | 51 个 `game_ids` | 400/10001 | 10001 | PASS |

## 默认游戏

| 场景 | 请求 | 实际 | 结果 |
| --- | --- | --- | --- |
| operator01 新建来源不带 game_id | `POST /content-pool`，platform=douyin，platform_content_id=`chg102-probe-<ts>` | `game_id=other`（HTTP 201） | PASS |

探针行在验证后按主键删除；`source_contents` 总数 664 → 664。策略创建/更新的默认游戏由 T-01 的 `TestStrategyDefaultsGameToOther` 覆盖，真实请求侧由 senior01 创建不带 game 的策略读回 `other` 佐证。

## 自动门禁

- `go test ./... -count=1` → 72 包 ok、0 FAIL；含 `TestParseGameIDsAcceptsCommaSeparatedValues`、`TestStrategyDefaultsGameToOther`、SQL 条件单测。
- 提交：`7f72dbf`。
