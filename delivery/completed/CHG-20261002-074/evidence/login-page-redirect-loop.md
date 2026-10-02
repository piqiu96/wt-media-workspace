# CHG-20261002-074 走查记录：登录页自指重定向，导致「一直在跳登录、无法登录」（2026-10-03）

用户报「当前 web 端一直在跳登录，无法登录」，并确认形态是：浏览器里的 Cloud Web；点「登录」后**直接回到登录页**（不是 20010 替换确认，也没有报错文案）。

## 根因（读码可证）

- `web/src/modules/auth/pages/LoginPage.vue:43` 在 `onMounted` 调 `sessionClient.me()` 做「我已登录了吗」探测；未登录时它必然 401。
- `web/src/shared/api/http.js` 把**任何** 401（除 `/auth/login`）变成整页导航：`window.location.href = '/login?redirect=' + encodeURIComponent(pathname + search)`。
- 于是登录页把自己再导航一次，`redirect` 每轮再叠一层编码（`/login` → `/login?redirect=%2Flogin` → …），整页重载 → 探测 → 401 → 再导航。**两台路由守卫都拦不住**：`apps/cloud/main.ts:23` 与 `apps/desktop/main.ts:37` 都在 `to.path === '/login'` 时直接 `next()`，`/login` 上根本没有守卫。
- 「点登录直接弹回」同源：整页重载每 ~90 ms 换一次 DOM，mousedown 的目标节点在 mouseup 前已被销毁 → **click 事件不产生**，请求不离开页面。这正是服务端一条登录 POST 都没有的原因。

## 实测读数

| 项 | 命令 / 来源 | 读数 |
| --- | --- | --- |
| 401 空转总量 | `logs/access.log` 计数 | `GET /api/v1/auth/me status=401` 共 **2482** 次 |
| 突发形态 | 按时间分组（间隔 >2 s 断开） | **86 段**，单段 49～147 次 / 7～14 s，相邻间隔 **80～140 ms** |
| 最后一次登录 POST | `logs/access.log` | `01:25:08`（打包版 起飞.app 的 desktop 登录）；此后**用户所有尝试都没有 POST 到达 18080** |
| 会话表 | `user_sessions` | operator01 有 `web`(00:00:48) 与 `desktop`(01:25:08) 两条有效会话；admin 一条 `web`(01:24:14) |
| 客户端归属 | `lsof -iTCP:18080` + `ps` | 持长连接的只有 `com.apple.WebKit.Networking`(44671)，其兄弟进程是 `.local/m2b/dmg-mount/起飞.app` 的 shell 与 agent → 打包版 app 至少制造了 `01:24:36` 那一段 |
| 后几段不是 app 发的 | access.log 窗口 | `02:02:56` 与 `02:03:26` 的 `me() 200` + `device-binding 200` 把 `02:03:02` 那段 401 夹在中间，30 秒节奏正是胶囊轮询 → 那几段来自**浏览器 Cloud Web**（经 `vite.config.cloud.js:24` 的 `/api → 127.0.0.1:18080` 代理到达） |

## 修法（只改 `wt-media-cloud/web`，一处判断）

`http.js` 的 401 分支加「已经站在 `/login` 就不再导航」：`const onLoginPage = win?.location?.pathname === '/login'`，条件变为 `... && !onLoginPage`；`window` 按同文件 `defaultApiBase()` 已有的 `typeof window === 'undefined' ? null : window` 取。

**不顺带豁免 `/auth/me`**：那会一并改掉「内容页发现会话失效 → 整页带 returnUrl 跳登录」的既有设计，而 `DashboardPage.vue:13` 这类只调 `me()` 的页面正靠它兜底（`AppLayout.vue:68` 的 catch 只把 `currentUser` 置 null，不导航）。只加这一条不动任何别的路径，只切断自指循环。

## 验证

| 项 | 读数 | 判定 |
| --- | --- | --- |
| `npx vitest run`（`web/`，最后一次改动之后） | **50 文件 / 486 用例**通过（484→486） | PASS |
| 新增用例 | `http.test.js` 增 2 条：`/login` 上 `me()` 401 不导航、`/login` 上任意 401 不导航 | PASS |
| 变异对照 | 撤掉 `&& !onLoginPage` → 恰好这 2 条红、其余 5 条（含两条既有重定向用例）全绿；还原后 7/7 绿 | PASS |
| **实机对照（同一装置）** | 无头 Chrome 常驻（`--headless=new --remote-debugging-port`，**不能**用 `--dump-dom`，它 dump 完首屏就退出、根本走不到第二轮导航）：同一次打开 `http://localhost:5199/login`，20 秒内 `/auth/me` 401 —— **撤掉守卫 71 次，带上守卫 1 次** | PASS |
| 未登录开内容页仍会跳一次 | 同装置打开 `http://localhost:5199/`，401 **2 次**（守卫探测 → 带 returnUrl 跳登录 → 登录页探测一次）后停住 | PASS（重定向没被一起关掉） |

## 覆盖边界

- 已验证范围：**Cloud Web dev 栈（5199）+ 无头 Chrome**。真实浏览器里的人工登录、以及 **打包版 起飞.app**（前端打进包里，**必须重打 DMG 才生效**）都未验证。
- 失败过一次的探法要记下来：`--dump-dom` 在两个状态下都只读到 **1**，因为 Chrome 在首屏 dump 后即退出，没有判别力——别把它当验证。判据是「同一装置、同一 URL、只有守卫一个变量」的那对 71 / 1。

## 待用户复验

重打 DMG → 安装 → 登出（或让会话失效）→ 应停在登录表单不再自跳 → 能登回去；`agent.log`/`access.log` 里不应再出现成串 `auth/me 401`。

## 关联更正

本文否定了 [walkthrough-panel-false-alarm.md](walkthrough-panel-false-alarm.md) 的「旁证登记」里「401 风暴来自残留的浏览器标签页轮询，与本缺陷无关」这句判断：它不是旁证，就是本缺陷本身，量级（146）也对得上。
