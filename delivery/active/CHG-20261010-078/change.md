# CHG-20261010-078：公开官网与桌面安装包下载

- Status: IN_PROGRESS
- Level: M
- Milestone: `delivery/milestones/M-first-production-release.md#公开官网与桌面安装包下载`
- References: `docs/superpowers/specs/2026-10-10-public-home-and-desktop-downloads-design.md`；`docs/superpowers/plans/2026-10-10-public-home-and-desktop-downloads.md`。
- Affected repositories: `wt-media-cloud`、`wt-media-workspace`。
- Current repository: `wt-media-workspace`
- 用户可见结果：公开 `/home` 提供官网、登录入口及三种桌面安装包链接；登录页与品牌图一致，升级时可更新下载清单。

## 范围与边界

1. Cloud Web 增加公开官网路由与响应式页面，认证守卫只放行 `/home` 和 `/login`；Desktop 路由不增加官网。
2. Cloud 与 Desktop 共用登录页按参考图改版，不改变登录、角色检查、会话替换和版本显示逻辑。
3. Workspace 脚本从显式 Tag 的 GitHub Release 读取资产 URL，拒绝非公开正式版及缺失、重复、异源资产；更新目标 JSON 文件时保留旧内容直至校验完成。
4. Cloud Web 从同源清单展示 Windows x64、macOS Intel、macOS Apple 芯片下载链接；首次清单对应公开 `v0.1.0`。

## Explicitly Not Doing

- 不修改 Desktop 安装器、自动升级器或 Cloud 业务 API。
- 不代理或镜像安装包文件，不把 GitHub 凭据暴露给浏览器。
- 不创建尚无价格或地址依据的收费、帮助或联系入口。
- 不自动推 Tag、公开 Draft 或部署服务器。

## 有序任务

1. 脚本与验证：三平台链接生成、正式版约束、原子写入、升级命令文档。
2. Cloud `/home`、清单读取、下载按钮与静态路由验证。
3. 共用登录页和品牌视觉重设计；保留认证行为。
4. 执行焦点测试、Cloud/Desktop 构建、GitHub 资产回读；记录人工视觉与终端网络待验收项。

## 验收

| 项 | 验收方法 | 状态 |
| --- | --- | --- |
| `/home` 公开且业务页仍需登录 | 路由与守卫测试、浏览器访问 | PENDING |
| 三平台下载链接与正式版资产一致 | 脚本测试、GitHub Release 回读、页面测试 | PENDING |
| 错误 Release 不覆盖旧清单 | 脚本失败场景测试 | PENDING |
| 共享登录流程与视觉可用 | Cloud/Desktop 构建、登录测试、人工宽窄屏走查 | PENDING |

## 提交边界

- Workspace：设计、计划、CHG、脚本和发布文档。
- Cloud：公开首页、登录视觉、品牌资产、初始下载清单及相关测试。
