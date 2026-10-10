# Task 1：下载清单更新

- 命令：`python3 -m unittest scripts.release.test_update_desktop_downloads -v`。
- 预期：稳定版三平台映射通过；Draft、RC、缺失、重复及异源 URL 被拒；失败保留旧清单。
- 实际：4 项测试通过，0 失败。测试先因目标模块不存在而失败，随后实现通过。
- 命令：`python3 scripts/release/update_desktop_downloads.py v0.1.0 --output ../wt-media-cloud/web/public/desktop-downloads.json`。
- 预期：从已公开 `v0.1.0` Release 生成首次清单。
- 实际：脚本返回 0；此前 `gh api` 回读 `draft=false`、`prerelease=false`，三平台资产 URL 完整。
- 限制：本机直连 GitHub 资产的 HEAD 请求超时；实际用户网络下载须在部署环境单独验收。
