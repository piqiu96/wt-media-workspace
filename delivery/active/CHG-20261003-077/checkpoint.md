# CHG-20261003-077 实施进度

- Status: IMPLEMENTING
- 当前：产品 `v0.1.0-rc.13` 打包 Run `37199184328` 已成功；Task 10/11 已分别在 Cloud commit `620cf89`、`be1d1a1` 完成。Task 12 的 Cloud 分支和 `v0.1.0-rc.12` Tag 已推送 GitHub 并回读指向 `be1d1a1`；Workspace 手动提交产品 Tag 脚本、测试和 `v0.1.0-rc.14` Manifest 已就绪，待提交推送。
- 已完成：`bin/wtmctl`（Go）实现远程变量拉取、Schema/取值校验、Artifact 校验、配置渲染、Migration、数据库验证、版本安装、`current` 原子切换、只读验收和回退；Python/shell 逐条部署入口全部删除，包内不再包含 `deploy/*.py`、`deploy/*.sh`；变量从 JSON 切换为 TOML 并上传远端回读校验通过；Cloud `README.md` 与 `deploy/DEPLOYMENT.md` 收敛为 `/home/www/wt-media-cloud/output` 一键部署命令。
- 已完成：`wtmctl`（含从包推导 release/package_root）、TOML 变量、路径绝对化、二进制改名、认证日志。
- 未完成：Task 12 的手动 Tag 脚本、源码/Tag 推送、GitHub 构建与摘要回读；RC13 Artifact 摘要回读；宝塔实际服务器验收（用户执行）。
- 阻塞：当前无代码阻塞；最终服务器数据库/账号创建与宝塔操作需要用户执行。
- 最近验证：Task 12 的 Cloud `go test ./... -count=1`、目标 `go vet` 与 4 项打包脚本测试通过；Workspace 手动 Tag 脚本 5 项测试、Manifest 校验通过。Workspace 全量 106 项测试有 5 项失败，均为既有 M0/跨仓 Contract/交付对齐断言，未修改相应检查文件；详情见 `evidence/rc14-manual-tag-and-build.md`。此前本地启动演练见 `evidence/cloud-local-package-start-from-home.md`。

- 本地私有变量：已删除旧 `~/.wt-media/config-variables/` 与 `*.json`；当前使用 `~/.wt-media/upload-config-variables.py`（TOML）和 `~/.wt-media/vars/cloud/{online,pre}.toml`，两者各 11 个变量，上传对象为 `wt-media/vars/cloud/{online,pre}.toml`，远端回读 SHA-256 一致，脚本不入 Git。

- 最终方案：单一 `bin/wtmctl` 负责远程变量拉取、校验、Artifact 校验、渲染、Migration、安装、current 切换和只读验收；宝塔独占服务启停。
- 路径裁定：在线服务器统一使用 `/home/www/wt-media-cloud/output`；变量文件使用 TOML（`online.toml`/`pre.toml`）；运行端口 `127.0.0.1:8188`。
