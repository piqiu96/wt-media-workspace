# CHG-20260914-036：M2-B 运营资源 Design System 与三页统一改造

> 日期：2026-09-14
> 状态：ACTIVE
> 所属 Milestone：M2-B 浏览器窗口与媒体账号真实闭环
> 关联闭环：`delivery/milestones/M2-account-runtime.md#运营资源统一视觉闭环`
> 当前仓库：`wt-media-workspace`
> 预计影响仓库：`wt-media-cloud`、`wt-media-workspace`

## 用户可见目标

浏览器窗口、代理管理和社媒账号展示为同一 WT Media 资源管理模块：现代东方、克制、高信息密度，且现有业务动作和 Desktop/Cloud 边界保持不变。

## 范围

### 包含

- 建立并全局引入 WT Media Design Token；
- 复用资源页 Header、内容卡片和状态 Badge；
- 统一三页的页面背景、统计卡、筛选区、表格、按钮层级、状态和操作列视觉；
- 将浏览器窗口的“绑定代理、关闭、编辑、启用/停用”等非主动作收纳到“更多”菜单；
- 保持已确认的“运营资源”折叠菜单视觉。

### 明确不做

- 不修改 API、数据结构、权限、路由、查询条件或真实 BitBrowser/Agent 执行流程；
- 不增加后端统计接口；统计仅从页面已加载的列表派生；
- 不处理 Cookie、验证码、登录、Windows 打包或非运营资源页面；
- 不引入新 UI 框架或花哨动画。

## 任务

1. Token、共享资源页组件与回归测试。
2. 浏览器窗口页统一 Header、统计、内容卡片、表格和低噪音操作菜单。
3. 代理管理与社媒账号页接入同一规范与现有业务行为回归。
4. Desktop 构建、全量 Web 测试和本机端到端验收。

## 验收标准

- 三页同时使用 `src/styles/design-token.css` 的 `--wt-*` Token；
- 页面 Header、内容卡片、按钮、表头 44px、表行 56px、Hover 和状态 Badge 一致；
- 代理/账号统计从既有数据派生并且筛选、创建、检查、编辑等既有行为不变；
- 浏览器窗口操作列只有详情、打开和更多；所有原动作仍能从菜单访问；
- Cloud Web/桌面前端构建、现有前端回归和本机 M2-B 环境验收通过。

## Checkpoint

- Completed：已新增并在 Cloud/Desktop 入口加载 `design-token.css` 与资源模块样式；`ResourcePageHeader`、`ResourceCard`、`ResourceStatGrid` 和 `ResourceStatusBadge` 均为展示层组件。新增 Token/组件回归测试通过。
- Completed：浏览器窗口、代理管理和社媒账号已接入统一 Header、统计卡、内容卡、表格和状态 Badge。浏览器窗口行操作保留详情、打开和更多；更多菜单仍连接分配、关闭、绑定代理、编辑和启用/停用的原处理函数。
- Completed：根据走查反馈，代理和社媒账号的筛选区从嵌套卡片收束为资源内容卡内的轻分隔区；代理行操作收束为详情、检测、更多；社媒账号移除独立 Cookie 列，保留检查、查看、更多，Cookie、窗口、编辑和启停动作均可从更多菜单访问。
- Completed：顶部栏不再展示英文路由名；根据左侧导航自动生成父级 / 子级面包屑，社媒账号显示为“运营资源 / 社媒账号”。
- Completed：代理管理与社媒账号改为浏览器窗口同款筛选条、横向滚动资源表格、独立分页和操作按钮层级；全局资源表格补齐白色行底、统一边界、垂直居中和悬浮反馈。
- Completed verification：Cloud Web 全量 Vitest 18 文件、65 测试通过；Desktop 前端生产构建通过。
- Current：待提交本轮源码并重建最新本地 DMG 供用户走查。
- Next：执行本机 M2-B 环境验收；在用户确认视觉结果前保持 ACTIVE。
- Blockers：无。`web/dist-desktop`、Desktop `.generated` 和无关的 Workspace 计划文件为既有或本机构建产物，不纳入提交。
