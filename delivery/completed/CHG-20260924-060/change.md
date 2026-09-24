# CHG-20260924-060：CHG-056 归档遗留的 CSP `ipc:`、回环代理与占位包处置

## 1. Basic Information

- Level: S
- Status: DONE
- Created: 2026-09-24
- Current repository: `wt-media-desktop`
- Affected repositories:
  - `wt-media-desktop`
  - `wt-media-agent`
  - `wt-media-workspace`

## 2. Change Goal

处置 `CHG-20260923-056` 归档时随记录留下的四项待用户裁定中的三项（第四项只登记），达成三个可观测结果：

1. 生产 CSP 的 `connect-src` 放行 Tauri IPC，真实启动的 `ipc://` 拒绝数由 3 降为 0。
2. 回环 HTTP 请求不再经过系统代理；远程 Cloud 仍走系统代理。
3. 基线 §5.2 早已写明「不保留」的 `modes/`、`generated/` 占位包被删除，使代码**满足**基线。

本 CHG 不是业务变更：不改变任何用户可见业务闭环，成功判据是工程可观测行为（拒绝计数、代理绕过、测试红绿）。

## 3. Baseline References

- 锚点（Level S，按 CHG-20260923-054 先例写散文，不引 Milestone）：本 CHG 处置的是
  `CHG-20260923-056` 归档记录 §12「Next」登记的四项待裁定，其中三项需动运行时代码。
- Engineering baseline：`docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md`
  §5.2（`:1040` 的「不保留」清单）、§5.4、§5.5、§5.8。
- Decisions：`docs/decisions/0016-agent-runtime-layering-and-dependency-boundaries.md`。
- Desktop 侧现行基线：`wt-media-desktop/src-tauri/resources/desktop.production.toml`、
  `src-tauri/src/config.rs`、`src-tauri/src/http/`。
- 上游记录：`delivery/completed/CHG-20260923-056/`（`change.md` §12、`evidence/task-09-desktop-launch.md`
  §Findings、`evidence/task-10-baseline-check.md` §偏离 1）。
- 程序总纲：`docs/engineering/specs/2026-09-23-launch-engineering-optimization-program.md`
  （本 CHG 属其中 A 阶段归档后的收尾，不是 B/C/D 的内容）。
- Contract governance：不涉及（无 contract 变更）。

## 4. Current Facts

- **CSP**：`desktop.production.toml:29` 现为 `csp_connect_src = "http://127.0.0.1:18080"`。
  CHG-056 的 M4 反事实 leg 实测：补上 `ipc: http://ipc.localhost http://127.0.0.1:18080`
  后 `ipc://` 拒绝数 **3 → 0**。**裸 `ipc:` 不足以清除**：`ipc:` 是 CSP scheme-source，
  只匹配 `ipc:` 方案的 URL，而 macOS 上 Tauri 的 IPC fetch 目标是 `http://ipc.localhost`
  （方案为 `http`）；macOS 的 IPC 同时有 `postMessage` 回落，故缺 `ipc:` 只产生拒绝、不致命。
- `config.rs:186-195` 对 `csp_connect_src` **只做非空校验**（无 scheme 白名单、无解析、无规范化），
  故本次改动不需要动校验逻辑。
- 改 TOML 会打红**两处**测试：`bootstrap.rs:268` 的金标字符串（其存在意义正是「改策略就必须改这里」）；
  `config.rs:407` 的 `from` 串（该表以 `assert!(PRODUCTION_TOML.contains(from))` 自检）。
- **代理**：`reqwest` 0.12.28 默认开启 `system-proxy`（`Cargo.toml:14` 未关 default features；
  锁文件内 `hyper-util` 0.1.20 + `system-configuration` 0.7.0 在编）。macOS 分支读
  `HTTPEnable/HTTPProxy/HTTPPort`，**不读 `ExceptionsList`** ⇒ 回环请求被 Cland `:7897` 接管，
  本机实测表现为代理回 502。
- **reqwest 0.12.28 没有「系统代理，但排除这些主机」这个表达**：`ClientBuilder::proxy()`
  （`async_impl/client.rs:1409-1418`）与 `no_proxy()`（`:1420-1431`）都会把 `auto_sys_proxy`
  置 false，而该字段全文只有 `= false` 的写法、**无公开方式设回 true**；`Proxy::no_proxy()`
  （`proxy.rs:361-363`）只作用于自建 Proxy。系统 matcher 虽读 `NO_PROXY` 环境变量
  （`hyper-util matcher.rs:227-249`），但那条路要全局 `set_var`，会覆盖用户自己的 `NO_PROXY`、
  会漏进子进程、且让测试无法并行隔离 ⇒ 否决。
- `build_client`（`http/mod.rs:32-38`）是两个 client 唯一的共同构造点。`LocalAgentClient`
  存 base（`config.agent.host` 被校验为只能是回环），`CloudClient` **不存 base**——URL 是每次调用的参数。
- `CloudClient` 的目标**确实逐次变化**：四个 URL 构造点（`commands/bind.rs:56`、
  `preflight.rs:219/252/305`）全部来自 Tauri command 参数，`require_cloud_base_url`
  （`preflight.rs:132-141`）只 trim、只拒空，**不比对 `config.cloud.base_url`**；且前端有
  两个互相矛盾的生产者——`init.js:41-55` 返回 `PublicConfig.cloud_base_url`（可能远程），
  `AccountsPage.vue:492-496` / `ProfilesPage.vue:207-211` 是**硬编码回环字面量**。
  出货默认值本身也是 `http://127.0.0.1:18080` ⇒ 今天几乎所有 Cloud 流量都是回环且都在过代理。
- **占位包**：`tests/test_dependency_boundaries.py:80` 的 `PLACEHOLDER_PACKAGES` 由 R1（`:412-416`）
  强制每个占位目录**必须恰好**含 `["__init__.py"]`；目录消失后 glob 得 `[]` ⇒ R1 报 `found []` 转红。
  三个占位包零导入、零打包引用、零入口引用、零冻结边。
- 架构基线 §5.2（`:1040`）**早已明写**「不保留 `modes/`、`core/`、`communication/`、`runtimes/`、
  `platforms/`、`generated/`」，且全文**未提及 `adapters/`**；ADR-0016 的 **Decision 从未点名**
  这三个占位包（第 4、5 条只撤销 `runtimes/` 与 `platforms/`，`Context:15` 提及三者是决策时的状态快照）。
- **无 active CHG**：`delivery/active/` 仅 `.gitkeep`，`LEDGER.md` 无表行，快照 `Active CHG: none`。
- 开发者自己的 BitBrowser `:54345`、Cloud `:18080`（PID 55442）、dev Agent `:8765`（PID 55443）
  全程不得触碰；所有启动用 scratch 端口。

## 5. Scope

### Add

- `wt-media-agent/`：无新增文件。
- `wt-media-desktop/`：`http/mod.rs` 新增 `build_client_without_proxy` 与 `is_loopback_url`；
  `http/cloud.rs` 新增 `client_for` 与 `#[cfg(test)] mod tests`；`http/mod.rs::tests` 新增四条测试。

### Modify

- `wt-media-desktop/src-tauri/resources/desktop.production.toml`：`csp_connect_src` 加 `ipc:` 前缀。
- `wt-media-desktop/src-tauri/src/bootstrap.rs:268`、`src/config.rs:407`：测试字面量随契约值同步。
- `wt-media-desktop/src-tauri/src/http/local_agent.rs:30`：改用无代理 client。
- `wt-media-desktop/src-tauri/src/http/mod.rs:77`：既有超时测试改用无代理 client。
- `wt-media-agent/tests/test_dependency_boundaries.py:78-80`：`PLACEHOLDER_PACKAGES` 收为 `{"adapters"}` 并改注释。
- `wt-media-workspace/`：本记录、`delivery/LEDGER.md`、`delivery/completed/CHG-20260923-056/change.md` §12 的处置去向标注。

### Delete

- `wt-media-agent/src/wt_media_agent/modes/`（含 `__init__.py`）。
- `wt-media-agent/src/wt_media_agent/generated/`（含 `__init__.py`）。

### Explicitly Not Doing

- **不碰开发者的 Cloud `:18080`**：裁定项 4（被误建的惰性 `noop_task`）本轮**只登记不处置**，
  与 CHG-056 保持同一边界（§9 的 cloud 清单从未含任何运维动作）。
- **不动 `adapters/`**：架构基线未撤销它，且 R1 的对照测试（`:785-788`）正是拿它当宿主。
- **不改 CSP 的校验逻辑**：`config.rs:186-195` 保持只做非空校验，不加 scheme 白名单。
- **不动** `csp_policy`（`bootstrap.rs:176-183`）、`apply_csp` 的格式串、`dev_csp`（保持 `None`）、
  `tauri.conf.json`（保持无策略字面量）。
- **不放宽 `config.rs:217 is_loopback_host`**：它是安全校验（决定 sidecar 被要求绑定的接口），
  与本次的「URL 目标是否回环」是两个不同的问题。
- **不关 reqwest 的 `system-proxy` feature**：要的是按目标绕过，不是全局关闭。
- **不修** `local_agent.rs:31` 的 IPv6 authority 缺陷（`agent.host = "::1"` 产出 `http://::1:8765`）——
  先于本 CHG 存在，本轮只登记。
- **不引入** `wiremock`/`httpmock`/`mockito` 等 mock 依赖；该 crate 无 `[dev-dependencies]`，保持原状。
- **不做** stage B/C/D 的任何内容（运行目录与日志、桌面设置 UI、打包升级）。

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | 生产 CSP 的 `connect-src` 加 `ipc:`。取**逐字值** `ipc: http://ipc.localhost http://127.0.0.1:18080` 而非裸 `ipc:`——理由见 §4（macOS 的 IPC fetch 目标是 `http://ipc.localhost`，方案是 `http`，裸 scheme-source 匹配不到）；该值经 CHG-056 M4 leg 实测把拒绝数 3 → 0。**用户 2026-09-24 裁定「加」**。 | CONFIRMED |
| D-02 | 代理按**回环目标**禁用：`LocalAgentClient` 无条件绕过（其目标由配置校验保证恒为回环）；`CloudClient` 持 `proxied`/`direct` 两个 client，在 `post()` 内按 URL 逐次选择；远程 Cloud 保留系统代理。**用户 2026-09-24 裁定「按回环目标禁用代理」**。 | CONFIRMED |
| D-03 | 删除 `modes/` 与 `generated/` 占位包，使代码满足架构基线 §5.2 `:1040` 的「不保留」要求。**用户 2026-09-24 裁定「删」**。因基线早已如此写明，**基线本身无需回写**（ADR-0016 的 Decision 亦未点名二者，其 `Context` 是历史快照，不改写）。 | CONFIRMED |
| D-04 | 开发者 Cloud `:18080` 上被误建的惰性 `noop_task`（`task_b21340775ace100173202de3`）**暂不处置**，只在本记录与 CHG-056 §12 登记裁定去向。**用户 2026-09-24 裁定「可以暂时不处理」**。 | CONFIRMED |
| D-05 | 五项裁定（含授权方式）合并为一个 **Level-S CHG** 承载，而非拆两个或直接小改：两项改动分属两个仓，构成 `AGENTS.md:218` 所列「跨项目修改」；且 D-01 是出货的生产安全配置变更，不宜走「小修改可直接执行」。Level S 无需 Milestone 引用（验证器只对 M/L 强制）。 | CONFIRMED |

## 7. Pending Questions

None.

（CHG-056 §12 登记的四项待裁定已由用户于 2026-09-24 全部裁定，见 §6 D-01…D-04；
本 CHG 执行期间若出现新决定需求，停下并新增 `Q-xx`，不自行推断。）

## 8. Implementation Tasks

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | 建本 CHG 并激活（change.md/checkpoint.md/evidence/、LEDGER 一行、快照再生成、两个验证器绿）。 | DONE | `prepare_ai_workspace.py --change CHG-20260924-060`；两个验证器绿。 |
| T-02 | Desktop：生产 CSP 加 `ipc:`（先失败 → 同步两处测试字面量 → 全绿 → 真实启动取证）。 | DONE | `cargo test --workspace` 63 passed；真实启动 `ipc://` 拒绝数 3 → 0（含阳性对照）。 |
| T-03 | Desktop：回环目标绕过系统代理（`build_client_without_proxy` + `is_loopback_url` + 四层测试）。 | DONE | 谓词表 **16 例**、builder 差异、假代理 hits 计数、`ptr::eq` 接线；变异对照红了 2 条；20× 循环两臂均 20/20 ⇒ **该对照无效**（见 §10.1）。 |
| T-04 | Agent：删 `modes/`、`generated/`（先失败 → 改 `PLACEHOLDER_PACKAGES` → 全绿）。 | DONE | 先 R1 恰好红 2 条（`found []`），再 `bash scripts/test.sh` 253 OK。 |
| T-05 | 文档回写与收尾（agent 四份文档、workspace 记录、归档）。 | DONE | agent 四份文档回写（`4d8e9ab`）；悬空指针扫描 22 + 375 份 md，带阳性对照；CHG-056 的证据缺口一并修补；两个验证器绿；归档。 |

## 9. Repository Checklist

### wt-media-workspace

- [ ] 本记录 + `checkpoint.md` + `evidence/` + `status/{desktop,agent,workspace}.md`。
- [ ] `delivery/LEDGER.md` 加一行表行，关闭时移除。
- [ ] `delivery/completed/CHG-20260923-056/change.md` §12 按裁定结果标注四项处置去向（收尾，不改写其历史结论）。
- [ ] `.ai/CURRENT_CONTEXT.md` 由脚本再生成（禁手改）。
- [ ] 归档后主动扫描并修掉失效指针。

### wt-media-cloud

- [ ] Not affected.（D-04 只登记不处置；不读取、不写入开发者 Cloud。）

### wt-media-agent

- [ ] 删 `src/wt_media_agent/modes/`、`src/wt_media_agent/generated/`。
- [ ] `tests/test_dependency_boundaries.py` 的 `PLACEHOLDER_PACKAGES` 收为 `{"adapters"}` + 改注释。
- [ ] `DIRECTORY_MAP.md`、`AGENTS.md`、`CLAUDE.md`、`AGENT-INDEX.md` 回写；`README.md` 无需改。

### wt-media-desktop

- [ ] `resources/desktop.production.toml` 的 `csp_connect_src` 加 `ipc:`。
- [ ] `bootstrap.rs:268`、`config.rs:407` 测试字面量同步。
- [ ] `http/mod.rs`：`timed_builder`、`build_client_without_proxy`、`is_loopback_url`、模块 docstring、`:77` 换 client。
- [ ] `http/local_agent.rs:30` 换 client；`http/cloud.rs` 双 client + `client_for` + 测试。
- [ ] `cargo test --workspace`、`cargo clippy`、`cargo build`。

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | 生产 CSP 的 `connect-src` 含 `ipc:` 与 `http://ipc.localhost`。 | 改后 TOML 逐字比对 + `bootstrap.rs` 金标测试绿。 | PASS（`9945f58`） |
| AC-02 | 真实启动的 `ipc://` 拒绝数由 3 降为 0。 | `evidence/tools/ac05_desktop_launch.py` 四 leg 真实启动（scratch 端口），逐 leg 记拒绝数。 | PASS（S1→0 / S2 对照→3） |
| AC-03 | CSP 变更未放宽校验逻辑，`dev_csp` 仍为 `None`。 | `cargo test --workspace` 中 `dev_csp` 相关断言绿；`config.rs:186-195` diff 为空。 | PASS |
| AC-04 | `is_loopback_url` 在 14 例表上两向正确（含 `localhost.evil.test`、`localhost@evil.test`、`[::1]`、`[::2]`、`0.0.0.0`）。 | `cargo test --lib http::` 谓词表测试；须同时有 ✓ 与 ✗ 两组。 | PASS（**实际 16 例**；命令修正为 `--bin`，见下） |
| AC-05 | `build_client` 与 `build_client_without_proxy` 的代理配置确实不同。 | Debug 字段断言（`proxies` 出现/不出现）；并做一次「删掉 `.no_proxy()`」的**变异阳性对照**，证明该测试能抓住它。 | PASS（对照红了 2 条） |
| AC-06 | 回环请求不经代理（行为性）。 | 假代理监听（答 502）+ 回环目标 accept 计数：subject 200 且 hits==1，control Ok(502) 且 hits 仍为 1。 | PASS（附注见下：该臂**不能**单独证明绕过存在） |
| AC-07 | `CloudClient` 按 URL 逐次选择 client。 | `cloud.rs` 测试用 `std::ptr::eq` 断言 `client_for` 指向 `direct`/`proxied`。 | PASS |
| AC-08 | 既有超时测试由不确定变确定。 | 20× 循环须 **20/20 单行 ok**；阳性对照把 `:77` 改回 `build_client` 后 20 次内须**至少一次红**；对照臂不出红则记「对照无效」而非通过。 | **对照无效（不算通过）**，需求已改写，见下 |
| AC-09 | `modes/`、`generated/` 已删除且 R1 由红转绿。 | 先跑出 `found []` 的红输出留证，再全绿。 | PASS（恰好红 2 条） |
| AC-10 | Agent 测试基线不降。 | `bash scripts/test.sh` → `Ran 253 tests ... OK`（删的是两个零测试包，计数不变）。 | PASS（253 → 253） |
| AC-11 | Desktop 测试全绿且计数已报出。 | `cargo test --workspace` 全绿；报出新的总数（CHG-056 记的是 63）。 | PASS（**63 → 68**） |
| AC-12 | 基线无需回写的论证落盘。 | evidence 内逐条对照架构基线 §5.2 `:1040` 与 ADR-0016 Decision；含阳性对照（证明扫描能命中）。 | PASS（阳性对照见下） |
| AC-13 | 文档回写无悬空指针。 | agent 四份 + workspace 的指针扫描，带分母与阳性对照。 | PASS（22 + 375 份 md） |
| AC-14 | 裁定项 4 只登记未处置。 | 全程无任何指向开发者 Cloud `:18080` 的读写；登记文本可在 §6 D-04 与 056 §12 复核。 | **原句改写后 PASS**：**零写入**成立；「无任何读」不成立，见下 |
| AC-15 | CHG-056 遗留③ 被**改写**而非标为闭合。 | 056 与 evidence 的文本核对：明写「`connect_timeout` 在回环上仍不可触发」。 | PASS |
| AC-16 | 治理一致：快照、LEDGER、active 目录互指同一 CHG。 | `verify_agent_entry.py` + `verify_delivery_governance.py` 绿；归档后快照为 `none`。 | PASS |

### 10.1 验收矩阵的三处修正（先失败即证据，不当作通过）

收尾时逐条核对，有三条**按原文字无法判为 PASS**。原文保留以显示计划原貌，修正与理由记在此处：

1. **AC-08 —— 对照无效，需求改写。** 原判据假定「既有超时测试不确定」，故用 20× 循环的
   阳性对照来证明它变确定。**实测把这个前提否证了**：把该测试的 client 指回带代理的
   `build_client`（对照臂）跑 20 次，**20/20 全绿**（`artifacts/t03-timeout-test-20x-control-arm.out`）。
   即该循环**根本区分不了两个 client**，按本条自己的判据须记「对照无效」而非通过。
   机制已查明：代理会自己去拨那个静默监听器，对面不回话，于是**本 client 自己的截止时间先到**，
   同样产出 `is_timeout`。故需求按其实际达成改写为：
   > 既有超时测试改用不经代理的 client，使截止时间对着**测试自己起的那个目标**量测，
   > 且结果不依赖运行测试的机器上装了什么代理。

   **这条改写后的需求成立**（20/20 绿，`artifacts/t03-timeout-test-20x.out`）。
   「绕过确实存在」这一条不靠它，靠 AC-05 的变异对照（红了 2 条）。
2. **AC-14 —— 「无任何读」不成立，零写入成立。** 复用 CHG-056 的 `ac05_desktop_launch.py` 时，
   它自己会 `request(f"{CLOUD}/healthz")`（该工具 `:622`，把 `:18080` 的 healthz 当 HARD STOP 前置条件），
   探针页也 `fetch('http://127.0.0.1:18080/healthz')`。所以对开发者的 Cloud 有 **GET 读**。
   **成立的是：零写入、零任务创建、零配置改动**——`noop_task` 未被触碰，Cloud 的业务状态一字未改。
   这与「不碰开发者的 Cloud」的意图一致（该工具是 CHG-056 既有的，本次按计划复用而非新写取数）。
3. **AC-04 / AC-06 的措辞修正。** AC-04 写「14 例」，实现后是 **16 例**（✓ 6 + ✗ 10）。
   AC-06 的假代理臂**不能**单独证明「绕过存在」：删掉 `.no_proxy()` 时它**仍然全绿**——
   系统代理会替它把回环请求送到目标，而目标答 200，断言于是全部成立。
   该臂证明的是「绕过存在时它确实生效」，**存在性**由 AC-05 的变异对照证明（已写进代码 docstring）。

另记一处**验证命令修正**：本矩阵多处写的 `cargo test --lib …` 在本仓**不成立**——
`wt-media-desktop-shell` 是二进制 crate，`--lib` 会以
`error: no library targets found in package` 结束并输出空。正确目标是
`cargo test --bin wt-media-desktop-shell <filter>`；所有循环与取证用的都是后者。

### 10.2 AC-12 的阳性对照（否定结论必须先证明检查能命中）

该条要求「证明扫描能命中」，本次**真实触发过一次假阴性**，恰好是它的对照：

```
$ grep -rn "不保留" docs/engineering/*.md        → 0 命中   ← 假阴性
$ grep -rln "5\.2" docs/                        → 命中 docs/engineering/architecture/…_V1.md
$ grep -rn "不保留" docs/engineering/architecture/…_V1.md → :1040 命中 ← 真结果
```

首轮 0 命中**不是**「基线没写」，而是 glob 没有递归、该文件在 `architecture/` 子目录。
换成递归检索后命中 `:1040`，逐字含 `modes/`、`generated/`，且**不含** `adapters/`。
即：命中是真的，且 0 命中的那次是检查坏了——与本 CHG 一贯的「否定结论必须先证明检查会失败」同源。

## 11. Evidence

Evidence files live in `evidence/` and must record facts, not repeat requirements.

实际落盘的文件（**与建 CHG 时列的清单有出入，以本节为准**）：

- `evidence/task-01-governance.md`：建 CHG 与激活（含 LEDGER 行写错格式导致验证器报错的复现与修正）。
- `evidence/task-02-csp.md`：先失败的红输出、同步后的绿、真实启动两条 leg 的拒绝计数与阳性对照；
  末节并记录顺带查出的 CHG-056「被引用但未入库」的证据缺口。
- `evidence/task-03-proxy.md`：先失败的量测（502 vs `is_connect`）、被否决的候选方案、
  五层验证、变异对照红了 2 条、**20× 循环两臂均 20/20 从而判为无效对照**、两处计划修正。
- `evidence/task-04-packages.md`：删包前零引用的实测、基线 §5.2 `:1040` 与 ADR-0016 的逐条对照
  （论证「无需回写」，含一次真实触发的假阴性阳性对照）、R1 先红后绿、`>= 60` 余量 65→63。
- `evidence/task-05-archive-sweep.md`：文档回写与归档；**主动**失效指针扫描的分类规则、
  四仓覆盖面与分母、阳性对照、2 处命中的逐条处置、修后复扫，以及「计划预判的三处连带引用
  实测不成立」的如实登记。
- `evidence/artifacts/`：原始输出 **8** 份（`t02-*.out` ×2、`t03-*.out` ×4、`t04-*.out` ×2）。

**两处偏离说明（不是遗漏）**：建 CHG 时计划另立 `baseline-check.md` 与 `acceptance.md`，
实际未单独立文件，其内容并入更合适的位置——基线对照落在 `task-04-packages.md` §一（更贴近它
所支撑的删包决定），验收矩阵落在本节 §10（验收矩阵本就属 `change.md`，另立副本会造出两份
要同步维护的真相）。`task-05-docs.md` 同样未单立，改由 `task-05-archive-sweep.md` 承载：
T-05 的文档回写 diff 见本 CHG 的 `wt-media-agent` 提交 `4d8e9ab`，指针扫描见该文件，
AC-12 的基线扫描阳性对照见本节 §10.2。

## 12. Current Checkpoint

Completed:
- T-01：建本记录并激活。
- T-02：Desktop 生产 CSP 加 `ipc:`。先失败恰好两条守卫转红（`bootstrap.rs` 全策略金标、
  `config.rs` 拒绝表的 `from` 串；61 passed; 2 failed），同步后 **63 passed; 0 failed**。
  真实启动取证：新增驱动脚本从出货文件**解析**该值再交给真实二进制，两条 leg 只差一行配置——
  出货值 → `ipc:// refusals 0`，改动前的值（阳性对照）→ `ipc:// refusals 3`。
  同批纠正 `bootstrap.rs` 金标 docstring（原文声称与已删除的 `tauri.conf.json` 字面量逐字相同，
  改值后不再成立）。Desktop commit `9945f58`。

Current:
- T-03 待开始（回环目标绕过系统代理）。

Next:
- None. T-03 → T-04 → T-05 全部完成，本记录已归档（见 §14）。本节的 Next/Recent verification
  是**执行期**的检查点记录，保留原样以存其历史；关闭时的最终验证数字以 §14 为准。

Blocked:
- None.（CHG-056 §12 的四项待裁定已全部由用户裁定，见 §6。）

Recent verification（执行期快照，非关闭时数字）：
- Start Gate：四仓工作区全部干净；`delivery/active/` 仅 `.gitkeep`；`LEDGER.md` 无表行；快照 `none`。
- T-01：`prepare_ai_workspace.py --change CHG-20260924-060` →
  `active_change=CHG-20260924-060`、`active_milestone=null`（Level S 预期）、三仓 `affected_repositories`；
  `verify_agent_entry.py` exit 0（快照 1971 字符）、`verify_delivery_governance.py` exit 0。
  首次 LEDGER 表行写成 markdown 链接而两个验证器同报 `!= none`，根因是 `LEDGER_ROW_RE`
  要求裸 id 紧跟竖线；改裸 id 后转绿。详见 `evidence/task-01-governance.md`。

## 13. DONE Gate

逐项签字（判据写在签字行里，勿只读勾）：

- [x] **Scope completed.** — §8 的 T-01…T-05 全 DONE。三项需动代码的裁定全部落地：
  ①CSP `ipc:`（`9945f58`）、②回环绕过系统代理（`d329abc`）、③删占位包（`c33680f` + `4d8e9ab`）；
  ④按裁定**只登记未处置**。
- [x] **No blocking `Q-xx`.** — §7 为 `None.`，执行期间未新增需用户裁定的问题。
  收尾时发现的三处判据不成立（§10.1）属**实测否证计划文本**，按「实现跑通就承认它、改文档」处理，
  未回退实现，也未静默放过。
- [x] **Acceptance matrix all PASS.** — §10 共 16 条。**按 §10.1 修正后的判据计 16/16 成立**；
  但必须同时看到：**修正前的 AC-08 从未通过**（20× 循环的对照臂 20/20 全绿 ⇒ 该对照无效），
  AC-14 的「无任何读」也不成立（有 GET `/healthz` 读、零写入）。两条改写都在 §10.1 留了原文与理由。
- [x] **Automated tests passed or justified.** — desktop `cargo test --workspace` **68 passed; 0 failed**；
  agent `bash scripts/test.sh` **Ran 253 tests OK**；cloud 未触碰。`cargo clippy --workspace --all-targets`
  的 8 条 warning **全在本次未触碰的文件**，`http/` 下零新增。
- [x] **Manual verification evidence recorded where required.** — T-02 真实启动两条 leg
  （`ipc://` 拒绝数 3 → 0，对照臂出数）；T-03 对无人监听的回环端口实测 `Ok(502)`（3.0s）
  vs `is_connect`（405µs）。两者都是外部可观测行为，非「测试变绿」。
- [x] **Diff checked for out-of-scope changes.** — desktop 3 个文件全在 `src-tauri/src/http/`；
  agent 两次提交（删 2 个 `__init__.py` + 常量与注释 / 四份文档）。无夹带。
- [x] **Runtime repositories touched only if listed in scope.** — 只动 `wt-media-desktop` 与 `wt-media-agent`，
  均在 §1 的 Affected repositories 内；`wt-media-cloud` 未触碰。
- [x] **Required baselines updated.** — **无需回写**，且这是本 CHG 一条需论证的结论：
  架构基线 §5.2 `:1040` 早已明写不保留 `modes/`、`generated/`，是**代码**一直没跟上；
  ADR-0016 不改（其 Decision 从未点名这三个占位包，`Context:15` 提它们只是决策时的状态快照）。
  论证与逐字对照见 `evidence/task-04-packages.md` §一。
- [x] **Affected repositories committed independently.** — desktop `9945f58`（T-02）、`d329abc`（T-03）；
  agent `c33680f`（T-04）、`4d8e9ab`（T-05 文档）；workspace 本 CHG 的分次收尾提交。
  「删除/搬移」与「改逻辑」未混进同一提交——T-04 的删除与常量收紧是同一件不可分的结构陈述
  （常量描述的正是那组目录），故合为一次提交并在此写明理由。

## 14. 关闭记录（2026-09-24）

- **关闭依据是 DONE Gate，不是用户签收**（如实登记，勿读成后者）：本 CHG 的授权来自用户
  2026-09-24 对 CHG-056 四项遗留的裁定与建 CHG 的批准；执行期间**没有**针对本 CHG 的用户验收轮次。
  §13 九项由我逐项签字，判据写在签字行里。若需要用户签收口径，请在此追加。
- **关闭时的验证快照**：desktop `cargo test --workspace` → **68 passed; 0 failed**（起点 63）、
  `cargo build` 成功；agent `bash scripts/test.sh` → **Ran 253 tests OK**（与删包前一致）；
  `verify_agent_entry.py` → **0 warning**（收尾前快照 1971 字符）；`verify_delivery_governance.py` → 绿。
- **归档与失效指针扫描（T-05 末步，2026-09-24）**：`Status: DONE` → `git mv` 入 `delivery/completed/` →
  LEDGER 表行移除（表留表头，照 `95f9487` 先例）→ 冷启动 `prepare_ai_workspace.py --no-active` 重生成快照。
  重生成后 `verify_agent_entry.py` → **0 warning（快照 1668 字符）**、`verify_delivery_governance.py` → **ok,
  Active CHG: none**，快照 `Active CHG: none` / `Status: NONE`，与 `delivery/active/`（仅 `.gitkeep`）、
  `LEDGER.md` 三者一致。**主动扫描**（分母 509 个在册文件 ×4 仓、阳性对照 3 命中，故 0/1 是真数）：
  2 处命中，1 处「修」（`task-02-csp.md` 的可重放命令路径 `active/`→`completed/`，命令其余未改），
  1 处「留」（`checkpoint.md` 描述 T-01 建目录的过去时叙述，同 056 `change.md:619` 先例）。
  修后复扫：**0 处「修」类残留**。计划预判的三处「连带引用」（056 归档记录、`planned/README.md`、
  程序总纲）**实测均不需要改**——060 是旁支 CHG，除记录自身外没有任何文档曾指向它。详见
  `evidence/task-05-archive-sweep.md`。
- **本 CHG 最重要的一条诚实记录**：AC-08 的判据被实测否证（§10.1）。计划假定既有超时测试
  「不确定」，故用 20× 循环的阳性对照来证明它变确定；实测改动前后**各 20/20 绿**，
  该循环区分不了两个 client。**这条判据从未通过，且已按计划自己的规则记为「对照无效」。**
  「绕过存在」改由 AC-05 的变异对照承载（删掉 `.no_proxy()` 后红了 2 条）。
  同理 AC-06 的假代理臂**不能**证明绕过存在（系统代理会把请求送到目标、目标答 200，断言全成立），
  这一点已写进代码 docstring，以免后人把它当成一条它做不到的守卫。
- **连带修补的归档缺陷**：CHG-056 的 `evidence/artifacts/ac05-run5.log`（8975 字节）原先
  **被六处引用但未入库**（被 `.gitignore` 的 `*.log` 吃掉），已以 `git add -f` 补入，
  内容与结论一字未改；补入前扫过凭证特征（无值命中）。056 的 `change.md` 关闭记录已追加
  四项遗留的裁定与处置去向。
- **遗留（两项，随记录归档，不阻塞关闭）**：
  ①开发者 Cloud `:18080` 上被误建的惰性 `noop_task`（`task_b21340775ace100173202de3`）——
  用户已裁定**暂时不处理**，本 CHG 未处置且不在其授权内。
  ②`local_agent.rs` 的 `base` 用 `format!("http://{}:{}", host, port)` 拼装，在
  `agent.host = "::1"`（**校验器认可**）时产出 `http://::1:8765` 这种无方括号的 IPv6 authority，
  合法配置产生无法寻址的 client。与本 CHG 无关（正因如此其绕过才写成无条件式），登记为独立遗留。
- **明确不在本次关闭内**：CHG-056 关闭记录里列的四项后续（日志轮转/清理/脱敏、用户设置 UI、
  端口就绪通知、打包完整性校验与升级回归）分属 CHG-057/058/059，**不得**据本记录的 DONE
  推断它们已完成。
