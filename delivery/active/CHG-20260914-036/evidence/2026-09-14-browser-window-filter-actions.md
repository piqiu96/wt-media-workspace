# 2026-09-14 浏览器窗口筛选操作核验

- 关联 Cloud 提交：`9a0375d fix(web): restore browser window filter actions`

| 核验项 | 操作 | 预期 | 实际 | 结果 |
| --- | --- | --- | --- | --- |
| 定向回归 | `npm test -- --run src/modules/profiles/pages/ProfilesPage.test.js` | 页面含查询、重置按钮并绑定对应处理函数 | 5 项测试全部通过 | PASS |
| Desktop 前端构建 | `npm run build:desktop` | 生成包含筛选操作的 Desktop 资源 | Vite 生产构建完成 | PASS |
| 本地环境 | `scripts/local-control.sh start` 后执行 `verify` | Cloud、Agent、BitBrowser、Desktop assets、DMG、登录烟测均通过 | 全部 PASS | PASS |
| Desktop 页面呈现 | 打开最新挂载 DMG 的“运营资源 / 浏览器窗口” | 九个筛选字段后显示“查询”“重置” | 实际页面中 `查询`、`重置` 位于 Cloud 状态筛选项之后；筛选字段标签与五个直出行操作保持正常 | PASS |

实现说明：浏览器窗口的筛选结果由既有前端计算属性派生；查询按钮将分页复位到第一页并重新读取窗口列表，重置按钮清空九项现有筛选条件后调用同一查询流程。未调整 API、路由、数据结构或窗口操作逻辑。
