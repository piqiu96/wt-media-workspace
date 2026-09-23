# Desktop 内容池：根因定位与修复验证

日期：2026-09-23　变更：CHG-20260923-055　现场：DMG 原生应用（用户直接报出）

用户报出两件事并追问一句：

> 1、当前内容池的前端风格都是错乱的　2、对于图片也无法正常加载
> 按理 desktop 和 web 是同一套视觉，为啥差别会这么大

那句追问是本次诊断的入口。结论是：**两端确实是同一套视觉，不存在设计分叉**；
观感差异来自**渲染环境**（Desktop 有 CSP、Web 没有）加**一个两端共有的页面级 CSS bug**。

---

## 一、先回答问题：两端是不是同一套视觉

是。四条独立证据，均在 2026-09-23 本次修复后**当场重新测得**（方法可复现）：

| 证据 | 结果 |
| --- | --- |
| 两个入口的样式导入 | **同样四行**：`tdesign-vue-next/es/style/index.css`、`shared/styles/layout.css`、`styles/design-token.css`、`shared/styles/resource-module.css` |
| 根组件 `src/App.vue` vs `apps/desktop/App.vue` | md5 同为 `8af37b4ca96906787c0ad30c2195a7e1`（逐字节相同） |
| 全量样式表 `index-o03HRtYg.css` | `dist/` 与 `dist-desktop/` 中 md5 同为 `c3a58f230f1813b05f9a521a9ac6c196`，451756 B |
| 其余共用组件样式 | `AppLayout--xe_KbYD.css`、`ResourceStatGrid`、`ResourceStatusBadge`、`LoginPage`、`CrawlTasksPage`、`DiscoveryStrategiesPage` 等 md5 两端**全部相同** |

两端**不相同**的只有各自独有的页面：Desktop 多 `AgentStatusPage`，
`ContentPoolPage` 因本次修复而不同（`dist/` 7252 B vs `dist-desktop/` 7317 B，即修复本身）。

所以「差别这么大」不可能来自样式表——它只能是**同一份样式在两个环境里被不同地执行/解释**。
已定位到两条根因，一条 Desktop 独有，一条两端共有。

---

## 二、根因 A：CSP 未放行图片（Desktop 独有）

`wt-media-desktop/src-tauri/tauri.conf.json` 的 CSP 原文：

```
default-src 'self'; connect-src 'self' http://127.0.0.1:18080; style-src 'self' 'unsafe-inline'
```

**没有 `img-src`**，于是回落到 `default-src 'self'`。macOS 下 Tauri 页面 origin 是
`tauri://localhost`，而内容池封面是**未经任何代理的抖音 CDN 绝对地址**
（`internal/modules/contentpool/service/discovery_crawler.go` 直接透传，Cloud 没有任何图片路由）：

```
https://p11-sign.douyinpic.com/tos-cn-p-0015/ocdlEQgqDEXKK1UqAkArIXIyfvAyEBACeD99sF~tplv-...
```

`https://p11-sign.douyinpic.com` ≠ `'self'` → **WKWebView 在请求发出前就拦掉**。
Tauri 自身只给 `script-src`/`style-src` 补 nonce，**从不补 `img-src`**，所以这个缺口不会被 Tauri 兜住。
Web 端是普通浏览器、根本没有 CSP，图片照常加载——**这就是两端观感差距的最大来源**。

叠加放大：三个 `img` 都没有 `@error` 兜底，被拦后不退化到既有的「暂无封面」占位，而是每行留一个破图空框。

### 量化（在带真实 CSP 的模拟台上测）

| | 修前 | 修后 |
| --- | --- | --- |
| `img.total` | 20 | 20 |
| `img.loaded` | **0** | **20** |
| `img.failed` | **20** | **0** |

截图：`screenshots/before-03-csp-1512-rowdetail.png`（每行破图）→ `screenshots/after-03-csp-1512-rowdetail.png`（封面正常）。

### 修法

1. CSP 追加 `img-src 'self' https:`（用户裁定：放开通配，不新增 Cloud 图片代理端点）。
2. 三处封面加 `@error` 兜底，加载失败退化为「暂无封面」。
   **CSP 与兜底都要有**——CSP 修不了上游防盗链、404、换域名等其余失败形态。

---

## 三、根因 B：一个被证否的推断（保留过程）

**我方原先的推断**：`ContentPoolPage.vue` 的 `:scroll="{ x: '2060px' }"` 小于列宽下界 2378，
会让右侧固定「操作」列按错误右边界定位、压住「来源」列——与用户截图观感相符。

**实测证否。** 三条：

1. 固定列在 TDesign 1.20.3 里渲染为**真实单元格上的 `position: sticky`**
   （class `t-table__cell--fixed-right`），定位**不依赖 `scroll.x`**。
2. 内层 `<table>` 实测宽度恰为 **2378px**（列宽下界之和），说明 `scroll.x` 只是被忽略，并非生效中的小值。
   原因是 `table-layout: fixed` 下内层表宽取 `max(scroll.x, 列宽和)`。
3. 在两个滚动极点各测一次，固定列与内容层**逐像素对齐**：

| 滚动位置 | 固定表头 / 固定单元格 | 内容层右边缘 |
| --- | --- | --- |
| `scrollLeft=0` | `left=1207 right=1467` | `right=1467` |
| `scrollLeft=1189`（最大） | `left=1207 right=1467` | `right=1467` |

且固定列单元格高度与行高**逐行相同**（`[85,85,85,85,…]` 两边一致），不存在纵向错位。

**处置：不改。** `scroll.x` 与断言该字面量的既有测试都保持原状
（断言字面量确实不好，但本轮裁定「列集不动」，且根因不成立时不应顺手改）。

---

## 四、根因 C：标题省略号漏了渲染分支（两端共有）

内容池「内容」列有**两个渲染分支**：有 `source_url` 时渲染 `<a class="wt-primary-link">`，
否则渲染 `<span>`。而省略号规则只写了 `.title-copy span`，**`<a>` 分支完全没被覆盖**。

于是有外链的行整段自由折行，把行高从声明值撑到三倍。

### 量化

| | 修前 | 修后 |
| --- | --- | --- |
| 前 8 行行高 | `[109, 87, 153, 153, 131, 109, 131, 87]` | `[85, 85, 85, 85, 85, 85, 85, 85]` |
| 标题 `<a>` 高 | **66px**（3 行） | **22px**（1 行） |
| `white-space` | `normal` | `nowrap` |
| `text-overflow` | `clip` | `ellipsis` |

`truncateTitle(max=80)` 帮不上忙：标题 44 字未触发截断，但该列可用宽度只有 224px。
整行 15 个 `td` 高度相同，证明是「内容」列单独驱动行高。

### 修法

```css
/* 标题有两种渲染分支：有 source_url 时是 <a class="wt-primary-link">，否则是 <span>。
   省略号必须同时覆盖两者——只写 span 时，有外链的行会整段自由折行。 */
.title-copy > a,
.title-copy > span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.title-copy > span { color: var(--wt-text-primary); font-weight: 600; }
```

`color` 刻意只留在 `span` 分支，避免覆盖 `.wt-primary-link` 自身的主题色。

---

## 五、行高的真实构成（把推断改正）

修后行高统一 **85px**。逐件实测拆解：

```
85 = td padding 8 + max(内容格 64, 来源格 68) + td padding 8 + 边框 1
```

- 「内容」格 = 64px（其 `min-height: 64px`；内含 88×56 封面，`box-sizing` 实测为 `border-box`）。
- 「来源」格 = 68px = 链接 22 + gap 2 + `<small>` 44（服务端拼的 `strategy_name + '_' + 14 位时间戳`
  在 260px 列里折成 2 行；`overflow-wrap: break-word` 实测生效）。

**所以驱动行高的是「来源」列，不是标题列。** 我此前关于「无全局 `box-sizing` 导致 56/58/64 冲突」
的说法也**是错的**：TDesign 全局设了 `border-box`，封面实测就是干净的 88×56。

`resource-module.css` 的 `tr { height: 56px }` 对本表**本来就不可达**：88×56 封面加 16px 单元格内边距
已给出 80px 下界。这是既有基线、非本次引入。修后行高由内容稳定决定，视觉一致，**故不改为 56**。

**未采纳的改法及理由**：给「来源」列加 `ellipsis` 可把行高降到 81px 左右，但「来源」值区分度在**末尾的时间戳**，
省略号恰好会把唯一能区分同策略各行的那一段藏掉。保持折行是更好的取舍。

---

## 六、根因 D：原生端报错转发从未生效

`main.rs` 的 `.setup()` 里有一段标着 `Temporary diagnostics` 的 `window.eval(...)` 注入，
把 WebView 内的 `error` / `console.error` 转发给 Rust 的 `log_js_error`。

但应用 CSP 的 `script-src` 回落到 `default-src 'self'` 且**不含 `'unsafe-eval'`**，
`window.eval` 会被 WebView 直接拒绝——**这段注入从未生效过**，原生端因此一行 JS 报错都看不到。

**修法**：删掉 eval 注入；改由前端入口（`src/apps/desktop/webviewErrors.js`）在 `main.ts` 最前注册
`error` / `unhandledrejection` / `console.error|warn` 转发，经既有 `log_js_error` 落 stdout。
前端入口本身就是 `'self'` 加载的脚本，不受 `script-src` 限制。
**不给 CSP 加 `'unsafe-eval'`**——那是拿安全边界换日志。

顺带：`use tauri::{Manager, State}` 里的 `Manager` 只被删掉的那段用到，已改为 `use tauri::State`，
否则留下 unused import 警告（`cargo check --all-targets` 已确认修复后无此警告）。

---

## 七、验证方法与覆盖范围（逐输入形态枚举）

### 7.1 为什么需要一个新的验证台

首轮 Desktop 走查用的是 `desktop-walkthrough-proxy.py`，它**不附加应用 CSP**。
在没有 CSP 的环境里，根因 A **结构性地不可能被观测到**——图片在走查里全部正常加载，
只在真实应用里失败。因此新增 `tools/csp-probe-proxy.py`：在 5174 上服务打包产物时
**原样附加 `tauri.conf.json` 里那条 CSP 响应头**，并代理 `/api` 到 18080。
这是能在无头浏览器里复现「原生端被 CSP 拦截」的唯一办法。

配套 `tools/capture.sh`（逐视口取图，单张硬超时兜底）与 `tools/run-capture.sh`
（登录 → 起台 → 抓图 → 收台，原子完成）。运营会话 cookie 存活窗口实测约 10 分钟，
分步操作会抓到登录页——这正是本次诊断早期拿到 18KB「内容池截图」假象的来源，故必须原子化。

### 7.2 逐项覆盖

| 输入形态 / 断言 | 是否覆盖 | 证据 |
| --- | --- | --- |
| 封面：正常可加载的上游 URL | 覆盖 | 修后 `loaded=20/failed=0` |
| 封面：被 CSP 拦截 | 覆盖（修前即此形态） | 修前 `failed=20` |
| 封面：404 / 防盗链 / 换域名等其余失败形态 | **未覆盖** | 仅由 `@error` 兜底逻辑与单元测试断言，未构造真实失败上游 |
| 标题：有 `source_url`（`<a>` 分支） | 覆盖 | `<a>` 高 66→22px，`nowrap`/`ellipsis` |
| 标题：无 `source_url`（`<span>` 分支） | **部分** | 断言规则同时匹配两分支；实拍样本里出现的是 `<a>` 分支 |
| 行高一致性 | 覆盖 | 前 8 行 `[85]×8`，固定列与行高逐行相同 |
| 固定列水平对齐 | 覆盖 | `scrollLeft=0` 与 `=1189` 两处均 `right=1467`，与内容层对齐 |
| 视口 1280×800（DMG 默认窗口） | 覆盖 | `after-01-csp-1280x800.png` |
| 视口 1512×900 | 覆盖 | `after-02`/`after-03` |
| 视口 1280 以下 / 其他缩放比 | **未覆盖** | 未测 |
| 原生 Tauri 窗口本体 | **未覆盖** | 本机无屏幕录制权限，`screencapture` 抓不了原生窗口；只能由用户确认 |
| 表格之外的其余内容池交互 | **未覆盖** | 本 CHG 只针对报出的两个现象 |
| 其余页面（策略、任务、素材库） | **未覆盖** | 本次未复测；根因 C 的选择器只存在于内容池页面 |

### 7.3 复现步骤

```
cd /Users/aqiuye/Develop/workspace/wt-media
WT055_PASSWORD=<运营账号密码> bash \
  wt-media-workspace/delivery/completed/CHG-20260923-055/evidence/tools/run-capture.sh \
  <输出目录> "after-01-csp-1280x800:1280x800" \
             "after-02-csp-1512x900-scrolled-right:1512x900:right" \
             "after-03-csp-1512-rowdetail:1512x900:rowdetail"
```

前提：Cloud 在 18080、`.generated/frontend` 已由 `scripts/build-desktop.sh` 构建。
探针只在 URL 带 `#probe=<标签>` 时动作，测得的 JSON 由代理打印为一行 `PROBE <标签> <json>`。

---

## 八、证据纪律回写（本次最重要的一条）

`CHG-20260916-052` 的 `16-desktop-walkthrough.md` 把验收项 7 判为通过。但：

1. **根因 C 就在那份走查自己的截图里。**
   `evidence/m3-e3-acceptance-20260923/screenshots/01-content-pool.png` 中，
   标题占 2～3 行、行高明显参差（与修前实测的 `[109,87,153,153,131,109,131,87]` 吻合）。
   该走查仍判为通过——这不是覆盖缺口，是**判读失误**。
2. **根因 A 是真正的覆盖缺口。** 走查的代理未附加 CSP，图片在走查里全部正常加载，
   结构性地不可能发现「真实应用里被拦」。
3. 该走查第七节原文写「只在 `1280×800` 下取图」，确实未覆盖更宽视口；
   但 1280×800 下受影响的列（来源、发布时间等）**是被右侧固定列遮住**，而非未渲染。

已据此收窄 `16-desktop-walkthrough.md` 第七节的覆盖声明。**M3 本身不因本次修复而改判**：
E3 验收结论不变，M3 仍 `IN_PROGRESS`，签收仍属用户。

---

## 九、残留与安全

**残留（本轮未做）**：

- 原生 Tauri 窗口的视觉确认仍待用户完成（无屏幕录制权限）。
- 封面在 404/防盗链/换域名下的表现只有 `@error` 兜底逻辑，无真实失败上游的端到端取证。
- 无 `source_url` 的 `<span>` 标题分支缺真实样本实拍（规则与单元测试已覆盖）。
- 「互动」列在 1280×800 下被右侧固定列遮住右半（15 列宽于可视区），需横向滚动才能看全。
  这是列集与视口宽度的固有结果，非本次引入；本轮裁定「列集不动」，故不改。
- 「来源」列长标识符折成 2 行使行高为 85 而非 81（取舍理由见第五节）。

**安全**：

- 证据目录不含任何凭据值。本机抖音凭据（`config/credentials/douyin.toml`）**未被读取、修改或引用**。
- 会话 cookie 仅存在于代理进程内存与一个 **0600 的临时文件 `/tmp/.wt055session`**（位于仓库之外），
  收台脚本已删除该文件。**不声称「从未落盘」**——它确实短暂落过盘，权限 0600、路径在 `/tmp`、已删除。
- 以真实凭据值（`douyin.toml` 中 3 个长度 35/6975/16 的取值，共 12 个子串）反查证据目录 14 个文件：
  **0 命中**。按 `wt_media_session=<值>` 形态反查：**0 命中**。
  （注：首轮反查曾因只匹配双引号而**空转**——该文件用单引号，那次「0 命中」什么都没测到；已改正后重测。）
- 证据里出现的 `operator01` 是本机验收用**账号名**（同时出现在界面截图中），非凭据。
- cloud 目录下的凭据文件路径**未**登记进证据；S-1（抖音凭据被 git 跟踪）按用户裁定
  原样留在 CHG-054，本 CHG 不处置、未改动 `.gitignore`、未轮换、未重写历史。
