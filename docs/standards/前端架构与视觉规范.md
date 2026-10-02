# Web / Desktop 前端架构与视觉体系基线

> 文档性质：项目级前端架构与视觉交互基线  
> 文档版本：V2.0  
> 文档日期：2026-09-25  
> 适用范围：WT Media Cloud Web、Desktop 内嵌 Web 与共享业务模块  
> 适用对象：产品、设计、前端开发、Claude Code、Codex、代码评审人员

---

# 1. 文档目的与范围

本文只规定两件事：

**一、前端架构基线**——Web 与 Desktop 如何共用一套 Vue 源码、源码落在哪个仓库与目录、如何开发与构建、如何锁定多仓库版本。

**二、视觉与交互基线**——前端技术与组件库边界；颜色、文字、间距、圆角和阴影；按钮、状态、标签、表格、表单、弹窗和抽屉；管理后台页面的统一信息层级；Cloud 与 Desktop 的界面边界；Claude Code 与 Codex 的前端修改约束。

本文回答四个问题：

1. Desktop 与 Cloud/Web 都需要展示各功能模块，是否会产生前端代码重复？
2. 前端源码只保留一份之后，修改如何同步到 Desktop？
3. 当前功能模板视觉效果较差，应该采用什么成熟、美观、易用的方案？
4. 同时使用组件库、后台模板、图表库等工具，会不会产生样式冲突和维护风险？

本文**不**记录以下内容，它们各有落点，写进本文会成为第二份事实源：

- 某个具体业务页面的按钮名称、字段顺序和特殊交互 → 放在独立的「页面设计案例／页面规格」文档中；
- 系统左侧导航的栏目划分、业务范围与里程碑排期 → 由 `docs/product` 与 `delivery/MASTER_IMPLEMENTATION_PLAN.md` 规定；
- 业务状态与任务状态的取值枚举 → 属契约落点（`docs/contracts`、各产物自己的 `versions.json`）。

---

# 2. 前端架构基线

## 2.1 总体结论：一套源码，两种运行模式

当前项目**不**维护两套完整前端。

> **一套 Vue 3 业务前端，两种运行模式；Web 负责浏览器运行，Desktop 通过 Tauri 承载同一套前端，并额外提供本地能力。**

整体预计可以复用约 **80%～90%** 的页面、组件和业务逻辑。

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

只有 Desktop 本地能力需要差异化实现。Desktop 不重新开发一套业务页面，只额外负责：

- 本地环境检测
- Agent 启停与状态观测
- 本地文件和目录访问
- 本地缓存与日志
- 浏览器窗口控制
- 依赖安装与卸载
- 客户端升级
- Tauri Bridge
- Desktop 安装包构建

推荐前端技术栈：

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

## 2.2 多仓库职责

- `wt-media-workspace`
- `wt-media-cloud`
- `wt-media-agent`
- `wt-media-desktop`

### 2.2.1 `wt-media-cloud`

前端源码位于本仓库的 `web/`：

```text
wt-media-cloud/
├── cmd/                    # Go 后端入口
├── internal/               # Go 后端实现
├── pkg/                    # Go 公共包
├── contracts/              # 对外契约工件
└── web/                    # 唯一 Vue 前端源码
    ├── src/
    ├── index.cloud.html
    ├── index.desktop.html
    ├── vite.config.js
    ├── vite.config.cloud.js
    └── vite.config.desktop.js
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

### 2.2.2 `wt-media-desktop`

```text
wt-media-desktop/
├── src-tauri/
├── scripts/
└── tests/
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

### 2.2.3 `wt-media-agent`

负责：

- Python 本地执行服务
- 浏览器控制
- 合成执行
- 发布执行
- 互动执行
- 依赖环境能力
- 本地任务日志
- 本地运行状态

### 2.2.4 `wt-media-workspace`

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

## 2.3 前端源码结构与依赖方向

技术栈：

```text
Vue 3
+ Vite
+ TDesign Vue Next
+ Cloud / Desktop 双入口
+ Tauri 2 Desktop 外壳
```

全部 Vue 源码统一位于 `wt-media-cloud/web`，应用组织：

```text
src/
├── apps/
│   ├── cloud/
│   └── desktop/
├── modules/
├── shared/
└── generated/
```

依赖方向：

```text
apps → modules
apps → shared
modules → shared
```

禁止：

```text
shared → modules
shared → apps
modules → apps
```

组件库统一使用 **TDesign Vue Next**。禁止引入第二套完整 UI 组件库。

---

## 2.4 Web 与 Desktop 差异能力的实现方式

不要在页面中大量编写：

```ts
if (isDesktop) {
  // Desktop 特殊逻辑
}
```

应该定义统一运行时接口：

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

## 2.5 开发与构建

### 2.5.1 开发环境

不复制源码，因此不需要日常「同步代码」。

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

`wt-media-cloud/web` 是唯一前端源码来源。开发时启动 Vite：

```text
wt-media-cloud/web
        ↓
http://127.0.0.1:5173            （npm run dev，Vite 默认端口）
        ↓
浏览器直接访问
        ↓
Tauri Desktop 通过 devUrl 加载 http://127.0.0.1:5174   （npm run dev:desktop）
```

修改 Vue 页面后：

- 浏览器立即热更新；
- Desktop 窗口立即热更新；
- 不需要复制源码；
- 不需要重复提交；
- 不需要生成两套页面。

`wt-media-desktop/src-tauri/tauri.conf.json` 中与前端相关的键（**这些是字段名／脚本名，不得改写**）：

```json
{
  "build": {
    "devUrl": "http://127.0.0.1:5174",
    "beforeDevCommand": "cd ../../wt-media-cloud/web && npm run dev:desktop",
    "beforeBuildCommand": "bash scripts/prepare-release-sidecar.sh && bash ../wt-media-workspace/scripts/build-desktop-frontend.sh",
    "frontendDist": "../.generated/frontend"
  }
}
```

### 2.5.2 正式构建

`wt-media-cloud/web` 的 `package.json` 提供的脚本（实测）：

```json
{
  "scripts": {
    "dev": "vite",
    "dev:desktop": "vite --config vite.config.desktop.js",
    "build": "vite build",
    "build:cloud": "vite build --config vite.config.cloud.js",
    "build:desktop": "vite build --config vite.config.desktop.js",
    "test": "vitest run"
  }
}
```

| 命令 | 配置 | 入口 HTML | 产物目录 |
|---|---|---|---|
| `npm run build:cloud` | `vite.config.cloud.js` | `index.cloud.html` | `dist-cloud/` |
| `npm run build:desktop` | `vite.config.desktop.js` | `index.desktop.html` | `dist-desktop/` |

包管理器为 **npm**，以仓库内的 `package-lock.json` 为准；安装使用 `npm ci`。

Cloud 构建：

```text
1. 进入 wt-media-cloud/web
2. npm ci
3. npm run build:cloud
4. 生成 dist-cloud
5. 部署到 Cloud/Web
```

Desktop 构建：

```text
1. 拉取指定版本的 wt-media-cloud
2. 进入 wt-media-cloud/web
3. npm ci
4. npm run build:desktop
5. 生成 dist-desktop
6. Tauri 打包（由 workspace 的 scripts/build-desktop-frontend.sh 复制到 .generated/frontend）
7. 生成 exe / msi / dmg
```

`wt-media-desktop/src-tauri/tauri.conf.json` 的开发态 `devUrl` 指向 `127.0.0.1:5174`，与 `dev:desktop` 的 Vite 端口一致（`strictPort: true`）。Desktop 的构建配置有一个 `desktop-html` 插件，把 `/src/apps/cloud/main.ts` 替换为 `/src/apps/desktop/main.ts`；该配置中另有注释禁止把 `@tauri-apps/api/core` 外部化。

### 2.5.3 Desktop 不会随 Web 即时更新

推荐方案是把前端静态资源打进 Desktop 安装包，所以：

| 修改内容 | Web | Desktop |
|---|---|---|
| 页面样式 | 重新部署后生效 | 需要重新发布客户端 |
| 普通业务逻辑 | 重新部署后生效 | 需要重新发布客户端 |
| Cloud API | 后端部署后生效 | 旧客户端可能受影响 |
| Agent | 不影响 Web | Agent 或 Desktop 需要更新 |
| Tauri Bridge | 不影响 Web | 必须更新 Desktop |

因此 **Cloud API 必须兼容一定范围内的旧客户端**——这正是下一节版本锁定要解决的问题。

---

## 2.6 多仓库版本锁定

真正需要解决的不是源码同步，而是：

> 某个 Desktop 安装包，到底使用了哪个版本的 Cloud 前端、Desktop 和 Agent？

版本事实由 `wt-media-workspace` 管理，落点是既有的三处，**不新增第四处**：

| 落点 | 作用 |
|---|---|
| `config/release-matrix.yaml` | 每个已核实 release 的 `components:`（cloud／cloud_agent／desktop／local_agent 版本）、`contracts:`、`verification:` 与 `scope` |
| `config/repository-map.yaml` | 相邻仓库路径映射（被 `verify_ai_workspace.py` 双向校验） |
| `scripts/release-versions.sh` | 版本号的唯一实现处；各产物自己的 `versions.json` 也在声明同一份事实 |

前端产物自身携带溯源信息。`scripts/build-desktop-frontend.sh` 在复制产物后调用 `release-versions.sh --stamp-frontend`，写出 `wt-media-desktop/.generated/frontend/frontend-build.json`，其字段为：

```json
{
  "source": "wt-media-cloud/web",
  "package_version": "<web/package.json 的 version>",
  "source_commit": "<wt-media-cloud 的 commit>",
  "source_dirty": false,
  "files": 0,
  "digest": "<内容摘要>",
  "manifest": {}
}
```

发布日期事实来自 `release-versions.sh` 写出的 `frontend_build_version`。

联合构建流程：

```text
读取 release-matrix / release-versions 的版本事实
        ↓
检出 cloud 指定 commit
        ↓
检出 desktop 指定 commit
        ↓
检出 agent 指定 commit
        ↓
构建前端（npm run build:desktop）
        ↓
构建 Agent
        ↓
构建 Desktop
        ↓
生成完整安装包
```

这样可以做到：

- 构建结果可复现
- 出现问题可定位
- 安装包版本清晰
- 前端、Agent、Desktop 不会随意漂移
- 支持回滚

---

## 2.7 不推荐的前端方案

### 2.7.1 两套完整前端

会导致：

- 页面修改两遍
- 字段修改两遍
- 权限修改两遍
- Bug 修复两遍
- 视觉逐渐分裂
- 业务逻辑不一致

### 2.7.2 Desktop 内再嵌套 iframe Web 后台

容易产生：

- 登录态问题
- 路由问题
- 弹窗层级问题
- 文件选择问题
- 快捷键问题
- 本地通信问题
- 安全边界复杂

### 2.7.3 Desktop 永远直接加载线上 Web 地址

虽然代码重复最少，但会带来：

- 无网络时不可使用
- Desktop 与 Cloud 版本不一致
- 线上页面升级可能破坏旧客户端
- 本地 Bridge 权限边界更难控制
- 客户端版本难以复现

推荐仍然是：

> 同一份源码，Web 在线部署，Desktop 打包静态资源。

---

# 3. 视觉与交互基线

## 3.1 视觉效果差的根本原因

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

因此不能只靠「更换组件库」解决。第 3 章与第 4 章就是针对这八条的规则。

---

## 3.2 组件库边界

推荐组合：

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

### 3.2.1 为什么推荐 TDesign

- Vue 3 支持成熟
- 表格、筛选、表单、抽屉和任务型后台组件齐全
- 对高密度运营后台更友好
- 具备 Design Token
- 有现成 Starter 后台骨架
- 权限和布局方案较完整
- 中文后台场景适配较好
- 可以减少自行拼装后台框架的工作量

### 3.2.2 其他方案评价

| 方案 | 评价 |
|---|---|
| Element Plus | 成熟，但默认视觉较普通，需要较多二次设计 |
| Ant Design Vue | 后台能力强，但容易偏传统管理后台风格 |
| Arco Design Vue | 视觉现代，可作为第二选择 |
| Naive UI | 组件完整，但需要自行构建更多后台规范 |
| shadcn-vue | 自由度高，但需要自行拼装大量组件 |
| 自研组件库 | 当前阶段成本过高 |
| 混用多个 UI 库 | 不建议，容易形成视觉和交互冲突 |

### 3.2.3 Starter 的取舍

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

## 3.3 五层样式复用模型

### 3.3.1 样式不是每个页面重新手写

本项目已经使用 TDesign Vue Next。按钮、输入框、下拉框、表格、分页、表单、标签、弹窗、抽屉、提示、加载和空状态等基础组件，必须优先使用 TDesign 提供的组件和默认交互。

**不得把前端页面理解为：每做一个页面，就重新写一套按钮、输入框、表格和弹窗 CSS。**

正确的样式复用关系为：

```text
第一层：TDesign Vue Next
提供基础组件、基础样式和通用交互状态

第二层：WT Media Theme / Design Tokens
统一品牌颜色、状态颜色、字号、间距、圆角、边框和密度

第三层：WT Media Shared UI
统一页面标题、统计区、筛选区、批量工具栏、状态展示和空状态

第四层：业务模块组件
统一账号、窗口、素材、发布等业务专用单元格和业务展示

第五层：页面局部样式
只处理当前页面少量无法复用的布局差异
```

AI 和开发人员必须先判断需求属于哪一层，再决定写在哪里。

### 3.3.2 各层具体负责什么

**第一层：TDesign Vue Next**

优先直接使用：

```text
Button
Input
Select
Form
Table
Pagination
Tag
Alert
Dialog
Drawer
Tooltip
Loading
Empty
Checkbox
Radio
Tabs
DatePicker
```

TDesign 已经处理：

- Hover、Active、Focus、Disabled；
- 表单校验；
- 弹窗和抽屉基础结构；
- 表格基础行为；
- 键盘与通用交互状态；
- 基础组件尺寸和视觉。

禁止为普通组件重新创建：

```text
MyButton
MyInput
MySelect
MyTable
MyDialog
```

除非项目确实需要统一封装且已经在多个页面复用。

**第二层：WT Media Theme / Design Tokens**

集中维护：

```text
品牌主色
成功、警告、危险色
页面背景
文字颜色
边框
字号
间距
圆角
阴影
组件密度
```

这层负责把项目视觉映射到 TDesign，不承担具体业务布局。

**第三层：WT Media Shared UI**

适合建设的公共组件包括：

```text
PageContainer
PageHeader
SummaryMetrics
PageActions
FilterPanel
SelectionToolbar
StatusBadge
EntityLink
CopyableText
EmptyState
ErrorState
ResultSummary
```

这些组件解决多个管理页面重复出现的结构，不得包含账号、素材、发布等具体业务规则。

**第四层：业务模块组件**

业务模块可以维护自己的复用组件，例如：

```text
AccountInfoCell
BrowserProfileSummary
AccountStatusBadge
BatchCheckProgress
MaterialInfoCell
PublicationStatusCell
```

这些组件应放在对应 `modules/<business>/components` 中，不放进全局 `shared`。

**第五层：页面局部样式**

只有以下内容可以在页面中局部书写：

- 当前页面独有的列宽；
- 当前页面特殊区域的 Grid 或 Flex 组合；
- 某个业务单元格的少量对齐；
- 无法通过 TDesign 属性、项目 Token 或共享组件解决的布局。

页面局部样式不得重新定义：

```text
项目主色
成功色
危险色
按钮通用样式
输入框通用样式
表格通用样式
全局字号
全局间距体系
```

### 3.3.3 推荐目标比例

```text
约 70%：TDesign 现成组件与交互
约 20%：项目主题、Token 和共享 UI
约 10%：业务模块组件与页面局部样式
```

该比例是设计目标，不是强制代码统计指标。它表达的核心要求是：**项目应以复用为主，而不是以页面手写 CSS 为主。**

---

## 3.4 样式决策顺序与禁止实现

### 3.4.1 决策顺序

Claude Code 或 Codex 遇到视觉、布局或组件任务时，必须按顺序检查：

```text
1. TDesign 是否已有对应组件或属性？
   有 → 直接使用。

2. 项目 Theme / Token 是否已有对应语义？
   有 → 使用 Token，不写硬编码颜色和尺寸。

3. shared/ui 是否已有公共页面组件？
   有 → 复用，不复制实现。

4. 当前业务模块是否已有业务组件？
   有 → 复用或扩展稳定接口。

5. 多个页面是否确实会重复使用？
   是 → 抽取到合适层级。

6. 以上都不满足？
   才允许写当前页面的局部样式。
```

禁止跳过前五步，直接在页面中堆 CSS。

### 3.4.2 禁止的错误实现

```text
每个页面重新定义 primary button
每个页面重新写 table header 和 pagination 样式
每个页面硬编码相同的蓝、绿、橙、红
为了一个页面引入 Element Plus、Naive UI 或 Ant Design Vue
复制一份 shared 组件后局部修改
在页面中使用大量 !important 覆盖 TDesign
依赖 TDesign 易变的内部 DOM 和内部类名
为了少量差异复制 Cloud 与 Desktop 两套页面
```

### 3.4.3 落地前必须核实真实代码

本文确认的是项目架构和设计原则，不构成「照目录新建文件」的许可。首次实际落地（以及任何一次新增公共样式或公共组件）前，必须读取真实代码，核查：

```text
package.json 中的 TDesign Vue Next 精确版本
现有全局样式入口与当前全局 CSS / Less 变量
已有主题覆盖文件
src/shared/styles
src/shared/ui
现有页面公共组件
```

不得因为文档写了推荐目录，就直接重复创建已经存在的文件或组件。本文的 Token 必须映射到**当前安装的** TDesign Vue Next 版本，不得凭空假设变量名。

---

## 3.5 总体设计原则

### 3.5.1 运营任务优先

页面应优先回答：

```text
当前是什么状态？
哪些内容需要处理？
下一步可以做什么？
操作后的真实结果是什么？
```

### 3.5.2 信息层级优先于装饰

管理后台页面默认信息层级：

```text
页面标题
→ 必要的页面级反馈
→ 概览或统计
→ 页面主操作
→ 搜索与筛选
→ 批量操作
→ 主列表或主内容
→ 分页
```

### 3.5.3 颜色表达语义

**全系统只有这一张颜色语义表**，其余各节（按钮、状态、标签、图表）都从它派生，不得另立一套含义。

| 颜色 | 语义 |
|---|---|
| 蓝色 | 品牌、主要操作、选中状态、链接；执行中、待处理 |
| 绿色 | 真实成功或正常 |
| 橙色 | 警告、需要关注、尚未完成、待确认、临近到期 |
| 红色 | 错误、冲突、受限、危险确认、失败、异常 |
| 灰色 | 停用、未配置、未检查、已关闭、已丢弃、已过期、辅助信息 |
| 紫色 | 自动化、AI 生成 |

### 3.5.4 状态与操作分离

状态颜色用于表达结果，不用于装饰按钮。操作按钮颜色由操作层级决定。

### 3.5.5 真实结果优先

涉及 Agent、BitBrowser、平台页面或外部服务的操作：

- 请求已发送不等于成功；
- 成功必须来自真实执行和必要读回；
- 无法确认时必须展示「结果待确认」或明确失败原因。

### 3.5.6 强制交互规则

1. 一页只允许一个主要按钮。
2. 卡片只用于摘要，不用于大量数据管理。
3. 表格操作按钮最多直接展示 2～3 个，其余放入「更多」。
4. 短信息使用弹窗。
5. 详情与轻量编辑使用抽屉。
6. 复杂流程使用独立页面。
7. 批量操作必须使用固定操作栏。
8. 本地数据统一标记「本地」。
9. 云端数据统一标记「云端」。
10. 失败状态必须直接展示失败原因和下一步操作。
11. 不使用大面积渐变、发光和毛玻璃。
12. 所有列表页必须提供空状态、加载状态和失败状态。

---

## 3.6 Design Tokens

### 3.6.1 颜色

```css
:root {
  /* Brand */
  --wt-color-primary: #0052d9;
  --wt-color-primary-hover: #266fe8;
  --wt-color-primary-active: #003cab;
  --wt-color-primary-light: #e8f3ff;
  --wt-color-primary-border: #bbd3fb;

  /* Semantic */
  --wt-color-success: #00a870;
  --wt-color-success-bg: #e8f8f2;
  --wt-color-success-border: #a7e3cf;

  --wt-color-warning: #ed7b2f;
  --wt-color-warning-bg: #fff3e8;
  --wt-color-warning-border: #f7c797;

  --wt-color-danger: #d54941;
  --wt-color-danger-hover: #e34d59;
  --wt-color-danger-bg: #fff0ed;
  --wt-color-danger-border: #f5b7b1;

  /* Text */
  --wt-color-text-primary: #1d2129;
  --wt-color-text-secondary: #4e5969;
  --wt-color-text-assist: #86909c;
  --wt-color-text-disabled: #c9cdd4;
  --wt-color-text-inverse: #ffffff;

  /* Background */
  --wt-color-bg-page: #f2f3f5;
  --wt-color-bg-container: #ffffff;
  --wt-color-bg-subtle: #f7f8fa;
  --wt-color-bg-hover: #f2f3f5;

  /* Border */
  --wt-color-border: #e5e6eb;
  --wt-color-border-strong: #c9cdd4;

  /* Shadow */
  --wt-shadow-fixed-column: -6px 0 12px rgb(0 0 0 / 6%);
  --wt-shadow-popup: 0 8px 24px rgb(0 0 0 / 12%);
}
```

业务页面不得散落硬编码十六进制颜色。应通过项目 Token 或 TDesign 主题映射使用。

### 3.6.2 字体

推荐字体栈：

```css
font-family:
  -apple-system,
  BlinkMacSystemFont,
  "Segoe UI",
  "PingFang SC",
  "Microsoft YaHei",
  Arial,
  sans-serif;
```

字号：

| 用途 | 字号 | 字重 |
|---|---:|---:|
| 页面标题 | 20px | 600 |
| 区块标题 | 16px | 600 |
| 正文 | 14px | 400 |
| 强调正文 | 14px | 500/600 |
| 辅助文字 | 12px | 400 |
| 统计数字 | 24–28px | 600 |

### 3.6.3 间距

统一采用 4px 基础网格：

```text
4 / 8 / 12 / 16 / 20 / 24 / 32
```

常用规则：

| 场景 | 间距 |
|---|---:|
| 页面左右内边距 | 24px |
| 页面上下内边距 | 20–24px |
| 页面区块间距 | 16px |
| 卡片内边距 | 16px |
| 表单字段纵向间距 | 16px |
| 同组按钮间距 | 8px |
| 文字按钮间距 | 12px |

### 3.6.4 圆角与阴影

- 卡片和筛选容器：6–8px；
- 普通按钮和输入框：使用 TDesign 默认中等圆角；
- 默认卡片不使用明显阴影；
- 固定表格列使用轻阴影；
- 弹窗和下拉层使用统一浮层阴影。

### 3.6.5 基础视觉取值

| 项目 | 取值 |
|---|---|
| 页面背景 | 浅灰白 |
| 内容容器 | 白色面板、轻边框、少阴影 |
| 品牌色 | 仅一个主色 |
| 圆角 | 6px 或 8px |
| 间距 | 4px 基础网格 |
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

## 3.7 按钮规范

### 3.7.1 Primary

当前区域最重要、最推荐执行的动作。样式：品牌蓝色实心。规则：每个操作区域最多一个 Primary。

### 3.7.2 Secondary

同一区域的重要辅助动作。样式：白底、灰色边框、深色文字。

### 3.7.3 Text

低层级、高频或表格行操作。样式：无背景、无边框。

### 3.7.4 Link Primary

明确可点击的实体名称或高频轻操作。样式：品牌色文字。

### 3.7.5 Danger

危险操作分两级：

- 列表或页面中：普通文字，悬停变红；
- 最终确认弹窗中：红色实心。

### 3.7.6 禁用

统一使用浅灰背景、浅灰边框和禁用文字。依赖选择后才出现的批量操作，应在未选择时隐藏，而不是长期展示大量禁用按钮。

---

## 3.8 状态规范

### 3.8.1 业务状态

| 状态语义 | 样式 |
|---|---|
| 启用、有效 | 绿色浅底标签 |
| 停用、归档 | 灰色浅底标签 |

「停用」是正常业务选择，不使用红色状态样式。

### 3.8.2 健康状态

| 状态语义 | 颜色 |
|---|---|
| 正常、成功 | 绿色 |
| 未检查、未配置 | 灰色 |
| 待处理、待验证、临近到期 | 橙色 |
| 错误、冲突、失效、受限 | 红色 |

状态必须同时显示文字，不得只使用颜色圆点。

### 3.8.3 任务状态

| 状态 | 颜色 |
|---|---|
| 等待执行 | 灰色 |
| 执行中 | 蓝色 |
| 成功 | 绿色 |
| 部分成功 | 橙色 |
| 失败 | 红色 |
| 已取消 | 灰色 |
| 已中断 | 橙色或灰色 |
| 结果待确认 | 橙色 |

状态取值本身由契约规定，本文不复制枚举；本文规定的是**颜色映射**与下面这条规则。

### 3.8.4 状态展示的封装

颜色含义见 §3.5.3，本节只规定**谁来选颜色**：应封装统一组件，

```vue
<BusinessStatus status="running" />
```

禁止各页面自行决定 Tag 颜色。业务状态（§3.8.1）、健康状态（§3.8.2）、任务状态（§3.8.3）三类都由这一个组件呈现，页面只传状态值。

### 3.8.5 一词一义

同一含义不得在不同模块分别使用不同说法：

```text
停止 / 取消 / 关闭 / 不发了 / 作废
```

---

## 3.9 业务标签规范

业务标签属于分类信息，不属于状态。统一使用：

```text
中性浅灰背景
中性边框
次级文字色
```

规则：

- 不随机使用红、橙、绿；
- 列表最多显示两个，超出显示 `+N`；
- 点击可以查看全部；
- 复杂标签中心需有独立需求，不得由页面临时扩展。

---

# 4. 页面结构与模板

## 4.1 管理列表页模板

固定结构：

```text
PageHeader
→ PageAlert（仅页面级问题）
→ SummaryMetrics
→ PageActions
→ FilterPanel
→ SelectionToolbar（有选择时出现）
→ DataTable
→ Pagination
```

### 4.1.1 PageHeader

- 中文业务名称；
- 一行副标题说明页面用途；
- 不使用英文占位标题。

### 4.1.2 SummaryMetrics

- 指标较少时使用单行紧凑卡片；
- 高度 72–80px；
- 只显示名称和数字；
- 点击可应用现有筛选；
- 不使用大面积强色背景。

### 4.1.3 PageActions

- 放在统计下方、筛选上方；
- 同一区域一个 Primary；
- 配置类入口与主要业务操作分开。

### 4.1.4 FilterPanel

推荐两行：

```text
第一行：综合搜索 + 查询 + 重置
第二行：高频筛选项
```

综合搜索建议 360–440px。

### 4.1.5 SelectionToolbar

未选择时隐藏；选择后展示已选数量和批量操作。

### 4.1.6 DataTable

- 表头高度 44–48px；
- 行高 64–76px；
- 单元格最多两到三行；
- 长 ID 使用省略、Tooltip 和复制；
- 状态列独立；
- 操作列固定右侧；
- 分页总数必须正确。

---

## 4.2 六类核心页面模板

全系统只保留六类核心页面模板。每类模板只规定**结构与规则**；它适用于哪些业务模块由产品文档决定，不在本文登记。

### 4.2.1 资源列表页

**它就是 §4.1 的管理列表页模板**（PageHeader → … → Pagination），不另立一套结构；右侧详情抽屉按 §4.4.2 实现。这类页面额外的规则：

- 资源管理优先使用表格；
- 封面和头像采用「小图 + 表格」；
- 点击记录打开右侧抽屉；
- 轻量编辑在抽屉中完成；
- 不频繁跳新页面。

### 4.2.2 任务工作台

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

状态的颜色映射见 §3.8.3；状态取值的枚举以契约为准。

### 4.2.3 批量配置向导

建议步骤：

```text
① 选择对象
② 配置规则
③ 预览与逐条调整
④ 确认执行
⑤ 查看结果
```

不要把全部字段放在一个超长表单中。

### 4.2.4 详情抽屉

**尺寸、分区与操作约定见 §4.4.2**（那里是抽屉的唯一落点）。本节只规定它的**统一 Tab 划分**：

```text
基本信息
关联记录
执行记录
操作日志
```

每个 Tab 只承担一类信息：基本信息、关联资源、执行结果、操作日志（修改人、修改时间、修改内容）。字段清单属具体页面设计，不在本文登记。

### 4.2.5 设置页面

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

### 4.2.6 数据看板

仅用于需要长期观察整体运行态势的页面（首页工作台、数据统计、系统运行监控）。

不要把所有业务管理页面都做成图表看板。

---

## 4.3 表格规范

### 4.3.1 信息单一职责

每列只承担一个主要语义。禁止把多个独立状态塞入同一列。

### 4.3.2 可点击内容

- 实体名称可以使用品牌色文字；
- ID 和 UID 使用复制图标与 Tooltip；
- 不可点击内容不得伪装成链接。

### 4.3.3 固定列

- 选择列可以固定左侧；
- 操作列固定右侧；
- 固定列边界使用轻阴影，不使用深色竖线。

### 4.3.4 分页

必须展示：总条数、每页数量、当前页、前后翻页。列表有数据但总数为零属于阻塞性缺陷。

---

## 4.4 表单、弹窗与抽屉

### 4.4.1 创建 / 编辑表单

字段按业务分组：

```text
基本信息
业务分类
关联资源
备注
```

新增和编辑尽量复用同一表单结构。

### 4.4.2 详情抽屉

- 建议宽度 560–640px；
- 按 §4.2.4 的四个 Tab 分区（基本信息里含当前状态）；
- 底部固定高频操作；
- 不复制完整独立管理页面。

### 4.4.3 确认弹窗

必须清楚说明：

```text
即将执行什么
会影响什么
不会影响什么
是否可恢复
```

危险操作的最终确认按钮使用红色实心。

---

## 4.5 反馈与异常

### 4.5.1 页面级 Alert

仅用于影响整个页面的问题，例如列表加载失败、权限不足、核心依赖导致页面不可用。必须说明：发生了什么、影响什么、如何处理。

### 4.5.2 单项操作失败

使用：

```text
Toast / Message
+ 当前行状态更新
+ 查看详情入口
```

不得将单项失败长期展示成页面级红条。

### 4.5.3 批量操作

必须展示总数、完成数、成功、失败、跳过、当前处理项和失败原因，并支持仅重试失败项。

### 4.5.4 环境异常

有独立环境监测页面时，业务页面不常驻复制环境状态卡片。用户发起依赖环境的操作时，再提示并提供跳转入口。

### 4.5.5 空状态

必须区分：无数据、筛选无结果、加载失败、无权限。

---

# 5. Cloud 与 Desktop UI 边界

- 共享业务页面放在 `modules`；
- 环境监测、本地 Agent、本地日志、软件更新等放在 Desktop 应用层；
- 共享页面通过 Runtime / Capability 控制本地能力；
- 页面不得直接检测 Tauri 全局对象；
- 不允许复制 Cloud 和 Desktop 两套业务页面。

---

# 6. 样式与代码组织

样式实现必须遵循第 3.3 节定义的五层复用模型，不得将所有样式堆入页面组件。

推荐代码分布：

```text
src/
├── shared/
│   ├── styles/
│   │   ├── tokens.css
│   │   ├── tdesign-theme.css
│   │   ├── base.css
│   │   ├── layout.css
│   │   └── utilities.css
│   └── ui/
│       ├── PageHeader/
│       ├── SummaryMetrics/
│       ├── FilterPanel/
│       ├── SelectionToolbar/
│       ├── StatusBadge/
│       ├── EmptyState/
│       └── ErrorState/
│
└── modules/
    └── accounts/
        ├── pages/
        └── components/
            ├── AccountInfoCell.vue
            ├── BrowserProfileSummary.vue
            └── AccountStatusBadge.vue
```

`src/shared/styles/` 各文件职责：

| 文件 | 职责 |
|---|---|
| `tokens.css` | 项目颜色、文字、间距、圆角、阴影等语义 Token |
| `tdesign-theme.css` | 将项目 Token 映射到当前 TDesign 版本 |
| `base.css` | 字体、页面背景、基础 Reset 等全局规则 |
| `layout.css` | 稳定复用的页面容器和管理后台布局 |
| `utilities.css` | 少量稳定工具类，如省略、不可换行、辅助文字 |

规则：

- Token 是项目视觉事实源；
- TDesign 主题覆盖集中管理；
- 先使用 TDesign 属性，再考虑 CSS 覆盖；
- 页面只写必要局部布局；
- 同类页面不得复制相同样式；
- 多页面稳定复用后，应提升到共享组件或公共样式；
- 禁止大量 `!important`；
- 禁止依赖 TDesign 易变内部 DOM 和类名；
- 状态中文、语义颜色和权限使用集中映射，不在页面散落三元表达式；
- 不得为了符合推荐目录而重复创建仓库中已经存在的文件。

---

# 7. 多套样式工具组合的主要风险

## 7.1 组件库互相污染

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

## 7.2 大量覆盖组件库内部 CSS

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

## 7.3 ECharts 与系统主题不一致

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

## 7.4 多套图标库

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

## 7.5 全量引入导致体积膨胀

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

当前 `vite.config.js` 已通过 `unplugin-auto-import` 与 `unplugin-vue-components` 配置了 `TDesignResolver` 自动导入，新增组件沿用该机制即可，不要额外手写全量注册。

## 7.6 Desktop 多系统 WebView 差异

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

# 8. 修改前检查与 Review

## 8.1 Claude / Codex 修改前检查

1. 当前任务是否允许修改功能？
2. 是否只要求布局、颜色或视觉调整？
3. 页面属于 Cloud、Desktop 还是共享模块？
4. TDesign 是否已经提供对应组件、属性或插槽？
5. 项目 Theme / Token 是否已有对应语义？
6. 是否存在可复用页面模板、共享 UI 或业务组件？
7. 是否正在引入第二套 UI 体系？
8. 是否硬编码已有 Token 可以表达的颜色或尺寸？
9. 是否复制了已经存在的样式或组件？
10. 是否把业务状态和健康状态混在一起？
11. 是否把单项错误升级为全局 Alert？
12. 是否把请求提交展示为真实成功？
13. 是否改变已确认的功能边界？

## 8.2 UI Review 清单

**页面层级**

- [ ] 中文页面标题和明确副标题；
- [ ] 统计、操作、筛选、列表顺序正确；
- [ ] 首屏能看到主内容；
- [ ] 同一区域只有一个蓝色实心主按钮。

**颜色与状态**

- [ ] 颜色来自 Token；
- [ ] 分类标签未使用状态色；
- [ ] 停用使用灰色；
- [ ] 红色只用于错误或危险确认；
- [ ] 状态同时包含文字。

**表格**

- [ ] 长文本不会无限换行；
- [ ] 操作列固定右侧；
- [ ] 状态列职责清晰；
- [ ] 固定列边界使用轻阴影；
- [ ] 分页总数正确；
- [ ] 空状态已区分。

**操作反馈**

- [ ] 单项失败未使用全局红条；
- [ ] 批量任务显示逐项进度；
- [ ] 外部操作经过真实确认；
- [ ] 危险操作有二次确认。

**架构**

- [ ] 已优先使用 TDesign 现成组件和属性；
- [ ] 已检查项目 Theme / Token 和共享组件；
- [ ] 页面没有重复实现公共按钮、表格、筛选和分页样式；
- [ ] 页面局部 CSS 只处理不可复用的业务布局；
- [ ] 未引入第二套 UI 组件库；
- [ ] 未复制 Cloud / Desktop 页面；
- [ ] 未在共享业务组件直接调用 Tauri；
- [ ] 未在页面散落硬编码颜色；
- [ ] 未重复创建仓库中已经存在的公共样式文件或组件；
- [ ] Cloud 与 Desktop 构建通过。

---

# 9. 规范维护

- 本文是项目级前端架构与视觉交互事实源；
- 新页面默认复用本文模板；
- 某个页面的具体按钮、字段和特殊交互必须放在独立页面案例或页面规格中；
- 只有多个页面出现稳定新模式时，才更新本文；
- 单页面临时样式不得直接升级为全局规范；
- 本文的目录与命令必须与仓库实测一致：路径、包管理器、构建命令、产物目录一旦在代码中改变，本文随之改写，不保留旧写法。

---

# 10. 最终定案表

| 问题 | 推荐定案 |
|---|---|
| Web 与 Desktop 前端 | 不做两套 |
| 前端代码 | 一套 Vue 业务前端 |
| 前端源码位置 | `wt-media-cloud/web` |
| Web 构建 | `npm run build:cloud` → `dist-cloud/` |
| Desktop 构建 | `npm run build:desktop` → `dist-desktop/` |
| Desktop 角色 | Tauri 壳、本地 Bridge、更新和系统能力 |
| Agent 角色 | Python 本地执行服务 |
| 多仓库联合构建 | `wt-media-workspace` |
| 版本锁定 | `config/release-matrix.yaml` + `scripts/release-versions.sh` 锁定版本事实 |
| UI 组件库 | TDesign Vue Next |
| 后台模板 | TDesign Starter，仅作为初始化骨架 |
| 图标 | TDesign Icons |
| 图表 | ECharts |
| 样式规范 | TDesign Token + 项目 Token |
| 第二套 UI 库 | 禁止引入 |
| 首版暗色模式 | 不做 |
| 页面体系 | 六类统一模板 |
| 强制交互 | 一页一主按钮、详情用抽屉、批量用固定操作栏 |

> **一句话总结**：当前系统应该建设成一套同时运行在浏览器和 Tauri 中的统一运营工作台。前端源码只保留一份，通过不同构建模式输出 Web 和 Desktop；视觉上只使用一套 UI 体系，并通过统一布局、状态、页面模板和 Design Token，解决当前页面风格混乱、重复开发和维护成本高的问题。
