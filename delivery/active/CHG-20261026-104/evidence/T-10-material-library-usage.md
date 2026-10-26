# T-10 素材库游戏选项与使用情况可见性

日期：2026-10-27

## 用户反馈与根因

用户走查第 1、2、3 项：

1. 游戏选项只列本人负责的游戏，没有游戏管理里已启用的全部游戏。
2. “使用情况”的具体使用人不可点击，多人时第二行放不下。
3. 没有已知使用人时仍写“负责人未记录”和空占位。

补充澄清：普通运营完全不展示使用情况（列、筛选、详情段）；高级运营/管理员点击摘要打开弹窗；无数据只显示 `—` 或成片数，不写冗余空态文案。

代码事实：

- `MaterialLibraryPage.vue` 的 `gameOptions` 从“本人负责游戏 + 当前页出现过的行”拼选项；默认游戏筛选在游戏字典加载前计算。
- `labels.js` 的 `usageSummaryLines` 返回两行，无已知负责人时固定拼“负责人未记录”。
- 详情抽屉的 `usageFacts` 对空值也产出条目，页面渲染占位。

## 修订

| 文件 | 修订 |
| --- | --- |
| `web/src/modules/materials/pages/MaterialLibraryPage.vue` | `gameOptions` 改为 `games`（游戏管理启用字典）全量；`defaultGameFilters()` 取“本人负责 ∩ 启用”（管理员为所选团队全部）；会话与字典加载完成后再取列表；新增 `canViewUsage`（高级运营/管理员）；普通运营的 `tableColumns` 过滤掉 `usage` 列，使用情况筛选项 `v-if`，详情抽屉传 `:show-usage="canViewUsage"`；摘要单元格为一行按钮，点击 `openUsage(row)` 打开弹窗；弹窗遍历 `usageOperators`，列表 `max-height: 280px; overflow-y: auto` |
| `web/src/modules/materials/labels.js` | 新增 `usageOutputCount`、`usageOperators`、`usageSummary`；`usageSummary`：无数据/0 成片 `—`，有数无已知负责人 `成片 N`，有负责人 `成片 N · 使用 M 人`；`usageFacts` 只返回有值条目 |
| `web/src/modules/materials/MaterialDetailDrawer.vue` | 新增 `showUsage` prop（默认 false）；标题在素材库且可见使用情况时为“当前进度 / 使用情况”；只有 `usageRows.length` 时渲染使用段 |
| `docs/product/prd/详细文档/第五章_素材生产.md` | §5.3.1/§5.3.3/§5.3.6/§5.3.7 同步：游戏选项来自启用字典；普通运营不渲染使用情况；高级运营/管理员一行摘要 + 弹窗；无占位文案 |
| `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md` | 读模型边界改为“普通运营页面不渲染使用情况，服务端也不返回使用人姓名” |

服务端读模型未改：仍按角色返回 `usage` 计数；普通运营不返回 `operators` 姓名，本次只收敛页面可见性，未新增合同字段。

## 自动验证

命令（Cloud `web/` 下）：

```text
npm test -- --run src/modules/materials
```

实际：`MaterialLibraryPage.test.js` 20、`MaterialDetailDrawer.test.js` 41、`labels.test.js` 24、`ListPageConventions.test.js` 3 等 materials 用例全部通过（本次目标集合 11 文件 / 165 用例）。

关键断言：

- 选项来自 `games`；默认项为“负责 ∩ 启用”；字典失败/未加载时不预选。
- 普通运营：表头无 `usage`、筛选不渲染、详情抽屉 `showUsage=false`。
- 高级运营/管理员：摘要 `—` / `成片 N` / `成片 N · 使用 M 人`；点击设置弹窗素材；弹窗遍历 `usage.operators`；列表有滚动样式。
- 源码不再包含“暂无成功成片”“负责人未记录”“姓名不可见”。

全量：Vitest 80 文件 / 736 用例通过。

## 覆盖边界

- 已验证：页面源码与纯函数层；真实数据由既有 T-06 读回（素材 17 成片 1/使用人 pika；素材 161 成片 6、无已知负责人）。
- 待用户走查：A1～A3、B1～B3、C1～C2 的实际页面显示与弹窗滚动。
- 未覆盖：素材 161 清理后的 `—` 状态，待 T-13 清理后复核。
