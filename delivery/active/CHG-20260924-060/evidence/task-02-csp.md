# evidence — T-02 生产 CSP 加 `ipc:`

- CHG: CHG-20260924-060
- Task: T-02
- Date: 2026-09-24
- Type: test + command
- Status: PASS

## Purpose

D-01：把 `ipc:` 与 `http://ipc.localhost` 加进生产 CSP 的 `connect-src`，消除每次启动的
`ipc://` 拒绝（Tauri 首选 IPC 传输被拒后回落 `postMessage`）。判据是**外部可观测行为**
（拒绝计数），不是「测试变绿」。

## Method

```
# 1. 先失败：只改 TOML，跑测试
cd wt-media-desktop/src-tauri
$EDITOR resources/desktop.production.toml      # csp_connect_src 加 ipc: 前缀
cargo test --workspace 2>&1 | sed -n '/^failures:/,$p'   # -> artifacts/t02-csp-guards-red.out

# 2. 最小实现：同步两处守卫字面量
#    src/bootstrap.rs  the_policy_is_shape_for_shape_the_literal_it_replaced
#    src/config.rs     out_of_range_values_are_rejected 的 from 串
cargo test --workspace

# 3. 真实启动取证（判据 = ipc:// 拒绝数）
python3 delivery/active/CHG-20260924-060/evidence/tools/t02_csp_shipped_value_launch.py
```

第 3 步的驱动脚本**从 `resources/desktop.production.toml` 解析出 `csp_connect_src`**，
再交给 CHG-056 的 `ac05_desktop_launch.py`（`importlib` 导入 `run_leg`，不复制）跑两条 leg：

- **S1**：用**出货文件里那个值**启动 → `ipc://` 拒绝数必须为 0。
- **S2**：用手写的**改动前那个值**启动 → 拒绝数必须 > 0（阳性对照）。

## Expected

1. 改 TOML 后恰好**两处**测试转红，且失败信息可逐条对应到守卫。
2. 同步两处字面量后全绿，计数 63。
3. S1 → `ipc:// refusals 0`；S2 → `ipc:// refusals > 0`。
4. `config.rs` 的校验逻辑（`:186-195`）零改动；`dev_csp` 仍为 `None`。

## Actual

**1. 先失败 —— 恰好两处，正是预测的两处**

```
---- bootstrap::tests::the_policy_is_shape_for_shape_the_literal_it_replaced stdout ----
panicked at src-tauri/src/bootstrap.rs:266:9:
assertion `left == right` failed
  left: "default-src 'self'; connect-src 'self' ipc: http://ipc.localhost http://127.0.0.1:18080; style-src 'self' 'unsafe-inline'; img-src 'self' https:"
 right: "default-src 'self'; connect-src 'self' http://127.0.0.1:18080; style-src 'self' 'unsafe-inline'; img-src 'self' https:"

---- config::tests::out_of_range_values_are_rejected stdout ----
panicked at src-tauri/src/config.rs:413:13:
row "empty csp connect-src in production" matches nothing

test result: FAILED. 61 passed; 2 failed; 0 ignored; 0 measured; 0 filtered out
```

原文见 `artifacts/t02-csp-guards-red.out`。`61 passed; 2 failed` 的分母说明其余 61 条与
这次取值无关——**只有**这两条守卫盯着这个契约值，也正是它们存在的意义（`bootstrap.rs`
那条的 docstring 明写「改策略就必须改这里」）。

**2. 同步后全绿**

```
$ cargo test --workspace
test result: ok. 63 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 1.23s
```

63 与 CHG-056 记录的 desktop 计数一致（本 Task 不改测试数量，只改两处字面量）。

**3. 真实启动 —— 3 → 0，且对照臂确实出数**

驱动脚本落盘于 `evidence/tools/t02_csp_shipped_value_launch.py`，原始输出
`artifacts/t02-csp-shipped-launch.out`。它先解析并打印了真正的输入：

```
shipped config: .../wt-media-desktop/src-tauri/resources/desktop.production.toml
  csp_connect_src = 'ipc: http://ipc.localhost http://127.0.0.1:18080'
  pre-change value = 'http://127.0.0.1:18080'
```

S1（出货文件里的值）：

```
S1-shipped-value  (csp_connect_src = ipc: http://ipc.localhost http://127.0.0.1:18080)
  ipc:// refusals  0 (Tauri's preferred transport)
  fetch http://127.0.0.1:18080/healthz -> resolved refusals=0
  fetch http://localhost:18080/healthz -> rejected refusals=1 (control ...)
  local_agent_start -> ok=True value='started'
  /healthz    no token -> 401, wrong token -> 401, the Desktop's own client -> 200
  data dir    ['local-agent.sqlite3', 'logs', 'versions']
  after stop: nothing listening on 53070
```

S2（阳性对照，改动前的值）：

```
S2-control-pre-change-value  (csp_connect_src = http://127.0.0.1:18080)
  ipc:// refusals  3 (Tauri's preferred transport)
    refused: ipc://localhost/get_public_config
    refused: ipc://localhost/log_js_error
```

判据成立：同一二进制、同一探针页、同一 Cloud，只有那一行配置不同，
拒绝数 **3 → 0**。S2 的 3 与 CHG-056 记录的基线一致——**对照臂出数**，所以 S1 的 0
不是「计数器从未增长」，这一点是这次取证是否有效的分界。

两 leg 的报告序列本身就是旁证：S1 的 `reports` 里只有一个 `Violation`（即那条
**按设计**必被拒的 `localhost:18080` 对照请求）；S2 的 `reports` 里多出 3 条
`Violation`，与拒绝计数吻合。

**4. 未动的东西**

`git diff src/config.rs` 的全部输出是一行（测试表里的 `from` 串）：

```
-                "csp_connect_src = \"http://127.0.0.1:18080\"",
+                "csp_connect_src = \"ipc: http://ipc.localhost http://127.0.0.1:18080\"",
```

`:186-195` 的非空校验零改动（无 scheme 白名单）。`dev_csp` 保持 `None`——由
`apply_csp_writes_the_field_a_dev_build_would_otherwise_prefer_over` 断言，在 63 条绿里。

**5. 一处被迫的文档回写**

`bootstrap.rs` 那条金标测试的 docstring 原文声称该字符串是「`tauri.conf.json` 里那个字面量
——逐字、逐序、逐分隔符相同」。改值之后这句话**不再成立**（connect-src 的取值变了），
故同批改写为「同样的指令、同样的顺序、同样的分隔符，**但 connect-src 的取值有一处刻意改动**」，
并把「它按设计红了」写进去。不改这句就等于在代码里留一句假话。

## Follow-Up

- **未覆盖：生产整文件启动**。两条 leg 用 `environment = "development"` 与 scratch 端口，
  因为出货文件是生产配置、`agent.port = 8765`——那是开发者自己的 dev Agent 占用的端口，
  照本 CHG 的边界不得触碰。所以本次测的是**出货文件声明的那个 `csp_connect_src` 取值**，
  不是「生产配置整文件跑起来」。补齐这一块需要开发者先停掉自己的 Agent，本轮不做。
- **未覆盖：非 macOS**。IPC 渲染在 Windows/Linux 上是真的 `ipc://` 方案，与 macOS 的
  `http://ipc.localhost` 不同；本次只在 macOS 上取证。`ipc:` 与显式 host 两条都写进配置
  正是为了让两个平台各自命中，但**只观测了 macOS**，不外推。照 CHG-056 的先例登记。
- **未做**：探针用 `mode:"no-cors"`，只量策略放行与否、不量 HTTP 状态码（承 CHG-056 的边界）。
- `bootstrap.rs` 的测试名仍是 `..._the_literal_it_replaced`。名字保留、docstring 写清
  「有一处刻意改动的例外」，未改名以免制造无谓的 diff 噪音。

## 顺带查出：CHG-056 归档记录里有一个**被引用但未入库**的证据文件

本次的证据原本也落成 `.log`，`git add -A` 之后**静默没进提交**——本仓 `.gitignore` 第 3 条是
`*.log`。顺着这条查了归档的 CHG-056，发现同一个坑已经踩过且没人发现：

```
$ for f in $(ls delivery/completed/CHG-20260923-056/evidence/artifacts/); do
    git ls-files --error-unmatch ".../$f" >/dev/null 2>&1 && echo "TRACKED   $f" || echo "UNTRACKED $f"; done
TRACKED   README.md
TRACKED   ac0109.out
UNTRACKED ac05-run5.log
TRACKED   ac06.out
TRACKED   ac07.out
TRACKED   ac10.out
TRACKED   ac11-mutants.py
```

`ac05-run5.log`（8975 字节）**被 CHG-056 四处引用**——`change.md:484`、`change.md:531`、
`evidence/task-09-desktop-launch.md:9`、`evidence/task-09-desktop-launch.md:90`，以及
该目录自己的 `artifacts/README.md` 表格——但 `git ls-files` 里没有它。
后果是：**换一个 clone 打开这份归档，它最强的一条证据（「四次真实启动全部 PASS」）指向一个
不存在的文件。** 体积只有 9 KB，不是为大小排除的，纯粹是 `*.log` 规则吃掉而收尾时没人扫。

分类与处置：这与 T-05 已计划的「修掉归档连带产生的失效指针」是**同一类缺陷**（引用不成立），
故归入 T-05 一处修（把这一个文件 `git add -f` 补进归档，不改其内容、不改任何结论）。
本 CHG 自己的证据改名为 `.out` 以避开该规则，不覆盖仓级 `.gitignore` 策略。
