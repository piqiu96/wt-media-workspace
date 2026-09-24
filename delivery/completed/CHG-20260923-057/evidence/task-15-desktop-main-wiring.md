# 证据 — T-15 Desktop 接进 `main`（唯一初始化入口）

范围：计划本条——在 `bootstrap::resolve` 之后、启动摘要之前接上 subscriber：
①新增 `logging/setup.rs`（`home`/`manifest_dir`/`Environment` 全部**参数注入**，测试不解析真实 `$HOME`）；
②目录不可用 → 只 stderr、**仍启动**；③启动摘要经 subscriber 发出，成为开发态日志文件的**首条记录**（AC-02）。
两条本次实施裁定：**环境取构建期**（`bootstrap::build_environment()`，不取 `startup.config.environment`）、
**摘要里同时写出两个环境与落点**；`level="warn"` 一臂实测后如实登记。

提交边界：`wt-media-desktop`（`src-tauri/src/logging/setup.rs` 新增、`logging/{mod,backend}.rs`、
`src-tauri/src/main.rs`），**1 个 commit**。

---

## 1. 交付形态

| 处 | 内容 |
|---|---|
| `logging/setup.rs`（新） | `Plan`（`levels`/`limits`/`directory: Result<PathBuf, String>`/`configured_level`/两个 `Environment`）+ `plan()`（**所有决定**）+ `install(plan, secrets)`（**只剩装配与安装**）+ `Installed::summary()` |
| `plan()` / `install()` 拆分的理由 | subscriber **每进程只能装一次**，留在 `install` 里的判断**只能靠启动程序才够得着**；拆分不是装饰——本 Task 第一个变异（`install` 从 `config.environment` 解析目录）**整套 152 条用例全绿**（当时的口径）。见 §3 |
| 环境口径 | `levels`、`resolve_directory` 都取 **`build_environment`**；`Installed` 两个环境都带，`summary()` 只在二者**不一致**时写出 `环境 X（构建 Y）` |
| `main.rs` | 摘要的 emit 点改走 subscriber（`target = "desktop.startup"`）；`install` 失败（已被别人装过）才回落 `eprintln!("[wt-media-desktop] …")` |
| 顺序 | token 生成**提前**到日志之前（sink 要拿它的值做掩码），随后 `plan` → `install` → 摘要。摘要因此是**首条记录**，也是一条 `INFO` |
| `logging/backend.rs` | `note` 由私有改 `pub(crate)`（`setup` 走同一个通道）；`logging/mod.rs` 加 `pub mod setup;` |

## 2. 真机三臂（每臂都是**真实二进制**，非单测）

命令统一为（`$BIN = target/debug/wt-media-desktop-shell`，每次先 `rm -rf src-tauri/.local/logs`）：

```bash
"$BIN" > /tmp/t15/armN-stderr.out 2>&1 &   # 8 秒后 kill -TERM
```

### 臂 1（AC-02）：开发态布局，出货文件

```
still alive after 8s: yes
stderr:
2026-09-24T10:06:55Z [INFO] desktop.startup: 配置来自开发树 resources/；日志目录 /Users/…/wt-media-desktop/src-tauri/.local/logs；级别 DEBUG（配置 auto）；环境 production（构建 development）
文件：src-tauri/.local/logs/desktop-20260924-1.log，249 字节
首条记录 == stderr 那一行（逐字相同）
```

三条判据同时成立：**stderr 与开发态文件都有摘要**、**文件首条即摘要**、**级别 DEBUG 且 `auto` 写出了配置来源**。
这是「环境取构建期」这条裁定的**行为证据**：debug 构建跑出货文件时 `config.environment == Production`，
若目录/级别跟着它走，这里会是 `~/Library/Logs/WTMedia/Desktop` 与 `级别 INFO`——两处都不是。

### 臂 2（AC-05 第二臂）：日志目录被占住

```
before: printf 'occupied\n' > src-tauri/.local/logs      # 用普通文件占住目录位
stderr:
desktop.log: log directory /Users/…/src-tauri/.local/logs is unusable: File exists (os error 17)
2026-09-24T10:07:02Z [INFO] desktop.startup: 配置来自开发树 resources/；日志目录不可用（log directory … is unusable: File exists (os error 17)），本次只写 stderr；级别 DEBUG（配置 auto）；环境 production（构建 development）
still alive after 8s: yes
占位文件仍在（内容 "occupied" 未被改动）
```

**不 panic、不退出、摘要在 stderr、原因写进摘要**（第一行是 `backend::note` 的通道，第二行是摘要本身）。
「目录不可用是**值**不是错误」这条设计在这里被真实进程证到。

### 臂 3：`level = "warn"` 与对照臂 `level = "info"`

两臂用 `WT_MEDIA_DESKTOP_CONFIG` 指向出货文件的副本，**只改 `level` 一行**：

| 臂 | `level` | stderr 的 `desktop.startup` 条数 | 日志目录 | 文件 |
|---|---|---|---|---|
| 实验 | `warn` | **0** | 建了（`prepare` 的职责）但**空的** | **0 个** |
| 对照 | `info` | **1** | 建了 | `desktop-20260924-1.log` 255 字节 |

对照臂证明「实验臂的 0 条」是级别造成的，不是 sink 坏了（该臂的摘要逐字含 `配置 info`）。
**实测比计划写的后果更宽**：计划只写「不建文件」，实际是**两个 layer 共用同一个 filter**，
故严于 INFO 的级别**同时**让 stderr 静默——`desktop.log` 一条没有，终端也一条没有，只有那一行
`backend::note`（它不走 subscriber，是直写 stderr 的通道）之外的**零**输出。已登记见 §5。

## 3. 变异表：两轮、控制行先绿

探针 `/tmp/t15_mutate.py`（第一轮 12 个）与 `/tmp/t15_mutate2.py`（第二轮 10 个），
逐次改**真实文件**的一处、每次从 pristine 副本还原，跑 `cargo test --workspace`
（第一轮在 152 条上跑、第二轮在 153 条上跑，两轮控制行都先绿）。

```
第一轮 控制行 → 153 passed / 0 failed
M1  install 用 config.environment 解析目录      → SURVIVED   ← 拆分前，见 §3.1
M2  auto 忽略构建环境（恒 production）           → RED（plan 的环境两向断言）
M3  trace → DEBUG                              → SURVIVED   ← 见 §3.2
M4  off → INFO                                 → SURVIVED   ← 见 §3.2
M5  level_name 改用 Display（小写）              → RED（摘要用例）
M6  limits_of 忽略配置（恒 SHIPPED）             → RED（预算用例）
M7  摘要恒带「构建 …」                          → RED（摘要用例）
M8  无 HOME 的 Err 换文案                       → RED（等值断言）
M9  摘要丢掉不可用原因                          → RED（摘要用例）
M10 filter_of 把 auto 也当级别                  → RED（auto 是哨兵）
M11 main 不把 token 交给掩码                    → SURVIVED   ← 见 §3.3
M12 main 传生效环境而非构建环境                  → SURVIVED   ← 见 §3.3

第二轮（拆分后重跑）控制行 → 153 passed / 0 failed
N1  plan 用 config.environment 解析目录         → RED（plan 两向断言 + 目录不可用那条）
N2  plan 用 config.environment 取级别           → RED（plan 两向断言）
N3  trace → DEBUG                              → RED（手写对表）
N4  off → INFO                                 → RED（手写对表）
N5  warn → ERROR                               → RED（正向臂）
N6  plan 不带配置的预算（恒 SHIPPED）            → RED（plan 的预算断言）
N7  plan 恒报 configured_level = auto           → RED（plan 的显式级断言）
N8  main 不把 token 交给掩码                    → SURVIVED   ← 见 §3.3
N9  main 传生效环境而非构建环境                  → SURVIVED   ← 见 §3.3
N10 已被装过那条 note 换文案                     → SURVIVED   ← 见 §3.3
```

### 3.1 M1 起初存活 ⇒ 拆出 `plan`

M1 把 `install` 里的 `resolve_directory(build_environment, …)` 改成 `config.environment`，
**整套 152 条全绿**：`install` 装的是**进程级** subscriber，测试碰不到它，而那正是该规则住的地方。
这不是「用例写少了」，是**位置错了**——决定必须住在测试够得着的地方。
修法：`Plan` + `plan()` 承担所有决定（`levels`/`limits`/`directory`/`configured_level`/两个环境），
`install(plan, secrets)` 只剩装配与安装，**连 `&DesktopConfig` 都不再拿**（拿不到就写不出这个错）。
拆分后 N1/N2/N6/N7 四个变异各自转红，控制行仍绿。

### 3.2 M3/M4 起初存活 ⇒ 手写对表

`every_accepted_token_maps_and_auto_is_the_sentinel` 的正向臂是 `assert_eq!(configured.default, filter_of(token))`
——**两侧都从 `filter_of` 推导**，把 `trace` 改成 DEBUG 时两侧一起变。
与 T-14 的 M6（词表删 `trace`）**同一形状的通病**，第二次出现：

| | 驱动源 | 修法 |
|---|---|---|
| T-14 M6 | 断言与报错文案都从 `LOG_LEVELS` 推导 | 常量用手写值钉死（`len == 6` + `join(" ")`） |
| T-15 M3/M4 | 期望值与实际值都从 `filter_of` 推导 | 新增 `PINNED_LEVELS` 手写对表 + `join(" ")` 把词表绑回 `config::LOG_LEVELS` |

新用例 `every_accepted_token_maps_to_this_filter` 逐对断言「token → 具体 `LevelFilter`」；
既有 `every_accepted_token_maps_and_auto_is_the_sentinel` 里那半「其余 target 跟随配置级别」也改读手写表
（不再读 `filter_of`），故它仍能红。N3/N4/N5 随即红，控制行仍绿。

### 3.3 三个幸存者：`main` 的两个实参与「已被装过」那条臂

| 变异 | 为什么整套用例打不掉它 | 它由什么守 |
|---|---|---|
| N8 `main` 不把 token 交给掩码 | `main.rs` 不在任何测试的射程内；而**真实启动的 grep 分母是 0**——今天没有任何一条记录会携带 token，所以「日志里没有 token」这句话对任何实现都成立 | T-13 的 **sink 级**用例（`assemble` 拿到的值一定被掩）+ 调用点只有一行。**不是「已验证」，是「无处可验」** |
| N9 `main` 传生效环境 | 同上，`main.rs` 打不到 | **臂 1 的真实启动**：传生效环境会让摘要变 `环境 production`（无「构建 development」）、目录变 `~/Library/Logs/WTMedia/Desktop`，与实测逐字不符 ⇒ 该变异被**真实进程**打掉，不是被用例 |
| N10 已被装过那条 note 的文案 | 该分支在本程序里**不可达**（没有任何别的代码装 subscriber），既没有用例也没有启动能触发 | 无。如实登记为**未覆盖分支**：保留它是为了「日志问题不得让启动炸掉」，不是为了有一条路径在跑 |

**第二条的分母是显式的**：臂 1 给出两处**可分辨**的事实（目录、级别/环境文案），两处都与 N9 的预期不符。

## 4. 读数

| 指标 | 改前（T-14 后 HEAD） | 改后 |
|---|---|---|
| `cargo test --workspace` | **147 passed; 0 failed** | **153 passed; 0 failed**（+6） |
| `cargo build` 条目级警告 | 93 | **9** |
| `cargo clippy --workspace --all-targets` | 97 | **13** |

新增 **6** 条用例：`setup.rs` 原有 **5** 条（环境两向那条在拆分后改由 `plan` 承担并改名为
`the_plan_follows_the_build_not_the_effective_environment`，是**改名不是新增**：5 条 = 环境两向 / 目录不可用 /
token 映射 / 预算 / 摘要）+ 手写对表 **1** 条。147 + 5 = 152（拆分前实测），+ 1 = **153**。

### 4.1 与登记的待验期望不符：期望 4/10，实测 **9/13**

T-11/T-12/T-13/T-14 四处登记的都是「接线后应回到 **4 / 10**」。实测 **9 / 13**，差 **5**，
且这 5 条**逐条可点名**——全是 `rolling.rs` 现在**只在测试里**被引用的项：

```
$ touch src-tauri/src/main.rs && cargo build 2>&1 | grep -E '^warning: [a-z]'
constant `DEFAULT_MAX_FILE_BYTES` is never used    rolling.rs:49
constant `DEFAULT_RETENTION_DAYS` is never used    rolling.rs:53
constant `DEFAULT_TOTAL_BYTES` is never used       rolling.rs:57
associated constant `SHIPPED` is never used        rolling.rs:254
method `open_path` is never used                   rolling.rs:479
（另 4 条是既有桩：filesystem / secure_store / system / updater 的 `never constructed`）
```

**根因是 T-14 的一处正确改动**：登记的期望隐含「`setup` 用 `Limits::SHIPPED` 建 writer」，
而 T-14 按计划把**配置文件**变成了四个数字的来源（`limits_of(config)`），于是
`SHIPPED`/三个 `DEFAULT_*` 只剩测试在用（分别是 `config.rs` 的漂移断言、`rolling.rs` 自己、
和 `setup.rs` 的 `assert_eq!(limits_of(&config), Limits::SHIPPED)`）。
`open_path` 本来就只被 `rolling.rs` 的用例调用。
**这 5 条是「常量与访问器只在测试里被引用」的正常结果，不是接线没接上**——反证有三条：
①计数 93 → 9 说明三模块的调用方**确实接上了**（否则仍是 93）；②臂 1 真的建出了文件（走的就是 `Writer`）；
③clippy 的 13 − 9 = 4 全是**既有**项（`main.rs:45` items after a test module、`account.rs` ×2 的 `?`、
`drain.rs:212` 的字面 bool 断言），**本 Task 新增代码 0 条 lint**。

## 5. 未覆盖项与如实登记

- **`level` 严于 INFO 时连 stderr 一起静默**（臂 3 实测，计划只预测「不建文件」）：目录由 `prepare` 建、
  文件因惰性而**不建**（T-12 的设计），而 stderr 层与文件层**共用同一个 filter** ⇒ `warn` 臂下
  「启动摘要」这条 INFO 记录**两个出口都没有**。合法级别，行为如实登记，未因此禁掉任何级别。
- **stderr 的形态变了**：摘要此前是 `eprintln!("[wt-media-desktop] …")`，现在是**记录形态**
  `2026-09-24T10:06:55Z [INFO] desktop.startup: …`（前缀没了）。这是有意的：同一条行现在两处同形，
  且带上了时间与 target；只有 `set_global_default` 失败时才回到旧前缀。
- **N8/N9/N10 三个幸存者**（见 §3.3）：两个是 `main.rs` 的实参、一个是不可达分支。
  N9 由臂 1 的真实启动守（两处可分辨事实），N8 与 N10 **无验证手段**——登记而不是声称已覆盖。
- **`path::prepare` 建目录**：臂 3 的 `warn` 臂里目录**是建了的**（空目录），故「不建文件」与「不建目录」
  是两件事，本 Task 只声称前者。
- **Windows 日志布局未取证**（与 T-11/T-12/T-13/T-14 同一登记）。
- **`cargo fmt` 口径**：新增的 `setup.rs` 整文件跑过 `rustfmt`（它是本 Task 的新文件，没有既有脏行）；
  `main.rs` **未跑全文件格式化**（本仓不是 rustfmt-clean 的，T-13 已量化），只手改两处，diff 里没有
  一行与 T-15 无关的重排。核对方式：`git diff -U0 -- src-tauri/src/main.rs | grep '^-'` 只有那两行。

## 6. 复现命令

```bash
cd wt-media-desktop
cargo test --workspace                                   # 153 passed
python3 /tmp/t15_mutate.py                               # 第一轮 12 个：4 个起初存活
python3 /tmp/t15_mutate2.py                              # 第二轮 10 个：3 个幸存（同一批原因）
touch src-tauri/src/main.rs && cargo build 2>&1 | grep -cE '^warning: [a-z]'          # 9
cargo clippy --workspace --all-targets 2>&1 | grep -cE '^warning: [a-z]'              # 13

# 臂 1（AC-02）：开发态布局；
rm -rf src-tauri/.local/logs && target/debug/wt-media-desktop-shell
# 臂 2（AC-05 第二臂）：先 printf 'occupied\n' > src-tauri/.local/logs
# 臂 3：cp src-tauri/resources/desktop.production.toml /tmp/t15/{warn,info}.toml，
#        把 level 分别改成 warn / info，再 WT_MEDIA_DESKTOP_CONFIG=/tmp/t15/<臂>.toml 启动
```
