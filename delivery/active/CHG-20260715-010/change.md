# CHG-20260715-010: M2-R0 UI 重构：TDesign 迁移 + 统一页面模板

## 1. Basic Information

- Level: M
- Status: IN_PROGRESS
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
- Desktop 本地控制台样式同步

### Modify

- Cloud Web `App.vue` 和所有现有页面 → TDesign 组件替换
- Desktop Vue 页面 → TDesign 组件替换
- Vite 配置（按需导入 TDesign 插件）

### Delete

- 手写 CSS 中与 TDesign Token 重复的样式

### Explicitly Not Doing

- 目录改名（`web/` → `frontend/` 延后）
- Desktop devUrl 更改（延后）
- 暗色模式（首版不做）
- 原子化 CSS 框架（首版不引入）
- 第二套 UI 组件库
- ECharts 集成（M9 再做）

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

| Task | Goal | Status |
|---|---|---|
| T-01 | 安装 TDesign Vue Next + Starter + Pinia，配置 Vite 按需导入 | PENDING |
| T-02 | 集成 TDesign Starter 骨架（Layout、导航、路由、登录页） | PENDING |
| T-03 | 创建 BusinessStatus 等基础业务组件 | PENDING |
| T-04 | 改造 Desktop 本地控制台页面 → TDesign | PENDING |
| T-05 | 改造 Cloud Web 登录页和工作台 → TDesign | PENDING |
| T-06 | 改造任务管理区域 → TDesign 表格/状态标签 | PENDING |
| T-07 | 建立六类页面模板文件和示例 | PENDING |
| T-08 | 验证：修复后页面在浏览器和 Vite dev 下均正常 | PENDING |

## 9. Acceptance Matrix

| AC | Requirement | Status |
|---|---|---|
| AC-01 | TDesign 组件在所有页面上正常渲染，无样式冲突 | PENDING |
| AC-02 | 登录/工作台/任务管理三页面全部使用 TDesign 组件 | PENDING |
| AC-03 | BusinessStatus 组件封装完毕，状态颜色统一 | PENDING |
| AC-04 | Desktop 控制台与 Cloud Web 视觉一致 | PENDING |
| AC-05 | 没有残留的多个 UI 库引用 | PENDING |
| AC-06 | 页面能正常构建和热更新 | PENDING |
