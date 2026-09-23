# 症状 F「内容列只剩封面」——实测**未能复现**，原假设被证伪

> **⚠️ 本文结论已作废，勿据本文判断症状 F。**
> 作废时间：2026-09-23。取代者：`20260923-symptom-f-root-cause-measured.md`。
>
> 本文的「未复现」**不是**现象不存在，而是**量测引擎不对**：
> 本文全程用无头 Chrome，而 **Chrome 认 `minWidth`、WebKit 不认**。
> 真实根因是「只声明 `minWidth` 的列在 WebKit 的 fixed 布局下被压到远低于声明值」，
> 用户实机截图量测证实：内容列 340→91.5、来源列 260→100。
>
> 本文保留，作为「光靠 Chrome 模拟台会把真实 bug 判成不复现」的案例。

记录时间：2026-09-23
被测：`ContentPoolPage` 主表「内容」列（`#title` 槽：封面 + 标题 + `platform_content_id`）

## 结论先行

**假设 H1 被实测证伪，症状 F 在本模拟台下复现不出。按计划「复现不出 → 停下回报」，未据此改动任何布局代码。**

H1 原设想：列宽写死 `2060px` < 列宽下界合计 2378 → 表格被压到 2060 →
缺口从两列只有 `minWidth`（内容 340 / 来源 260）的列里扣 → `.title-copy`（`min-width:0` 且无 `flex-grow`）
被压到 0 → 只剩封面。

## 实测读数

模拟台：`tools/csp-probe-proxy.py --stub tools/stub-contentpool.json`
（**离线假数据模式，全程不接触任何凭据**），静态根分别为改前产物 `/tmp/wt055-before`
（`ContentPoolPage-DyS5ht54.js`）与改后产物（`ContentPoolPage-BiH7Bgcw.js`）。
CSP 原样取自 `tauri.conf.json`。

### 改前产物，逐窗口尺寸

| 窗口 | clientWidth | **滚动容器 scrollWidth** | 表头「内容」 | 「来源」 | `.title-copy` | 标题元素 | platform_id |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 900x700 | — | — | 340 | 260 | 222 | 222x22 | 222x22 |
| 1280x800 | 957 | **2378** | 340 | 260 | 222 | 222x22 | 222x22 |
| 1512x900 | 1189 | **2378** | 340 | 260 | 222 | 222x22 | 222x22 |
| 1920x1080 | 1597 | **2378** | 340 | 260 | 222 | 222x22 | 222x22 |
| 2560x1440 | 2237 | **2378** | 340 | 260 | 222 | 222x22 | 222x22 |

各 td 宽（全窗口一致）：
`[48, 80, 340, 110, 110, 140, 170, 110, 260, 170, 170, 170, 120, 120, 260]`

**关键反证一**：滚动容器 `scrollWidth` 实测 **2378**，不是 2060。
即写死的 `2060px` **从未生效**——TDesign 取的是列宽合计。H1 的前提（表格被压到 2060）不成立。

**关键反证二**：`.title-copy` 实测 **222px**（封面加载成功时为 224px），不是 0。
标题与 `platform_content_id` 都在，且宽高各 222x22，两个渲染分支都单行省略号正常。

**关键反证三**：窗口从 900 宽到 2560 宽，上述数字**一个都没变**——
「内容」列恒为 340（等于其 `minWidth`），因为表格恒在横向滚动，视口宽度不参与该列分配。
所以「窗口开大开小」也不是触发条件。

### 改后产物（1280x800 / 2560x1440）

时间列如期由 170 变 150，滚动容器 `scrollWidth` 2318；「内容」列仍 340、`.title-copy` 仍 224。
即：本轮列宽改动**没有改变**「内容」列的读数（本来就没被压）。

## 已排除的其他解释

| 猜因 | 检查方式 | 结果 |
| --- | --- | --- |
| 封面加载成功与否影响布局 | stub 封面由不可达 CDN 换成本源 1080x1440 真图 | 探针 `img.loaded=2 failed=0`；`.title-copy` 反而由 222 → 224（占位按钮 1px 边框之差）。**排除** |
| 只有 `<a>` 或只有 `<span>` 分支出问题 | stub 同时造了有 `source_url`（1001/1002）与无 `source_url`（1003）的行 | 两分支均正常单行省略。**排除** |
| `truncateTitle` 把标题吞掉 | 读实现 `ContentPoolPage.vue:440` | `String(title \|\| '')`，且模板有 `\|\| '未命名内容'` 兜底，**不可能空**。排除 |
| 列表接口没返回这两个字段 | 读 `dto.go` / `model.go` / `store_mysql.go` | 列表返回 `model.SourceContent`，含 `title` 与 `platform_content_id`。**排除** |

## 尚未排除（**需要用户指认**）

本模拟台能把「窗口尺寸、封面是否加载、标题长度、两个渲染分支、CSP」都覆盖到，
**唯一无法复制的是真实数据本身**——以及用户实际看的到底是不是这张表。
剩下的可能：

1. **不是主表**：用户看到的可能是详情抽屉 `detail-workspace`、审核模式卡片，
   或「发现内容」结果表（那张表首列叫 `标题`，`minWidth: 280`）。本记录只量了主表。
2. **真实数据形态**：某些行的 `title` / `platform_content_id` 在库里就是空串
   （那行会显示「未命名内容」，`platform_content_id` 处为空白）。
3. 用户看到的产物与本记录的改前产物不是同一份。

**因此未按 H1 改任何布局代码。** `tableScroll` 推导仍然保留，但理由已更正为
「消除一个写了但不生效、且不随列宽变化的漂移源」，**不是**修 F（见
`ContentPoolPage.vue` 与 `ContentPoolPage.test.js` 内的说明）。

## 复现命令

```bash
cd delivery/active/CHG-20260923-055/evidence/tools
bash measure-stub.sh /tmp/wt055-before /tmp/wt055-m before 1280x800 1512x900 1920x1080 2560x1440
bash measure-stub.sh /tmp/wt055-after  /tmp/wt055-m after  1280x800 2560x1440
```

`/tmp/wt055-before` = 改前 `dist-desktop` 快照；`/tmp/wt055-after` = 改后 `dist-desktop` 快照
（两者都补一份 `index.html`，因为打包产物入口名是 `index.desktop.html`）。
