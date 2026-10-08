# CHG-20261003-077 实施进度

- Status: IMPLEMENTING
- 当前：Cloud `v0.1.0-rc.12` 和产品 `v0.1.0-rc.14` 已推送；产品 [`release.yml` Run 37581481877](https://github.com/piqiu96/wt-media-workspace/actions/runs/37581481877) 全部发布作业成功，Pre-release 已生成。Cloud Linux tar SHA-256 `e7ea73b3984c4735d3e61db1a008ff1e8ea0c48966cf50cc39b0323485d9ac4e` 已与 `build-info.json`、Actions Artifact 与本地下载核对。
- 已完成：`bin/wtmctl`（Go）实现远程变量拉取、Schema/取值校验、Artifact 校验、配置渲染、Migration、数据库验证、版本安装、`current` 原子切换、只读验收和回退；Python/shell 逐条部署入口全部删除，包内不再包含 `deploy/*.py`、`deploy/*.sh`；变量从 JSON 切换为 TOML 并上传远端回读校验通过；Cloud `README.md` 与 `deploy/DEPLOYMENT.md` 收敛为 `/home/www/wt-media-cloud/output` 一键部署命令。
- 已完成：`wtmctl`（含从包推导 release/package_root）、TOML 变量、路径绝对化、二进制改名、认证日志。
- 未完成：宝塔服务器直接拉取 RC14 Artifact、实际安装、数据库迁移、三进程与 HTTPS/登录验收（用户执行并回填 `server-acceptance.md`）。直拉命令及本地校验见 `evidence/server-direct-pull.md`；RC13 历史摘要见 `evidence/rc14-manual-tag-and-build.md`。
- 阻塞：当前无代码阻塞；服务器需准备私有 Workspace 仓库 Actions 只读凭据，最终数据库/账号创建与宝塔操作需要用户执行。
- 最近验证：Task 12 的 Cloud `go test ./... -count=1`、目标 `go vet` 与 4 项打包脚本测试通过；Workspace 发布相关 18 项测试、Delivery governance、AI workspace 校验通过。Workspace 全量 106 项测试有 5 项失败，均为既有 M0/跨仓 Contract/交付对齐断言，未修改相应检查文件；详情见 `evidence/rc14-manual-tag-and-build.md`。此前本地启动演练见 `evidence/cloud-local-package-start-from-home.md`。

- 本地私有变量：已删除旧 `~/.wt-media/config-variables/` 与 `*.json`；当前使用 `~/.wt-media/upload-config-variables.py`（TOML）和 `~/.wt-media/vars/cloud/{online,pre}.toml`，两者各 11 个变量，上传对象为 `wt-media/vars/cloud/{online,pre}.toml`，远端回读 SHA-256 一致，脚本不入 Git。

- 最终方案：单一 `bin/wtmctl` 负责远程变量拉取、校验、Artifact 校验、渲染、Migration、安装、current 切换和只读验收；宝塔独占服务启停。
- 路径裁定：在线服务器统一使用 `/home/www/wt-media-cloud/output`；变量文件使用 TOML（`online.toml`/`pre.toml`）；运行端口 `127.0.0.1:8188`。

## 2026-10-08 增量

- 用户裁定：Windows Desktop 控制台、日志、路径与下载设置问题并入本 CHG，不再另立 CHG-20261008-078。
- 当前增量范围：按已批准设计修复 Windows release GUI subsystem、每用户 Windows 路径、日志读写一致性、侧车 Agent 数据目录传递、旧数据保护，以及 Cloud Web 下载目录提示。
- 当前边界：Windows 实机和 CI 证据尚未回填；本地实现和单元测试不能单独宣布部署闭环。

## 2026-10-08 Windows 修复执行状态

- Desktop：Commit `5deebf9` 实现 Windows release-only GUI subsystem、统一 `SystemPaths`、Windows per-user Desktop/Agent 路径、日志临时回退、Sidecar 环境变量和旧数据保护。`cargo check --all-targets --message-format=short`、`cargo test`（527 通过 / 0 失败 / 6 忽略）、`git diff --check`、`python3 tests/windows_release_subsystem.py` 均通过。证据：`evidence/windows-desktop-console-logging.md`。
- Cloud Web：Commit `9478a64` 将保存位置提示改为 `请先选择下载目录`，无默认下载目录。局部 wiring 测试与全量 `npm test`（50 个文件 / 488 项）通过。证据：`evidence/cloud-web-download-prompt.md`。
- 未闭环：尚未构建并检查 Windows 主 EXE PE subsystem，也未执行 Windows 实机/CI 安装与下载、日志、重复启动、卸载回归。
