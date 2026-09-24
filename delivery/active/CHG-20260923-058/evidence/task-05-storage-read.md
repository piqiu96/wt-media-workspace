# Evidence: T-05 存储与日志只读命令

## Purpose

交付 AC-06 的两半：**数据取自真实目录**（不是配置里抄的路径、不是缓存下来的旧读数），
**读取失败是错误而不是 0 MB**。三个命令供 T-08 的「本机设置」页调用：

| 命令 | 回答 |
| --- | --- |
| `local_storage_usage` | 可用空间、缓存占用、每棵日志树的字节数与文件数 |
| `local_log_files` | 两棵树里的每一个日志文件（名字、种类、字节、mtime） |
| `local_log_tail` | 某一个文件的尾部若干行，带级别筛选 |

**登记的偏离**：CHG 的 T-05 行写的是「`logging::rolling` 补公开读取面」，实际落点是**新模块
`logging/reader.rs`**。理由与 T-02 的 `Writer` 换代同源：`rolling` 现在是 `file-rotate` 的一层薄壳，
读的规则却必须与那个 crate 的**命名规则**（不是它的 API）对齐，写进 `rolling` 会让人以为读的是它自己的
格式。`rolling` 只多导出两个既有常量（`LOG_FILE_NAME`、`ARCHIVE_FORMAT`），没有新增读取面。

## Method

```bash
cd wt-media-desktop && bash scripts/test.sh           # 起点 198 passed，只增不减
cd wt-media-desktop/src-tauri
rustfmt --edition 2021 src/logging/reader.rs src/storage.rs src/commands/storage.rs src/dto/storage.rs
rustfmt --edition 2021 --check src/logging/paths.rs   # 只查，不改：见边界 2
python3 /tmp/chg058/mutate_t05.py reader|paths|storage|commands   # 变异表，四组各自带阴性对照
cargo test probe_real_machine_readings -- --nocapture # 真机探针（跑完即撤销，见定向检查）
```

## Actual

### 落点表

| 文件 | 性质 | 行数 | sha256(前 12) |
| --- | --- | --- | --- |
| `src-tauri/src/logging/reader.rs` | 新 | 1189 | `0ff1a2560b31` |
| `src-tauri/src/commands/storage.rs` | 新 | 692 | `f121df555ac0` |
| `src-tauri/src/storage.rs` | 新 | 517 | `7ca3d49e9148` |
| `src-tauri/src/dto/storage.rs` | 新 | 273 | `1bbc657a7df6` |
| `src-tauri/src/logging/paths.rs` | 改（+292） | — | `2011f4fd7386` |
| `src-tauri/src/{logging,commands,dto}/mod.rs` | 改（各 1-2 行声明） | — | — |
| `src-tauri/src/main.rs` | 改（3 个命令**追加**在 `invoke_handler!` 末尾） | — | — |

**`storage.rs` 在 T-04 结束时的 198 里不存在**（`git log --stat 7825a75` 只有 `settings.rs` 与 `main.rs`），
所以 T-05 的四个新模块件件都是本 Task 新增，计数差额可以逐件对上（见下）。

### 契约一：一个不可读的树让整次调用失败

`reader::list` 与 `storage::directory_bytes` 都是「**不在** ⇒ 空/0，**读不到** ⇒ `Err`」，
分界画在 `io::ErrorKind` 上而不是 `Path::exists()`（后者对「不存在」与「祖先不可搜索」都返回 false）。
命令层不吞这个 `Err`：`local_storage_usage` 里任何一棵树读不到，整个调用失败并报出那个路径。

**被拒绝的替代方案**：按字段返回错误（`{bytes: null, error: "…"}`）。拒绝的理由是页面**不能**把缺键
渲染成 `0 MB`，但完全可以把 `null` 渲染成 `0 MB`——「缓存占 0 MB，可以清空」出现在一棵从没读到的树上，
正是本里程碑要消灭的那句话。**代价如实登记**：一棵坏树会遮住同一次调用里其它树的读数，
页面的补救是逐项读（命令是分开的，代价是一次点击）。

### 契约二：列表就是尾读的白名单

`local_log_tail` 收的是**文件名**，它从不把这个名字拼到目录上：它先列目录，再在结果里按名字找
（`listed_file`）。所以 `../../../../etc/passwd` 不是「被校验拒绝的字符串」，而是**不在列表里**——
遍历的所有拼法都进不了列表，因为列表里只可能有那一个目录返回的名字。

分母与阳性对照（`a_name_that_is_not_in_the_listing_is_never_read`）：**5 个越界名字**
（`../../../etc/passwd`、`../<树外目录>/secret.txt`、`secret.txt`、`/etc/passwd`、空串）
必须全部 `Err`，**同一个调用**用 `desktop.log` 必须成功——「全都失败」不能通过这条用例。
变异 C1（把名字拼上去）打掉的正是它，报错文本是：

```
"../wt-media-commands-allowlist-outside-29444-612190000/secret.txt" must not be read: it is not in the listing
```

即**那个越界名字在变异下真的被打开了**（`metadata` 成功才可能返回 `Ok`）——这条用例不是空转，
它抓的是一个真能读到树外文件的实现。

作用域是**目录**而不是**文件种类**（`the_listing_scopes_by_directory_and_not_by_kind`）：
同名文件在别的目录里读不到，而读者不认识的 `other`（真机上就是 T-02 之前的 `desktop-20260924-1.log`）
**在**这个目录里就能读——拒绝它等于把用户打开查看器要看的历史藏起来。

### 契约三：档案名必须与 `file-rotate` 的判定逐字一致

crate 决定删哪些文件，读者决定页面显示哪些文件、T-06 可以清哪些。两边答案不一致的后果是
**一个被 crate 当作自己归档的文件被列成 `other` 而悄悄免于保留策略**。所以镜像的是 crate 的**命名规则**：

| 后缀 | `NaiveDateTime::parse_from_str` | crate 的判定（读者照抄） |
| --- | --- | --- |
| `2026-09-24-19` | `NotEnough` | 自己的归档 |
| `2026-09` / `2026-09-24` / `2026` | `TooShort` | 不是 |
| `2026-09-24-19-00` | `TooLong` | 不是 |
| `nonsense` | `Invalid` | 不是 |
| `2026-09-24-19.1` | 整串 `TooLong`；**先按第一个点切开**后 `NotEnough` | 自己的归档（同小时第二次轮转） |

六种形状由 `only_the_stamp_shapes_the_crate_accepts_are_archives` 逐行钉住（其中 `TooShort` 三种
是我第一版**猜错**的：我曾以为「戳的前缀也是戳」，实测不是）。

### 存储只读的两处真实计量

`storage.rs` 的既有 `directory_bytes` 之外只加了 `available_bytes_for`：**已存在的路径就地量，
不存在的路径走到最近的存在祖先**（`statvfs` 对不存在的路径直接 `NotFound`）。两者分工写进模块注释：
`directory_bytes` 对缺失的树回答 0 是因为**里面没有东西**，`available_bytes_for` 往上走是因为
**卷不在那个目录里面**。只走 `NotFound`：祖先上的 `PermissionDenied` 意味着卷在那里而本进程不能看，
父目录不会给出不同答案。

命令层**从列表求和**得到每棵树的字节数，而不是用 `directory_bytes` 再量一次：两次相隔片刻的测量
是页面可以显示为互相矛盾的两个数，而且遍历会进子目录、列表不进——两个集合根本不同。
这条以前只写在注释里，变异 C2 存活把它暴露出来，于是抽成 `tree_usage` 并新增
`a_trees_total_is_the_sum_of_the_files_the_listing_shows`（用一个子目录把两个集合分开）。

### 真机读数（探针，跑完即撤销）

`cargo test probe_real_machine_readings -- --nocapture`，输出存 `/tmp/chg058/t05/probe-real-machine.out`：

```
PROBE data_root=…/src-tauri/.local/data          # 不存在，正是「走祖先」那条路
PROBE cache_root=…/src-tauri/.local/cache        # 不存在 ⇒ 0
PROBE desktop_tree=…/src-tauri/.local/logs       # 开发构建 ⇒ 开发树，不是装机树
PROBE agent_tree=/Users/aqiuye/Library/Logs/WTMedia/Agent
PROBE available_bytes=Ok(91757219840)
PROBE cache_bytes=Ok(0)
PROBE list desktop count=1 bytes=248
PROBE file desktop live bytes=248 path=…/.local/logs/desktop.log
PROBE line level=Some("info") text="2026-09-24T20:47:36 [INFO] desktop.startup: 配置来自开发树 …"
PROBE list agent count=3 bytes=1674
PROBE file agent live bytes=1674 …/agent.log     # 三个 live 名按名排序
PROBE file agent live bytes=0 …/error.log
PROBE file agent live bytes=0 …/task.log
PROBE line level=Some("warn") text="2026-09-24T19:49:48 [WARNING] wt_media_agent.local_api.server: …"
PROBE filter warn agent.log read=9 shown=2 min=Some("warn")
```

四件事因此是**实测**而不是推断：①两棵树各自解析到真目录（Desktop 是开发树、Agent 是装机树）；
②Agent 真机上就写 `agent.log`/`error.log`/`task.log` 三个名字——`Source::Agent::live_names` 是
**镜像**，没有任何编译期检查保证它与 `runtime/logging.py` 一致，这条读数是它的对账；
③两侧的级别拼写（`[INFO]` 与 Python 的 `[WARNING]`）都从真行里解析出来；
④筛选在真数据上按级别工作（读 9 行、留 2 行）。

### 可用空间的独立对账

| 来源 | 读数（字节） |
| --- | --- |
| `storage::available_bytes_for`（本模块） | 91 757 240 320 |
| `python3 -c "os.statvfs(...).f_bavail*f_frsize"`（stdlib，另一实现） | 91 757 240 320 |
| `df -k /Users/aqiuye/Develop` 的 Available × 1024 | 91 757 240 320 |

三者**逐字节相同**。这是单位那条注释的判据：本机 `f_bsize` 是 1 MiB、`f_frsize` 是 4096，
乘错一个字段会报 23 489 853 521 920（256 倍），而三个来源会立刻分开。
`python3 os.statvfs('…/.local/data')` 直接抛 `FileNotFoundError`——顺带证明那个路径确实不存在，
`available_bytes_for` 的往上走是真的在做事。

## 计数（只增不减）

| 侧 | 起点 | 现在 | 差额 |
| --- | --- | --- | --- |
| desktop | 198 passed | **255 passed** | **+57**（0 删除，0 skipped） |

逐件对账：`logging::reader` 26（新模块）、`storage::tests` 13（新模块）、`commands::storage` 10（新模块，
其中 2 条是变异 C2/C9 暴露后才补的）、`dto::storage` 2（新模块）、`logging::paths` 6（10 → 16）。
26+13+10+2+6 = 57，与 `cargo test -- --list` 的分模块计数一致。

非测试构建警告：`cargo check` 计 **27 条**（另有 1 行汇总，`grep -c '^warning'` 读 28）。
T-04 记的是 35（同一条命令、同一计数口径，但**没有在 T-04 的树上复测**，所以这只是趋势不是对照）：
T-05 的消费方把 T-03/T-04 留下的 `never used` 用掉了一部分。剩余的仍是既有模块的未接消费方，
**不用 `allow` 盖掉**。

## 实现变异：50 行，48 灭，2 登记为等价

四组各自先跑**阴性对照**（未变异的字节上同一条命令必须报 `0 failed`），四组全部通过；
每组跑完断言文件逐字节还原：

| 组 | 目标 | 过滤 | 行数 | 结果 | 还原 sha256(前 12) |
| --- | --- | --- | --- | --- | --- |
| reader | `logging/reader.rs` | `logging::reader` | 24 | 23 灭 + 1 等价 | `0ff1a2560b31` |
| paths | `logging/paths.rs` | `logging::paths` | 8 | 8 灭 | `2011f4fd7386` |
| storage | `storage.rs` | `storage::tests` | 7 | 6 灭 + 1 等价 | `7ca3d49e9148` |
| commands | `commands/storage.rs` | `commands::storage` | 10 | 10 灭 | `f121df555ac0` |

原始输出：`/tmp/chg058/t05/mutations-{reader,paths,storage,commands}.out`。

### reader（23 灭）

| # | 变异 | 判据（打掉它的用例，摘） |
| --- | --- | --- |
| R1 | 去掉 `NotEnough` 那一臂 | `only_the_stamp_shapes…`、`an_archive_is_recognised…`、`the_listing_is_live_then…` |
| R3 | 不要求冲突序号能解析成数 | `names_the_rotator_never_writes_are_other` |
| R4 | 归档一律算 `other` | 同 R1 四条 |
| R5 | 不认 `WARNING` | `both_components_level_spellings_are_recognised` |
| R6 | 不认 `CRITICAL` | 同上 |
| R7 | 改成搜索 `[` 定位记录 | `a_level_inside_a_message_is_not_a_record` |
| R8 | 不要求括号前的空格 | 同上 |
| R9 | 不要求括号后的空格 | 同上 |
| R10 | 续行不继承级别 | `a_continuation_line_inherits_the_record_above_it`、`the_filter_keeps_blocks_whole…` |
| R11 | 续行不标记 `continues` | `a_continuation_line_inherits…`、`a_line_before_the_first_record_has_no_level` |
| R12 | 筛选丢掉无法分类的行 | `the_filter_keeps_blocks_whole_and_never_hides_the_unclassified` |
| R13 | 筛选的比较反向 | 同上 |
| R14 | 目录不存在 ⇒ 报错 | `an_absent_directory_lists_as_empty_and_is_not_created` |
| R15 | 目录读不到 ⇒ 空列表 | `an_unreadable_directory_is_an_error_rather_than_empty` |
| R16 | 子目录当文件列出 | `a_subdirectory_is_not_listed` |
| R17 | 归档按最旧在前 | `the_listing_is_live_then_newest_archive_then_the_unknown` |
| R18 | 保留结尾的空片 | 六条尾读用例 |
| R19 | 保留开头的残片 | `a_tail_stopped_by_the_byte_ceiling…`、`one_record_longer_than_the_ceiling…` |
| R20 | 不执行字节上限 | 同上两条 |
| R21 | `truncated` 恒为 false | 同上两条 |
| R22 | 窗口恒当作完整 | 同上两条 |
| R23 | 页面拼写不认识时默认 Info | `the_page_spelling_parses_and_an_unknown_one_does_not` |
| R24 | 来源标签不认识时默认 Desktop | `the_wire_spelling_round_trips_and_an_unknown_one_does_not` |

### paths（8 灭）

| # | 变异 | 判据（摘） |
| --- | --- | --- |
| P1 | 空 `data_dir` 当作配过的值 | `an_unset_agent_data_dir_lands_in_the_agents_installed_tree` 等四条 |
| P2 | `~/` 不展开而是去掉前缀 | `a_configured_agent_data_dir_puts_the_logs_beside_it`、`no_home_refuses_the_arms_that_need_one` |
| P3 | 相对路径当相对路径用 | `a_data_dir_that_cannot_be_resolved_from_here_is_refused`、`the_refusal_does_not_fall_back…` |
| P4 | `~someone` 按本用户家目录展开 | `a_data_dir_that_cannot_be_resolved_from_here_is_refused` |
| P5 | 裸 `~` 被拒 | `a_configured_agent_data_dir_puts_the_logs_beside_it` |
| P6 | 装机树丢掉 `Library/Logs` | `an_unset_agent_data_dir_lands…`、`the_agent_tree_is_not_desktops_tree` |
| P7 | 配了 `data_dir` 时丢掉 `logs/` | `a_configured_agent_data_dir_puts_the_logs_beside_it`、`no_home_refuses…` |
| P8 | 拒绝文案报本机家目录而不是那个值 | `a_data_dir_that_cannot_be_resolved_from_here_is_refused` |

### storage（6 灭）

| # | 变异 | 判据（摘） |
| --- | --- | --- |
| S1 | 读不到的树报 0 | `a_tree_that_cannot_be_read_is_an_error_rather_than_zero`、`a_tree_that_is_a_file…` |
| S2 | 缺失的树报错 | `an_absent_tree_is_zero_and_is_not_created` |
| S3 | 目录按单文件求和（不往下走） | `a_tree_is_the_sum_of_its_files` |
| S4 | 跟随符号链接的目录 | `a_symlinked_directory_is_not_walked` |
| S5 | 缺失路径不从祖先取 | `free_space_for_an_absent_path_comes_from_its_nearest_existing_ancestor` |
| S7 | 乘 `f_bsize` 而不是 `f_frsize` | `free_space_is_measured_for_an_existing_path`（**改强之后**，见下） |

### commands（10 灭）

| # | 变异 | 判据（摘） |
| --- | --- | --- |
| C1 | 名字直接拼到目录上（去掉白名单） | `a_name_that_is_not_in_the_listing_is_never_read` |
| C2 | 树的字节数改用第二次遍历 | `a_trees_total_is_the_sum_of_the_files_the_listing_shows` |
| C3 | 未知级别默认 Info | `an_unknown_level_is_an_error_rather_than_a_default` |
| C4 | 不夹取请求行数 | `the_line_count_is_clamped_to_the_reader_ceiling` |
| C5 | 目录跟随配置的 environment | `the_trees_are_the_builds_not_the_configs_environment` |
| C6 | Agent 树忽略配置的 `data_dir` | `the_agents_tree_comes_from_the_configured_data_dir` |
| C7 | `lines_read` 报 0 | `the_filter_reports_both_counts_and_the_level_it_used` |
| C8 | `lines_shown` 报筛选前的数 | 同上 |
| C9 | Agent 树排在前面 | `the_two_trees_are_this_components_then_the_agents` |
| C10 | `min_level` 回显请求而不是实际用的 | `an_unknown_level_is_an_error_rather_than_a_default` |

### 两条登记为等价（存活是预期读数）

- **R2（分子按最后一个点切）**：`find` 与 `rfind` 对**任何**名字给出同一判定。
  证明：后缀里点 ≥ 2 时，`find` 的「点之后」还含点 ⇒ `parse::<usize>` 必失败，
  `rfind` 的「点之前」还含点 ⇒ 日期格式必不通过；点 ≤ 1 时两个点就是同一个点。
  实测同样存活。**保留 `find` 的理由是它与 crate 逐字一致**（注释已写），不是因为可测。
- **S6（`f_bfree` 而非 `f_bavail`）**：本卷上两者**相等**——
  `os.statvfs` 实测 `f_bfree = f_bavail = 22 702 354`（APFS 不为 root 保留块）。
  所以在**本机**这条变异不可观测；`f_bavail` 的选择在注释里写明是为有保留块的卷（ext4 默认 5%）。
  这条等价是**平台性**的，不是语义性的：换一个文件系统它就变成杀得掉的变异。
  （`df -k` 与 `os.statvfs` 的对账也抓不到它——三者一致正是因为本卷两者相等。）

## 变异表带出的三处改动（不是先写代码再补测试）

1. **C2 存活** ⇒ 抽 `tree_usage` 并加 `a_trees_total_is_the_sum_of_the_files_the_listing_shows`
   （一个子目录把「遍历」与「列表」两个集合分开，让那条只写在注释里的不变量可断言）。
2. **S7 存活** ⇒ `free_space_is_measured_for_an_existing_path` 原先的上界是「小于 1 EiB」，
   而本机错乘 `f_bsize` 得到 23.8 TB——**过得去**。改成「不超过卷的总容量」
   （`f_blocks × f_frsize`，同一次 `statvfs` 的另两个字段）：S7 随即被它打掉。
   这条正是本模块注释里点名警告的那个陷阱，之前**没有任何用例钉住它**。
3. **一次可疑的「灭」**⇒ 定位为**用例自身的竞态**，已修：
   `S6` 首轮被判「灭」，但同一条变异**聚焦重跑 20 次全过**（未变异字节同样 20 次全过），
   说明那次失败是间歇的，不是变异造成的。根因是用例比较**同一卷的两次读数**（相隔片刻，
   中间任何写入都会移动它；本轮对账里同一路径在几分钟内就动了 20 KiB）。
   改法不是放宽容差而是**重试**：`readings_agree` 最多读 4 次，其中一次相等即通过——
   「同一卷」的强断言保留，而相邻的卷在**任何一次**尝试里都不会相等。
   同时新增 **C9** 用例与 **R25**（见下）把两处此前无主的决定钉住。

### R25（表跑完后补的一行，聚焦跑）

`local_log_files`/`local_log_times` 的排序里，`Live` 组此前用空键 ⇒ 组内顺序由 `read_dir` 决定。
Agent 有**三个** live 文件，页面上它们的顺序会是文件系统的选择（换机器、删了重写都可能变）。
改成按名字排序，并加 `the_agents_three_live_files_are_listed_by_name`。
聚焦变异（`left_group == 1` → `left_group == 0 || left_group == 1`，即 live 组也倒序）：

```
test logging::reader::tests::the_agents_three_live_files_are_listed_by_name ... FAILED
test logging::reader::tests::the_listing_is_live_then_newest_archive_then_the_unknown ... ok
test result: FAILED. 25 passed; 1 failed
```

只有新用例红、归档顺序用例仍绿——这一行钉的正是「live 组按名」这一条规则。改完 `reader` 26/26 绿。

## 边界登记（不静默吸收）

1. **三个命令的**命令体（收`State`）没有单测，这是 `commands::agent` 的既有先例：可断言的部分抽成
   `resolve`/`listed_file`/`tail_of`/`file_fact`/`tree_usage`，命令体只剩把结果搬进 DTO 的几行。
   真机读数由上面的探针覆盖（探针**跑完即撤销**，不是常驻用例）。
2. **`logging/paths.rs` 只做了半格式化**：本文件是 CHG-057 的产物，`rustfmt --check` 仍报 3 处
   （第 258/516/605 行附近，全是 CHG-057 已提交的字节）。本仓不是 rustfmt-clean，
   只格式化**本 CHG 自己的**新增片段，别人的历史行不动。
3. **CHG 行里的「读尾部约 500 行」之上还有一层请求上限 5000**（`MAX_TAIL_LINES`）：
   读者的字节上限（4 MiB）已经界定内存，但一次调用几 MB 的 JSON 不该让页面顺手要出来。
4. **单条记录长于 4 MiB ⇒ 空视图 + `truncated=true`**。这是 T-05 有意保留的形态（记录上限 1 MiB，
   四个满记录仍在上限内），页面必须据此说「这是窗口」而不是「文件是空的」。
5. **无效 UTF-8 变成 U+FFFD**，不是拒绝显示该文件（字节上限本身就会切断多字节字符）。
6. **Agent 的非 frozen 开发分支**仍不镜像：Desktop 读的是 Agent 装机树或它配置里的 `data_dir`；
   一个自报 development 的 Agent 会写自己的 `.local/logs`，Desktop 看不到（T-03 的开口，此处仍开着）。
7. **Q-08（两棵树）在本 Task 的答案**：Desktop 树来自 `app_paths`（本构建的环境），
   Agent 树来自 `logging::paths::agent_directory`（`HOME` + 配置的 `agent.data_dir`），
   两者都不缓存、每次调用重算；不可解时命令失败而不是猜一个目录。
