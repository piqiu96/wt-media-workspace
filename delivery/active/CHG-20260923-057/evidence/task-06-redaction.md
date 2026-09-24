# 证据 — T-06 脱敏（Agent）

范围：裁定十、十三·7，以及里程碑 `M-launch-engineering` 成功事实 #5 后半
「敏感信息（Cookie/Token/代理密码）不进日志**与诊断包**」。

提交：`wt-media-agent` `b66d7f5`（T-06 主体）、`70c1f93`（共享基类refactor）；
两者各自单独 checkout 跑 `scripts/test.sh` 均 **293 tests OK, exit=0**。

---

## 1. 起点先量：表 15 行，改动前漏 15 行

探针 `/tmp/t06-before-after.py` **import 测试自己的 `CASES`**（不重打一份表，避免漂移），
同一张表分别经改动前后的渲染路径：

```
改动前（普通 Formatter）: 15 行中泄漏 15 行
改动后（RedactingFormatter）: 15 行中泄漏 0 行
```

**对照有效性（这一条先踩了坑）**：第一版探针按 `ast.Assign` 读表，而表是**带注解赋值**
（`CASES: list[...] = [...]`）⇒ 读到 0 行并打印「表 0 行：仍泄漏 0 行」——一个**空转的绿灯**。
改为直接 import 后分母才是 15（`assert CASES` 现在会让空表直接报「对照无效」）。

表本身两列都断言：`gone` 不得出现、`kept`（周围文本）必须仍在；
另有 `test_ordinary_text_passes_through_unchanged` 作反向对照——把整行涂成 `***` 的实现在那 5 条普通文本上会红。

## 2. 掩码的落点是实测选出来的：formatter，不是 Filter

`logging.Filter` 改 `record.msg` **碰不到 traceback**（traceback 由 `Formatter.formatException`
从 `exc_info` 渲染），而 traceback 正是凭据最容易出现的地方。`RedactingFormatter.format`
对**渲染后的文本**下手，因此消息面与 traceback 面同时覆盖，且被四个 handler
（stderr + 三文件）共用 ⇒ 一次改动覆盖所有出口，含终端。

- `test_a_secret_in_the_message_is_masked`
- `test_a_secret_inside_a_traceback_is_masked`（先断言 `ValueError` 已渲染，再断言密码不在）

## 3. 词表不另起一份

`_LEAF` 由 `runtime/config.py` 的 `SENSITIVE_KEY_NAMES`（**拒绝凭据写进出货 TOML 的那份**）生成，
`_`/`-` 两种拼法都收（`proxy_password`、`set-cookie`、`X-Api-Key`）。
`test_every_configured_sensitive_key_name_is_covered` 遍历**真实集合**（分母 ≥10），加名即自动纳入。
键必须是真实凭据名——早先版本让 `https:` 先被当成键、把后面的凭据一起吞掉，故收窄为词表交替。

## 4. 配置对象不自曝（裁定十·Python 侧）

`AgentConfig.runtime_token` 改 `field(repr=False)`：一个词、不会漂移
（手写 `__repr__` 要跟每个新字段保持同步）。
`ConfigObjectReprTest`：`repr`/`str`/f-string 三处都不含 token 值，且 `log_level='WARNING'` 仍可见
（不许整体变桩）。

## 5. 诊断包那一半：实测到一处真泄漏，本 Task 修掉

`environment_facts()` 的 docstring 自称 non-sensitive，token 确实不在（`Field(..., secret=True)`），
但**值**可以是凭据。实测（探针 `/tmp/t06-facts-probe.py`，走真实 `build_components`）：

```
改动前: cloud_base_url = https://alice:pw123456@cloud.example.test/api
        URL 里的密码是否出现: True
改动后: cloud_base_url = https://alice:***@cloud.example.test/api
        URL 里的密码是否出现: False
```

这条路径值得单独修的理由：诊断包走 `print` → **stdout**，不经任何 handler，
而 Rust 侧 `sidecar/drain.rs` 会持续消费 stdout、退出时打尾 20 行 ⇒ 有真实外溢路径。
修法：`environment_facts` 的字符串值统一过 `redact()`（同一处，覆盖所有消费者）。
配对测试 `test_a_credential_inside_a_configured_url_is_masked_in_the_environment_facts`
先断言 host 与 `alice` 仍在，再断言密码不在——负向断言不能靠在空值上通过。

## 6. 顺带：套件里那 27 条 `--- Logging error ---`（先证根因，一次假设被推翻）

现象：全套输出夹着 `--- Logging error --- FileNotFoundError: …/tmpXXXX/.local/logs/agent.log`，**27** 条。

- **第一个假设被判错**：我以为是 T-05 测试文件只恢复 root logger 造成的。据此把共享
  `LoggingStateTestCase` 抽到 `tests/support.py`（这步保留，是真问题），**噪声计数不变（仍 27）⇒ 假设错**。
- 逐用例插桩（替换 `logging.Handler.handleError`）后**点名**：死 handler 集合由
  **`test_bootstrap.py`（9 条用例）**与 **`test_sidecar_entry.py`（1 条）**装进去——
  两者都走真实装配（`build_components`，即裁定要求的**唯一 Logger 入口**），谁都没恢复；
  之后**每条恢复都是把死集合原样放回**，于是整套跑完一直背着它。
  真正打到死 handler 的发射点只有 **9 条用例 / 27 次**，分布在 4 个模块
  （`test_new_task_type` 3、`test_runner_registry` 4、`test_runner_session` 1、`test_runtime_config` 1）。
- **归因实测**：`305975b^`（本 CHG T-04 之前）单开工作树跑同一探针 ⇒ 死集合**当天就在**
  （213 条用例背着它、2 个 handler），但**一次也没打到**（发射点 0 次），故当时无可见噪声；
  到 T-04/T-05 之后是 6 个 handler、27 次命中。**两份计数与集合归属是实测**；
  0 → 27 的直接机制**未定位**（曾设想「macOS 删除目录后仍持打开 fd，写入照旧成功；被关闭后再写才重开失败」，
  但两次实测跑完时死 handler 的流都仍是打开的，故**不作为结论登记**）。
- 修：两个文件继承 `LoggingStateTestCase`；新增机器规则
  `tests/test_logging_state_isolation.py`（凡 import `wt_media_agent.bootstrap` 的测试模块，
  必须有类继承 `LoggingStateTestCase`；分母 ≥2 作对照，规则文件按路径自排除）。
  规则**先红且恰好点名这两个文件**。
- 修的过程中**基类暴露出第二个缺陷**：`AssemblyTests.setUp` 与 `HealthzAuthenticationTests.setUp`
  覆盖了 `setUp` 却没调 `super().setUp()` ⇒ `tearDown` 无状态可恢复，**7 条用例报错**
  （292 tests, `errors=7`）。补 `super().setUp()` 后噪声与泄漏双双归零。

```
死 handler 泄漏报告: 245 -> 0
Logging error 次数 :  27 -> 0
```

## 7. 声明为未覆盖（不得当成已验）

- **没有真机启动臂**：今天生产代码**没有任何 emit 点会带上凭据**（全仓只有 3 个 logger：
  `runner.runner`、`local_api.server`、`runtime.config`），所以「真实进程里 grep 不到 token」
  这条臂只能是**空转**，故不做。本 Task 的接线证据是：掩码挂在唯一的 `configure_from` 入口上，
  而该入口的真实进程行为已由 T-05 的两臂证明。
- **无键、无 JWT 形状的裸 64-hex 不掩**（`_JWT` 刻意窄：泛化「长随机串」会把 id/哈希一并涂掉）。
- `context` 字段今日**无生产点**（T-05 已登记）。
- `MIN_SECRET_LENGTH=8` 以下的配置值**不作字面 needle**（否则 `abc` 会涂掉普通散文；两向都有测试）。
- `local_api` 的 `/api/v1/status` 响应体**本 Task 未断言**：它是契约面（`Local Agent API` 归 agent 仓，
  T-08 的范围），读到的字段里没有凭据来源，但**未测**。

## 8. 验证命令与结果

| 命令 | 期望 | 实际 |
|---|---|---|
| `bash scripts/test.sh` | 只增不减、`.local/` 守卫不响 | **293 tests OK, exit=0**（T-05 后 291 → +1 规则 +1 诊断包用例）；守卫未响 |
| 每个提交单独 checkout 再跑 | 每个提交自身绿 | `b66d7f5` 293 OK / `70c1f93` 293 OK |
| 探针 `/tmp/t06-before-after.py` | 表 15 行由漏 15 → 漏 0 | `15 -> 0` |
| 探针 `/tmp/t06-facts-probe.py` | 诊断包密码由在 → 不在、URL 仍可读 | `True -> False`，`alice:***@host` |
| 探针 `/tmp/t06-leak-probe.py` | 死 handler 报告归零 | `245 -> 0` |
| 探针 `/tmp/t06-emitter-probe.py` | 死 handler 上抛错归零 | `27 -> 0` |
| `.local/` 守卫的对照 | 多一个路径必须报出来 | `comm -13` 对照臂报出 `.local/logs/task.log` |

（探针都在 `/tmp`，不进仓。守卫的第一次对照**无效**——我把目录建在跑之前，BEFORE 里就有它，
故改为对 `comm` 比较本身做对照，见上表末行。）
