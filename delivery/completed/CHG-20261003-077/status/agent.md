# agent 状态

- Status: DONE
- Evidence: `../evidence/windows-agent-download-commit.md`
- Notes: Agent commit `106f6ff` 修复 Windows 下载 `.part` 提交阶段只读句柄 `fsync` 与目录 `fsync` 不兼容路径。组件 Tag `v0.2.2-rc.3` 已推送并回读至该 commit。本地故障注入测试由红转绿；当前工作区 701 项测试通过，独立干净克隆的发布源 690 项通过。产品 RC17 Windows Agent 与 Desktop 构建作业成功，`build-info.json` 回读 Agent commit 为 `106f6ff`；真机最终文件、Cloud 成功状态尚未验证；用户远端 D: 文件保持原样。

- Final: 用户于 2026-10-09 确认 Windows D: 下载生成最终文件且 Cloud 任务成功；正式版 `v0.1.0` 固定 Agent `v0.2.2-rc.3`，发布作业通过。旧失败任务历史状态未单独回填。
