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
- 2026-09-23 17:xx～18:1x 用户实机复核后的第二轮（根因 E、F + 呈现与时间列）：
  - **根因 E（图标）已由用户实机确认恢复**：sprite 内置到 `web/public/tdesign-icons/0.4.3/`。
  - **根因 F（列宽被压）**：用户从实机截图报「内容池没有标题和内容ID」「挖掘任务列被压成 `m3a…`」。
    改用**截图逐列量测**（PNG 解码 + 表头左边界间距反推，DPR=2）定位：内容 340→**91.5**、
    来源 260→**100**；任务名称 220→**76**、任务来源 160→**76.5**、发现结果 240→**76.5**；
    而所有声明 `width` 的列逐列精确。修法：所有列改声明确定 `width`；三表 `scroll.x` 改由列宽推导；
    `.title-copy` 补 `flex: 1`。详见 `evidence/20260923-symptom-f-root-cause-measured.md`。
  - **上一轮「症状 F 未复现」的结论作废**：不是现象不存在，是**模拟台引擎失明**——
    Chrome 认 `minWidth`、WebKit 不认。该文已加作废横幅保留，作为方法学案例。
    **Chrome 模拟台此后只用于证明「无回归」，不再用于判断 F 是否修好。**
  - **新增回归闸门**：`ListPageConventions.test.js` 断言五张表每列都声明 `width`，写死列数作分母；
    **已做阳性对照**（改回 minWidth-only → 立即失败并指名该列，随后按 SHA 还原）。
  - 用户裁定：数字由 `·` 串行改**竖排一行一项**；任务名称内嵌时间戳**去秒**；三页时间列统一 150px。
  - 验证：`npm run test` 96 passed（含新增 6 条）；`go test ./...` 57 ok / 0 FAIL；`build:cloud`、
    `build:desktop` 均通过；DMG 重建成功且 "valid on disk"；新卷二进制内命中三个新 chunk 名
    （`ContentPoolPage-Cht9c0Jj.js` 等各 1），两个旧 chunk 名 0 命中——证明内嵌的是新产物。
  - **待用户亲眼确认**：内容列标题与平台 ID 是否回来、挖掘任务三列是否正常、时间列是否 150px 无秒、
    数字是否竖排。**WebKit 实际行高需由截图重读后回写 `change.md` 行高节**。
