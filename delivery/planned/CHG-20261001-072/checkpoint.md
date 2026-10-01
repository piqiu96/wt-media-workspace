# CHG-072 / CHG-073 实施进度（2026-10-01）

本文件记录**进行中的实现草稿**，供后续模型从现有工作树继续。它不是验收证据，不改变两份 CHG 的 `PLANNED` 状态。产品裁定以 [CHG-072](change.md)、[CHG-073](../CHG-20261001-073/change.md)、[M2-F/G](../../milestones/M2-account-runtime.md) 为准。

## 1. 工作区与先读顺序

1. 先读 Workspace `AGENT-INDEX.md`、`.ai/CURRENT_CONTEXT.md`、`delivery/LEDGER.md`；当前原仓已有 CHG-069 的未提交改动。不要把两个独立工作树直接覆盖回原 checkout。
2. 从 `config/repository-map.yaml` 找到 Cloud 和 Desktop 原仓，再用各仓 `git worktree list` 找分支 `codex/device-profile-brand` 的 worktree；Cloud 起点 `6928291`，Desktop 起点 `909d582`。两树截至本文件编写时均有**未提交**改动。先各自运行 `git status --short` 和 `git diff --stat`，不把本机物理路径写成长期事实。
3. 读目标仓 `CLAUDE.md` 与 `AGENT-INDEX.md`，再看 Cloud 的 `contracts/cloud-agent-api/v1/runtime-binding.openapi.yaml`、`contracts/cloud-api/v1/identity.openapi.yaml`，最后看 Desktop `contracts.lock.json`。Provider 版本与消费者版本均暂改为 `2026.10.01.1`；尚未完成契约生成/兼容性全套检查。
4. Workspace 原仓已有其他用户或 CHG 的修改：`AGENT-INDEX.md`、`AGENTS.md`、`CLAUDE.md`、`delivery/MASTER_IMPLEMENTATION_PLAN.md`、M5 文档、`docs/standards/`、`reference/` 等；不要清理或重写。

## 2. 已修改但尚未交付的实现

| 范围 | 现有草稿入口 |
| --- | --- |
| Cloud 用户资料 | `migrations/20261001_044_user_avatar.sql`；`internal/modules/identity/{model,service,repository,handler,router}`；`contracts/cloud-api/v1/identity.openapi.yaml`。已有 `nickname` 字段沿用旧迁移，新加 `avatar_id`；`PATCH /api/v1/auth/me` 更新本人昵称与系统头像，空昵称/头像读取时回退到用户名/默认头像。登出 Handler 已改为识别 Desktop 的 Authorization token。 |
| Cloud 设备事实与门禁 | `migrations/20261001_045_user_device_binding.sql`；`internal/modules/runtimebinding/{dto,model,service,repository,handler,router}`；`contracts/cloud-agent-api/v1/runtime-binding.openapi.yaml`。`POST /api/v1/local-agent/nodes` 增加设备公钥、签名、名称和 `bind_device`；`GET/DELETE /api/v1/local-agent/device-binding` 供展示/解绑；节点信任查询加设备匹配。`internal/modules/cloudagent/service/compatibility.go` 版本同步。 |
| Desktop 本机身份证明 | `src-tauri/src/device_identity.rs` 在应用数据目录生成/读取 Ed25519 PKCS8 密钥，仅向 WebView 返回设备 ID/名称；`src-tauri/src/commands/bind.rs` 用一次性票据签名并注册节点；`src-tauri/src/dto/bind.rs` 增加显式绑定标志；`main.rs` 注册命令，`Cargo.toml` 增加依赖。 |
| 共用 Vue：个人信息与恢复 | `web/src/modules/auth/pages/PersonalInfoPage.vue`、`web/src/shared/ui/{SystemAvatar.vue,systemAvatars.js}`、`web/src/shared/api/deviceBinding.js`、Cloud/Desktop 路由、`web/src/layout/AppLayout.vue`、`web/src/shared/api/session.js`。Desktop 自动续接在 `web/src/apps/desktop/features/local-agent/{init.js,service.js}`；下载入口在 `web/src/shared/api/materials.js` 做续接前置；Agent 状态页和下载错误文案改为区分设备绑定与会话连接。 |
| 起飞品牌 | `web/public/brand-mark.svg`、`web/public/login-scene.svg`、`web/src/shared/ui/BrandLogo.vue`、`web/src/modules/auth/pages/LoginPage.vue`、三个 `web/index*.html`。Desktop `src-tauri/icons/brand-mark.svg` 同源，已生成 PNG/ICNS/ICO，`tauri.conf.json` 改应用名和标题，版本仍为真实 `0.1.0`。 |

Workspace 中已添加第三章 PRD 个人信息/设备规则、ADR-0018、两张参考图和本次 M2 扩展。旧 ADR-0003 增加 ADR-0018 的细化引用。

## 3. 已运行验证与环境前置

- `go test ./internal/modules/identity/... ./internal/modules/runtimebinding/... ./internal/modules/cloudagent/...` 在 Cloud 独立工作树 **通过**（2026-10-01）。这只证明现有单元/包测试，并未覆盖所有新场景。
- `npm run build:cloud` 在 Cloud 独立工作树 **尚未完成**：该新 worktree 缺少 `web/node_modules`，找不到 `@vitejs/plugin-vue`、`vite` 等依赖。先在该树 `web` 下按锁文件安装依赖（通常 `npm ci`），再做 Cloud/Desktop 双构建与定向测试。此失败不是 Vue 代码的编译结论。
- `cargo test device_identity --manifest-path src-tauri/Cargo.toml` 在 Desktop 独立工作树 **尚未完成**：Tauri build script 缺少 `src-tauri/binaries/wt-media-agent-aarch64-apple-darwin`。按 Desktop 仓原有 Sidecar 构建/放置流程准备二进制后重试；目前不能声称 Rust 编译或测试通过。
- 尚未运行迁移到真实 MySQL、OpenAPI lint/生成校验、真实 Agent/BitBrowser、打包 Desktop 或人工走查。

## 4. 下一位执行者的具体顺序

1. 检查两个工作树的未提交 diff，确认没有其他人新改动；检查 CHG-069 当前状态，遵守单活跃 CHG 规则。保留本草稿，不提前把 072/073 写为 `DONE`。
2. 在 Cloud 工作树安装 Web 锁定依赖，运行 `npm run build:cloud`、`npm run build:desktop` 与相关 Vitest；修复真实的 Vue/样式/导入错误。检查实际登录页、个人信息页和小屏效果。
3. 在 Desktop 工作树按仓库规则准备 Sidecar，运行 `cargo fmt --check`、`cargo test`/`cargo check` 与 Tauri 打包；确认图标资源完整、同源 SVG 一致，实际 Dock/任务栏图标和版本显示正确。
4. 补强 Cloud 设备关键场景测试：同一密钥跨会话续接、另一密钥拒绝、解绑后换绑、旧节点失效、伪造签名、BitBrowser 主账号不符、依赖不可用不解绑；校验所有本机执行入口的门禁，不只下载入口。确认解绑事务不触碰本地文件、Cloud 历史或 BitBrowser 主账号绑定。
5. 校验 Cloud 两个迁移与契约兼容性；对真实 MySQL/打包 Desktop/Agent/BitBrowser 走查“首次绑定 → 重启/重新登录自动恢复 → 换设备被拒 → 显式解绑 → 新设备绑定 → 旧设备失效”。必要时更新 CHG 实施证据，再请用户验收。

## 5. 已知需要审查的设计点

- Desktop 本机密钥目前保存在 Tauri 应用数据目录并设 Unix `0600`，应核对 Windows 文件权限及密钥创建并发/崩溃后的恢复，不把原始密钥暴露到日志、Vue 或 Agent。
- Cloud 第一次 `bind_device=true` 可能先完成 Cloud 绑定，后续 Agent 写入/运行时上报再失败；页面需要显示“设备已绑定但环境不可用”并允许同机重试，不能误报绑定失败后引导再次换绑。
- `ensureTrustedLocalAgent` 在登录/启动时异步触发，下载前会等待；其他所有本机执行入口需盘点，必要时统一前置恢复，防止只修下载路径。
- 新设备可登录并进入个人信息页，不能仅因没有本机节点就阻止查看和手动解绑；Cloud Web 显示的本机环境状态不能冒充当前电脑的真实 Agent 状态。
- PRD 与 M2 旧文中的“会话替换需重新绑定”表述已被 M2 §6 与 ADR-0018 细化；实现与测试不得继续把节点失效等同于设备解绑。
