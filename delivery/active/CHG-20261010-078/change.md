# CHG-20261010-078：公开官网与桌面安装包下载

- Status: VERIFYING
- Level: M
- Milestone: `delivery/milestones/M-first-production-release.md#公开官网与桌面安装包下载`
- References: `docs/superpowers/specs/2026-10-10-public-home-and-desktop-downloads-design.md`；`docs/superpowers/plans/2026-10-10-public-home-and-desktop-downloads.md`。
- Affected repositories: `wt-media-cloud`、`wt-media-workspace`。
- Current repository: `wt-media-workspace`
- 用户可见结果：公开 `/home` 提供官网及三种桌面安装包链接，不展示登录入口或登录引导；独立登录页与品牌图一致，升级时可更新下载清单。

## 范围与边界

1. Cloud Web 增加公开官网路由与响应式页面，认证守卫只放行 `/home` 和 `/login`；官网不展示登录入口或登录引导，顶部悬浮导航只含产品、下载、定价、联系，单页按 Hero、产品、下载、定价、联系排列，点击或上下滚动可定位并高亮，Desktop 路由不增加官网。
2. Cloud 与 Desktop 共用登录页按参考图改版，不改变登录、角色检查、会话替换和版本显示逻辑。
3. Workspace 脚本从显式 Tag 的 GitHub Release 读取资产 URL，拒绝非公开正式版及缺失、重复、异源资产；更新目标 JSON 文件时保留旧内容直至校验完成。
4. Cloud Web 从同源清单展示 Windows x64、macOS Intel、macOS Apple 芯片下载链接；首次清单对应公开 `v0.1.0`。

## Explicitly Not Doing

- 不修改 Desktop 安装器、自动升级器或 Cloud 业务 API。
- 不代理或镜像安装包文件，不把 GitHub 凭据暴露给浏览器。
- 不创建尚无价格或地址依据的收费、帮助或联系入口。
- 不自动推 Tag、公开 Draft 或部署服务器。

## 有序任务

1. 脚本与验证：三平台链接生成、正式版约束、原子写入、升级命令文档。（该脚本已于 2026-10-11 由单仓小任务退役：清单改为正式版 CI 构建期按 Tag 生成并烙入 Cloud 包，见 `scripts/release/desktop_downloads.py` 与设计文档补记。）
2. Cloud `/home`、清单读取、下载按钮与静态路由验证。
3. 共用登录页和品牌视觉重设计；保留认证行为。
4. 执行焦点测试、Cloud/Desktop 构建、GitHub 资产回读；记录人工视觉与终端网络待验收项。
5. 按用户新设计稿收敛官网视觉和滚动交互；保留真实下载 URL、路由与认证边界。

## 验收

| 项 | 验收方法 | 状态 |
| --- | --- | --- |
| `/home` 公开且业务页仍需登录 | 路由与守卫测试、浏览器访问 | AUTOMATED PASS；部署环境待验收 |
| 官网不出现登录入口或登录引导 | 首页宽窄屏浏览器及页面 DOM 检查 | 本地 PASS；部署环境待验收 |
| 官网悬浮导航可点击、上下滚动及指示当前区域 | 桌面浏览器锚点、上下滚动与活动态检查 | 本地浏览器 PASS；实际鼠标滚轮及部署环境待验收 |
| 官网单页视觉按新设计稿收敛 | 1920/1440/1280/390/320 px 浏览器页面与截图 | 本地 PASS；部署环境待验收 |
| 三平台下载链接与正式版资产一致 | 脚本测试、GitHub Release 回读、页面测试 | AUTOMATED PASS；终端下载待验收 |
| 错误 Release 不覆盖旧清单 | 脚本失败场景测试 | PASS |
| 共享登录流程与视觉可用 | Cloud/Desktop 构建、登录测试、人工宽窄屏走查 | 视觉人工验收 PASS（2026-10-11）；真实账号登录待验收 |

## 提交边界

- Workspace：设计、计划、CHG、脚本和发布文档。
- Cloud：公开首页、登录视觉、品牌资产、初始下载清单及相关测试。
