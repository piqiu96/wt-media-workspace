# 环境重建证据（A2 恢复 Cloud 配置重验前）

日期：2026-08-05
CHG：CHG-20260725-031（M2-B 浏览器窗口收口）
目的：从最新源码确定性重建本地验收环境，供用户人工重验 A2 恢复 Cloud 配置。

## 关键提交（本次环境必须内嵌）

- Agent `fbf9576`（05:16:32）：`update_profile` 读回并保留 BitBrowser 当前指纹（A2 502 修复）
- Cloud `c38cb3b`（05:16:43）：移除「取消变更」按钮

## 首次 `all` 的新鲜度问题

第一轮 `m2b-local-acceptance.sh all`（无 `--force-restart`）发现 Cloud/Agent 已健康即复用：
- Agent PID 65569 启动 04:21:02，**早于** 修复提交 fbf9576（05:16:32）→ 陈旧，A2 修复未生效。

按 environment-bring-up skill 规则不信任"已健康"进程，改用 `all --force-restart` 强制重建。

## 强制重建结果（`all --force-restart`）

| 步骤 | 命令 | 实际 | PASS/FAIL |
|---|---|---|---|
| 停旧进程 | force-restart 杀 18080/8765 陈旧进程 | PID 65568/65569 已停 | PASS |
| Cloud 重建 | `go run ./cmd/server` | PID 67941，启动 05:22:41 > c38cb3b（05:16:43） | PASS |
| Agent 重建 | `.venv/bin/python -m wt_media_agent.local_api.server` | PID 67946，启动 05:22:43 > fbf9576（05:16:32） | PASS |
| Agent 含修复 | 源码 grep `_read_profile_fingerprint` | 2 处存在 | PASS |
| migrations | `scripts/migrate.sh` | migration ok, 18 total | PASS |
| DMG | `cargo tauri build --bundles dmg --no-sign`（先清理产物） | 构建成功，挂载 /Volumes/WT Media，App 已启动 | PASS |

## 门禁独立复核（harness + 手动）

| 门禁 | 实际 | PASS/FAIL |
|---|---|---|
| Cloud `/api/v1/health` | errcode 0 | PASS |
| Agent `/healthz` + `/api/v1/status` | bitbrowser_status normal | PASS |
| BitBrowser via Agent | 正常 | PASS |
| Desktop assets fresh | chunk 含 127.0.0.1:18080/api/v1 | PASS |
| DMG fresh + mounted | /Volumes/WT Media（hfs, read-only）挂载；App PID 68232 运行 | PASS |
| CORS preflight `Origin: http://tauri.localhost` | 204 + `Access-Control-Allow-Origin: http://tauri.localhost` | PASS |
| 登录冒烟 admin | `all` verify_login PASS | PASS |
| 登录冒烟 operator01/operator01 | errcode 0，operator/team1/game1 | PASS |

## 结论

环境已就绪，Cloud/Agent/DMG 均为最新源码。用户可人工重验 A2：对产生 Diff 的窗口执行「恢复Cloud配置并读回验证」，确认不再 502、写回读回一致、指纹未重置。若报「无法读取窗口当前指纹」说明指纹字段名不符，需调整 Agent `_read_profile_fingerprint` 字段名。
