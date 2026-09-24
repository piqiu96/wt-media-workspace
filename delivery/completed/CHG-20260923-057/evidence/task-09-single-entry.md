# 证据 — T-09 唯一入口、`state` 必传、`-m` 下的记录名

范围：裁定二（「唯一初始化入口」「禁止 server 重复初始化 Config、component 初始化 Logger」）
与 T-07 顺带实测并登记的 `__main__` 记录名（`evidence/task-07-retention.md` §7）。

提交：`wt-media-agent`（见 change.md 的 T-09 行）。
`bash scripts/test.sh` → **354 tests OK, exit=0**（T-08 后 345 → +9）。`.local/` 守卫不响。

---

## 1. 三件事、三类判据

| 项 | 判据 | 形态 |
|---|---|---|
| ① 删掉 `server.py` 的第二次 `configure_from` | **R11**：AST 规则 + 三个对照 | 规则今天红、修后绿（§2） |
| ② `state` 改必传（`LocalApiServer` 与 `serve`） | 三个用例 + 签名检查 + 变异 | §3 |
| ③ `-m` 下 logger 名不再是 `__main__` | 源码规则（套件）+ **真机 `-m` 进程**（§4） | §4 |

①和③是同一条裁定面的两半：`server.py` 既是那个重复初始化 Logger 的地方，也是那个在 `-m`
下丢掉组件名的地方。

## 2. R11：把「唯一入口」变成机器规则

`tests/test_dependency_boundaries.py` 新增 `r11_single_logging_initializer`，并入既有的
「纯函数规则 + `BoundaryRuleControls` 反例」结构。规则**今天就会红**：

```
R11 wt_media_agent/local_api/server.py:39: imports configure_from from
    wt_media_agent.runtime.logging (CHG-057 T-09: one initializer, in bootstrap)
```

修完（删掉那行 import 与 `main()` 里的调用）转绿，且**只此一处**删掉即可转绿——分母是干净的。

两条被这次实现量出来的事：

- **规则的第一版太宽，会误报正常代码。** 第一版写成「除 `bootstrap/app.py` 外任何模块都不得
  import `runtime.logging`」，跑出来两条：`server.py:39`（真违规）**和 `bootstrap/cloud.py:20`**
  ——后者 `from wt_media_agent.runtime.logging import redact` 引的是**纯函数**，不是初始化器。
  一条会误报在跑的代码的规则，第一个被人削掉的就是它。故收窄成**点名两个初始化器与两条到达路径**：
  符号拼写（`from … import configure_from`）、模块拼写（`from … import logging as rt` 或
  `import wt_media_agent.runtime.logging`）。`runtime/logging.py` 里的 `redact` 类助手不受影响。
- **第三个对照本来与树的状态纠缠。** 「树里没有任何初始化器」这条对照最初只把 `app.py` 的那行删掉，
  于是**真正的违规（`server.py:39`）让它红着**——它红的是别的原因，而且修完才可能绿。
  改成对**每个文件**都删掉该行，规则里只剩「没有初始化器」这一条可能触发。

## 3. `state` 必传：一处被推翻的说法，一处不成立的失效模式

计划（本记录 §8 T-09 ③）把它写成「component 构造器成了**第二个初始化点**」。**独立复核后这句不准**：
裁定二的唯一性说的是 **Config 与 Logger** 的初始化，`LocalAgentState()` 是内存里的可观测状态，
既不是 Config 也不是 Logger。真正成立的是另一件事，而且更贴本 CHG 的主题：

> `state or LocalAgentState()` 让**忘了传 state 的调用方**拿到一个**看起来完全正常**的默认态——
> `agent_id="local-agent-dev"`、`status="idle"`。`/api/v1/status` 于是会描述一个**没在跑**的 Agent，
> 而且没有任何迹象表明它这么做了。

所以修法成立、理由要改。同时复核了更严重的那个失效模式**不成立**：`LocalAgentState` 是普通
dataclass，**没有 `__bool__`/`__len__`**（`local_api/state.py:26-41`），所以 `state or …` 不会把
传进来的 state 丢掉——失效的入口只有「忘了传」，不是「传了个假的」。

修法照本文件既有的先例（`bitbrowser` 就是必传 + 一句为什么），`serve()` 的同名默认一并删掉
（它会把 `None` 显式往下传）。**留一处会静默的默认值，等于留一条「报了个假身份」的路。**

30 个测试构造点显式传 `LocalAgentState()`（9 个文件）。两处必须点名：

- `test_the_bitbrowser_client_must_be_supplied` 原本用 `LocalApiServer()` 断言 TypeError；state 也必传后
  这个 TypeError **改由 state 缺参触发**，测试名说的东西就不成立了 → 改为传 state 再断言，
  使 TypeError 只可能是 bitbrowser。
- 新写的 `test_serve_requires_the_state_it_serves` **第一版是危险写法**：它直接调用
  `serve(bitbrowser=…)`，而在默认值还在时这会**真的去 `ThreadingHTTPServer(("127.0.0.1", 8765))`**
  ——开发者正在跑的 dev Agent 端口。红跑当场报错（该端口被占）。改为**读签名**
  （`inspect.signature(serve).parameters["state"].default is empty`）：要断的事实是「没有默认值」，
  而调用它要么碰到 8765、要么在 scratch 端口上阻塞进 `serve_forever`。**判据不许伸向 8765。**

## 4. `-m` 下的记录名：真机量到，且证明这条判据能红

`scripts/verify-health.sh:11` 与 `scripts/start-health.sh:44` 都用
`python -m wt_media_agent.local_api.server` 起进程。`-m` 下模块以 `__main__` 执行，
`getLogger(__name__)` 于是把 HTTP 侧记录全挂在 `__main__` 名下——组件名没了，这正是
T-04 的路由与 `wt_media_agent` 组件前缀要防的事。

修法：`LOGGER_NAME = "wt_media_agent.local_api.server"` 显式写出；它在 **import 路径上的取值与
`__name__` 完全一致**，故对三条生产入口零变化。

套件里是两条互补的检查（各自看不见全部）：`logger.name` 的**值**（只在 import 模式下能读）
与源码里**不得出现 `__name__`**（`-m` 模式的差异只在这里）。真机探针 `/tmp/t09-real-run.py`：

```
PASS  A0 the -m process came up and answered /healthz  -- b'{"status":"ok","service":"wt-media-agent","mode":"m1"}'
PASS  A2 the surviving initializer wrote agent.log  -- 114 bytes
PASS  A3 no record is named __main__ (and the parse found some)  -- names=['wt_media_agent.local_api.server']
PASS  A4 the HTTP side logs under the component name  -- names=['wt_media_agent.local_api.server']
PASS  A5 the listening record is the module's own logger
      -- ['2026-09-24T14:38:05 [INFO] wt_media_agent.local_api.server: wt-media-agent local API listening on 127.0.0.1:57166']
PASS  A6 agent.log / task.log / error.log 三者都在（留下那个初始化器是承重的）
PASS  A7 /api/v1/health 200        PASS  A8 响应体形状正常
11/11 PASS
```

**同一探针的变异**（把 `LOGGER_NAME` 改回 `__name__`，跑完还原）：

```
FAIL  A3 no record is named __main__ (and the parse found some)  -- names=['__main__']
FAIL  A4 the HTTP side logs under the component name  -- names=['__main__']
8/11 PASS
```

⇒ 这条判据**有能力失败**，且 T-07 登记的缺陷是真的（实测记录名就是 `__main__`）。

**A3 的第一版自己空转**：解析器找 `"]: "`，而真实格式是 `] <name>: `（时间戳后是 `] ` 加空格），
于是一个名字都没解析出来，A3 因为「没有东西可查」而**通过**。加 `bool(names)` 分母并修正解析后
才成为真检查。这是本 CHG 第三处「检查自己先坏了」（前两处在 `evidence/task-08-health.md` §1）。

## 5. 六个变异（套件层）

探针 `/tmp/t09-mutation-probe.py`，控制行先跑：

```
mutation                                   verdict  tests that noticed
(control, nothing mutated)                 OK       no test noticed
state gets a default again                 RED      test_the_state_must_be_supplied
serve's state gets a default again         RED      test_serve_requires_the_state_it_serves
the logger name comes from __name__ again  RED      test_the_logger_name_does_not_come_from___name__
the duplicate initializer comes back       RED      test_r11_only_bootstrap_initializes_logging
R11 stops looking (returns no violations)  RED      test_r11_control_for_a_tree_with_no_initializer,
                                                    test_r11_control_for_the_module_spelling,
                                                    test_r11_control_for_the_symbol_spelling
```

最后一行是**对照的对照**：把规则改成 `return []`，三个反例全红 ⇒ 它们真的在检规则，
而不是「规则找不到东西」时也一样绿。

## 6. 一处如实登记的「测不出差异」

第二次 `configure_from` **没有可观测的独立后果**：`configure_logging` 是幂等的
（`runtime/logging.py:397` 的 docstring 就是这条），且 `_prepare_log_dir` 与三文件声明都是重复安全的。
所以本 Task 拿不出「删掉它前后行为不同」的读数——**它的害处是重复本身**（一处会漂移出第二个真相源），
判据只能是结构性的 R11。这不算遗憾，但要写清楚：不能声称有一个行为差异。

## 7. 声明为未覆盖 / 未取证

- **Windows 未取证**（同 §5.8 的既有登记）。
- 真机只跑了 `-m` 这一条入口；`bootstrap/local.py`、`bootstrap/sidecar.py` 两条入口靠
  既有的 354 条套件（含 `test_bootstrap.py` 的真实装配）覆盖，**未单起进程**。
- R11 看不见运行期派发的名字（`getattr`/`importlib`/字符串拼出的模块名）——与
  `test_dependency_boundaries.py` 文件头声明的既有边界一致。
- `serve()` 必传只由**签名**断言（理由见 §3），没有「调用它并断言 TypeError」的真机读数。

## 8. 验证命令与结果

| 命令 | 期望 | 实际 |
|---|---|---|
| `bash scripts/test.sh` | 只增不减、`.local/` 守卫不响 | **354 tests OK, exit=0**（+9）；守卫未响 |
| `python3 -m unittest tests.test_local_api_server tests.test_dependency_boundaries` | 全绿 | OK（46 条） |
| 探针 `/tmp/t09-mutation-probe.py` | 五个变异各打掉自己的用例 / 对照 | 见 §5；控制行先绿 |
| 探针 `/tmp/t09-real-run.py` | 真机 11/11 + 变异 8/11（A3/A4 红） | 见 §4 |
| R11 的阳性对照 | 三个反例各自出红 | §2 与 §5 末行 |

（探针都在 `/tmp`，不进仓。）
