# CHG-20260715-010: M2-R0 UI 重构：TDesign 迁移 + 统一页面模板

## 1. Basic Information

- Level: M
- Status: DONE
- Created: 2026-07-15
- Current repository: `wt-media-cloud`
- Affected repositories:
  - `wt-media-cloud`
  - `wt-media-desktop`

## 2. Change Goal

在 M2 业务模块开发之前，完成 Cloud Web 前端 UI 重构。基于决策 0007（视觉工程基线），将手写 CSS 替换为 TDesign Vue Next 组件库，建立六类统一页面模板，统一状态颜色和交互规范，为后续所有业务页面提供一致视觉基础。

## 3. Baseline References

- Decision 0007: Visual and Frontend Engineering Baseline
- Master route: `wt-media-workspace/delivery/MASTER_IMPLEMENTATION_PLAN.md`
- Visual proposal: `docs/视觉/模块化自媒体运营平台_Web与Desktop前端复用及视觉体系方案.md`

## 4. Current Facts

- Cloud Web 使用手写 CSS，无组件库，视觉不一致
- Desktop Vue 页面（5174）同样使用手写 CSS
- M1 三端流程已打通，M2 业务模块即将开始
- TDesign Vue Next 已选为唯一 UI 组件库
- TDesign Starter 将作为后台骨架

## 5. Scope

### Add

- TDesign Vue Next 依赖
- TDesign Starter 骨架（Layout、导航、路由、登录页）
- Pinia 状态管理
- `<BusinessStatus>` 统一状态组件
- 六类页面模板的初始实现
- `apps/modules/shared` 三层目录骨架
- Desktop Vue 入口和独有页面 → 迁入 `apps/desktop/`
- Cloud/Desktop 独立路由和菜单

### Modify

- Cloud Web `App.vue` 和所有现有页面 → TDesign 组件替换
- Vite 配置（按需导入 TDesign 插件）

### Delete

- 手写 CSS 中与 TDesign Token 重复的样式
- Desktop 仓库中的 Vue 前端工程文件（迁移后清理）

### Explicitly Not Doing

- 目录改名（`web/` → `frontend/` 延后）
- Desktop devUrl 更改（延后）
- 暗色模式（首版不做）
- 原子化 CSS 框架（首版不引入）
- 第二套 UI 组件库
- ECharts 集成（M9 再做）
- OpenAPI 代码生成（阶段六再做）

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | TDesign Vue Next 为唯一 UI 组件库，禁止引入其他库。 | CONFIRMED |
| D-02 | TDesign Starter 作为初始骨架，去掉演示内容后作为项目源码维护。 | CONFIRMED |
| D-03 | 六类页面模板（资源列表、任务工作台、批量向导、详情抽屉、设置、看板）为全系统标准。 | CONFIRMED |
| D-04 | 状态颜色统一映射，封装 BusinessStatus 组件。 | CONFIRMED |
| D-05 | 首批改造三个页面：Desktop 状态中心、内容发现列表、合成任务台。 | CONFIRMED |

## 7. Pending Questions

None.

## 8. Implementation Tasks

| Task | Goal | Status | Notes |
|---|---|---|---|
| T-01 | 安装 TDesign Vue Next + Starter + Pinia，配置 Vite 按需导入 | DONE | commit `e381161` |
| T-02 | 集成 TDesign Starter 骨架（Layout、导航、路由、登录页） | DONE | commit `5634f9c`；追加修复 `83e5e66` |
| T-03 | 改造 Cloud Web 登录页、工作台、任务台、账号管理 → TDesign | DONE | commits `e381161`、`5634f9c`；6 页面全部使用 TDesign |
| T-04 | 建立 `apps/modules/shared/generated` 目录骨架 | DONE | 阶段一完成 |
| T-05 | 迁移 Desktop 入口和独有页面至 `apps/desktop/` | DONE | 阶段二完成；Desktop main.ts + App.vue + AgentStatusPage + store/service |
| T-06 | 拆分 Cloud/Desktop 独立路由和菜单 | DONE | 阶段三完成；Cloud: `apps/cloud/router.ts` (不含 /agent /logs)；Desktop: `apps/desktop/router.ts` (不含 /users) |
| T-07 | 创建 BusinessStatus 组件（状态颜色统一封装） | DONE | `shared/ui/BusinessStatus.vue` + `shared/styles/tokens.css` |
| T-08 | 建立六类页面模板文件和示例 | DONE | 6 个模板: ResourceList/TaskWorkbench/BatchWizard/DetailDrawer/Settings/Dashboard |
| T-09 | 验证：Cloud 和 Desktop 构建均正常，页面无样式冲突 | DONE | 双构建通过，路由边界正确 |

## 9. Acceptance Matrix

| AC | Requirement | Status | Notes |
|---|---|---|---|
| AC-01 | TDesign 组件在所有页面上正常渲染，无样式冲突 | DONE | Cloud 6 页面已确认；Desktop 构建通过 |
| AC-02 | 登录/工作台/任务管理/账号管理/用户管理全部使用 TDesign 组件 | DONE | Login 15处、Dashboard 16处、Tasks 9处、Accounts 28处、Users 23处引用 |
| AC-03 | BusinessStatus 组件封装完毕，状态颜色统一 | DONE | `shared/ui/BusinessStatus.vue` 覆盖 14 种状态映射 |
| AC-04 | Desktop 使用 TDesign | DONE | `apps/desktop/main.ts` 加载 TDesign；本地页面通过路由内嵌 |
| AC-05 | 没有残留的多个 UI 库引用 | DONE | 仅有 TDesign |
| AC-06 | Cloud 构建（vite build）正常 | DONE | `npm run build:cloud` 通过，不含 Desktop 页面 |
| AC-07 | Desktop 构建（vite build）正常 | DONE | `npm run build:desktop` 通过，不含 Cloud 管理页面 |
| AC-08 | `apps/modules/shared` 目录结构和依赖方向正确 | DONE | 三层骨架建立完毕 |
| AC-09 | Cloud/Desktop 独立路由菜单 | DONE | Cloud 无 /agent /logs；Desktop 无 /users |
| AC-10 | 6类统一页面模板建立 | DONE | ResourceList/TaskWorkbench/BatchWizard/DetailDrawer/Settings/Dashboard |
