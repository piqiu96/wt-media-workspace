# CHG-20261010-078 Checkpoint

- 已完成：Task 1 脚本与初始清单；Task 2 Cloud `/home` 与三平台按钮；Task 3 共享登录页及品牌视觉；Task 5 新设计稿单页收敛及宽窄屏截图、滚动交互本地验证；2026-10-11 发布产品 Tag `v0.1.1` 并已完成 CI 构建、六资产校验、包内清单烙入逐字节验证与 Release 公开（证据：`evidence/v011-release-stamping-20261011.md`）。
- 当前工作：等待把 `wt-media-cloud_v0.1.1_linux-amd64.tar.gz` 部署到宝塔服务器（包已置于用户 `~/Downloads/`）。状态仍为 VERIFYING；部署后的 `/home`、真实账号登录与目标用户网络三平台下载验收待执行。
- 下一步：用户按 `wt-media-cloud/deploy/DEPLOYMENT.md` §4-§7 执行服务器部署；部署后回读 `https://wt.longyanyue.cn/desktop-downloads.json` 应为 v0.1.1，再逐个平台点击下载；收到结果后关闭 CHG。
- 阻塞：无代码阻塞。在线部署和终端网络验收依赖目标环境人工执行。
- 最近验证：v0.1.1 run 38073520974 全绿；`submit_tag.py v0.1.1 --verify` 通过；包内 `web/desktop-downloads.json` 与黄金清单 SHA-256 一致（`7b23dba2…`）；Release 已公开（`isDraft=false`），资产匿名 HEAD 302。此前的登录页与官网本地验证记录仍有效。
