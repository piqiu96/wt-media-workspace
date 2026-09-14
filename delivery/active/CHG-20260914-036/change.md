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
- 当资源页单行操作总数不超过 6 个时直接展示；超过时才收纳到“更多”菜单，并让操作列按实际内容宽度自适应；
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
- 浏览器窗口、代理管理和社媒账号的单行操作少于等于 6 个时均直接展示，操作列固定右侧且不保留无效大面积空白；
- Cloud Web/桌面前端构建、现有前端回归和本机 M2-B 环境验收通过。

## Checkpoint

- Completed：已新增并在 Cloud/Desktop 入口加载 `design-token.css` 与资源模块样式；`ResourcePageHeader`、`ResourceCard`、`ResourceStatGrid` 和 `ResourceStatusBadge` 均为展示层组件。新增 Token/组件回归测试通过。
- Completed：浏览器窗口、代理管理和社媒账号已接入统一 Header、统计卡、内容卡、表格和状态 Badge。浏览器窗口行操作保留详情、打开和更多；更多菜单仍连接分配、关闭、绑定代理、编辑和启用/停用的原处理函数。
- Completed：根据走查反馈，代理和社媒账号的筛选区从嵌套卡片收束为资源内容卡内的轻分隔区；代理行操作收束为详情、检测、更多；社媒账号移除独立 Cookie 列，保留检查、查看、更多，Cookie、窗口、编辑和启停动作均可从更多菜单访问。
- Completed：顶部栏不再展示英文路由名；根据左侧导航自动生成父级 / 子级面包屑，社媒账号显示为“运营资源 / 社媒账号”。
- Completed：代理管理与社媒账号改为浏览器窗口同款筛选条、横向滚动资源表格、独立分页和操作按钮层级；全局资源表格补齐白色行底、统一边界、垂直居中和悬浮反馈。
- Completed：运营资源三页筛选区统一为每行最多四项、1400px 以下三项、980px 以下两项；浏览器窗口操作列补为右侧固定。三个页面当前直接行操作均为三项，其余动作已在“更多”菜单中，严于“最多五项”的约束。
- Completed verification：Cloud Web 全量 Vitest 18 文件、67 测试通过；Desktop 前端生产构建通过。
- Completed verification：`scripts/local-control.sh start` 已从 `wt-media-cloud` 提交 `f6b7f24` 重建；随后 `scripts/local-control.sh verify` 确认 Cloud、Agent、BitBrowser、Desktop assets、最新 DMG 与管理员登录烟测均 PASS。
- Completed：根据最新走查，浏览器窗口、代理管理和社媒账号的筛选控件均恢复可见字段前缀；操作列统一固定右侧并扩至 420px，可容纳至多六个直接操作，其余动作仍收纳于“更多”。
- Completed verification：最新 DMG 已使用 `operator01` 登录并逐页截图核验。三页字段前缀、三列自动换行、420px 固定右侧操作列及“运营资源 / 子页面”面包屑均符合预期；详见 `evidence/2026-09-14-resource-filter-and-action-visual-verification.md`。
- Completed：根据最新走查，三页行操作改为“小于等于 6 个全部直接展示”的规则，操作列由固定 420px 改为根据按钮内容计算的最小 260px；筛选网格最小列宽提高至 220px，控件改为填满可用列宽。
- Current：正在从最新源码重建并通过 Desktop 逐页截图核验直接操作和宽筛选区。
- Next：记录最新核验；根据用户最终结论决定是否关闭本 CHG。
- Blockers：无。`web/dist-desktop`、Desktop `.generated` 和无关的 Workspace 计划文件为既有或本机构建产物，不纳入提交。
