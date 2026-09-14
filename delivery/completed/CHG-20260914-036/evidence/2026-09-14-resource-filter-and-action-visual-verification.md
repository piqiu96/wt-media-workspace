# 2026-09-14 运营资源筛选与操作列视觉核验

- 关联 Cloud 提交：`031d4d7 fix(web): restore resource filter labels`
- 关联 Workspace 提交：`c1fe387 docs(delivery): checkpoint resource UI validation`

| 核验项 | 操作 | 预期 | 实际 | 结果 |
| --- | --- | --- | --- | --- |
| 定向回归 | `npm test -- --run` 三个资源页测试 | 字段前缀、420px 固定操作列与原有动作均受回归覆盖 | 3 文件、12 测试通过 | PASS |
| 全量前端回归 | `npm test -- --run` | 资源页修改不破坏既有前端测试 | 18 文件、70 测试通过 | PASS |
| Desktop 前端构建 | `npm run build:desktop` | 生成最新 Desktop Web 资源 | Vite 构建完成 | PASS |
| 本地环境 | `scripts/local-control.sh start` 与 `verify` | 最新 Cloud、Agent、BitBrowser、DMG 和登录烟测均可用 | 全部 PASS；DMG 为最新构建 | PASS |
| 浏览器窗口视觉 | 最新 DMG 登录 `operator01` 后打开“运营资源 / 浏览器窗口” | 9 个筛选项显示前缀，按当前宽度三列换行；右侧固定操作列显示详情、打开、更多 | 字段前缀均可见，三列换行，无溢出；操作列固定 | PASS |
| 代理管理视觉 | 最新 DMG 打开“运营资源 / 代理管理” | 字段前缀完整、右侧固定操作列可预留六个直接操作 | 代理状态、供应商、地区、搜索均可见；操作列固定，当前显示详情、检测、更多 | PASS |
| 社媒账号视觉 | 最新 DMG 打开“运营资源 / 社媒账号” | 面包屑正确，七个筛选项带前缀并自动换行，右侧固定操作列 | 面包屑为“运营资源 / 社媒账号”；综合搜索、游戏、平台、业务状态、账号状态、标签、窗口均可见；操作列固定 | PASS |

备注：操作列统一为 420px，样式容量支持至多 6 个直接操作；当前三页均保留 3 个高频直接动作，其他原有业务动作继续收纳在“更多”菜单中。
