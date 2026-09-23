# Evidence: Cloud Web 两处回环字面量（T-08）

- CHG: `CHG-20260923-056`
- Task: `T-08`
- Date: 2026-09-24
- Type: refactor + test + mutation
- Status: PASS

## Purpose

T-08 拆掉前端两处「自己猜本机地址」的写法，使它们改走两侧契约：

1. `init.js::cloudBaseUrl()` 不再返回 `http://127.0.0.1:18080`，改问
   `get_public_config`（T-07 F）——AC-05。
2. `LocalLogsPage.vue` 不再 `fetch('http://127.0.0.1:8765/healthz')`，改走
   `createLocalAgentService().health()`。

**与本 CHG 的耦合**：Agent 从 T-07 D 起对每个 GET/POST 强制 token，而 (2) 的无头
`fetch` 一旦被 CSP 拦掉就只能是「不可达」，两者同时落地才不留下一个已知的破碎状态。

## Method

### 1. 提交（1 个 commit，`wt-media-cloud`）

| commit | 内容 |
|---|---|
| `305d002` | 两处改动 + 3 条 `cloudBaseUrl` 测试 + 2 条边界断言 |

### 2. 红验证（先只把 `cloudBaseUrl` 导出、函数体一字不改）

目的是让红是**行为性**的，而不是「函数不存在」导致的导入失败：

```
× where Cloud is > answers with nothing rather than a loopback address
  → expected 'http://127.0.0.1:18080' to be ''

× Desktop Local Agent boundary > does not let the local-logs page reach the Agent port itself
  → expected '<script setup>\nimport { ref } from \…' not to match /127\.0\.0\.1/
```

另两条当时报 `You must provide a Promise to expect() when using .resolves, not 'string'`
——同一条行为差异的另一面：改前是**同步**函数。

### 3. 变异矩阵（`/tmp/cloudbaseurl-mutants.py`，先跑未变异阳性对照）

```
M-01 失败路径回退回环字面量        -> answers with nothing...             CAUGHT
M-02 忽略原生答复、改用回环字面量  -> asks the native side...             CAUGHT
M-03 去掉缓存（失败即遗忘）        -> keeps the last known good address   CAUGHT
M-04 local-logs 页改回直连 fetch   -> 边界规则                           CAUGHT
M-05 init 路径重新出现 18080       -> carries no hard-coded Cloud address CAUGHT
```

**5/5 杀，0 存活，0 无效。**

缓存的三条测试各自 `vi.resetModules()` 后重新 import：`init.js` 的缓存是模块级的，
共用一个实例会让它们依赖执行顺序。

## Expected

- `cloudBaseUrl()` 返回 `get_public_config` 给的地址；问不到时返回**空串**，且**永不**
  返回回环字面量。
- 缓存保留最后已知良好值：一次成功之后的失败仍返回上次的地址。
- `LocalLogsPage.vue` 内不出现 `127.0.0.1`、不出现 `fetch(`。
- `npm test` 全绿，含既有的 `localAgentBoundary.test.js`。

## Actual

```
cd wt-media-cloud/web && npm test
  Test Files  21 passed (21)
       Tests  101 passed (101)          <- 改动前 96
```

`init.js` 改动后 grep 无 `18080`（AC-05 的一次性证据已**同时**落成常驻断言，见下）。

## Coverage

- **已覆盖**：地址来源、空串回退、缓存语义、命令名契约（`get_public_config` 字面量，
  故意不引用被测模块自己的常量——改名只改一侧就会红）、local-logs 页不再直连、init 路径
  无 18080。
- **未覆盖**：`bindTrustedLocalAgent()` 本身（需要真实 Tauri 窗口）——它由 T-09 的
  Desktop 真实启动观察。三个残留 18080 站点（`AccountsPage.vue`、`ProfilesPage.vue`、
  `shared/api/http.js`）按用户裁定登记为遗留，**本 CHG 不改**，故两条边界规则都**显式
  限定文件范围**，理由写在测试注释里：全树规则今天就会红，只能靠删规则来通过。

## Follow-Up

### 1. AC-05 的 grep 已升级为常驻断言

`localAgentBoundary.test.js` 新增 `carries no hard-coded Cloud address`，把「初始化路径
无 18080 硬编码」变成永久性质而非一次性 grep（M-05 是它的阳性对照）。

### 2. 一处测试写法自查

值级哨兵里原本还有 `"true"`（想覆盖 `development.python_fallback`），但它在红跑里**从未
触发**，且布尔只有两种拼写、都不是哨兵——`"true"` 会为错误的理由匹配到将来的任何字段。
已删除，并把该字段的保证明确划给键集棘轮（属 T-07 F 的测试）。

### 3. 未做

`LocalLogsPage` 的 `health()` 调用**没有**单元测试（只断言了它不再直连）。断言「用的是
`health()` 而不是 `status()`」属于对实现细节过拟合，且两者都经桥、都不越界，没有可断言
的行为差异，故不写。运行期由 T-09 的真实启动覆盖。
