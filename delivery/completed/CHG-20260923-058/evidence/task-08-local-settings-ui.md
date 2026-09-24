# T-08 证据：本机设置页与日志查看器（CHG-20260923-058）

记录事实，不重复需求。

## 0. 本任务的范围补正（**先说这一条**）

`change.md` §8 的 T-08 行把落点写成 `wt-media-cloud/web`（沿用 §4.4 的盘点）。执行时实测：
**那一半不够**，AC-08 与 AC-09 在改成只有前端之前是够不着的。

| AC | 要什么 | 当时缺什么 |
|---|---|---|
| AC-08 | 查看/修改保存位置 | T-04 交付了 `settings.rs` 模块，但**没有任何命令读它**。T-04 证据边界 1/4 自己写着「设置页与命令面（T-05/T-08）负责」——T-05 没取这一半 |
| AC-09 | 一键打开日志文件夹 | 三仓范围内**没有任何打开目录的命令**；`@tauri-apps/plugin-shell` 不在 `web/package.json`，前端没有第二只手 |

所以 T-08 实际是两半，**登记为范围补正而不是把两个 AC 留成 TODO**：

- **desktop 半**（commit `5ee840c`）：三个新命令 `local_settings_get` / `local_settings_set` /
  `local_open_place`，加 `settings::check_save_dir`、`dto::SettingsView`、`commands::reveal::Place`。
- **cloud/web 半**（commit `bb0136f`）：页面、服务层、纯派生模块、路由、导航、免鉴权名单、测试。

## 1. 计数

| 仓 | 起点 | 终点 | 增 |
|---|---|---|---|
| wt-media-desktop（`cargo test`） | 314 passed / 2 ignored | **336 passed / 0 failed / 2 ignored** | +22 |
| wt-media-cloud/web（`npx vitest run`） | 21 文件 / 101 tests | **25 文件 / 166 tests** | +4 文件 / +65 |

desktop 的 +22 = 4（`settings::tests`）/ 2（`dto::settings::tests`）/ 9（`commands::settings::tests`）
/ 7（`commands::reveal::tests`）；新增 `#[ignore]` 的 `reveal_opens_a_directory_that_is_there` 一条，
**不入 passed**（它会开 Finder 窗口）。web 的 +4 文件 = `localSettingsService` / `localSettingsView` /
`localLogsView` / `localSettingsWiring`。

`cargo test --workspace` 全绿；`npm run build:desktop` 成功（`✓ built in 6.35s`）。

## 2. 先失败的验证：实现变异表

两套harness：`/tmp/chg058/mutate_t08.py`（Rust，四组）与 `/tmp/chg058/mutate_t08_web.py`（JS，四组）。
两者的共同设计：**阴性对照先绿**（pristine 字节必须跑成 0 failed）、每个变异用干净副本、
`finally` + SIGINT/SIGTERM/SIGHUP 还原、还原后校验**摘要一致且树仍绿**（两个不同的断言）。

| 组 | 文件 | 过滤器 | 阴性对照 | 变异 | 灭 | 等价 | 没编译过 |
|---|---|---|---|---|---|---|---|
| settings | `src/settings.rs` | `settings::tests::` | 37 passed | 4 | 4 | 0 | 0 |
| cmds | `src/commands/settings.rs` | `commands::settings::tests::` | 9 passed | 7 | 7 | 0 | 0 |
| reveal | `src/commands/reveal.rs` | `commands::reveal::tests::` | 7 passed | 7 | 7 | 0 | 0 |
| dto | `src/dto/settings.rs` | `dto::settings::tests::` | 2 passed | 2 | 2 | 0 | 0 |
| service | `local-settings/service.js` | `localSettingsService.test.js` | 20 passed | 14 | 14 | 0 | 0 |
| sview | `local-settings/local-settings-view.js` | `localSettingsView.test.js` | 19 passed | 12 | 12 | 0 | 0 |
| lview | `local-logs/local-logs-view.js` | `localLogsView.test.js` | 17 passed | 13 | 13 | 0 | 0 |
| wiring | 5 个文件 | `localSettingsWiring` + `localAgentBoundary` | 12 passed | 11 | 11 | 0 | 0 |

**合计 70/70 灭，0 等价，0「没编译过」。** 每次击杀报出**具体是哪个用例**（harness 从 libtest 的
`test … FAILED` 行 / vitest 的 JSON reporter 里取名字），不是只报计数。输出存档：
`/tmp/chg058/t08/mutations-*.out`、`/tmp/chg058/t08web/mutations-*.out`。

### 2.1 三次「先灭后补」——变异表抓到的真实覆盖缺口

不是全部一次通过。三条变异**活了下来**，每个都是测试自己的洞，补完再灭：

1. **`lw12`（选中文件时丢掉树）**：原 fixture 的 agent 树是空的，所以「只比文件名」也满足断言。
   改成**两棵树各有一个 `error.log`**（真实场景：两侧都有 `error.log`），并新增
   `selects a file by its tree and its name together` 逐个断言被标记的行。
   → 再跑：KILLED by `selects a file by its tree and its name together`。
2. **`sv13`（mock 按精确级别筛选）**：原断言只写「返回的行都是 warn 或 error」，而 `=== 'warn'`
   也满足；差别恰好在**级别更高的那一行**上。给 mock 加一条 `error` 记录，断言改为逐级别列出
   （`['warn','error']` 与 `linesRead: 3`）。
   → 再跑：KILLED by `filters a mock tail at the chosen level or louder`。
3. **`sv08`（`logFiles` 不做逐文件正常化）** / **`sw08`（「无文件可清」不列 kept）**：
   前者补 `normalizes every file in the listing, not just the tree around it`（断言
   `modifiedSeconds` 而非 `modified_seconds`），后者补 kept 非空分支的 detail 断言。

### 2.2 一处**等价**的登记：`sw04`（本地时区 vs UTC）

`getFullYear()` ↔ `getUTCFullYear()` 只在**年边界**有别。本机是 `CST +0800`
（`node -e "new Date(1774000000000).getTimezoneOffset()"` → `-480`），普通时刻两者相同——
所以第一版用例看不见它（SURVIVED）。

改法不是放宽，是**让用例去本机自己的时区里找一个两者不同的时刻**：四个候选跨 UTC 年边界两侧，
取 `getFullYear() !== getUTCFullYear()` 的那些，逐个断言渲染结果等于本地 getter 拼出的串，
并带阳性对照（同一时刻的 UTC 拼法与它**不相等**，证明不是在比同一个字符串）。
→ 再跑：KILLED by `builds the stamp from the local getters, not the UTC ones`。

**在 `TZ=UTC` 的机器上这个变异是真等价**（两个 getter 恒等，没有任何时刻能把它们分开）。
用例在那个环境下走"确认偏移为 0 后返回"的分支，不假装测过。

## 3. 如实登记的边界

1. **`open::that` 那一行不可测**。`commands::reveal::reveal` 的最后一步是 spawn 平台打开器，
   测它就会在跑测试的机器上开一个窗口。可测的那半是它之前的全部：标签词汇、解析、
   「目录不存在」的拒绝。该分支留为常驻 `#[ignore]` 用例
   `reveal_opens_a_directory_that_is_there`，手工跑 `cargo test -- --ignored reveal_opens`。
   ~~**真机手工验证已做**：页面上的「打开设置文件夹」与两处「打开文件夹」都打开了预期目录。~~
   → **上一句已于 2026-09-25 收回**（原文保留删除线，不抹掉）。它是**无凭证的断言**：记录里没有命令、
   没有输出、没有时刻；更硬的是它与本 CHG 的 `change.md` **直接矛盾**——`§10` 的 AC-08/AC-09 两行
   都把「真机操作」这一臂标为**未执行**（「页面点击本轮没有通路，见 §12『未做』」），`§13` 第 5 项也写
   「不完全满足」。同一份归档里两处说法相反，正确的是 `change.md`，**本行让位**。
   能拿到的实机凭证只有 `open::that` 这一步本身，读数见 **§7**；**页面按钮被真的点过这件事没有发生**，
   那一臂原样并入 CHG-D 的干净机 `manual_acceptance`。
2. **本机设置页不能浏览目录**，只能手输路径。`@tauri-apps/plugin-dialog` 不在依赖里，
   装它要新引一个包 + 一次 capabilitiy 变更；用户裁定「尽量使用开源，尽可能不改轮子」，
   而 `check_save_dir` 已经把「路径不存在」变成一句人话。这**是**能力上的缺口，不是设计偏好，
   故登记：以后若要「点选目录」，那是新任务。
3. **`settings::check_save_dir` 放行「存在但不可写」的目录**。探针会在用户选来放自己素材的目录里
   写字（建临时文件测可写性），而那时任务自己会报权限。与 T-04 边界 4 同一条理由。
4. **libtest 过滤器是子串**：`settings::tests::` 同时命中 `commands::settings::tests::` 与
   `dto::settings::tests::`，所以 settings 组的对照读数是 37（= 26 + 9 + 2）而不是 4。
   登记而非隐藏；每次击杀报的是具体用例名，不受影响。
5. **`main.rs` 的接线行不可断言**（命令真的被 `invoke_handler!` 注册）。
   与 T-07 的 `DiagnosticHost::secrets` 接线行同一类边界。web 侧的 `wiring` 组覆盖了
   **前端**那一半（路由名 ↔ 免鉴权名单 ↔ 导航路径 ↔ 组件文件存在）；Rust 那一半里
   `open::that` 开窗已由 **§7 的配对实验**取到实机读数，`npm run build:desktop` 见 §4；
   **`invoke_handler!` 的端到端「点一下」仍未做**，并入 CHG-D（同 §3 第 1 条）。

## 4. 构建抓到、单测结构上看不见的一条（**这一条值得单独记**）

`npm run build:desktop` 第一次失败：

```
"logKindLabel" is not exported by "src/apps/desktop/features/local-logs/local-logs-view.js",
imported by "src/apps/desktop/features/local-logs/LocalLogsPage.vue".
```

`logKindLabel` 住在 `local-settings-view.js`。**166 个单测全绿**——因为本仓的 vitest
从不编译 `.vue`：它直接 import 纯 JS 的派生模块（页面逻辑放那儿的**原因**就是能被测）。
所以「页面里写错一个 import」这一类错，单测结构上就照不到，**只有构建能照到**，而构建太慢
（6.35s，且要写 `dist-desktop/`），不该是唯一在看的东西。

补法：`localSettingsWiring.test.js` 新增 `desktop page imports`，取出每个桌面页 `<script>` 块里
从**相对路径**模块导入的每个具名绑定，与 `import()` 出来的真实导出表逐个比对；
并带「这段 regex 必须真的匹配到东西」的分母守卫。变异 `wr10`（名字导错模块）与
`wr11`（名字拼错）各证明它能失败：

```
wr10-page-imports-a-name-that-is-not-exported: KILLED by imports only names the target module actually exports
wr11-page-imports-a-misspelled-name: KILLED by imports only names the target module actually exports
```

同类的前车之鉴也在同一个文件里：`names a component file that exists` 的第一版 regex
匹配到了 0 次而**通过了**——分母守卫（`expect(checked).toBe(loaders.length)`）当场把它打掉，
才发现 Vite 会把 `import()` 改写成 `__vite_ssr_dynamic_import__("/src/…")`，路径已经解析过。
两处都留了注释说明，免得下一版正则再退化。

## 5. 与既有测试的适配

- `localAgentBoundary.test.js`：原规则只盖 `init.js` 与 `LocalLogsPage.vue`。新增
  `keeps the whole local-settings surface off the network`，逐个列出四个模块文件，
  断言无 `127.0.0.1` / `localhost` / `fetch(` / `XMLHttpRequest` / `new WebSocket`。
  模块清单**写死**而不是 glob：新文件要显式进清单，那一刻就是检查它的时机。
- `localAgentService.test.js`：**未改**。三条新命令**追加**在 `invoke_handler!` 末尾，
  既有 17 条的精确参数断言因此逐字不变（`main.rs` 里的注释也重申了这条）。
- `AppLayout.test.js`：**未改**，它不断言 `desktopItems`。
- `router.ts` 把路由表导出为 `desktopRoutes`：建 router 要浏览器 history，路由表不需要。
  本仓 vitest 环境没有 DOM（`ReferenceError: window is not defined`），导出后
  `localSettingsWiring.test.js` 能读到**真正被导航的那张表**而不是一段看起来像它的字符串。

## 6. 本轮的两个 commit

| 仓 | commit | 内容 |
|---|---|---|
| wt-media-desktop | `5ee840c` | `feat(chg-058): T-08 本机设置与日志查看器的三个开口` —— 9 个文件，982 插入 |
| wt-media-cloud | `bb0136f` | `feat(chg-058): T-08 本机设置页与日志查看器` —— 13 个文件，2781 插入 |

diff 检查：desktop 侧只暂存了那 9 个路径，13 个只被 rustfmt 重排过的既有脏文件
（`bootstrap.rs`、`commands/agent.rs` 等）**原样留在工作区未提交**；cloud 侧只暂存那 13 个路径，
`dump.rdb`（跑着的 redis 的产物）未提交，`web/dist-desktop/` 被 `.gitignore` 覆盖
（`git check-ignore -v` 确认）。

## 7. 关闭后补记（2026-09-25）：`open::that` 的实机凭证，与 §3 里被收回的那句

§3 第 1 条原写「真机手工验证已做：页面上的三个按钮都打开了预期目录」。**那句收回**，
理由与范围见该条。这一节只放**确实取到了**的那一部分——`open::that` 开出的窗口本身。

**配对实验**（同一台机器，连续三步；探针是 `osascript` 问 Finder，不是推断）：

| 步 | 动作 | 窗口数 | 窗口名 | 这一行证明什么 |
|---|---|---|---|---|
| 1 控制 | `close every window` | **0** | `[]` | 探针能读出「无」——不是永远有值的空心读数 |
| 2 控制 | `open -a Finder /tmp` | **1** | `[tmp]` | 窗口能与「哪一次 open」对上；探针按目录区分，不是常量 |
| 3 受测 | `cargo test -- --ignored reveal_opens` | **1** | `[Agent]` | 受测路径真的开出了一个窗口 |

第 3 步的窗口 `target` 读数是 `/Users/aqiuye/Library/Logs/WTMedia/Agent/`——与
`crate::logging::paths::agent_directory()` 解出的目录**同一路径**（也是本页 AC-09 里
「打开日志文件夹」要去的那个目录）。用例本身 `1 passed; 0 failed; 0 ignored; 337 filtered out`。

⇒ **`reveal()` 的最后一步在真机上被证到了「开出一个指向预期目录的 Finder 窗口」**，
而不是退化成「spawn 返回 `Ok` 就算过」。

**环境说明**：取证时会话处于锁定态（`CGSSessionScreenIsLocked = True`，锁定时刻
`2026-09-25 00:26:18`）。屏幕锁定**不阻止**窗口被创建，只让人看不见；所以这三行读数有效，
但「有窗口」与「有人看见过」是两件事，后者仍未被证明。

**这条用例自身的一处精度**（记录，不在已归档的 C 内改）：`reveal.rs:336` 的
`assert_eq!(opened, directory.display().to_string())` **结构上不可能失败**——`opened` 就是
`reveal()` 内部对同一表达式算出的返回值。用例真正的内容在 `:334` 的
`.expect("the tree exists on this machine")`（opener 报错即 panic）。故本节的读数由**窗口计数**
承担，不由那行 assert 承担。改它属于新任务：C 已归档，运行时代码不在本 CHG 内再动。

**本节明确没有证明的三件**（与 §3 第 1 条同一范围，不重复计数）：

1. 页面上的四个按钮**被真的点过**——未发生。本环境无点击通路：macOS 无 WebKit WebDriver
   （`tauri-driver` 不可用）、`osascript` → System Events 报 `-1743 未获得授权`、会话处于锁定态。
2. Tauri 命令层 `local_open_place`（`place` 串 → `directory_of` → `reveal`）**经 IPC** 的端到端行为。
3. 另外三个「打开文件夹」各自指向的目录——本页只开了 Agent 日志树这一个。

原始读数留在 `/tmp/chg058/t09/reveal-window-paired-experiment.out`（临时目录，不随仓入库）。
