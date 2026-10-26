# T-05：综合验收

## 代码与合并

| 仓 | 提交／PR | CI | 合并 |
| --- | --- | --- | --- |
| `wt-media-cloud` | [PR #8](https://github.com/piqiu96/wt-media-cloud/pull/8)，分支 `chg/CHG-20261026-102`，末次代码提交 `1f54e42` | `verify` pass，2m39s | merge commit `cb26c66`，2026-10-26T10:12:58Z |
| `wt-media-workspace` | 本记录所在分支 `chg/CHG-20261026-102` | 收尾时运行，见下 | 由本记录所在 PR 合入 |
| `wt-media-desktop` | 无源码改动 | — | — |

合并后 Cloud `main` 工作树干净；下面实时读回在合并后的代码树上执行，代码与 `1f54e42` 相同。

## 自动门禁（收尾重跑）

| 门禁 | 命令 | 读数 | 结果 |
| --- | --- | --- | --- |
| Cloud Go | `go test ./... -count=1` | exit 0；72 包 `ok`、0 `FAIL`、11 个无测试文件包 | PASS |
| Cloud Web | `npx vitest run`（cwd=`web/`） | 79 文件 / 720 用例通过 | PASS |
| Cloud control | `bash scripts/verify/test-control.sh` | 12 passed, 0 failed | PASS |
| Workspace | `PYTHONDONTWRITEBYTECODE=1 python3 scripts/wt.py test repo --repo wt-media-workspace` | `Ran 174 tests ... OK`；治理、AI 工作区、技能、产品对齐、M0 配置、文档索引、control 校验全部 ok | PASS |
| PR CI | GitHub `verify` | pass，2m39s | PASS |

`python3 scripts/wt.py chg verify CHG-20261026-102`（H 风险）：Workspace 174 用例、Cloud `go test ./internal/modules/...`、Desktop `scripts/test.sh` 均通过；最后一步固定调用 `verify_m1_integration.py`，因导入已退役的 `wt_media_agent.cloud_agent_client` 报 `ModuleNotFoundError` 退出 1。该脚本在 `scripts/README.md` 第 25 行已标注“行为已知阻塞”，与 CHG-101 收尾时的现象相同，不属于本 CHG 的运行时回归；本 CHG 的真实读数以上面的门禁与实时读回为准。

## 实时读回（收尾重跑）

- **API 38/38 PASS**：T-01 的 7 个普通运营写入口全部 11003；高级运营跨团队创建／列表 11003；管理员缺团队 14009、带团队创建与列表成功；内容忽略／恢复回读一致；游戏筛选矩阵 7 项；游戏目录 5 项；Desktop 登录与 Agent Token 拒绝 5 项；会话冲突／替换 5 项。
- **页面 10/10 PASS**：Cloud 6 个用例（内容池、策略、任务按角色读回筛选与按钮），Desktop 4 个用例（高级运营／管理员被拦回内容池且本机菜单不可见、个人信息页无本机区块、普通运营阳性对照五项菜单齐全）。
- **拒绝无写入**：拒绝矩阵前后 `discovery_strategies`（team 1）4→4、`crawl_tasks` 73→73、`source_contents` 664→664；探测行与忽略状态在验证后还原。
- **迁移可重放**：`go run ./cmd/migrate` → `0 applied, 75 total`；手工重放 `20261026_073` 的 SQL 两次后 `operation_games` 的 `other` 仍为 1 行，且保留了库中 2026-09-04 已有的 remark 与 `created_at`（`INSERT IGNORE` 不覆盖既有行）。
- **Desktop 产物**：前端戳 `source_commit=1f54e42`、`source_dirty=false`、digest `4d867c97137722fd794ba4dd38aec0cece022377031a76d3460ef428c783ff9c`；`cargo tauri build --no-bundle` 产物 24,509,280 bytes，资产文件名在二进制中命中；详见 `T-04-desktop-boundary.md`。

逐项矩阵与命令见 `T-01-role-gates.md`、`T-02-game-filter.md`、`T-03-catalog-and-pages.md`、`T-04-desktop-boundary.md`。

## Done When 对照

| Done When | 证据 | 结果 |
| --- | --- | --- |
| 普通运营处理本团队所有游戏内容；游戏多选默认本人负责项且不越团队 | T-02：默认 hy+sjz 147 行、改选 other 109 行、无筛选 256 行、伪造 `team_id` 11003；T-03 页面读回游戏筛选与本人游戏标签；T-01 忽略／恢复 906 读库一致 | PASS |
| 普通运营不能写策略或处置任务异常；高级运营限本团队；管理员明确目标团队后跨团队 | T-01：7 个写入口 11003 且计数不变；senior 指定 team 2 被拒；admin 缺 team 400/14009、带 team 创建与列表成功 | PASS |
| Cloud Web／Desktop 共用页面显示与 API 权限一致，拒绝无业务写入 | T-01 服务端拒绝＋计数；T-03 页面 6 例；T-04 页面 4 例；前端仅隐藏按钮，门禁在服务端 | PASS |
| 管理角色可登录 Desktop 与操作 M3 页面，但不能取得本机执行凭证；会话冲突／替换仍生效 | T-04：senior/admin Desktop 登录成功、Agent Token 403/11003；四条 M2 路由重定向、菜单与本机卡片隐藏；普通运营阳性对照；20010／替换／旧 token 401／登出 200 | PASS |
| `source_content` 团队唯一性与忽略语义、调度与 M3 路径回归；真实请求／数据库／页面读回 | 未改 `source_contents` 表与忽略逻辑；T-01 忽略／恢复与计数；迁移重放；Go 全量套件含 `contentpool`、`scheduler`；API 38/38 与页面 10/10 | PASS |

## 覆盖范围与未覆盖项

- **已实测**：上面列出的 API 入口、数据库计数、Cloud／Desktop 页面读回、迁移重放、Desktop 二进制资产锚点。
- **仅自动测试覆盖**：普通运营的 Desktop 会话换 Agent Token 正向链路（开发库中 operator01 只有一条属于用户本机的真实会话，现场登录会触发 20010 替换）；停用游戏仍被 `/games?scope=all` 排除；管理员跨团队的编辑／启停／删除／执行逐入口未全部现场发请求，现场实测的是创建与列表，其余入口共用同一角色门禁与团队解析路径。
- **未触发**：未执行真实外部抓取。拒绝写入口的判据是数据库零行增量与无新任务，不以外呼日志为判据；未做的入口不据此推断为已覆盖。
- **留给用户**：Tauri 安装包 GUI 走查（本机无法程序化驱动 GUI，二进制只做到资产级闭合）。
