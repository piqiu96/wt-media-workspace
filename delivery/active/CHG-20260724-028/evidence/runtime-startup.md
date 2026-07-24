# Runtime startup evidence

## 时间

2026-07-24

## 操作

启动并核对 CHG-20260724-028 人工验收所需运行环境。

## 实际结果

- Cloud API 已运行，`/api/v1/health` 返回 `status=ok`。
- Local Agent 已运行，`/api/v1/status` 返回 `status=idle`、`bitbrowser_status=normal`，并能读取真实 BitBrowser `main_user_id` 与本机 Profile 列表。
- Cloud Web dev server 已运行，`http://127.0.0.1:5173/login` 可访问。
- Desktop Web dev server 已运行，`http://127.0.0.1:5174/login` 可访问。
- 真实 Tauri Desktop 壳已通过 `cargo run --no-default-features --color always --` 启动。

## 验收提示

Local Agent 当前 `node_id` 为空属于启动后的未绑定状态。用户需在 Desktop 的“环境状态”页执行“重新检测并绑定”，让 Cloud 记录当前可信本机节点后，再进入媒体账号详情执行单个账号检查。

## 结论

人工验收环境已启动，等待用户在 Desktop 内完成真实 BitBrowser 账号检查链路验证。
