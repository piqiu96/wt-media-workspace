# 官网登录引导与图标遮挡修正

- 用户反馈：首页不应出现登录引导；手机首页右上角不应有人物头像；左下五角星遮挡播放图标。
- 当前执行基线已同步到 `delivery/milestones/M-first-production-release.md#公开官网与桌面安装包下载` 和本 CHG：官网只提供内容介绍与下载，独立 `/login` 页面继续提供认证。
- 代码改动：移除首页手机头像链接、联系管理员卡片与页脚的登录链接、帮助说明中的登录账号描述；移除左下装饰星及相应样式。
- Cloud 提交：`26d85b1`。
- 命令：`npm run build:cloud` 退出码 0；`git diff --check` 退出码 0。
- 浏览器验证：Chrome DevTools 在 1672×941、390×844、320×844 首页视口中，`/login` 链接数与可见「登录」字数均为 0，三平台下载卡数均为 3，左下装饰星元素数为 0。390/320 px 文档宽度等于视口宽度；390 px 截图中播放图标完整可见。直接访问 `/login` 仍显示登录页。
- 截图：`screenshots/wt-home-wide.png`、`screenshots/wt-home-mobile-cdp.png`、`screenshots/wt-home-mobile-320.png`、`screenshots/wt-home-mobile-full.png`。
- 边界：这是本地页面和构建验证；线上部署、真实登录和目标用户网络下载仍待验收。
