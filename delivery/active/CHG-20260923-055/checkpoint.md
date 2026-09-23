# Checkpoint

- Completed：定位并修复用户在 DMG 原生应用上报出的内容池两处呈现问题。根因 A（Desktop 独有）：
  `tauri.conf.json` 的 CSP 无 `img-src`，回落 `default-src 'self'` = `tauri://localhost`，
  而封面是未经代理的抖音 CDN 绝对地址，WKWebView 发请求前即拦掉——已追加 `img-src 'self' https:`，
  并给三处封面加 `@error` 兜底。根因 C（两端共有）：标题省略号规则只覆盖 `<span>` 分支，
  有 `source_url` 的行渲染成 `<a>` 而整段折行，行高被撑到 153px——已把选择器补成
  `.title-copy > a, .title-copy > span`。附带修复根因 D：Rust 侧 `window.eval` 注入的报错转发
  因 CSP 无 `'unsafe-eval'` 从未生效，已改为前端注册转发，不给 CSP 开 `'unsafe-eval'`。
- Current：ACTIVE；改动已落三仓并各自提交（不混合）：
  `wt-media-desktop` `051fc5a`（CSP + `main.rs` + 刷新的 `.generated/frontend` 入口）、
  `wt-media-cloud` `0c54ed2`（内容池页面 + 新增 `webviewErrors.js` + 入口注册 + 测试）、
  `wt-media-workspace`（本记录）。
  验证已过：带真实 CSP 的模拟台上，封面由 `loaded=0/failed=20` 变为 `loaded=20/failed=0`，
  行高由 `[109,87,153,153,131,109,131,87]` 变为统一 `85`；
  release 二进制内嵌 CSP 已含 `img-src 'self' https:`；`cargo test` 11 passed；
  工作区 `npm run test` 89 passed；`go test ./...` PASS；DMG 已重建且 `local-control.sh verify` 全项 PASS。
  **原生窗口仍待用户亲眼确认**。
- Next：用户在 DMG 上确认两处现象消失后签收本 CHG。若原生端仍报问题，用新装的前端转发收集
  `[WEBVIEW]` 输出定位（该通道此前因 eval 被拦而全程沉默）。
- Blockers：无。原生窗口取图需屏幕录制权限，本机未授予，故该项只能由用户确认。
- Verification：见 `evidence/20260923-fix-and-verification.md`（含根因 B 的证否过程）。
