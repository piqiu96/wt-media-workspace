# T-25 列表页 10 秒自动刷新

日期：2026-10-27（Asia/Shanghai）
结论：PASS（机器腿）。内容挖掘、内容生产、系统设置三个分区的 11 个列表页全部移除「刷新」按钮，改由公共 `useAutoRefresh` 每 10 秒静默重读；抽屉/弹窗/表单打开、有选中行、批量或提交进行中时跳过，页面不可见时跳过。真实页面等待读数并入 T-26。

## 提交

| 仓 | 分支 | 提交 |
| --- | --- | --- |
| wt-media-cloud | `chg/CHG-20261015-098-round3` | `940716b`（`useAutoRefresh` + 11 页 + 测试） |
| wt-media-workspace | `chg/CHG-20261015-098-docs` | 本文件所在提交（前端交互规范 §5.7、PRD 第四/五章、角色矩阵、change.md） |

## 一、公共实现

`wt-media-cloud/web/src/shared/utils/useAutoRefresh.js`：

| 项 | 行为 |
| --- | --- |
| 间隔 | `AUTO_REFRESH_INTERVAL_MS = 10000` |
| 互斥 | 上一拍未返回就跳过，慢接口不会叠请求 |
| 暂停 | `document.hidden`、`shouldSkip()` 为真、判据自身抛错时都跳过 |
| 生命周期 | 组件内 `onMounted(start)` / `onUnmounted(stop)`；节点环境由调用方启停 |
| 失败 | 吞掉 rejection，由页面的 quiet 读取自己记账；下一拍照常 |

与 `useTaskPolling` 并存：那个是「有任务在跑才轮询」的执行状态跟踪，详情抽屉仍用它；列表改由 `useAutoRefresh` 承担。

## 二、页面清单与静默语义

| 分区 | 页面 | 重读函数 | 跳过判据 |
| --- | --- | --- | --- |
| 内容挖掘 | 内容池 | `load` | 详情 / 来源 / 人工导入 / 图片查看打开、审核模式、已选行、批量或人工导入/审核处理中 |
| 内容挖掘 | 挖掘策略 | `load` | 新增编辑表单、详情、关键词、博主弹窗、保存中 |
| 内容挖掘 | 挖掘任务 | `load` | 详情、来源策略抽屉、重试中 |
| 内容生产 | 素材库 | `load` | 详情、使用情况弹窗、详情加载中 |
| 内容生产 | 我的素材 | `load` | 详情、已选行、批量下载中 |
| 内容生产 | 合成策略 | `load` | 新增编辑、复制、详情、立即执行、启停中 |
| 内容生产 | 合成任务 | `load` | 新建面板、详情、核对处置中 |
| 内容生产 | 成片管理 | `load` | 详情、已选行、批量下载、单条下载中、素材/策略/任务抽屉 |
| 系统设置 | 用户管理 | `loadAll` | 用户弹窗、重置密码弹窗、保存中 |
| 系统设置 | 运营团队 | `loadAll` | 团队弹窗、保存中 |
| 系统设置 | 游戏管理 | `loadGames` | 游戏弹窗、保存中、关联详情弹窗、关联读取中 |

所有页面的 quiet 读取统一：不置 `loading`、不清 `error`、不重置页码（成片管理沿用既有 `resetPage` 开关，定时那一遍不带它）、失败保留上一次读数。用户主动查询、重置、切筛选仍走非 quiet，显式显示 Loading 与错误。

合成任务页的列表由「有排队中/处理中任务才 5 秒轮询、跑完自停」改为同一个 10 秒定时器；详情抽屉的 5 秒轮询保留（`syncDetailPolling` 仍在）。页面不再 import `hasActiveTask`，也不自己建 timer。

## 三、文档同步

| 文件 | 变更 |
| --- | --- |
| `docs/standards/frontend/前端交互规范.md` | 新增 §5.7 自动刷新：不设刷新按钮、10 秒、公共实现、跳过条件、静默语义；本机执行面（账号/开户/窗口/代理/本地日志）明确不受此约束 |
| `docs/product/prd/详细文档/第四章_内容挖掘.md` | §4.3.5 补三个列表页的自动刷新与暂停口径 |
| `docs/product/prd/详细文档/第五章_素材生产.md` | §5.3.7 补五个列表页同一口径 |
| `delivery/.../2026-10-27-round3-role-capability-matrix.md` | 「刷新按钮」「列表刷新」两行改为已实现 |

## 四、测试读数

```
$ npx vitest run   # wt-media-cloud/web
Test Files  88 passed (88)
     Tests  799 passed (799)

$ npm run build:cloud    # ✓ built in 7.03s
$ npm run build:desktop  # ✓ built in 6.67s
```

| 用例 | 覆盖 |
| --- | --- |
| `shared/utils/useAutoRefresh.test.js`（7 条） | 10 秒默认间隔（9999ms 不触发、10000ms 触发）、重复 start 只有一个 timer、inFlight 去重、`shouldSkip` 开关、`document.hidden` 跳过、失败后下一拍照常、卸载停表（源码断言） |
| `shared/utils/autoRefreshPages.test.js`（12 条） | 11 页逐页断言：引入公共实现、`useAutoRefresh(() => load({ quiet: true })`、`shouldSkip: () =>`、quiet 不闪 Loading、不重置页码、无 `>刷新<`；另 1 条阳性对照断言账号页仍有 `>刷新<`，证明「0 命中」不是模式空转 |
| `ComposeTasksPage.test.js` | 原「有活任务才轮询」用例改写为：列表走 `useAutoRefresh`、不再有 `hasActiveTask(rows.value)` 与 `syncListPolling`、详情 `useTaskPolling` 与 `syncDetailPolling` 保留、quiet 语义保留、刷新按钮不再出现、页面无 `setInterval` |

按钮扫描（`git grep -n ">刷新<"`）：

```
$ git grep -n ">刷新<" -- src/modules/contentpool src/modules/materials src/modules/compose src/apps/cloud/pages/users
（0 行）

$ git grep -n ">刷新<" -- src/modules/accounts src/modules/profiles src/modules/proxy
src/modules/accounts/pages/AccountsPage.vue:837:  …>刷新</t-button>
src/modules/profiles/pages/ProfilesPage.vue:918:  …>刷新</t-button>
src/modules/proxy/pages/ProxyPage.vue:344:  …>刷新</t-button>
```

三条阳性对照同时说明本机执行面仍保留手动刷新，这是 §5.7 的显式例外。

## 五、覆盖边界（未覆盖项）

- **真实 10 秒读数**：定时器行为由 fake timers 覆盖；真浏览器里「等待 ≥10 秒看到列表静默更新」并入 T-26 三账号走查。
- **后台标签页跳过**：`document.hidden` 分支只有单测；浏览器节流下的实际表现未在真实环境计时。
- **静默失败无提示**：quiet 失败只保留旧数据，不显示「上次刷新失败」。这是本轮拍定的取舍（不每 10 秒打扰）；若用户需要轻量状态，另行追加。
- **目录类请求随刷新重复**：用户管理每次同时读团队/游戏、挖掘策略读任务与游戏、合成策略读模板/游戏/团队。10 秒一次在小团队规模下可接受，未做缓存分层。
- **GUI 视觉**：刷新区移除后的页头留白由 T-26 用户按打包产物确认。
