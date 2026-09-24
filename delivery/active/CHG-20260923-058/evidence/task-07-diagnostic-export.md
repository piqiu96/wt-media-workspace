# Evidence: T-07 脱敏诊断导出

## Purpose

交付 AC-10：**诊断包不含完整凭证、Cookie、代理密码与用户媒体文件**。
一个命令供 T-08 的「本机设置」页调用，**不收任何参数**：

| 命令 | 回答 |
| --- | --- |
| `local_diagnostic_export` | 把「版本 + 组件状态 + 已脱敏日志 + 失败任务摘要」打成一个归档，返回它在哪、多大、摘要值 |

命令体不做决定：归档的名字、内容、上限、脱敏都在 `diagnostic.rs` 里，接线在 `commands/diagnostic.rs`，
线上形状在 `dto/diagnostic.rs`。

## Method

```bash
cd wt-media-desktop && bash scripts/test.sh                       # 起点 276 passed，只增不减
cd wt-media-desktop/src-tauri
rustfmt --edition 2021 --check --config skip_children=true <本次每个文件>   # 只对单个文件跑
python3 /tmp/chg058/mutate_t07.py diag|cmds|dto                   # 三组各自带阴性对照
cargo test --offline commands::diagnostic::probe::probe_real_machine -- --ignored --nocapture
cargo check --offline                                             # 警告计数按文件归位
```

## Actual

### 落点表

| 文件 | 性质 | 行数 | sha256(前 12) |
| --- | --- | --- | --- |
| `src-tauri/src/diagnostic.rs` | 新（规则本体 + 28 条用例） | 1768 | `426ba2458357` |
| `src-tauri/src/commands/diagnostic.rs` | 新（接线 + 4 条用例 + 1 条 ignored 探针） | 784 | `d08373452616` |
| `src-tauri/src/dto/diagnostic.rs` | 新（线上形状 + 2 条用例） | 262 | `c98fa6557d72` |
| `src-tauri/src/main.rs` | 改：`mod diagnostic;`、`DiagnosticHost` 入 `manage`、**一份 `secrets`**、命令追加在 `invoke_handler!` 末尾 | 24/1 | `f2576421fb6a` |
| `src-tauri/src/paths.rs` | 改：`Source::code()`（5 个小写词）+ 1 条用例 | 48/0 | `5258e0e7d00d` |
| `src-tauri/src/config.rs` | 改：`Environment::code()` + 1 条用例 | | `916c046b5fe2` |
| `src-tauri/src/logging/backend.rs` | 改：抽出 `stamp_with(format, time)`（唯一读钟处）+ 1 条用例 | | `e457fcecb29f` |
| `src-tauri/src/app_paths.rs` | 改：`the_log_root_is_never_inside_the_data_root` + 1 条用例 | 35/0 | `a51f03ab1dbe` |
| `src-tauri/src/{commands,dto}/mod.rs` | 改：各 1-4 行声明 | | `66364c14c095` / `58e2928a58f4` |
| `src-tauri/Cargo.toml` / `Cargo.lock` | 改：+4 个依赖（`tar`/`flate2`/`sha2`/`hex`）；lockfile 514 → **516** 包（`tar 0.4.46` + `filetime 0.2.29`） | 19/0、24/0 | `b637eefddb0d` |

`paths.rs` 是**从 `HEAD` 重建**的（`git diff --numstat` = `48 0`）：它是 T-06 登记的 14 个格式化残留文件之一，
直接提交工作区版本会把 ~25 行与本 Task 无关的排版带进这个 commit。

### 归档的形状

```text
wt-media-diagnostic-20260924-234615.tar.gz     # 一个 gzip tar，一棵目录树
├── summary.json      # 机器读：四件事
├── manifest.txt      # 人读：同一批事实 + 上限 + 脱敏声明
└── logs/
    ├── desktop/desktop.log
    └── agent/{agent,error,task}.log
wt-media-diagnostic-20260924-234615.tar.gz.sha256   # `shasum -a 256` 格式，一行
```

摘要在**归档之外**：把 sha256 放进自己被摘要的归档里会变成自指，所以它是同目录的兄弟文件
（manifest 里写了这句话，用例 `the_manifest_lists_every_entry_and_every_omission` 钉住 `.sha256` 出现在正文里）。

### 信封里有什么——逐项枚举

`summary.json` 的键（`the_wire_key_sets_are_pinned` 断言**集合**、`an_empty_report_still_carries_every_key`
断言空报告仍带**每一个**键——不是读某一个字段：少一个键和改一个键名同样显眼）：

| 段 | 内容 |
| --- | --- |
| `created_at` | 本机时区，与日志行同形（19 字符，D-09 同一个钟） |
| `desktop` | `app_version`（产物版本，`.dmg` 上刻的）、`build_version`（`CARGO_PKG_VERSION`）、`environment`、`config_source`（`Source::code()`）、`config_rejected`、`data_root`、`logs_root`、`cache_root`、`free_bytes` |
| `sidecar` | `running` |
| `binding` | `bound`、`node_id` |
| `agent` | `state`（`answered`/`unreachable`）、应答时的具名字段、无应答时的 `error` |
| `logs` | `entries`、`omitted`、`bytes` |
| `failed_work` | `source`、`count`、`records`、`truncated` |

**两个版本号是有意的**：`app_version` 是产物版本（用户说「我装的是哪个包」时看的就是它），
`build_version` 是这次编译的 crate 版本。合成一个号码会让「包和内核不是同一次构建」这类事实读不出来。

**`bit_profile_ids` 只计数、不列举**（`bit_profile_count`）：这些 id 命名的是用户的浏览器配置，
一台机器可能有几百个；读包的人需要知道 Agent 手里有没有，不需要知道是哪些。**登记为有意省略**（D-14），
因为它属于「我们少放了一样东西」这一类——那类事应该被读到，而不是从截图上推断。

**`main_user_id` 有意包含**：它是「这个包属于哪个账号」的唯一线索，本身不是凭证。

`omitted` 的三种理由与 T-06 的保留原因同一套拼法习惯：`name_too_long` / `unreadable` / `archive_full`。

### AC-10 的「不含用户媒体文件」靠的是**布局**，不是过滤器

这是本 Task 最值得写下来的一条。导出的日志载荷来自 `reader::list`——它是**查看器、清理、导出共用的唯一分类源**。
而 `reader::list` **不按名字过滤**：它列出目录里**每一个普通文件**（`classify` 只给它一个类目，
`Other` 也照列——D-12 已经定过这条：不认识的日志名是**可见**类目）。

所以「不含用户媒体」不能靠「名字长得像日志」这条判据，它靠的是：

| 断言 | 位置 |
| --- | --- |
| 每棵树**只读一层**、只读**目录的直接子项**，从不向下走 | `a_media_file_inside_a_subdirectory_of_the_tree_is_not_reachable` |
| 本组件的日志根**不在**本组件数据根里（两种布局各一次） | `app_paths::the_log_root_is_never_inside_the_data_root` |
| 缓存根同样不在数据根里（T-03 已有） | `app_paths::cache_is_never_inside_the_data_root` |

素材/成片在数据根下、且在子目录里；**没有任何代码路径会走进去**——与 T-06 保护五类业务数据是同一个论证。

那条新用例自带**阳性对照**：同一个树里**直接躺着**的 `clip.mp4` 会被列出（`entries` 两个，含它），
所以「子目录里的进不来」是关于**不向下走**的断言，不是关于「一个把陌生名字都拒掉」的过滤器。
`reader::list` 的 `NotFound` 与 `Err` 之分（T-05 定的）也一并保留：树不存在是「还没有日志」，
树读不出来是 `omitted: unreadable`——**不是**整次导出失败，因为一个失败的导出给不出任何证据。

**如实登记**：直接躺在日志树里的陌生文件是**会被收进来**的（脱敏、限长之后）。理由不是「无所谓」，
而是：那棵树归本组件所有，直接躺在里面的文件是关于本组件的证据，而 T-06 已经定过这条线的另一边——
不认识的日志名是**可见**类目。想清掉它只能手动（D-12），想看它是这个包的职责。

### 脱敏不变量是**门上的**，不是调用者手上的

每一条进入归档的字符串都经过 `diagnostic::mask`（= `logging::redact::redact`）：
**日志条目是两次**——写它的那一层一次、进归档时再一次。第二次不是仪式：

- 写者换成带 mask 的版本**之前**留下的文件还在磁盘上，而这个归档**是离开这台机器的那个东西**；
- 调用者可以递进来一条不是本模块构造的条目（`bundled_files` 的入参就是），门必须自己成立。

`bundle_files` 里那一行（`bytes: mask(&entry.text, &host.secrets)`）就是这扇门，变异 **d02** 打的正是它。
`redact` 幂等（Agent 自己的文档写着，两侧用例都钉着），所以第二次不会破坏任何一行——
`masking_twice_leaves_the_bytes_alone` 是这条依赖的判据。

### 凭据证据：先证明针抓得住，再报分母

**单测**（`a_credential_in_the_logs_or_the_facts_never_reaches_the_archive`）：
把一个含真凭据行种进日志树（`token=launch-token-9f2c8a41`、`node_credential=node-credential-4b7e1d90`），
**先把那个文件从磁盘读回来、断言两个针都在**（阳性对照：证明这棵树真的含它），再打归档、
断言归档字节里**两个针的字节序列都不存在**；最后断言 `node_credential=***` 与 `token=***` **在**——
证明是 mask 干了活，而不是整行被丢掉。

**真机探针**（读数见下）：先用一条含**全部五个**标记模式（`token=`/`password=`/`client_secret`/
`authorization:`/`cookies:`）的合成串确认模式表抓得住 ⇒ **5/5**；再对真归档扫描 ⇒
**0 命中 / 1593 字节 / 4 条目**，两个替换进去的凭据串各自 `present=false`。

**这个「0 命中」的分母要说清**：它证明的是「真机上这一刻的两个树里没有任何一条被这五个模式抓住」——
是**模式**的分母，不是「真日志里真的埋了针」的分母。「埋针再证明抓得住」那一半由上面的单测承担，
它在真字节上跑。两半合起来才是完整的分母。

### 上限表（`Caps`，默认值即出货值）

| 上限 | 值 | 到边时 |
| --- | --- | --- |
| 每文件行数 | 20 000 | 从**尾部**取（`reader::tail`，多读一行好区分「正好到顶」），条目自报 `truncated` |
| 每文件字节 | reader 的 `TAIL_MAX_BYTES` | 同上，两道限长取先到的那道 |
| 条目名 | 128 字节 | 进 `omitted: name_too_long`：**改过名的日志是没人找得到的日志** |
| 日志载荷 | 32 MiB | 后续条目进 `omitted: archive_full`，已在里面的**留着** |
| 失败摘要 | 50 条 / 64 KiB | `truncated: true`，摘要自己的上限，免得一行超大记录背走整个归档 |

**载荷上限的方向是承重的**：`reader::list` 是**新在前**，所以先填满载荷的是**最近**的那批，
被上限丢掉的是**最早的历史**。反过来读——「留下这周开头、丢掉报告针对的那一个小时」——
是本模块**唯一一种仍然产出一个看着合理的归档**的失败方式，所以用例钉的是**丢哪一端**，
不是只钉「丢了东西」。变异 **d05**（把列出顺序反转）被断言 `entries` **精确顺序**的用例打掉——
本轮是 `a_media_file_inside_a_subdirectory_of_the_tree_is_not_reachable`，
上一轮（该用例加入前）是 `both_trees_are_named_after_their_source…`；两条判据都成立。

### 真机读数（探针，**保留**为常驻 ignored 用例）

`cargo test --offline commands::diagnostic::probe::probe_real_machine -- --ignored --nocapture`：

```
PROBE created_at=2026-09-24T23:46:15
PROBE desktop tree=…/src-tauri/.local/logs
PROBE agent   tree=/Users/aqiuye/Library/Logs/WTMedia/Agent
PROBE archive=…/Downloads/wt-media-diagnostic-20260924-234615.tar.gz bytes=1593 sha256=87159bd6…
PROBE entries=4 omitted=0
PROBE   logs/desktop/desktop.log text=247 source_bytes=248 truncated=false
PROBE   logs/agent/agent.log text=1673 source_bytes=1674 truncated=false
PROBE   logs/agent/error.log text=0 source_bytes=0 truncated=false
PROBE   logs/agent/task.log text=0 source_bytes=0 truncated=false
PROBE failures source=Some("logs/agent/task.log") records=0 truncated=false
PROBE scan control: the pattern matches 5/5 markers in a synthetic string
PROBE scan of the archive: 0 marker hits over 1593 bytes, 4 entries
PROBE   probe-launch-token-value: present=false
PROBE   probe-node-credential-value: present=false
PROBE read-back 6 entries: summary.json 937 / manifest.txt 877 / logs/desktop/desktop.log 247 /
                           logs/agent/agent.log 1673 / logs/agent/error.log 0 / logs/agent/task.log 0
PROBE checksum file: 87159bd6…  wt-media-diagnostic-20260924-234615.tar.gz
```

探针**读回来的 6 条**与归档里应有的 6 条一致（2 个信封 + 4 个日志），校验文件的首字段与归档的 sha256 逐字符相同。
真机两棵树**根不同**（开发树 `.local/logs` 与装机树 `~/Library/Logs/WTMedia/Agent`）——这是「两个来源确实是两个来源」的第二次对账。

**探针保留为常驻 ignored 用例**（`#[ignore]`，要跑得显式 `--ignored`）。这与 T-05/T-06 的「跑完即撤销」**不同**，
所以登记：理由是这个探针**只读（写进临时目录的替身 HOME）**、而且它是唯一一条能证明
「四件事真的来自一台真机器的真目录」的路径；撤销它等于只剩临时目录里的合成树。
`cargo test` 默认不跑它，计数里它永远是那 1 条 `ignored`。

### 三处只有「跑起来」才能发现的缺陷

| # | 缺陷 | 谁发现的 |
| --- | --- | --- |
| 1 | **落点目录可能不存在**（真机 `…/.local/data` 不是目录）：探针报 `could not be written to: not a directory` | 探针 |
| 2 | **manifest 里那句脱敏声明被换行拆成两段**（一个多余的 `\n` 落在 Rust 续行前） | 探针（读回 manifest 正文时看到） |
| 3 | **`bundle_files` 没有对条目文本再脱敏**：手工构造的条目能把凭据带进归档 | 单测（`the_credential_is_masked_even_in_the_field_the_agent_answered` 首跑即红） |

第 1 条的修法是 T-03 定的规矩（读者只问在哪，写者负责准备）：`export` 在写之前 `create_dir_all` 它自己选的那个目录，
失败映射成 `DiagnosticError::Target`。

**两处由变异表反推出来的覆盖缺口**（不是缺陷，是「没有用例在读这个字段」）：

- `AgentFacts::state()` 是同一套词汇的**第三处拼写**，只有命令在用，没有任何用例读它 ⇒
  改成让 `summary()` 也从它取值，一处定义、一处被钉（变异 **d19**）。
- 摘要的**摘要值**没有任何独立读者：`the_checksum_file_names_the_archive_and_holds_its_digest` 是**自洽**的
  （拿 `written.sha256` 跟 `write_archive` 自己写的那一行比），任何「确定性函数」都能通过它。
  新增 `the_digest_is_the_digest_of_the_file_by_an_independent_reader`：**调用操作系统的 `shasum -a 256`**
  （没有则试 `sha256sum`，都没有就打印前提失败并返回——不可用的证人不算通过）做第二个说法。
  变异 **d18**（摘要只覆盖零个字节）首轮只被「did not compile」判灭，换成 `std::io::empty()` 后可编译，
  随即被这条用例真实打掉。

### 先红的口径

新代码（三个新模块）实现前没有可跑的壳：`diagnostic.rs` 第一次能编译时用例就已经在文件里了，
所以**本 Task 不宣称有「先失败的验证」那一轮**。新代码的红的判据全部由下面的变异表承担——
`ImportError` 式的红什么都证明不了（T-05/T-06 已定过这条口径）。

## 计数（只增不减）

| 侧 | 起点（T-06 收尾） | 现在 | 差额 |
| --- | --- | --- | --- |
| desktop | 276 passed | **314 passed** | **+38**（0 删除，0 skipped；另有 1 ignored） |

逐件对账：`diagnostic` 28 + `commands::diagnostic` 4 + `dto::diagnostic` 2 = 34（新模块），
`app_paths` +1、`config` +1、`logging::backend` +1、`paths` +1 = 4（改动文件），34+4 = 38；
`commands::diagnostic` 另有 1 条 `#[ignore]` 的探针，**不计入 passed**。
（`cargo test diagnostic` 报 34 是因为过滤串是子串匹配，它同时选中后两个模块的用例。）

非测试构建警告：`cargo check` 计 **28 行 = 27 条 + 1 行汇总**，**与 T-05/T-06 相同**。
**逐个按文件归位后没有一条落在本次任何文件上**（全部来自 `settings.rs`、`rolling.rs`、`storage.rs`、
`cleanup.rs` 与 `filesystem`/`secure_store`/`system`/`updater` 四个空壳）。

## 实现变异：32 行，32 灭，0 等价

三组各自先跑**阴性对照**（未变异的字节上同一条命令必须报 `0 failed`），三组全部通过；
每组跑完**断言文件逐字节还原**，**并且**再跑一次同一条命令证明留下的是一棵**绿的**树。

| 组 | 目标 | 过滤 | 行数 | 阴性对照 | 结果 | 还原 sha256(前 12) |
| --- | --- | --- | --- | --- | --- | --- |
| diag | `diagnostic.rs` | `diagnostic::tests::` | 19 | 34 passed / 0 failed | **19 灭** | `426ba2458357` |
| cmds | `commands/diagnostic.rs` | `commands::diagnostic::tests::` | 6 | 4 passed / 0 failed | **6 灭** | `d08373452616` |
| dto | `dto/diagnostic.rs` | `dto::diagnostic::tests::` | 7 | 2 passed / 0 failed | **7 灭** | `c98fa6557d72` |

原始输出：`/tmp/chg058/t07/mutations-{diag,cmds,dto}.out`。**32 行全部被真实用例打掉，没有一行靠「did not compile」，
也没有登记为等价的存活行。**

### 变异表：四处**只有这张表能发现**的覆盖缺口

写这张表之前先问「哪一条规则**没有**用例在读」，问出来四件事（都已在上面登记并补齐）：
`AgentFacts::state()`、摘要值的独立读者、三种省略理由里没有一条被读的 `name_too_long`、
以及 dto 里 `bytes` 与 `source_bytes` 在夹具里**恰好相等**（相等就看不出差异）。
剩下的行是「同一条规则换一种错法」，逐行结果如下（编号与原始输出一致）：

#### diag（19 灭）

| # | 变异 | 打掉它的用例 |
| --- | --- | --- |
| d01 | `mask` 变成恒等 | `the_export_reports_the_node_id_and_never_the_credential` |
| d02 | `bundle_files` 不再复脱敏 | `the_credential_is_masked_even_in_the_field_the_agent_answered` |
| d03 | 条目名上限不生效 | `a_name_over_the_cap_is_left_out_rather_than_shortened` |
| d04 | 日志载荷上限不生效 | `the_log_payload_stops_at_its_ceiling_and_registers_everything_after_it` |
| d05 | 列出顺序反转（丢掉**最新**的而不是最旧的） | `a_media_file_inside_a_subdirectory_of_the_tree_is_not_reachable` |
| d06 | 超长时留**开头**而不是结尾 | `a_file_longer_than_the_cap_is_the_end_of_the_file_and_says_so` |
| d07 | `truncated` 永不为真 | 同上 |
| d08 | 正好到顶也当成窗口 | `a_file_that_ends_at_the_cap_exactly_is_not_reported_as_a_window` |
| d09 | `unreadable` 换拼写 | `the_wire_key_sets_are_pinned`（dto 组） |
| d10 | `archive_full` 换拼写 | `the_manifest_lists_every_entry_and_every_omission` |
| d11 | `name_too_long` 换拼写 | `the_wire_key_sets_are_pinned`（dto 组） |
| d12 | 失败摘要取 INFO 及以上 | `the_failure_summary_is_the_warn_and_louder_records` |
| d13 | 失败摘要的上限不生效 | `the_failure_summary_stops_at_its_cap_and_says_so` |
| d14 | 失败日志名换拼写 | `the_export_reports_the_node_id_and_never_the_credential` |
| d15 | 归档被**覆盖**而不是新建 | 同上 |
| d16 | 撞名的后缀恒定 | `the_attempts_are_bounded` |
| d17 | 条目名检查全部放行 | `a_name_that_is_not_one_component_is_refused` |
| d18 | 摘要不覆盖**任何**字节 | `the_digest_is_the_digest_of_the_file_by_an_independent_reader` |
| d19 | `AgentFacts::state` 换拼写 | `an_unreachable_agent_is_a_stated_state_not_a_failed_export` |

**d05 的判据这一轮换了**：上一轮（媒体用例加入前）打它的是 `both_trees_are_named_after_their_source…`，
这一轮是新的媒体用例——它断言 `entries` 的**精确顺序**，两条条目一反转就红。两条判据都成立，如实按本轮记录。

#### cmds（6 灭）

| # | 变异 | 打掉它的用例 |
| --- | --- | --- |
| c01 | 绑定凭据不加入 mask 名单 | `an_empty_secret_is_dropped_and_a_real_one_is_kept` |
| c02 | 空 secret 保留 | 同上 |
| c03 | 落点恒为数据根 | `the_export_goes_to_downloads_when_there_is_one_and_the_data_root_when_there_is_not` |
| c04 | `Downloads` 不要求是目录 | 同上 |
| c05 | 配置 id **列举**而不是计数 | `the_agent_fields_are_what_it_answered_and_never_the_profile_list` |
| c06 | 缺的字段变成空串 | 同上 |

#### dto（7 灭）

| # | 变异 | 打掉它的用例 |
| --- | --- | --- |
| w01 | `path` 线上换名 | `the_wire_key_sets_are_pinned` |
| w02 | `sha256` 线上换名 | 同上 |
| w03 | 空的 `omitted` 不上线（省掉 `[]`） | `an_empty_report_still_carries_every_key` |
| w04 | 条目的 `truncated` 线上换名 | `the_wire_key_sets_are_pinned` |
| w05 | `failed_records` 恒为 0 | 同上 |
| w06 | 条目的 `bytes` 取源文件大小 | 同上 |
| w07 | 归档的 `bytes` 取条目之和 | 同上 |

（过滤串 `diagnostic::tests::` 是**子串匹配**，所以 diag 组同时选中了后两个模块的用例——
这也是 d09/d11 被 dto 用例打掉的原因；每一行的灭都发生在自己那一轮里，不影响归因。）

### 变异表的两处**工具缺陷**（都是本次发现并修掉的）

| 缺陷 | 症状 | 修法 |
| --- | --- | --- |
| **还原走 `shutil.copy2`，连源文件的 mtime 一起恢复**——比上一次变异建出的产物**旧** ⇒ cargo 认为树是干净的，于是**用上一次变异的产物**跑这一次 | 组跑完报 7/7 灭，但紧接着一次 `cargo test` 报 `the_wire_key_sets_are_pinned` **FAILED**，而那个源文件的摘要正是**通过**的那一份 | 还原后用**墙钟**把 mtime 推到产物之后（不是「上一次 +2s」——那个相对量同样会落在产物之后），并在组末尾**再跑一次阴性对照**，把「留下的是一棵绿的树」也变成断言 |
| **信号不还原**：`finally` 在 SIGTERM/SIGINT 下不执行 | 一次被我停掉的运行在工作区留下了 **d16**（`n + 1` → `2`）的源码；此后读到的文件是**变异过的**，但看起来像真的 | 注册 `SIGINT/SIGTERM/SIGHUP` 处理器，收到就还原并退出 |

两处都要说清归属。**第一条是本 Task 自己引入的**：T-06 的 `write_mutated` 本来就用墙钟（`time.time() + 2`），
是我为了「逐字节还原」改用 `shutil.copy2`，才把源文件的旧 mtime 一起带了回来——「逐字节相同」与「构建系统认为它变了」
是两件事，我只断言了前一件。**第二条 T-06 同样有**：那次运行没有被中途打断，所以没有留下变异源码，
但它的收尾同样只断言了 `byte-identical`，没有断言「留下的树是绿的」。修复后重跑本 Task 的表时两条断言都在。

## 边界登记（不静默吸收）

1. **探针保留为常驻 `#[ignore]` 用例**，与 T-05/T-06「跑完即撤销」先例不同。理由见上（只读 + 唯一一条真机器路径）。
2. **启动 token 进入 `DiagnosticHost::secrets` 是一条 `main.rs` 的接线行，没有用例能断言它**。
   可断言的都断言了（`secrets()` 的合并规则、空值丢弃、绑定凭据加入），
   而「`main.rs` 真的把同一个 `Vec` 交给了 sink 和命令」在类型上成立、在用例上不可达——
   **登记为证据边界，不宣称已测**。`main.rs` 的注释里也写明了这一点。
3. **落点决定（D-13）**：`~/Downloads` 存在时用它，否则用本组件数据根，且**写前 `create_dir_all`**。
   这不是安全边界（包本身就是脱敏的），是一个**便利性决定**：人们要附文件时看的就是那里。
4. **内容边界（D-14）**：`bit_profile_ids` 只计数；`main_user_id` 有意包含；失败摘要只取 **warn 及以上**；
   直接躺在日志树里的陌生文件**收进来**（脱敏、限长）。
5. **条目文本比源文件少 1 字节**（真机：247 vs 248，两侧日志都一样）：条目文本是**按行 join** 的，
   文件末尾那个换行不属于任何一行。manifest 因此同时给两个数——「窗口是多少」和「源文件多大」都要能读到。
6. **`reader::list` 返回的是 `Ok(vec![])`（目录不在）还是 `Err`（读不出来）**，这个区分一直活到归档里：
   「还没有日志」与「你的日志在那儿但我读不到」。T-07 没有改变它，也没有把它抹平。
7. **`#[tauri::command]` 展开成带 `#[diagnostic::on_unimplemented]` 的项**，那是一个在**该作用域里解析**的工具属性：
   命令模块里 `use crate::diagnostic::{self, …}` 会把名字 `diagnostic` 绑成一个**模块**，
   于是展开报 `E0433: cannot find 'on_unimplemented' in 'diagnostic'`。
   修法是不导入 `self`、一律走全路径。这是踩过的坑，写在 `commands/diagnostic.rs` 的模块注释里。
8. **`AppPaths` 与两个命令体（收 `State`）没有单测**，沿 `commands::agent`/`commands::storage`/`commands::cleanup` 的先例：
   可断言的部分抽成纯函数（`secrets`/`output_directory`/`agent_fields`/`host_facts`/`export` 的入参），
   命令体只剩几行接线。真机覆盖由上面的探针提供。
9. **`the_digest_is_the_digest_of_the_file_by_an_independent_reader` 依赖本机的 `shasum`/`sha256sum`**（本机两者都在：
   `/usr/bin/shasum`、`/sbin/sha256sum`）。两者都不在时它打印**前提失败**并返回，不假装通过——
   也就是说这条断言在那种机器上**不覆盖**，而不是**通过**。
10. **T-06 登记的 13 个格式化残留文件本次仍未动**。逐个核验：11 个在「去掉所有空白 + 去掉收尾逗号」后与 `HEAD` 逐字符相同；
    余下 2 个（`commands/agent.rs` 长度完全相同、仅 `use` 组重新分行；`sidecar/drain.rs` 把一个 match 臂的
    `{…}` 收成 `…,`）逐行看过，同为排版。本次提交**只 add 本 Task 的路径**。
