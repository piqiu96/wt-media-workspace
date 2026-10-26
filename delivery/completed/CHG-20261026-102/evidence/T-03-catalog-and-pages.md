# T-03：游戏目录与前端筛选／角色按钮

## 游戏目录（真实 API）

| 账号 | 请求 | 期望 | 实际 | 结果 |
| --- | --- | --- | --- | --- |
| operator01（负责 hy+sjz） | `GET /games` | 仅本人负责的启用游戏 | `hy,sjz` | PASS |
| operator01 | `GET /games?scope=all` | 全部启用游戏 | 3 行：`hy,other,sjz` | PASS |
| senior01（负责 other） | `GET /games` | `other` | `other` | PASS |
| senior01 | `GET /games?scope=all` | 3 个启用游戏 | 3 行 | PASS |
| admin | `GET /games?scope=all` | 3 个启用游戏 | 3 行 | PASS |

停用游戏仍被排除：开发库当前无停用游戏行，该分支由 `TestListAllGamesReturnsEnabledCatalogForOperators` 覆盖（构造 `retired` 停用游戏并断言不出现）。

## 页面读回（真实浏览器）

方法：Chrome 155 headless + DevTools Protocol，独立 profile；每个用例清 Cookie 后用页面同源 `fetch` 真实登录，导航到目标路由，等待路由与页面标题就绪后再读 DOM。筛选区读 `.filter-bar`，侧栏读 `.app-aside` 的 `textContent`。

| 页面 / 角色 | 读回 | 期望 | 结果 |
| --- | --- | --- | --- |
| Cloud `/content-pool` operator01 | 筛选区含「游戏」、含火影忍者与三角洲标签，无「运营团队」；表格 20 行（分页） | 默认本人游戏、无团队筛选 | PASS |
| Cloud `/content-pool` admin | 筛选区含「运营团队」与「游戏」；表格 20 行 | 管理员可跨团队 | PASS |
| Cloud `/discovery-strategies` operator01 | 无「新增策略」按钮、无「运营团队」筛选；表格 4 行 | 只读 | PASS |
| Cloud `/discovery-strategies` senior01 | 有「新增策略」，无「运营团队」筛选；表格 4 行 | 本团队可管理 | PASS |
| Cloud `/discovery-strategies` admin | 有「新增策略」与「运营团队」筛选；表格 20 行 | 跨团队管理 | PASS |
| Cloud `/crawl-tasks` operator01 | 无「运营团队」筛选，无「重试」按钮；表格 13 行 | 只读 | PASS |

页面读回 6/6 PASS；完整 10 用例（含 T-04 的 4 个 Desktop 用例）汇总见 `T-05-acceptance.md`。

## 自动门禁

- `npx vitest run`（cwd=`web/`）→ 79 文件 / 720 用例全绿。
- 页面源码断言覆盖游戏默认值、团队参数与角色按钮显隐（`ContentPoolPage.test.js`、`DiscoveryPages.test.js`、`ListPageConventions.test.js`）。
- 提交：`53e3c75`。
