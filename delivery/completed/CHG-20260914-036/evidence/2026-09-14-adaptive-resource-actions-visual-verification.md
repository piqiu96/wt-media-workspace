# 2026-09-14 运营资源自适应筛选与操作列最终视觉核验

- 关联 Cloud 提交：`de41535 fix(web): adapt resource actions and filters`
- 关联 Cloud 提交：`42570b4 fix(web): size resource action columns by action count`
- 关联 Workspace 提交：`5614d1f docs(delivery): checkpoint adaptive resource layout`
- 关联 Workspace 提交：`b01aa73 docs(delivery): record action column sizing`

| 核验项 | 操作 | 预期 | 实际 | 结果 |
| --- | --- | --- | --- | --- |
| 定向回归 | `npm test -- --run` | 三页筛选、操作数与固定列宽均有回归覆盖 | 18 文件、70 测试通过 | PASS |
| Desktop 前端构建 | `npm run build:desktop` | 使用最新源码生成 Desktop Web 资源 | Vite 生产构建完成 | PASS |
| 本地环境 | `scripts/local-control.sh start` 与 `verify` | Cloud、Agent、BitBrowser、Desktop assets、DMG 和登录烟测均可用 | 全部 PASS | PASS |
| 浏览器窗口 | 最新 DMG 以 `operator01` 打开“运营资源 / 浏览器窗口” | 五项行操作不收纳；右侧固定列无空白浪费；筛选项按可用空间填充 | 详情、打开、绑定代理、编辑、停用均直接展示；操作列为 320px；筛选标签和宽控件均可见 | PASS |
| 代理管理 | 最新 DMG 打开“运营资源 / 代理管理” | 五项行操作不收纳；右侧固定列按动作数量收束 | 详情、检测、编辑、设置配额、删除均直接展示；操作列为 340px；四项筛选均为带标签的宽控件 | PASS |
| 社媒账号 | 最新 DMG 打开“运营资源 / 社媒账号” | 已绑定行的六项操作均直接展示；未绑定行按实际动作数收束；筛选区自动换行 | 已绑定行直接显示检查、查看、打开窗口、查看 Cookie、编辑、停用；未绑定行不显示无效的打开窗口；操作列为 400px，筛选控件按三列自动换行且标签完整 | PASS |

结论：资源页行操作遵循“小于等于六项全部直出，超过六项才收纳”的规则。由于右侧固定列需要显式宽度，三个页面按其真实最大直接操作数分别采用 320px、340px 与 400px，既不会截断按钮，也避免保留 420px 的无效空白。
