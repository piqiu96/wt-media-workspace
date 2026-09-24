# 证据 — T-21 Agent 侧请求级 `operation_id`

范围：§5 Scope/Add 要求、§8 却**无任务承接**的 Agent 侧进程内 `operation_id`（本次会话用户裁定补
T-21 交付）。它是 §8 **AC-06**（日志可定位问题）在 Agent 侧的最后一块：T-04 证了三文件路由、T-05 证了
`error.log` 五字段、T-16 证了 Desktop 侧 `agent.supervisor` 的五个生命周期记录，但「同一次请求写了哪几行」
在 Agent 侧此前无任何字段可依。

提交边界：

| 仓 | commit | 内容 |
|---|---|---|
| `wt-media-agent` | `5570906` | `src/wt_media_agent/runtime/logging.py`（+94/−16）、`src/wt_media_agent/local_api/server.py`（+26/−0）、`tests/test_log_operation_id.py`（+304，新文件）；提交后 `git status --porcelain` 为空 |

一个 id 与「在哪个提交上量的」：

| 文件 | sha256 | 说明 |
|---|---|---|
| `runtime/logging.py`（修后） | `df71289a8a1f6eed503f6dd45517accd71367d87b8422609c2d4b0b073151fa9` | = `5570906`，提交后重算未变 |
| `local_api/server.py`（修后） | `fcb6620b56c81c99645e1b9fb2704e6c49d91525f56dc3447f925894fb84a56d` | = `5570906`，提交后重算未变 |
| `tests/test_log_operation_id.py` | `ed93a16128d424c6f64604fd9e13fb9384fd8b504ca61974aff1c0ceae915f31` | 新文件，= `5570906` |
| `runtime/logging.py`（修前） | `d82d52efaa5f63351477abf64ebd4970c365dbd61c4147e643ba3c22db8251cd` | = `65725f4`，**＝ T-20 证据里的「修后」值** |
| `local_api/server.py`（修前） | `5ea029904e086c8835d667812bd4326a98a438e084a04712613d183a20867046` | = `65725f4` |

两个修前值都取自 `65725f4`（T-20 的提交，即本 Task 的基点）；`/tmp/t21/pre` 由 `git archive HEAD src`
展开，不是拷的工作树，所以「修前」这棵树里不含本 Task 一行代码。

---

## 1. 交付形态

| 处 | 内容 | 为什么不能是别的 |
|---|---|---|
| id 源 | `secrets.token_hex(8)`，生成在 `local_api/server.py` | `secrets` 该模块**已 import**（绑定 token 用），`dependencies = []` 不变。生成点放服务端而不放 `runtime/logging.py`：那个模块管「字段落在行里哪个位置」，「什么算一次请求」是服务端的问题 |
| 载体 | `contextvars.ContextVar`，落在 `runtime/logging.py`（与 `ERROR_CODE_FIELD` 等字段名并列） | 放 `local_api` 会倒置 ADR-0016 的分层。用 contextvar 而非 thread-local：`ThreadingHTTPServer` 每连接一线程，thread-local **今天碰巧能用**，但请求里任何一段搬到执行器就失效 |
| 边界 | 覆写 `AgentHandler.handle_one_request`（`make_handler` 内），`try/finally` 复位 | 这个位置 **upstream 于 `_check_auth`、`do_OPTIONS` 与 `send_error`**，所以 401 / 404 / 畸形请求行**构造上**都在一个 id 里，且以后新加的 `do_*` 不会忘记设。`finally` 是必须的：请求以抛异常收场时 id 也不得活过它 |
| 进行方式 | formatter 的 `prepare` 钩子盖 `record.operation_field`，`FMT`/`ERROR_FMT` 各加 `%(operation_field)s` | 沿用 T-05 的落点结论（字段是**行的形状**的一部分，归塑造行的那一处），不碰 `record`、不用 `extra`。名字**故意不叫** `operation_id`：调用方传 `extra={"operation_id": …}` 时不会被这里静默盖掉 |
| 无请求时 | 渲染成 `""`（不是 `operation_id=none`） | 请求外的行**逐字**保持今天的形状——既有那批形状断言因此一行都不用改（§5 真机臂把这条量成了等式） |
| `error.log` 位置 | logger 名之后、`error_code` 之前，与另两文件同一位移 | 裁定六。D-03 的五字段一个不少、顺序不变、message 仍最后 |
| 线上 | **不发 header、不发 query、不进 sidecar 环境变量**（裁定九 / D-10） | T-17 刚把 Desktop 出站请求的头集合逐字钉住，这一侧不能倒回去把它推翻。用例断言两个响应（头集合 + body）里都不含该 id |

`_single_line(value)` 从 `_field` 里提出来，`_operation_field` 复用它：id 今天是本地生成的，但一个能把换行
带进格式串的字段会在「一行一条记录」的文件里伪造记录。`NoTracebackFormatter` 因此不再自带 `format`
（它的「只 isolate 一次」理由挪进了父类 `format` 的 docstring），只剩一行 `prepare` 调 `super().prepare`。

**接口零变化面**：`redact()`、`configure_from()`、`set_global_default` 调用点、`ERROR_FMT` 的五个字段名、
`NO_VALUE`、`OWNED_TARGETS` 都未动；新增的公开面只有 `OPERATION_ID_FIELD` / `begin_operation` /
`end_operation` 三个名字。

## 2. 先红

新用例与实现同批写入，所以「先红」不能靠「测试先写」。第一次跑出来的红是 **ImportError**（`begin_operation`
还不存在）——那种红什么都证明不了，跟没跑一样。因此实现**分两步**落，让接线的红是行为性的：

| 步 | 落什么 | 读数 |
|---|---|---|
| 第 1 步 | 字段 API（contextvar + `begin_*`/`end_*`/`_operation_field`）+ 两个 `FMT` 的槽位 + `prepare`/`format` | **6 pass / 2 fail**，两个失败**恰是两条真 HTTP 用例**（`test_each_request_gets_its_own_id_and_the_line_says_so`、`test_the_id_is_set_before_the_request_line_is_read`）——字段机制齐了，接线的窟窿看得见 |
| 第 2 步 | `handle_one_request` 覆写 | **8 tests OK** |

这跟我此前存的那条规则一致：`ImportError` 式的红是空的，接线路径必须先有真实协作对象，再让缺口在行为上显形。

## 3. 一个测不到的界，如实登记：per-request 与 per-connection 在线上不可分

`BaseHTTPRequestHandler` 没有设 `protocol_version`（`server.py` 里 `server_version` 有值而
`protocol_version` 无值）⇒ 走 HTTP/1.0 ⇒ **一个请求一条连接、答完即关**。于是「id 按请求生成」与
「id 按连接生成」在真实 socket 上**产出完全相同的行**，行为用例**区分不了**这两者。

所以 `finally` 的**顺序**（复位不可能先于处理）与「设在 `handle_one_request` 而不是 `handle`」这两条，
**只有结构覆盖**：`test_the_id_is_set_before_the_request_line_is_read` 读 wrapper 源码，断言
`begin_operation` 在处理之前、`finally:` 在处理之后、`end_operation` 在 `finally` 体内。这条用例在
docstring 里**自己写明**它是结构断言、弱于行为断言，并说明它代表的行为没有文件可落（401/404/畸形请求行
都在写任何记录之前返回）。

§4 的 **M7 打掉这个用例、且只打掉这个用例**——这正是上面对「只有结构覆盖」的实测：换成按连接分配，
四个行为用例**全绿**。

## 4. 变异（控制行先绿：`379 tests OK`）

驱动 `/tmp/t21_mutate.py`：每次改**一处**、跑全量套件、按 sha256 还原，改动的锚点必须**恰好命中一次**
（锚点不唯一即报 `ANCHOR PROBLEM` 并跳过，不算 KILLED）。**9/9 KILLED，0 SURVIVED**：

| # | 改掉什么 | 判定 | 打掉自己的用例 |
|---|---|---|---|
| M1 | 请求内完全不设 id（函数体只剩 `super().handle_one_request()`） | KILLED | `test_each_request_gets_its_own_id_and_the_line_says_so`（**行为**）、`test_the_id_is_set_before_the_request_line_is_read`（结构） |
| M2 | 整进程一个固定 id（`secrets.token_hex(8)` → 字面量） | KILLED | `test_each_request_gets_its_own_id_and_the_line_says_so` |
| M3 | `FMT` 去掉槽位（`agent.log`/`task.log` 不再渲染） | KILLED | `…the_field_sits_after_the_logger_name…`、`…an_id_is_scoped…`、`…each_request_gets_its_own_id…`（3 条） |
| M4 | `ERROR_FMT` 去掉槽位 | KILLED | `test_error_log_keeps_its_fields_in_order_with_the_id_inserted` |
| M5 | `ERROR_FMT` 把 id 挪到 `error_code` **之后** | KILLED | 同上（顺序那一条） |
| M6 | 复位改清空（`reset(token)` → `set("")`） | KILLED | `…an_id_is_scoped_and_does_not_outlive_its_request`（嵌套请求的外层 id 回不来） |
| M7 | 按连接分配（wrapper 从 `handle_one_request` 挪到 `handle`） | KILLED | **只有** `test_the_id_is_set_before_the_request_line_is_read`——见 §3 |
| M8 | 永不复位（删掉 `_OPERATION_ID.reset(token)`） | KILLED | `…an_id_is_scoped…`、`…error_log_without_a_request_keeps_the_none_placeholder`、`…a_record_written_outside_a_request_has_no_id`（3 条） |
| M9 | id 从响应头出去（`send_header("x-operation-id", …)`） | KILLED | `…each_request_gets_its_own_id_and_the_line_says_so`（头集合那一段） |

M6 与 M2 都 KILLED 说明「复位是**恢复**而非清空」「两个请求不同 id」这两条是**行为**覆盖的，不是靠结构断言兜的；
只有 M7 这一类（分配边界的位置）落在结构覆盖上，已按 §3 点名。

## 5. 真机臂：真实进程 + 两次真实 HTTP 请求

脚本 `/tmp/t21/real_arm.sh`，两臂同源（`WS` 指向哪棵树），scratch 端口 **18771**、两个死端口
（18792/18793）保证请求必失败、`WT_MEDIA_LOG_FILE`/`WT_MEDIA_AGENT_DATA_DIR` 都在 `/tmp`。**不碰
`:8765`/`:18080`/`:54345`**，跑完 `left listening: 0`。两臂各发两次真实 POST
（`/api/v1/bit-browser/profile-create`，带 `Authorization: Bearer <scratch token>`），两次都 502（死端口），
因此每次请求**两条**记录（`…profile_create.start` + `…profile_create.failure`）——比单条更能证明 id 是
**按请求**分组的。

### 臂 A：修前（`/tmp/t21/pre`，`git archive HEAD src`）

```
2026-09-24T19:05:53 [INFO] wt_media_agent.local_api.server: wt-media-agent local API listening on 127.0.0.1:18771
2026-09-24T19:05:54 [INFO] wt_media_agent.local_api.server: local_api.profile_create.start name=first-request group_id=g-1
2026-09-24T19:05:54 [WARNING] wt_media_agent.local_api.server: local_api.profile_create.failure name=first-request group_id=g-1 duration_ms=12 error=BitBrowser Local API request failed: <urlopen error [Errno 61] Connection refused>
2026-09-24T19:05:54 [INFO] wt_media_agent.local_api.server: local_api.profile_create.start name=second-request group_id=g-1
2026-09-24T19:05:54 [WARNING] wt_media_agent.local_api.server: local_api.profile_create.failure name=second-request group_id=g-1 duration_ms=0 error=BitBrowser Local API request failed: <urlopen error [Errno 61] Connection refused>
```

### 臂 B：修后（`/tmp/t21/ws`）

```
2026-09-24T19:05:47 [INFO] wt_media_agent.local_api.server: wt-media-agent local API listening on 127.0.0.1:18771
2026-09-24T19:05:48 [INFO] wt_media_agent.local_api.server: operation_id=927a813c8e69b04c local_api.profile_create.start name=first-request group_id=g-1
2026-09-24T19:05:48 [WARNING] wt_media_agent.local_api.server: operation_id=927a813c8e69b04c local_api.profile_create.failure name=first-request group_id=g-1 duration_ms=12 error=BitBrowser Local API request failed: <urlopen error [Errno 61] Connection refused>
2026-09-24T19:05:48 [INFO] wt_media_agent.local_api.server: operation_id=925cc1c99adc2bce local_api.profile_create.start name=second-request group_id=g-1
2026-09-24T19:05:48 [WARNING] wt_media_agent.local_api.server: operation_id=925cc1c99adc2bce local_api.profile_create.failure name=second-request group_id=g-1 duration_ms=0 error=BitBrowser Local API request failed: <urlopen error [Errno 61] Connection refused>
```

### 断言（`/tmp/t21/assert_arm.py`，含分母与对照）

| 断言 | 读数 |
|---|---|
| 对照：两臂行数相同、都服务了两次请求 | 各 **5** 行，`profile_create.start` 各 **2** |
| 对照：`operation_id` 这个针在**修前**日志上**打得中 0 条** | 分母 5 行，命中 **0** ⇒ 这个针**会**失败，不是万能匹配 |
| 修后日志上命中数 | 分母 5 行，命中 **4**（=四条请求记录） |
| 一次请求的记录共用一个 id | `{'first-request': {'927a813c8e69b04c'}, 'second-request': {'925cc1c99adc2bce'}}`，各 1 |
| 两次请求的 id 不同 | 成立 |
| start 与 failure 两条记录同 id | 成立 |
| **进程自己写的启动行不带 id** | 成立（那条 `listening on` 停在主线程，不在任何请求里） |
| 去掉 id 字段后，修后每一行与修前**逐字相等** | 成立 ⇒ 这 5 行的差别**只有**插入的字段本身 |

最后一条是 §1「无请求时渲染成 `""`」在真机上的等式形式：不是「没有 id」，而是**除字段外一字不差**。

## 6. 登记（不静默吸收）

- **SSE 流整条共用一个 id**：一条流是一次 `handle_one_request` 调用，所以它写的每一条记录共享一个 id，
  而不是一个事件一个 id。有意为之（id 的单位是「一次请求」），已写进 wrapper 的 docstring。
- **关联范围仅请求内、处理线程内**：contextvar 不跨线程。实测（`/tmp/t21/threads.py`，同一进程内）：

  ```
  wt_media_agent.runner.task: operation_id=1111111111111111 on the request thread
  wt_media_agent.runner.task: on a runner thread
  ```

  请求线程上写的带 id，同一请求里另起的线程写的不带 ⇒ `runner.task` 的记录仍只能靠 `task_id` 关联，
  与 T-05 既有的边界一致。跨端串联仍未交付（D-10 不变）。
- **`error.log` 的 id 是 D-03 五字段之外的第六个可选字段**：裁定六已批准，位置与另两文件同一位移。
- **AC-06 的另一半仍不覆盖**：`context` 通道今天**无生产点**（T-05 的既有登记），`operation_id` 落地**不**
  使那一条变绿。

## 7. 读数与非覆盖

- 模块：`PYTHONPATH=tests python3 -m unittest tests.test_log_operation_id` → **8 tests OK**。
- 全量：`bash scripts/test.sh` → **379 tests OK**（**371 → +8**，只增不减）。
- 本 Task **未**重跑 T-20 的两条登记臂（`error.log`/`task.log` 的真机臂）与 Desktop 侧任何臂；
  `error.log` 的 id 位置仅由单测（M4/M5 各自打掉顺序那条）覆盖。

## 8. 复现

```bash
cd wt-media-agent
PYTHONPATH=tests python3 -m unittest tests.test_log_operation_id -v
bash scripts/test.sh
python3 /tmp/t21_mutate.py                 # 控制行先绿；9/9 KILLED
mkdir -p /tmp/t21/ws /tmp/t21/pre
git archive HEAD src | tar -x -C /tmp/t21/pre && cp -R src /tmp/t21/ws/
WS=/tmp/t21/pre ARM=/tmp/t21/pre_out bash /tmp/t21/real_arm.sh   # 对照臂
WS=/tmp/t21/ws  ARM=/tmp/t21/fixed   bash /tmp/t21/real_arm.sh   # 修后臂
python3 /tmp/t21/assert_arm.py                                   # 全部断言 + 分母 + 对照
```
