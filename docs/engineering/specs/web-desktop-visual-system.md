# 模块化自媒体运营平台：Web / Desktop 前端复用与视觉体系方案

## 1. 文档目的

本文基于当前项目架构与前端规划，统一回答以下问题：

1. Desktop 与 Cloud/Web 都需要展示各功能模块，是否会产生前端代码重复？
2. 如果前端源码统一放在 `wt-media-cloud/frontend`，修改后如何同步到 Desktop？
3. 当前功能模板视觉效果较差，应该采用什么成熟、美观、易用的方案？
4. 同时使用组件库、后台模板、图表库等工具，会不会产生样式冲突和维护风险？

---

# 2. 总体结论

当前项目不应该维护两套完整前端。

推荐方案是：

> **一套 Vue 3 业务前端，两种运行模式；Web 负责浏览器运行，Desktop 通过 Tauri 承载同一套前端，并额外提供本地能力。**

整体预计可以复用约 **80%～90%** 的页面、组件和业务逻辑。

Desktop 不重新开发一套业务页面，只额外负责：

- 本地环境检测
- Agent 启停与状态观测
- 本地文件和目录访问
- 本地缓存与日志
- 浏览器窗口控制
- 依赖安装与卸载
- 客户端升级
- Tauri Bridge
- Desktop 安装包构建

推荐前端视觉技术栈：

| 类型 | 选择 |
|---|---|
| 前端框架 | Vue 3 |
| 构建工具 | Vite |
| Desktop 容器 | Tauri 2 |
| UI 组件库 | TDesign Vue Next |
| 初始后台骨架 | TDesign Starter Vue Next |
| 图标体系 | TDesign Icons |
| 图表 | Apache ECharts |
| 状态管理 | Pinia |
| 样式方案 | CSS / SCSS + TDesign Design Token |
| 第二套 UI 组件库 | 禁止引入 |
| 原子化 CSS 框架 | 首版不引入 |

---

# 3. Web 与 Desktop 是否会产生代码重复

## 3.1 推荐运行架构

```text
                    共享 Vue 3 前端
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
   Web 运行模式                          Desktop 运行模式
        │                                     │
  浏览器 + Cloud API               Tauri WebView + Cloud API
                                           │
                                  Tauri Bridge / Local Agent
                                           │
                               文件、日志、浏览器、环境管理
```

Web 和 Desktop 使用同一套：

- 页面
- 路由
- 状态管理
- 权限逻辑
- API 类型
- 通用组件
- 业务组件
- 视觉规范

只有 Desktop 本地能力需要差异化实现。

---

## 3.2 各模块复用情况

| 功能模块 | Web | Desktop | 复用方式 |
|---|---:|---:|---|
| 内容发现 | 展示、操作 | 展示、操作 | 完全复用 |
| 素材库 | 展示、操作 | 展示、操作 | 完全复用 |
| 我的素材 | 展示、操作 | 展示、操作 | 完全复用 |
| 合成策略 | 展示、配置 | 展示、配置 | 完全复用 |
| 合成任务台 | 展示、管理 | 展示、管理、本地执行 | 页面复用，执行能力不同 |
| 成片管理 | 云端数据 | 云端数据、本地文件 | 页面复用，能力不同 |
| 发布管理 | 查看、配置 | 查看、配置、执行 | 页面复用，Desktop 增加执行能力 |
| 互动管理 | 查看、配置 | 查看、配置、执行 | 页面复用，Desktop 增加执行能力 |
| 数据统计 | 展示 | 展示 | 完全复用 |
| 用户、账号、权限 | 展示、配置 | 展示、配置 | 完全复用 |
| 环境检测 | 不提供或只读 | 完整提供 | Desktop 独有 |
| Agent 启停 | 不提供 | 完整提供 | Desktop 独有 |
| 依赖安装与卸载 | 不提供 | 完整提供 | Desktop 独有 |
| 本地路径、缓存、日志 | 不提供 | 完整提供 | Desktop 独有 |
| 客户端更新 | 不提供 | 完整提供 | Desktop 独有 |

---

## 3.3 前端内部推荐结构

```text
frontend/
├── apps/
│   └── console/                 # 唯一业务前端
│
├── packages/
│   ├── ui/                      # 通用 UI、主题、布局
│   ├── business-components/     # 素材卡片、任务状态、账号选择器
│   ├── domain/                  # material、publication 等领域模型
│   ├── api/                     # Cloud API 请求与类型
│   ├── runtime/                 # Web / Desktop 运行环境适配
│   └── permissions/             # 三角色权限
│
└── entries/
    ├── web.ts
    └── desktop.ts
```

构建方式：

```text
build:web       → 部署到 Cloud/Web
build:desktop   → 生成静态资源，交给 Tauri 打包
```

---

# 4. 当前多仓库职责划分

当前项目仓库：

- `wt-media-workspace`
- `wt-media-cloud`
- `wt-media-agent`
- `wt-media-desktop`

推荐职责如下。

## 4.1 `wt-media-cloud`

```text
wt-media-cloud/
├── backend/
└── frontend/
    ├── apps/console
    ├── packages/ui
    ├── packages/api
    ├── packages/domain
    ├── packages/runtime
    └── packages/business-components
```

负责：

- 所有业务页面
- 所有公共组件
- 路由
- 状态管理
- 权限控制
- Cloud API 调用
- Web 构建
- Desktop 前端静态资源构建

---

## 4.2 `wt-media-desktop`

```text
wt-media-desktop/
├── src-tauri/
├── scripts/
└── desktop-config/
```

负责：

- Tauri 壳
- 系统托盘
- Tauri Bridge
- 本地文件访问
- 客户端更新
- 本地进程管理
- Desktop 打包
- Windows / macOS 安装包
- 与本地 Agent 通信

**不再维护第二套 Vue 业务页面。**

---

## 4.3 `wt-media-agent`

负责：

- Python 本地执行服务
- 浏览器控制
- 合成执行
- 发布执行
- 互动执行
- 依赖环境能力
- 本地任务日志
- 本地运行状态

---

## 4.4 `wt-media-workspace`

负责：

- 多仓库初始化
- 统一启动脚本
- 联合开发环境
- 各仓库版本锁定
- 联合构建
- 发布流程
- Skills
- 架构与需求文档

---

# 5. 前端源码放在 `wt-media-cloud/frontend` 后如何同步

## 5.1 核心原则

不复制源码，因此不需要日常“同步代码”。

错误方式：

```text
Cloud frontend
    ↓ 手工复制
Desktop frontend
```

正确方式：

```text
唯一前端源码
    ├── 构建为 Web
    └── 构建为 Desktop 静态资源
```

`wt-media-cloud/frontend` 是唯一前端源码来源。

---

## 5.2 开发环境

开发时启动 Vite：

```text
wt-media-cloud/frontend
        ↓
http://localhost:5173
        ↓
浏览器直接访问
        ↓
Tauri Desktop 通过 devUrl 加载
```

修改 Vue 页面后：

- 浏览器立即热更新
- Desktop 窗口立即热更新
- 不需要复制源码
- 不需要重复提交
- 不需要生成两套页面

示意配置：

```json
{
  "build": {
    "beforeDevCommand": "pnpm run frontend:dev",
    "devUrl": "http://localhost:5173",
    "beforeBuildCommand": "pnpm run frontend:build:desktop",
    "frontendDist": "../../wt-media-cloud/frontend/dist-desktop"
  }
}
```

具体相对路径按照最终工作区目录调整。

---

## 5.3 正式构建

### Web 构建

```text
1. 进入 wt-media-cloud/frontend
2. 执行 pnpm install --frozen-lockfile
3. 执行 pnpm build:web
4. 生成 dist-web
5. 部署到 Cloud/Web
```

### Desktop 构建

```text
1. 拉取指定版本的 wt-media-cloud
2. 进入 wt-media-cloud/frontend
3. 执行 pnpm install --frozen-lockfile
4. 执行 pnpm build:desktop
5. 生成 dist-desktop
6. Tauri 打包 dist-desktop
7. 生成 exe / msi / dmg
```

推荐脚本：

```json
{
  "scripts": {
    "dev:web": "vite --mode web",
    "dev:desktop": "vite --mode desktop",
    "build:web": "vite build --mode web --outDir dist-web",
    "build:desktop": "vite build --mode desktop --outDir dist-desktop"
  }
}
```

环境变量：

```text
VITE_RUNTIME=web
VITE_RUNTIME=desktop
```

---

## 5.4 Desktop 是否会立即获得 Web 更新

不会。

因为推荐方案是将前端静态资源打进 Desktop 安装包。

| 修改内容 | Web | Desktop |
|---|---|---|
| 页面样式 | 重新部署后生效 | 需要重新发布客户端 |
| 普通业务逻辑 | 重新部署后生效 | 需要重新发布客户端 |
| Cloud API | 后端部署后生效 | 旧客户端可能受影响 |
| Agent | 不影响 Web | Agent 或 Desktop 需要更新 |
| Tauri Bridge | 不影响 Web | 必须更新 Desktop |

因此 Cloud API 必须兼容一定范围内的旧客户端。

---

# 6. 多仓库版本锁定

真正需要解决的不是源码同步，而是：

> 某个 Desktop 安装包，到底使用了哪个版本的 Cloud 前端、Desktop 和 Agent？

建议由 `wt-media-workspace` 管理版本清单。

示例：

```yaml
version: 0.1.0

repositories:
  cloud:
    commit: a19f3d8
  desktop:
    commit: 73c918a
  agent:
    commit: b521c76
```

联合构建流程：

```text
读取 release-manifest
        ↓
检出 cloud 指定 commit
        ↓
检出 desktop 指定 commit
        ↓
检出 agent 指定 commit
        ↓
构建前端
        ↓
构建 Agent
        ↓
构建 Desktop
        ↓
生成完整安装包
```

安装包内建议记录：

```json
{
  "desktopVersion": "0.1.0",
  "frontendCommit": "a19f3d8",
  "desktopCommit": "73c918a",
  "agentCommit": "b521c76",
  "apiVersion": "v1"
}
```

这样可以做到：

- 构建结果可复现
- 出现问题可定位
- 安装包版本清晰
- 前端、Agent、Desktop 不会随意漂移
- 支持回滚

---

# 7. Web 与 Desktop 差异能力的实现方式

不要在页面中大量编写：

```ts
if (isDesktop) {
  // Desktop 特殊逻辑
}
```

应该定义统一运行时接口。

```ts
interface RuntimeAdapter {
  isDesktop: boolean

  selectLocalFile(): Promise<string | null>

  openLocalFolder(path: string): Promise<void>

  startAgent(): Promise<void>

  stopAgent(): Promise<void>

  getEnvironmentStatus(): Promise<EnvironmentStatus>

  showNotification(message: string): Promise<void>
}
```

分别实现：

```text
WebRuntimeAdapter
DesktopRuntimeAdapter
```

业务页面只依赖 `RuntimeAdapter`，不关心底层是：

- 浏览器
- Tauri
- Rust Command
- Python Agent

---

# 8. 不推荐的前端方案

## 8.1 两套完整前端

会导致：

- 页面修改两遍
- 字段修改两遍
- 权限修改两遍
- Bug 修复两遍
- 视觉逐渐分裂
- 业务逻辑不一致

---

## 8.2 Desktop 内再嵌套 iframe Web 后台

容易产生：

- 登录态问题
- 路由问题
- 弹窗层级问题
- 文件选择问题
- 快捷键问题
- 本地通信问题
- 安全边界复杂

---

## 8.3 Desktop 永远直接加载线上 Web 地址

虽然代码重复最少，但会带来：

- 无网络时不可使用
- Desktop 与 Cloud 版本不一致
- 线上页面升级可能破坏旧客户端
- 本地 Bridge 权限边界更难控制
- 客户端版本难以复现

推荐仍然是：

> 同一份源码，Web 在线部署，Desktop 打包静态资源。

---

# 9. 当前视觉效果差的根本原因

视觉问题通常不只是组件库选择问题，而是系统缺少统一的页面和交互规范。

常见问题：

1. 每个功能模块单独设计页面。
2. 表格、卡片、弹窗、筛选区没有统一标准。
3. 页面只是把字段全部铺出来，没有任务主线。
4. 不同模块使用不同状态名称和颜色。
5. 大量卡片、阴影、渐变，信息密度反而下降。
6. 资源管理页、任务页、配置页没有区分。
7. AI 或不同开发人员生成的页面风格不一致。
8. Desktop 与 Web 各自修改样式，逐渐形成两套产品。

因此不能只靠“更换组件库”解决。

---

# 10. 推荐视觉技术方案

## 10.1 推荐组合

```text
Vue 3
├── TDesign Vue Next
├── TDesign Icons
├── TDesign Design Token
├── TDesign Starter Vue Next
└── ECharts，仅用于图表
```

其中：

| 工具 | 作用 | 是否属于 UI 样式库 |
|---|---|---|
| TDesign Vue Next | 按钮、表格、表单、抽屉、弹窗等 | 是，唯一组件库 |
| TDesign Starter | 后台工程骨架和布局示例 | 不是第二套组件库 |
| TDesign Icons | 图标 | 同一设计体系 |
| ECharts | 数据图表 | 不是通用组件库 |
| Pinia | 状态管理 | 不是样式库 |
| Vue Router | 路由 | 不是样式库 |

最终原则：

> **一套组件库、一套同源图标、一个图表引擎。**

---

## 10.2 为什么推荐 TDesign

适合当前项目的原因：

- Vue 3 支持成熟
- 表格、筛选、表单、抽屉和任务型后台组件齐全
- 对高密度运营后台更友好
- 具备 Design Token
- 有现成 Starter 后台骨架
- 权限和布局方案较完整
- 中文后台场景适配较好
- 可以减少自行拼装后台框架的工作量

---

## 10.3 其他方案评价

| 方案 | 评价 |
|---|---|
| Element Plus | 成熟，但默认视觉较普通，需要较多二次设计 |
| Ant Design Vue | 后台能力强，但容易偏传统管理后台风格 |
| Arco Design Vue | 视觉现代，可作为第二选择 |
| Naive UI | 组件完整，但需要自行构建更多后台规范 |
| shadcn-vue | 自由度高，但需要自行拼装大量组件 |
| 自研组件库 | 当前阶段成本过高 |
| 混用多个 UI 库 | 不建议，容易形成视觉和交互冲突 |

---

# 11. 多套样式工具组合的主要风险

## 11.1 组件库互相污染

禁止同时引入：

```text
TDesign
Element Plus
Ant Design Vue
Arco Design
Naive UI
shadcn-vue
```

多个组件库同时存在，容易出现：

- 字体不统一
- 按钮高度不统一
- 输入框尺寸不统一
- 弹窗圆角不统一
- 状态颜色不统一
- `z-index` 冲突
- CSS Reset 冲突
- 下拉菜单被遮挡
- 页面看起来像多套系统拼接

项目应明确：

> TDesign 是唯一通用 UI 组件库。

TDesign 不满足的业务需求，应基于 TDesign 封装业务组件，而不是再引入另一套库。

---

## 11.2 Starter 与组件版本漂移

TDesign Starter 应只作为初始化骨架。

建议保留：

- Layout
- 菜单
- 路由
- 权限
- 登录基础逻辑
- 基础响应式结构

建议删除或重做：

- 演示 Dashboard
- 演示数据卡片
- 演示图表
- 营销型欢迎页
- 不需要的主题切换
- 不需要的国际化
- 不需要的布局模式

后续把 Starter 当作项目源码维护，不持续复制 Starter 官方仓库的页面。

真正需要升级的是：

```text
tdesign-vue-next
tdesign-icons-vue-next
vue
vite
```

---

## 11.3 大量覆盖组件库内部 CSS

禁止：

```css
.t-button {
  height: 38px !important;
}

.t-table td {
  padding: 5px !important;
}

.t-dialog {
  border-radius: 15px !important;
}
```

这会导致：

- 升级后失效
- 一个页面影响全系统
- `!important` 越来越多
- 样式来源无法追踪
- 组件行为不可控

推荐分层：

```text
第一层：TDesign 官方 Token
第二层：项目业务 Token
第三层：页面局部样式
```

示例：

```css
:root {
  --app-page-bg: var(--td-bg-color-page);
  --app-panel-bg: var(--td-bg-color-container);
  --app-border-radius: var(--td-radius-medium);
  --app-page-gap: 16px;
  --app-content-max-width: 1600px;
}
```

---

## 11.4 ECharts 与系统主题不一致

ECharts 只负责图表，不会自动继承业务 UI 的全部视觉。

需要统一：

- 颜色
- 字体
- 字号
- Tooltip
- 图例
- 网格线
- 状态颜色
- 暗色与亮色策略

建议封装：

```ts
export const appChartTheme = {
  color: [
    'brand',
    'success',
    'warning',
    'error',
    'neutral'
  ]
}
```

实际使用时由统一主题模块解析为具体颜色后传入 ECharts。

---

## 11.5 多套图标库

不建议同时存在：

```text
TDesign Icons
Lucide
Font Awesome
IconPark
Material Icons
```

推荐只使用：

```text
TDesign Icons
```

极少数缺失图标，放进项目自己的 SVG 目录。

---

## 11.6 全量引入导致体积膨胀

避免：

```ts
app.use(TDesign)
```

以及一次性导入全部图标。

建议：

- 按需导入
- 自动导入
- Tree Shaking
- 路由懒加载
- 图表按模块加载
- 大型编辑器单独拆包

---

## 11.7 Desktop 多系统 WebView 差异

Desktop 在不同系统可能使用不同 WebView，可能存在：

- 字体渲染差异
- 滚动条差异
- 输入框差异
- CSS 特性差异
- 文件拖拽差异
- 窗口缩放差异

当前项目如果以 Windows 为主，建议测试重点：

```text
主测试环境：Windows 11
辅助测试环境：Windows 10
兼容检查：macOS
```

重点测试：

- Drawer
- Dialog
- Dropdown
- Select 下拉层
- 固定表头
- 大表格滚动
- 125% / 150% 系统缩放
- 中文字体
- 本地文件选择器
- 窗口缩放
- 多显示器

---

# 12. 系统导航建议

需求文档的八章结构，不应该直接等同于产品左侧导航。

建议按照运营工作流组织。

```text
工作台

内容生产
├── 内容发现
├── 素材库
├── 我的素材
├── 合成任务
└── 成片管理

运营执行
├── 发布管理
├── 互动管理
└── 执行任务

数据分析
└── 数据统计

资源管理
├── 社媒账号
├── 浏览器用户
├── 合成策略
└── 评论模板

系统
├── 用户与权限
├── 云端配置
├── 本地环境（Desktop）
├── Agent 与日志（Desktop）
└── 系统设置
```

---

# 13. 全系统统一页面模板

建议全系统只保留六类核心页面模板。

---

## 13.1 资源列表页

适用于：

- 内容发现
- 素材库
- 我的素材
- 成片管理
- 社媒账号
- 评论模板

统一结构：

```text
页面标题 + 主操作
快捷筛选
高级筛选
表格
固定批量操作栏
分页
右侧详情抽屉
```

规则：

- 资源管理优先使用表格
- 封面和头像采用“小图 + 表格”
- 点击记录打开右侧抽屉
- 轻量编辑在抽屉中完成
- 不频繁跳新页面

---

## 13.2 任务工作台

适用于：

- 抓取任务
- 合成任务
- 发布任务
- 互动任务
- 自动生产任务

统一结构：

```text
任务统计
待处理 / 执行中 / 失败 / 已完成
任务列表
当前进度
执行步骤
异常信息
日志
重试 / 中断 / 丢弃
```

建议统一状态：

| 状态值 | 中文 |
|---|---|
| pending | 待执行 |
| queued | 排队中 |
| running | 执行中 |
| paused | 已暂停 |
| success | 已完成 |
| failed | 失败 |
| discarded | 已丢弃 |
| interrupted | 已中断 |

禁止同一含义在不同模块分别使用：

- 停止
- 取消
- 关闭
- 不发了
- 作废

---

## 13.3 批量配置向导

适用于：

- 批量发布
- 批量互动
- 批量领取
- 批量合成
- 批量账号分配

建议步骤：

```text
① 选择对象
② 配置规则
③ 预览与逐条调整
④ 确认执行
⑤ 查看结果
```

不要把全部字段放在一个超长表单中。

---

## 13.4 详情抽屉

统一 Tab：

```text
基本信息
关联记录
执行记录
操作日志
```

以素材为例：

- 基本信息：标题、封面、作者、来源
- 关联记录：material_usage、compose_task、composite_output
- 执行记录：生产、发布、互动结果
- 操作日志：修改人、修改时间、修改内容

---

## 13.5 设置页面

适用于：

- 平台元素配置
- 风控配置
- 自动生产规则
- 角色权限
- Agent 配置

统一结构：

```text
左侧设置分类
右侧分组表单
顶部保存状态
底部固定保存按钮
```

高级 JSON 配置应同时提供：

- 普通可视化表单
- 高级 JSON
- 校验提示
- 恢复默认值
- 配置预览

---

## 13.6 数据看板

仅用于：

- 首页工作台
- 数据统计
- 系统运行监控

不要把所有业务管理页面都做成图表看板。

---

# 14. 首页工作台建议

首页应围绕“运营下一步要做什么”设计，而不是只展示装饰性数字。

## 14.1 第一屏：系统运行状态

```text
云端服务       正常
本地 Agent     正常
浏览器环境     8 / 10 可用
本地依赖       正常
等待执行任务   23
失败任务       4
```

---

## 14.2 第二屏：需要处理

```text
4 个发布任务失败
2 个互动任务等待补链接
6 个成片等待领取
3 个账号状态异常
1 个依赖需要修复
```

---

## 14.3 第三屏：今日执行流程

```text
内容抓取 → 素材生产 → 合成 → 发布 → 互动
```

可以展示阶段计数或漏斗，但不要过度图表化。

---

## 14.4 第四屏：快捷入口

仅保留高频操作：

- 导入抖音链接
- 创建合成任务
- 批量发布
- 创建互动任务
- 查看失败任务

---

# 15. 视觉规范建议

## 15.1 基础风格

| 项目 | 建议 |
|---|---|
| 页面背景 | 浅灰白 |
| 内容容器 | 白色面板、轻边框、少阴影 |
| 品牌色 | 仅一个主色 |
| 圆角 | 6px 或 8px |
| 间距 | 8px 基础单位 |
| 正文字号 | 14px |
| 页面标题 | 20px |
| 模块标题 | 16px |
| 普通控件高度 | 32px |
| 关键表单控件 | 40px |
| 表格密度 | 中等偏紧凑 |
| 图标 | 统一 TDesign Icons |
| 动画 | 仅保留必要状态和抽屉动画 |
| 暗色模式 | 首版不做 |

---

## 15.2 状态颜色

```text
蓝色：执行中、待处理
绿色：成功、正常
橙色：警告、待确认
红色：失败、异常
灰色：关闭、丢弃、过期
紫色：自动化、AI 生成
```

应封装统一组件：

```vue
<BusinessStatus status="running" />
```

禁止各页面自行决定 Tag 颜色。

---

## 15.3 强制交互规则

1. 一页只允许一个主要按钮。
2. 卡片只用于摘要，不用于大量数据管理。
3. 表格操作按钮最多直接展示 2～3 个，其余放入“更多”。
4. 短信息使用弹窗。
5. 详情与轻量编辑使用抽屉。
6. 复杂流程使用独立页面。
7. 批量操作必须使用固定操作栏。
8. 本地数据统一标记“本地”。
9. 云端数据统一标记“云端”。
10. 失败状态必须直接展示失败原因和下一步操作。
11. 不使用大面积渐变、发光和毛玻璃。
12. 所有列表页必须提供空状态、加载状态和失败状态。

---

# 16. 优先改造顺序

不建议一次性推翻全部页面。

建议先选择三个页面建立标准。

## 16.1 Desktop 系统状态中心

验证：

- Desktop 独有能力
- Agent 状态
- 本地环境
- 本地依赖
- 日志
- 云端与本地标记
- 异常修复入口

---

## 16.2 内容发现列表

验证：

- 筛选区
- 表格
- 封面预览
- 详情抽屉
- 批量转素材
- 去重状态
- 来源信息

---

## 16.3 合成任务台

验证：

- 任务状态
- 队列
- 进度
- 失败原因
- 重试
- 中断
- 实时更新
- 本地与云端执行差异

三个页面定型后，再复制模板到：

- 素材管理
- 成片管理
- 发布管理
- 互动管理
- 抓取任务
- 自动生产任务

---

# 17. 最终定案表

| 问题 | 推荐定案 |
|---|---|
| Web 与 Desktop 前端 | 不做两套 |
| 前端代码 | 一套 Vue 业务前端 |
| 前端源码位置 | `wt-media-cloud/frontend` |
| Web 构建 | `build:web` |
| Desktop 构建 | `build:desktop` |
| Desktop 角色 | Tauri 壳、本地 Bridge、更新和系统能力 |
| Agent 角色 | Python 本地执行服务 |
| 多仓库联合构建 | `wt-media-workspace` |
| 版本锁定 | 使用 release manifest 锁定 commit |
| UI 组件库 | TDesign Vue Next |
| 后台模板 | TDesign Starter，仅作为初始化骨架 |
| 图标 | TDesign Icons |
| 图表 | ECharts |
| 样式规范 | TDesign Token + 项目 Token |
| 第二套 UI 库 | 禁止引入 |
| 首版暗色模式 | 不做 |
| 页面体系 | 六类统一模板 |
| 首批改造 | 状态中心、内容发现、合成任务台 |

---

# 18. 一句话总结

> 当前系统应该建设成一套同时运行在浏览器和 Tauri 中的统一运营工作台。前端源码只保留一份，通过不同构建模式输出 Web 和 Desktop；视觉上只使用一套 UI 体系，并通过统一布局、状态、页面模板和 Design Token，解决当前页面风格混乱、重复开发和维护成本高的问题。
