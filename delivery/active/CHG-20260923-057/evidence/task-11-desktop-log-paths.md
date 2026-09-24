# 证据 — T-11 Desktop 日志目录解析（纯函数 + 可写性判定）

范围：裁定「Desktop 路径：`~/Library/Logs/WTMedia/Desktop`；dev `<repo>/.local/logs`」，
以及收窄说明（通用运行目录 `AppPaths` 顺延，`paths.rs` 的配置定位那半**行为逐字不变**）。

提交：`wt-media-desktop`（`src/logging/` 新增、`main.rs` 加 `mod logging;`、`.gitignore` 补 `.local/`）。

---

## 1. 交付形态：纯规则 + 一处薄 IO

| 项 | 形态 |
|---|---|
| `logging::paths::directory(home, environment, manifest_dir)` | **纯函数**，三个输入全部注入，无文件系统、无真实 `$HOME` |
| `logging::paths::prepare(...)` | 唯一的 IO：`create_dir_all` + **真实写探测**，返回 `Result<PathBuf, LogDirectoryError>`，**永不 panic** |
| `LogDirectoryError` | 带 `path` + `io::Error`，`Display` 可读，不含任何凭据（日志目录是目录路径） |

`home` 之所以是参数而不是在函数里读环境：会读 `$HOME` 的函数没法回答「给我**这个** home 你会怎么做」，
而测试一旦真去读，写的就是跑测试的那个人的家目录。

两套布局**互斥**且由测试钉住（见 §3 的 M2/M3）：生产读 `home`、**绝不**读 manifest 目录；开发读 manifest
目录、**绝不**写进真实 `home`。这不是修饰——发行版写进「碰巧构建它的那个目录」会把文件撒满机器，
开发运行写进真实 `Library/Logs` 会把开发草稿混进安装版日志里。

## 2. 写探测：为什么 `create_dir_all` 不够

计划要求「不可写目录**返回错误值而非 panic**」。关键在于：**目录已存在时 `create_dir_all` 返回 `Ok`**，
无论它是否可写——只靠它，只读目录会被报成可用，第一条真实记录才发现不是。

故 `prepare` 做两件事，且第二步是**真的写**：

```
create_dir_all(dir)?            → 失败 → LogDirectoryError { path, reason }
probe_write(dir)?               → 失败 → LogDirectoryError { path, reason }
```

`probe_write` 建一个 `.wt-media-write-probe-<pid>` 再立刻删掉；成功的路径上不留任何东西（有专门用例断言
目录里没有 `PROBE_PREFIX` 开头的残留）。

**只读目录那一臂真的在本机跑了**：`--nocapture` 下**没有**出现 skip 行，即前提成立；断言里还含
`PermissionDenied` 这一条，所以「失败原因是只读」也是被验的，不只是「失败了」。skip 的分支确实存在
（特权进程会忽略 mode 位），它是**打印出来**的而不是静默通过。

## 3. 变异表：控制臂先绿，8 个变异逐个红

探针 `/tmp/t11-mutation-probe.py`：逐次改**真实模块**的一处，跑整套 `logging::paths` 用例，记下谁死了。
原文本在 `finally` 里还原，并用 sha256 **核对**（不是假定）——两次跑分别报 `restored=True`。

```
mutation | prod_home | dev_manifest | one_input | component | prepare_creates | repeatable | no_probe | stale_probe | not_a_dir | read_only
0 控制：未变异              | green ×10
M1 生产去掉组件目录层        | RED | .   | .   | RED | . | . | . | . | . | .
M2 生产建在 manifest 目录下  | RED | .   | RED | .   | . | . | . | . | . | .
M3 开发建在 home 下          | .   | RED | RED | .   | . | . | . | . | . | .
M4 开发目录拼错（logs→log）  | .   | RED | .   | .   | . | . | . | . | . | .
M5 去掉写探测（只留建目录）  | .   | .   | .   | .   | . | . | . | RED | . | RED
M6 探测文件不删             | .   | .   | .   | .   | . | . | RED | RED | . | RED
M7 吞掉 create_dir_all 失败  | .   | .   | .   | .   | . | . | . | . | RED | .
M8 探测改用 create_new      | .   | .   | .   | .   | . | . | . | RED | . | .
```

**每条规则都有用例守着**（8/8 红），且没有一条用例是永远绿的。

### 3.1 探针查出的两个缺口（都已补，不是记下来了事）

- **M8 起初全绿 → 补用例**。`create_new` 与 `create` 在这个套件能构造的所有路径上表现一致，因为探测
  文件总会被删掉。差别只在**崩溃后留下探测文件**时：`create_new` 会报 `AlreadyExists`，把一个好目录
  报成不可用，且**只在崩溃后的第一次启动**——恰恰是最可能被排查的那次。这正是本模块 docstring
  自己承诺的场景，所以补了 `a_stale_probe_file_does_not_make_the_directory_unusable`（种一个陈旧
  探测文件 → 仍须 `Ok` 且被清掉），M8 随即转红。
- **M7 起初全绿，先当作「等价变异」，一量发现不是**。原断言只查「有错误」。改为断言**错误的
  `kind`** 后需要知道真实值——实测 macOS 上是 **`AlreadyExists`**（`create_dir_all` 撞到一个被普通
  文件占住的路径），而绕过它、让探测去撞同一路径得到的是 `NotADirectory`。所以 M7 **不是**等价的：
  它把根因换成了下游原因。断言写实测到的 `AlreadyExists` 后 M7 转红。

### 3.2 M6 多红一条，根因量出来了

M6（不删探测文件）除 `prepare_leaves_no_probe_file` 外还红了只读那一臂。**先证根因**：
在只读目录里**打开一个已存在的可写文件是成功的**（目录的 mode 位挡的是新建条目），只有 `remove_file`
会失败。M6 恰好删掉的就是那个 `remove_file` ⇒ 探测整体报成功 ⇒ 只读目录被判为可用，用例按设计红了。

所以这条额外的红是**诚实耦合**：`remove_file` 正是把「目录可写」与「不可写目录里恰好有个可写文件」
区分开的那一步。登记而非掩盖。

## 4. 逐字边界

- **`paths.rs` 零改动**：本 Task 只新增 `src/logging/`，配置定位那半（`candidates`/`locate`/`file_text`）
  一个字符没动——「`paths.py`/`paths.rs` 是落盘位置唯一事实源」的既有宣称不受影响。
- **通用运行目录 `AppPaths` 不交付**（裁定只固定了 Desktop 的日志路径），登记为未交付，
  不发明一份无权威的目录规范。
- **Windows 未取证**：`home/Library/Logs/...` 是 macOS 形状，本 Task **不猜**一个 Windows 布局；
  按 CHG-056 先例登记为未取证。
- `.gitignore` 补 `.local/`（放在目录类模式一起，`target/` 之后）：`git check-ignore -v` 回报
  `.gitignore:4:.local/` → `src-tauri/.local/logs/probe.tmp`，**规则命中且是这一条**（阳性对照）；
  `*.log` 那条仍然有效。

## 5. 测试与警告读数

| 指标 | 改前 | 改后 |
|---|---|---|
| `cargo test --workspace` | **68 passed; 0 failed** | **78 passed; 0 failed**（+10：4 条纯规则 + 6 条 IO/边界） |
| `cargo build` 条目级警告 | 4 | **12** |
| `cargo clippy --workspace --all-targets`（与 T-10 同一条命令的计数法） | 10 | **18** |

**+8 全部是同一件事**：新模块的 8 个条目（`APPLICATION_DIR`、`COMPONENT_DIR`、`DEVELOPMENT_DIR`、
`PROBE_PREFIX`、`directory`、`LogDirectoryError`、`prepare`、`probe_write`）在**非测试构建**里还没有
调用方——`dead_code`，因为调用方（`main` 的接线）按计划在 **T-15**。

**登记为待验的期望，而不是承诺**：T-15 接线完成后，这两个数字都应回到改前的 4 / 10。T-15 收尾时会
**实测**这一点——警告数不降，说明模块没被真正接上，那是个比缺测试更严重的信号。
