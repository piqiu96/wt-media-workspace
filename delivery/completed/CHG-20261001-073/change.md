# CHG-20261001-073：起飞品牌、登录页与桌面应用图标

- Status: CLOSED
- Level: `M`
- 来源：2026-10-01 用户提供的 Logo 和登录页参考图，并明确要求桌面端应用图标一致。
- 业务锚点：[M2-G](../../milestones/M2-account-runtime.md)。参考图：[品牌](../../../docs/product/assets/qifei-brand-reference.png)、[登录页](../../../docs/product/assets/qifei-login-reference.png)。
- 激活条件：随唯一活跃 [CHG-20261001-072](../../active/CHG-20261001-072/change.md) 的**耦合伴记**一并执行——共享同一 worktree，提交/证据按 CHG 区分，072 关闭时一并验收归档。本记录自身仍为 PLANNED（`delivery/active/` 同一时间只允许一个活跃 CHG）。
- 代码位置：与 CHG-20261001-072 共用两个独立工作树及分支 `codex/device-profile-brand`，见本 CHG 的[实施进度](checkpoint.md)。后续提交与验收证据需能按 CHG 区分。

## 1. 独立结果

Cloud Web 与 Desktop 的登录页、顶部品牌和网页图标统一为“起飞 · 内容运营平台”；Desktop 安装包、窗口与系统应用图标使用同一纸飞机 Logo。登录页保留真实登录、替换旧会话和 Desktop 权限限制，版本号显示实际运行版本。

## 2. 视觉与交互范围

- 以参考图的蓝白色纸飞机、轻蓝背景、左侧产品价值说明、右侧白色登录卡为视觉方向；图中的营销文案与 `v1.0.0` 只是参考，不覆盖真实业务行为与版本号。
- Logo 在 `web/public/brand-mark.svg` 作为 Web 视觉源；Desktop `src-tauri/icons/brand-mark.svg` 使用同源图形，并生成平台要求的 PNG、ICNS、ICO 图标。更改 Logo 后必须一起重新生成原生图标。
- 登录页继续支持用户名、密码、已有会话替换确认、错误反馈；登录成功进入原业务路由。Cloud Web 与 Desktop 共享页面，但 Desktop 仍仅允许普通运营使用本机执行能力。
- 页面浏览器标题、favicon、顶部品牌、Tauri productName/window title 一致；版本号从实际 Web 包或 Tauri 运行版本读取，不手写参考图版本。
- 右上角个人入口及独立个人信息页属 CHG-20261001-072；本 CHG 只处理它们与品牌风格的一致性。

## 3. 验收与边界

- Cloud Web 与 Desktop 双构建通过，登录成功、失败、会话替换和退出回登录页可用；小屏布局没有横向溢出。
- SVG、favicon、窗口图标、Dock/任务栏图标在真实打包应用中可见，形状和颜色一致；macOS、Windows、Linux 资源由同一源生成。
- 显示真实当前版本；不因为参考图把 `0.1.0` 改写为 `1.0.0`。
- 走查后再由用户签收；仅代码存在、构建通过或生成了图标都不算本 CHG 完成。

## 4. 当前实施状态

2026-10-01 在独立工作树中实现页面、SVG、favicon 和 Tauri 图标/名称改动，随 CHG-20261001-072 阶段 0 一并走查验收（cloud `a88604c`、desktop `0519fa8`），2026-10-02 用户确认验收，随 072 归档。走查结论与关闭读数见 [CHG-072 关闭证据](../../completed/CHG-20261001-072/evidence/phase0-walkthrough-and-closing.md)。实施顺序见 [plan.md](plan.md)。
