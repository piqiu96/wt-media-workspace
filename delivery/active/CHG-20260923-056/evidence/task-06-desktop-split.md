# Evidence: Desktop 拆分 main.rs（T-06）

- CHG: `CHG-20260923-056`
- Task: `T-06`
- Date: 2026-09-23 ～ 2026-09-24
- Type: refactor + test + mutation + command
- Status: PASS

## Purpose

T-06 把 `wt-media-desktop` 的 1570 行单文件 `main.rs` 拆成分层模块，且**不改行为**。
三类判据：

1. **搬家没有搬走行为**：「17 个命令体逐字搬迁」「9 个既有测试内容不变」是两句关于
   **字节**的话，故必须逐函数实测，而不是看着像就算了（§4）。
2. **搬家没有搬走接线**：`generate_handler!` 的 17 项**顺序与集合**必须逐字不变
   （Tauri 的命令注册顺序影响前端可见面，§3）。
3. **死代码真的死了，且删除带来的覆盖缺口要认**（§6）。

## Method

### 1. 提交序列

`wt-media-desktop`，`main`，基线 `c03d244`（T-01 收尾）→ `4b3a7b4`，共 **11** 个 commit：

| # | commit | 内容 |
|---|---|---|
| 1 | `ec2d34b` | DTO 迁出 `main.rs`（纯移动） |
| 2 | `d4ab510` | `HttpClient` 拆为 `LocalAgentClient` / `CloudClient` |
| 3 | `3bcf2c7` | 17 个 Tauri 命令迁出（含 `state.rs`） |
| 4 | `72095b9` | 新增 `config.rs` 与 `resources/desktop.production.toml` |
| 5 | `e6842c1` | 抽出 `preflight.rs`，合并两处重复的预检与身份守卫 |
| 6 | `30b9ebf` | 删除 `local_agent/mod.rs` 的死代码，只留 `BoundNodeFacts` |
| 7 | `0982fc3` | sidecar 启停从 `commands/agent.rs` 抽到 `sidecar/mod.rs` |
| 8 | `5cddc4e` | sidecar 输出不再被丢弃：内存环形缓冲 + 退出报告 |
| 9 | `38b97be` | `scripts/test.sh` 改跑 `cargo test --workspace` |
| 10 | `19541b3` | 新增 `paths.rs`：配置定位顺序与编译内置兜底 |
| 11 | `4b3a7b4` | 退出报告补上「缓冲共 N 行」，文案抽成可测的纯函数 |

逐 commit 测试矩阵（`/tmp/t06_matrix.sh`，逐个 checkout 后**强制重编**再量：

    git log --reverse --format=%H c03d244~1..HEAD

| commit | tests | bin 告警 | test 告警 |
|---|---|---|---|
| `c03d244`（基线） | 11 | 14 | 12 |
| `ec2d34b` | 11 | 14 | 12 |
| `d4ab510` | 11 | 14 | 12 |
| `3bcf2c7` | 11 | 13 | 11 |
| `72095b9` | 21 | 29 | 11 |
| `e6842c1` | 29 | 29 | 11 |
| `30b9ebf` | 27 | 20 | 4 |
| `0982fc3` | 27 | 20 | 4 |
| `5cddc4e` | 33 | 21 | 4 |
| `38b97be` | 33 | 21 | 4 |
| `19541b3` | 40 | 28 | 4 |
| `4b3a7b4` | **42** | **27** | 4 |

测试数逐 commit 核算（不是「涨了就行」，而是每一步都能对上）：

    11（基线）→ 21（+10 config.rs）→ 29（+8 preflight）
    → 27（-2 删 local_agent 的两条死代码测试）→ 33（+6 drain）
    → 40（+7 paths）→ 42（+2 exit_report）

告警数同法：`21 → 28` 是 `paths.rs` 新增 7 条「从未使用」；`28 → 27` 是
`4b3a7b4` 让 `drain::len` 不再是死函数。**量为 0 的两条不是空转**：cargo 只在
**重编**的 crate 上重发告警，故每次量测前 `touch src-tauri/src/*.rs
src-tauri/src/*/*.rs`；否则缓存命中会把告警数报低。

> **测量口径的一处订正**：本轮曾用 `grep -c '^warning'` 量到 bin 28（与上一
> commit 相同，看似没消除），实为把 cargo 收尾行 ``warning: `wt-media-desktop-shell`
> (bin ...) generated 27 warnings`` 也数了进去，**多算 1**。上表用的是 cargo
> 自报的 `generated N warnings`（`/tmp/t06_matrix.sh` 一直是这个口径），故历次
> 数字不受影响。

### 2. AC-04 的两个数

```
$ git show c03d244:src-tauri/src/main.rs | wc -l   →  1570
$ wc -l src-tauri/src/main.rs                      →    89
$ cargo test --workspace                           →  test result: ok. 42 passed
$ cargo build                                      →  成功
```

1570 → 89（**< 300，AC-04 达成**；计划写的「~140 行」是估算，实际更小：拆完后
`main.rs` 只剩 `mod` 清单、两个 fallback 判定、`main()` 装配与 1 条测试）。

### 3. 接线未动：`generate_handler!` 17/17 逐字同序

```
baseline 17 项（裸名，因为命令当时就定义在 main.rs 里）
now      17 项（commands::<mod>::<name>，取末段比）
diff → 空
```

### 4. 搬家是否逐字：逐函数实测（本期的核心判据）

`/tmp/t06_body_parity.py`：按花括号配对取出每个函数的**签名**与**函数体**，
去掉空行与缩进后比较。**带阳性对照**——`python_fallback_allowed` 是一条确定
逐字未动的函数，若匹配器连它都判不出 IDENTICAL，则它对别的函数说什么都不算数。

比对前先抵消 commit 2 引入的**机械改名**：`HttpClient` → `LocalAgentClient`、
`local_agent_base`/`cloud_base` → `base`。不抵消的话，`client.local_agent_base`
这种**函数体内**的一行会被算成「逻辑改了」，结论就不是 7 条而是 13 条（这是本
脚本的第一版结论，已作废）。

结果 **26 项（17 命令 + 9 测试）**：

| 判定 | 条数 | 含义 |
|---|---|---|
| IDENTICAL | 9 | 9 条既有测试，内容逐字不变 |
| BODY-SAME/SIG | 10 | 函数体逐字不变，只有签名行变了 |
| BODY-CHANGED | 7 | 函数体确实改了——**逐条都对应一处计划内的改动** |

7 条 BODY-CHANGED 逐条核对（`unified_diff`，去空行去缩进），全部是预期中的改动：

| 命令 | 改动 | 出处 |
|---|---|---|
| `local_agent_start` | 25 行匹配臂 → 委托 `sidecar::start(...)` | commit 7 |
| `local_agent_stop` | 4 行 → `sidecar::stop(child)` | commit 7 |
| `local_agent_health` | 两处 `map_err` 尾部追加 `drain::summary(...)` | commit 7/8 |
| `local_agent_account_check` | 53 行重复 preflight + 3 个守卫 → `preflight::run(..., ACCOUNT_CHECK)` 等 | commit 5 |
| `local_agent_cookie_read` | 53 行 → `preflight::run(..., COOKIE_READ)` | commit 5 |
| `local_agent_bind_session` | 空地址守卫 + 身份守卫 → `preflight::require_*` | commit 5 |
| `local_agent_refresh_runtime` | 空地址守卫 + 绑定守卫 → `preflight::require_*` | commit 5 |

**签名行的改动只有两类**，均为搬迁的必然结果：`fn` → `pub fn`（跨模块后必须
可达），以及 `HttpClient`/`local_agent_base` → `LocalAgentClient`/`base`
（commit 2 的拆型）。

9 条既有测试**全部按名找到、内容逐字不变**（`/tmp/base_tests.txt` 与当前树逐个
比对），分布：`commands/profile.rs` 4 条、`dto/profile.rs` 2 条、`commands/profile.rs`
3 条（共 7 条 profile + 1 条 `main.rs` 的 fallback 判定 + 1 条见上表）。

### 5. 文案没漂：CJK 字面量普查 + 16 行渲染表

「错误文案逐字节不变」这句话用两种办法钉：

**(a) 字面量普查**（本次重跑）：baseline `main.rs` 有 **99** 条含中文的字符串
字面量（去重 **84**）。其中 **93** 条在新树的某处**逐字存在**；**6 条不逐字
存在**——恰好是 6 条带占位符的模板：

```
Cookie读取预检响应格式错误: {}      Cookie读取预检失败: {}
Cookie读取预检失败: {} {}           账号检查预检响应格式错误: {}
账号检查预检失败: {}                账号检查预检失败: {} {}
```

这 6 条由 `{noun}` + 固定后缀**拼**出来（`preflight.rs:107-125`），词干与后缀
两半都在树里，故不是丢失而是分解。**拼出来的结果由 `message_parity` 的 16 行
表钉住**（`preflight.rs:352`：`[(PreflightSpec, PreflightFailure, &str); 16]`），
每一行都是 `（流程规格, 失败形态, 该形态历史上输出的那一句）` 的精确相等断言。

**(b) 两处 `StatusCode` 的渲染**：`reqwest::StatusCode` 的 `Display` 带
reason phrase（`400 Bad Request`，不是 `400`）。这一点最初被我写错、被测试抓住：
`message_parity` 报 `expected "…: 400 body" / actual "…: 400 Bad Request body"`。
回查 `git show HEAD:src-tauri/src/commands/account.rs` 确认原实现用的是 `{}`，
即**测试错了不是代码错了**，改正期望值并把那条测试改名（它原来的名字断言的正是
我误以为的那件事）。

**(c) 流程规格的粒度**：`PreflightSpec` 是 `{noun, no_cloud_address}` 而**不是**
计划所写的 `{noun, verb}`。理由是实测：四条流程的空地址句子四种写法
（`…无法执行账号检查`/`…无法读取Cookie`/`…无法完成本机可信绑定`/`…无法刷新本机可信状态`），
且预检后的文案也各差一个字（`…重新检测并绑定` vs `…绑定当前比特浏览器账号`）。
一个能覆盖四种的模板就等于「一个装了四个句子的语法」，故差异按**文本**传参
（`NO_CLOUD_ADDRESS_BIND`/`NO_CLOUD_ADDRESS_REFRESH`/`NO_BINDING_SENSITIVE`/
`NO_BINDING_REFRESH`），其余共用。

### 6. 死代码删除与它带来的覆盖缺口（如实登记）

`30b9ebf` 删除 `local_agent/mod.rs` 的 5 个 `*_COMMAND` 常量、
`BindSessionError`、`BindingTransport`、`LocalAgentBridge`、`command_names`
与 2 条测试，只留 `BoundNodeFacts`。删除依据是先枚举**全部**符号的引用点，不靠
印象（首次 grep 用 `-v '^./local_agent/mod.rs'` 排自身，路径里的 `.` 是正则通配
符，导致**每个**符号看起来都有外部引用；重列命中位置后才拿到真相：只有
`BoundNodeFacts` 是活的）。

**覆盖缺口（登记，不在本 CHG 修补）**：被删的
`empty_binding_ticket_is_rejected_before_transport` 是「空票据在发出请求前就被
拒绝」这条规则的**唯一**测试，而它测的是被删的那个替身
（`LocalAgentBridge::bind_session` + 注入的 `RecordingTransport`）。活代码里这条
规则仍在——`commands/bind.rs:48-50` 的 `trim()` + 空判定——但**它从来没有被任何
测试覆盖过**：

```
$ grep -rn 'binding_ticket' src-tauri/src
dto/bind.rs:15:    pub binding_ticket: String,
commands/bind.rs:48:    let binding_ticket = args.binding_ticket.trim().to_string();
commands/bind.rs:49:    if binding_ticket.is_empty() {
commands/bind.rs:60:        binding_token: binding_ticket,
```

即：规则没有丢，**验证丢了**。补测需要在命令层造一个 Cloud 替身（本仓目前没有
命令层测试脚手架），不在 T-06 的授权范围。计划原文说这两条测试「重写」，实际是
**删除**——因为它们的被测对象整体都不在了。

### 7. 变异对照（红验证）

| 目标 | 变异数 | 结果 | 脚本 |
|---|---|---|---|
| `config.rs` | 12 | 12/12 CAUGHT | `/tmp/t06_configmut.py` |
| `drain.rs` | 8 | 8/8 CAUGHT | `/tmp/t06c8_drainmut.py` |
| `paths.rs` | 7 | 7/7 CAUGHT | `/tmp/t06c10_pathsmut.py` |
| `exit_report` | 4 | 4/4 CAUGHT | `/tmp/t06c11_exitmut.py` |

每份脚本都带两道防空转护栏：**解析到 0 条测试结果即停**、**变异锚点匹配数 ≠ 1
即停**。护栏不是装饰——`paths.rs` 那份第一版因 `FILE.parents[3]` 指到了
workspace 根而不是 crate 根，cargo 根本没跑起来，正是「解析到 0 条」拦下的。

`exit_report` 的 4 条变异本轮新做：M-01 把「持有行数」改成末段长度（这半个功能
的存在理由就是两个数**会不等**）、M-02/M-03 改文案、M-04 去行前缀。**这份脚本
自己错了五次才跑对**，每次都朝同一方向报出「0/4 caught」这个**假结论**（即
「测试很弱」）：

1. 按 `__file__` 向上找 crate 根——脚本在 `/tmp`，上面没有 `Cargo.toml`，护栏拦下；
2. 结果正则只匹配 `test result: ok.`，而被杀死的变异打印 `test result: FAILED.
   41 passed`，于是解析到 0 条通过——护栏拦下；
3. 编译失败正则写成 `^error(\[|:)`，把 cargo 的 `error: test failed, to rerun …`
   （**正是成功捕获时会打印的那行**）当成编译不过，每个捕获都被丢弃；
4. 失败测试名从 `name ... FAILED` 行抓，而这里的输出里没有这种行（名字在
   `failures:` 块内）→ 四条真捕获全报成 SURVIVED；
5. 修好 (4) 后仍全 SURVIVED：表里写裸名，`failed` 里是
   `sidecar::drain::tests::<name>` 全限定名。

(1)(2)(3) 被护栏拦下；**(4)(5) 说明护栏挡不住「解析成功但解析错了」**——那只能
靠人看清 `passing` 在降而 `failed` 是空的这个矛盾。记在这里，因为下次写变异脚本
还会遇到。

**两条变异逼出了真问题**（`paths.rs`）：M-07「把读不出的文件改成 panic」最初
**存活**——`Err(_) => 兜底` 这个分支根本没有测试。补
`an_existing_file_that_cannot_be_read_falls_back_instead_of_panicking`（用**非
UTF-8 字节**造「文件存在但读不出」，比权限位可靠：权限位对 root 与不同 CI 行为
不一致）；另 `locate_takes_the_first_candidate_that_exists` 原本**只让一个候选
存在**，于是「取第一个」与「取最后一个」两种实现对它**都成立**，改为让所有候选
都存在。

### 8. 顺手修好一个坏掉的闸门，并登记一个更大的发现

`scripts/test.sh` 原本是 `npm test`，而本仓**没有 `package.json`**（顶层只有
`src-tauri/`、`tests/`、`Cargo.*` 与治理文档；前端在 `wt-media-cloud/web` 构建后
以 `.generated/frontend/` 进来）。先证明它确实坏：

```
$ npm test
npm error code ENOENT
npm error path .../wt-media-desktop/package.json
```

改为 `cargo test --workspace` 后 33 passed。

**顺带查出比计划记录更大的问题**（登记，本 commit 不处理）：M0 时期的整套 Node
工具链还挂在本仓，而它们引用的东西都不存在——

| 文件 | 引用 | 现状 |
|---|---|---|
| `.github/workflows/m0-desktop.yml` | `setup-node` + `cache-dependency-path: package-lock.json`，然后 `scripts/bootstrap.sh`、`npm run lint` | 第一步就停：无 `package.json` |
| `scripts/{bootstrap,dev,start,stop,build,health}.sh` | 全部 `npm …` | 同样无法运行 |
| `scripts/verify-real-scripts.mjs` | 读 `package.json` 并断言 10 个 npm scripts | 连启动都不行 |
| `scripts/health-check.mjs` | 要求存在 `src/services/local-agent.js` | 该目录树本仓不存在 |

也就是说**这个 CI workflow 今天在任何分支上都不可能通过**，这同时解释了「坏掉的
`npm test` 为何一直没人发现」：CI 在 `bootstrap.sh` 就失败了，从没走到 test。
计划只授权改 `test.sh`，其余涉及「这些能力该由谁承担」的独立决策，本 CHG 的 AC
一条也不覆盖，故只改被授权的那一行。

### 9. 范围与越界检查

`git diff --stat c03d244..HEAD` 共 **27 个文件**（+3142 / -1608），删除文件 **0**。
两处看起来「越界」的改动都在计划内：

| 文件 | 改动 | 判定 |
|---|---|---|
| `src-tauri/Cargo.toml` (+3) | 加 `toml = "0.9"`（`config.rs` 用；已在 `Cargo.lock` 传递闭包内，不引入新 crate） | 属 `72095b9`，在计划 T-06 提交序列「`config.rs`+`resources/*.toml`+`bundle.resources`」内 |
| `src-tauri/tauri.conf.json` (+1) | `"resources": ["resources/*.toml"]` | 同上；计划的 T-06 序列与 T-07 条目都写了它，实际落在 T-06 的 config commit |
| `Cargo.lock` (+1) | `toml` 条目 | 同上 |
| `scripts/test.sh` | 见 §8 | 计划 T-06 明列 |

`web/dist-desktop/`、`.generated/` 未被触碰（0 命中）。

**未动的冻结面**：`tauri.conf.json` 的 CSP 字面量仍在（CSP 运行时注入是 T-07）、
`main.rs:1534` 的 `8765` 仍在（T-07）、`Client::new()` 仍无超时（T-07）。

## Expected

- `main.rs` 收缩到 < 300 行，17 个命令与 `generate_handler!` 逐字同序；
- 9 条既有测试逐字不变，17 个命令体的改动**逐条可归因**到计划内的改动；
- 用户可见文案不漂（字面量普查 + 渲染表双证据）；
- `cargo test --workspace` 全绿且逐 commit 单调不减；`cargo build` 通过。

## Actual

全部达成。需要如实记录的有：

### 9.1 仍未落地、按计划归 T-07 的部分（T-06 的目标树未走完）

计划 T-06 的目标树列了 3 个文件，其内容实际是 T-07 的，故 T-06 收尾时**不存在**：

| 目标树列出 | 状态 |
|---|---|
| `bootstrap.rs` | 未建（T-07：配置引导装载） |
| `dto/config.rs` | 未建（T-07：`get_public_config` 的返回 DTO） |
| `commands/public_config.rs` | 未建（T-07：第 17+1 个命令） |

T-06 自己的验收条目（`cargo test` 全绿 + `cargo build` 通过）已达成，故记 DONE；
这 3 个文件随 T-07 落地。

### 9.2 须知的中间态（T-07 落地即消除）

bin target **27 条告警**中 **23 条**是「从未使用」：`config.rs` 16 条 +
`paths.rs` 7 条。这不是缺陷而是**本次拆分必然的中间态**——`config.rs`/`paths.rs`
已就位但还没有消费者，T-07 把 `main` 接上去即消除。其余 4 条是既有的四个空壳
（`filesystem/`、`secure_store/`、`system/`、`updater/`，本 CHG 不动）。

**`sidecar/` 与用户裁定措辞的差异**：用户裁定写的是「真实 sidecar 生命周期与
Rust HTTP 代理搬进 `local_agent/`」，实际落在 `sidecar/{mod,drain}.rs`。依据是
计划 T-06 的目标树**逐文件**列了 `sidecar/{mod,drain}.rs`（目标树是文件级产物，
裁定是意图级描述），且 `local_agent/mod.rs` 在本 CHG 里被明确要求删除死代码。
`local_agent/mod.rs` 现只保留 `BoundNodeFacts`（17 行），其 docstring 记了一条
残留：若它要挪，应随其余 bind DTO 一起走，不单独动。

### 9.3 已登记的决策

- **D-09**（T-06 内新登记）：`RELEASE_FAILED` = 「释放账号检查本机授权失败」，
  在 Cookie 读取流程里也这么说。这是它**一直**的说法，本次重构把文案钉住不动；
  改成按流程取名是一词之改，但**刻意不塞进一个承诺「无用户可见文案变更」的
  commit**。由 `release_text_still_names_the_account_check_flow` 钉住现状。

### 9.4 未覆盖面（枚举，不以「测试通过」代替）

- **命令层无测试脚手架**：本仓没有任何一条测试驱动过 `#[tauri::command]` 函数体，
  故 §4 的 7 条 BODY-CHANGED 的**新**行为只能靠逐字 diff + 文案表佐证，
  没有「调一次命令看它返回什么」这一层。T-09 的真实链路取证补这一块。
- **`preflight.rs` 的 async 路径**（`run`/`sync_runtime_facts`/`finish_permit`）
  全部走 HTTP，本模块测试只覆盖纯文案与守卫逻辑，async 部分同属 T-09。
- **`config.rs`/`paths.rs` 无消费者**：测试只证明它们自身的规则，不证明
  「`main` 真的会把它们接上」——那要等 T-07。
- **4 个空壳模块**（`filesystem`/`secure_store`/`system`/`updater`）仍是 3 行，
  本 CHG 明示不动。
- **§6 的空票据守卫无覆盖**（见上）。

## Follow-Up

- **T-07 是 T-06 的直接续**：`bootstrap.rs`、`dto/config.rs`、
  `commands/public_config.rs` 三个文件、`8765` 字面量、CSP 运行时注入、
  http 超时、`uuid` 的 per-launch token、**两条 spawn 路径同一组四个环境变量**，
  并在同批落地 T-08。落地后 §9.2 的 23 条中间态告警归零。
- **§6 的空票据守卫**需在命令层测试脚手架具备后补测（T-09 或后续 CHG）。
- **§8 的 Node 工具链**（CI workflow + 8 个脚本 + 2 个 mjs）需独立决策后处理；
  当前 CI 在任何分支上都不可能通过。
- **仓库级 CI 与打包脚本**不在本 CHG 的 AC 内，未动。
