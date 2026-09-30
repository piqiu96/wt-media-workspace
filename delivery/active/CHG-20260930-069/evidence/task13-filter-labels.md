# 任务 13 证据：筛选栏统一「字段标题 + 控件」（走查七轮）

日期：2026-09-30　仓库：`wt-media-cloud`　提交：`5519c1c`　范围：纯前端

## 1. 用户裁定

用户提示词第「四、筛选区域」节 + 末尾一段：所有 FilterPanel 都用「Label + Control」，
不要有的页面写「综合搜索」、有的只靠 placeholder。用户给出两个版式并推荐控件在上的那种；
在澄清问题里最终裁定**统一保持控件左侧**（沿用素材库 / 我的素材 / 内容池已经写好的
`.filter-field` 那一版，只把缺标题的三页补上）。

## 2. 动手前的实测盘点

命令：`npx vitest run src/filterPanelConvention.test.js`，扫描器跑在 `git stash` 之后的
**HEAD 工作区**上（先写守卫、读到的就是动手前的真值），逐条打印 offender。

实际：7 个页面、19 个控件（8 输入框 + 11 Select）。分布：

| 页面 | 控件 | HEAD 状态 |
| --- | --- | --- |
| `apps/cloud/pages/users/UsersPage.vue` | 2 输入 + 4 Select | **6 个全裸**；另有一个区块标题 `<span class="filter-title">筛选</span>`；原清空键叫「清空」 |
| `apps/cloud/pages/users/TeamsPage.vue` | 1 输入 | **裸**；无「重置」；查询非 Primary |
| `apps/cloud/pages/users/GamesPage.vue` | 1 输入 + 1 Select | **2 个全裸**；无「重置」；查询非 Primary |
| `modules/contentpool/pages/CrawlTasksPage.vue` | 1 输入 + 1 Select | **2 个全裸** |
| `modules/contentpool/pages/DiscoveryStrategiesPage.vue` | 1 输入 + 2 Select | **3 个全裸** |
| `modules/materials/pages/MaterialLibraryPage.vue` | 1 输入 + 2 Select | 3 个都有标题；2 个 Select 拿字段名当 placeholder |
| `modules/materials/pages/MyMaterialsPage.vue` | 1 输入 + 1 Select | 2 个都有标题；1 个 Select 同上；缺「查询」 |

（内容池两页此前被我记成「已有标题、只有 Select 的 placeholder 不对」，实测是**整行都裸着**——
这正是拿扫描器重量 HEAD 的原因，肉眼扫改过的 diff 会把标签看成原本就有的。）

## 3. 先红

新增站级守卫 `web/src/filterPanelConvention.test.js`（照 `drawerFooterConvention.test.js`
的路子写：先钉分母，再逐条断言，扫描器命中数为 0 时下面每条都在空集上通过）。

命令：`npx vitest run src/filterPanelConvention.test.js`（工作区处于 HEAD 状态）

实际：**4 条里 3 条红**，共 14 + 11 + 7 条 offender：

- 缺标题 **14** 个控件 / 6 页：UsersPage 6（UID、用户名、角色、运营分组、游戏、状态）、
  DiscoveryStrategiesPage 3（策略名称、策略类型、状态）、CrawlTasksPage 2（任务名称 / 来源策略、状态）、
  GamesPage 2（搜索游戏ID或名称、状态）、TeamsPage 1（搜索分组ID或名称）；
- Select 的 placeholder 不是「全部」**11** 个：UsersPage 4（角色 / 运营分组 / 游戏 / 状态）、
  DiscoveryStrategiesPage 2（策略类型 / 状态）、MaterialLibraryPage 2（文件状态 / 游戏）、
  GamesPage 1（状态）、CrawlTasksPage 1（状态）、MyMaterialsPage 1（文件状态）；
- 查询 / 重置 **7** 条：GamesPage、TeamsPage、UsersPage 各缺「重置」且「查询」不是 Primary，
  MyMaterialsPage 缺「查询」（UsersPage 的原按钮叫「清空」，规范 §3 的统一词是「重置」）。

分母那条是绿的（7 行 / 19 控件），说明红线不是扫描器没扫到造成的。

## 4. 实现

- 6 页的 11 个 Select：placeholder 由字段名改成「全部」（空值即不过滤，显示的正是全部）；
- UsersPage：6 个控件套 `.filter-field`，删掉那个已无必要的区块标题 `<span class="filter-title">筛选</span>`；
  「清空」改「重置」并按 §4.3 给它次级样式，「查询」改 Primary；
- TeamsPage / GamesPage / CrawlTasksPage / DiscoveryStrategiesPage：行内控件套 `.filter-field`，
  输入框按约定用字段名当标题、把原 placeholder 降级为输入提示（`分组 ID / 名称`、
  `游戏 ID / 名称`；内容池两页沿用它们自己已有的「策略名称」「任务名称 / 来源策略」）；
  TeamsPage / GamesPage 补「重置」与 `resetFilters()`，四页的「查询」改 Primary；
- 三页的 `.filter-row` 由 grid 改 flex-wrap（加标题后列数会变），并补 `.filter-field` 样式；
- MyMaterialsPage 补「查询」（接 `load()`：它的筛选是客户端即时过滤，这个按钮做的是重新拉取，
  与素材库一致——素材库的「查询」也只对 `search` 有效，文件状态与游戏同样是客户端过滤）。

## 5. 后绿

命令：`npx vitest run src/filterPanelConvention.test.js`

实际：4 passed。

**阳性对照**（证明这条断言不是空转）：把 `MaterialLibraryPage.vue` 里
「文件状态」那个 Select 的 placeholder 改回 `文件状态`，重跑 → `Tests 1 failed | 3 passed`，
失败信息指名 `MaterialLibraryPage.vue:251 「文件状态」的 placeholder 是 文件状态，不是「全部」`；
改回后复跑 4 passed。

## 6. 连带修正的既有断言

三处旧文案断言随实现更新（它们钉的是被改掉的原字面量）：

- `UsersPage.test.js`：去掉已删的「筛选」区块标题，补「用户名 / 角色 / 查询 / 重置」；
- `TeamsAndGamesPage.test.js`：`搜索分组ID或名称` → `综合搜索` + `分组 ID / 名称` + `查询` + `重置`；
  `搜索游戏ID或名称` → `综合搜索` + `游戏 ID / 名称` + `状态` + `查询` + `重置`。

## 7. 读数

- 全量 `npx vitest run`（cwd = `web/`）：**46 文件 / 373 用例全绿**（本轮前为 45 / 369，
  新增守卫 1 文件 4 用例）；
- `npm run build:cloud` exit 0、`npm run build:desktop` exit 0（均在 `.vue` 改完之后跑）；
- 提交 `5519c1c`（10 个文件）。

**读数时点**：全量与双构建在**最后一次改动之后**重跑（改的是守卫测试里的分母，
连同前面那次一起重来），不是沿用之前那轮的读数。

## 8. 边界

- 本轮只动前端，不碰后端与契约；
- 不把筛选改成服务端参数（见 `change.md` §3 与 `CHG-20260930-071` Q-06）；
- 内容池两页（crawl-tasks、挖掘策略）的筛选栏改动与它们既有的未提交改动一同提交——
  它们此前按「不属于 execute-tasks 那次删除」被留在工作区，本轮起属于本任务范围。
