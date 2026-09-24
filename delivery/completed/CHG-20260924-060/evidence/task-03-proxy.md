# evidence — T-03 回环目标绕过系统代理

- CHG: CHG-20260924-060
- Task: T-03
- Date: 2026-09-24
- Type: test + measurement + command
- Status: PASS（一项计划内的对照臂判定为**无效对照**，已如实降级，见「无效对照」节）
- Commits: `wt-media-desktop` — 见本文件末「提交」

## Purpose

D-02：回环目标（本机 Cloud / Local Agent）不走系统代理，远程 Cloud **保留**系统代理。

判据不是「测试变绿」，而是**外部可观测行为**：同一台机器、同一个目标，
经代理的 client 与不经代理的 client 的行为必须可区分，且被绕过的那条确实直连。

## 一、先失败：实测出这条 bug 是真的，且这是本 Task 的「先失败」证据

实现之前先做判别实验（临时诊断测试，取证后已删除，不在提交里）。目标是找一条
**不能被两种解释同时说明**的判别式——早先一版诊断用「对端地址是临时端口、请求行是 origin-form」
当作「直连」的证据，被自己否掉：代理自己发起的出站连接同样用临时端口，且许多代理会改写
成 origin-form。换成**去一个无人监听的端口**：

```
DIAG dead-port  proxied-client -> Ok("Ok(502 Bad Gateway)") in 3.045552667s
DIAG dead-port  no_proxy-client -> Err("Err(is_connect=true, is_timeout=false)") in 405.375µs
DIAG mute-server proxied-client -> Err("Err(is_timeout=true)") accepts=1 in 1.002619833s
```

- **没有任何进程监听那个回环端口，经代理的 client 却拿到了 `502 Bad Gateway`** ——
  只有代理能替一个不存在的服务作答。⇒ 回环请求**确实被系统代理截获**，bug 当前真实存在。
- `no_proxy()` 的 client 对同一端口 405µs 内 `is_connect` —— 内核立刻拒绝，这是直连的形状。
- 3.0s 是代理自己的重试/超时，不是本 client 的。

本机 `scutil --proxy`：HTTPEnable 1 / HTTPProxy 127.0.0.1 / HTTPPort 7897，
SSOCKSEnable 1，`ExceptionsList` **列了** `127.0.0.1`、`localhost`、`192.168.0.0/16` 等，
但 hyper-util 0.1.20 的 macOS 分支只读 `HTTPEnable/HTTPProxy/HTTPPort`，**从不读 `ExceptionsList`**
（`src/client/proxy/matcher.rs:588-636`）——这就是「系统明明写了例外、请求还是被接管」的机制。
环境变量里没有任何代理相关项（只有 `GOPROXY`），所以走的确实是系统 matcher 那条路。

## 二、先否掉一条看起来最顺的路（v4 之前）

「给共享的 `build_client` 挂一个 `Proxy` 并附 `NoProxy::from_string("127.0.0.1,localhost")`，
保留系统代理」——**reqwest 0.12.28 做不到**，读 vendored 源码确认：

- `ClientBuilder::proxy()` 会**关掉** `auto_sys_proxy`（`async_impl/client.rs:1414-1418`），
  且 `auto_sys_proxy` 全文只有 `= false` 的写法（`:1416`、`:1429`），**没有公开方式设回 true**。
  系统 matcher 是 `build()` 时在 `:418-421` 追加的，仅在 `auto_sys_proxy` 为真时。
  ⇒ 挂 `Proxy` 不是收窄系统代理，而是**删除**它。
- `ClientBuilder::no_proxy()`（`:1428-1432`）是**全有全无**：清空 proxies 且同样关 `auto_sys_proxy`。
- `Proxy::no_proxy()`（`proxy.rs:361-363`）只作用于**你自己构造的那个 Proxy**。
- 走 `NO_PROXY` 环境变量确实可行（`matcher.rs:227-249`），但要 `std::env::set_var` **全局改环境**：
  会覆盖用户自己的 `NO_PROXY`、会漏进子进程、测试无法并行隔离。**否决。**

## 三、实现

`src-tauri/src/http/` 三个文件，**零新增依赖、零新增 `[dev-dependencies]`**：

- `mod.rs`：抽出 `timed_builder`；`build_client` 语义不变；新增 `build_client_without_proxy`
  （同一 builder 加 `.no_proxy()`）；新增 `is_loopback_url`；模块 docstring 补第三条不变量
  （一个 client 对所有目标要么全带系统代理、要么全不带，故回环面自持 client）。
- `local_agent.rs:41`：`build_client` → `build_client_without_proxy`，**无条件**。
  理由写在 docstring 里：`base` 是 `format!("http://{}:{}", host, port)`，`agent.host` 合法值含 `::1`，
  该式会拼出 `http://::1:8765`（未加方括号的 IPv6 authority），`Url::parse` 直接拒——
  若这里的绕过是条件式，`::1` 会**静默退回**带代理的 client。无条件写法则让
  「本地 Agent 永不经过代理」由构造保证，而不是由一个字符串谓词保证。
- `cloud.rs`：`CloudClient` 持 `proxied` / `direct` 两个 client，`post()` 经 `client_for(url)` 选；
  重写 docstring（「按请求的事实」多一项：代理决策）。

**`is_loopback_url` 解析而非子串匹配**，理由是凭证式 URL：`http://localhost@evil.test/` 里
既有 `localhost` 又有远程主机，只有解析能分开。`reqwest::Url` 是 `pub use url::Url`
（`reqwest-0.12.28/src/lib.rs:280`，无条件 re-export），**不引入新依赖**，且它本就是 reqwest
自己的解析入口——这一句写进了代码注释，否则后人会把它当成「为一个 host 判断引入 URL parser」而回退。
`host_str()` 对 `http://[::1]:18080/` 返回 `"[::1]"`，而 `"[::1]".parse::<IpAddr>()` 失败，
故按文本剥方括号（`url::Host` 枚举不可达：`url` 不是直接依赖）。已实测确认这两点。

### 决策点唯一性（实测，非引述）

```
$ grep -rn --include='*.rs' -e 'CloudClient' -e '\.post(' -e 'client_for' src/
```

`CloudClient` 的 `post` 调用点**恰好四处**：`commands/bind.rs:69`、`preflight.rs:224/257/310`。
（计划里写的是 `bind.rs:56`、`preflight.rs:219/252/305`，**行号偏了，数目对**——以本次实测为准。）

另一个方向也查了：**`http/` 之外没有任何地方构造 `reqwest::Client`**，
`build_client` / `build_client_without_proxy` 是两个唯一构造点（加上测试内联的对照 client）。
故 `client_for` 是唯一的代理决策点，没有第二条路要与它保持同步。

## 四、验证（五层）

### 4.1 谓词表 —— 16 例，两向都断言

`http::tests::only_loopback_destinations_are_treated_as_local`：
`127.0.0.1`/`127.0.0.2`/`127.255.255.254`/`localhost`/`LOCALHOST`/`[::1]` ✓；
`0.0.0.0`/`192.168.1.10`/`cloud.example.test`/`localhost.evil.test`/`127.0.0.1.evil.test`/
`[::2]`/`localhost@evil.test`/`127.0.0.1:18080`（无 scheme）/`""`/`http:///x` ✗。
两向都断言的理由同 `config.rs`：只会说「不是」的规则和「全否」无法区分。

### 4.2 两个 builder 确实不同 —— **这条才是抓得住变异的那条**

`http::tests::the_unproxied_client_is_built_without_the_system_proxy`。

reqwest **没有 getter** 可读回已构 client 的代理配置，唯一进程内可观测量是 `Debug`，
而它够用，理由在源码里可读：`ClientRef::fmt_fields` **仅当 proxies 非空**时才写 `proxies`
（`async_impl/client.rs:2943-2945`），而 `build()` 在 `auto_sys_proxy` 为真时**无条件**压入
系统 matcher（`:418-421`）——**与本机是否真有代理无关**。所以这条断言**机器无关**。

### 4.3 绕过是真的（假代理 + 命中计数）

`http::tests::a_loopback_request_does_not_reach_the_proxy_it_was_handed`：
两个 `TcpListener`——目标（计数 accept，答 200）与假代理（计数 accept，答 502）。
subject = `build_client_without_proxy`；control = **测试内联** `Client::builder().proxy(Proxy::all(fake))`
（**不能用 `build_client`**，那会连到开发者真 Clash，测试变机器相关）。
判据是 **hits 计数**而非状态码，就不依赖 hyper 对明文 http 是转发还是隧道。
断言：subject ⇒ 200 / dest=1 / proxy=0；control ⇒ 502 / proxy=1 / dest **仍为 1**。

已核实 control 臂是机器无关的：`Proxy::all` → `Proxy::new(Intercept::All(..))`，
其 `no_proxy` 字段是 `None`，`into_matcher` 于是 `.no("")`（`proxy.rs:265-274`、`:377-386`）——
**不读环境变量 `NO_PROXY`**；hyper-util 的 `intercept` 里也没有任何内建的
loopback/localhost 豁免（`matcher.rs:122-133` 只查 `no` 表与 scheme）。

### 4.4 关闭的回环端口快速失败

`http::tests::a_closed_loopback_port_is_refused_promptly_instead_of_hanging`：
bind `127.0.0.1:0` → 取端口 → **drop** → `connect_timeout_seconds = 10` → 请求。
断言 `!is_timeout()` 且 `elapsed < 1s`。主判据是「快速失败而非等超时」。

已实测 `error.is_connect()` 成立（诊断输出里 `is_connect=true`），但**未**把它写成本测试的断言：
它经一层 hyper-util downcast，且两个断言已经足够定性，不引入未验证的脆弱点。

### 4.5 接线测试（选择，而非 builder）

`http::cloud::tests::a_loopback_cloud_url_is_sent_without_the_system_proxy`，
用 `std::ptr::eq` 断言 `client_for` 的选择：`127.0.0.1`/`localhost` ⇒ `&direct`；
`cloud.example.test`/`192.168.1.10` ⇒ `&proxied`。指针相等精确，不需字符串匹配。
4.2 锁的是 **builder**，这一条锁的是**选择**，互不替代——「一对正确的 client 接到错的分支」
正是本次要修的 bug 的形状。

## 五、阳性对照（否定结论必须先证明检查能失败）

### 5.1 变异对照：删掉 `.no_proxy()` —— **有效对照，红了 2 条**

把 `build_client_without_proxy` 里的 `.no_proxy()` 去掉后重跑（原文
`artifacts/t03-tests-red-no-no_proxy.out`）：

```
test result: FAILED. 66 passed; 2 failed; 0 ignored; 0 measured; 0 filtered out
failures:
    http::tests::a_closed_loopback_port_is_refused_promptly_instead_of_hanging
    http::tests::the_unproxied_client_is_built_without_the_system_proxy
```

两条失败信息本身就是证据：

```
nothing may be proxied here: Client { accepts: Accepts, proxies: [Matcher { http:
  Intercept { uri: http://127.0.0.1:7897/ }, https: Intercept { uri: http://127.0.0.1:7897/ } }], ... }
nothing is listening, so this cannot succeed: Response { url: "http://127.0.0.1:56789/healthz", status: 502, ... }
```

- 第一条把**系统 matcher 真实解析出的代理**打了出来：`http://127.0.0.1:7897/` ——
  正是本机 Clash。这不是建模，是活的系统 matcher。
- 第二条对一个**没人监听**的端口拿到 `502` —— 与第一节的诊断同一个现象。

**同时发现一处必须纠正的说法（已改进代码 docstring）**：这条变异下
**假代理那条测试（4.3）仍然通过**。原因实测得很清楚——系统代理会自己去拨目标，
而目标是本次测试起的监听器、会答 200，于是 4.3 的每一条断言都仍然成立，
**请求事实上正在离开本机**。所以 4.3 证明的是「绕过存在时它确实生效」，
**不能**证明「绕过存在」。原 docstring 把 4.3 说成「在没有系统代理的机器上抓不住变异」，
是个错误的解释，已改写为上述实测结论。

### 5.2 20× 循环 —— **无效对照，如实降级，不计为通过**

计划要求：把超时测试指回 `build_client` 跑 20 次，**预期至少红一次**；一次都不红则报「对照无效」。

```
# 出货配置（unproxied client）
$ for i in $(seq 1 20); do cargo test --bin wt-media-desktop-shell http::tests::a_request_to_a_silent_server_...; done
  20 × test result: ok. 1 passed; 0 failed; ...          → artifacts/t03-timeout-test-20x.out

# CONTROL ARM：把该测试的 client 变异回带代理的 build_client，同一循环
  20 × test result: ok. 1 passed; 0 failed; ...          → artifacts/t03-timeout-test-20x-control-arm.out
```

**对照臂 20/20 全绿 ⇒ 这个循环区分不了两个 client，按计划自己的判据记为「无效对照」，不得算通过。**

机制也解释了：Clash 会自己去拨那个静默监听器（诊断里 `accepts=1`），对面不回话，
于是**本 client 自己的 1s 截止时间先到**，产出 `is_timeout` —— 与直连时是同一种错误，
`expect_err` 与 `is_timeout()` 两条断言都满足。**该测试改动前后都通过，且它看不见这个区别。**

因此 T-03 的判据**不靠这条循环**，而靠 5.1 的变异对照（红了 2 条）+ 第一节的
502-vs-is_connect 实测。该循环的价值仅在于记录「出货配置下 20/20 稳定」这一事实。

### 5.3 测试计数

```
$ cargo test --workspace
test result: ok. 68 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 1.02s
```

`artifacts/t03-tests-green.out`。**63 → 68**（T-02 后是 63，本次新增 5 条）：
谓词表、builder 差异、假代理、关闭端口、接线。`cargo build` 通过；
`cargo clippy --workspace --all-targets` 的 8 条 warning **全部在本次未触碰的文件**
（`updater/`、`system/`、`secure_store/`、`filesystem/`、`main.rs:43`、
`commands/account.rs` ×2、`sidecar/drain.rs`），`http/` 下**零新增 warning**。

### 5.4 一处计划修正（必须记）

计划里的验证命令写的是 `cargo test --lib http::tests::...`。**这条命令在本仓不成立**：
`wt-media-desktop-shell` 是**二进制 crate**，`--lib` 会以
`error: no library targets found in package wt-media-desktop-shell` 结束、输出为空。
正确目标是 `--bin wt-media-desktop-shell <filter>`，本文件所有循环都用的是它。

## 六、未覆盖 / 只登记不修

- **未做：真机启动 + Clash 连接日志**。计划把它列为「最强的端到端证据」（修前日志里同时出现
  `127.0.0.1:18080` 与 `127.0.0.1:8765`，修后两者都消失）。本轮**没有做**，不声称。
  但要说清它与已做证据的关系：它想回答的是「系统 matcher 是否解析到 Clash、是否截获回环」，
  而这两个问题**已经被直接量测回答了**，且是在进程内、可归因的（5.1 第一条打印出了活的
  `http://127.0.0.1:7897/`；第一节打印出了代理替死端口作答的 502）。所以那条日志是**佐证**，
  不是唯一证据。仍如实登记为未做。
- **未覆盖（登记）**：`local_agent.rs:42` 的 `format!("http://{}:{}", host, port)` 在
  `agent.host = "::1"`（**校验器认可**）时产出 `http://::1:8765`，任何 HTTP 服务器都不会按预期
  看待它——合法配置产生无法寻址的 client。与本轮代理改动无关（正因如此，`local_agent` 的绕过
  才写成无条件式，否则它会变成静默回归），登记为本 CHG 之外的独立遗留，**不修**。
- **未做（有理由的非动作）**：不跑 `cargo fmt`。本仓**没有** `rustfmt.toml`，
  且 `cargo fmt --check` 在 66 处报差异，绝大多数在本次未触碰的文件
  （`paths.rs`、`sidecar/mod.rs`、`preflight.rs`、`bootstrap.rs`…）——即本仓**刻意不跑 rustfmt**、
  自行放宽到约 136 列（`preflight.rs` 现存最长行 136）。本次新增最长行约 110 列，在该约定之内。
  跑 `cargo fmt` 会重写二十余个无关文件，故**不跑**。
- **未做**：不关 reqwest 的 `system-proxy` feature（要的是按目标绕过，不是全局关闭）；
  不放宽 `config.rs` 的 `is_loopback_host`（会悄悄改掉一条安全校验：`127.0.0.2` 会变成合法的
  `agent.host`，改变 sidecar 被要求绑定的接口）；不改 `dev_csp` / `tauri.conf.json`。

## 七、顺带：CHG-056 遗留③ 的**改写**，不是闭合

`CHG-056` 把「`connect_timeout` 在宿主机上不可量测」记为遗留。本次修复**不会**让它变得可量测：
回环上的**关闭端口由内核立刻 ECONNREFUSED**（实测 405µs），产生不了「SYN 无人应答」那个
`connect_timeout` 存在的条件——**有无代理都如此**。故该项记为**改写**：

> 回环请求不再被系统代理截获；`connect_timeout` 在回环上仍不可触发，
> 因为关闭的回环端口是被拒绝而非挂起。

**不标成「已闭合」。**

## 提交

`wt-media-desktop`，3 个文件（`src-tauri/src/http/{mod,cloud,local_agent}.rs`），
commit **`d329abc`**。本次**只改逻辑**，不含任何文件搬移或删除。
