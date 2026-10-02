# CHG-20261002-074：会话/执行凭据与数据模型解耦（契约 v2 主线）

- Status: DONE
- Level: `L`（跨仓契约变化，占位待与既有跨仓 CHG 级别对齐后确认）
- Closure anchor: §4「验收标准」
- Current repositories: `wt-media-cloud`（主）、`wt-media-desktop`（执行凭据落盘）、`wt-media-agent`（触点核验）
- 来源：2026-10-02 走查结论——CHG-072 阶段 0 只完成样式与即时修复，联动功能（desktop/web 会话共存、执行凭据独立、换机重投递、环境自助确认）均未实现；用户裁定：先归档 072/073，再开本 CHG 承载阶段 1+2+3。
- 契约基线：v1 将 node 保持与 session 耦合；本 CHG 升级为 v2，node 执行在场层改绑 device 而非 session。
- 激活条件：`CHG-20261001-072/073` 关闭归档后激活（`delivery/active` 同一时间只允许一个活跃 CHG）。**已于 2026-10-02 激活**（072/073 已归档，本 CHG 为唯一活跃）。

## 1. 独立结果

一个账号可以同时持有 desktop 与 web 会话互不挤掉；执行凭据只依赖「设备绑定 + 节点在线」，会话失效不夺权、进程重启凭据仍在；换设备后下载任务可重投递、解绑自动重新分配；比特浏览器主账号可由用户在个人信息页自助「以当前环境为准」确认，不再依赖管理员入口。

## 2. 范围（三阶段，按顺序实施）

### 阶段 1 — 会话层 client_type 解耦（cloud 为主）

- `user_sessions` 增加 `client_type`（`desktop` / `web`）+ 迁移脚本。
- 服务端从请求特征推断 client_type：`X-Session-Token` header 或 `Origin: tauri.localhost` → desktop；否则 web。
- `LoginWithOptions`（identity/service.go:269）line 285 的全量 `InvalidateUserSessions(user.ID)` 改为仅失效同 client_type 的旧会话；web 登录不再挤 desktop，desktop 之间同 client_type 才触发 20010。
- `InvalidateUserSessions`（store_adapter.go:93）加 client_type 过滤；`Logout`（service.go:332）按 token 失效自身。
- 前端：desktop 登录请求注入 `X-Session-Token` 特征；LoginPage replaceExisting 流程保留（20010 语义收敛后文案仍成立）。

### 阶段 2 — 执行凭据独立 + 设备级持久化（cloud + desktop）

- `authenticateCredential` / `FindTrustedLocalNode` / `CheckLocalTrust`（runtimebinding/store_adapter.go:36-39、service.go:176-183）SQL 去掉 `invalidated_at IS NULL` / `IsSessionActive`，改为凭据有效 = device 绑定存在 + 节点在线（presence 心跳）。
- node 拆两层（契约 v2 核心）：
  - 身份/会话层：登录会话、`user_sessions`；
  - 执行在场层：`runtime_presence.node_id`、敏感任务 node_id、`credential`——绑定 device_id 而非 session；对应 runtimebinding 存储模型拆分 + 迁移脚本。
- Desktop `RuntimeBindingState`（Mutex<Option<RuntimeBinding>>，进程内存）落盘：bind.rs:197 `.replace(RuntimeBinding{...})` 后同步写盘，启动时恢复；复用 `device_identity.pk8`（device_identity.rs:18）持久化先例。`RuntimeBinding::node_credential` 安全边界（diagnostic.rs:15）保持不变。
- 设备级单实例互斥：同 device_id 只允许一个执行实例持有凭据并领任务；新实例上线替换旧实例。
- 前端：WorkEnvPill「重新同步本机环境」过渡入口（阶段 0 遗留）在凭据持久后移除。

### 阶段 3 — 数据模型 + 比特环境自助（cloud + desktop + agent 触点）

- `CreateUserDownloadTask` / `userDownloadDedupeKey`（filetransfer/store_mysql.go:156/219）去重维度 node→device：换设备重投递不再被 dedupe_key 吞；存量行为兼容。
- `UnbindDevice`（runtimebinding/service.go:176）解绑时把该设备名下 pending/running 任务重新分配或标记可重取。
- DownloadCentre 对「已绑定当前设备但状态悬置」的任务主动重取。
- profilebinding 用户自助「以当前环境为准」入口（复用 ConfirmMainIdentity / ConfirmMainIdentityDirect，service.go:227-231），替代 admin-only `DELETE /api/v1/users/:user_id/bit-browser-main-identity`（router.go:15）。
- 契约定义 23002 / 23003 错误码/接口语义（重投递、环境确认）写入契约文档。

## 3. 明确不做

- 不做产品改名或品牌（由 073 承担，已随 072 归档）。
- 不改下载引擎/分片实现（069 已交付）。
- 不引入多设备同时在线执行（仍是单设备互斥，只是换机迁移与重投递顺畅）。

## 4. 验收标准

- desktop 与 web 双会话共存实测不互挤；desktop 之间同 client_type 才 20010。
- 会话失效后凭据仍可 authenticate；节点离线则失效；Desktop 重启后凭据仍在、无需重走登录同步。
- 设备 A 领任务→解绑→设备 B 绑定后可重取；比特主账号切换后可自助确认。
- 契约文档与实现一致：grep 无 `invalidated_at IS NULL` 残留、无 node 维度 dedupe。
- 走查后再由用户签收；仅代码存在或单测通过不算完成。

## 5. 有序任务

1. 契约 v2 文档先行（client_type 推断、node 两层、23002/23003、dedupe 维度）锁定语义；
2. 阶段 1：迁移 + identity 改造 + 单测（登录矩阵）+ 前端注入特征；
3. 阶段 2：runtimebinding 凭据解耦 + node 两层 + Desktop 落盘 + 单实例互斥；
4. 阶段 3：filetransfer dedupe 改维 + UnbindDevice 重分配 + DownloadCentre 重取 + profilebinding 自助；
5. 收尾：WorkEnvPill 过渡入口清理、ADR（node 两层决策）、全量单测/双构建/端到端走查。

## 6. 待用户裁定

- CHG 编号（暂占 074）、Level 级别；
- 是否在实施中同步更新 `contracts.lock.json`（desktop 消费者）与 Cloud OpenAPI 兼容性版本。

## 8. 验收与关闭（2026-10-03）

用户裁定：**「chg074 可以关闭，基本功能已完成，有些优化项后续在做」**，并在四项待确认上逐条选择——**直接关闭**（出包与人工走查用户已手动完成，本次不重打 DMG、不等复验）；工作树里不属本 CHG 的改动**不提交、只在记录里登记**；`wt-media-desktop/contracts.lock.json` **维持不 bump**；遗留按**混合**落点（技术债另立 planned 草案、本 CHG 自身的复验留在本记录）。§4 最后一条「走查后再由用户签收；仅代码存在或单测通过不算完成」据此满足。

### 8.1 走查结果（用户自报，逐项标注证据覆盖）

用户给的是**一句总签收**，未逐项给读数。下表按 §4 拆条，机器证据一列区分「覆盖」与「仅用户自报」——不把用户的一句话翻译成它没有的粒度。

| §4 验收项 | 用户结果 | 机器证据 |
| --- | --- | --- |
| 面板全绿（正在这台电脑工作 / 已连接 / 已登录指定账号）；停比特浏览器只落比特浏览器条 blocker、本机服务行仍「已连接」 | 通过 | **部分覆盖**：映射与三行文案由 `416489f` 交付并有用例钉住（web `vitest` 50 文件 / 486 用例）；但**打包版**的这次读数只有用户的眼睛，见 8.2 |
| 登录页不再自指重定向、能登回（`8a21041`） | 通过 | **部分覆盖**：dev 栈 + 无头 Chrome 同一装置对照——`/auth/me` 401 撤守卫 **71** 次 / 带上 **1** 次，未登录打开 `/` 仍恰好 2 次后停住；打包版由用户走查覆盖 |
| 胶囊冷启动自行转绿、切账号 30s 内变「需检查」 | 通过 | **仅用户自报**（无独立读数；`document.hidden` 一次都没量，见 8.2） |
| 同机再登录的 20010 确认框显示 v2 新文案（`9d54203`） | 通过 | **部分覆盖**：两处文案已按 v2 语义改写并落在 `web/`；实发文案由用户走查覆盖 |
| 设备 A 领任务→解绑→设备 B 绑定后可重取；唯一非终态任务不再悬置旧节点 | 通过 | **覆盖**：`c33859d` 的重指谓词对着真库 `SELECT` 恰好命中那 1 行；走查期新任务落在当前可信节点 |
| 安装包能真的下载（本 CHG 唯一硬读数） | 通过 | **覆盖**：最终包、无手起 Agent、无 export —— 素材 161 从 `pending` → `running`（`claimed_by_node_id` = 当前节点）→ **00:07:27 success 495383052/495383052**，落盘 `stat` 恰为 495383052 字节，另一份 162200269 字节，均与 `materials.video_size_bytes` 逐字节相符 |

### 8.2 未覆盖项登记

- **打包 app 下「胶囊每 30 秒真的带上 `scan=reuse`」未验证**：本环境下 WebView 反复重载（`IPC custom protocol failed` 278 次 / `Couldn't find callback id` 122 次），`local_agent_start` 被调 279 次后 Agent 被停，胶囊始终未进稳态（`agent.log` 在 00:39:04 后无新行）。该路径只由源串断言 + 变异对照覆盖。已证到的另一半是打包 sidecar 二进制本身：两次真扫描相隔 **5 分 12 秒**。
- **`document.hidden` 在 Tauri WebView 启动时的取值未实测**。若为 `true`，走查修复 2 之前的 interval 从不建立；现实现已改为挂载/手动/轮询/重新可见共用，但这条读数仍空。
- **desktop 与 web 双会话共存、会话失效后凭据仍 authenticate、Desktop 重启凭据仍在**：§4 的第 1、2 条只有用户总签收，没有再取独立读数（阶段 2/3 的落地由单测与 migration 覆盖，不等同于实机读数）。
- **停比特浏览器只落一条 blocker**：用户报告通过，未留截图或日志级证据。

### 8.3 关闭读数（最后一次代码改动之后重跑）

| 仓 | 读数（判据 / 命令） |
| --- | --- |
| `wt-media-cloud` | `go build ./...` + `go vet ./internal/...` rc 0；`go test -count=1 ./internal/...` **62 包 ok / 0 FAIL**（末次改动 `9732a07`） |
| `wt-media-cloud/web` | `npx vitest run`（cwd = `web/`）**50 文件 / 486 用例通过**，rc 0（486 含登录修复新增的 2 条） |
| `wt-media-agent` | `bash scripts/test.sh` **Ran 688 tests / OK**，rc 0（末次改动 `f7b8f11`） |
| `wt-media-desktop/src-tauri` | `cargo test` **507 通过 / 0 失败 / 6 ignored**（静置机读数，见下）；6 个改动文件 `rustfmt --check --edition 2021` 全绿 |
| `wt-media-workspace` | `python3 -m unittest discover -s tests` **92 用例 / 3 红**——3 条全部先于本 CHG 存在，逐条列在 8.4 (a)/(b) |
| 校验器 | `scripts/verify_delivery_governance.py` **rc 0**；`scripts/verify_product_master_alignment.py` **rc 0**；`.ai/CURRENT_CONTEXT.md` = `Active CHG: none` / `Status: NONE` |
| 提交 | cloud `8a21041`（登录自跳）、`86f4128`（扫描降频 + 胶囊取数）、`c33859d`（换节点重指）、`9732a07`（操作后刷新）；agent `b369d8f`（契约 `2026.10.03.1`）、`f7b8f11`（用例修正）；desktop `758f07e`（实时扫描）、`0440d54`（执行器开关）、`664f072`（发布链与「起飞」文案）；workspace 本记录自身随归档提交。三个运行仓工作树在各自最后一次提交后无代码改动 |

**关闭期间修掉的一条假红（`f7b8f11`）**：`test_reuse_serves_the_first_scan_to_the_second_request` 在四套件并发时红过（688 / 1 红），单独跑 5 次里 1 红 4 绿。根因实测定位——该断言比较**整个响应体**，而 `data.disk.free_megabytes` 是每次请求现测的主机事实：起 churn 线程每约 30 ms 写/删 16 MiB 文件后 **8/8 红**，逐字段 diff 的唯一差异就是 `.data.disk.free_megabytes`（49757 → 49789），同一响应里 `client.calls` 始终为 1（缓存行为正确）。改法：弹出 `disk` 后再全量比较；churn 下 **8/8 绿**，把 `BitBrowserScanCache.snapshot` 改成永不复用后仍红（`calls 2 != 1`），判别力未失。**desktop 侧同类用例未修**，登记在 8.4 (c)。

### 8.4 遗留（登记，不阻塞关闭）

- **a. `contracts.lock.json` 与 M2 静态矩阵不一致**（`test_static_cross_repo_contract_and_security_matrix` 的红）：实测使该用例红的是 **`cloud_agent_api`**——lock 钉 `v1@2026.10.01.1`，`scripts/verify_m2_acceptance.py:114-128` 硬编码期望 `v1@2026.07.15.1`，漂移自 desktop `20e00d1`。**这里的更正很重要**：此前 checkpoint 登记「`local_agent_api` / `local_event_schemas` 相对 map 陈旧导致红」是误判——那两条恰好等于硬编码期望、因此是绿的；相反，单独把 lock 的 `local_agent_api` 对齐到 `2026.10.03.1` 会让红从 1 条变 2 条。这正是「不 bump」裁定的直接依据。
- **b. `scripts/verify_m0_config.py` 的 `cloud_agent_api` 钉子过期**（rc 1；`test_contract_map_matches_m1_cloud_agent_compatibility` 与 `test_contract_map_provider_paths_exist_in_full_workspace` 两条红，实测同一个发现）：期望 `2026.07.14.7` vs map `2026.10.01.1`，引入于 `786fdeb`（CHG-069 任务 21 落档只推 map 未同步钉子）。**不修**：按该门禁的设计，移动钉子本身就是那次契约前进的复核动作。本 CHG 推进 `local_agent_api` 时**同步了**该文件的对应钉子（否则会当场多一条红灯，已实测）。
- **c. 技术债另立草案**：以上两条与其余 9 类遗留（`docs/standards/` 未索引 + 两处死链、`sensitive_browser_tasks.node_id` / `browser_profile_runtime_presence.node_id` 同族悬置、会话 cookie 无 `Max-Age`、`document.hidden` 未实测、`scan=reuse` 待实机、desktop `a_tampered_sidecar_is_refused…` 负载下假红、反引号 `Level` 使门禁静默跳过、M2-F 基线回写）逐条落点见 [CHG-20261003-075](../../planned/CHG-20261003-075/change.md) §2。
- **d. workspace 工作树里不属本 CHG 的改动**（按用户裁定不提交、只登记，留待归属方）：`AGENT-INDEX.md`、`AGENTS.md`、`CLAUDE.md` 三篇重写；`delivery/MASTER_IMPLEMENTATION_PLAN.md` §3 之外的 M4-C3~C7 措辞改写（:449 那一段）；`delivery/milestones/M5-automatic-production.md`；`docs/standards/前端架构与视觉规范.md`（新增）与 `docs/engineering/specs/web-desktop-visual-system.md`（删除）；`reference/`；`docs/superpowers/specs/2026-10-02-first-production-deployment-plan.md`、`2026-10-03-github-packaging-trial-plan.md`。**本 CHG 只提交自己的路径，不代它们决策。**
- **e. 归档记录里的死链（只登记，不回改）**：按 `delivery/completed/README.md:11` 的只读边界不修。实测 `delivery/completed/**` 共 **30 处**相对链接解析不到（23 处是真链接、7 处是 `NO-SUCH-FILE.md` / `…` 这类行文占位；其中 **12 处**指向 `wt-media-*` 兄弟仓——那些仓不在本仓目录树内，**任何**相对路径都到不了，属既有约定、非本次引入）。与本 CHG 直接相关的 **7 处**：`CHG-20261001-072` 的 `change.md:48`、`checkpoint.md:3`（4 条指向已归档的 073/074）与 `CHG-20261001-073` 的 `change.md`、`checkpoint.md`（3 条指向 `../../active/CHG-20261001-072`，该目录早已清空）。本 CHG 自己 evidence 里的 6 处同类链接**本次已修**（层数 4→5，实测 6/6 解析成功），故不在遗留内。活文件侧的旧指针也一并改到 `../completed/…`（`delivery/planned/README.md`）。
- **f. `- Level:` 仍未定级**：本记录写 `` `L`（跨仓契约变化，占位待与既有跨仓 CHG 级别对齐后确认）``，用户本轮未裁定。**保持占位**——同时实测到一个连带后果：该写法使 `verify_delivery_governance.py:14` 的 `LEVEL_RE`（要求裸 `[A-Z]`）匹配不到，里程碑引用检查对这类记录整段跳过（68 篇里 6 篇如此），登记进 075 §2 第 10 项。
- **g. §6 两条的裁定结果**：CHG 编号**沿用 074**；`Level` **未定**（见 (f)）；`contracts.lock.json` **不 bump**（wire schema 未变，见 ADR-0019 后果节），陈旧条登记为 (a)/(c)。

**本记录归档后不再修改**（`delivery/completed/README.md` 的只读边界）；后续处置都在 075 或各自的归属方。
