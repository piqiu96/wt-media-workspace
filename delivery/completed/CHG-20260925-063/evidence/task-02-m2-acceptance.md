# Evidence: T-02 `verify_m2_acceptance.py` 转绿

- CHG: `CHG-20260925-063`
- Task: `T-02`
- Date: 2026-09-25
- Type: command
- Status: PASS

## Purpose

消除 `verify_m2_acceptance.py` 的 5 条红项，并**加固**它真正该守的那一层。
改前 5 红全部是跨仓源码字面量（`change.md` §4.2），改后 `exit=0`。

## D-01 与 D-02 的张力，以及本轮的解

D-01 规定「跨仓**源码字面量**断言不再作为门禁判据」，而 D-02 说 binding-ticket 那条要
「断言改指该处真实强制点」。若照字面执行 D-02，就会**再加一条跨仓源码字面量**，与 D-01 冲突。
测量之后张力解开：

1. **真正的强制点在 Cloud，且其语义覆盖已在 Cloud 自己的套件里**——
   `wt-media-cloud/internal/modules/runtimebinding/service/service_test.go:126`
   `TestRegisterConsumesTicketOnceAndIssuesHashedCredential`（函数名即「ConsumesTicketOnce」）。
   **本仓门禁不重复跑别的仓的 Go 测试**，也不应在自己这里复述它的实现。
2. **schema 那一层是可持久断言的**：`migrations/20260714_004_agent_runtime.sql` 定义
   `used_at DATETIME(6) NULL` 与 `UNIQUE KEY uq_local_agent_binding_ticket_hash (token_hash)`。
   **已应用的 migration 是 append-only 的**——它不是会被重构搬走的源码，其文本冻结。
   这正是它满足 D-01「稳定性分层」而源码字面量不满足的原因。

故本 CHG 的做法：**删掉源码字面量断言，在 migration 的 schema 层补一条**，并在脚本 docstring
里写明行为覆盖归各仓自己的套件（并点名那条测试），避免以后有人再来本仓复述一遍。

## 改动清单

### 删除（AC-04）

| 原位置 | 原断言 | 实测红因（`change.md` §4.2） |
|---|---|---|
| `:69-73` | `cloud/internal/modules/cloudagent/compatibility.go` 含 2 个 Go 常量 | 文件移到 `cloudagent/service/`，**两个值一字未改** |
| `:83-87` | agent `cloud_agent_contract.py` 含 `REQUIRED_CONTRACT_REVISION = "2026.07.15.1"` | 值未变，定义搬到 `clients/cloud/contract.py:11`，原文件改为再导出 |
| `:110-114` | desktop `main.rs` 含 `"wt-media-agent"` 等 3 个 needle | CHG-056 拆分 `main.rs`，字符串迁到 `sidecar/integrity.rs:69,75` |
| `:115-123` | desktop `local_agent/mod.rs` 含 `consume_binding_ticket(` 与泛型 `bind_session<T: BindingTransport>(` | 消费路径改为 `commands/bind.rs:38` 的 `#[tauri::command]`；**强制点跨仓迁到 Cloud** |

共 **9 个 needle** 被移除（3 + 1 + 3 + 2）。

### 新增

`migrations/20260714_004_agent_runtime.sql` 的 3 个 schema needle：
`CREATE TABLE local_agent_binding_tickets`、`used_at DATETIME(6) NULL`、
`UNIQUE KEY uq_local_agent_binding_ticket_hash (token_hash)`。

### 保留（AC-05）

`require_contains` 的 6 个被判目标 + 1 处 dict 比对 + 1 组 forbidden 标记。**逐条列出以免含糊**：

| 层 | 目标 |
|---|---|
| 工作区配置 | `config/contract-map.yaml` |
| 工作区配置 | `config/release-matrix.yaml` |
| Cloud 已发布契约 | `contracts/cloud-agent-api/v1/sensitive-profile-guard.openapi.yaml` |
| Agent 自有契约 | `contracts/local-event-schemas/v1/profile-guard.yaml` |
| Agent 包元数据 | `pyproject.toml`（`version = "0.2.2"`） |
| Cloud 已应用 migration | `migrations/20260714_004_agent_runtime.sql`（本任务新增） |
| Desktop 契约锁 | `contracts.lock.json` 的 `consumes` dict 比对（非 `require_contains`） |
| 安全不变量 | 5 个 forbidden 标记：`binding_token varchar`、`node_credential varchar`、`permit_credential varchar`、`localstorage`、`sessionstorage` |

## Method

```bash
python3 -B -X pycache_prefix=/tmp/pyc-none scripts/verify_m2_acceptance.py
python3 -B -X pycache_prefix=/tmp/pyc-none -m unittest tests.test_verify_m2_acceptance -q
```

原始输出：`artifacts/t01-baseline-verify_m2_acceptance.out`（改前 5 红）、
`artifacts/t02-postfix-verify_m2_acceptance.out`、`artifacts/t02-postfix-test_verify_m2_acceptance.out`、
`artifacts/t02-diff-verify_m2_acceptance.patch`、`artifacts/t02-mutation-control.out`、
`artifacts/t02-ast-scope-checks.out`。

改后：`M2 static cross-repository acceptance matrix ok` / `exit=0`；
`tests.test_verify_m2_acceptance` **Ran 1 test / OK**。

## Mutation control（AC-06）

新增的 migration 断言必须能失败，且其三个 needle **各自**都要有判别力。
把模块的 `CLOUD` 指向一个只含真实 `migrations/` 目录的临时树，逐条变异 004：

```
unmutated (positive control)     0  errors
drop used_at column              1  missing 'used_at DATETIME(6) NULL'
drop UNIQUE on token_hash        1  missing 'UNIQUE KEY uq_local_agent_binding_ticket_hash (token_hash)'
rename the table                 1  missing 'CREATE TABLE local_agent_binding_tickets'
real tree untouched -> []
```

**阳性对照的作用**：未变异的副本经同一路径读数得 0——这证明读取器确实在读那棵**假树**
（否则三条变异也该是 0），故该对照有判别力，三条变异不是空转。

### 两句自我纠正（都登记）

1. **v1 对照是空转的**。首版把仓库复制到临时目录，却**没有重定向 `m.CLOUD`**，
   `validate_static_matrix()` 照旧读真实文件 ⇒ 三条变异**全部 0 error**。
   若把「0 error」读成「变异不影响」，就会得出与事实相反的结论。
   发现方式：**0/3 变异命中与「阳性对照本该有命中」的预期冲突**。
2. **AC-04 的 grep 判据不具判别力**。我用 `grep -c` 查 9 个被删 needle 是否还在文件里，
   结果 3 个显示 `hits=1`——因为我在**解释删除原因的注释里引用了这些字符串**。
   grep 分不清「断言」与「散文」。改用 **AST** 枚举 `require_contains` 实际传入的 needle 集合后：
   **9 个被删 needle 中 0 个仍在断言集合里**（`artifacts/t02-ast-scope-checks.out` C 节）。
3. **AC-05 的首版判据写错了**（同批产物 D 节报 3 个 `MISSING`）：我把路径名当成 needle 去找，
   而路径是 `require_contains` 的 **arg[1]**，不是 needle。修正后 E/F 节显示六类**全部 present**。
   **这三条是同一类错**：判据自己写错时，输出看起来同样「像量过的」。

## 与 §14 遗留的关系

- `verify_m2_acceptance.py` 的 4 条过期期望是 CHG-062 遗留第 3 项的一部分，**本任务关闭它**。
- 行为覆盖归位到 `wt-media-cloud/.../service_test.go` 这一点已写进脚本 docstring，
  使「本仓不再复述别的仓的实现」成为可读的约定，而非只存在于本记录。
