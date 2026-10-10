# 官网文案与手机布局校准

- 用户标注：删除主视觉上方「起飞 · 内容运营平台」与「轻量易用」；放大居中导航；缩小「起飞」左侧 Logo 内图形，顶部略留白。补充反馈：手机端底部功能文案被遮挡。
- 代码改动：首页导航文字 17→21 px；仅首页品牌图背景尺寸 150%→130%；删除两处指定文案。手机端取消 390 px 下隐藏功能副文案与最后一项支持说明的规则，插画高度 330→250 px；320 px 及以下高度 235 px、功能卡文字和间距适配。
- Cloud 提交：`7c725c3`。
- 自动验证：`npm run build:cloud` 退出码 0；`git diff --check` 退出码 0。
- 浏览器验证：Chrome DevTools 视口 1672×941、390×844、320×844；390 与 320 px 文档宽度分别为 390 与 320，无水平溢出。390 px 下四张功能卡底部为 817.25 px，320 px 下为 832.23 px，均位于 844 px 视口内；四张卡的标题和副文案均在页面中可见。手机端「Windows / macOS 支持」和「本地与云端协同」均可见。
- 截图：`screenshots/wt-home-wide.png`、`screenshots/wt-home-mobile-cdp.png`、`screenshots/wt-home-mobile-320.png`、`screenshots/wt-home-mobile-full.png`。
- 边界：只验证本地页面与构建；线上部署和目标用户网络下载仍待验收。
