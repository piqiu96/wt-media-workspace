# T-03：视觉一致性与收尾门禁

## 合并

Cloud PR [#9](https://github.com/piqiu96/wt-media-cloud/pull/9)，CI `verify` pass（2m59s），merge commit `d793d92`（2026-10-26T10:46:22Z）。

## 删除前后读回

方法：同一 Chrome 155 headless（CDP 9224）、同一 operator01 会话，分别打开 `/compose` 与 `/finished-media`，等待表格行出现后读根变量、真实徽标的计算色、克隆徽标五种 tone 的计算色、加载的 token 资源。删除 `tokens.css` 后重跑同一脚本。

| 读数 | 删除前 | 删除后 | 结果 |
| --- | --- | --- | --- |
| 合成任务表格行数 | 6 | 6 | 一致 |
| 成片管理表格行数 | 6 | 6 | 一致 |
| 真实成功徽标色 | `rgb(22,163,74)` / 背景 `rgb(220,252,231)` | 同左 | 一致 |
| 克隆 `success/warning/danger/info/neutral` | 22,163,74 / 217,119,6 / 220,38,38 / 37,99,235 / 100,116,139（背景同左表） | 同左 | 一致 |
| 根变量 `--wt-status-*` | 全空 | 全空 | 一致 |
| `--td-success-color` | `#2ba471`（TDesign 默认） | `#2ba471` | 一致 |
| 加载的 token 资源 | 仅 `src/styles/design-token.css` | 仅同文件 | 一致 |
| 页面内联样式定义 `--wt-status-*:` | 0 | 0 | 一致 |
| 页面内联样式提到 `--wt-status-` | 1（Compose 注释） | 0 | 预期差异：注释已改 |

两页的视觉字段逐项相同；唯一差异是源码注释不再提及旧前缀。没有新增 TDesign 全局覆盖。

## 构建与自动门禁

| 门禁 | 读数 | 结果 |
| --- | --- | --- |
| `npm run build`（cwd=`web/`） | 成功，7.87s；产物中 `--wt-status-` 0 文件命中 | PASS |
| 同一扫描阳性对照 | 删除前的 `tokens.css` 命中 6 次；产物中 `--wt-success:` 有命中 | 非空转 |
| `npx vitest run` | 79 文件 / 722 用例通过 | PASS |
| `go test ./... -count=1` | 72 包 ok、0 FAIL | PASS |
| Workspace 收尾套件 | 174 用例通过；治理、AI 工作区、技能、产品对齐、M0、文档、control 校验通过 | PASS |

## 覆盖范围与未覆盖项

- 已覆盖：合成任务与成片管理的真实成功徽标、两页五种状态色的计算值、入口实际加载的样式表、构建产物与源码定义。
- operator01 可见数据只有成功任务；失败/警告色用页面内真实 `ResourceStatusBadge` 的克隆节点读取，保留 scoped `data-v` 属性，未伪造状态行。开发库另有 3 条失败任务属于管理员，未取得管理员凭据，未切账号读回。
- 未做 GUI 截图比对；判据是同一浏览器同一选择器的计算色逐项相等，不是肉眼观感。
- 未改 TDesign 默认 success/error 色，未做主题重构。
