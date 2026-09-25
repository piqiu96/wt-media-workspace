# T-02 证据 — 活性探针（`already_running` 改为问一次 Agent）

日期：2026-09-25 ｜ 仓：`wt-media-desktop`（本任务只动这一仓）

## 1. 交付了什么

`src-tauri/src/commands/agent.rs`：

- `Occupancy { Vacant, Running, Stale }` + `occupancy()`：先读受管槽位，**空则不发任何请求**判 `Vacant`；
  非空才用一次 `/healthz` 区分 `Running` 与 `Stale`。
- `answering()`：`client.get("/healthz").send().await.is_ok()`。
- `discard()`：记一条 `stale` 记录 → 把句柄从槽里 `take` 走 → 试一次 `kill` → 清掉它命名的会话。
- `start()` 的守卫由 `if 槽里有句柄 { already_running }` 换成 `match occupancy(...)`。
- `Cargo.toml`：`tauri` 的 `test` feature 作为 **dev-dependency**（见 §5）。

三个提交：

| commit | 内容 |
|---|---|
| `15951a4` | `test(chg-059): T-02 让 test 构建能把真子进程放进受管槽位` —— 启用性改动，不改行为 |
| `c54025a` | `fix(chg-059): T-02 \`already_running\` 改为问一次 Agent` —— 生产修复 + 4 条用例 |
| 本条 | `docs(chg-059): T-02 记录与证据` |

## 2. 缺陷的复现（「先红」读数）

CHG-057 登记的实缺陷，原文在 `CHG-20260923-057/checkpoint.md:358-359`：
「`already_running` 在 sidecar 自己死掉之后仍会说「已在运行」」。

复现方式：**把守卫那一块整块还原成修复前的形状**（就是 `f1d1fba^:src-tauri/src/commands/agent.rs:163-168`
那个 `if process.0.lock()…is_some() { already_running(…); return Ok("already_running") }`），
再重跑同一条用例。**这不是历史转录，是重跑**——如实写明，免得被当成「修复之前跑过一次」的原始证据。

原始转录：`task-02-red.out`

```
test commands::agent::tests::a_start_after_the_agent_died_does_not_answer_already_running ... FAILED
thread '…' panicked at src-tauri/src/commands/agent.rs:865:9:
assertion `left != right` failed: the slot holds a handle, not an Agent: Ok("already_running")
  left: Ok("already_running")
 right: Ok("already_running")
test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 350 filtered out; finished in 0.02s
```

`Ok("already_running")` 是**对着一具尸体**给出的答案。用例里没有任何替身：
槽里是一个**真的 `CommandChild`**（`sh -c "exit 0"`，并等到 `CommandEvent::Terminated` 才算它真的结束了），
端口是**真的没人听**（`silent_port()` 绑了就放）。

修复后同一条转绿（`task-02-green.out`，该过滤器下 `16 passed; 0 failed`）。

## 3. 设计：为什么问 `/healthz`，以及这里 401 **不**致命

T-01 与 T-02 问的是两个不同的问题，答案的处置也不同：

| | 问题 | 401 的含义 | 处置 |
|---|---|---|---|
| T-01 就绪闸门 | 「我**能用的它**起来了吗」 | 在，但拒绝我们 ⇒ 用不了 | **致命，立即失败** |
| T-02 活性探针 | 「那个位置上**有东西在**吗」 | 在 | **算活着**，`Running` |

`answering()` 用的是 `is_ok()`，即「连上并拿到一个 HTTP 应答」，**不看状态码**。
这正是要的：401 说明对端在听、在按协议说话，只是不认这份凭据——那是「有人应答」，
不是「没人应答」。把它当 `Stale` 会去 `kill` 一个活着的进程并重启一个，比原缺陷更糟。

反过来，`Occupancy::Vacant` **一次请求都不发**。这不是省事：空槽时那个端口上可能是
**开发机上别人正在跑的 Agent**（本机 8765 就是），去问它等于把别人的进程当成自己的。
这条有独立用例——用会应答的桩，断言它**一个字节都没收到**。

## 4. 变异表：8/8 被各自的用例打掉

脚本 `/tmp/chg059/mutate_t02.py`，每条变异都**点名**它必须打掉的那条用例，
并带 `running 0 tests` 守卫（空过滤器会报成功，读成「打掉了」）。转录：`task-02-mutations.out`。

| # | 变异 | 必须被打掉的用例 | 读数 |
|---|---|---|---|
| M1 | `Stale` 分支变空操作（不丢弃，句柄留在槽里） | `a_start_after_the_agent_died_…` | 打掉 ✓ |
| M2 | 探针永远说「有人应答」 | 同上 | 打掉 ✓ |
| M3 | 探针永远说「没人应答」 | `an_agent_that_answers_is_left_alone` | 打掉 ✓ |
| M4 | 空槽也去问一次（丢掉先读槽位那一步） | `a_vacant_slot_is_decided_without_asking` | 打掉 ✓ |
| M5 | 陈旧句柄当成「在运行」 | `a_start_after_the_agent_died_…` | 打掉 ✓ |
| M6 | 丢弃时不清会话 | `a_stale_handle_is_recorded_dropped_…` | 打掉 ✓ |
| M7 | 丢弃时只读不取（`take`→`is_some`） | 同上 | 打掉 ✓ |
| M8 | 丢弃时不写那条记录 | 同上 | 打掉 ✓ |

### 4.1 第一轮有两个变异**存活**，两个洞都是真的

第一轮读数是 **6/8**。两个都查到了根因，没有靠调断言了事：

**M1 存活**。根因不是「用例没覆盖丢弃」，而是**那条断言在说它证明不了的事**：
原断言是「用例结束后槽位是空的」，可是修复后的 `start` 会继续往下走、spawn 失败，
而失败分支自己就会 `stop` 掉槽位——所以空槽**区分不了**「陈旧句柄被 `discard` 丢弃」
与「留着、后来被清理」，而它的消息写的是「a process that ended is dropped, not kept」。
改法两件：① 断言**那条记录**（`discard` 里唯一会写的东西，M1 打掉它就不再出现）；
② 删掉这条用例里的空槽断言，并写明为什么删——该半由 `a_stale_handle_is_recorded_dropped_…`
独占，那里只有 `discard` 会跑，空槽才有含义。

**M7 存活**。根因是**错派**：M7 改的是 `discard` 的内部（`take` → `is_some`，句柄取不走），
而它被指给了 `a_start_after_the_agent_died_…` —— 那条用例的槽位确实是陈句柄、也确实会进
`discard`，但它的两条断言一条看**返回值**、一条看**记录**，M7 两样都不改，所以看不见。
（上一轮它那条空槽断言**在的时候**本可以打掉 M7，而那正是 §4.1 上一段刚认定「不能留着、
因为它同时会被失败分支的空槽满足」的那条——同一个断言既证明不了 M1、又顺带盖住了 M7，
说明它测的是「事后槽位空不空」，而不是任何一条职责。）
改派给 `a_stale_handle_is_recorded_dropped_and_released_with_its_session`：那里
会话被释放、记录存在、槽位为空三件各断言一次，且只有 `discard` 会跑，M7 立刻被打掉。

**这两个洞正是变异表存在的理由**：两条用例的注释都说自己覆盖了「丢弃」，
而 8 条变异里只有把它们改成能红的形状之后，8 条才真的全被打掉。

## 5. `tauri` 的 `test` feature：只进 test 构建

要写出**能红的**用例，就必须让真子进程进入 `AgentProcess(Mutex<Option<CommandChild>>)`，
而此前只有真 Desktop 应用能造出 `CommandChild`（既有用例逐条登记了这一点）。
`tauri` 的 `test` feature 提供 `tauri::test::{mock_builder, mock_context, mock_app, noop_assets}`，
其 `MockRuntime` 之上的 `tauri-plugin-shell` **不是替身**——同一个 crate、同一条 spawn 路径，
所以拿到的是真的 `CommandChild`。

它写成 **dev-dependency**，所以出货构建看不到：

```
cargo tree --manifest-path src-tauri/Cargo.toml -e features,no-dev -i tauri | grep -c 'feature "test"'   → 0
cargo tree --manifest-path src-tauri/Cargo.toml -e features             -i tauri | grep -c 'feature "test"'   → 1
```

**两行都要报**：只报 0 分不清「真的不在」与「查询本身抓不到」。不新增任何 crate（`tauri` 本来就在图里）。

`sidecar::start` 与 `commands::agent::start` 因此泛化到 `R: tauri::Runtime`；
**调用点一个未改**（都传 `Wry` 句柄，类型推断）。

## 6. 读数

| 项 | T-01 结束时 | 现在 | 差 |
|---|---|---|---|
| `cargo test --workspace` | 344 passed / 0 failed / 3 ignored | **348 passed / 0 failed / 3 ignored** | +4 passed |
| 编译警告 | 7 | **7** | +0 |
| 套件耗时 | 2.36s | **1.93s** | −0.43s |

新增的 4 条就是 §4 表里被点名的那四条；本次**没有**新增 `#[ignore]` 真机臂
（仍 3 条），因为 T-02 要的「真东西」是一个真的 `CommandChild`，而它在套件内就够得着——
不像 T-01 必须起一个真的 Agent 进程才能证明「那行宣告真的在 `listen()` 之后」。

**唯一一处非生产设定，写在这里而不是藏着**：`a_start_after_the_agent_died_…` 把
`config.sidecar.start_timeout_ms` 从出货的 15000 改成 300。原因：守卫放行之后 start 会真的
去 spawn `binaries/wt-media-agent`——那是**未入库的 10 MB 产物**（`.gitignore:9`），
在开发机上有就等满 15000ms，没有就立刻失败，读数随机器而变。这条用例的主语是**守卫**，
它在 spawn 之前就判完，所以之后的等待被压到 300ms。修复前带这个 300ms 也是红的（§2 的转录）。

## 7. 未覆盖项（登记，不静默吸收）

1. **真机臂未做，且不做**：与 §6 同源。T-02 的判据是「槽里那个句柄的性质」，套件内已用真句柄
   覆盖；没有一条读数来自真正的 Desktop 应用 + 真正被杀死的 sidecar。AC-02 因此由
   「先红后绿的复现用例」这一半满足，「真机读数」那一半**未做**——与 D-09 的登记方式一致，
   不以文字充当证据。
2. **`/healthz` 是探针而不是心跳**：探针只判「在不在」，不判「好不好」。
   一个卡死在某个请求里的 Agent 仍会被判 `Running`——这不是本任务的范围（T-03 处理退出，
   任务执行期的健康是另一件事），登记于此免得被读成已覆盖。
3. **`kill` 的结果不记录**：`discard` 里 `let _ = sidecar::stop(child);`。理由是它**两向都会错**——
   已经结束的进程 `kill` 必失败（没东西可信号），卡死的进程 `kill` 必成功；错误在最不要紧的
   情形里出现、在最要紧的情形里缺席。写进了函数文档。
4. **`start` 的失败分支（spawn 失败→`stop`→关会话）仍无独立用例**：与 T-01 §4 第 1 条同源，
   需要 `AppHandle` 走到真正的命令层。T-02 的用例已能到达 `start` 内部，
   但它断言的是守卫的两侧，不是失败分支本身。
5. **Windows / x86_64** 未测（§5 明示不做）。
