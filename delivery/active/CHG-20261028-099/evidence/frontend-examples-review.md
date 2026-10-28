# 公共HTML参考与业务原型目录验收

日期：2026-10-28 13:17（Asia/Shanghai）。Task 11。公共HTML参考已可审核；全CHG仍VERIFYING，真实比特/目标网络/整体集成待验不变。

## 目录决定与交付

用户要求先推荐目录并执行，随后明确指定“workspace根目录，example/proto 业务原型，example/common 公共视觉交互”。已按该决定落位，不保留最初建议的frontend/examples副本。

- [example入口](../../../../example/README.md)：目录职责与引用方向。
- [公共参考HTML](../../../../example/common/index.html)：7组模式，直接离线打开；[源码与复用说明](../../../../example/common/README.md)。
- [业务原型起始页](../../../../example/proto/starter.html)：精简结构，共用common资源；[主题原型目录约定](../../../../example/proto/README.md)。
- 正式frontend四份规范与README均补反向引用；Workspace README和AGENT-INDEX注册目录。规则仍由frontend文档维护，HTML不定义第二套规则，运行仓不依赖这些演示文件。

覆盖：8行资源列表/多平台关联账号/筛选与勾选；内容密度和实际容器决定的单/双列详情；560/640px短Dialog与800/960px Drawer；960px资源选择、560px空选择、嵌套摘要和风险确认；帮助/影响/风险/错误分层及六种资源状态；批量过程、结果、七类计数与恢复；配色、字号、控件、按钮/Loading/禁用/状态。

## 验证事实

| 检查 | 操作与预期 | 实际结果 |
|---|---|---|
| 文档治理 | `python3 scripts/docs/check.py`：索引与引用有效 | PASS，15 indexes |
| 格式 | `git diff --check`：无空白错误 | PASS，退出0 |
| 静态资源 | `python3 delivery/active/CHG-20261028-099/evidence/frontend-examples/static-verify.py`：本地链接、ID/label、Token与无联网/计时器依赖 | PASS，8组；37个Token与规范精确一致 |
| 浏览器交互 | 从Workspace根目录执行 `node delivery/active/CHG-20261028-099/evidence/frontend-examples/browser-verify.cjs`，调用本机Chrome的Playwright，DPR1、100%缩放 | PASS，100项，浏览器156.0.8078.48；无脚本/资源错误，无外部网络请求 |
| 可视检查 | 打开列表、短Dialog、双列详情、批量结果与390px Dialog截图，核对比例/轻重/正文与Footer可达 | PASS，采用已审批冷灰、密度与浮层；详情长字段满行，窄表单选择卡片堆叠 |

浏览器脚本需要Node.js、可解析的Playwright模块和本机Chrome；本次使用桌面应用提供的Node/Playwright运行环境，通过NODE_PATH指定其模块目录。执行只打开本地文件并写本CHG证据，不启动业务服务。完整逐项结果：[browser-results.json](frontend-examples/browser-results.json)；[浏览器核验脚本](frontend-examples/browser-verify.cjs)；[静态核验脚本](frontend-examples/static-verify.py)。

三个核验视口：1600×1000、1366×900、390×844。检查七组模式和六种反馈状态的页面溢出、弹窗边界和操作到达；列表窄屏允许内部表格滚动，不整体缩放页面。详情验证800px密集双列、560px单列、800px稀疏单列、长字段满行；新增/编辑保留输入与字段错误，Radio键盘可选。资源选择在嵌套详情返回后保留筛选和选择。批量处理中Esc/X/关闭受保护，按所选范围生成演示项目，手动推进到结果，仅失败重试、待确认独立核实；六类项目计数互斥、总和为总数。

## 必要截图

只保存5张代表证据，无需批量导出全部原型场景：

- [列表1600](frontend-examples/list-1600.png)
- [短Dialog1600](frontend-examples/short-dialog-1600.png)
- [详情自适应1600](frontend-examples/detail-adaptive-1600.png)
- [批量结果1600](frontend-examples/batch-result-1600.png)
- [窄屏Dialog390](frontend-examples/short-dialog-390.png)

列表与详情采用全页截图以展示内容，视口仍为1600×1000；弹层截图使用当前视口。未改变DPR或整页缩放来调整比例。

## 边界与后续

此提交只增加规范配套制品和引用。HTML以原生控件演示模式，实际产品继续基于TDesign/TDesign Icons/shared-ui实现；不把示例脚本/CSS引入运行仓。所有数据明确为虚构，保存、重试、核实和应用只影响本地演示，不调用服务、不定时假报成功，不代替真实业务验收。原有业务视觉稿不自动搬迁；proto/starter不是完整窗口/代理业务原型。

对应差异以本文件所在提交及 `example/`、frontend引用、CHG Task 11核对。未推送、合并或发布。后续产品页面视觉实施仍按已批准规范与原稿质量目标继续，本轮不宣称运行时迁移完成。
