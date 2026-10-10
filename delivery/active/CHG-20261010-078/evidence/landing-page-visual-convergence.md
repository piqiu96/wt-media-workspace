# 官网单页视觉收敛验证

- 范围：按用户 2026-10-10 提供的视觉图和固定文案重构 Cloud /home。未修改 /login、业务 API、路由守卫、下载清单解析与 Release 更新脚本。
- 页面结构：Header → #hero → #product → #download → #pricing → #contact → Footer；顶部仅有产品、下载、定价、联系四项。
- 实现：复用 BrandLogo、TDesign Icon、--td-brand-color 与 loadDownloadManifest；Hero 右侧使用用户本次提供设计图中的插画区域，未绘制新 Logo 或生成新插画。三张下载卡仍读取同源清单。
- Cloud 提交：9718404。
- 命令：npm run build:cloud 退出码 0；npm run test -- src/modules/public/downloadManifest.test.js src/apps/cloud/publicRoutes.test.js 为 2 文件、3 测试通过；git diff --check 退出码 0。npm run typecheck、npm run lint 已执行，均因 web/package.json 未提供该脚本而退出 1；本仓也没有 vue-tsc、tsc、eslint 可执行文件。
- 浏览器：Chrome DevTools 1440×900 初始高亮「产品」，悬浮栏顶部 16px。点击产品、下载、定价、联系后分别滚动到 530、1034、1210、1270px，活动项均对应；点击 Logo 回到 0px 并恢复产品，Hero CTA 到下载区，定价卡按钮到联系区。程序驱动上下滚动时活动项双向跟随。
- 下载链接：浏览器读取 Windows、macOS Apple 芯片、macOS Intel 三卡，均为 aria-disabled=false，URL 分别指向现有 v0.1.0 正式版的 Windows setup、ARM64 zip、x64 zip。
- 响应式：1920、1440、1280、390、320px 视口的文档宽度等于视口宽度；390/320px 没有被遮挡的正文，三下载卡保持可见。320×844 浏览器还验证了四项导航、Logo、Hero CTA 和定价联系按钮的点击定位。截图：screenshots/wt-landing-1440-full.png、screenshots/wt-landing-390-full.png（320px 截图已随 2026-10-11 记录清理移除）。
- 边界：无头浏览器通过程序滚动验证活动态，真实鼠标滚轮及目标网络上的安装包下载留给部署环境验收。
