# 证据 — T-19 测试不误连真实外部服务（AC-11b）

范围：里程碑 `M-launch-engineering` 的**失败行为**「测试不误连真实外部服务」，对应
§7 Q-08 登记的那处覆盖缺口（计划把 AC-11 整条映射给 T-02，T-02 实测该半**今天无任何规则在守**）。
裁定来源：§7 Q-08；AC-11b。

提交：`wt-media-agent`（见 change.md 的 T-19 行）。
`bash scripts/test.sh` → **365 tests OK, exit=0**（T-09 后 354 → +11）。`.local/` 守卫不响。

改动面：新增 `tests/test_no_external_services.py`（规则 + 对照，11 条），并在 4 个既有测试文件里
加 **5 处 `# network-ok:` 标记注释**（纯注释，逐字 diff 见 §6）。**未动任何生产代码。**

---

## 1. 先量分母：计划给的数字与实测不符，登记偏差

计划（change.md §8 T-19）写的是「41 处网络调用点 / 34 个测试模块」。**实测（未改一行规则前）：**

```
counts: {'modules': 40, 'constructions': 38, 'with_transport': 36, 'urlopen_calls': 3}
```

| 项 | 计划 | 实测 | 处置 |
|---|---|---|---|
| 测试模块 | 34 | **40** | 计划偏低；分母按实测写进测试常量 |
| 网络调用点 | 41 | **38 处客户端构造 + 3 处 `urlopen` = 41** | 数字**对得上**：计划的 41 是这两类之和，不是单一类 |

即：计划的总数没错，是分类粒度不同——它把两类合成一个 41，本规则必须分成两个通道（客户端的判据是
「有没有注入 `transport`」，`urlopen` 的判据是「本函数里有没有 patch」）。模块数 34 → 40 是计划偏低的
真实偏差，按实测登记。

分母断言（`KNOWN_MODULES = 30` / `KNOWN_CONSTRUCTIONS = 35` / `urlopen >= 3`）取的是**地板**而非等值：
等值会让任何新增用例都必须回来改这个文件，而规则要守的是「扫描还在看东西」，不是「树不再长大」。

## 2. 规则先红：第一次跑就报出 5 处，都是真的

规则写完、未加任何标记时，对**真实测试树**跑出：

```
test_bootstrap.py:201: urlopen in _get_healthz() with no patch and no marker
test_cloud_agent_client.py:204: CloudAgentClient(...) without a transport
test_cloud_agent_client.py:210: CloudAgentClient(...) without a transport
test_local_health.py:368: urlopen in _get() with no patch and no marker
test_proxy_extract.py:73: urlopen in test_loopback_endpoint_routes_dynamic_extraction()
    with no patch and no marker
```

五处**都不是误报**，五处也都**不该被修**——它们各自有一个成立的理由，所以走了标记通道而不是改代码：

| 位置 | 为什么合法 |
|---|---|
| `test_bootstrap.py:201` | 打的是同一函数上一段刚起的 loopback HTTP server |
| `test_local_health.py:368` | 同上（`RouteTest._get`） |
| `test_proxy_extract.py:73` | 同上 |
| `test_cloud_agent_client.py:204` / `:210` | **真实传输就是被测对象**（CHG-056 T-04 验的是超时值真的到达请求），`_call` 里 patch 了 `urlopen` |

这正是规则该有的形状：**5 处红、0 处要改代码**。若它跑出来是「0 处红」，那说明规则在空转。

## 3. 一处真误报及其修法：`as urlopen` 绑出来的是 mock，不是库

`test_cloud_agent_client.py:199`（`_call`）里写的是：

```python
with mock.patch.object(urlrequest, "urlopen", return_value=response) as urlopen:
    client.heartbeat("agent-1")
```

`as urlopen` 把 **mock** 绑到了 `urlopen` 这个名字上。规则最初只看「函数名是不是 `urlopen`」，
于是把 `test_noop_executor.py` 里那句 `return urlopen()`（调的就是 mock）判成联网——**这正是驱动
一个假传输最干净的写法**。一条把最干净的测试写法判成违规的规则，第一个被人删掉的就是它。

修法：名字解析成「这个作用域里它被绑成了什么」——

- `as urlopen`（`ast.With.optional_vars`）、函数参数、赋值、注解赋值 → `local`，**跳过**；
- `import urlopen` / `from … import urlopen` → `import`，**照报**（这才是真的到达网络的那条拼写）；
- 都没绑 → 空，照报。

两条配套：

- **优先 `local` 而非 `import`**：同一函数里既有 `import urlopen` 又有 `as urlopen` 时，后者在
  `ast.walk` 顺序上可能后出现。第一版按顺序返回，结果取决于源码行序——那是个随编辑漂移的判定。
  改成「有 local 就 local，否则看有没有 import」，与顺序无关。
- **模块级作用域不得被函数体里的绑定开脱**：`ast.walk(module)` 会把某个**兄弟函数**里的
  `as urlopen` 拎出来，用来豁免模块级的裸 `urlopen()` 调用。故加了 `_own_scope()`：模块级只看
  不进入任何函数/类体的节点；而且**连 `def` 节点本身都不收**——它的参数表属于它自己的作用域，
  一个叫 `urlopen` 的参数对模块级的调用什么也没说。

这一处由对照 `test_control_for_an_imported_urlopen`（配对的另一半）与
`test_control_for_a_patched_urlopen` 两向钉住。

## 4. 变异表：控制臂先绿，7 个变异逐个红，三条真断言各有至少一个变异能红它

探针 `/tmp/t19-mutation-probe.py`：把**真实测试文件**逐次破一处，然后用 monkeypatch `test_files()`
的方式跑**真的那 11 条用例**（不重写断言）。第 0 行是未变异的控制臂。

```
mutation | A1 分母 | A2 无违规 | A3 标记棘轮 | 对照
0 控制：未变异          | green | green | green | green
M1 一个真实标记被删      | green | RED   | RED   | green
M2 一个真实标记丢理由    | green | RED   | RED   | green
M3 真实文件多一处无 transport 的客户端构造 | green | RED | green | RED(2)
M4 真实文件多一处未 patch 的裸 urlopen     | green | RED | green | RED(2)
M5 真实文件多一处未申报的标记              | green | green | RED | green
M6 两处云标记被删        | green | RED   | RED   | green
M7 扫描再也看不到测试树（只剩 1 个文件）    | RED   | green | RED   | RED(1)
```

- A1（分母）、A2（无违规）、A3（标记棘轮）**各自都有变异能红**：A1 ← M7，A2 ← M1/M2/M3/M4/M6，
  A3 ← M1/M2/M5/M6。没有一条断言是「永远绿」的。
- M1 与 M2 的差别是**理由**：M1 把标记整行删掉，M2 只删理由（留下 `# network-ok:`）。两者都红，
  证明「空理由不算通过」不是写在文档里的承诺。
- A2 的报出内容逐条核对过，形态对得上（M3 → `without a transport`，M4 → `no patch and no marker`）。

### 4.1 这张表查出我自己两个对照的缺陷

M1/M2/M6 让**对照臂**也红了，而它们和我种下的东西无关。原因是那两个对照读的是**整棵树的报告**：

- `test_control_for_a_patched_urlopen` 断言的是「全树没有 `no patch and no marker`」；
- `test_control_for_a_rule_that_stops_looking` 断言的是「全树恰好 2 条」。

于是**任何**真实树的变动都会让它们红——红的理由和它们点名的东西无关，且**看起来和控制臂工作正常
一模一样**。改成只读自己种的那个文件（`plant()` 返回过滤到 `test_noop_executor.py` 的报告）。

改完后 M1/M2/M6 不再动对照臂，只剩 M3/M4 会：那两处恰好把违规种进了**同一个文件**，对照「这个文件
里没有违规」的断言因此为真地失败——这是诚实耦合，不是缺陷，**如实登记而不掩盖**。

## 5. 这条规则看不见什么（写进文件头，不是事后补）

- **经助手到达网络**：`test_cloud_agent_client.py` 无 transport 构造客户端、由 `_call` patch
  `urlopen` 后再调用。这是**正确代码**，规则会报，所以它带标记；若哪天 `_call` 不再 patch，本规则
  **不会发现**——标记是给读者的指针，不是证明。
- **构造了但从不调用的外部 URL**：只判构造，所以指向公网却从不使用的客户端能通过。
- `os.system` / 裸 `socket` / subprocess / 换名字到达的客户端工厂：与
  `test_dependency_boundaries.py` 自陈的「运行期派发的模块」同一处边界。
- **注入的假传输有没有被用**：`transport=lambda …: {}` 按形状通过，不判断言是否有意义。

## 6. 逐字 diff：5 处标记，全是注释

```
tests/test_bootstrap.py         | 2 +-   （把标记单独一行，与其余 4 处同形；未改代码）
tests/test_cloud_agent_client.py| 2 ++   （两行注释）
tests/test_local_health.py      | 1 +    （一行注释）
tests/test_proxy_extract.py     | 1 +    （一行注释）
```

`tests/test_no_external_services.py` 为新增文件。**生产代码 0 行改动**，`wt-media-agent` 之外 0 仓改动。
标记数按**文件**冻结（`NETWORK_OK_COUNTS`）而非按行号：行号会因上方任何编辑而失效，届时棘轮红的
理由没人能处理。棘轮两个方向都由 `MarkerRatchetControls` 各出一条对照证明能红。

规则文件自己被排除在**标记计数**之外（它把标记当字符串写着），但仍在**违规扫描**范围内——它扫自己
是应当的，且正确地什么也扫不到（字符串里的标记是 `Constant`，不是调用）。
