# 证据 — T-13 Desktop 后端装配 + target 白名单 + 单行格式 + 脱敏

范围：计划本条的四件事——①`tracing-subscriber` 后端装配（**唯一初始化入口**，裁定二的 Desktop 侧）；
②target 白名单，默认 `OFF`，`const OWNED_TARGETS` 枚举断言逐个可用；③记录格式（纯文本、单行、对齐 Agent 形状）；
④脱敏。外加计划本条两向断言的三条：外来 target **不入**文件、自有 target **入**文件、
`agent.supervisor` **永不比 INFO 更严**（两向）；含 token 的记录落盘后 **grep 不到**且周围文本仍在。

提交边界：`wt-media-desktop`（新增 `src/logging/{redact,targets,backend}.rs` + `logging/mod.rs` 8 行）。

---

## 1. 交付形态：三个模块，四条规则，一处收口

| 模块 | 形态 | 纯/薄 |
|---|---|---|
| `logging/redact.rs` | `redact(text, secrets) -> String`——手写扫描器，**零依赖**（不引 `regex`）。次序：`mask_keyed → mask_userinfo → mask_bearer → mask_jwt → mask_known` | **纯**（同输入同输出，幂等） |
| `logging/targets.rs` | `OWNED_TARGETS`（3 个）、`SUPERVISION_TARGET`、`effective_level`（规则）、`Levels{shipped, for_target, filter}` | **纯**（`filter()` 只造 `Targets` 值，不安装） |
| `logging/backend.rs` | `Options` + `assemble(Options) -> impl Subscriber`（装配）、`LineFormat`（渲染）、`Sink{File,Stderr}`/`LineWriter`/`LineSink`（收口） | 薄 IO：唯一碰文件的地方 |

**掩码点选在 sink，而不是 `Filter`。** 理由是 T-06 在 Agent 侧实测出的那条教训：`logging.Filter` 改不到
traceback，而凭据最容易出现在 traceback 里。放在「成品行 → writer」这一处收口上，
消息、字段与**将来任何 formatter 加的东西**都被按构造覆盖。Agent 侧同一结论的落点是 formatter，
Desktop 侧是 sink——两处都是「记录成形后、离开进程前」的那一个点。

装配形态 `Registry::default().with(document).with(terminal)`，两个 layer 各自 `.with_filter(filter)`；
无目录时 `document` 是 `Identity::default()`（**总有一个 stderr 出口**，裁定五的 Desktop 侧）。
`assemble` 返回 `impl Subscriber + Send + Sync` 而**不安装**，所以测试用 `tracing::subscriber::with_default`
（线程局部）注入，不需要全局默认值、不需要串行跑。

## 2. 与 Agent 的差分表（20 行同一张表跑两边实现）

词表与形状抄 Agent（`runtime/logging.py`），但抄不等于一致。故做了一次**差分实测**：
同一 20 行、同一 `secrets`（本机 runtime token 形状的字面值）分别过 Agent 的 `redact` 与 Desktop 的
`redact`，逐行比输出。**17/20 逐字相同，3 行不同**：

| # | 行 | Agent | Desktop |
|---|---|---|---|
| 7 | `{"client_secret": "s3cr3tvalue"}` | `{"client_secret: "***"}` | `{"client_secret": "***"}` |
| 13 | `token=aaa password=bbb` | `token=*** password=bbb` | `token=*** password=***` |
| 16 | `cookies: a=1; b=2` | `cookies: ***; b=2` | `cookies: a=***; b=***` |

相同的那 17 行含 `Cookie:`/`Set-Cookie:`/`Authorization: Bearer`/`Basic`/`proxy_password`/`password`/
`refresh_token`/`X-Api-Key`/查询串 `?token=`/URL userinfo/裸 JWT/`runtime_token`/裸 `Bearer` 词后无令牌形状
（两边都不动）/`mytoken=`（两边都不动）/`tokenizer`（两边都不动）/`token=a`/`launch tid=<token> in flight`。

三处不同的根因都**从 Agent 自己的代码里读出**，不是猜的：

- **#13**：`_KEYED = (?i)\b(KEY)["']?(\s*[:=]\s*)([^\n]*)` 把**整行剩余**捕获进 `tail`，而 `re.sub`
  从整段匹配之后继续 ⇒ 一行里的第二个凭据**永远不进扫描**。Desktop 的扫描在「刚掩掉的那个值之后」续扫
  （`mask_keyed` 的 `search = resumed_at`），故两个都掩。**这是本 Task 有意修正的第一处**，变异 M1 守着它。
- **#16**：`_is_cookie_key` 判的是 `endswith("cookie")`（**单数**），而词表里有复数 `cookies` ⇒ 复数键
  落到通用 keyed 路径，只吃到 `;` 前的第一个值，`; b=2` 原样留下。Desktop 的 `family()` 同时认
  `cookie`/`cookies`。**这是有意修正的第二处**，变异 M12 守着它。
- **#7**：`_KEYED` 里的 `["']?` 属于**被消费掉**的部分，回显只拼 `key + separator` ⇒ JSON 键的闭引号
  丢失，该行不再是合法 JSON（读日志的人看不出这是哪个字段）。Desktop 的 `separator_end` 只**跳过**引号，
  回显仍取原文 `text[key_end..tail_start]`，引号保留。

**这三处是 Agent 侧的发现，不是 Desktop 的胜利**：三行里有两行（#13、#16）是真泄漏。
按「一仓一 commit」，它们**不在本 Task 里改**，登记为 **Q-08**（见 §7），交你裁定后再开 Agent 侧 Task。

## 3. 变异表：控制行先绿，12 个变异逐个红

探针 `/private/tmp/t13/probe.py`：逐次改**真实模块**的一处，跑 `cargo test --bin wt-media-desktop-shell logging::`
（76 条），记下谁死了；每次**立即**从 pristine 还原并 sha256 核对（`restored redact.rs/targets.rs/backend.rs: True`）。

```
控制：未变异                          → 76 passed / 0 failed
M1  redact：值掩完后不在值尾续扫（Agent 的缺陷）  → RED ×3（含落盘那条）
M2  redact：把值的尾巴也在这里 push（打两遍）     → RED ×1
M3  redact：MIN_SECRET_LENGTH 8 → 3               → RED ×2
M4  redact：去掉 mask_bearer 调用                 → RED ×2
M5  redact：is_sensitive_key 去掉 `_` 前缀条件     → RED ×1
M6  targets：effective_level 去掉 INFO 下限        → RED ×3
M7  targets：filter 的 with_default 用配置级别     → RED ×2
M8  targets：OWNED_TARGETS 里 webview 改个名       → RED ×3
M9  backend：single_line 不转义                    → RED ×1
M10 backend：sink 不再 redact                      → RED ×1
M11 backend：stamp 去掉 `Z`                        → RED ×2
M12 redact：family 只认单数 cookie 键              → RED ×1
```

**12/12 红，且没有一条断言永远绿。** 覆盖面按计划本条的判据逐条枚举：

| 判据（计划本条） | 守它的用例 | 变异 |
|---|---|---|
| 外来 target **不入**文件 | `a_target_desktop_does_not_own_never_reaches_the_file`（**同一条里带对照臂**：同一 subscriber、同一写路径，自有 target 的那条记录在文件里） | M7 |
| 自有 target **入**文件（枚举） | `every_target_desktop_owns_produces_a_record_in_the_file`（`EMITTED_TARGETS` 与 `OWNED_TARGETS` 逐字 `assert_eq!`，再逐 target 断言文件里有它的记录，并断言行数 == target 数） | M8 |
| `agent.supervisor` **永不比 INFO 更严**（两向） | `supervision_is_never_held_stricter_than_info`（OFF/ERROR/WARN → INFO；INFO/DEBUG/TRACE 不上抬）、`the_floor_belongs_to_the_supervision_target_alone`、`the_floor_holds_at_the_filter_and_not_only_in_the_rule`（规则层与 filter 层各一条）、`supervision_is_recorded_even_at_a_level_that_would_hide_it`（落盘层） | M6 |
| 含 token 的记录落盘后 **grep 不到**、周围文本仍在 | `a_credential_never_reaches_the_file_and_the_line_around_it_does` | M10/M1 |
| 记录格式：纯文本单行、对齐 Agent | `the_line_reads_the_way_the_agent_writes_it`（**整行逐字**：`2026-09-24T10:11:12Z [INFO] desktop.startup: hello\n`）、`the_stamp_is_the_day_and_the_time_utc`、`a_record_stays_one_line_when_the_message_does_not` | M11/M9 |
| 脱敏形状覆盖（表驱动 16 行，`gone` 与 `kept` 两列） | `every_credential_shape_is_masked_and_the_line_around_it_survives`、`every_credential_on_a_line_is_masked_and_not_just_the_first`、`a_name_that_merely_contains_a_credential_name_is_left_alone`、`a_bearer_word_with_nothing_token_shaped_after_it_is_left_alone`、`a_url_with_a_user_but_no_password_keeps_its_user`、`a_value_too_short_to_be_a_secret_is_not_used_as_a_needle`、`a_secret_this_process_holds_is_masked_without_a_key_to_name_it`（**带对照臂**）、`masking_a_line_twice_changes_nothing_more` | M1–M5/M12 |
| 目录不可用不阻断 | `an_unusable_directory_still_gives_a_subscriber`、`a_file_that_cannot_be_written_does_not_turn_into_an_io_error`、`a_record_that_never_got_its_newline_is_still_written_when_the_sink_drops` | —（M9/M10 顺带覆盖前两条的路径） |

### 3.1 探针查出的三个缺口（三个都补了，不是记下来了事）

- **M2 是探针之前就被我自己的表测抓到的真 bug**：`Family::Value` 分支最初把「掩码 + 尾巴剩余」一起 push，
  而循环的 `copied` 只推进到值的末尾 ⇒ 尾巴被打印两遍（`token=*** password=bbb password=*** …`）。
  修法 = 该分支只 push 值的掩码、返回「续扫位置 = 值尾」，剩余由循环的复制路径走一遍。
  M2 就是把这个错误写法放回去，表测当即为红。
- **表测里原有的 `Bearer` 行不是 `mask_bearer` 的守卫**：那一行是 JWT，被 `mask_jwt` 掩掉，
  于是「裸 `Bearer` 词 + 令牌形状」这条规则**只有** `a_bearer_word_with_nothing_token_shaped_after_it_is_left_alone`
  一条用例守着——而那条的名字只说了**反向**（不掩）。补一行**非 JWT** 的
  `handed bearer aaabbbcccddd to the Agent`；M4 随即从「RED ×1」变成「RED ×2」（表测也红了）⇒ 新行是承重的。
- **`family()` 的复数 `cookies` 分支此前没有任何用例**（`grep cookies` 在测试里零命中，词表与规则各有一处）。
  补一行 `cookies: a=1; b=2`；并新增变异 **M12**（把复数条件删掉）验证它能红——**M12 第一次跑就红**。
  这条同时是 §2 #16 那处 Agent 缺陷的守卫：Desktop 认复数这件事从此有机器守着。

## 4. 记录格式：三处与 Agent 的**有意**差异（逐个登记，不是疏漏）

| 项 | Agent | Desktop | 理由 |
|---|---|---|---|
| 时间戳 | `%Y-%m-%dT%H:%M:%S`（本地时间，无 `Z`） | `…Z`（UTC，`rolling::date_of` + `rem_euclid(86_400)`） | Desktop 的文件名已按 UTC 日期分档（T-12），记录与文件名必须同一把尺，否则跨午夜读日志会看到「文件名 09-24、行首 09-23」 |
| 键前边界 | `\b`（Unicode 感知） | ASCII 词边界 | 与 T-12 的文件名解析同一条口径；差异方向是**更严**（紧跟非 ASCII 字符后的键，这里掩、那里漏） |
| 复数 cookie 键 | 走通用路径，只掩第一个值 | 按 cookie 表全掩 | §2 #16；**有意修正**，变异 M12 守着 |

**未引 `env-filter`**（T-10 已定）：没有正则就没有 matchers 依赖树，白名单用 `Targets` 足够表达。
**`Levels::shipped`** 生产 INFO / 开发 DEBUG（裁定四），`Levels::filter()` 的默认是 `OFF` 而不是 default 级别
——`h2 0.4.15`/`hyper-util 0.1.20`/`softbuffer 0.4.8` 已在树里且已在向任何 subscriber 发 span，
不挡就会在**最需要日志的那一刻**把文件灌满连接帧。默认 `OFF` 之后，「加一个 target」是一次决定而不是一次疏忽。

## 5. `cargo fmt` 的连带面（如实登记：本仓不是 rustfmt-clean 的）

收尾前对新增文件跑了一次格式化，第一反应是 `cargo fmt`（全仓）。它**重排了 16 个文件**
（481 insertions / 153 deletions），其中 15 个**与本 Task 无关**，含 T-12 已提交的 `logging/rolling.rs`
与 `bootstrap.rs`/`config.rs`/`http/*`/`sidecar/*`/`commands/*`/`paths.rs`/`preflight.rs` 等。

**先量后判**：逐文件把两侧都去掉全部空白与逗号后取 sha256 比对——3 个逐字相同，其余 12 个的差异
**全是逗号与换行**（rustfmt 补或删尾随逗号、把一行拆成多行），唯一的非逗号差异是 `paths.rs` 的
闭包花括号（`|p| p.is_file()` → `|p| { p.is_file() }`，语义相同）⇒ **全部落在格式层面，没有一处语义变化**。
结论：本仓的既有代码**从未**满足过 `cargo fmt`（若满足，重排不会是 16 个文件），
故这是「格式化器与仓库既有风格不一致」，不是「我改了别人的代码」。

**处置**：整份 diff 存成 `/private/tmp/t13/fmt-spillover.patch`（sha256 `4b01a5a1dfab7d6a…`，1252 行），
再用 `git stash push -m "T-13 out-of-scope: cargo fmt spillover over 15 files"` 落成 `stash@{0}`
（**可还原**，不是丢弃）。工作树只留本 Task 的 4 个文件。新增的三个文件保持格式化后的形态
（它们本来就是新文件，不牵动任何既有文件）。**全仓格式化是另一个决定，不在本 Task**
——它要动的文件属于别的 CHG，且会让每个后续 Task 的 diff 检查失去意义。

## 6. 测试与警告读数

| 指标 | 改前（T-12 后） | 改后 |
|---|---|---|
| `cargo test --workspace` | **116 passed; 0 failed** | **144 passed; 0 failed**（+28） |
| 其中 `logging::` 过滤（探针与变化用的口径） | — | **76 passed**；144 − 76 = **68** = 起点，与计划登记一致 |
| `cargo build` 条目级警告 | 43 | **93** |
| `cargo clippy --workspace --all-targets` | 48 | **97** |

**+28 的构成**：`redact` 8 条、`targets` 8 条、`backend` 12 条（后加的并行表行不新增用例）。

**增量逐文件核对**（build：`redact` 32 + `backend` 13 + `targets` 5 = +50，别的文件 0 增；
clippy：同三个文件 +50，同时 `rolling.rs` **32 → 31**）。

那 **−1** 已查明根因，且它本身就是一条独立证据：**`Date::{year, month, day}` 因 `backend::stamp`
调用而不再是 dead code**。做法是临时把 `logging/mod.rs` 里的三行 `pub mod` 撤掉、把 T-12 的状态**复现**出来
再量：build **43**、clippy **48**，与 T-12 的证据逐字一致 ⇒ 两轮读数可比、拆分精确。
（`rolling.rs` 的 clippy 条目差异是 `` methods `year`, `month`, and `day` are never used `` 这一条消失。）

**新增的 97 条里没有一条是我三个模块的真 lint**：`97 − 93 = 4` 条非 dead_code，全部是既有项
（`commands/account.rs` ×2 的 `?` 运算符、`main.rs` 的 `items after a test module`、
`sidecar/drain.rs` 的 `assert_eq!` 配字面 bool），都在本 Task 未触碰的文件里。
过程中我自己写出的两条真 lint 已改而不是带上：`write!` 配「以单个换行结尾」的格式串 → `writeln!`。

**T-15 的待验期望据此更新**：接线完成后 `cargo build` 条目级警告应从 **93** 回到 **4**、
clippy `--all-targets` 从 **97** 回到 **10**（T-12 登记的终点不变——本 Task 的 +50 全是接线后变活的 `dead_code`）。
不降即说明模块没被真正接上。

## 7. 未覆盖项与待裁定项

- **Q-08（新增，`Blocking = NO`，但 DONE Gate 前必须落地）**：§2 的 Agent 侧三处发现里，
  **#13 与 #16 是真泄漏**（一行里的第二个凭据、复数 cookie 键的第二个值会原样进 Agent 的日志文件）。
  T-06 已提交（`b66d7f5`/`70c1f93`），按「一仓一 commit」不在本 Task 里改。
  拟开 **Agent 侧一个独立 Task（T-20）**：同一张 20 行差分表进测试 + 一条变异 + 真实启动取证，
  自己的 commit 与 evidence。**等你一句话**再动 Agent 仓。
- **真实启动未做**（本 Task 只到装配层）：`assemble` 的调用点在 **T-15**，stderr 与开发态日志文件
  两条出口的端到端判据也在 T-15。`note()` 的 stderr 文本、`secrets` 的实际来源（launch token）
  同属 T-15 的取证范围，本 Task **没有**断言它们。
- **Windows 未取证**（与 T-11/T-12 同一登记）。
- **已知极限**（写进模块文档，不是隐藏）：无键、无 JWT/bearer 形状的**裸凭据**形状规则不抓，
  只能靠 `secrets` 命中——这正是 launch token 的通道。
- **未覆盖的边**：`SystemClock::now`（一行 `SystemTime::now()`，按构造无从单测，T-15 覆盖）；
  `Sink::Stderr` 的**并发交错**（多条记录同写 stderr 的字节级交错）未断言。
