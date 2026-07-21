# CHG-20260721-020: M2 跨闭环执行基础建设

## 1. Basic Information

- Level: L
- Status: DONE
- Created: 2026-07-21
- Completed: 2026-07-22
- Affected repositories: `wt-media-cloud`, `wt-media-agent`, `wt-media-desktop`, `wt-media-workspace`
- Current repository: `wt-media-workspace`
- Milestone: `delivery/milestones/M2-account-runtime.md`
- Design: `docs/superpowers/specs/2026-07-21-m2-completion-design.md`

## 2. Change Goal

归档 CHG-020 已有且可复验的 M2 跨端技术基础，包括可信自动化门禁、权限与会话保护、敏感任务与结果投影、Profile/代理/Cookie 执行基础、脱敏、重试和 Desktop Agent 生命周期基础。

本 CHG 不再声明“完整交付 M2-A～E”。各业务闭环是否完成，只按 Milestone 成功事实与真实验收判断。

## 3. Completed Scope

- 恢复 Web API client、Cloud、Agent、Desktop 与 Workspace 自动化门禁；
- 增加媒体账号游戏范围回归、失效 Agent 会话排空、BitBrowser 绑定审计；
- 建立 Profile、代理、账号检查和 Cookie 的 typed task、Agent executor、结果读回与局部 Cloud 投影基础；
- 增加敏感字段脱敏、失败/取消任务新尝试和部分 UI 任务状态展示；
- 增加 Desktop 对 Local Agent 子进程的持有和停止基础；
- 修复代理空列表页面与同步短操作边界。

## 4. Acceptance Boundary

已完成内容及复验结果见 `evidence/governance-scope-audit.md`。

以下内容没有被本 CHG 验收为完成：

- M2-A 三角色 UI/API、401/403 与真实绑定人工验收；
- M2-B Profile 完整生命周期、Diff 双向处理和单个/批量账号检查用户闭环；
- M2-C 无副作用导入预览、完整配额、真实代理写入/读回与 Profile 打开；
- M2-D Cookie 实际写入/读回、三种开户、部分成功与精确重试；
- M2-E 打包 Sidecar、真实 Desktop 操作、恢复、安全和最终人工验收。

## 5. Explicitly Not Doing

- 不把代码存在、任务创建或局部自动化测试当作业务闭环完成；
- 不修改 M3 及以后范围；
- 不在本治理收口中继续修改运行时代码；
- 不将 M2 标记为 `DONE` 或 `VERIFYING`。

## 6. Checkpoint

- Completed: 已有阶段性基础工作完成事实审计；Cloud、Agent、Web、Desktop 与 Workspace 自动化重新通过；范围已从“完整 M2”纠正为“跨闭环执行基础建设”。
- Current: CHG-020 已完成并准备归档；M2 保持 `IN_PROGRESS`。
- Next: 创建独立 M2-A 人工与真实环境验收收口 CHG。
- Blockers: M2-A 人工角色/UI/真实绑定验收尚未执行，因此任何 M2 业务闭环均不能声明完成。
- Recent verification: Cloud 全量 Go PASS；Agent 48/48 PASS；Web 8/8 与双构建 PASS；Desktop 2/2 PASS；Workspace 静态 M2 与产品计划对齐 PASS。

## 7. Evidence Index

- `evidence/governance-scope-audit.md` — 本次声明、原 Evidence、提交和复验结果的事实表。
- 其余 Evidence 文件保留原始阶段性实现与验证记录。

## 8. Pending Questions

None.
