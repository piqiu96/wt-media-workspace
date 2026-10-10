# 圆形徽章与手机登录文案校准

- 用户标注：首页手机主视觉及登录页中部图标贴近或超出圆圈；手机首页顶部和页脚不显示「登录平台」文字。
- 代码改动：首页 `.hero-emblem` 和登录页 `.story-emblem` 的背景图缩放从 150% 调整为 110%，保留圆形边界与图形之间的空白。手机首页顶部改为只有用户图标的登录链接，保留 `aria-label="登录平台"`；手机页脚隐藏文字登录链接。
- Cloud 提交：`0ec44a4`。
- 命令：`npm run build:cloud` 与 `npm run build:desktop`，均退出码 0；`git diff --check` 退出码 0。
- 浏览器验证：Chrome DevTools 390×844 与 320×844 首页截图，1440×900 登录截图；圆形徽章计算背景尺寸为 `110% auto`。手机顶部登录链接可见、文字为空、无障碍名称为「登录平台」；页脚文字链接计算样式为 `display:none`。390/320 px 文档宽度与视口宽度相同。
- 截图：`screenshots/wt-home-mobile-cdp.png`、`screenshots/wt-home-mobile-320.png`、`screenshots/wt-home-mobile-full.png`、`screenshots/wt-login-wide.png`。
- 边界：这是本地页面和构建验证；线上部署与真实账号登录仍待验收。
