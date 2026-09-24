# Evidence: T-06 清理闭环

## Purpose

交付 AC-07：**只删可安全再生文件与已轮转历史日志**，白名单排除
素材/成片/SQLite/检查点/待回传结果/正在写入文件，并**回报实际释放字节**。
两个命令供 T-08 的「本机设置」页调用：

| 命令 | 回答 |
| --- | --- |
| `local_cache_cleanup` | 清空本组件缓存根，保留缓存根自身 |
| `local_log_cleanup(source)` | 删除**一棵**日志树的已轮转归档，活文件永不删 |

## Method

```bash
cd wt-media-desktop && bash scripts/test.sh                    # 起点 255 passed，只增不减
cd wt-media-desktop/src-tauri
rustfmt --edition 2021 src/cleanup.rs src/commands/cleanup.rs src/dto/cleanup.rs
python3 /tmp/chg058/mutate_t06.py cleanup|cmds|dto              # 变异表，三组各自带阴性对照
cargo test --offline commands::cleanup::tests::probe_real_machine -- --nocapture
                                                                # 真机预览探针（只读，跑完即撤销）
```

## Actual

### 落点表

| 文件 | 性质 | 行数 | sha256(前 12) |
| --- | --- | --- | --- |
| `src-tauri/src/cleanup.rs` | 新（规则本体 + 14 条用例） | 768 | `e9048f66c36f` |
| `src-tauri/src/commands/cleanup.rs` | 新（接线 + 5 条用例） | 387 | `34ee2c9c4ea2` |
| `src-tauri/src/dto/cleanup.rs` | 新（线上形状 + 2 条用例） | 158 | `c78c0b40aa63` |
| `src-tauri/src/commands/storage.rs` | 改：`Resolved`/`resolve` 升 `pub(crate)`、抽出 `tree(source)` | 705 | `b5dc5c7d538b` |
| `src-tauri/src/{commands,dto}/mod.rs` | 改：各 1-2 行声明 | — | — |
| `src-tauri/src/main.rs` | 改：`mod cleanup;` + 2 个命令**追加**在 `invoke_handler!` 末尾 | — | — |

`commands/storage.rs` 的三处改动都是 T-06 的语义改动，不是格式化（`git diff` 已逐行确认）：
两个解析器会是两条没人保证一致的规则——**页面可能列一棵树、清另一棵树**。

### 保护是一条**路径**，不是一个名字清单

里程碑的白名单有六类。**其中五类根本不在清理能指到的目录里**，所以「不删素材」不是一段需要维护的
判断代码，而是目录布局的性质：

| 类别 | 所在目录 | 清理能指到的三个根 |
| --- | --- | --- |
| 素材 / 成片 / SQLite / 检查点 / 待回传结果 | `AppPaths::data`（含 `versions/`） | 缓存根、Desktop 日志树、Agent 日志树 |

**命令不接受路径参数**：`local_cache_cleanup` 什么都不收，`local_log_cleanup` 收的是**来源标签**
（`"desktop"`/`"agent"`），在两个**由应用自己解析出来**的目录之间做选择。
于是页面能决定「清本应用的哪样东西」，不能决定「清磁盘上的哪个目录」。

分母与阳性对照（`the_five_categories_are_outside_every_directory_a_cleanup_can_name`）：
**5 类 × 3 个可达根 × 2 种布局 = 30 次比较**全部断言「不在内」，同时**同一个比较**对一个真的在缓存根下的
路径断言「在内」——「对什么都答 false」的谓词不能通过这条用例。另一半由 T-03 的
`app_paths::cache_is_never_inside_the_data_root` 从对面钉住（缓存根从不落在数据根里）。

### 可达树里的逐类规则

| 输入 | 处理 | 理由（`kept` 的线上词） |
| --- | --- | --- |
| 活文件（`desktop.log`/`agent.log`/`error.log`/`task.log`） | 留 | `live` — 写在写者手里，删了在句柄关闭前一个字节也不释放 |
| 应用没写过的名字（T-02 之前的 `desktop-20260924-1.log`） | 留 | `unrecognised` — 读者自己的注释说这种文件「不是我们的」 |
| 符号链接 | 留 | `symlink` — 链接指向的内容不在这棵树里（`storage.rs` 量体积时同一条规则） |
| 目录以外的特殊文件（套接字等） | 留 | `special` — 删它不是清理，是破坏 |
| 空子目录 | 删 | 它是可再生的；**仍持有被留项的子目录跟着留** |
| 树本身 / 缓存根本身 | 留 | 清的是内容，不是容器 |

`reader::list` 是**查看器与清理共用的唯一分类源**，所以「人看到的」与「会被删的」不可能不一致——
这是把保护写成路径之后剩下的那一半。

### `freed_bytes` 的判据：不是可用空间差值

`freed_bytes` 是**被删掉的那些文件的逻辑大小之和**，**不是**两次 `available_bytes_for` 读数之差。
理由写在 `cleanup` 与 `dto::cleanup` 的模块注释里：卷在机器上每个进程脚下都在动，这样的差值**可以为负**，
而这里要向人报告的是「这个按钮做成了什么」。

独立对账（`a_freed_byte_count_is_what_an_independent_walk_says_the_tree_lost`）：释放字节数必须等于
`storage::directory_bytes`（**另一条代码路径**，T-05 的模块）在**同一棵树**上少掉的量。变异 C7
（`metadata.len()` 改成 `+= 1`）被它连同另外四条一起打掉。

### 两种失败，两种处置

| 情形 | 结果 | 为什么不是另一种 |
| --- | --- | --- |
| 树读不出来 | 整次调用 `Err` | 什么都不确定，报「已释放 0 字节」就是 T-05 消灭过的那个 0 MB 谎言 |
| 单个 `remove_file` 失败 | 报告里一行 `failures`，`freed_bytes` 只累计返回 `Ok` 的那些 | 其余文件确实删掉了，把整次调用判失败会抹掉已经发生的事实 |

页面因此能区分「没东西可删」「都删了」「都没删成」——一个数字做不到这件事（`dto::cleanup` 的头注释）。

### 新用例抓出的一个真缺陷（本 Task 第三处由测试驱动的改动）

`a_failed_removal_reaches_the_page` 第一次跑就是红的：`left: 2, right: 1`。
报告里对**同一个文件**出现两条——`Permission denied (os error 13)`（文件本身）
**和** `Directory not empty (os error 66)`（它的父目录）。根因是文件删除失败那一臂没有把
`empty = false`，于是父目录仍去试 `remove_dir`，为同一个问题报了第二条更含糊的错。
修复是那一臂置 `empty = false` 并写明理由；`a_file_that_cannot_be_deleted_is_reported_and_not_counted`
随后加强为 `assert_eq!(outcome.failures.len(), 1)` 并点出文件名。变异 **C10** 打的正是这一行。

### 真机读数（探针，只读，跑完即撤销）

`cargo test --offline commands::cleanup::tests::probe_real_machine -- --nocapture`：

```
PROBE cache=…/src-tauri/.local/cache entries=0 bytes=Ok(0)
PROBE tree=desktop dir=…/src-tauri/.local/logs files=1 would_remove=0 bytes=248
PROBE   desktop.log kind=live bytes=248
PROBE tree=agent dir=/Users/aqiuye/Library/Logs/WTMedia/Agent files=3 would_remove=0 bytes=1674
PROBE   agent.log kind=live bytes=1674
PROBE   error.log kind=live bytes=0
PROBE   task.log kind=live bytes=0
```

探针**不删任何文件**：它用 `resolve` 解出真机的根，再用与 `remove_rotated_archives` 同一份
`reader::list` + 种类过滤算出「会被删的清单」，然后停在那里。

**如实登记的读数范围**：本机两个按钮**会删 0 个文件**——所以**破坏性路径没有被真机验证过**，
这是有意的（为了证明删除能用而删掉用户的真日志不是验证，是损失）。真机上被验证的是：
①两侧根解析到真目录（Desktop 是开发树 `.local/`，Agent 是装机树）；
②缓存根真机上不存在 ⇒ `directory_bytes` 独立地报 `Ok(0)`；
③Agent 树三个活名 `agent.log`/`error.log`/`task.log` 与 T-05 的读数一致（不同时刻的第二次对账）；
④`would_remove = 0`：健康机器上清理是空操作，不会误删。
删除行为本身的判据是临时目录里的 21 条用例与下面的变异表。

### 先红的口径

实现前对空壳跑过一轮：12 条里 9 条红（当时只有 cleanup 5 + commands 5 + dto 2）。
**那一轮的原始输出没有留存**，所以本条只作过程记录，**不作为判据**。
新代码的先红由下面的变异表承担——`ImportError` 式的红什么都证明不了（T-05 记录里已定过这条口径）。

## 计数（只增不减）

| 侧 | 起点 | 现在 | 差额 |
| --- | --- | --- | --- |
| desktop | 255 passed | **276 passed** | **+21**（0 删除，0 skipped） |

逐件对账：`cleanup` 14（新模块）、`commands::cleanup` 5（新模块）、`dto::cleanup` 2（新模块），14+5+2 = 21。
（`cargo test cleanup` 报 21 是因为过滤串是子串匹配，它同时选中后两个模块。）

非测试构建警告：`cargo check` 计 **27 条**（另有 1 行汇总，`grep -c '^warning'` 读 28），**与 T-05 相同**。
`--all-targets` 读 31 行 = 27 + 7 条测试专属 − 5 条重复 + 汇总。
**逐个警告按文件归位后，没有一条落在 `cleanup.rs`/`commands/cleanup.rs`/`dto/cleanup.rs` 上**
（28 条里全部来自 `settings.rs`、`rolling.rs`、`app_paths.rs`、`storage.rs` 与 `filesystem`/`secure_store`/`system`/`updater` 四个空壳）。

## 实现变异：26 行，26 灭，0 等价

三组各自先跑**阴性对照**（未变异的字节上同一条命令必须报 `0 failed`），三组全部通过；
每组跑完断言文件逐字节还原：

| 组 | 目标 | 过滤 | 行数 | 结果 | 还原 sha256(前 12) |
| --- | --- | --- | --- | --- | --- |
| cleanup | `cleanup.rs` | `cleanup::` | 14 | 14 灭 | `e9048f66c36f` |
| cmds | `commands/cleanup.rs` | `commands::cleanup` | 7 | 7 灭 | `34ee2c9c4ea2` |
| dto | `dto/cleanup.rs` | `dto::cleanup` | 5 | 5 灭 | `c78c0b40aa63` |

原始输出：`/tmp/chg058/t06/mutations-{cleanup,cmds,dto}.out`。

### cleanup（14 灭）

| # | 变异 | 判据（打掉它的用例，摘） |
| --- | --- | --- |
| C1 | 缺失的根当作「没东西可删」以外的错 | `an_absent_root_has_nothing_to_delete_and_is_not_created` |
| C2 | 读不到的根答得像空的一样 | `an_unreadable_root_is_an_error_rather_than_a_silent_zero` |
| C3 | 不认符号链接（落到下一条规则） | `a_symlink_is_left_in_place_and_never_followed` |
| C4 | 非普通文件按普通文件删 | `a_socket_is_left_in_place` |
| C5 | 活文件按归档删 | `the_live_file_is_never_touched_and_the_archives_are`、`an_archive_that_cannot_be_deleted…`、`the_log_command_removes_archives…` |
| C6 | 应用没写过的名字也删 | `an_unrecognised_name_is_left_where_the_reader_leaves_it`、`the_log_command_removes_archives…` |
| C7 | 释放字节不是文件大小 | `a_freed_byte_count_is_what_an_independent_walk_says_the_tree_lost` 等五条 |
| C8 | 根连同内容一起删 | `a_root_is_emptied_down_to_its_own_contents`、`the_cache_command_empties…` |
| C9 | 被留项不保留它的目录 | `a_directory_that_still_holds_a_kept_entry_stays_with_it` 等六条 |
| C10 | 删不掉的文件的目录仍然被删 | `a_file_that_cannot_be_deleted_is_reported_and_not_counted`、`a_failed_removal_reaches_the_page` |
| C11 | 日志树本身被删 | `the_log_tree_itself_is_never_removed` |
| C12 | 归档永不被看到 | `the_log_tree_itself_is_never_removed` 等五条 |
| C13 | 删不掉的归档不报告 | `an_archive_that_cannot_be_deleted_is_reported_and_the_live_file_stays` |
| C14 | 保留原因换拼写 | `the_kept_reasons_are_the_pages_vocabulary`、`the_log_command_removes_archives…` |

### cmds（7 灭）

| # | 变异 | 判据（摘） |
| --- | --- | --- |
| D1 | 未知来源默认成 Desktop | `an_unknown_source_is_an_error_rather_than_a_default` |
| D2 | 缓存报告换标签 | `the_cache_command_empties_the_cache_and_not_the_data_root` |
| D3 | 日志报告换标签 | `the_log_command_removes_archives_and_reports_what_it_kept` |
| D4 | 释放字节不到页面 | 同上两条 |
| D5 | 被清的目录不到页面 | 同上两条 |
| D6 | 失败不到页面 | `a_failed_removal_reaches_the_page` |
| D7 | 所有被留项报同一个原因 | `the_log_command_removes_archives_and_reports_what_it_kept` |

**D6 的一处自纠**：首轮 D6（改 `KeptFileFact` 的构造）只被「did not compile」判灭，
按新代码先红的口径这算弱的灭——什么都证明不了。改成整块替换
`failures: outcome.failures.into_iter().map(…).collect(),` 为 `failures: Vec::new(),` 后重跑，
D6 由 `a_failed_removal_reaches_the_page` 真实打掉。

### dto（5 灭）

| # | 变异 | 判据（摘） |
| --- | --- | --- |
| E1 | `freed_bytes` 线上换名 | `the_wire_key_sets_are_pinned`、`an_empty_report_still_carries_every_key` |
| E2 | `files_removed` 线上换名 | 同上 |
| E3 | `kept` 不上线 | 同上 |
| E4 | 被留项的 `reason` 线上换名 | `the_wire_key_sets_are_pinned` |
| E5 | 空的 `failures` 不上线（省掉 `[]`） | `an_empty_report_still_carries_every_key` |

**没有登记为等价的存活行**：26 行全部被真实用例打掉（无「did not compile」式的灭）。

## 边界登记（不静默吸收）

1. **`local_log_cleanup` 一次只清一棵树**（`change.md` §6 D-11）。Q-08 的裁定覆盖**读**两棵树，
   把「删」也延伸过去是**本 Task 的决定**，不是用户的：Agent 的归档是 Agent 的，
   替另一个组件决定它的历史可以删，不能靠一句读的裁定借来。页面仍可给每个树一个按钮。
2. **`FileKind::Other` 永不删**（`change.md` §6 D-12）。真机上的样本就是 T-02 之前留下的
   `desktop-20260924-1.log`：它在查看器里看得见，**留在原地**，想清掉只能手动。
   理由取读者自己的定义（这种名字「不是我们的」），而不是「可能没用所以删了更干净」。
3. **`resolve`/`Resolved`/`tree` 与两个命令体（收 `State`）没有单测**，这是 `commands::agent`/`commands::storage`
   的既有先例：可断言的部分抽成 `source_of`/`report`/`cache_report`/`log_report`，命令体只剩几行接线。
   真机覆盖由上面的只读探针提供（探针**跑完即撤销**，不是常驻用例）。
4. **`freed_bytes` 与卷面的 `available_bytes_for` 差值有意不等**。这条是设计，不是缺口；
   判据是独立walk（见上）。想让两者相等的人会先遇到 `a_freed_byte_count…` 这条用例。
5. **被删文件的父目录**：清理会删掉空掉的子目录（`directories_removed`），
   日志树恒为 0——树本身永不被删（变异 C11 钉住）。
6. **本 Task 收尾时的仓库卫生发现（未纳入本次提交）**：`git status` 显示 **14 个本 Task 之外的文件**
   带改动（`bootstrap.rs`、`paths.rs`、`preflight.rs`、`sidecar/{mod,drain}.rs`、`http/{mod,cloud,local_agent}.rs`、
   `commands/{account,agent,bind,webview}.rs`、`dto/config.rs`、`logging/paths.rs`）。机械核验
   （对 `HEAD` 版本跑 `rustfmt`，逐字节等于当前文件）证明**它们全是格式化、无语义变化**；
   mtime 落在本 Task 时间窗内（22:31–22:32），来源是一次**没有走单文件路径**的格式化调用——
   本仓**不是 rustfmt-clean**，规则要求只对单个文件跑。本次提交**只 add T-06 的路径**，
   这些改动**留在工作区未动**，完整 diff 存档 `/tmp/chg058/fmt-stray/stray-formatting.patch`。
7. **`commands/storage.rs` 的 `tree()` 用 `expect`**：读者认识的每个标签在 `trees()` 里都有树，
   所以查不到只可能是「新来源加进了一个列表而没加进另一个」。那时 panic 是**有意的**——
   静默回退到一个默认目录，正是这个模块要消灭的错误。变异 C/D 组没有单列这一行，
   它由 `an_unknown_source_is_an_error_rather_than_a_default` 从调用侧覆盖（未知标签在解析前就被拒）。
