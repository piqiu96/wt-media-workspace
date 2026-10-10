# 登录页抽象流量视觉验收（2026-10-10）

> 本方案经用户走查认为偏离视觉图，已由 [登录页视觉图重组验收](login-reference-assembly-20261010.md) 替代；以下保留为中间过程证据。

- 范围：Cloud 与 Desktop 共用的 `LoginPage.vue` 视觉；不改登录脚本、认证 API、会话和路由。
- 实施：保留页首品牌标和版本角标、左文右表单结构；中央完整 Logo 改为三条 SVG Bézier 轨迹、四个蓝青节点、两条椭圆轨道，外围复用 TDesign 图片、播放、数据图标；卡片、渐变按钮、底部波浪按参考图调整。视觉颜色与卡片参数读取 `design-token.css` 新增的品牌变量。
- 说明：原页面使用原生 `<input>` 并有自定义密码显隐按钮；提示词所说“继续使用 TDesign Input”与代码现状不符。本次保留现有输入 DOM 与事件，避免改变密码显隐、输入时重置替换会话提示和表单提交行为。
- 浏览器：本地 `/login` 在 1920、1440、1280、390 px 视口均无水平溢出；桌面为双栏，手机沿用单列并隐藏中央装饰图。1440 px 截图：[login-flow-1440.png](screenshots/login-flow-1440.png)。
- 交互：浏览器检查密码输入初始为 `password`，点击显隐后为 `text`；按钮 aria-label 由“显示密码”变为“隐藏密码”；保留一个表单和 `type=submit` 按钮。
- 测试：`npm test -- src/apps/desktop/desktopRoleGuard.test.js src/session.test.js src/http.test.js`，3 文件 12 项通过。
- 构建：`npm run build:cloud`、`npm run build:desktop` 均通过；Vite 提示已有大包与 Desktop session 混用动态/静态导入警告，无构建失败。
- 其他门禁：`git diff --check -- web/src/modules/auth/pages/LoginPage.vue web/src/styles/design-token.css` 通过。`npm run typecheck` 和 `npm run lint` 均返回 Missing script；`web/package.json` 未配置这两项，也未安装对应可执行文件。
- 提交：Cloud `db2c868`，仅包含登录页与共享视觉变量。Cloud 工作区其他未提交改动未纳入本提交。
- 当前状态：本地视觉与构建通过；真实账号登录和部署环境浏览器验收仍未执行。
