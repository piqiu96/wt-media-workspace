# 运营资源模块统一 Design System

## 目标

将浏览器窗口、代理管理和社媒账号改造为同一套 WT Media 资源管理体验：现代东方 SaaS、信息密度高、低噪音且可长期复用。用户提供的参考图仅用作视觉方向；本规范以现有 Vue 3 与 TDesign 为实现基础。

## 不变量

- 不修改 API、路由、数据字段、权限、搜索和分页语义。
- 不修改 Cloud Web 与 Desktop 的边界；所有本机操作仍走既有 Tauri/Rust/Local Agent 调用。
- 不改变现有表格列业务含义和已有动作，只调整分组、呈现与样式。
- 不新增服务端统计接口；统计由当前已加载列表计算。

## Token

新增 `web/src/styles/design-token.css` 并在 Cloud 和 Desktop 入口加载。Token 是唯一的颜色、圆角、阴影来源：

- 主色 `#2563EB`，悬浮 `#1D4ED8`；
- 页面底 `#F8FAFC`，卡片白色；
- 正文 `#0F172A`、次正文 `#334155`、辅助文案 `#64748B`；
- 边界 `rgba(15,23,42,0.06)`；圆角 `8px/12px/16px`；
- 卡片阴影 `0 1px 3px rgba(0,0,0,0.04)`；
- 成功、警告、异常 Token 分别映射浅底/深字 Badge，而非实体彩色按钮。

## 共享组件

`shared/ui/resource/` 中的组件只处理表现，不拥有资源状态或发起请求：

- `ResourcePageHeader`：标题、描述和右侧操作插槽；
- `ResourceCard`：统一白色内容容器；
- `ResourceStatGrid`：接收 `{ key, label, value, tone }[]`，可选点击事件，渲染 80–100px 资源统计；
- `ResourceStatusBadge`：接收 `tone` 和 `label`，使用浅色语义状态，不替换全局 `BusinessStatus`。

共享 CSS 提供 `.wt-resource-page`、`.wt-resource-table`、`.wt-resource-filter`、`.wt-secondary-button`、`.wt-danger-button` 与 `.wt-resource-actions`。TDesign 继续负责表格、下拉菜单、Dialog/Drawer 的行为。

## 统一布局与交互

每页使用“Header → 统计（按需）→ Content Card”的顺序。页面背景为 `--wt-bg-page`；内容卡片使用 `--wt-bg-card`、1px 边界、12px 圆角和轻阴影。主按钮高 36px，次按钮为白底细边界，危险动作只在确认/更多菜单中使用红色文本。

表头高度 44px、背景 `--wt-bg-page`、13px 辅助字；表行最低 56px、14px 次正文色，Hover 复用页面浅底。状态均通过 `ResourceStatusBadge` 展示。

## 页面适配

### 浏览器窗口

标题为“浏览器窗口”，描述为“管理 BitBrowser 浏览环境、窗口状态和账号绑定”。统计基于已加载窗口：总数、运行中、已绑定代理、异常/本机缺失。原操作保留：行内显示“详情”、桌面端的“打开”，其余“分配、关闭、绑定代理、编辑、启用/停用”放入 `t-dropdown` 更多菜单。

### 代理管理

标题为“代理管理”，描述为“管理代理资源池、连通性和窗口绑定”。统计基于已加载代理：代理总数、可用（active + check ok）、异常（存在非 ok 检测结果或过期）、已绑定窗口总数。新建代理为唯一主操作；批量导入、批量检测和刷新为次操作。

### 社媒账号

标题为“社媒账号”，描述为“管理账号资产、浏览器环境关联和账号检查状态”。统计基于现有 `stats`：账号总数、正常、异常、未绑定环境。新增账号为唯一主操作；批量检查和刷新为次操作。业务与账号状态使用一致 Badge。

## 验收

静态回归测试断言 Token 已在两个入口加载、三页使用共享组件和资源表格类、浏览器窗口动作仍绑定原处理函数。全量 Vitest、Desktop 前端构建和 `local-control.sh start` 必须通过；人工走查确认三个页面有一致 Header、卡片、统计、表格和状态风格。
