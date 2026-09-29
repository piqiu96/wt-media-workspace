# Engineering Specs

Long-lived engineering specs belong here only when they describe current system design.

Do not place implementation plans, progress notes, session handoffs, or temporary code-delivery records in this directory. Current implementation work belongs under `delivery/active/<change-id>/change.md`.

This file is the index. Every other `*.md` in this directory must be listed below; keep the list complete when a spec is added or removed.

## Current capability designs

- [M4-M5 Cloud 内容生产工程设计](2026-09-24-m4-m5-cloud-content-production.md)：Cloud Scheduler / Worker / FFmpeg、对象存储、文件传输和恢复边界（ADR-0017）。
- [Web / Desktop 前端架构与视觉体系基线](web-desktop-visual-system.md)：一套 Vue 源码两种运行模式、仓库与目录职责、开发与构建命令、多仓库版本锁定，以及 Design Token、组件库边界、页面模板与 UI Review 清单。

## Programs and conventions

- [Desktop × Agent 联合上线工程优化程序](2026-09-23-launch-engineering-optimization-program.md)：上线前工程加固程序（已结束，四个阶段全部归档 DONE）；记录 A/B/C/D 四阶段的验收结果与未决风险。
