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
- 2026-09-23 16:5x 换装与启动复核：`hdiutil` 卸载旧卷 → 挂载新 DMG → 从新卷启动应用（pid 71172）。
  复核新卷二进制仍含 `img-src 'self' https:`（命中 1）、`Temporary diagnostics` 残留 0；
  Cloud `18080/healthz` 与 Agent `8765/healthz` 均 200。
  **根因 D 的修复已在生产形态下生效**：`/tmp/wt055-app.log` 出现 `[WEBVIEW]` 行
  （两条 `IPC custom protocol failed` 的 `console.warn`，Tauri 自身的良性告警，无 error、无未处理拒绝）。
  应用当前停在登录页——**由服务端证据坐实，非推断**：`wt-media-cloud/logs/access.log` 今日
  `16:42:54`、`16:43:16` 各有两条 `GET /api/v1/auth/me → 401` 且无 `user_id`，
  即会话守卫未取到有效会话。该会话是被本次取证用的登录（`replace_existing: true`）顶掉的。
  故**封面是否加载尚无法判定**：未登录就取不到列表，也就无所谓封面。需用户以 `operator01` 登录后亲眼看。
  教训（现场踩到，与既有证据纪律同源）：本轮先用「WebKit 无 cookie 目录」与
  「WebKit 网络进程零连接」两条否定结论去推「应用没发请求」，**两条都是空转**——
  前者文件名模式没匹配上（`com.wtmedia.desktop` 目录其实存在），后者更糟——被采样的
  `com.apple.WebKit.Networking` 进程 **PPID 为 1（launchd）**，根本证明不了它是本应用的网络进程，
  「零连接」既非本应用的读数、也只是一次性快照。真正定案的是服务端访问日志。
  另：`Containers/com.wtmedia.desktop` 不存在，应用非沙箱，不存在被我漏掉的容器态 cookie 存储。
  否定结论必须先证明检查能失败。
- Blockers：无。原生窗口取图需屏幕录制权限，本机未授予，故该项只能由用户确认。
- Verification：见 `evidence/20260923-fix-and-verification.md`（含根因 B 的证否过程）。
