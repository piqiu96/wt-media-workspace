# CHG-20261010-078 Checkpoint

- 已完成：Task 1 脚本与初始清单；Task 2 Cloud `/home` 与三平台按钮；Task 3 共享登录页及品牌视觉；Task 5 新设计稿单页收敛及宽窄屏截图、滚动交互本地验证。`v0.1.1` 发布、烙入校验、部署与线上回读闭环（`evidence/v011-release-stamping-20261011.md`）。`v0.1.2`（登录错误提示拆分补丁）发布、部署、线上探针闭环（`evidence/v012-release-and-deploy-20261011.md`）。
- 当前工作：v0.1.2 已在生产服务：`desktop-downloads.json` 翻为 v0.1.2，`/home`、`/login` 200，未认证业务 API 401+11001，登录错误码 10005/10006/11004 线上生效。两条 release-matrix 记录（v0.1.1、v0.1.2）已回填。
- 剩余验收（依赖用户人工）：真实账号登录走查（重点三种登录错误提示）；官网视觉与悬浮导航滚动走查；目标用户网络三平台下载点击。
- 阻塞：无代码阻塞。
- 最近验证：release.yml run 38138153403 全绿（首跑 Windows agent CA-bundle CRLF 哈希不匹配，agent `8e27531` 修复后组件 tag 重钉重跑）；六资产 SHA256SUMS 通过；部署包 SHA-256 与 build-info 记录一致；部署后探针见 v0.1.2 证据文件。
