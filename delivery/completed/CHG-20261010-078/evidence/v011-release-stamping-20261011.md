# v0.1.1 发布链烙入证据（2026-10-11）

- 产品 Tag `v0.1.1`（stable，manifest `releases/manifests/v0.1.1.yaml`：cloud `v0.1.1-rc.1` / agent `v0.2.2-rc.3` / desktop `v0.1.0-rc.8`）触发 `release.yml` run 38073520974，全部 job 绿。
- 烙入验证：从 run 的 `cloud-linux-amd64` artifact 取 `wt-media-cloud_v0.1.1_linux-amd64.tar.gz`，流式提取包内 `web/desktop-downloads.json`，与本地 `python3 -m scripts.release.desktop_downloads --tag v0.1.1` 生成的黄金清单 `cmp` 逐字节一致，SHA-256 `7b23dba26536c56287e78be5c23d58a94e7f351e50c395cc59a19fce4ae76f99`。清单内容：`version v0.1.1`，三平台 `file_name`/`url` 精确指向 `github.com/piqiu96/wt-media-workspace/releases/download/v0.1.1/WT-Media_v0.1.1_*`。
- 资产校验：`submit_tag.py v0.1.1 --verify` 退出码 0，六资产（三平台安装包 + build-info.json + SHA256SUMS + v0.1.1.yaml）名称与 SHA256 全部通过；Windows 安装包 SHA-256 `fb23144935f9e3d77710fd3580ffa3aa53a2cf3804b27f360e5ac8cafc3747a5`。
- 公开：草稿复验通过后人工执行 `gh release edit v0.1.1 --draft=false --prerelease=false`（本版 workflow 尚无自动公开，属预期），回读 `isDraft=false isPrerelease=false`；资产 URL 匿名 HEAD 返回 302（草稿期会 404）。
- 边界：本机直连 GitHub 曾超时，302 只证明 Release 已公开可达，真实下载速度与完整性以目标用户网络验收为准；线上 `curl https://wt.longyanyue.cn/desktop-downloads.json` 回读 v0.1.1 待 Cloud 包部署后执行。
- 后续正式版（v0.1.2+）由 PR #4 的 CI 自动公开取代本版的人工 `gh release edit`。
- 部署回读（2026-10-11，用户在宝塔完成 v0.1.1 Cloud 包部署后）：`https://wt.longyanyue.cn/desktop-downloads.json` 的 SHA-256 与烙入黄金清单完全一致（`7b23dba2…`），`version v0.1.1`；`/home` 与 `/` 均返回 200。CI 烙入 → 包 → 部署 → 线上读取全链路闭环。剩余人工验收：真实账号登录、目标用户网络三平台下载。
