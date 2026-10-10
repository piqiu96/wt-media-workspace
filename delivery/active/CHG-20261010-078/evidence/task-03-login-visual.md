# Task 3：共享登录页与品牌视觉

- 命令：`npm test -- src/apps/desktop/desktopRoleGuard.test.js src/apps/routerParity.test.js src/modules/public/downloadManifest.test.js src/apps/cloud/publicRoutes.test.js`。
- 实际：4 个测试文件、13 项测试通过；Desktop 角色规则和双端共享路由未被破坏。
- 命令：`npm run build:desktop`、`npm run build:cloud`。
- 实际：两个构建均成功；现有主 chunk 体积提示不影响构建。
- 命令：`npm test`。
- 实际：52 个测试文件、490 项测试通过。
- 生产构建经本地静态服务及 Chrome 无头浏览器查看：首页宽屏、登录宽屏、首页 390 px、登录 390 px、下载区 390 px 截图见 `screenshots/`；移动视口 `innerWidth=390` 且 `documentElement.scrollWidth=390`，页面无水平滚动。下载区显示 `v0.1.0` 和三平台卡片。
- 限制：无头浏览器使用静态服务，未验证真实账号登录和终端网络下载；上述截图只证明页面渲染。
