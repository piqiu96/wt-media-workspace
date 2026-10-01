# 任务 27 证据：外链交给系统浏览器

任务 26 落档后走查时点「打开云端视频」，弹出的是**「浏览器拦截了新标签页，请允许弹出窗口后
重试」**（用户截图），链接打不开。本文件记这次查实的根因、量到的读数、改了什么、以及还没有
被量到的部分。

## 1. 根因

那句话是任务 26 自己写下的错误分支（`MaterialDetailDrawer.vue` 的 `openCloudVideo`）：
`window.open('', '_blank')` 返回了 null。当时按**浏览器**的规矩去修——空标签页开在 `await`
之前，因为跨过 `await` 就不再算用户手势——**这条规矩对 Safari/Chrome 是对的，对宿主不适用**：

- 打包的 Desktop 是 Tauri 2.11.5 的 WKWebView（`Cargo.lock` 钉的版本）。
- Tauri v2 里 `window.open` **不产生窗口**：新窗口请求交给 webview 的 `new_window_handler`，
  而壳里从未装过它（`tauri-2.11.5/src/webview/mod.rs:354,433` 两处默认构造都是 `None`），
  `capabilities/default.json` 也没有 `core:webview:allow-create-webview-window`。请求无人
  接管 → `window.open` 每次返回 null，**与是否跨 `await` 无关**。
- 同一个机制还压着「平台原视频」「作者主页」这些 `<a target="_blank">`：它们走的是同一条
  「请求新窗口」的路，在打包桌面端同样打不开，一声不响。

## 2. 探针与读数（WKWebView 本人）

这道闸门的读数只能来自 WKWebView 本身——Chrome 测不出 Safari 的规矩，而宿主正是它。探针是
`evidence/task27-wkwebview-probe.swift`（直接投事件给自己的窗口，不经过系统事件队列，运营的
桌面不会被碰到）：

```
swiftc -O probe.swift -o probe
./probe scripted false     # 页面脚本自己开（无手势），pref=false —— 宿主默认
./probe scripted true      # 同一页 pref=true —— 阳性对照
./probe trusted false      # 应用侧 evaluateJavaScript 触发（带激活），pref=false
./probe window false       # 一次激活之后隔 N 毫秒再开
```

| 组 | 动作 | 期望 | 实测 | 判定 |
| --- | --- | --- | --- | --- |
| 1 | 页面脚本 `window.open` + 脚本点锚点，**无手势**，pref=false | 闸门关着，一次都到不了 | `CALLS=0 []`，`openReturned=null` | 确认 |
| 1c | 同一页，pref=**true**（阳性对照） | 两次都到达 | `CALLS=2 ["probe-open","probe-anchor"]` | 探针接得住 |
| 2 | 页内对照 + 应用侧 `evaluateJavaScript`，pref=false | 页内 0 次；应用侧带激活则到达 | 页内 `calls=0`；`APP_JS_SEES_ACTIVATION=true`；随后 `app-open`、`anchor-in-page` 各到达一次 | 确认：闸门问的是**激活**，不是「谁调的」 |
| 3 | 同一个激活下，0/250/1000/2000/3000/5000/8000 ms 各开一次 | 量出激活能撑多久 | `REACHED=["0","250"] DROPPED=["1000","2000","3000","5000","8000"]` | 亚秒级 |

第 3 组正是任务 27 要解决的事：素材详情的地址来自一次请求，跨过 `await` 之后手势已经过期，
所以「取到地址再 `window.open`」是**竞态**——多数时候开得出来，慢一点就一声不响。而
`javaScriptCanOpenWindowsAutomatically` 在 macOS 上 wry 不设（只在 Android 设：
`wry-0.55.1/src/android/kotlin/RustWebView.kt:26`），留的是 WKWebView 的默认 false。

**本组读数的覆盖面**（没量的部分不当作量过）：

- 量到：无手势的 `window.open` 与无手势的锚点点击都到不了；有激活时两者都到得了。
- **没量到**：真实鼠标点击（第 2 组的激活是应用侧 `evaluateJavaScript` 造出来的，页面自己报
  `userActivation.isActive === true`，与真实点击在页面这一侧的读数相同，但毕竟不是真鼠标）。
  这一条靠真机验收第 2 条补。
- **没量到**：那条偏好拿到打包应用里是否真的生效。靠真机验收第 1 条补。

## 3. 改了什么

| 仓 | 提交 | 内容 |
| --- | --- | --- |
| `wt-media-desktop` | `a09dccb` | 新模块 `external_links.rs`：判据只放行 `http`/`https`，`open::that` 交给系统浏览器，一律 `NewWindowResponse::Deny`；主窗口改由 `create: false` + `WebviewWindowBuilder::from_config` 在 setup 里建（`on_new_window` 只在 builder 上） |
| `wt-media-desktop` | `967ddb2` | 闸门那一条：主窗口从一份自己设了 `javaScriptCanOpenWindowsAutomatically` 的 `WKWebViewConfiguration` 建（`with_webview_configuration`）。`Cargo.lock` +2 行，无新 crate |
| `wt-media-cloud` | `b51108e` | 前端按宿主交付地址，判据抽到 `web/src/modules/materials/cloudVideo.js`；抽屉只说「现在跑在哪个宿主里」 |

对计划的两处偏离，都在提交信息里写明了：

1. **不新增 `local_open_external_url` 之类的命令**（计划钉死的一条）：保持住了。收尾选的是把
   WebKit 那道闸门打开，页面要的仍然只是**导航**，落点由壳决定——与计划的关键判断同向；命令
   才会是同一条判断的反面（收页面给的 URL 就是「打开任意位置」的通用原语）。
2. **计划的前端那一条（桌面端取到地址后直接 `window.open`）原样保留**，但没有闸门它只是竞态
   （第 2 节第 3 组），所以本任务追加了 `967ddb2` 那一条偏好。
3. 计划里写的「处理器记一条日志」**没有做**：`logging::targets` 的词表是 Q-07 定死的三个
   target，`webview` 那个 target 的文档又明写只放两条 JS 错误记录，两处都要用户的裁定。附带
   的好处是签名地址不会进 `desktop.log`（presigned URL 本身就是凭据）。

## 4. 自动化读数

| 读数 | 命令 | 结果 |
| --- | --- | --- |
| Desktop 测试 | `cargo test`（`src-tauri/`） | **502 通过 / 0 失败 / 6 忽略**（与改动前同） |
| Desktop 构建 | `cargo build` | 12 条警告，与改动前逐条同一批（stash 后实测基线也是 12） |
| 前端测试 | `npx vitest run`（`web/` 下） | **47 文件 / 436 通过**（任务 26 记的 46/430 → +1 文件 +6 用例，抽屉那两条原地替换） |
| Go | 未跑 | 本任务未改 Go |

`cargo build` 这条顺带更正 `a09dccb` 提交信息里的「13」：那次把汇总行
「generated 12 warnings」也数进去了，实际条数一直是 12（本次以 stash 到改动前实测为准）。

## 5. 先红与变异

前端 6 个变异，逐个跑完再 `sha256` 核对还原（`cloudVideo.js` 与 `MaterialDetailDrawer.vue`
两个文件逐字节一致）：

| 变异 | 变红 |
| --- | --- |
| 桌面端也去预留标签页 | 「桌面端不预留」+「空地址算失败」 |
| 把壳返回的 null 读成「被拦」（**原缺陷的形状**） | 「壳拒绝不算被拦」+ 另两条 |
| 取址失败时不关预留的标签页 | 「失败要关掉预留标签页」 |
| 空地址不再当失败 | 「空地址算失败」 |
| 抽屉把宿主写死成浏览器（**原缺陷**） | 抽屉那条 |
| 先取地址、后开标签页 | 「浏览器先预留再取地址」 |

`cargo test` 的判据测试与变异在 `a09dccb` 记过（两个方向各杀各的臂）；本任务新增的那条偏好
是**测不了**的：`WKWebViewConfiguration` 只能在主线程造，而 libtest 每个用例都跑在自己的线程
上——与 `open::that` 一样登记为边界，用真机点击复核。

## 6. 真机验收（用户手动执行，本任务的成败在这里）

**顺序有约束：先提交 Cloud（`b51108e` 已完成），再重建 DMG**，否则
`.generated/frontend/frontend-build.json` 会把 `source_commit`/`source_dirty` 记成脏工作区。

```
bash wt-media-workspace/scripts/build-desktop-frontend.sh
cd wt-media-desktop/src-tauri && cargo tauri build --bundles dmg --no-sign
```

1. 点「打开云端视频」→ **系统默认浏览器**打开并播放；应用内不出新窗口，也不再出现「浏览器
   拦截了新标签页」。
2. 点「平台原视频」→ 系统浏览器打开抖音页（同时补第 2 节没量到的那一条）。
3. `本机设置` 里的目录选择器仍能打开（`dialog:allow-open` 走的还是 `windows: ["main"]`）。
4. 窗口本身无回归：标题/尺寸/单实例聚焦（第二次启动仍应退出并聚焦既有窗口）——`create: false`
   要冒的险。
5. 不打印、不写盘任何签名地址；`desktop.log` 里不得出现该地址。

## 7. 顺带查实的 Garage 一问

用户要求查的那条：**Garage v2.x 没有匿名访问，这不是配置漏了**。403 响应体里
`Garage does not support anonymous access yet` 是上游在「没找到 API key」时的硬编码拒绝；公开
读只有一条路——bucket 的 **website 模式**（`garage bucket website --allow`，bucket 名须即公开
域名并配 DNS），**bucket 级匿名访问是 WIP（上游 PR #1306，目标 3.0）**。本部署恰好两套都在：
`data.bucket.oss.longyanyue.cn` 是 Garage 的 `s3_web` 只读网站，`s3.oss.longyanyue.cn`
（bucket `data`、prefix `dev/`）是 S3 API。**桶侧没有可翻转的开关**，任务 26 改走签发是唯一
方向；本任务不改这条路径，也不动桶。

## 8. 遗留

- 真机验收 5 条未做（等用户重建 DMG），因此本任务**未关闭**。
- 任务 26 落档时登记的那条**已裁并落地**（2026-10-01，用户裁定「删掉」）：`storage.PublicURL` 连同
  `publicBaseOf`、`registry.publicBase` 与 4 条相关用例已删除，提交 cloud `594a99c`。
