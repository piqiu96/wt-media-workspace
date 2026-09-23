# CHG-20260923-055：Desktop 内容池封面加载与标题换行修复

- Status: ACTIVE
- Level: S
- Milestone: `delivery/milestones/M3-content-discovery-v2.md`
- 日期：2026-09-23
- 基线：`docs/product/M3-content-mining-v2.md`；ADR-0013、ADR-0015
- 当前仓库：`wt-media-desktop`（CSP 与原生外壳）+ `wt-media-cloud`（Web 前端）；治理记录在本仓。
- 来源：`delivery/completed/CHG-20260916-052/`（M3 E3 综合验收）之后，**由用户在生产形态的 DMG 原生应用上直接报出**。

## 独立目标与范围

用户从 DMG 原生应用报出内容池两处呈现问题，并追问「desktop 和 web 是同一套视觉，为啥差别会这么大」：

1. 当前内容池前端风格错乱；
2. 封面图片无法正常加载。

本 CHG 的独立目标是**回答这一问并修掉被证实的根因**。两处现象经实测归结为**两条互相独立的根因**：
一条 Desktop 独有（CSP 未放行图片），一条两端共有（标题省略号规则漏了渲染分支）。
「两端视觉是不是同一套」本身也被独立证否/证实，见 `evidence/20260923-fix-and-verification.md` 第一节。

不含于本 CHG：不新增 Cloud 图片代理端点、不精简内容池列集、不动 `scroll.x`、
不标 M3 DONE、不修 CHG-054 已登记的 D1～D10/S-1。

## 根因与修法

| # | 根因 | 证否/证实 | 修法 | 仓库 |
| --- | --- | --- | --- | --- |
| A | `tauri.conf.json` 的 CSP **无 `img-src`** → 回落 `default-src 'self'` = `tauri://localhost`；封面是未经代理的抖音 CDN 绝对地址，WKWebView 在发请求前即拦掉 | **证实**：在**带真实 CSP** 的模拟台上，修前 `img.loaded=0 / failed=20` | CSP 追加 `img-src 'self' https:`；另加 `@error` 兜底，覆盖防盗链/404/换域名等 CSP 管不到的失败形态 | `wt-media-desktop`、`wt-media-cloud` |
| B | `scroll.x: '2060px'` 小于列宽下界 2378，导致右侧固定「操作」列错位压住「来源」列 | **证否**（原先是我方推断）：固定列是 `position: sticky`，与 `scroll.x` 无关；修前修后在 `scrollLeft=0` 与最大 `1189` 两处测得固定列 `[1207,1467]` 与内容层右边缘逐像素对齐 | **不改**。`scroll.x` 与断言该字面量的测试均保持原状 | — |
| C | 标题省略号规则只写 `.title-copy span`，而「有 `source_url`」的行渲染成 `<a class="wt-primary-link">` → 该分支整段自由折行，把行高从声明值撑到 153px | **证实**：修前 `<a>` 计算样式 `white-space: normal / text-overflow: clip`、高 66px（3 行），行高实测 `[109,87,153,153,131,109,131,87]` | 选择器补 `>` 且覆盖 `<a>`；`color` 只留在 `span` 分支，不覆盖链接主题色 | `wt-media-cloud` |
| D | Rust 侧用 `window.eval` 注入的报错转发**从未生效**（CSP `script-src` 回落 `'self'` 且无 `'unsafe-eval'`），原生端因此一行 JS 报错都看不到 | **证实**：删掉注入后原生端无任何 `[WEBVIEW]` 输出；该注入在修前也无法工作 | 删掉 eval 注入，改由前端入口注册 `error`/`unhandledrejection`/`console` 转发，经既有 `log_js_error` 落 stdout。**不给 CSP 加 `'unsafe-eval'`** | `wt-media-desktop`、`wt-media-cloud` |

### 行高的真实构成（修正推断）

修后行高**统一 85px**（此前 87～153 不等）。逐件实测：
`85 = td padding 8 + max(内容格 64, 来源格 68) + td padding 8 + 边框 1`。
**驱动者是「来源」列而非标题列**——来源格 68 = 链接 22 + gap 2 + `<small>` 44（长标识符折成 2 行）。
`resource-module.css` 的 `tr { height: 56px }` 对本表**本来就不可达**：88×56 的封面加 16px 单元格内边距
已经给出 80px 下界。这是既有基线，不是本次引入，故不改；行高现已由内容稳定决定，视觉一致。

## 验收口径

- 用户在 DMG 原生应用上**亲眼确认**（本机无屏幕录制权限，我方无法抓原生窗口）。
- 自动化口径见 `evidence/20260923-fix-and-verification.md`：带真实 CSP 的模拟台 + 注入探针的量化断言。

## 证据纪律回写（本次最重要的一条）

`CHG-20260916-052` 的走查把验收项 7 判为通过，而根因 C **就在那份走查自己的截图里**：
`evidence/m3-e3-acceptance-20260923/screenshots/01-content-pool.png` 中标题占 2～3 行、行高参差。
根因 A 则**结构性地**不可见——该走查的代理**未附加应用 CSP**，所以图片在走查里全部正常加载，
只在真实应用里失败。两者性质不同：A 是覆盖缺口，C 是**判读失误**。
已据此收窄 `16-desktop-walkthrough.md` 第七节的覆盖声明，详见该文与本节证据文档。

## 明确不做

- 不给 CSP 加 `'unsafe-eval'`；不新增 Cloud 图片代理端点（裁定用 `https:` 通配）。
- 不动 `scroll.x`（根因 B 已证否）；不精简列集（用户裁定「列集不动」）。
- 不改 `config/credentials/douyin.toml`；S-1 原样登记在 CHG-054，本 CHG 不处置。
- 不标 M3 DONE（签收属用户）；不激活 `CHG-20260915-051`；不碰 `CHG-20260923-053`。
