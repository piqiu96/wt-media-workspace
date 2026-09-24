# 证据 — T-14 Desktop `[logging]` 配置 + 校验 + 出货资源

范围：计划本条——①出货 TOML 补 `[logging]`（`level` / `max_file_bytes` / `retention_days` / `total_bytes`）；
②`DesktopConfig` 加 `Logging`，与其余六节同款 `#[derive(Clone, Debug, Deserialize)] #[serde(deny_unknown_fields)]`，
**不加** `#[serde(default)]`；③`validate()` 追加检查，**只点名键、绝不回显值**；
④一条断言出货值 == `rolling::Limits::SHIPPED` 的用例（两处不能漂移）。

提交边界：`wt-media-desktop`（`src-tauri/src/config.rs`、`src-tauri/resources/desktop.production.toml`），**1 个 commit**。

---

## 1. 先红：`[logging]` 不存在时，新表自己先打到自己

`out_of_range_values_are_rejected` 的表在这条改成 **4 列**（第 4 列 = 报错必须点名的键），
并在每行前断言 `PRODUCTION_TOML.contains(from)`——于是「出货文件里还没有这一节」这件事**先于**校验逻辑暴露：

```
$ cargo test --bin wt-media-desktop-shell config::tests::out_of_range_values_are_rejected
test result: FAILED. 0 passed; 1 failed
panicked at src-tauri/src/config.rs:429:13:
row "unusable log level" matches nothing
```

第 4 列是**承重**的，不是装饰：没有它，一行也可能因为**更早的**检查顺手拒掉了改写后的文件而变绿，
该行便不再证明自己的规则——检查一旦重排或在它上面插入新检查就会静默失效。这一点写进了用例的文档注释。

## 2. 交付形态

| 处 | 内容 |
|---|---|
| 出货 TOML | `[logging]` 四键 + 注释说明 `auto` 的含义与「级别严于 info 时不建文件」（实测在 T-15） |
| `Logging` struct | `level: String`、`max_file_bytes: u64`、`retention_days: i64`、`total_bytes: u64`；`deny_unknown_fields`，**无** `#[serde(default)]`（字段缺失即错：出货文件与本结构不许悄悄分叉） |
| `LOG_LEVELS` / `LOG_LEVEL_AUTO` | 常量，`pub` 到 crate 内——T-15 的 subscriber 要拿这份词表映射 `LevelFilter`，**不许在别处再手写一份**（第二份词表可以接受这里拒绝的级别） |
| `validate()` | 级别不在词表且不是 `auto`；两个 u64 的 `== 0`；`retention_days <= 0`；`total_bytes < max_file_bytes` |
| 用例 | 表扩到 **13 行**；新增 `the_shipped_logging_values_are_the_writers_shipped_limits`、`every_accepted_log_level_loads_and_is_named_in_the_message`、`the_accepted_log_levels_are_these_six_spellings`；`unknown_key_is_rejected...` 改为**逐节**枚举 |

三处**超出计划原文**的检查，逐条登记而不是夹带：

| 超出项 | 理由 |
|---|---|
| `retention_days <= 0`（计划写「三个 0」） | TOML 有负数，`-1` 能装进 `i64`；负保留期把截止点推到未来 ⇒ 今天之前**每个文件**都过期，而当天文件靠 T-12 的「当前文件永不删」兜住 ⇒ 症状是「文件隔天消失得比配置说的早」。计划只说 0 是因为默认类型是 `u64`，这里不是 |
| `total_bytes < max_file_bytes` | 总量比单文件上限还小是**不可满足**的配置：writer 为守单文件上限翻档，再为守总量删掉刚写的那个文件 ⇒ 每条记录同时是赶走自己的那条 |
| `unknown_key` 用例逐节枚举 | `deny_unknown_fields` 是**按 struct** 写的：顶层那条 derive 只守顶层。见 §3 的 M9 |

## 3. 变异表：控制行先绿，9 个变异逐个红

探针 `/tmp/t14_mutate.py`：逐次改**真实文件**的一处（每次从 pristine 副本还原），
跑 `cargo test --bin wt-media-desktop-shell config::tests`（16 条）。

```
控制：未变异                                   → 147 passed / 0 failed（全仓口径）
M1 撤掉 logging.level 检查                     → RED（表 + 级别正向用例）
M2 撤掉两个 u64 的 == 0 检查                    → RED（表）
M3 retention_days 的 <= 0 改回 == 0            → RED（表「negative log retention」行）
M4 撤掉 total_bytes >= max_file_bytes           → RED（表）
M5 出货 TOML 单文件上限改 20971520 → 20971521   → RED（表 + 漂移用例）
M6 LOG_LEVELS 去掉 trace                       → RED（词表钉死用例）
M7 LOG_LEVELS 里 trace 变成第二个 debug         → RED（同上）
M8 auto 混进 LOG_LEVELS                        → RED（同上）
M9 Logging 的 deny_unknown_fields 撤掉          → RED（逐节枚举用例）
```

**9/9 红，没有幸存者。** 覆盖面按计划本条的判据逐条枚举：

| 判据（计划本条） | 守它的用例 | 变异 |
|---|---|---|
| 非法级别被拒 | 表「unusable log level」行（点名 `logging.level`） | M1 |
| 三个 0 被拒 | 表「zero log file cap / zero log retention / zero log total budget」三行 | M2/M3 |
| 总量小于单文件上限被拒 | 表「log budget smaller than one file」行（点名**两个**键） | M4 |
| 报错**只点名键、不回显值** | 既有 `rejected_values_are_not_echoed_in_validation_errors`（`cloud.base_url` 带 `user:secret@` 仍逐字绿）+ 表新增的键名断言 | M1–M4（新消息全部键名式，未引入任何值） |
| 出货值与 `rolling::SHIPPED` 不漂移 | `the_shipped_logging_values_are_the_writers_shipped_limits` | M5 |
| 字段缺失即错 | 结构上**无** `#[serde(default)]`（无 default 就没有「缺失即默认」这条路） | —（见 §5） |

### 3.1 探针查出两个缺口，两个都补了

- **M6/M7/M8 暴露的是「词表驱动的断言」的通病**：正向臂与报错文案**都从 `LOG_LEVELS` 推导**，
  于是把数组改小/改错时，两侧一起跟着变，整个模块**全绿**——M6 第一次跑就是 SURVIVED。
  修法是把常量本身**用手写值钉死**（`len == 6` + `join(" ")` 逐字比对 + `auto` 不在表内），
  照 `rolling::Limits::SHIPPED` 的成例。用 `join` 而非数组比较是有意的：数组比较在长度变化时是**编不过**，
  而「编不过的变异什么都证明不了」（T-12 的 M13 已登记过同一条教训）。
- **M9 暴露 `deny_unknown_fields` 从未在**节内**被验证过**：既有用例把 `runtime_token` 放在文件**顶层**，
  被顶层的 derive 拒掉，于是每个子结构的那行 derive 都无人守。这直接咬住本 Task 新增的 `[logging]`——
  多写一个 `token = "…"` 会被**静默忽略**。修法是把该用例改成**逐节枚举**（顶层 + 七个节头），
  M9 随即红。

## 4. 读数

| 指标 | 改前（T-13 后 HEAD） | 改后 |
|---|---|---|
| `cargo test --workspace` | **144 passed; 0 failed** | **147 passed; 0 failed**（+3） |
| `cargo build` 条目级警告 | 93 | **93**（不变） |
| `cargo clippy --workspace --all-targets` | 97 | **97**（不变） |

**警告不升是测量结果，不是默认**：新加的两个常量都从 `validate()`（**非测试代码**）引用，
故不产生新的 `dead_code`；`Logging` 的字段由 derive 构造/读取，同样不入 `dead_code`。
T-15 的待验期望因此仍是 **93 → 4 / 97 → 10**，起点未被本 Task 移动。

## 5. 未覆盖项与待验项

- **`level` → `LevelFilter` 的映射未落地**（本 Task 只到「词表 + 校验」）：`auto` → `Levels::shipped(env)`、
  显式值直接采用，都在 **T-15** 的装配函数里，本 Task 没有断言它。词表已 `pub` 供其复用。
- **四个数字到 `rolling` 的接线在 T-15**：本 Task 只断言「出货值 == `rolling::SHIPPED`」，
  没有断言「app 真的把出货值交给了 writer」。
- **「字段缺失即错」无独立用例**：靠的是**不写** `#[serde(default)]`，而不是靠一条检查——
  没有 default 属性就没有「缺失时取默认」这条路径可断言。M9 是它的邻接守卫（未知键而非缺失键）。
- **Windows 日志布局未取证**（与 T-11/T-12/T-13 同一登记）。
- **`cargo fmt` 的口径**：只对本文件跑 `rustfmt`，然后**逐行比对**其输出与我的版本——
  差异**只有 7 处既有脏行**（本仓不是 rustfmt-clean 的，T-13 已量化过），已全部还原成 HEAD 形态；
  新增代码本身是 rustfmt-clean 的。故本 Task 的 diff 里没有一行与本 Task 无关的重排。

## 6. 复现命令

```bash
cd wt-media-desktop
cargo test --workspace
cargo test --bin wt-media-desktop-shell config::tests
python3 /tmp/t14_mutate.py            # 9 个变异，逐个红
```
