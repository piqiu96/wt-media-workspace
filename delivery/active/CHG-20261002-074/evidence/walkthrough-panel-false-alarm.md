# CHG-20261002-074 走查记录：工作环境面板误报「需检查」（2026-10-02）

走查形态：DMG 安装版（`起飞_0.1.0_aarch64.dmg`，18:56 构建，内嵌前端快照 18:55）；迁移 046/047/048 已应用；本机 Agent 与比特浏览器客户端均在运行。面板却显示「这台电脑需要检查」：工作设备=正在这台电脑工作、本机服务=未连接执行节点、比特浏览器=未知，blocker「未检测到可用的比特浏览器，请先启动比特浏览器后再检测。」。

## 根因（实证）

**JS 字段形状断裂**：`WorkEnvPill.vue` 把 `service.status()` 的输出（`normalizeLocalAgentStatus` 产物，**snake_case**）直喂读 **camelCase** 的 `createLocalAgentStatusPage`。真实运行时 camel 键全 undefined：

- `bitbrowserStatus` undefined → 默认 `unknown` → 行文案「未知」+ blocker「未检测到可用的比特浏览器…」；
- `nodeId` undefined → `page.bound` 恒假 → 本机服务行「未连接执行节点」；
- **判别性证据**：`status` 键在 snake/camel 同名存活（读到 `idle`），所以 blocker 落在比特浏览器条而非「本机执行服务未运行」条——若快照整体为 null（端口抢占/401 假设），status 也会缺失，blocker 应是服务条。截图与形状断裂逐字吻合，与 null 快照假设矛盾。

## 实测读数（走查窗口，只读探查）

| 探查 | 命令 | 读数 |
| --- | --- | --- |
| 8765 监听者 | `lsof -nP -i :8765` | agent 仓 dev 树 editable 安装进程（18:55:10 启动），非僵尸旧版 |
| Agent 真实状态 | `curl 127.0.0.1:8765/api/v1/status` | `status:"idle"`、`bitbrowser_status:"normal"`、`main_user_id` 在、`node_id=agent-node_dd4ec1…`（与 Cloud 注册一致）——**Agent 侧数据全好** |
| 节点注册/上报 | cloud `logs/access.log` 18:55–19:05 | `nodes/register` 201、`runtime-report` 200、`device-binding` 200×51——执行链路通 |
| Rust 透传 | `dto/agent.rs` | `LocalAgentStatus` 全字段 snake 无 rename——Desktop 壳不是断点 |
| 单测漏报原因 | `workEnvStatus.test.js`（修复前） | 夹具手写 camelCase、注释误称「normalizeLocalAgentStatus 的产物（camelCase）」，从未经过真实形状边界 |

## 修复（wt-media-cloud `416489f`，2026-10-02）

- `service.js` 新增 `localAgentStateFromStatus` 作为唯一 snake→camel 映射源；`store.js` 复用；`aggregateWorkEnv` 入口适配（WorkEnvPill 调用点零改动即修复）。
- 三行各说各话：`serviceText`（未运行/未连接云端/已连接，当前任务 X）与 `bitbrowserText`（normal+mainUserId 才「已登录指定账号」）由 page 工厂产出，一行坏不再歪曲另一行。
- 文案白话化：「未连接执行节点」→「未连接云端/未运行」、「未知」→「未检测」、blocker 去「执行节点/本机执行服务」术语，节点条 blocker 指向「个人信息」页。
- 测试：夹具改真实线格式（snake），新增 normalize→aggregate 接线用例与行语义用例；变异对照（撤掉适配）6 例红、还原全绿，证明接线用例有判别力。

## 修复后验证

| 项 | 读数 | 判定 |
| --- | --- | --- |
| `npx vitest run`（web/） | 49 文件 / **462 用例**通过（457→462，净增 5） | PASS |
| `npm run build:cloud` | 成功（6.80s，仅既有 chunk 提示） | PASS |
| `npm run build:desktop` | 成功（7.03s，仅既有 chunk 提示） | PASS |
| 变异对照（撤适配） | 6 例失败（含接线用例）；还原后 12/12 绿 | PASS |

## 旁证登记（不修）

- 走查窗口 `/api/v1/auth/me` 401×146：胶囊的 `cloudUser` 若 401 会报「请先登录运营平台」，实际 blocker 是比特浏览器条 → 应用内会话有效；401 风暴来自残留的浏览器标签页轮询，与本缺陷无关。
- `runtime-report` 为事件驱动（走查窗口 18:57 一次、19:26–19:28 三连发），非周期心跳；面板判定不依赖心跳窗口，不受其影响。

## 待用户复验（需重打 DMG）

内嵌前端快照刷新 + 重新打包安装后：当前健康环境面板应显示「这台电脑可以工作」，三行为 正在这台电脑工作 / 已连接，当前无任务 / 已登录指定账号；反向验证：停比特浏览器 → 「需检查」+ 比特浏览器条 blocker，且本机服务行仍「已连接」。
