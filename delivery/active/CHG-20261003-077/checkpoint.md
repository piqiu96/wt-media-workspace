# CHG-20261003-077 实施进度

- Status: IMPLEMENTING
- 当前：在 RC11 基础上收敛部署控制面。Cloud `main` `1d6457f` 已推送并打 Tag `v0.1.0-rc.9`，`M0 Cloud` CI `37182796598` 通过。产品 `v0.1.0-rc.12` 已发布为成功 Pre-release（Run `37182978601` 全绿），Cloud Artifact `wt-media-cloud_v0.1.0-rc.12_linux-amd64.tar.gz` SHA-256 `90026317...6fb6`。RC11 已将模板变量缩减为 11 个。
- 已完成：`bin/wtmctl`（Go）实现远程变量拉取、Schema/取值校验、Artifact 校验、配置渲染、Migration、数据库验证、版本安装、`current` 原子切换、只读验收和回退；Python/shell 逐条部署入口全部删除，包内不再包含 `deploy/*.py`、`deploy/*.sh`；变量从 JSON 切换为 TOML 并上传远端回读校验通过；Cloud `README.md` 与 `deploy/DEPLOYMENT.md` 收敛为 `/home/www/wt-media-cloud/output` 一键部署命令。
- 未完成：宝塔实际服务器验收（用户执行）。
- 阻塞：当前无代码阻塞；最终服务器数据库/账号创建与宝塔操作需要用户执行。
- 最近验证：Cloud `go test ./...` 全部通过；`scripts/verify/test_package_release_linux`、`test_stamp_desktop_web` 通过；`wtmctl vars check/pull/config render` 与真实 `config_online` 模板端到端渲染通过；Workspace release 打包测试通过；RC12 `package` 作业对真实 Cloud Artifact 执行 `verify_cloud`（含 `bin/wtmctl`、Schema/示例、拒绝 `deploy/*.py|*.sh`）并通过。

- 本地私有变量：已删除旧 `~/.wt-media/config-variables/` 与 `*.json`；当前使用 `~/.wt-media/upload-config-variables.py`（TOML）和 `~/.wt-media/vars/cloud/{online,pre}.toml`，两者各 11 个变量，上传对象为 `wt-media/vars/cloud/{online,pre}.toml`，远端回读 SHA-256 一致，脚本不入 Git。

- 最终方案：单一 `bin/wtmctl` 负责远程变量拉取、校验、Artifact 校验、渲染、Migration、安装、current 切换和只读验收；宝塔独占服务启停。
- 路径裁定：在线服务器统一使用 `/home/www/wt-media-cloud/output`；变量文件使用 TOML（`online.toml`/`pre.toml`）；运行端口 `127.0.0.1:8188`。
