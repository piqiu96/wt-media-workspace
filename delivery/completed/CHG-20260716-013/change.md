# CHG-20260716-013: 架构迁移阶段五 + 阶段六 — Desktop TDesign / Runtime / 构建流水线

## 1. Basic Information

- Level: M
- Status: DONE
- Created: 2026-07-16
- Current repository: `wt-media-cloud`、`wt-media-desktop`、`wt-media-workspace`
- Affected repositories: `wt-media-cloud`、`wt-media-desktop`、`wt-media-workspace`

## 2. Change Goal

完成架构迁移的剩余工作：Desktop AgentStatus 页面改用 TDesign 组件，建立 Runtime 分层，配置工作区联合构建流水线，清理 Desktop 仓库中的 Vue 前端文件。

## 3. Scope

### Add

- Workspace 构建脚本 — 将 dist-desktop 复制到 Desktop `.generated/frontend/`

### Modify

- Desktop AgentStatusPage.vue — 手写 CSS 替换为 TDesign 组件
- Desktop `tauri.conf.json` — `frontendDist` 指向 `.generated/frontend`，`beforeBuildCommand` 指向 Cloud web

### Delete

- `wt-media-desktop/index.html`
- `wt-media-desktop/vite.config.ts`
- `wt-media-desktop/package.json`
- `wt-media-desktop/tsconfig.json`
- `wt-media-desktop/src/` 下 Vue 文件（`App.vue`、`main.ts`、`local-pages/`、`stores/`、`services/`）

### Explicitly Not Doing

- Runtime 接口抽象（`shared/runtime/AppRuntime.ts`）延后
- `apps/desktop/features/local-logs/LocalLogsPage.vue` 迁移延后
- `apps/cloud/pages/users/UsersPage.vue` 迁移延后
- Desktop `src-tauri/` 代码分层（commands/services）延后

## 5. Implementation Tasks

| Task | Goal | Status |
|---|---|---|
| T-01 | AgentStatusPage.vue 手写 CSS → TDesign 组件 | DONE | BusinessStatus 封装 + TDesign descriptions 替代手写 CSS |
| T-02 | 配置 Workspace 构建复制脚本（dist-desktop → desktop/.generated/frontend） | DONE | `scripts/build-desktop.sh` |
| T-03 | 更新 Desktop tauri.conf.json（frontendDist + build commands） | DONE | frontendDist → `../.generated/frontend` |
| T-04 | 删除 Desktop 仓库中 Vue 前端文件 | DONE | index.html/vite.config.ts/tsconfig.json/package.json + src/ 下全部 Vue 文件 |
| T-05 | 验证：npm run build:desktop + 复制 + cargo tauri build 全链路 | DONE | 全链路通过，14 个文件复制到 .generated/frontend |

## 6. Acceptance Matrix

| AC | Requirement | Status |
|---|---|---|
| AC-01 | Desktop AgentStatus 页使用 TDesign 组件渲染 | DONE | BusinessStatus + TDesign descriptions |
| AC-02 | npm run build:desktop 输出 dist-desktop/ | DONE | 构建通过 |
| AC-03 | Workspace 脚本将 dist-desktop 复制到 desktop/.generated/frontend/ | DONE | 14 个文件复制成功 |
| AC-04 | tauri.conf.json frontendDist 指向 .generated/frontend | DONE | 配置已验证 |
| AC-05 | Desktop 仓库无 Vue 前端残留 | DONE | index.html/vite/tsconfig/package.json + src/ 全部清除 |

