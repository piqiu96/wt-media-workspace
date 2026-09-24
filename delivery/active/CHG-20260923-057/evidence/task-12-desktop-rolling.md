# 证据 — T-12 Desktop `rolling` writer（四条界 + 预算，`Clock` 注入）

范围：裁定六的四条界在 Desktop 侧的落点——单文件 **20MB**、保留 **14 天**、三文件共享总量
Desktop **100MB**（Q-01）、**单条超限截断并标 `truncate=true original_size=<n>`**；
外加计划本条自己要求的「日期翻档 / 20MB 翻档 / 按天删除 / 按总量删除 / 当前文件永不被删」
五条与「`create_new` 式命名防多实例」。

提交：`wt-media-desktop`（`src/logging/rolling.rs` 新增、`logging/mod.rs` 加一行 `pub mod rolling;`）。

---

## 1. 交付形态：四条纯规则 + 一处薄 IO

| 项 | 形态 |
|---|---|
| `date_of(SystemTime) -> Date` | **纯**：时刻进去、UTC 日期出来，不读任何环境 |
| `fit(line, max) -> Fitted{line, original_size}` | **纯**：单条截断 + 标记 |
| `rotation(open_date, today, current, next, max) -> {Keep, Roll}` | **纯**：这条记录该进哪个文件 |
| `expired(candidates, today, limits, keep, rolled_by_us) -> Vec<String>` | **纯**：删哪些文件（名字出、IO 不碰） |
| `Writer` | 唯一的 IO：`create_new` 抢名字、写、翻档、prune。**永不 panic**，全是 `Err` 或报告后继续 |

`Clock` 是注入的（`trait Clock { fn now(&self) -> SystemTime }`，真实实现 `SystemClock`）。
理由是裁定六的第二、三条界都是**时间**界：「第 15 天会怎样」必须能在不等到第 15 天的前提下回答。

## 2. 命名与多实例：为什么每个文件都带日期

`desktop-YYYYMMDD-N.log`，UTC。**包括正在写的那个**——这与 Agent 侧不同（那里是稳定名
`agent.log` + 带日期的历史名）。Desktop 不能那么做：两个实例可能同时开着，一个稳定名会让两者
写同一个文件、再由其中任意一个把它改走。故每个 writer 用 `create_new` **抢**自己的名字，
第二个实例落到 `-2` 而不是第一个实例的文件上。**索引进名字的全部理由就是这次抢占。**

`create_new` 是原子的，所以「两个实例同一秒启动」有一个确定的结局：一个拿到 `-1`，另一个被
`AlreadyExists` 推到 `-2`。有专门用例（`a_second_writer_takes_the_next_index_rather_than_the_same_file`）
在同一进程里真的起两个 writer 来钉这条。

**没有文件被提前创建**：`Writer::open` 不建文件，第一条记录才建。理由与 T-11 同：一个空文件的
意思是「Desktop 启动了但什么都没记」，一目录这样的文件比空目录更糟。代价如实登记——目录不可用
要到第一条记录才暴露（T-11 的 `prepare()` 在启动时已经把可写性问过一次，所以不算新盲区）。

## 3. 预算的两条口径（与 Agent 侧逐条对齐）

1. **日期界**：`cutoff = today - retention_days`，`date <= cutoff` 的删。14 天窗口 = 今天 + 之前 13 天；
   恰好 14 天前的那天是第 15 天，删。与 Agent 侧同一口径。
2. **总量界**：把**当前打开的文件也算进总量**（它在磁盘上），然后**从最老的开始删到装得下为止**。
3. **当前文件永不参与**（裁定六）：`keep` 先被摘出候选，之后无论日期界还是总量界都碰不到它。
   两向断言：同一个文件「开着」时活、「关了」时被日期界删掉——否则「没删」可能只是规则没生效。
4. **今天且不是本 writer 翻出来的文件不删**（本条是本 Task 自己加的，理由见下）：按总量删时，
   一个今天的 `-N` 文件可能是**另一个实例正在写的文件**。删了它，那个实例的记录会写进一个
   已经被 unlink 的 inode——不崩，但那些记录没了。故这道口子按「宁可迟一天到界」的方向设。

### 3.1 如实登记：这套命名下仍然存在的一处残余风险

**跨过午夜的第二个实例**。它在昨天启动、现在还在跑，它的活文件日期是**昨天**，而昨天的文件
无论谁写的都是历史（今天不再有任何 writer 应当写它）。故按天删除会删掉它。
两实例 + 跨午夜 + 到了界才发生，且 writer 无法区分「对端的活文件」与「历史」——**登记为未覆盖，
不假装解决了**。同一天内的对端活文件已被上一条挡住。

另一处方向相反的口子：**今天早些时候另一次运行翻出来的文件**，今天不会按总量回收（对本次运行
来说它是「不是本 writer 翻的」），要等跨天。这是安全方向的代价，同样登记。

## 4. 变异表：控制行先绿，25 个变异逐个红

探针 `/tmp/t12-mutation-probe.py`：逐次改**真实模块**的一处，跑整套 `logging::rolling` 用例，
记下谁死了。原文本在 `finally` 里还原，并用 sha256 **核对**（不是假定）——
最后一次跑报 `restored=True (c3301b6334b3)`，与提交文本的 sha256 逐字一致。

```
mutation | 00 | 01 | 02 | … | 37
0 控制：未变异                    | green ×38
M01 date 用 / 而不是 div_euclid   | RED → dates_before_the_epoch_are_converted_rather_than_wrapped
M02 去掉百年规则（1900 变闰年）    | RED → leap_years_follow_the_century_rule
M03 纪元位移差一天                | RED → 13 条（含全部真实落盘用例）
M04 不把月份位移还原              | RED → 4 条
M05 时间戳不补零                  | RED → 9 条（含 a_file_name_states_its_date_and_index）
M06 索引 0 可解析                 | RED → a_name_we_did_not_write_is_not_ours
M07 去掉 8 位长度检查             | RED → 同上
M08 带符号的索引可解析            | RED → 同上
M09 超长单条整条写入              | RED → 4 条
M10 截断不标记                    | RED → 3 条
M11 original_size 报截断后的长度  | RED → 3 条
M12 不预留换行那一个字节          | RED → 3 条
M13 截断可以切半个字符            | RED → truncation_never_leaves_half_a_character
M14 日期变了不翻档                | RED → 2 条
M15 恰好填满也翻档                | RED → 2 条
M16 超长单条自己开一个文件        | RED → a_record_too_large_for_an_empty_file_is_still_written
M17 窗口边界那天存活（<= 改 <）    | RED → the_window_is_today_plus_the_days_before_it
M18 打开的文件可被删              | RED → the_open_file_is_never_a_candidate
M19 总量不计打开的文件            | RED → 6 条
M20 总量界把剩下的全删            | RED → 6 条
M21 今天的对端文件可删            | RED → todays_file_is_spared_unless_this_writer_rolled_it
M22 抢名字不排他（create）        | RED → 3 条（含双 writer 那条）
M23 翻档不记录翻过谁              | RED → a_file_this_writer_rolled_today_is_reclaimable_under_pressure
M24 抢之前不建目录                | RED → 10 条
M25 打开文件的大小不是真实大小    | RED → 2 条
```

**8 条界各有用例守着，且没有一条用例永远绿。** 覆盖面按「裁定六的四条 + 计划的五条 + 多实例」逐条枚举：

| 界/规则 | 守它的用例 | 变异能红它吗 |
|---|---|---|
| 日期翻档 | `the_day_changing_rolls_even_a_file_with_room_left`、`the_day_changing_starts_a_new_file_and_keeps_the_old_one` | M03/M05/M14 |
| 20MB 翻档 | `a_record_that_would_pass_the_cap_rolls`、`a_full_file_rolls_…`、`a_record_that_exactly_fills_the_file_is_kept` | M15/M25 |
| **单条超限截断 + 标记** | `an_oversized_record_is_truncated_and_says_how_long_it_was`、`…is_marked_in_the_file_it_lands_in`、`a_cap_too_small_for_the_marker_still_marks_the_record`、`truncation_never_leaves_half_a_character` | M09/M10/M11/M12/M13 |
| 按天删除 | `the_window_is_today_plus_the_days_before_it` | M17 |
| 按总量删除 | `files_are_deleted_oldest_first_until_the_total_fits`、`the_total_rule_deletes_no_more_than_it_has_to` | M19/M20 |
| **当前文件永不被删** | `the_open_file_is_never_a_candidate`、`a_record_written_after_a_prune_is_still_there` | M18/M19 |
| 多实例不写同一文件 | `a_second_writer_takes_the_next_index_rather_than_the_same_file` | M22 |
| 预算是活的（能回收自己翻出来的） | `a_file_this_writer_rolled_today_is_reclaimable_under_pressure` | M23 |

### 4.1 探针查出的两个问题（都改了，不是记下来了事）

- **M13 第一次是 NO-COMPILE，不算「规则被守住」**。第一版变异写的是
  `Err(_) => String::from_utf8_lossy(head).into_owned().as_str()`，临时值借不到 `&str`，
  **整个 crate 编不过**——探针把它记成 `NO-COMPILE` 而不是 red，这是对的：编译失败的变异
  证明不了任何事。改成可编译的等价变异（先 `into_owned()` 绑到局部变量再取 `as_str()`）后转红。
  这条要单独说，是因为「红」和「编不过」在只看用例列表时长得一样。
- **M23 起初全绿 → 补用例**。「翻档时记住自己翻过谁」这条规则**没有任何用例守着**：
  `rolled_by_us` 只在「总量界要删一个今天的文件」时才起作用，而我原有的用例要么总量够宽
  （根本不删）、要么删的是昨天的（不看这个集合）。补
  `a_file_this_writer_rolled_today_is_reclaimable_under_pressure`：20 字节单文件 + 30 字节总量，
  连写 5 条，算出第 5 条写入时的翻档会删掉 `-1` 并停在 `-2`；断言 `-1` 没了、`-2` 还在、
  打开的 `-3` 里有最新记录。M23 随即转红。

## 5. 逐字边界与未覆盖项

- **零改动**：`paths.rs`、`sidecar/drain.rs`、`http/local_agent.rs`、`config.rs` 一个字符没动
  （本 Task 只新增一个模块 + `logging/mod.rs` 一行）。
- **不改 `Cargo.toml`**：不需要新依赖。日期换算自己写（Hinnant 的 `civil_from_days`/`days_from_civil`），
  因为这是纯整数运算、可穷举验证，而引 `chrono`/`time` 会为「一个日期」增加一棵依赖树。
- **未覆盖（逐条登记，不静默跳过）**：
  - `SystemClock::now`：一行 `SystemTime::now()`，按构造无从单测；由 T-15 的真实启动覆盖。
  - `report()` 的**输出内容**：路径本身在用例里真的走到了（`a_writer_that_cannot_list_its_directory_still_writes`
    触发了 list 失败），但没断言 stderr 文本；可见性部分由 T-15 真实启动覆盖。
  - `MAX_INDEX_PER_DAY` 这道防死循环的守卫：要 10000 个文件才能走到，**没有用例**。
    它是防线不是界（裁定没要求），登记为未覆盖。
  - Windows：文件语义（追加写、不 rename 翻档）是可移植的，但**未取证**，与 T-11 同一登记。
  - 跨午夜的第二个实例：见 §3.1。
- **与 Agent 侧的一致性**：截断标记 ` truncate=true original_size=<n>` 逐字相同，单条上限即单文件
  上限也相同；`original_size` 同样是**不含末尾换行**的原始字节数。差异只在命名（见 §2）与
  「今天的对端文件」这一口子。

## 6. 测试与警告读数

| 指标 | 改前（T-11 后） | 改后 |
|---|---|---|
| `cargo test --workspace` | **78 passed; 0 failed** | **116 passed; 0 failed**（+38） |
| `cargo build` 条目级警告 | 12 | **43** |
| `cargo clippy --workspace --all-targets` 条目级 | 18 | **48** |

**计数法这次写明，免得再漂**：先 `touch src/main.rs` 让警告真的被重新发出，再
`cargo build 2>&1 | grep -cE '^warning: [a-z]'`（clippy 同理，命令是
`cargo clippy --workspace --all-targets`）。T-11 的 12/18 在这条口径下可复现（4 条既有存根 + 8 条
`paths` 的 `dead_code`），故两轮读数可比。

**+31 / +30 全部是同一件事**：`rolling.rs` 的条目在非测试构建里还没有调用方——`dead_code`，
因为调用方（`main` 的接线）按计划在 **T-15**。按文件拆开核对过：build 条目
`rolling.rs` **31** 条、`paths.rs` 8 条、既有存根 4 条（`filesystem`/`secure_store`/`system`/`updater`），
合计 43，**没有一条来自别的文件**。

**另有两处是 clippy 的真意见，已改而不是带上**（不是 `dead_code`，故不在上面那 31 条里）：
①`impl Clock + Send + Sync` 里 `Send + Sync` 是 `Clock` 的超 trait 已经保证的——
改成 `impl Clock + 'static`；②测试里 `fitted.line.len() + 1 <= 200` 这类写法，改成先绑一个
`with_newline` 变量，保住「算上换行」这个读法。两处都是自己新写的代码，改完 clippy 条目数
由 51 落到 48。

**T-15 的待验期望据此更新**：接线完成后 `cargo build` 条目级警告应从 **43** 回到 **4**、
clippy 从 **48** 回到 **10**。不降即说明模块没被真正接上——那比缺测试更严重。
