# CHG-20261003-077 实施进度

- Status: IMPLEMENTING
- 当前：产品 `v0.1.0-rc.13` 打包 Run `37199184328` 已成功；其 Cloud `v0.1.0-rc.11` 仍需服务器安装验收。针对用户追加的任意工作目录启动与关键错误日志要求，Task 10 已在 Cloud commit `620cf89` 完成路径解析硬化、启动路径/步骤日志和验证，待后续制品发布裁定。
- 已完成：`bin/wtmctl`（Go）实现远程变量拉取、Schema/取值校验、Artifact 校验、配置渲染、Migration、数据库验证、版本安装、`current` 原子切换、只读验收和回退；Python/shell 逐条部署入口全部删除，包内不再包含 `deploy/*.py`、`deploy/*.sh`；变量从 JSON 切换为 TOML 并上传远端回读校验通过；Cloud `README.md` 与 `deploy/DEPLOYMENT.md` 收敛为 `/home/www/wt-media-cloud/output` 一键部署命令。
- 已完成：`wtmctl`（含从包推导 release/package_root）、TOML 变量、路径绝对化、二进制改名、认证日志。
- 未完成：RC13 Artifact 摘要回读；Task 10 新制品发布裁定；宝塔实际服务器验收（用户执行）。
- 阻塞：当前无代码阻塞；最终服务器数据库/账号创建与宝塔操作需要用户执行。
- 最近验证：Task 10 的 Cloud `go test ./... -count=1`、目标 `go vet`、部署包 Python 测试和 `git diff --check` 通过；临时发布二进制从无关 cwd 启动时，缺失配置错误准确指向发布目录。细节见 `evidence/cloud-runtime-paths-and-startup-logs.md`。

- 本地私有变量：已删除旧 `~/.wt-media/config-variables/` 与 `*.json`；当前使用 `~/.wt-media/upload-config-variables.py`（TOML）和 `~/.wt-media/vars/cloud/{online,pre}.toml`，两者各 11 个变量，上传对象为 `wt-media/vars/cloud/{online,pre}.toml`，远端回读 SHA-256 一致，脚本不入 Git。

- 最终方案：单一 `bin/wtmctl` 负责远程变量拉取、校验、Artifact 校验、渲染、Migration、安装、current 切换和只读验收；宝塔独占服务启停。
- 路径裁定：在线服务器统一使用 `/home/www/wt-media-cloud/output`；变量文件使用 TOML（`online.toml`/`pre.toml`）；运行端口 `127.0.0.1:8188`。
