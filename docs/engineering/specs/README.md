<!-- governance: class=index default_load=task -->

# Engineering Specs

Long-lived engineering specs belong here only when they describe current system design.

Do not place implementation plans, progress notes, session handoffs, or temporary code-delivery records in this directory. A CHG's formal record is `delivery/active/<change-id>/change.md`; use optional `.ai/WORK_STATE.md` for temporary execution state and add `evidence/` only when needed.

This file is the index. Every other `*.md` in this directory must be listed below; keep the list complete when a spec is added or removed.

## Current capability designs

- [M4-M5 Cloud 内容生产工程设计](2026-09-24-m4-m5-cloud-content-production.md)：Cloud Scheduler / Worker / FFmpeg、对象存储、文件传输和恢复边界（ADR-0017）。
- [Web / Desktop 前端架构与视觉体系基线](../../standards/frontend/前端架构与视觉规范.md)：一套 Vue 源码两种运行模式、仓库与目录职责、开发与构建命令、多仓库版本锁定，以及 Design Token、组件库边界、页面模板与 UI Review 清单。
