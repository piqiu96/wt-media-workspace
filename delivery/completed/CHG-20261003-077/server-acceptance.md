# CHG-20261003-077 宝塔预发布人工验收记录

本记录在实际服务器部署时填写。Cloud 包内步骤见 `wt-media-cloud/deploy/DEPLOYMENT.md`；这里不记录数据库密码、管理员密码、平台密钥或对象存储密钥。

> 2026-10-09 回填：用户对 Cloud 部署、数据库当前态和宝塔/HTTPS/登录走查答复「完成」「完成」「正常」。下表原为 RC14 操作模板，实际服务器 Tag、命令输出、路径和回退细节未提供，保留「待填写」以避免补造证据。真实跨版本数据库升级与回退由用户明确延期至下一次升级；见 `evidence/2026-10-09-manual-acceptance.md`。

## 版本与安装

| 项目 | 实际值 / 证据 |
| --- | --- |
| 产品 Tag | `v0.1.0-rc.14` |
| Cloud 组件 Tag | `v0.1.0-rc.12` |
| GitHub Actions Run URL | `https://github.com/piqiu96/wt-media-workspace/actions/runs/37581481877`（全部发布作业成功） |
| Cloud Artifact 文件名与 SHA-256 | `wt-media-cloud_v0.1.0-rc.14_linux-amd64.tar.gz`；`e7ea73b3984c4735d3e61db1a008ff1e8ea0c48966cf50cc39b0323485d9ac4e` |
| 服务器直拉与校验结果 | 待填写：只读 GitHub 权限、下载目录、`SHA256SUMS` 和固定摘要核验输出 |
| Cloud 源码 Commit | `be1d1a11a603da475b4d6ce16244927adc8d8486` |
| 服务器系统、CPU 架构、宝塔版本 | 待填写 |
| 安装路径与 `current` 指向 | 待填写 |
| 维护提示开始/结束时间 | 待填写 |

## 数据与配置

| 检查项 | 结果 / 证据 |
| --- | --- |
| 已手动创建预发布 MySQL 库与专用账号；目标库名/主机 | 待填写 |
| 迁移前 MySQL 备份位置与恢复演练结果 | 待填写 |
| 对象存储备份或隔离前缀 | 待填写 |
| 版本内 `config/` 权限、`online` 环境记录、HTTP 监听地址、HTTPS 域名 | 待填写 |
| 首次迁移结果（应为 50 个） | 待填写 |
| 重复迁移结果（应为 0 个） | 待填写 |
| `schema_migrations` 与 `users` 管理员行检查 | 待填写 |

## 运行验收

| 检查项 | 结果 / 证据 |
| --- | --- |
| 宝塔 Go 项目 Server / 进程管理器 Scheduler、Worker 状态 | 待填写 |
| 本机 `/healthz` 和 `/api/v1/health` | 待填写 |
| HTTPS 域名健康接口与 Web 页面 | 待填写 |
| HTTPS `/login` 刷新后仍能加载 Cloud Web；`/api/v1/health` 为 JSON | 待填写 |
| 初始管理员 `admin/admin123` 登录 | 待填写 |
| 回退切换演练或未执行原因 | 待填写 |
| 异常、处理与发布结论 | 待填写 |

此记录只覆盖 Cloud 预发布安装与基础运行。对象存储业务写入、BitBrowser、真实发布流程和正式版上线另行验收。

## 服务器一键部署命令

Cloud 包内步骤见 `wt-media-cloud/deploy/DEPLOYMENT.md`。服务器操作只需准备 profile 与预签名 URL 文件，随后由 `wtmctl` 一键完成：

Cloud tar 位于上述 Run 的 `cloud-linux-amd64` Actions Artifact ZIP 内（Artifact ID `11463834682`，ZIP SHA-256 `db9f52f0e1e64225d8522ad78888bac8957612fbb2d374423fdc4659deb79b12`），不是 GitHub Pre-release 的直接附件。在服务器上安装 GitHub CLI，并通过受控环境提供 `GH_TOKEN`：令牌仅需对私有 `piqiu96/wt-media-workspace` 仓库具有 Actions 读取权限，不写入仓库、部署 profile 或命令历史。下面的命令直接在服务器拉取、核验并解压固定 RC14 制品，不经本地电脑中转：

```bash
set -euo pipefail
: "${GH_TOKEN:?需要 GitHub Actions 只读令牌}"
command -v gh
test "$(uname -m)" = x86_64
output=/home/www/wt-media-cloud/output
package=wt-media-cloud_v0.1.0-rc.14_linux-amd64
mkdir -p "$output"
test ! -e "$output/$package"
download_dir="$(mktemp -d "$output/.download-rc14.XXXXXX")"
gh run download 37581481877 \
  --repo piqiu96/wt-media-workspace \
  --name cloud-linux-amd64 \
  --dir "$download_dir"
(cd "$download_dir" && sha256sum -c SHA256SUMS)
printf '%s  %s\n' \
  e7ea73b3984c4735d3e61db1a008ff1e8ea0c48966cf50cc39b0323485d9ac4e \
  "$download_dir/$package.tar.gz" | sha256sum -c -
tar -xzf "$download_dir/$package.tar.gz" -C "$output"
test -x "$output/$package/bin/wtmctl"
```

`gh run download` 会解开 Actions Artifact ZIP，因此此处直接验证包内 `SHA256SUMS` 和预先固定的 Cloud tar SHA-256。下载失败或任一校验失败时，`set -e` 会停止执行；此时不运行 `wtmctl deploy apply`。保留 `download_dir` 供事后核对，成功验收后再清理。

```bash
cd /home/www/wt-media-cloud/output/wt-media-cloud_v0.1.0-rc.14_linux-amd64
./bin/wtmctl artifact verify --profile /home/www/wt-media-cloud/output/online-deploy.toml
./bin/wtmctl doctor        --profile /home/www/wt-media-cloud/output/online-deploy.toml
./bin/wtmctl deploy plan   --profile /home/www/wt-media-cloud/output/online-deploy.toml
# 宝塔先停止 Server、Worker、Scheduler
sudo ./bin/wtmctl deploy apply --profile /home/www/wt-media-cloud/output/online-deploy.toml
# 宝塔再按 Server -> Worker -> Scheduler 启动
sudo /home/www/wt-media-cloud/current/bin/wtmctl deploy verify --profile /home/www/wt-media-cloud/output/online-deploy.toml
```

变量表：`wt-media/vars/cloud/online.toml`（服务器仅保存 `online.url` 预签名地址）；本地私有上传工具 `/Users/aqiuye/.wt-media/upload-config-variables.py`（不入 Git）。初始管理员保持 `admin/admin123`。

Server 启动文件为 `current/bin/wt-media-cloud`（不再是 `server`）。程序按 `WT_MEDIA_CLOUD_HOME` → 二进制所在 `<home>/bin` → 当前工作目录解析根路径，`config`/`logs`/`web` 默认由根路径派生，并可用 `WT_MEDIA_CLOUD_CONFIG_PATH`、`WT_MEDIA_CLOUD_LOG_PATH`、`WT_MEDIA_CLOUD_WEB_PATH` 覆盖，因此宝塔从 `current/bin` 启动也能找到配置。
