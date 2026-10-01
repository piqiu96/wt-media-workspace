# 任务 17 证据：我的素材详情显示本机下载目录并可打开（Desktop + Cloud）

日期：2026-09-30　仓库：`wt-media-desktop`（`src-tauri`）+ `wt-media-cloud`（前端 `web/`）
范围：新增一个 Desktop 命令 + Cloud 前端一处渲染；无迁移、无后端 API、无状态枚举

提交：`wt-media-desktop 496e6a7`（命令）、`d890268`（构建快照）；`wt-media-cloud 390168d`（前端）、`aabb9bb`（用例收紧）

## 1. 来源

用户裁定，原文：

> 我的素材的详情里还需要加一项，已下载的素材，需要有展示下载目录的地方同时能打开目录快速找到原视频

> 放在文件新信息一栏里

范围裁定（本轮问过后由用户选定）：**折进 CHG-069 任务 17**，允许把 CHG 从「只改 Cloud」扩到
`wt-media-desktop/src-tauri`，同步更新 `change.md` §2 / §4 / §5。

## 2. 动手前核实：现有的两个「打开」命令都到不了目录

| 命令 | 实际动作 | 为什么不能用来做这一条 |
|---|---|---|
| `local_open_saved_file(name)` | `open::that(文件)` | 把**文件本身**交给默认程序——视频会开始播，运营要的是「它在哪个文件夹里」 |
| `local_open_place(place)` | 按位置标签打开 app 自有目录 | `place` 是封闭词表（`desktop`/`agent`/`data`），下载落点不在其中，且它**没有从文件名出发的入口** |

所以「按名字定位到已下载文件**所在目录**」这件事，Desktop 侧今天不存在，必须新增一条。选它而不是
「在文件管理器里选中该文件」，是因为后者是三个平台分支（`open -R` / `/select,` /
`FileManager1`），而本仓 `bundle.targets` 是 `all`——写一条只有 macOS 能跑的分支等于另外两个
平台拿不到实现。登记在 `change.md` §5 任务 17「不在本轮」。

**值的两半各来自哪里**（这一条是本任务最容易做错的地方）：

- 文件名：`file_transfer_tasks` 里这张用户自己的下载任务（`asset_type=material` +
  `asset_id` + `purpose=user_download` + `execution_scope=local_agent` + `status=success` +
  非空 `file_name`）。`ListTasks` 按 `created_at DESC, id DESC` 返回，取第一条。
- 目录：Desktop 量出来的 `local_saved_file_states`（`local_saved_file_states` 在所有已知保存
  位置里找这个名字）。**前端一次都不拼路径。**

## 3. 先红

3 份用例（本轮新增的 14 条）在实现之前跑：

```
Test Files  3 failed (3)
     Tests  14 failed | 54 passed (68)
```

红的正好是新增的 14 条（`downloadFacts` 6 + `desktopBridge` 3 + `MaterialDetailDrawer` 5），
既有的 54 条一条不红。做法是 `git checkout ebfae03 -- <三个源文件>`（实现之前那一版）再跑，
跑完 `git checkout HEAD -- …` 还原，`git status` 空。

Desktop 侧不做这一步「整份回退」的对照：把 `containing_dir` 整块撤掉是**编译不过**，
那种红什么都证明不了（这条在本 CHG 的前序任务里已经吃过一次）。Rust 侧的判别力放在 §6 的
R1–R3。

## 4. 实现

**Desktop（`wt-media-desktop`）**

- `src-tauri/src/commands/reveal.rs`：把 `reveal` 里的 `open::that(directory)` 提成
  `pub(crate) fn open_directory`，`reveal` 改为调用它。两处各写一份 `open::that` 就是两个
  「这台机器怎么打开文件夹」的答案。
- `src-tauri/src/commands/downloads.rs`：新增
  ```rust
  fn containing_dir(found: &Path) -> Result<&Path, String>
  #[tauri::command]
  pub fn local_reveal_saved_file(name: String) -> Result<String, String>
  ```
  `local_reveal_saved_file` = `settings::save_places()` → `saved_files::find_in_known` →
  `containing_dir` → `reveal::open_directory`，返回打开的目录。收**名字**不收路径，与
  `local_open_saved_file` 同形；`find_in_known` 里的 `file_name_of` 是「名字不是路径」这条
  规矩的唯一实现。
- `src-tauri/src/main.rs`：`commands::downloads::local_reveal_saved_file,` 追加进
  `generate_handler!`。
- 测试：`the_directory_is_the_one_the_file_was_found_in`、
  `a_path_with_nothing_above_it_is_refused`、`#[ignore]` 的
  `reveal_saved_file_opens_the_directory_the_file_is_in`；注册守卫的分母 4 → 5。
- 能力文件不用改：`capabilities/default.json` 的 `core:default` 覆盖 app 自定义命令。

**Cloud（`wt-media-cloud/web/`）**

- `modules/transfer/downloadFacts.js`：新增纯函数 `downloadedFileName(tasks, assetId)`。
- `modules/transfer/desktopBridge.js`：`TRANSFER_COMMANDS` 增 `revealSavedFile`，新增
  `revealSavedFile(name)`（与 `openSavedFile` 同一形状、同一条规矩，连空名字的拒绝文案都
  逐字相同）。
- `modules/materials/MaterialDetailDrawer.vue`：在 `mine` 上下文里读一次任务表 →
  `savedFileStates([name])`，在「文件信息」卡里渲染目录 + 「打开目录」；读不到本机时整行
  不出现。

## 5. 「已下载」的判据（本任务的核心约定）

判据在**本机事实**里，不在 `video_status` 上。文件状态描述的是**云端那份源文件**：

- 一块云端已就绪、本机从没下过的素材，`video_status === 'ready'` 为真，磁盘上却没有东西；
- 一份已经下好、云端还在准备的文件，照样躺在磁盘上。

拿 `video_status` 当条件，两种情况下都会说谎。「读不到本机」也不写成「文件不在」——与下载中心
同一条约定（浏览器读不了本机，Desktop 也要扫过才知道）。

## 6. 变异对照（每条新断言都要能红）

Cloud 前端，逐条施加后只跑对应那一份用例，还原后核对 sha256：

| 变异 | 结果 |
|---|---|
| M1 去掉 `asset_type` 过滤 | FAIL `… ignores everything that is not this material, this machine and this action` |
| M2 去掉 `execution_scope` 过滤 | 同一条 FAIL |
| M3 去掉 `purpose` 过滤 | 同一条 FAIL |
| M4 去掉 `status` 过滤 | 同一条 FAIL |
| M5 不按 `asset_id` 匹配（取第一条） | 该条 + `has no answer when the executor never reported a name` FAIL（2 条） |
| M6 空文件名也算命中 | `has no answer …` FAIL |
| M7 命令名写成不存在的名字 | `pins the command names the Desktop repository registers` + `sends the name the executor reported` FAIL（2 条） |
| M8 去掉「文件名必须有」的拒绝 | `refuses in a browser and refuses without a name` FAIL |
| M9 去掉「只在我的素材里问本机」 | `asks this machine only in the 我的素材 context` FAIL |
| M10 把这一块从「文件信息」卡里搬走 | `says nothing at all when this machine has nothing measured` FAIL |
| M11 拿 `video_status` 当判据 | `does not read the local copy off the file state` FAIL |
| M12 读不到本机时写「未下载」 | `says nothing at all …` FAIL |

Rust：

| 变异 | 结果 |
|---|---|
| R1 把命令从 `generate_handler!` 里撤掉 | FAIL `every_command_in_this_module_is_registered` |
| R2 去掉「没有上一层目录」的那次过滤 | FAIL `a_path_with_nothing_above_it_is_refused` |
| R3 守卫分母写小一位（5 → 4） | FAIL `every_command_in_this_module_is_registered` |

**第一遍跑出三条「施加了也不红」的读数**，逐条补完才得到上表：

1. **M1 全绿**。`asset_type` 在今天没有任何用例翻过它（`model.AssetMaterial` 只有一个取值，
   库里 36 行全是 `material`）。补一条 42 号但另一类资源的用例（取值沿用同文件第 175 行的
   既有写法），改后红。
2. **M11 全绿**。`does not read the local copy off the file state` 只切了**模板**那一块，
   把 `video_status` 写进取事实的 `watch` 体里它看不见。补一条对那条 `watch` 体自身的断言
   （整份源码不能这样断言——云端视频地址那条 watch 就按文件状态分支），改后红。
3. **M13 全绿（切片锚点自己坏了）**。`puts the download directory in the 文件信息 card`
   原本以**下一张卡的标题**为切片终点，两张卡之间的空档被算了进来：把这一整块搬到卡外的空档
   里，29 条仍全绿。改成切到该卡自己的 `</section>`，同一次搬迁立刻红（28 passed / 1 failed）。
   这条与 M10 是同一对：M10 证明「元素没了会红」，M13 证明「元素搬出卡片也会红」——只有前者
   时，一句「在文件信息卡里」的说法是没有守卫的。

三条修补都做了改前/改后两次读数，源码还原后与提交字节一致（sha256：`downloadFacts.js
75d603dc…`、`desktopBridge.js e235b462…`、`MaterialDetailDrawer.vue f281aaab…`、
`downloads.rs f30a1faa…`、`main.rs 6e291db3…`）。

## 7. 后绿与读数

最后一次改动之后重跑：

- `npx vitest run`（cwd = `web/`）：**46 文件 / 405 用例全绿**。
- `cargo test --offline`（cwd = `src-tauri/`）：**498 条里 492 passed / 0 failed / 6 ignored**。
  6 条 ignored 是本仓既有约定（会真的开窗口 / 碰外部环境的那几条）。
- `npm run build:cloud`、`npm run build:desktop`：均 exit 0（只有既有的 chunk 体积提示）。
- 收尾后 `wt-media-cloud` 与 `wt-media-desktop` 的 `git status --porcelain` 均为空。

## 8. 被 `#[ignore]` 的那一条：实测与一处会骗人的读数

`cargo test --offline -- --ignored reveal_saved_file` → `1 passed`。但「测试过了」与「窗口开了」
是两件事，所以另做了两次观察：

- **数 Finder 窗口会得到 0（骗人的读数）**。跑之前 0，跑完立刻数仍是 0，间隔轮询 5.8 s 一路
  0。原因不是命令没生效，而是这条测试自己紧接着 `remove_dir_all`——目录没了，Finder 把窗口
  关了。
- **阳性对照**：手工 `/usr/bin/open -- <目录>`（就是 `open` crate 5.4.0 的 macOS 实现，
  `macos.rs:commands`）在本机四种路径形态下都让窗口数 0 → 1。
- **决定性读数**：把该测试里那次 `remove_dir_all` 临时换成 `sleep 20`（探针，用完从备份还原，
  `git diff` 空），跑起来时窗口数 **1**，窗口标题就是 `wt-media-reveal-saved-37036`——与探针
  打印的目录一致。命令本身从头到尾都是好的，是测试的收尾时序把可观测的证据擦掉了。

结论：这条 `#[ignore]` 的用例只证明「spawn 这一步没报错」；「窗口真的开了」由上面第三条给出。
单看窗口计数会把一个正常的实现对错判成没生效。

## 9. 实机数据核对（走查的前置条件）

走查环境（`m2b-local-acceptance.sh all --force-restart` 重建之后）读开发库：

```
分子：purpose=user_download AND execution_scope=local_agent AND status=success        8 行
其中 file_name 非空                                                                    8 行
分母：file_transfer_tasks 全部                                                        36 行
涉及的素材：27 / 33 / 34 / 151 / 152 / 153（各 1～2 行），全部 requested_by = 3（operator01）
```

另一半（本机）：

```
~/Library/Application Support/WTMedia/Desktop/settings.toml
  save_dir = "/tmp/wt-media-m4a-acceptance"
  known_save_dirs = ["/tmp/wt-media-m4a-acceptance"]

ls -d /tmp/wt-media-m4a-acceptance   → No such file or directory
find /tmp …  -name '*-27.mp4' 等      → 无
```

`save_places().search` 就是这一个目录（`settings.rs:220` 的 `SavePlaces`：chosen 在前、历史在
后），`find_in_known` 对读不到的目录不是命中而是记进 `unreadable`（`saved_files.rs:337`），
所以**今天这一行不会对任何素材出现**。这不是缺陷，是这台机器上确实没有那份文件。

**走查前置条件**：先在 Desktop 里真的下载一块素材。Agent 写入时会建目录
（`wt-media_agent/storage/download_sink.py:216`：`path.parent.mkdir(parents=True, exist_ok=True)`），
所以「下载一次」足够造出这一行需要的全部条件。若不下这一份，走查会看到「这一项没出现」并据此
判断功能没做——那是误判。

**没有走 API 读回**：`admin` 与 `operator01` 两个账号登录都被
`20010 当前账号已在其他位置登录` 挡住（走查环境里已有会话），而 `replace_existing: true` 会把
走查环境挤下线，所以没有强行登录。无会话请求 `POST /api/v1/material-usages/3/restore` 得到
`11001`，说明端点确实受会话约束；这一条在上一个任务里已登记。本轮的核对因此走直连数据库 +
本机文件系统两处，比接口更接近这两半事实的来源。

## 10. 提交后重建与产物读回

`all --force-restart`（提交后）：三道构建前门与两份构建产物全过——`Cloud: PASS` /
`Agent: PASS` / `BitBrowser via Agent: PASS` / `Desktop assets: fresh PASS` /
`DMG: fresh PASS` / `Login smoke: PASS user=admin`，exit 0。**本轮没有出现**那条已知的
「Agent `GET /api/v1/status` 偶发假 FAIL」。

产物读回（构建时间 20:12–20:13，在本轮提交之后）：

| 位置 | 读数 |
|---|---|
| `.generated/frontend/assets/`（分母 32 个 js） | `local_reveal_saved_file` 1 个文件命中、`下载目录` 1 个、`detail-local-file` 1 个、`打开目录` 2 个（另一处是 `desktopBridge` 的报错文案） |
| `web/dist-desktop/assets/` | 与上面同一组哈希（`MaterialDetailDrawer-zUb2cJAH.js`、`units-D3DQfcGz.js`），同样读数 |
| `target/release/wt-media-desktop-shell` | `local_reveal_saved_file` 在（阳性对照：同族的 `local_open_saved_file` 也在），新增的错误文案也在 |

读回自带的对照：同一次扫描里，同族的旧命令字符串在（说明读的是真产物），而该在的新字符串也在。
`strings` 读中文会漏（把多字节串当成不可打印直接丢掉，同一个二进制上「无法打开」读 0 而
`grep -a` 读 2），这一条读数用的是 `grep -a`。

本轮最后一次改动是**用例**（`aabb9bb`），不进产物，所以没有为它重建；上面两份产物与提交后的
源码一致。

## 11. 边界与遗留观察

- 不动后端 API、数据库字段、状态枚举、权限模型与业务语义。
- 不在文件管理器里选中那个文件（见 §2 的 `bundle.targets = all`）。
- 「已下载」不进列表列与筛选——用户只说了详情。
- **遗留观察（留给走查）**：`local_reveal_saved_file` 的返回值（打开的目录）没有单测。命令体
  要 `settings::save_places()` 打真实数据根，单测够不到；能测到的两半（`find_in_known` 与
  `containing_dir`）都在，spawn 那一半在 §8。返回值在页面上没有被使用（前端只关心有没有抛错），
  所以这条不构成当前的风险，登记备查。
- **遗留观察**：同一素材存在两行成功下载时（库里 153 就有两条，第二条名字带 ` (2)`），取的是
  服务端返回的第一条，也就是**最新**的那一条，可能不是磁盘上运营正在找的那一份。文件是同一块
  素材重下的，两条任务通常指向同一个文件；若走查看到「目录对了、文件名是前一版」，那是这个
  取法的边界，登记备查。
- 真实点击走查仍留给用户：本轮能给的证据是「产物里有这一行与这颗按钮」+「命令会在文件管理器里
  打开那个目录」，不是「我在页面上点过了」。
