# T-02：删除死表与入口断言

## 变更

- 删除 `web/src/shared/styles/tokens.css`（14 行，6 个 `--wt-status-*` 与 2 个 TDesign 全局色覆盖）。
- `ComposeTasksPage.vue` 的失败态注释改为说明 `--wt-danger` 来自入口加载的 `design-token.css`，并与失败徽标同色；失败态本身未改。
- `resourceModule.test.js` 新增两条断言：
  - 状态色定义在入口 import 的 `design-token.css`，且 `shared/styles/tokens.css` 已不存在；
  - 递归扫描 `web/src` 的 `.vue/.css/.js/.ts`，不允许再出现 `--wt-status-*:` 定义；以 `--wt-primary:` 命中 `styles/design-token.css` 作阳性对照。

## 断言读数

| 检查 | 读数 | 结果 |
| --- | --- | --- |
| `npx vitest run src/shared/ui/resource/resourceModule.test.js src/modules/compose/pages/ComposeTasksPage.test.js` | 2 文件 / 38 用例通过 | PASS |
| 扫描分母 | `web/src` 下 192 个目标文件（断言 >100） | 非空转 |
| 旧定义阳性对照 | `git show HEAD:web/src/shared/styles/tokens.css` 命中 `--wt-status-` 6 次 | 匹配模式能命中 |
| 删除后源码 | `web/src` 中 `--wt-status-[a-z-]+:` 0 处 | PASS |
| 入口 | 两个入口仍 import `design-token.css` + `resource-module.css` | PASS |

## 提交

Cloud 分支 `chg/CHG-20261026-106` 提交 `068f1f7`。
