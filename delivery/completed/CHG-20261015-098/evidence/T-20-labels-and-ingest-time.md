# T-20 综合搜索、入库时间与统一详情

日期：2026-10-27（Asia/Shanghai）
结论：PASS（机器腿）；真实页面读回并入 T-26 复走查

## 提交

| 仓 | 分支 | 提交 |
| --- | --- | --- |
| wt-media-cloud | `chg/CHG-20261015-098-round3` | `35aa2ae`（前端） |
| wt-media-workspace | `chg/CHG-20261015-098-docs` | 本文件所在提交（PRD 第四章） |

## 改动与读回

| 用户项 | 改动 | 断言 |
| --- | --- | --- |
| 2 综合搜索 | `DiscoveryStrategiesPage` 标签「策略名称」→「综合搜索」，占位「搜索策略 ID / 策略名称」；`CrawlTasksPage` 标签「任务名称 / 来源策略」→「综合搜索」，占位「搜索任务 ID / 任务名称 / 来源策略」 | `DiscoveryPages.test.js` 断言两个标签与两个占位文案 |
| 7 操作区按钮 | 内容池行操作删除按状态分叉的「素材详情」，行上统一只留「详情」；素材跳转保留在详情抽屉「关联素材」 | `expect(source).not.toContain('>素材详情</t-button>')`；`@click="viewMaterial(detail)">素材详情</t-link>` 仍在抽屉内 |
| 8 入库时间 | 内容池 `created_at` 列标题与详情字段「发现时间」→「入库时间」；字段与排序不变 | 新用例断言列声明、详情标签，并 `not.toContain('发现时间')` |

后端检索范围核对（只读，无改动）：策略 `search` 命中 `s.name LIKE` 与 `CAST(s.id AS CHAR) =`（`discovery_store_mysql.go:65-68`）；任务 `search` 命中展示名、`t.task_id LIKE` 与内部 id 精确（`discovery_store_mysql.go:168-177`）。因此标签写「综合搜索」与占位列出的字段与实际检索一致，不需要改查询参数或字段名。

## 测试

| 项 | 实测 |
| --- | --- |
| 前端全量 | 在 `wt-media-cloud/web` 下 `npx vitest run`：85 文件 / 763 测试全绿（T-19 后为 762，新增「入库时间」用例 1 条） |
| 反向断言 | `ContentPoolPage.test.js` 的 `>素材详情</t-button>`、`>查看</t-button>`、`查看素材` 均不存在 |

文案扫描（`grep -rn` 于 `web/src`，分母 = 全部 `.vue`/`.js`）：

| 模式 | 命中 | 说明 |
| --- | --- | --- |
| `发现时间` | 2 | 全部是 `ContentPoolPage.test.js` 自身的用例名与反向断言；`ContentPoolPage.vue` 0 |
| `>素材详情</t-button>` | 0 | 行按钮已删 |
| `素材详情`（不限形状） | 14（非测试文件 8） | 合法语境：素材抽屉标题、`查看素材详情` 跳转、内容池抽屉「关联素材」链接、注释 |
| `入库时间`（阳性对照） | 16 | 证明扫描在工作，不是空转 |
| `综合搜索`（阳性对照） | 策略页与任务页各 1 处 | 见上表 |

## 文档

`docs/product/prd/详细文档/第四章_内容挖掘.md`：§4.3.5 增「入库时间」口径与操作列统一按钮名；§4.4.7 增策略「综合搜索」；§4.5.5 增任务「综合搜索」及可搜字段。

## 未覆盖

- 真实页面读回（三账号）并入 T-26。
- `ContentPoolPage` 与 `CrawlTasksPage` 的 10 秒自动刷新属 T-25，本任务未改加载逻辑。
