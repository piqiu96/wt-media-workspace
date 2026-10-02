# CHG-20261002-074：会话/执行凭据与数据模型解耦（契约 v2 主线）

- Status: IMPLEMENTING
- Level: `L`（跨仓契约变化，占位待与既有跨仓 CHG 级别对齐后确认）
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
