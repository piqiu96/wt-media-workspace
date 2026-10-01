# 任务 11 证据：走查六轮（详情平铺、标题与作者可跳转、游戏独立行）

- 日期：2026-09-30
- CHG：CHG-20260930-069（M4-A 素材详情与下载中心走查修正）
- 仓库：`wt-media-cloud`（前端）
- 提交：`004272d`（`feat(chg-069): 详情平铺、标题与作者可跳转（走查六轮）`）
- 附带：`71deb48` 含本任务文件去冗余注释后的回写（与任务 12 同一次提交）

## 0. 用户反馈原文（三条）

1. 游戏是独立行；
2. 详情里对应的 TAB 切换取消，直接平铺在一页，当前内容较少；
3. 素材关联内容的标题点击可以去落地页，作者信息也需要有，同时作者也是可以点击跳转。

同一轮内追加的范围修订（改变任务 9 的「后端另立 CHG」裁定）：

> 素材状态的值当下是可以有数据的，是素材库的内部职责，需要完成状态展示。

该修订由任务 12 承载；本任务只做上面三条纯交互层改动。

## 1. 红：先钉住目标形态

**命令**：`npx vitest run src/modules/materials/MaterialDetailDrawer.test.js`

**预期**：四条新断言失败，其余保持绿——红要落在「新要求」上，不能靠编译不过。

**实测**：4 failed / 16 passed。失败项即本轮要做的四件事：

| 断言 | 期望 |
| --- | --- |
| `lays the sections out flat instead of behind tabs` | 无 `t-tabs` / `t-tab-panel` / `activeTab`；五张 `.detail-card` 依序 |
| `links the hero title to the source landing page` | hero 标题是 `source_url` 外链 |
| `makes the author in the hero clickable too` | hero 副行作者是 `author_home_url` 外链 |
| `keeps 游戏 out of the hero source line` | `detail-source-line` 内不含 `gameName` |

## 2. 绿：最小实现

- 删掉 `activeTab` ref 与两处标签重置；五个面板的 `t-tab-panel` 换成平铺的 `.detail-card`
  （顺序：使用情况 → 基本信息 → 文件信息 → 来源信息 → 来源内容池统计）；
  间距从 `.detail-tabs` 的 margin 改为 `.detail-workspace` 的 `gap: 14px`。
- hero 标题在 `material.source_url` 存在时渲染蓝色外链（`target="_blank" rel="noopener noreferrer"`），
  否则退回普通文本——链接形状留给真能点的东西。
- 副行作者同理挂 `material.author_home_url`。
- 副行去掉游戏名（它在列表有列、在「基本信息」有行）。

**命令**：`npx vitest run src/modules/materials` → 68 passed（6 文件）。

## 3. 一处自己踩的坑（记录为方法，不是产品事实）

平铺后那条「五张卡依序」的断言最初用裸词扫描 `template`，被我自己刚写在模板里的注释
判反：注释里的「基本信息」在偏移 752，真正的卡片标题在 2232，`indexOf` 先撞上注释。
改为按标记取标题（`class="detail-card__title">` + 中文词）后成立。

同一文件里 `keeps 游戏 out of the hero source line` 断言的切片也不含模板注释，
是因为切片起点取在 `detail-source-line` 标记上，注释在该标记之前。

## 4. 复验读数（注释收敛后重跑）

- `npx vitest run src/modules/materials` → 6 文件 / 68 用例全绿；
- 全量 `npx vitest run` → **Test Files 1 failed | 44 passed (45)**、**Tests 1 failed | 368 passed (369)**；
  唯一失败是 `src/localSettingsWiring.test.js`（桌面路由数量 `expected 20 to be greater than 20`），
  根因是工作区里本 CHG 暂存范围之外的未提交改动删掉了 `execute-tasks` 路由（`web/src/apps/desktop/router.ts`
  与 `web/src/modules/tasks/pages/TasksPage.vue` 的删除均不在本 CHG 暂存范围），与本任务无关；
  **更正**：该删除后来按「单仓任务」独立提交（`029ae3a` / `5c3a5fa`），下限改为实测的 20，
  全量随之复绿（45 文件 / 369 用例），详见 `checkpoint.md` 的范围外备注；
- `npm run build:cloud` exit 0、`npm run build:desktop` exit 0。

## 5. 边界

- 本轮不改后端：三条反馈都是交互层。
- 交互层之外的那条追加修订（素材状态有真值）走任务 12。
- 用户对「游戏是独立行」的裁定同时撤销了任务 10 里登记的那处偏差（原设计图副行写
  「douyin · 三角洲行动」），`change.md` §4 的偏差登记随之撤下。
