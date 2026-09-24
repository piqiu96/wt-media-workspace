# 证据 — T-08 `GET /api/v1/health` 聚合健康检查

范围：架构基线 §5.6:1125-1130 与 ADR-0016 §10——`/healthz` 冻结不扩展；新增
`GET /api/v1/health` 返回 Agent 版本、Agent 状态、Cloud 状态、BitBrowser 状态、Storage 状态；
**不得触发任何对外写请求（含 heartbeat）**，**不得因依赖不可用而抛异常**，只能把对应状态降级为
`abnormal` 或 `unknown`。契约 `contracts/local-agent-api/v1/local-agent.openapi.yaml` 同步。

提交：`wt-media-agent`（见 change.md 的 T-08 行）。
`bash scripts/test.sh` → **345 tests OK, exit=0**（T-07 后 320 → +25）。

---

## 1. 十二个变异：先量「谁在撑这条断言」

新写的 `local_api/health.py` 第一次跑红的只是 `ImportError`，**它证明不了任何行为**（T-07 的
同一条教训）。故改量变异：逐个把实现里的机制关掉，看哪些用例倒。探针 `/tmp/t08-mutation-probe.py`，
控制行先跑（不绿即探针无效）：

```
mutation                                                  verdict  tests that noticed
(control, nothing mutated)                                OK       (nothing -- the probe is invalid)
cloud: routine outage unmapped                            RED      test_cloud_refused_degrades_to_abnormal_without_raising,
                                                                   test_cloud_timeout_degrades_to_abnormal,
                                                                   test_the_route_answers_200_when_every_dependency_is_down
bitbrowser: unreachable unmapped                          RED      test_bitbrowser_unreachable_degrades_to_unreachable,
                                                                   test_one_dead_dependency_does_not_hide_the_others,
                                                                   test_an_unexpected_failure_degrades_to_unknown_and_is_logged,
                                                                   test_the_route_answers_200_when_every_dependency_is_down
storage: probe failure not caught                         RED      test_storage_that_cannot_be_read_degrades_to_abnormal,
                                                                   test_the_route_answers_200_when_every_dependency_is_down
unexpected failure folded into abnormal                   RED      test_an_unexpected_failure_degrades_to_unknown_and_is_logged
probe reaches Cloud with an HTTP client                   RED      test_the_health_module_imports_no_http_client
roll-up forgives unknown                                  RED      test_no_cloud_endpoint_and_no_store_are_unknown_not_abnormal, +5
/healthz extended                                         RED      test_healthz_is_byte_for_byte_unchanged,
                                                                   test_the_two_paths_are_separate
cloud endpoint not forwarded by main()                    RED      test_the_production_entry_points_forward_the_cloud_endpoint
cloud endpoint not forwarded by bootstrap/local           RED      test_the_production_entry_points_forward_the_cloud_endpoint
storage probe creates the database it was asked to check  RED      test_a_missing_database_fails_and_is_not_created
storage probe does not read the schema                    RED      test_a_database_with_no_schema_fails
```

三条被这次变异量出来的东西，都不是顺手写的：

- **「探针不走 HTTP 客户端」那条检查第一版是假绿**。它解析 AST 收集 import 时，对
  `from urllib import request` 只取了 `node.module`（`"urllib"`），于是 deny-list 里的
  `"urllib.request"` 永远匹配不上。变异「往 health.py 加一行 `from urllib import request`」
  第一次跑出 **OK（没有用例注意到）**——这正是「检查没能力失败」。修法是两种写法都拼出完整点号名，
  修完该变异转 RED。**这条检查本身是被变异救回来的。**
- **真机探针的就绪判断是空转**。探针的 `get()` 为了把「处理函数死了」记成事实而宽catch 一切异常，
  我把它当成就绪探针用 ⇒ 第一次连接被拒也当成「起来了」，臂 A 的九项断言全跑在一个没人服务的端口上
  （实测形态：`URLError: Connection refused` 而 `/healthz` 却「通过」）。改用**严格**请求后就绪才成立。
  与 T-07 的启动清理同型：**判据自己先坏了，结论就全是假的**。
- 「当前文件永不被删」那类**靠副作用成立**的用例这次也有一处：臂 B 里「各依赖都不可用」原本用
  `store=None`，它的 `storage: unknown` 是**「没配存储」**这条路给的，不是**「存储坏了」**给的，
  于是把存储探针的失败处理整个删掉那条也不会红。改成指向真实缺失的库文件后才真的撑住该断言。

## 2. 真机两臂（判据在真实进程的真实响应里）

单元测试只锁模块；「一个真进程会不会 200、会不会发请求」只能在进程里看。两臂都走真实入口
`python -m wt_media_agent.local_api.server`，scratch 端口、临时树、**全程未碰**
BitBrowser `:54345`、Cloud `:18080`、dev Agent `:8765`。探针 `/tmp/t08-real-run.py`。

臂 A：Cloud = 一个只计数不答话的 TCP 监听；BitBrowser = 一个只答 group 列表的 HTTP double。

| 判据 | 结果 |
|---|---|
| A0 响应体 | `{"status":"ok","service":"wt-media-agent","agent_version":"0.2.2","agent_status":"idle","dependencies":{"cloud":{"status":"normal"},"bitbrowser":{"status":"normal"},"storage":{"status":"normal"}}}` |
| A1 HTTP 状态 | 200 |
| A4 **Cloud 被连上，一个字节也没发** | `connections=1 received=b''` |
| A5 BitBrowser 探针是什么 | `['POST /group/list']`（读，非变更） |
| A6 `/healthz` 逐字 | `{"status":"ok","service":"wt-media-agent","mode":"m1"}` |
| A7 `/api/v1/status` | 200，形状未变（该 double 只答 group 列表，值判决在臂 B） |
| A8 聚合耗时 | 0.030s |

臂 B：Cloud 与 BitBrowser 都指向已关闭的回环端口，启动后再删掉 Agent 自己的库文件。

| 判据 | 结果 |
|---|---|
| B6 **重测 T-04 的题设**：BitBrowser 死端口 | `/api/v1/status` → **200 + `unreachable`**，不抛（不是假设，是实测） |
| B2/B3 三依赖全不可用 | `/api/v1/health` → **200**，`cloud=abnormal bitbrowser=unreachable storage=abnormal`，`status=abnormal` |
| B5 `/healthz` | 仍逐字 `{"status":"ok","service":"wt-media-agent","mode":"m1"}` |
| B10 对照：同一时刻的 `/api/v1/status` | **-1**（连接被关、无响应）——存储没了它**确实抛** |
| B7 进程 | 仍然活着 |
| B8 降级响应耗时 | 0.005s |
| B9 `agent.log` | 3 条 `local_api.health.*.degraded` 警告，**无一条带 traceback** |

B10 是本节最要紧的一行：裁定要求的是「聚合健康检查不抛」，而**既有的** `/api/v1/status`
在存储不可用时是抛的（处理函数异常 → 连接关闭、无响应）。这不是本 Task 引入的，也不在本
Task 的改动范围内（裁定只约束聚合端点），故**只如实登记、不改它**——但它正好说明这条裁定在
防的是什么，也让「聚合端点不抛」有了一个同进程的反例作对照。

「不触发对外写请求」的判据是 A4：Cloud 侧是个真监听，它**接受到了连接**（说明探针确实去连了）
且**读到的字节数恰好为 0**（说明连上之后什么都没发——没有 HTTP 请求行、没有 heartbeat、没有
携带任何凭据）。这是对裁定那句话的直接量测，不是承诺。

## 3. Cloud 状态的口径：可达性，不是健康

本 Agent 的 Cloud 客户端**只有写接口**（`clients/cloud/client.py` 里 register / heartbeat /
claim_task / report_task / register_local / report_runtime / 两个敏感任务 permit，无一只读），
而裁定禁止健康检查发写请求。故 Cloud 状态唯一诚实的来源是**不需要请求的那个信号**：能不能和配置的
host:port 建立 socket。含义被写进契约与本模块 docstring：**连接被接受 = `normal`，不代表 Cloud 认可
这个 Agent**（token 被拒也仍是 `normal`）；更宽的问题归 `/api/v1/status`。

- 空/非 http(s) URL、端口不是数字 → `unknown`（没有可探的端点，不是端点挂了）；
- 拒绝/超时 → `abnormal`；
- 探针超时 2.0s，注入式 `connect`，模块内除 `socket.create_connection` 外没有任何出站调用（§1 的
  变异守着这一条）。

另一种读法（「连也不许连」）会把 Cloud 状态永远钉在 `unknown`，使裁定的「Cloud 不可用 → 降级」
一项无法取证。本 Task 按字面「不得触发任何对外**写请求**」实施，并在此写明该判断。

## 4. `storage.probe()` 的三处取舍

新增 `CheckpointStore.probe()`（读一行，什么都不写）：

- 读的是 `task_checkpoints` 而不是 `SELECT 1`：能开文件不等于能执行任务，没迁移过的库应当报坏；
- **库文件不存在即失败，绝不创建**：`sqlite3.connect` 会顺手建一个空库，那等于「你要我验的东西我自己造好了」，
  建库属 `apply_migrations`（bootstrap）的事，不属探针；
- 它是唯一**显式 close** 的 store 方法（其余 `with self._connect()` 只提交不关闭，见 `storage/sqlite.py` 的说明）：
  健康端点会被周期性轮询，一次轮询漏一个连接不可接受。

## 5. 声明为未覆盖 / 未取证

- **只验了回环**。Cloud 探针在真机上量的是「回环端口被拒」（瞬时、`abnormal`），**没有**量到
  「远端不可达导致的 2s 超时」在真进程里的表现；超时分支只有注入式单元测试
  （`test_cloud_timeout_degrades_to_abnormal`）。
- **Windows 未取证**（同 §5.8 的既有登记）。
- 契约里 `/api/v1/health` 的 schema 是**手写同步**的：本仓没有 openapi 校验器
  （`grep -rln openapi src tests scripts` 零命中），本次只用 `ruby -ryaml` 验过它能解析、
  路径与 schema 齐全，**没有**做「响应体符合 schema」的机器校验。
- BitBrowser 探针是 `group_list`（读、轻），因此只能给 `normal`/`unreachable`；`identity_unverifiable`
  **不会**出现在聚合里——身份校验仍只在 `/api/v1/status`。这是取舍，不是遗漏。

## 6. 验证命令与结果

| 命令 | 期望 | 实际 |
|---|---|---|
| `bash scripts/test.sh` | 只增不减、`.local/` 守卫不响 | **345 tests OK, exit=0**（+25）；守卫未响 |
| `python3 -m unittest tests.test_local_health` | 25 条全绿 | OK |
| 探针 `/tmp/t08-mutation-probe.py` | 12 个变异各打掉自己的用例 | 见 §1 表；控制行先绿 |
| 探针 `/tmp/t08-real-run.py` | 两臂判据全绿 | **20/20 PASS** |
| `ruby -ryaml` 解析契约 | 路径与 schema 齐全 | `/api/v1/health` + `AggregateHealth`/`DependencyStatus`，version `2026.09.24.1` |
| `.local/` 是否被写 | 不写 | `find .local -newermt '-2 hours'` 零命中 |

（探针都在 `/tmp`，不进仓。）
