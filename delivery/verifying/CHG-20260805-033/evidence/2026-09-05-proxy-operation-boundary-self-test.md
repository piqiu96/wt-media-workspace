# 代理操作入口边界调整：自动自测与验收环境

日期：2026-09-05  
CHG：CHG-20260805-033  
关联提交：`133ada5`、`f9023f7`、`e28cf7d`

## 自动自测

| 操作 | 预期 | 实际 | 结果 |
| --- | --- | --- | --- |
| `npm test -- --run`（Cloud Web） | 页面职责与既有前端行为通过 | 12 文件、44 测试通过；含 `proxyOperationBoundary.test.js` 2 项 | PASS |
| `go test ./internal/modules/proxy ./internal/modules/profilebinding -count=1` | 代理写回、正式关系与绑定模块不回归 | 两模块均通过 | PASS |
| `scripts/m2b-local-acceptance.sh all` | 从当前源码重建迁移、前端与 DMG | 27 条迁移已就绪；Desktop 前端与 DMG 重建完成 | PASS |
| Cloud/Agent 运行态检查 | Cloud、Agent 与 BitBrowser 均可用 | Cloud health `errcode:0`；Agent `healthz:ok`；`bitbrowser_status:normal` | PASS |
| DMG 启动检查 | 当前构建的桌面应用已启动 | `WT Media_0.1.0_aarch64.dmg` 于 2026-09-05 21:44 生成；`/Volumes/WT Media/WT Media.app` 进程运行 | PASS |

## 未执行的有副作用检查

未对已有 BitBrowser 窗口执行分配、替换或解绑。以上动作会立即写入真实窗口代理配置；应由人工选择明确可用于验收的窗口和代理后执行，并以 BitBrowser 实际读回作为最终证据。

