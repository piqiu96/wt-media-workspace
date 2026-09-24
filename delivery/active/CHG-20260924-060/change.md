# CHG-20260924-060：CHG-056 归档遗留的 CSP `ipc:`、回环代理与占位包处置

## 1. Basic Information

- Level: S
- Status: IMPLEMENTING
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
| T-03 | Desktop：回环目标绕过系统代理（`build_client_without_proxy` + `is_loopback_url` + 四层测试）。 | TODO | 谓词表 14 例、builder 差异、假代理 hits 计数、`ptr::eq` 接线；20× 循环含阳性对照。 |
| T-04 | Agent：删 `modes/`、`generated/`（先失败 → 改 `PLACEHOLDER_PACKAGES` → 全绿）。 | TODO | 先 R1 报 `found []` 转红，再 `bash scripts/test.sh` 253 OK。 |
| T-05 | 文档回写与收尾（agent 四份文档、workspace 记录、归档）。 | TODO | `verify_agent_entry.py` + `verify_delivery_governance.py` 绿；悬空指针扫描带阳性对照。 |

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
| AC-01 | 生产 CSP 的 `connect-src` 含 `ipc:` 与 `http://ipc.localhost`。 | 改后 TOML 逐字比对 + `bootstrap.rs` 金标测试绿。 | TODO |
| AC-02 | 真实启动的 `ipc://` 拒绝数由 3 降为 0。 | `evidence/tools/ac05_desktop_launch.py` 四 leg 真实启动（scratch 端口），逐 leg 记拒绝数。 | TODO |
| AC-03 | CSP 变更未放宽校验逻辑，`dev_csp` 仍为 `None`。 | `cargo test --workspace` 中 `dev_csp` 相关断言绿；`config.rs:186-195` diff 为空。 | TODO |
| AC-04 | `is_loopback_url` 在 14 例表上两向正确（含 `localhost.evil.test`、`localhost@evil.test`、`[::1]`、`[::2]`、`0.0.0.0`）。 | `cargo test --lib http::` 谓词表测试；须同时有 ✓ 与 ✗ 两组。 | TODO |
| AC-05 | `build_client` 与 `build_client_without_proxy` 的代理配置确实不同。 | Debug 字段断言（`proxies` 出现/不出现）；并做一次「删掉 `.no_proxy()`」的**变异阳性对照**，证明该测试能抓住它。 | TODO |
| AC-06 | 回环请求不经代理（行为性）。 | 假代理监听（答 502）+ 回环目标 accept 计数：subject 200 且 hits==1，control Ok(502) 且 hits 仍为 1。 | TODO |
| AC-07 | `CloudClient` 按 URL 逐次选择 client。 | `cloud.rs` 测试用 `std::ptr::eq` 断言 `client_for` 指向 `direct`/`proxied`。 | TODO |
| AC-08 | 既有超时测试由不确定变确定。 | 20× 循环须 **20/20 单行 ok**；阳性对照把 `:77` 改回 `build_client` 后 20 次内须**至少一次红**；对照臂不出红则记「对照无效」而非通过。 | TODO |
| AC-09 | `modes/`、`generated/` 已删除且 R1 由红转绿。 | 先跑出 `found []` 的红输出留证，再全绿。 | TODO |
| AC-10 | Agent 测试基线不降。 | `bash scripts/test.sh` → `Ran 253 tests ... OK`（删的是两个零测试包，计数不变）。 | TODO |
| AC-11 | Desktop 测试全绿且计数已报出。 | `cargo test --workspace` 全绿；报出新的总数（CHG-056 记的是 63）。 | TODO |
| AC-12 | 基线无需回写的论证落盘。 | evidence 内逐条对照架构基线 §5.2 `:1040` 与 ADR-0016 Decision；含阳性对照（证明扫描能命中）。 | TODO |
| AC-13 | 文档回写无悬空指针。 | agent 四份 + workspace 的指针扫描，带分母与阳性对照。 | TODO |
| AC-14 | 裁定项 4 只登记未处置。 | 全程无任何指向开发者 Cloud `:18080` 的读写；登记文本可在 §6 D-04 与 056 §12 复核。 | TODO |
| AC-15 | CHG-056 遗留③ 被**改写**而非标为闭合。 | 056 与 evidence 的文本核对：明写「`connect_timeout` 在回环上仍不可触发」。 | TODO |
| AC-16 | 治理一致：快照、LEDGER、active 目录互指同一 CHG。 | `verify_agent_entry.py` + `verify_delivery_governance.py` 绿；归档后快照为 `none`。 | TODO |

## 11. Evidence

Evidence files live in `evidence/` and must record facts, not repeat requirements.

- `evidence/task-01-governance.md`：建 CHG 与激活（验证器输出、快照 diff）。
- `evidence/task-02-csp.md`：先失败的红输出、同步后的绿、真实启动四 leg 的拒绝计数。
- `evidence/task-03-loopback-proxy.md`：谓词表、Builder 差异与变异对照、假代理 hits 计数、接线测试、20× 循环两臂。
- `evidence/task-04-placeholder-packages.md`：R1 先红后绿、测试计数、`>= 60` 余量由 65→63。
- `evidence/task-05-docs.md`：文档回写 diff、悬空指针扫描（带分母与阳性对照）。
- `evidence/baseline-check.md`：架构基线 §5.2 与 ADR-0016 的逐条对照，论证「无需回写」。
- `evidence/acceptance.md`：AC-01…AC-16 验收矩阵，逐条命令、实测输出与阳性对照，含**覆盖边界**。
- `evidence/artifacts/`：原始输出。

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
- T-03 → T-04 → T-05，一仓一 commit，删除/搬移与改逻辑不混在同一提交。

Blocked:
- None.（CHG-056 §12 的四项待裁定已全部由用户裁定，见 §6。）

Recent verification:
- Start Gate：四仓工作区全部干净；`delivery/active/` 仅 `.gitkeep`；`LEDGER.md` 无表行；快照 `none`。
- T-01：`prepare_ai_workspace.py --change CHG-20260924-060` →
  `active_change=CHG-20260924-060`、`active_milestone=null`（Level S 预期）、三仓 `affected_repositories`；
  `verify_agent_entry.py` exit 0（快照 1971 字符）、`verify_delivery_governance.py` exit 0。
  首次 LEDGER 表行写成 markdown 链接而两个验证器同报 `!= none`，根因是 `LEDGER_ROW_RE`
  要求裸 id 紧跟竖线；改裸 id 后转绿。详见 `evidence/task-01-governance.md`。

## 13. DONE Gate

- [ ] Scope completed.
- [ ] No blocking `Q-xx`.
- [ ] Acceptance matrix all PASS.
- [ ] Automated tests passed or justified.
- [ ] Manual verification evidence recorded where required.
- [ ] Diff checked for out-of-scope changes.
- [ ] Runtime repositories touched only if listed in scope.
- [ ] Required baselines updated.
- [ ] Affected repositories committed independently.
