# CHG-20260924-060 — wt-media-desktop 状态

- 2026-09-24 T-01：未开始。
- 2026-09-24 T-02（CSP，commit `9945f58`，3 文件）：`resources/desktop.production.toml` 的
  `csp_connect_src` 改为 `ipc: http://ipc.localhost http://127.0.0.1:18080`；两处守卫字面量同步
  （`bootstrap.rs` 全策略金标、`config.rs` 拒绝表 `from` 串）。**先失败**恰好这两条红
  （61 passed; 2 failed），同步后 **63 passed; 0 failed**。
  - 真实启动取证：新增 `evidence/tools/t02_csp_shipped_value_launch.py`，
    `importlib` 导入 CHG-056 的 `run_leg`（不复制，避免两处漂移），**从出货文件解析** `csp_connect_src`
    后跑两条 leg：出货值 → `ipc:// refusals 0`；改动前的值（阳性对照）→ `ipc:// refusals 3`。
    同一 leg 复现 sidecar 启动、`401/401/200` token 三态、data dir 三项，CSP 改动无外溢。
  - **被逼出的文档回写**：金标 docstring 原称该串与已删除的 `tauri.conf.json` 字面量「逐字相同」，
    改值后不再成立，已改写为「有一处刻意改动的例外」。保留测试名以免无谓 diff。
  - **未覆盖（登记）**：生产**整文件**启动——出货文件 `agent.port = 8765` 是开发者自己 dev Agent
    的端口，按本 CHG 边界不得触碰，故 leg 用 `development` + scratch 端口，测的是**出货文件声明的取值**
    而非「生产配置整文件跑起来」；非 macOS 平台未观测（Windows/Linux 的 IPC 是真 `ipc://` 方案），不外推。
- 2026-09-24 T-03：未开始。
