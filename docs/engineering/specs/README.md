<!-- governance: class=index default_load=task -->

# Engineering Specs

Long-lived engineering specs belong here only when they describe current system design.

Do not place implementation plans, progress notes, session handoffs, or temporary code-delivery records in this directory. A CHG's formal record is `delivery/active/<change-id>/change.md`; use optional `.ai/WORK_STATE.md` for temporary execution state and add `evidence/` only when needed.

This file is the index. Every other `*.md` in this directory must be listed below; keep the list complete when a spec is added or removed.

## Current capability designs

- [社媒账号：数据、接口与本机执行](social-accounts.md)：矩阵维护、人工登录识别、Cookie 版本与接入批次；ADR-0030。

- [运营资源：Cloud 事实与本机执行](2026-10-29-operating-resources.md)：社媒账号、浏览器窗口、代理的事实归属、同步、代理操作恢复、角色与批量处理边界（ADR-0027）。
- [M4-M5 Cloud 内容生产工程设计](2026-09-24-m4-m5-cloud-content-production.md)：Cloud Scheduler / Worker / FFmpeg、对象存储、文件传输和恢复边界（ADR-0017）。
- [Web / Desktop 前端架构与视觉体系基线](../../standards/frontend/前端架构与视觉规范.md)：一套 Vue 源码两种运行模式、仓库与目录职责、开发与构建命令、多仓库版本锁定，以及 Design Token、组件库边界、页面模板与 UI Review 清单。
