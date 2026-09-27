# Q-11 选项 ②：「把这个目录也作为查找位置」读数（2026-09-27）

本文件记录 Q-11 的裁定（用户 2026-09-27 选定**选项 ②**：设置页给一个入口，用文件夹对话框挑目录、写进已有的 `known_save_dirs`，**不扫文件系统、不动合同、不加第二份名单**）落到代码后的读数。裁定原文在 `checkpoint.md` 的 Q-11 条目。

- 判据一律「命令／手动动作 → 期望 → 实际 → PASS/FAIL」，**未跑的一律写「未跑」并说明原因**，不写成通过。
- 本文件不含凭据、Cookie、签名 URL、本机用户名与绝对路径。
- 提交：Desktop 仓 `16e0224`（五个 Rust 文件）；Cloud 仓 `0b861e4`（六个 web 文件）。

## 1. 交付内容与提交边界

| 仓 | 提交 | 文件 | 动了什么 |
| --- | --- | --- | --- |
| wt-media-desktop | `16e0224` | `src/settings.rs`、`src/dto/settings.rs`、`src/commands/settings.rs`、`src/commands/downloads.rs`、`src/main.rs` | `note_search_dir` / `SearchNote`、`SearchDirectoryView`、`add_search_dir` / `store_search_dir`、`local_pick_search_directory` 及其注册 |
| wt-media-cloud | `0b861e4` | `web/src/apps/desktop/features/local-settings/{service.js,local-settings-view.js,LocalSettingsPage.vue}`、三个测试文件（含新增 `localSettingsSearchWiring.test.js`） | 命令映射、`normalizeSearchDirectoryView`、`pickSearchDirectory`、`describeSearchDirectory`、按钮与提示、mock 分支 |

**边界（可对照 `git show --stat` 复核）**：

- **合同零改动**：两个提交都没有 `docs/contracts/`、`docs/engineering/`、任何 `AGENT-INDEX.md` 或跨仓接口文件；Cloud 提交只含 `web/` 下的六个文件。
- **Agent 仓零改动**：查找空间只由 Desktop 自己的 `settings.toml` 决定（`saved_files::presences`、`find_in_known`、`local_open_saved_file` 都读 `settings::save_places()`），本次未改 `wt-media-agent` 任何文件。
- **磁盘 schema 零改动**：`SCHEMA_VERSION` 仍是 `2`（diff 里它只作为上下文出现），`UserSettings` 的字段一行未增未删；新增的 `SearchNote { added, dropped }` 是**返回值**，不落盘、不序列化。入册用的还是既有的 `known_save_dirs`。

## 2. Desktop 侧

### 2.1 套件

| 仓 | 命令 | 读数 |
| --- | --- | --- |
| wt-media-desktop | `bash scripts/test.sh` | Rust workspace `490 passed / 0 failed / 5 ignored`；`control.test.sh` 12 passed / 0 failed；`release-versions.test.sh` 20 passed / 0 failed；`package-release-macos.test.sh` 无输出即通过（脚本 `set -euo pipefail`，它若失败则后面的 release-versions 不会运行） |
| wt-media-desktop | `cargo test --workspace <filter>`（逐条点名） | 见 2.2 的十个测试，全部 `ok` |

**差值**：`+10`，与 2.2 名单的条数相等。基线取 `checkpoint.md` §Recent verification 记下的同一工作树在读改前那次重跑（Desktop `9b85bf2`，即本提交的父提交）：**480 passed / 0 failed / 5 ignored**；改动后 **490 passed / 0 failed / 5 ignored**，ignored 数与 failed 数都未变。（`scripts/test.sh` 注释里的「377 tests」是更早修订的读数，不用它做基线。）

### 2.2 新增的十个测试（改动后全部 `ok`）

| 文件 | 测试 | 钉住的事实 |
| --- | --- | --- |
| `settings.rs` | `a_search_directory_is_added_without_becoming_the_choice` | 入册只进历史，`save_dir` 不变 |
| `settings.rs` | `a_directory_already_searched_is_not_added_again` | 已在范围内 = 无变化（不占第二个名额） |
| `settings.rs` | `adding_a_search_directory_reports_the_oldest_it_evicted` | 超过上限时返回被挤掉的那个 |
| `settings.rs` | `a_save_keeps_a_noted_directory_behind_the_choice` | 后续 `save` 归一化后，入册的目录仍在选择之后 |
| `dto/settings.rs` | `the_search_directory_keys_are_pinned` | 键集 `added/dropped/picked/searched`；`dropped` 是 JSON `null` |
| `commands/settings.rs` | `a_search_directory_is_added_without_becoming_the_directory_in_use` | v1 文件 + 旧目录 → 两个都在查找空间、**选择未变**、文件被升到 v2 |
| `commands/settings.rs` | `a_directory_already_searched_is_not_added_again` | 命令层同上，且 `searched == 1` |
| `commands/settings.rs` | `the_search_space_is_bounded_and_the_eviction_is_named` | 计数停在 `MAX_KNOWN_SAVE_DIRS`，**被报为挤掉的那个真的不再被查找** |
| `commands/settings.rs` | `adding_a_search_directory_does_not_undo_clearing_the_choice` | 已「清除」的机器不会被入册顺带重新指定下载位置 |
| `commands/settings.rs` | `a_search_directory_that_cannot_be_used_leaves_the_file_alone` | 三种不可用写法都在开文件之前被拒；文件字节不变（**没有**被顺带升级） |

### 2.3 变异臂（每条都真的转红了）

原始树（未变异）读数：`490 passed / 0 failed / 5 ignored`。

| 臂 | 变异 | 期望转红的测试 | 实际 |
| --- | --- | --- | --- |
| M1 | 去掉 `note_search_dir` 里的 `search_dirs().contains` 早返回 | 去重两条 | **RED**：`settings::tests::a_directory_already_searched_is_not_added_again`、`commands::settings::tests::a_directory_already_searched_is_not_added_again` 双双 FAILED |
| M2 | `let dropped = dirs.get(MAX_KNOWN_SAVE_DIRS).cloned();` → `None` | 挤掉的两条 | **RED**：`settings::tests::adding_a_search_directory_reports_the_oldest_it_evicted`、`commands::settings::tests::the_search_space_is_bounded_and_the_eviction_is_named` 双双 FAILED |
| M3 | `add_search_dir` 改用 `remember(Some(dir))`（把入册做成「顺便改当前目录」） | 「不改变选择」那条 | **RED**：`commands::settings::tests::a_search_directory_is_added_without_becoming_the_directory_in_use` FAILED（同过滤器的 settings 层那条仍通过，因为它不经过命令层） |
| M4 | 删掉 `add_search_dir` 开头的 `check_save_dir` 判据 | 拒绝并保持文件不变那条 | **RED**：`commands::settings::tests::a_search_directory_that_cannot_be_used_leaves_the_file_alone` FAILED（同一过滤器下 save_dir 的那条仍通过） |

M3 是关键臂：它把「入册」实现成「换个保存位置」，也就是这个入口最可能被写错的样子——新下载会静默改道。

## 3. Cloud Web 侧

### 3.1 套件与构建

| 命令 | 读数 |
| --- | --- |
| `npm test` | **41 files / 312 tests，全绿**（改动前同一读数为 40 files / 300 tests，见 `20260927-walkthrough-defects.md` → **+1 文件 / +12 测试**） |
| `npm run build:cloud` | `✓ built`（无错误） |
| `npm run build:desktop` | `✓ built`（无错误） |

两个 build 都要跑：单测不编译 `.vue`，模板里的导入错了只会在这里现形。

### 3.2 新增／改动的测试

| 文件 | 内容 |
| --- | --- |
| `localSettingsService.test.js`（30 tests） | 命令表多一项 `addSearchDirectory: 'local_pick_search_directory'`；picker 调用**只有命令名一个参数**（整条 `invoke.mock.calls[0]` 比对）；`null` 与 `undefined` 两种取消都归为 `null`；normalizer 的 `dropped: null` 与 `added` 默认值 |
| `localSettingsView.test.js`（43 tests） | `describeSearchDirectory` 三分支：加入（success，带「以后下载仍保存到当前保存位置」）／已在范围（info，**不含**「已加入」）／挤掉（warning，点名被挤掉的目录 + 「已不存在」） |
| `localSettingsSearchWiring.test.js`（**新增**，5 tests） | 页面接到 `pickSearchDirectory` 与 `describeSearchDirectory`；取消分支在渲染**之前** return；**不**调 `setSaveDir` / `pushSaveDir`（并带阳性对照：同一套断言对 `saveSaveDir` 必须命中）；提示句存在 |
| `localSettingsService.test.js`（mock 段） | mock 的 picker 第一次 `added: true`、第二次 `added: false`；计数把当前选择算进去（选择 + 一个入册目录 = 2） |

### 3.3 变异臂（每条都真的转红了）

原始树（未变异）读数：`41 files / 312 tests` 全绿。

| 臂 | 变异 | 期望转红 | 实际 |
| --- | --- | --- | --- |
| W1 | 页面 handler 改成先 `service.setSaveDir('/picked')` 再取答案 | 接线测试的否定断言 | **RED**：`localSettingsSearchWiring > does not store or push a save location`，`expected '…' not to contain 'setSaveDir'` |
| W2 | `pickSearchDirectory` 不再对 `null` 特判 | 取消不是答案那条 | **RED**：`localSettingsService > answers a cancelled picker with nothing…`，`expected { picked: '', added: false, … } to be null` |
| W3 | `describeSearchDirectory` 的「已在范围」分支失效 | 无变化不说成加入那条 | **RED**：`localSettingsView > does not report a change when the directory was already searched`，`expected 'success' to be 'info'` |

W1 是关键臂，且它证明的是**否定**断言真的能失败——否则「没调 setSaveDir」这句话在实现真的调了的时候也会通过。

## 4. 本次**未覆盖**的部分（如实登记）

| 未覆盖 | 为什么没跑 | 谁能跑 |
| --- | --- | --- |
| **原生文件夹对话框那一行**（`open_folder_dialog` → `blocking_pick_folder`） | 需要真人点一次系统对话框；自动化只能测到它之前（`chosen_path`、`add_search_dir`）与它之后（查找空间真的变大）。它是 `local_pick_save_directory` 与本次新命令**共用**的那一行——保存位置那条走查里已被真人点过 | 用户（走查环境） |
| **页面上按下「添加查找位置」的端到端确认**（061-AC-15 的页面半边） | 同上，且需要五个进程的运行环境 | 用户（走查环境） |
| **「旧文件由『已不存在』变为可打开」的实机读数** | 需要一台真有旧目录、且其设置文件为 v1 的机器；开发机上没有这样的 `settings.toml`。命令层与查找空间层的等价读数在 2.2 的 `a_search_directory_is_added_without_becoming_the_directory_in_use` 与 `the_search_space_is_bounded_and_the_eviction_is_named` 里 | 用户（走查环境）或一台真机 |
| `store_search_dir` / `set_save_dir`（吃真实数据根的薄封装） | 与既有的 `set_save_dir` 同形：它们只做 `layout()` + `write_root()`，规则都在 `add_search_dir` / `write` 里，而后者有测试。**本次没有为它单独造测试**，与仓库既有做法一致 | — |

上面四条都不改变「机制已落地并有红过的测试」这一结论，但**都不能算作已验收**：061-AC-15 的页面半边仍是用户的签收项。

## 5. 复现命令

| 仓 | 命令 |
| --- | --- |
| wt-media-desktop（worktree `m4-a`） | `bash scripts/test.sh` |
| wt-media-desktop | `cargo test --workspace a_search_directory` / `cargo test --workspace already_searched` / `cargo test --workspace evict` / `cargo test --workspace cannot_be_used` |
| wt-media-cloud（worktree `m4-a`，`web/`） | `npm test` |
| wt-media-cloud | `npm run build:cloud && npm run build:desktop` |

变异臂不是脚本，是手工改一处再跑同名过滤器；四个臂的改法在 §2.3 / §3.3 的第二列，读法在第四列（失败测试名与断言原文）。
