# T-13 批量验收反馈与 BitBrowser 离线提示

日期：2026-10-26

## 用户验收结论

| 项目 | 结论 | 依据 / 后续 |
| --- | --- | --- |
| 101-1 | 用户反馈 OK | 本次批量验收回复；保留原验收口径 |
| 101-2 | 用户反馈 OK | 本次批量验收回复；保留原验收口径 |
| 101-3 | 用户反馈 OK | 本次批量验收回复；保留原验收口径 |
| 101-4 | 发现问题，修复后待更新包 GUI 复看 | 用户截图：浏览器窗口页在 BitBrowser 未启动时显示原始 `502 Bad Gateway`、JSON 与 `Connection refused`。期望提示运营启动并登录比特浏览器后重试 |
| 101-5 | 退出人工验收清单 | 用户决定按时机复现，或由研发模拟自测。T-10 已有断开 `/report`、重启 Agent 后先补报且不重跑的故障注入 17/17；真实环境回归 64/64。无需用户在本轮人为制造故障 |

101-1/2/3 仅记录用户本次的 OK 反馈，不外推到未展示的子场景。101-4 在更新包实际 GUI 复看前不记为用户通过。

## 101-4 原因与处理

BitBrowser Local API 拒绝连接时，Agent 将网络不可达归入普通响应错误，并把底层异常放入 502 响应。Desktop 的窗口操作命令把状态码和响应体拼成字符串；页面直接展示该字符串。关闭窗口的客户端还会吞掉该类异常，可能误报成功。

- Agent 将连接拒绝/超时识别为 `BitBrowserUnavailableError`；扫描、分组、创建、打开、关闭、更新等受影响入口返回既有契约的 `503 bit_browser_offline`，附 `recovery_action=start_bitbrowser`，不向界面传底层异常。关闭窗口不再将离线视为已关闭。
- Desktop 窗口命令统一返回结构化 `GuardRefusal`，保留 Agent 的错误码及恢复动作；Agent 本身不可达时返回 `agent_unreachable`。
- 共用页面按错误码展示“请先启动比特浏览器并完成登录，然后重试”；批量窗口操作展示首个失败原因，扫描也使用统一提示。
- 沿用已有 `bit_browser_offline` 契约码，无新增跨仓协议版本。

实现提交：Agent `6e3db8b`、Desktop `8a03a49`、Cloud 共用前端 `5fd5240`。

## 自动化验证

| 验证 | 结果 |
| --- | --- |
| Agent 模拟 BitBrowser `Connection refused`，覆盖扫描/分组/创建/打开/关闭 | 五个入口返回 503、`bit_browser_offline`、`start_bitbrowser`，响应不含底层异常 |
| Agent 全量 `python3 -m unittest discover -s tests -q` | 728 项通过 |
| Desktop `cargo test --manifest-path src-tauri/Cargo.toml --offline --quiet` | 540 项通过，6 项忽略；另有 1 项新增结构化错误回归测试 |
| Cloud Web `npm test -- --maxWorkers 2` | 78 个测试文件、712 项通过；新增离线与一般 BitBrowser 响应错误文案测试 |
| Cloud Web `npm run build:desktop` | 构建通过 |

上述为源码与自动化证据，不等同于新打包 Desktop 的 GUI 验收。后续在更新后的 Desktop 包中关闭 BitBrowser，点击“浏览器窗口”的打开/扫描/关闭，确认看到可操作提示且无 502/JSON/连接拒绝原文；再启动并登录 BitBrowser 重试。

101-5 的既有证据：`evidence/T-10-full-verification.md` 的断网与重启补报读数，以及 `report.md` 的 17/17 和 64/64 汇总。
