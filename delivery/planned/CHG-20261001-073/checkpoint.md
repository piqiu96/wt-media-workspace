# CHG-20261001-073 实施进度（2026-10-01）

- Status: `PLANNED`；独立工作树中有未提交草稿，未完成构建、打包和用户验收。通过 `config/repository-map.yaml` 找到 Cloud/Desktop 原仓，再以 `git worktree list` 找 `codex/device-profile-brand` 分支；不要在 CHG-069 的原 Cloud checkout 上合并草稿。
- Cloud 草稿：`web/public/brand-mark.svg`、`web/public/login-scene.svg`、`web/src/shared/ui/BrandLogo.vue`、`web/src/modules/auth/pages/LoginPage.vue`、三个 `web/index*.html`、`web/src/layout/AppLayout.vue` 品牌区域。
- Desktop 草稿：`src-tauri/icons/brand-mark.svg` 与生成的 PNG/ICNS/ICO、`src-tauri/tauri.conf.json` 的 productName/window title/icon。当前原生版本仍是 `0.1.0`，页面应读取真实版本。
- Workspace 参考图：`docs/product/assets/qifei-brand-reference.png`、`docs/product/assets/qifei-login-reference.png`。
- 验证现状：`npm run build:cloud` 因新 worktree 缺 `web/node_modules` 停在 Vite 依赖解析，尚无页面编译结论；Tauri 测试因 Sidecar 二进制缺失停在 build script，尚无原生打包结论。
- 下一步：按 [plan.md](plan.md) 安装锁定依赖、完成双构建与登录测试；准备 Sidecar 打包并实际查看应用图标、标题、版本和登录页。完整跨仓前置与已知风险见 CHG-072 的 [checkpoint.md](../CHG-20261001-072/checkpoint.md)。
