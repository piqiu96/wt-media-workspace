# 证据 — T-07 保留与轮转（Agent）

范围：裁定六（单文件 ≤ 20MB、保留 ≤ 14 天、总容量受限、单条超限必须截断并标
`truncate=true original_size=<原字节数>`），裁定十一·轮转真实生效／历史清理有效／超长日志截断，
裁定十三·4「日志不会无限增长」。

提交：`wt-media-agent` `f07d9e8`；该提交单独 `git worktree` checkout 跑 `scripts/test.sh` →
**320 tests OK, exit=0**（提交边界真实）。

---

## 1. 六个界各一个变异：先把「谁在撑这条断言」量出来

新类的「先红」只是 `ImportError`（`BoundedFileHandler` 还不存在），**它证明不了任何行为**。
所以改量变异：把每个界在实现里逐个关掉，看哪些用例倒。

探针 `/tmp/t07-mutation-probe.py`（先跑未变异对照行，不绿就说明探针本身无效）：

```
mutation             verdict  tests that noticed
(none, control)      OK       (nothing -- the probe is invalid)
date roll            RED      test_a_day_change_rolls_the_file
size roll            RED      test_a_file_that_reaches_the_single_file_cap_rolls
                              test_a_roll_ages_out_the_history_without_being_asked
                              test_the_total_does_not_grow_with_the_volume_written
                              test_two_rolls_on_one_day_get_different_names
record truncation    RED      test_one_oversized_record_is_truncated_and_marked
                              test_the_marker_records_bytes_not_characters
age prune            RED      test_a_roll_ages_out_the_history_without_being_asked
                              test_an_open_file_whose_name_looks_like_history_is_still_protected
                              test_configure_logging_deletes_stale_history_before_the_first_write
                              test_rolled_files_outside_the_retention_window_are_deleted
total prune          RED      test_the_budget_is_shared_by_the_three_files
                              test_the_oldest_rolled_files_are_deleted_when_the_budget_is_exceeded
                              test_the_total_does_not_grow_with_the_volume_written
live-file guard      RED      test_an_open_file_whose_name_looks_like_history_is_still_protected
(restored)           OK       source put back
```

两条设计上的说明，都不是顺手写的：

- **「当前文件永不被删」原先测不到**。默认活跃名是 `agent.log`，它**不匹配**轮转名正则
  `agent-\d{8}-\d+\.log`，所以那个用例即使去掉 `register` 守卫也照样绿——绿的成因不是守卫。
  故新增一例：活跃文件名**恰好长得像历史**（`agent-20260924-1.log`），两向断言——注册过的
  留下、同名的未注册历史被删。变异表里只有这一例倒，说明守卫生效且此前确实无测试。
- 边界是**两侧都断**：13 天前的文件留、14 天前的删（`cutoff <=` 即「14 天窗口 = 今天 + 前 13 天」）。

## 2. 真机两臂取证（判据在真实进程的真实文件里）

单元测试只锁 writer；「一个进程会不会轮转自己的日志」只能在进程里看。两臂都走真实入口
`python -m wt_media_agent.local_api.server`，scratch 端口 18793、临时树、BitBrowser 指向死端口
`:15432`（开发者 `:54345`／`:8765`／`:18080` 全程未碰）。探针 `/tmp/t07-real-run.py`。

同一份流量（30 次 `/api/v1/status` + 1 次带 3000 字节 `id` 的 `profile-open`），只换界：

| | 臂 A（`max_bytes=2000`，`total_bytes=6000`） | 臂 B（出厂 20MB／400MB） |
|---|---|---|
| 跑完后磁盘 | `agent.log` 2000 + `agent-20260924-2.log` 2000 + `task-20260924-3.log` 2500 | `agent.log` 12236 + 三个 `task-*.log` 各 2500 |
| 今天新滚出的文件 | **有**（`agent-20260924-2.log`） | **无** |
| 截断标记 | **1 条** `truncate=true original_size=3185` | **0 条** |
| 1999 年历史 | 已删 | 已删 |
| 预置的当日 `task-…-1.log` | 被总量规则退掉 | 保留（远未超预算） |

臂 B 是臂 A 的对照：**同样的流量、同样的树形，只是不换界**。没有它，「滚了」就分不清是
20MB 上限干的还是别的原因（日期？启动？）。臂 A 的总量停在 6500（> 6000），见 §4。

真实截断那一行的原文（来自臂 A 的 `agent.log`，是被 3000 字节 `profile_id` 撑出来的真实记录）：

```
2026-09-24T14:14:16 [WARNING] __main__: local_api.profile_open.failure profile_id=ppppppp… truncate=true original_size=3185
```

## 3. 实测到一处真缺陷并修掉：启动清理此前是**空转**

臂 B 第一次跑完，1999 年的两个文件**还在**——我原以为「历史清理有效」已经由单元测试覆盖。

根因（实测，不是推想）：

```
families known before the handlers exist: []
what prune would delete        : []
is that because nothing matches: []
stale file still on disk       : True
```

`prune()` 靠**已注册的家族名**匹配文件，而家族名是 handler 构造时才注册的；`configure_logging`
却必须在 handler 存在**之前**就 prune（要在第一次写入前清）。于是启动那次删不掉任何东西，
只有等到运行中发生一次轮转、`_roll()` 再调一次 prune 时才「看起来生效」。
**我的单元测试之所以绿，是因为它先建了 handler** —— 测的是代码而非接线。

修法：`configure_logging` 先把三个文件路径注册给预算再 `prune()`，`register` 改为幂等。
回归测试 `StartupCleanupTest`（**先红，且只点这一条**，并配一条「活跃文件不被启动清理误删」的对照）。
修后臂 B 的 1999 文件才消失。

## 4. 不准的地方：总量的真实上界不是 `total_bytes` 到字节

臂 A 跑完 6500 字节，**超过**了 6000 的预算。机制：prune 只在**轮转与启动**两个点发生，
两次 prune 之间三个活跃文件仍可各自长到自己的单文件上限（滚动后活跃文件从 0 重新长）。

所以成立的说法是：磁盘总量上界 = `total_bytes + 3 × max_bytes`（出厂 400MB + 60MB），
**是有界，不是逐字节精确**。裁定要的是「总容量受限／不会无限增长」，这一条成立；
不成立的是「恰好不超过 `total_bytes`」，所以不这么写。

- 代码里如实写在 `LogBudget` 的 docstring 里，并给出这 60MB 的来源；
- 用 `test_the_total_does_not_grow_with_the_volume_written` 钉住它：**写 200KB 进去，
  总量 ≤ 500 + 3×200**。这才是裁定的要点——目录大小不随「记了多少」增长，而不是某个数字。
- 真机那一臂的判据也按此改（原判据 `≤ 6000` 会假红）。

## 5. 并发下的一处守卫（有专门测试，且能红）

三个 handler 线程共享一个预算：A 线程的 prune 列出文件后，B 线程的轮转可能已把它改名走。
`path.stat()` 抛 `FileNotFoundError` 会**中断整次 prune，并丢掉触发它的那条记录**。
`LogBudget._size` 把「已经不在的文件」计为 0 字节。`BudgetRobustnessTest` 先红后绿
（去掉守卫 → `FileNotFoundError` 出栈）。

## 6. 声明为未覆盖

- 真机取证只在 **macOS** 上做。Windows 的路径形状按 §5.8 登记为**未取证**。
- **真机臂没有覆盖「日期翻档」**：翻转 UTC 日期需要跨零点或改系统时钟，两者在本机取证里
  都不可接受，故日期翻档只有注入时钟的单元测试（`DateRollTest`）撑着。
- 两进程同时写同一日志目录**未测**：`_free_name` 用「先查再改名」而**不是** `O_EXCL` 创建
  （Desktop 侧 T-12 才用 `create_new`）；跨进程同名竞争可能让一个进程的轮转命名多一次重试，
  未实测，登记为未覆盖。
- 总量口径是**三个文件合起来 400MB**（共享一个预算对象）。若按「每个文件各 400MB」解读，
  则应为 1.2GB——按 Q-02 的「Agent 400MB」取前者，T-18 回写时把口径写清楚。

## 7. 顺带实测（不属于本 Task，登记给 T-09）

真机臂里 `agent.log` 的 logger 名是 `__main__`，不是 `wt_media_agent.local_api.server`：

```
2026-09-24T14:14:16 [WARNING] __main__: local_api.profile_open.failure …
```

`python -m wt_media_agent.local_api.server` 使模块以 `__main__` 执行，`getLogger(__name__)`
随之得名 `__main__`。今天不影响路由（`task.log` 只收 `wt_media_agent.runner.*`），
但它削弱了「日志可定位问题」——真实 dev/装机运行的 HTTP 侧记录看不出是哪个组件发的。
**本 Task 不改**（属 T-09 对 `local_api/server.py` 的范围），如实登记。

## 8. 验证命令与结果

| 命令 | 期望 | 实际 |
|---|---|---|
| `bash scripts/test.sh` | 只增不减、`.local/` 守卫不响 | **320 tests OK, exit=0**（T-06 后 293 → +21 轮转/预算 +6 配置）；守卫未响；`--- Logging error ---` 0 条 |
| `f07d9e8` 单独 worktree 再跑 | 提交自身绿 | **320 OK, exit=0** |
| 探针 `/tmp/t07-mutation-probe.py` | 六个界各打掉自己的用例 | 见 §1 表，`(none, control)` 先绿 |
| 探针 `/tmp/t07-real-run.py` | 8 项判据全绿 | 8/8 PASS（臂 A 五项、臂 B 三项对照） |
| 守卫的去/留 | 去掉即红 | 去掉 `_size` → `FileNotFoundError`；去掉 `register` 幂等 + 预注册 → `StartupCleanupTest` 红 |

（探针都在 `/tmp`，不进仓。）
