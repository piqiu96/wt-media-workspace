# 任务 10 证据：走查五轮（状态维度、详情框、抽屉页脚）

- 日期：2026-09-30
- CHG：CHG-20260930-069（M4-A 素材详情与下载中心走查修正）
- 仓库：`wt-media-cloud`（前端）；工作区文档在本仓
- 提交：`27f74b3`（`feat(chg-069): 状态维度、详情框与抽屉页脚（走查五轮）`）

## 0. 用户反馈原文（四条）

1. 列表应该有素材状态、文件状态、使用情况；
2. 详情里底部的确认取消应该不存在；
3. 对于按钮切 tab 后的按钮应该放在底部统一；
4. 详情里的展示框效果远不如预期。

用户对澄清问题的裁定：

- 列表新列：「先把样式定了，除了以来（依赖）外部数据可只保留展现样式和协议，数据等打通以后再进行同步过来」；
- 详情展示框：「参考内容池的详情的框，其次我提供了图片给你」；
- 同类抽屉：「一起修，并加全站守卫测试（推荐）」。

## 1. 前置盘点：设计图与「远不如预期」的所指

**设计图找回。** 走查四轮的设计图是上一轮对话里的附件，压缩后已不在上下文里，
磁盘上也没有（`reference/` 只有 `state-models/*.md`）。它在会话记录里以 base64 存在，
本次从中取出（`/private/tmp/wt-design-308973.jpeg`，308,973 字节，image/jpeg），
据此逐条核对，不再凭印象。

图中与四条反馈直接相关的判据：

| 反馈 | 设计图上的对应 |
| --- | --- |
| ① 三列 | 列头为「素材 \| 游戏 \| 素材状态 ⓘ \| 文件状态 ⓘ \| 使用情况 ⓘ \| 入库时间 ↓ \| 操作」；使用情况两行（`成片 12 · 发布 8` / `最近发布 2025/9/20`）；素材状态徽章三态（可用/已暂停/已下架） |
| ② 无确认取消 | 详情页脚只有「关闭」与一颗主操作 |
| ③ 按钮统一在底部 | 同上，页脚是一条独立的横条 |
| ④ 详情框 | 每段信息是一张有边界的卡：概览 = 使用情况（成片/发布/最近生产/最近发布/重复风险）+ 基本信息（素材 ID/游戏/入库时间）；文件信息、来源信息各一张；来源内容池统计一张；顶部是封面 + 标题 + 「游戏 · 平台 · 作者」副行 + 三枚徽章 |

图下方的「优化要点总结」是这张图的文字版，其中：
- ① 明确「素材状态：可用 / 已暂停 / 已下架」「文件状态：未准备 / 准备中 / 可下载 / 准备失败」「使用状态：是否已加入我的素材」；
- ④ 明确「暂停/下架时不允许新增加入」；
- ⑤ 明确「将「已退役」改为「已下架」「详情底部不再使用「确认/取消」改为统一的关闭和主操作按钮」。

设计图里 素材 格的副行写的是「douyin · 三角洲行动」（平台 · 游戏），而 游戏 另有独立列；
该处偏差已在 `change.md` §4 登记待用户裁定，本轮不改动。

## 2. 第 2 条：根因不是本仓代码

**命令**：读 `node_modules/tdesign-vue-next/es/drawer/{props.mjs,drawer.mjs}`。

**实测事实**：

- `props.mjs:39-42`：`footer: { type: [Boolean, Function], "default": true }`；
- `drawer.mjs:209-223`：`getDefaultFooter()` 用全局配置造出取消 / 确认两颗按钮；
- `drawer.mjs:371`：`props2.footer && createVNode("div", {class: "...__footer"}, [renderTNodeJSX("footer", defaultFooter)])`。

**结论**：用户看到的「取消 / 确认」不是本仓任何一行写的，是组件库在 `footer` 缺省时注入的。
`MaterialDetailDrawer.test.js` 原有的 `expect(template).not.toContain('>取消</t-button>')`
因此一直为绿——**源码字符串断言看不见一个由组件库注入的默认页脚**。这条不是走查四轮引入的
回归：`git show HEAD:web/src/modules/materials/MaterialDetailDrawer.vue` 里从抽屉创建那天
起就没有 `footer` 属性。

## 3. 全站抽屉盘点（用户裁定「一起修 + 加守卫测试」）

第一遍盘点用「开标签后 4 行内找 `#footer`」的窗口扫描，报出 4 个漏写。**这个读数是错的**：
`<t-drawer>` 的开标签会跨行，属性写在 4 行之外。改用按引号配对取完整开标签 + 取到
`</t-drawer>` 的块内找 `#footer` 插槽后：

**分母**：12 个抽屉，分布在 8 个文件（materials 1、contentpool 3、profiles 2、proxy 1、
accounts 1、transfer 1、users 1、shared 模板 1）。

**漏写 2 个**：

| 文件 | 行为 |
| --- | --- |
| `web/src/modules/proxy/pages/ProxyPage.vue:496` | 详情抽屉，无 `footer` 属性、无 `#footer` 插槽 → 底部必然长出一对取消/确认。已加 `:footer="false"` |
| `web/src/shared/ui/templates/DetailDrawerPage.vue:15` | 同上。该文件无引用（用 `web/src/**` 全量 grep 核对），仍一并修，避免下一个人照抄 |

`ProfilesPage.vue:1185` 一度被判为漏写，实为假阳性：它的 `#footer` 插槽在文件更靠下的位置。
改正后的扫描结果与新守卫测试的红输出完全一致（同一份 2 个文件名与行号）。

**守卫测试**：`web/src/drawerFooterConvention.test.js`。两条断言——先钉分母（≥12 个抽屉、
≥8 个文件），再要求每个抽屉「给 `#footer` 插槽或显式写 `footer` 属性」。只扫 `t-drawer`：
`t-dialog` 有同样的默认值，但确认对话框要的**正是**那对取消/确认，一并扫会造出一堆假阳性。

- 红：`Tests 1 failed | 1 passed (2)`，失败信息为
  `["modules/proxy/pages/ProxyPage.vue:496", "shared/ui/templates/DetailDrawerPage.vue:15"]`。
- 修完两处后：`Tests 2 passed (2)`。

## 4. 测试先行（红）

先改 5 个测试文件、新增 2 个，钉住目标形态。

**命令**：`npx vitest run src/modules/materials src/shared/utils/datetime.test.js`

**期望**：新增与改写的断言语义上应当红，既有断言不得被破坏。

**实际**：

```text
Test Files  4 failed | 3 passed (7)
     Tests  19 failed | 48 passed (67)
```

19 条全落在本轮新增/改写的断言上（`labels.test.js` 9 条、`MaterialDetailDrawer.test.js` 5 条、
`MaterialLibraryPage.test.js` 3 条、`datetime.test.js` 2 条），既有断言无一变红。

> 说明覆盖面：`labels.js` 的新导出是**新代码**，它在实现前的不存在只会让模块拿到 `undefined`，
> 这类红本身证明不了调用点接好了没有。真正证明接线的是同一批里的源码断言
> （`source).toContain('usageLines(row)')`、`materialStatusLabel(row.status)` 等），
> 它们在实现前同样是红的，因为那些字符串此前根本不在文件里。

## 5. 实现后（绿）

**命令**：同 §4。

**实际**：`Test Files 7 passed (7)` / `Tests 68 passed (68)`。

全量：

**命令**：`npx vitest run`

**实际**：

```text
Test Files  1 failed | 44 passed (45)
     Tests  1 failed | 364 passed (365)
```

唯一失败是 `src/localSettingsWiring.test.js`（`expected 20 to be greater than 20`），
**与本 CHG 无关**，根因已定位：HEAD 的 `web/src/apps/desktop/router.ts:19,26` 有
`execute-tasks → TasksPage.vue` 一条路由，工作区把它删了（`TasksPage.vue` 与
`shared/api/tasks.js` 同时处于删除状态），可数的 loader 从 21 掉到 20，撞上 `>20` 的阈值。
这两处删除都是本 CHG 之前就在工作区的脏改动，按 `change.md` §6 保持原样、不随本 CHG 提交。
**更正**：该删除后来按「单仓任务」独立提交（`029ae3a` / `5c3a5fa`），测试下限改为实测的 20，
全量复绿（45 文件 / 369 用例）；「既有失败」这个说法也随之作废——它一直是同一处脏改动，
不是仓库里的独立缺陷。详见 `checkpoint.md` 的范围外备注。

## 6. 实现要点

**协议与文案**（`web/src/modules/materials/labels.js`）：

- `MATERIAL_STATUSES = ['available','paused','delisted']` → 可用 / 已暂停 / 已下架；
- `USAGE_FIELDS = ['clip_count','published_count','last_produced_at','last_published_at','duplicate_risk']`；
- `usageLines(material)` → 列表两行；`usageFacts(material)` → 详情五格；`duplicateRiskLabel/Tone`；
- **缺值渲染占位，不兜底**：`materialStatusLabel(undefined)` 是 `-` 而不是 `可用`，
  `usageLines({})` 是 `成片 - · 发布 -` 而不是 `0`。`0` 与「没有值」分开——前者是「一条成片都没生产」，
  后者是「这个字段还没来」。

**列表**（`MaterialLibraryPage.vue`）：

- 列集合 6 → 8：`素材 ID | 素材 | 游戏 | 素材状态 | 文件状态 | 使用情况 | 入库时间 | 操作`，
  每一列显式 `width`（WebKit fixed 布局，理由见 `shared/testing/listPageConventions.js`）；
- 操作列加 `canAdd(row)` 门：`未领取 + 非可用` 不提供主操作，画 `—`；已领取的行任何状态仍给
  「去我的素材」。**字段未到达时 `canAdd` 恒为真、不改变现有行为**——这一点在代码注释里写明了，
  同时写明服务端此刻并不兜底：`POST /materials/:id/usages` 在
  `internal/modules/production/repository/store_mysql.go:159` 是一次无状态校验的 upsert，
  它拦不住一条已下架的素材。服务端那一半要等第五章落下 `status`。

**详情**（`MaterialDetailDrawer.vue`）：

- 顶部 hero：封面 160×100 + 标题 + 「游戏 · 平台 · 作者」副行 + 素材状态/文件状态/加入状态三枚徽章
  （素材状态缺值时不画徽章）；
- 正文五张 `.detail-card`（有边界、圆角 10px）：概览 = 使用情况 + 基本信息；文件信息卡标题带文件状态徽章；
  来源信息 = 来源信息 + 来源内容池统计（从概览移入——它是来源行的快照，跟着来源走）；
- 动作条**接管 `#footer` 插槽**，同时解决反馈 ② 与 ③：消掉组件库默认页脚，并让它钉在抽屉底部
  不随标签内容高度移动。左「关闭」右上下文主操作。

**样式**（`shared/utils/datetime.js` 与抽屉 CSS）：

- 新增 `formatDate`：只要日期。「最近发布 2025/9/20」这一格若带时刻会比它右边的「入库时间」还宽；
- 顺手修掉一处自己写出来的 CSS bug：使用情况那格原本写成 `.detail-usage__item > span`，
  而重复风险那一行的第一行是 `ResourceStatusBadge`，它的根元素也是 `span` 且会带上父组件的
  scoped 属性——后代选择器会把徽章一起染成次要色，绿色「正常」会变成灰的。
  改成给标签挂 `.detail-usage__label` 类名。

## 7. 文档回写

- `docs/standards/前端交互规范.md` §7.2：文件状态示例词由「未下载 / 下载中 / 已下载 / 下载失败」
  改为「未准备 / 准备中 / 可下载 / 准备失败」，并补用词说明（这一档说的是**云端源文件准备好了没有**，
  不是本机下载进度；`video_status` 契约取值不变）。这是走查四轮起就登记在 `checkpoint.md`
  「待用户裁定」里的不一致，设计图「文案优化」条给出了答案。
- 同文件 §16.2：操作矩阵补第四行「已暂停 / 已下架 + 已领取 → 详情 | 去我的素材」。
  原文只有「已暂停 / 已下架 → 详情」，与已定稿的实现（已领取的行任何状态都保留「去我的素材」）
  冲突；「历史关系和结果继续保留」那句话本身就说明了禁止的是**新增**，不是导航。

## 8. 构建与产物核对

**命令**：`npm run build:cloud` / `npm run build:desktop`（`wt-media-cloud/web`）

**期望**：两条都成功，且产物里真的带上新文案。

**实际**：`build:cloud` ✓ built in 6.51s；`build:desktop` ✓ built in 6.40s，均 exit 0
（各自只有 >500 kB chunk 的既有告警）。

产物字符串核对（`dist-desktop/assets`，按文件而非按单文件）：

| 串 | 命中文件数 | 文件 |
| --- | --- | --- |
| 素材状态 | 1 | `MaterialLibraryPage-*.js` |
| 使用情况 | 2 | `MaterialLibraryPage-*.js`、`MaterialDetailDrawer-*.js` |
| 成片（`已生产成片`） | 2 | `MaterialDetailDrawer-*.js`（另 1 个命中在 `local-settings-view` 的无关文案里） |
| 最近发布 | 1 | `MaterialDetailDrawer-*.js` |
| 疑似重复 | 1 | `MaterialDetailDrawer-*.js` |
| 已下架 | 1 | `MaterialDetailDrawer-*.js` |

对照：

- 阴性对照 `ZZZnotpresentZZZ`：命中 0（证明这个 grep 在这批产物上会失败，不是空转）；
- 源码注释串「详情里的展示框」：命中 0（压缩把注释剥掉了——这同时说明上面那些命中来自**活着的字符串**，
  而不是某个保留注释的意外产物）。

## 9. 环境重建（供用户走查）

**命令**：`./scripts/m2b-local-acceptance.sh all --force-restart`

**前置**：先确认比特浏览器在 54345 上监听（本机不自启，`all` 的第一道门就是它，不先起会白起一遍
Cloud/Agent 再中止）。

**实际**：**exit 0，六道门一次全 PASS**（这次没有复现上轮那个单发 3s 无重试的 BitBrowser 假 FAIL）。

```text
Cloud: PASS http://127.0.0.1:18080/api/v1/health
Agent: PASS http://127.0.0.1:8765/healthz
BitBrowser via Agent: PASS
Desktop assets: fresh / PASS
DMG: fresh / PASS  WT Media_0.1.0_aarch64.dmg
Login smoke: PASS user=admin
[exited with code 0]
```

产物核对：

- `wt-media-desktop/.generated/frontend/assets/MaterialLibraryPage-DhZ_QhYt.js` 与
  `wt-media-cloud/web/dist-desktop/assets/MaterialLibraryPage-DhZ_QhYt.js` 同名同内容，
  SHA-256 均为 `05b5c877299b6bb1add3e8c43a4a493d55197b6b13b6897ae36cb9914051a17a`；
- `.generated/frontend/assets` 里 `已生产成片`、`疑似重复`、`最近发布`、`已下架` 各命中 1 个文件
  （抽屉 chunk），阴性对照 0；
- DMG 构建时间 16:52（在 `27f74b3` 之后），产物里的 `source_commit` 戳为 **`27f74b3`**，
  即本次任务的前端提交（上一轮是 `26e1f62`，已翻页）；
- Cloud 在 127.0.0.1:18080、Agent 在 127.0.0.1:8765 上监听。

**打包后二进制不做字符串判据**（这是量法本身的限制，不是结论）：对
`/Volumes/WT Media/WT Media.app/Contents/MacOS/wt-media-desktop-shell` grep
`素材状态`、`wt-resource-actions` 与阴性对照 `ZZZnotpresentZZZ`，三者**都是 0**——
阴性对照同样是 0 说明这个 grep 在该文件上会失败（Tauri 压缩了内嵌资源），
因此从这个 0 里得不出任何关于「包里有没有新代码」的结论。上面那条 SHA-256 相等才是判据：
进包的前端产物就是刚构建的这一份。

## 10. 范围外登记

- `src/localSettingsWiring.test.js` 的既有失败（§5）：工作区脏改动造成，非本 CHG，保持原样。
- `web/src/modules/proxy/pages/ProxyPage.vue` 工作区里还有另一条工作线的改动
  （删除 `queuedTaskId` 与「查看任务进度」按钮，与 `TasksPage.vue` 的删除同源），
  本次**只暂存本 CHG 的那一个 hunk**（`:footer="false"`，用 `git apply --cached` 挑单一 hunk），
  其余改动原样留在工作区。
- 设计图上「素材」格副行含游戏名，与已定稿实现（副行只带来源平台）不一致，见 §1 末，
  待用户裁定。
- 列表顶部的统计卡与状态筛选**未动**：在缺 `status` 的数据上挂一排「素材状态」计数卡与筛选器，
  每一档点下去都是 0 行。
