# Evidence: T-02 日志命名与轮转（两侧）+ 四处活基线回写

- CHG: `CHG-20260923-058`
- Task: `T-02`
- Date: 2026-09-24
- Type: command | manual
- Status: PASS（两侧代码与测试），**基线回写见本文件末节**
- Commits:
  - desktop `b344511` 第一步——轮转交给 `file-rotate`
  - desktop `a4abcd6` 第二步——记录戳改本机时区
  - desktop `f95cb28` 第三步——单实例守卫，且它必须跑在日志落盘之前
  - agent `1160f3c` 日志按小时切到 `agent.log.<时间戳>`，只按天保留

## Purpose

把裁定 1/2/3（用户 2026-09-24）落到两侧运行时代码：**稳定默认文件名 + 按小时切割**、
**不控总量、只按天保留**、**加单实例守卫**（裁定 4），并保留既有的单条截断与脱敏。

## Method

```bash
# Desktop
cd ../wt-media-desktop && cargo test --manifest-path src-tauri/Cargo.toml
# Agent
cd ../wt-media-agent && bash scripts/test.sh
# 实现变异：逐条改一处实现，看用例是否打掉自己
python3 /tmp/mutate-logs.py
# 真机探针（真实进程，不只看单测）
#   形态 / 轮转 / 年龄删除 / 脱敏阳性对照，见下
```

## Actual

### 形态（两侧一致）

| | 活文件 | 归档 | 轮转 | 保留 |
|---|---|---|---|---|
| Desktop | `desktop.log` | `desktop.log.<YYYY-MM-DD-HH>` | `file-rotate` `ContentLimit::Time(Hourly)` | `FileLimit::Age(14d)`（crate 承担） |
| Agent | `agent.log` | `agent.log.<YYYY-MM-DD-HH>` | 标准库 `TimedRotatingFileHandler(when="H")` | `LogRetention.prune`（自有，按天） |

`task.log`/`error.log` 同 Agent 侧规则。**两侧出货值一致**：`retention_days = 14`、
`max_record_bytes = 1048576`（Desktop `Limits::SHIPPED`；Agent `DEFAULT_LOG_MAX_RECORD_BYTES`）。
Agent 侧「按天删除由自有代码承担」是**有意的不对称**（标准库只提供按个数删除），已写进
`runtime/logging.py` 模块注释与基线。

### 测试计数（只增不减；差额逐条登记）

| 仓 | 基线 | 现在 | 差额 |
|---|---|---|---|
| agent | 379 OK | **377 OK** | −2，见下 |
| desktop | 175 passed | **160 passed** | −15，见下 |

**Agent −2**：`tests/test_runtime_config.py` 删去 `test_a_total_below_the_single_file_cap_is_rejected`
与 `test_equal_bounds_are_accepted` —— 两条都在断言 `max_bytes` 与 `total_bytes` 的**互相约束**，
而这两个键已被裁定 3 删除，没有比较对象。`tests/test_log_rollover.py` 10 删 10 增（净 0）。

**Desktop −15**：34 删 19 增。这是**裁定要求的删除**（「这些正是被 crate 取代的轮子」），
但逐条必须落地，故按类目全列：

- **日期与命名的自写算术（8，全部被 crate/`chrono` 取代）**：
  `a_date_moves_back_by_a_whole_number_of_days`、`a_file_name_states_its_date_and_index`、
  `dates_before_the_epoch_are_converted_rather_than_wrapped`、`every_day_of_a_leap_year_round_trips`、
  `leap_years_follow_the_century_rule`、`the_epoch_is_1970_01_01`、`the_stamp_is_zero_padded`、
  `the_stamp_is_the_day_and_the_time_utc`
  —— 对应 `file_name`/`parse_file_name` 已删；戳的格式由
  `the_stamp_is_the_local_day_and_time_with_no_zone_mark` 与 `the_stamp_is_local_at_the_edges_of_the_day` 接管。
- **单文件上限与总量预算（8，裁定 3 删除）**：
  `a_full_file_rolls_and_the_next_record_starts_a_new_one`、
  `a_file_this_writer_rolled_today_is_reclaimable_under_pressure`、
  `a_record_that_exactly_fills_the_file_is_kept`、`a_record_that_fits_stays_in_the_open_file`、
  `a_record_that_would_pass_the_cap_rolls`、`files_are_deleted_oldest_first_until_the_total_fits`、
  `the_total_rule_deletes_no_more_than_it_has_to`、`the_window_is_today_plus_the_days_before_it`
  —— 窗口定义由 `the_window_is_the_configured_one` 接管。
- **换机制后一对一替换（9）**：`a_directory_that_cannot_be_created_..._panic`→`an_unusable_directory_..._panic`；
  `a_name_we_did_not_write_is_not_ours`→`a_file_that_is_not_an_archive_is_left_alone`；
  `a_record_too_large_for_an_empty_file_is_still_written` 与
  `an_oversized_record_is_marked_in_the_file_it_lands_in`→`a_record_over_the_cap_is_marked_in_the_file_it_lands_in`；
  `the_day_changing_*`（2 条）→`a_record_in_a_new_hour_rotates_the_file_the_previous_run_left`；
  `the_first_record_lands_in_todays_first_file`→`..._stable_live_file`；
  `opening_the_writer_prunes_what_is_expired`→`history_past_the_window_is_deleted_and_history_inside_it_is_kept`；
  `the_listing_holds_our_files_and_nothing_else`→`archives()` 助手 + `a_file_that_is_not_an_archive_is_left_alone`。
- **场景消失（4）**：`a_second_writer_takes_the_next_index_rather_than_the_same_file`、
  `todays_file_is_spared_unless_this_writer_rolled_it`、`yesterdays_file_is_history_whoever_wrote_it`
  —— 三条都在测 `claim()` 的 `create_new` 抢名与所有权；该机制已删，第二写入者由单实例守卫从根上消掉。
  `the_open_file_is_never_a_candidate` —— 现在**结构性成立**（crate 只把 `{base}.{stamp}` 认作归档，
  活文件是 `{base}`），由 `history_past_the_window_...` 的
  「the file being written is never history」间接钉住。
- **语义**改写（4，**不是覆盖丢失，是行为变更**，见下「登记」）：`nothing_is_created_before_the_first_record`
  → `the_live_file_exists_as_soon_as_the_writer_does`；`a_file_that_cannot_be_written_does_not_turn_into_an_io_error`
  与 `an_unusable_directory_still_gives_a_subscriber` → `an_unusable_directory_is_an_error_rather_than_a_panic`、
  `a_live_path_that_is_a_directory_is_an_error_rather_than_a_silent_sink`、
  `a_directory_that_cannot_be_written_is_refused_and_the_launch_still_has_a_subscriber`。
- 余 1 条 `a_record_written_after_a_prune_is_still_there`：由
  `a_file_that_is_not_an_archive_is_left_alone` 与 `history_past_the_window_...` 覆盖（两者都在 prune
  之后写入并断言文件仍在）。

合计 8+8+9+4+4+1 = 34 ✓，与编译器读数 `175 → 160` 相符。

### 实现变异（每个界至少一次，且能打掉自己的用例）

Agent 侧 10 项，**全部被灭**：

| 变异 | 被谁灭 |
|---|---|
| 去掉 `self.suffix = ARCHIVE_FORMAT`（退回标准库下划线形） | `..._carry_the_configured_numbers` |
| `backupCount=0` → `3`（把按个数删除装回来） | 同上 |
| `utc=False` → `True` | 同上 |
| `doRollover` 里去掉 `retention.prune()` | `test_a_roll_ages_out_the_history_without_being_asked` |
| `stamp < cutoff` → `<=` | `test_an_archive_in_the_cutoff_hour_itself_is_kept` |
| `path.unlink()` 改成空操作 | 8 条 |
| `_fit` 不再截断 | 2 条 |
| `register()` 不记录族名 | 8 条 |
| `rolled()` 去掉 `_live` 保护 | `test_an_open_file_whose_name_looks_like_history_is_still_protected` |
| 去掉 `computeRollover` 对齐 | `test_the_roll_lands_on_the_hour_boundary_not_an_hour_after_startup` |

**其中一项先前是空转的**：`_live` 保护那一项**第一轮变异没被任何用例发现**。原因是
`test_an_open_file_whose_name_looks_like_history_is_still_protected` 用了 `retention_days=0` 与
同时刻的戳，活文件是靠**年龄**（严格 `<` 未命中）留下来的，`_live` 那一段根本没被执行——
即该用例当时**为错误的理由通过**。已改成把活文件戳到窗口**之外**（cutoff−24h），
并保留同龄未注册的对照（cutoff−48h 必须被删），变异随即被灭。

### 真机探针（真实进程，非单测）

1. **形态与轮转**（Agent）：真进程启动后目录为 `agent.log`（活）+ `agent.log.2026-09-24-21`（归档）+
   `task.log`/`error.log`；`suffix=%Y-%m-%d-%H`、`backupCount=0`、`utc=False`。
   归档名与其中记录的戳**同为 21**。
2. **年龄删除**（Agent，裁定「超过 14 天自动删除」）：种入 15 天前 / 13 天前 / 2 天前三个归档，
   **真启动**一次后 15 天前的被删、13 天前与 2 天前的留下，活文件与两个兄弟文件建出。
   同龄对照存在，故删除是年龄驱动而非无差别删除。
3. **Desktop 侧**：`file-rotate` 0.8.0 探针（`/tmp/cratecheck/probe`，激活时先行取得）给出
   20 天删 / 15 天删 / 2 天留、活文件 `desktop.log` 完好；本 CHG 的
   `history_past_the_window_is_deleted_and_history_inside_it_is_kept` 把同一读数固化为用例。
4. **脱敏**（阳性对照 + 分母）：一行真凭据先确认模式**抓得住**（`/tmp/redact-control.txt` 5 行命中 5）；
   同一模式扫本次真进程写的 3 个日志文件得 3 处命中，**三处都是键名 + `***`**（我们自己的探针文本里
   写了字面 `token=`），凭据值在磁盘上**零出现**。故这里不是「0 命中」，而是「命中皆为掩码后的键名」。

### 实测发现（读文档推不出来的三条）

1. **标准库 `when="H"` 自选 suffix 是 `%Y-%m-%d_%H`（下划线）**，与裁定要求的分隔符不符；
   `__init__` 不接受 `suffix` 参数，只能在 `super().__init__` 之后显式设回 `ARCHIVE_FORMAT`。
   第一版实现产出 `agent.log.2026-09-24_20`，被 wiring 用例当场读出。
2. **`computeRollover` 对 `when="H"` 不做对齐**：标准库只在 `MIDNIGHT` 与周模式有对齐分支，
   小时档返回 `currentTime + interval`。于是 20:58 起的进程在 21:58 轮转，而 `doRollover` 用
   `rolloverAt - interval` 命名 ⇒ 归档名说 20、内容却写到 21:58，**名字与内容差近一小时**，
   也与 Desktop 的整点轮转不对应。已覆写为对齐到下一个本地整点。
   这条由**真机探针读 `rolloverAt`** 发现（读到 `21:58`），不是读文档推断。
3. **`file-rotate` 的 `too_old` 比的是**归档名里的时间戳字符串**（`suffix.timestamp < old_timestamp`，
   `old_timestamp = (Local::now() - age).format(...)`），**不是 mtime**；且两侧都是严格 `<`。
   Agent 侧据此对齐，边界行为一致（`test_an_archive_in_the_cutoff_hour_itself_is_kept` 的两侧注释引用）。

## 登记的边界与行为变更（不静默吸收）

1. **同名归档已存在时的行为两侧不同**（Agent 侧已在模块注释中登记）：
   标准库 `doRollover` **早退跳过**该次轮转（「Already rolled over」），且早退发生在推进
   `rolloverAt` **之前** ⇒ 该进程此后每次写都会再次跳过，**活文件不再轮转**；
   Desktop 的 crate 则是级联 `.1`，且它的年龄规则只读时间戳部分，级联文件仍会被删。
   触发标准库这一支需要两个写入者共用一个活文件 ⇒ 两侧现已分别用单实例守卫（Desktop）与
   端口单绑定（Agent）挡住。**未修**，理由是：给归档另起一个名字就等于 crate 的级联，
   而那个名字不匹配 Agent 侧四字段的保留模式，文件反而会活过窗口。
2. **Desktop 活文件由「首次写入才创建」变为「writer 一存在就创建」**（
   `nothing_is_created_before_the_first_record` → `the_live_file_exists_as_soon_as_the_writer_does`）。
   原因：crate 的 `FileRotate::new` 会建文件。两侧现在一致（Agent 侧 `delay=False` 同样是立即打开，
   且旧注释写明「Agent 不能启动后看起来像没配日志」）。**行为变更，已登记**。
3. **Desktop 对不可用日志目录的语义由「静默吸收」变为「明确拒绝」**：
   旧实现 `Writer::open` 在路径是个文件时**成功**、写入也不报错（怕在 sink 已打印的原因上再叠一条），
   新实现返回 `Err(RollingError)`；用例名从「still gives a subscriber」变成
   「is **refused** and the launch **still has** a subscriber」——启动仍拿到 subscriber这一点不变，
   但不可用目录**不再被悄悄吞掉**。这与本 CHG 成功事实 #6「读取失败必须是错误而非 0 MB」同向。
4. **`Writer::list` 已删**（原为私有、生产路径零调用）。T-04 的「列出日志文件」命令是**新建**，
   不是「把已有的接出来」——避免 T-04 误判为已有能力。
5. **`Clock` 注入丢失**（§7 Q-05，激活时已登记）：crate 的 `mock_time` 是内部 `#[cfg(test)]`，
   下游拿不到。CHG-057 T-12 的 25 个变异原本靠注入时钟；本 CHG 改用 `FileRotate::rotate()`
   （`pub`）与 `filetime` 改 mtime 构造边界。**覆盖降级如实登记**，不假装等价。
6. **开发态遗留的旧格式文件对新轮转器不可见**：`desktop-20260924-1.log`（旧命名）不匹配
   新归档模式，故升级后不会被清理。本轮未处理（开发机上的残留，非出货路径）。
7. **未测**：第二个实例被召到前台这一动作本身在无头环境下测不了；本次以「实例 2 以 `exit 0` 退出」
   证明 `notify_singleton` 成功（即实例 1 的回调已派发），**没有截到窗口被抬起的画面**。
   plugin 自身「同刻两次启动可能都自认单例」的竞态不在范围内。

## 探针方法与一处方法论更正

单实例守卫的探针 `/tmp/si-probe.sh` 先是**空转**的：macOS 没有 `timeout`，命令以 `exit=127`
结束、实例 2 根本没起来，而脚本照样打印「verdict: byte-identical」。改成 `kill -0` 轮询后才拿到
真读数：变异版（把 sink 安装挪回 `Builder::run` 之前）复现出 `desktop.log.2026-09-24-19` 与一个新
inode 的 `desktop.log`（只装着那个已死进程的一行）；修复版两次运行的读数逐字节相同、inode 不变、
不产生归档。**该探针已被证明能失败**。

同样地，本文件里的两条 Agent 探针一度处于**真实运行不会到达的状态**（把 `rolloverAt` 推到
记录写入**之前**），读数里出现「归档名 19、内容戳 20:58」。这不是缺陷而是探针自己造的非法态，
已在正文中更正为：驱动 `doRollover()`（`pub`）并让触发器留在标准库给的**真实**下一个整点。

## workspace 收口门禁：同集合阳性对照（以及一次**无效对照**）

判据是 `git archive HEAD` 的**同集合阳性对照**。第一次按字面做——`git archive HEAD | tar -x -C /tmp/ws-head`
——得出「HEAD 2 红 / 工作树 4 红」，看上去像是我新添了 2 条红。**这个对照是无效的**，读数不能用：
`tests/test_verify_m2_acceptance.py:28` 与 `tests/test_verify_m0_config.py` 把兄弟仓解析为
**仓库根的父目录**下的 `<name>`，在 `/tmp` 里就成了 `/private/tmp/wt-media-cloud`——不存在，于是这两条
**被 skip**（`skipped 'runtime sibling repositories are not present in this checkout'`），
**红项被 skip 顶掉**，数量从 4 变成 2。也就是说：只把 HEAD 的内容搬到一个父目录不对的地方，
路径敏感的用例会静默降级，同集合对照就被污染成「数量不等」。

正确做法是**把 HEAD 的内容放在真实路径上**：把本次改动的 7 个跟踪文件与 1 个未跟踪证据文件备份
（`git diff HEAD` 出 146 行补丁 + 单独 copy 证据文件），`git checkout HEAD --` 这几个文件，
就地跑**同一个** `unittest discover -s tests`，再 `git apply` 补丁还原。

读数（两侧都是就地、同一条命令）：

| 树 | 红项集合 | 计数 |
| --- | --- | --- |
| HEAD（就地） | `test_contract_map_matches_m1_cloud_agent_compatibility`、`test_contract_map_provider_paths_exist_in_full_workspace`、`test_current_product_master_and_governance_are_aligned`、`test_static_cross_repo_contract_and_security_matrix` | 4 |
| 工作树（含 T-02 全部改动） | **同上四条，逐名相同** | 4 |

四条都不是本次改动引入的：它们分别读 `config/contract-map.yaml` 的 `contract_revision`
与 `wt-media-cloud/internal/modules/cloudagent/compatibility.go` 等云侧文件，与 T-02 触及的
日志代码、四处活基线无关——但**这个「无关」不是判据，判据是上面两张表**。
还原后用 `git status --porcelain` 与交换前的快照做 `diff`，结果 **IDENTICAL**（六条无关的脏文件全程未动）。
