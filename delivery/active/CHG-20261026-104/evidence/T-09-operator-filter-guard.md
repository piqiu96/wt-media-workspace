# T-09 空负责人筛选守卫

日期：2026-10-27

## 用户反馈与根因

用户走查第 5、6 项：合成任务页和成片管理页把负责人筛选清空为“全部”后，再点筛选报错，页面提示 `undefined is not an object (evaluating '...operator.startsWith')`。

代码事实：TDesign `t-select` 清空可清选项时把 `v-model` 写成 `undefined`，不是空串。两页在 `load()` 和负责人选项加载处直接调用 `filters.value.operator.startsWith('op:')`，空值即抛错。

## 修订

| 文件 | 修订 |
| --- | --- |
| `web/src/modules/compose/operatorFilter.js` | 新增 `operatorIdFromOption(value)`：只接受 `op:<正整数>`，其余（`undefined`、`null`、空串、数字、对象、非法 id）返回 `0`；新增 `missingOperatorOption(value, options)`：空值返回 `false`，非空但不在当前选项里返回 `true` |
| `web/src/modules/compose/pages/ComposeTasksPage.vue` | `load()` 改用 `operatorIdFromOption(filters.value.operator)`；`loadOperators()` 用 `missingOperatorOption` 把不在选项里的旧值重置为空；源码不再出现 `filters.value.operator.startsWith` |
| `web/src/modules/compose/pages/MyOutputsPage.vue` | 同上 |

清空后请求不携带 `operator_id`，按角色范围返回全部；非法值按“全部”处理，不返回 400。

## 自动验证

命令（Cloud `web/` 下）：

```text
npm test -- --run src/modules/compose src/modules/materials src/shared/api
```

实际：11 个文件 / 165 用例通过，其中 `operatorFilter.test.js` 4 个纯函数用例覆盖 `undefined`、`null`、`''`、数字、对象、`'op:3'`、`'op:03'`、`'op:0'`、`'op:-1'`、`'op:2.5'`、`'op:abc'`、`'op:'`、超出安全整数、`'mine'`，以及匹配/缺失选项和空选项列表。

页面源码断言：`ComposeTasksPage.test.js`、`MyOutputsPage.test.js` 均断言使用 `operatorIdFromOption` / `missingOperatorOption`，并断言源码不包含 `filters.value.operator.startsWith`。

全量读数见 T-14：Vitest 80 文件 / 736 用例通过；Cloud `go test ./...` 72 包 ok、0 FAIL。

## 覆盖边界

- 已验证：清空值引发的解析路径、非法值兜底、旧选项缺失重置。
- 待用户走查：A5、A8、B4 的“清空负责人再筛选不报错”真实页面操作。
- 未覆盖：浏览器原生事件序列本身（Vitest 直接调用纯函数与源码断言）；由走查补足。

## 用户复走查结果（2026-10-27，通过）

- 合成任务页：清空负责人回“全部”后再筛选，页面不报错，列表按团队范围返回。
- 成片管理页：清空负责人再筛选同样不报错；新增游戏筛选与游戏列可见。
- 结论：用户确认 T-09 的“空值按全部处理”在真实页面成立。
