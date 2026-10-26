# T-01：状态色死表审计

## 环境

- Cloud 检出 `wt-media-cloud`，分支 `chg/CHG-20261026-106`，起点 `main` `cb26c66`。
- 开发栈：API 8188（`bin/control.sh start`）、Cloud Web 5173（Vite）、Chrome 155 headless（CDP 9224）。

## 引用关系

| 检查 | 读数 | 结论 |
| --- | --- | --- |
| 两个应用入口的 CSS import | `apps/cloud/main.ts:9`、`apps/desktop/main.ts:12` 均只 import `styles/design-token.css`；另有 `resource-module.css` | `shared/styles/tokens.css` 不在入口链上 |
| `tokens.css` 内容 | 6 个 `--wt-status-*` 定义，并在 `:root` 里把 `--td-success-color` 设为 `#00a870`、`--td-error-color` 设为 `#d54941` | 若被加载，会全局改写 TDesign 状态色 |
| `var(--wt-status-` 消费方 | `web/src` 0 处（唯一命中是 `ComposeTasksPage.vue` 注释） | 没有任何页面读取这支表 |
| 入口真正加载的 `design-token.css` | 定义 `--wt-success: #16A34A`、`--wt-warning: #D97706`、`--wt-danger: #DC2626` 等 | 页面现有状态色来源 |

## 运行时读回（删除前）

`document.styleSheets` 在 Vite 下为内联样式，改用资源条目与根变量读回：

| 读数 | 实际 | 说明 |
| --- | --- | --- |
| 加载的 token 资源 | 仅 `http://127.0.0.1:5173/src/styles/design-token.css` | 无 `tokens.css` 请求 |
| 根变量 `--wt-status-success/error/...` | 全部为空 | 语义表未生效 |
| 根变量 `--td-success-color` | `#2ba471`（TDesign 默认） | 不是 `tokens.css` 写的 `#00a870` |
| 页面内联样式定义 `--wt-status-*:` | 0 处（Compose 页仅 1 处注释提到该前缀） | 无隐藏定义 |

结论：`tokens.css` 及其状态色表从未进入任何入口，页面颜色实际来自 `design-token.css` 与 TDesign 默认值；按“删除死表”收口。
