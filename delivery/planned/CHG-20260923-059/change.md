# CHG-20260923-059：联合工程优化 D——Sidecar、打包、升级与回归

- Status: PLANNED
- Level: L
- 锚点：`docs/engineering/specs/2026-09-23-launch-engineering-optimization-program.md` §3 CHG-D
- 日期：2026-09-23
- 前置：CHG-20260923-058（C）完成
- 当前仓库：`wt-media-desktop`、`wt-media-agent` 为主；`wt-media-workspace`（发布矩阵与治理）为辅

## 独立目标与范围

Sidecar 协议完善（动态端口就绪通知、实例身份验证防连旧进程、spawn 后真实健康检查、退出遵守 draining 与检查点）、打包交付闭环（PyInstaller 产物完整性、`config_online → 产物/config` 打包步骤与校验、版本兼容验证、正式安装包脱离开发源码/venv/开发机路径运行）、升级回滚不覆盖用户配置/SQLite/检查点/待回传结果、现有 M2 业务回归。

**吸收自 CHG-20260923-053 Task 7**：`scripts/build_desktop_sidecar.py` 落地 `config_online → 产物/config` 整目录替换（验收：`diff -r` 无差异）；Agent 侧 `AGENTS.md`/`README.md`/`contracts/*/README.md` 同步；workspace skill `agent-platform-adapter-change` 改指 `clients/<platform>` 并跑 `sync_skills.py` 同步生成副本。

关键验收点（来自程序总纲）：
- 发布可追溯：Desktop 版本、Agent 版本、前端构建版本、Contract 版本、组件与资源版本。
- 发布脚本验证目标架构、Sidecar 完整性、必要资源及版本兼容性；前端与 Rust 使用同一目标环境（CHG-A 已建一致性检查的强化）。
- `config_online/agent.toml` 与 `resources/desktop.production.toml` 的生产真实地址必须替换占位（Q-01 的关闭条件）。

## 明确不做

- 不重写现有稳定脚本；不为目录整齐整体重构。
