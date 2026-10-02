# 走查修复：比特账号绑定入口 + 工作环境胶囊刷新（2026-10-02）

走查形态：DMG 安装版，个人信息页「设备与本机环境」。用户提出四项：按钮名看不懂、账号相同时仍给绑定入口、弹窗不说后果、右上角胶囊与个人中心数据不一致。

## 改动（wt-media-cloud `web/`，单仓）

1. **入口改名 + 收紧可见性**：`PersonalInfoPage.vue` 按钮「以当前环境为准」→「比特账号绑定」，`v-if` 由 `inDesktop && binding.bit_account_bound && localAgent.main_user_id` 改为 `inDesktop && bitAccountDiffers`（账号一致即隐藏）。原先页面里那个 `bitAccountDiffers` 计算属性**已存在但模板从未引用**（死代码），本次成为唯一判据。
2. **弹窗说明后果**：正文改为逐条列出「新账号窗口才能执行任务 / 原账号窗口需重新扫描 / 窗口记录可切回恢复」。
3. **判定同源**：`work-env-status.js` 新增导出 `bitAccountDiffers(binding, localMainUserId)` 与 `maskBitAccountId(id)`；页面、`aggregateWorkEnv`、胶囊三处共用一份判定，不再各写一份。
4. **胶囊刷新收敛**：`WorkEnvPill.vue` 的取数合并为一条 `loadWorkEnvInputs`（四项一次读齐），挂载、手动「重新检查」、30s 轮询、窗口重新可见全部走它；`document.hidden` 在挂载时不再参与「要不要建 interval」的判断；新增冷启动退避 `[2s,5s,10s]`。

## 第 4 项的根因（代码证据）

两个入口读同一套数据（`GET /api/v1/local-agent/device-binding` + `local_agent_status` / `local_device_identity`），但各持组件本地 `ref`、无共享 store，刷新策略不同：

| | 个人中心 | 右上角胶囊 |
| --- | --- | --- |
| 取数 | 每次路由挂载重读四项 | 挂载/手动点才读四项 |
| 周期刷新 | 无 | 30s 一次，但**只刷 2 项**（`snapshot`、`binding`） |
| `cloudUser` / `localDevice` | 每次挂载重读 | 轮询**永不重读** |
| 窗口重新可见 | — | 只重启 interval，不立即刷新 |
| 轮询能否启动 | — | 挂载时取决于 `!document.hidden` |

- 「一进来就需检查」：`local_agent_status`（`src-tauri/src/commands/agent.rs:188-203`）在 sidecar 未监听时返回 Err，而 sidecar 是 `main.ts:29` 的 fire-and-forget 启动；胶囊挂载时的检查撞在这个窗口上 → `snapshot`/`binding` 停在 `null`。个人中心是稍后进入的路由，那时 Agent 已就绪。
- 「个人中心改完不更新」：轮询不含 `cloudUser`/`localDevice`，且重新可见时不刷新。

### 未闭环的一条（须实机判定，勿写成推断）

`document.hidden` 在 Tauri WebView 启动时是否为 true，本轮**未实测**。若为 true，旧代码的 interval 一个都不建，轮询整场缺席——这能单独解释两个症状；若为 false，则症状来自启动竞态 + 30s 延迟。修复对两种都成立（初始不再读 `document.hidden`，改为乐观可见 + 事件纠正），但走查时须测：**不做任何点击等满 30 秒，胶囊会不会自己变绿**，读数按实测写回本节。

## 测试与读数

- `npx vitest run`（**web/ 下跑**）：49 文件 / **476 用例**通过（462 → 476，净增 14：`bitAccountDiffers` 8、`maskBitAccountId` 3、`loadWorkEnvInputs` 3）。
- `npm run build:cloud`、`npm run build:desktop` 均成功（仅既有 chunk 提示）。
- **变异对照**（撤掉新行为，看用例是否变红）：
  - 把 `loadWorkEnvInputs` 换回只读 `service.status()` + `devices.get()` → 3 条接线用例红；
  - 把 `aggregateWorkEnv` 换回旧的内联判定 → 一致性用例红。
  均还原后全绿。

### 判定边界（枚举过的输入形态）

`bitAccountDiffers` 对**比对不了**的输入倒向「不一致」，不是「一致」：

| 输入 | 取值 | 为何 |
| --- | --- | --- |
| 账号一致 | false | 首尾 4 位吻合 |
| 账号不同 | true | 客户端换过账号 |
| `bit_account_bound=false`（即便有残留掩码） | false | 闸门是绑定标志，不是掩码非空 |
| 掩码整个是 `****`（后端 `len<=8` 的产物） | **true** | 无从比对，宁可多给一次自助入口 |
| 本机账号短到无法按首尾 4 位切分 | **true** | 同上 |

另：`bitAccountDiffers` 的判定闸门由「掩码非空」改为「`bit_account_bound`」，与旧实现在这组输入上不同；这条差异由一致性用例钉住。

## 继承的未提交改动（非本次引入）

开始前工作区已有未提交编辑：`WorkEnvPill.vue` 里 `bitRowText`（账号不一致时比特浏览器行显示「账号待确认」）已定义但模板未接线，`PersonalInfoPage.vue` 的注释已改词。本次**保留**这些改动，并把 `bitRowText` 接进模板（原先那行仍读 `env.page.bitbrowserText`，与上方注释说的行为不符）。

## 未改

- `contracts/` 三处仍以「以当前环境为准」指代该 UI 标签（`cloud-error-codes/v1/browser-profile.yaml:7`、`cloud-api/v1/browser-profiles.openapi.yaml:43,93`）。`overwrite` 的 wire 语义未变，故未动；若要与 UI 改名保持一致，需按契约策略 bump revision，待用户裁定。
- 胶囊判定口径（额外要求 `nodeId` + `cloudUser`）不变；用户未报「两者结论相反」这一类症状。
- 后端、Agent、Desktop 零改动。

## 待用户复验（需重打 DMG）

1. 冷启动后**不做任何点击**，胶囊应在 Agent 就绪后自动变绿；面板不留 `agent unreachable` 残留。
2. **判别实测**：不点任何东西等满 30s，记下胶囊是否自行转绿（判定上面那条未闭环项）。
3. 个人中心切换比特账号后，胶囊在 30s 内、或切走窗口再切回时立即变为「需检查 / 账号待确认」。
4. 账号一致时个人中心不出现「比特账号绑定」按钮；不一致时出现，弹窗显示新文案与掩码账号，确认后账号行更新、胶囊转绿。
5. 停比特浏览器 → 只落比特浏览器条 blocker，本机服务行仍「已连接」。
