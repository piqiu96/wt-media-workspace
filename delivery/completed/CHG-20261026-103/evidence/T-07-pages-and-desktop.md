# T-07：Cloud Web／Desktop 共用页面

页面读回在真实 Vite（5173）＋ Cloud API（8188）上执行，浏览器为 CDP 9224 的 Chromium；原始摘录见 `T-07-pages.json`。

## 列表与筛选

| 场景 | 读回 | 结果 |
| --- | --- | --- |
| 普通运营策略页 | 仅 1 行：44 / CHG103负责人链路 / pika；操作只有“详情” | PASS |
| 高级运营策略页 | 9 行，负责人列显示 CHG103高级、pika，历史 7 行“未记录” | PASS |
| 管理员策略页 | 9 行，负责人列同上 | PASS |
| 普通运营任务页 | 默认 8 行，含 pika 的 325/326；无“团队”筛选 | PASS |
| 高级运营任务页 | 默认 1 行（327）；负责人下拉“我的／团队全部／CHG103高级／pika／senior01”；切团队后 22 行 | PASS |
| 管理员任务页 | 默认 20 行（当时含 3 条验收任务）；负责人筛选在选团队前禁用，选团队后出现 CHG103高级、pika、senior01；选 pika 后只剩 325 | PASS |
| 普通运营成片页 | 8 行，含 70/69；负责人列 pika；历史行“未记录” | PASS |
| 高级运营成片页 | 默认 1 行（71）；切团队 19 行 | PASS |
| 管理员成片页 | 19 行（历史＋3 条验收），负责人列混合 | PASS |

## 表单与详情

| 场景 | 读回 | 结果 |
| --- | --- | --- |
| 管理员策略表单 | 负责人选择在未选团队／游戏时禁用、占位“先选择游戏”；选团队 1＋游戏 hy 后启用，选项 CHG103高级、pika；可选中 pika | PASS |
| 策略详情抽屉（历史 43） | 字段“负责人”，值“未记录”；不显示创建人冒充负责人 | PASS |
| 任务／成片详情抽屉 | 任务 327→CHG103高级、326/成片 69→pika、成片 71→CHG103高级；任务 324、成片 68→“未记录” | PASS |
| 创建任务抽屉 | 选择策略 44 后，“合成策略 CHG103负责人链路”“负责人 pika” | PASS |

抽屉读回使用保存的会话 Cookie 注入浏览器，未重新输入口令；同一探针内既有已指派行也有历史未记录行，避免“只读到未记录”或“只读到人名”的单侧空转。

## Desktop 产物

| 证据 | 读数 |
| --- | --- |
| 前端戳 | `source_commit=54c0e87`、`source_dirty=false`、files=86、digest=`1bf32b2eaf01e94eb512f95b84d54a758c89c7f129ef8e1e9f6b9ba231254bbf` |
| 构建 | `cargo tauri build --no-bundle` 成功；`target/release/wt-media-desktop-shell` 24,509,280 bytes（19:24） |
| 资产锚 | `ComposeStrategyPage-Dp3Ocf7I.js`、`ComposeTasksPage--nT-mXSk.js`、`MyOutputsPage-BydC6nJG.js`、`ComposeOutputDetail-B4qEFbC4.js` 及其 CSS 各在二进制中命中 1 次 |

Tauri 资产在二进制中压缩存放，业务字符串不能直接 grep；这里用当前构建的内容哈希资产名作为锚，闭合“二进制使用的是这一版共用页面”。Tauri GUI 走查留给用户。
