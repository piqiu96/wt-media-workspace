# RC6 最终发布验收

## 操作与结果

- GitHub Run：[37091241538](https://github.com/piqiu96/wt-media-workspace/actions/runs/37091241538)，`v0.1.0-rc.6`。
- 首轮构建全部成功后，`package` 因 GitHub 账号付款/Spending limit 未启动；用户修复计费后于 2026-10-03 手动执行 `gh run rerun 37091241538 --failed`。
- Rerun 结果：`package` 与 `publish-pre` 成功，整Run 为 `success`。
- GitHub Pre-release：<https://github.com/piqiu96/wt-media-workspace/releases/tag/v0.1.0-rc.6>，`draft=false`、`prerelease=true`。
- 用户在 2026-10-03 反馈 RC6 客户端可以正常打开。该反馈记录为人工打开验证；未要求或宣称真实 Cloud 登录、BitBrowser、对象存储或业务发布链路。

## 固定来源

- Workspace：`3ea6f129424014f63b076745e3fa988b14c8a1e8`
- Cloud：`ed5a3c9a16fe3e22a66a769fc557241b23768c6d`（`v0.1.0-rc.3`）
- Agent：`ac7f0b670b40be50fd2e5dad0f6ba69450370106`（`v0.2.2-rc.2`）
- Desktop：`0b919b0e8ff11d08d733362d6ff48e574d833b69`（`v0.1.0-rc.3`）
- 目标 Cloud origin：`https://wt.longyanyue.cn`

## 发布附件与 SHA-256

发布 Job 在 GitHub 侧重新下载附件并执行 `sha256sum --check`，5 项全部 OK。人工下载同一 Pre-release 后复核同样 5 项 OK：

- `WT-Media_v0.1.0-rc.6_macos-arm64.zip` — 32,052,763 bytes，SHA-256 `28537f343be95ebc5c27e9a0e85d7d03957bc97907c3585281e3b4dcaec99580`
- `WT-Media_v0.1.0-rc.6_macos-x64.zip` — 34,011,660 bytes，SHA-256 `6385fdb93f17659c4519fda4e6c95cdf27e9e2106eaa149a92a16c8aeaaccfb3`
- `WT-Media_v0.1.0-rc.6_windows-x64-setup.exe` — 14,983,656 bytes，SHA-256 `ffcbea6186b00a728c15afa377e7aaf95b7c877f25a72c6d83847838a4717602`
- `build-info.json` — SHA-256 `bfffd1489e8de42901e31af8375f6ba1fcabe19f63937c15577b92a11ac43579`
- `v0.1.0-rc.6.yaml` — SHA-256 `3e07648fe5401d83fc9621cf9036682c3bb1b34d2d9c95873997311516a4bb50`

## 受控 Actions Artifact

- Cloud：`cloud-linux-amd64`，Artifact ID `11261989758`，Artifact ZIP 摘要 `a4cb59a4aae6dbed9922c69a4e3410c685f34fbdca610c780f1ae210027543f0`；其中 Cloud Linux 包 `wt-media-cloud_v0.1.0-rc.6_linux-amd64.tar.gz` 摘要 `01efbe0b0ba4bc2c2afbb3ae8d039cc3c90975489711e41eb33570bbf0cfb6d0`。
- Desktop Web：`desktop-web_v0.1.0-rc.6.tar.gz` 摘要 `5fef95d50d89736a217c478fe63556cb2f7bd567fc25e883aafe428d502d3391`。
- Agent 三平台摘要见 `build-info.json`，Actions 下载时另由平台 Artifact ZIP 摘要校验。
- 发布汇总 Artifact：`product-release-assets`，Artifact ID `11263404007`，ZIP 摘要 `aff46baeab88f62418dd4c38fb1ec69a8a0671a1b9e428ce420b2c03aa074b70`。

## 边界

- 已验证：固定 Tag/Commit、GitHub 原生平台构建、Agent 冻结进程健康 smoke、Desktop 包结构和版本/摘要、Pre-release 公开附件、下载后 SHA-256。
- 未验证且不得宣称通过：宝塔部署、生产 MySQL 迁移、生产对象存储、真实 Cloud 登录、BitBrowser 账号操作、业务发布和正式稳定版上线。
