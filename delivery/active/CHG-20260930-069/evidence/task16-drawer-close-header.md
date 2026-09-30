# 任务 16 证据：抽屉关闭统一到右上角（纯前端）

日期：2026-09-30　仓库：`wt-media-cloud`（前端 `web/`）　范围：前端 + 规范

## 1. 来源

用户对走查图五条裁定的第 5 条，原文：

> 5、关闭按钮统一做到右上角（统一改组件统一），顶部 tab 切换不需要

第 1～4 条（平铺一页、筛选栏左标题、超过 5 个才有更多、来源列不做）都是对**已落地实现**
的确认，本轮无代码改动，登记在 `change.md` §3 与 `checkpoint.md`。

## 2. 动手前核实：一条被我记错的既有事实

动手前我对这条的理解是「把唯一那颗页脚『关闭』删掉即可 —— 顶部的 × 本来就在（全站没有
任何抽屉写过 `close-btn`，说明用的是 TDesign 的默认值 true）」。**这条是推断，而且错了。**

三条独立读数：

1. **源码**：`node_modules/tdesign-vue-next/es/drawer/props.mjs` 里 `closeBtn` 只声明
   `type: [String, Boolean, Function]`，**没有 `default`**；同一版本 `es/dialog/props.mjs:19`
   写着 `"default": true`。渲染处 `es/drawer/drawer.mjs:366` 是
   `props2.closeBtn && createVNode(...)`，而 `useConfig('drawer').globalConfig` 只兜
   `size / closeOnEscKeydown / closeOnOverlayClick / confirm / cancel`，**不兜 closeBtn**。
2. **Vue 语义**（用一个同形状的 prop 探针，带判别力对照）：
   `{ type: [String, Boolean, Function] }` 不传 → `false`；传 `true` → `true`；写成
   `{ ..., default: true }` 不传 → `true`。声明了 Boolean 又没有 default 的 prop，缺省即
   `false`。
3. **真实浏览器**（headless Chrome + Vite dev，`--dump-dom` 读渲染后的 DOM，三个抽屉互
   为对照）：不写 `close-btn` → 无 `.t-drawer__close-btn`；`:close-btn="true"` → 有；
   `:close-btn="false"` → 无。三个抽屉的 `header`/`footer` 都正常渲染（阳性对照成立）。

结论：**今天全站 12 个抽屉一个 × 都没有**，关闭只剩遮罩点击与 Esc。按原计划只删那两颗页脚
「关闭」，会让这两个抽屉连唯一一个明确入口都没掉——正好与用户的诉求相反。所以任务 16 的
实际范围是「撤页脚 + **给 12 个抽屉补上 ×**」。

先做的那次 SSR 探针（`renderToString`）对三种输入都报 `__close-btn: false`、连 footer 都报
false（`len: 2`，整棵树没渲染），是**没有判别力的空转**；加阳性对照后立刻暴露，改用
headless Chrome。若没有那一步阳性对照，这里会得到一个「× 不存在」的错误佐证方向。

## 3. 先红

`npx vitest run`（cwd = `web/`，下同）在实现前：

- `drawerFooterConvention.test.js > keeps every drawer footer on business actions, never a 关闭 button`
  FAIL，`[…]` 里有 2 条：`modules/materials/MaterialDetailDrawer.vue`、`modules/profiles/pages/ProfilesPage.vue`；
- `MaterialDetailDrawer.test.js` 三条 FAIL（`leaves closing to the header × …`、
  `pins the context actions into that footer …`、`keeps the footer on the context actions alone, aligned right`）。

## 4. 实现

- `MaterialDetailDrawer.vue`：撤页脚那颗「关闭」；顺带去掉只包主操作的 `.material-detail__primary`
  一层（页脚现在只有一组动作），`.material-detail__actions` 由 `justify-content: space-between`
  改 `flex-end`。
- `ProfilesPage.vue`：扫描抽屉页脚撤「关闭」；两颗按钮的
  `v-if="currentScan?.status === 'ready' && hasDiff(currentScan)"` 提成 computed
  `scanAcceptsChanges`，并同时用作 `:footer` 的门——`footer` 为 `false` 时 TDesign 连
  `.t-drawer__footer` 容器一起不渲染（`drawer.mjs:371` 的 `props2.footer && …`），否则
  没有可接受变化时会留下一道空条。
- 12 个 `t-drawer`（10 个文件）一律补 `:close-btn="true"`。
- `drawerFooterConvention.test.js`：新增按标签配对的 `#footer` 切片（页脚里有嵌套
  `<template v-if>`，按第一个 `</template>` 切会把动作条剪断），两条新断言 + 分母对齐。
- `MaterialDetailDrawer.test.js` / `ProfilesPage.test.js` 各自钉住本页那条。
- `docs/standards/前端交互规范.md` §6.3、§9.1 回写：关闭只有 `×` 一个入口，页脚只放业务
  动作并靠右收，没有业务动作时整条不出现；并写明「抽屉必须对页脚表态」的既有约定。

## 5. 与「统一改组件统一」的关系（明确登记）

用户原话里有「改组件」。本仓**没有共享抽屉包装组件**可以改这一处：`shared/ui/templates/`
下只有一个 `DetailDrawerPage.vue`，全仓无人引用（守卫扫描的 12 个抽屉里它是唯一那个模板）；
其余抽屉各自写 `<t-drawer>`。TDesign 也没有能一次改掉 closeBtn 的全局开关（见 §2 第 1 条）。

因此「统一」落在两处：站级守卫测试 + 规范条目——这与本 CHG 既定做法一致（任务 13 的
「筛选栏统一左标题」就是 7 页铺设 + 站级守卫）。**没有**为此新建包装组件：那是一次
跨 12 个调用点的重构，且会让守卫的 `t-drawer` 扫描方式失效，超出「关闭按钮挪到右上角」
这一条裁定。若用户要的是抽出包装组件，应另立任务。

## 6. 变异对照（每条新断言都要能红）

| 变异 | 结果 |
|---|---|
| 把「关闭」加回扫描抽屉页脚 | `keeps every drawer footer on business actions …` FAIL |
| 把「关闭」加回素材详情页脚（嵌套 `<template>` 内） | 同一条 FAIL |
| `.material-detail__actions` 回退 `space-between` | `MaterialDetailDrawer.test.js` FAIL |
| 去掉一个抽屉的 `:close-btn="true"` | `enables the header close button …` FAIL |
| 把它写成 `:close-btn="false"` | 同一条 FAIL |
| 去掉素材详情的 `:close-btn="true"` | `MaterialDetailDrawer.test.js` FAIL |
| 去掉扫描抽屉的 `:footer="scanAcceptsChanges"` | `ProfilesPage.test.js` FAIL |
| 切片器一律 `return null` | `keeps every drawer footer …` FAIL（分母 0） |
| 切片器改成 `at !== -1 return null`（返回垃圾串） | 同一条 FAIL（分母 12 ≠ 正则数 3） |

最后两条是分母的自检。第三条到第四条这一对特意做了两次：第一次的写法（`at !== -1`）在
本仓会返回一段**真值垃圾串**而不是 null，于是 `expect(withFooter.length).toBeGreaterThanOrEqual(3)`
照样通过——**是坏的探针，不是坏的断言**。据此把分母改成与不经切片的 `hasFooterSlot`
正则**逐数对齐**，这样两种坏法（null / 垃圾串）都会红；改完重跑两个探针，都红。

每条变异都在还原后复跑全绿，无残留（`grep -c` 逐文件核对过补回的属性数）。

## 7. 后绿与读数

- `npx vitest run`（cwd = `web/`）：**46 文件 / 392 用例全绿**。分母与任务 15 的
  46 / 389 差 +3，正是本任务新增的三条（守卫 +2、`ProfilesPage` +1），无其他增减。
- `npm run build:cloud`、`npm run build:desktop`：均 exit 0（仅既有 chunk 体积提示）。
- 全站 `t-drawer` 计数与属性计数：抽屉 12 个、`:close-btn="true"` 12 处、页脚 `>关闭</t-button>` 0 处。
  （`ProfilesPage.vue:1048` 那颗「关闭」是**行内操作**「关闭窗口」，不是抽屉页脚，保留。）
- 以上全部在最后一次改动之后重跑。

## 8. 实机量测（headless Chrome，渲染后的 DOM）

同一探针页里渲染一个与页面同形的抽屉（`:close-btn="true"`、`header="代理详情"`、
`size="480px"`、`:footer="false"`），读 rect 与 computed style：

| 量 | 值 |
|---|---|
| `.t-drawer__close-btn` 是否存在 | 是，且含 `.t-icon` |
| computed | `position: absolute; top: 16px; right: 8px`，24×24 |
| 距面板右边 | 8px；距面板顶 16px |
| 是否落在页头内 | 是（页头 480×56，按钮纵向 16～40） |
| 页脚按钮 | `[]`（`:footer="false"`）；给页脚插槽时只有 `接受本地变化`，不含「关闭」 |

第一次量测报出「距面板右边 −292px」（按钮在面板外），是探针自己的错：两个抽屉同时
`visible: true` 时我量的是另一个抽屉的外层容器。改成单抽屉 + 按面板 `.t-drawer__content-wrapper`
量之后才得到上表。负值那版没有作为结论使用。

## 9. 边界与遗留观察

- 不动后端、数据库、状态枚举、权限模型与业务语义；本任务零 Go 改动。
- 不抽包装组件、不加顶部 tab（见 §5、`change.md` §3）。
- **遗留观察（留给走查）**：× 绝对定位在页头右侧 8～32px，而页头自身右内边距是 24px，
  所以标题很长时会压到 × 下面。本仓抽屉标题最长的是游戏关联详情那一条
  （`${referenceGame?.name || ''} 的关联详情`），游戏名较长时可能撞上。这是 TDesign 自带
  的摆法、也是「把关闭放到右上角」本身带来的，本轮不额外加页面级 CSS；走查若看到碰撞，
  再按那一页补右内边距。
- 真实点击走查仍留给用户：本轮能给的证据是「渲染后的 DOM 里有 × 且落在右上角」与
  「页脚没有关闭」，不是「我点过了」。

## 10. 提交后重建与产物读回（走查环境必须与 HEAD 一致）

`all --force-restart`（提交后）：三道构建前门与两份构建产物都过，**但收尾的 `verify` 门
exit 1** —— Agent `GET /api/v1/status` 读超时。这是本 CHG 已知的会偶发假 FAIL 的门
（checkpoint 早有登记：该门单发无重试）。判据不是「再跑一次就好了」，而是：连打三次该
端点，`status=200`、耗时 1.25 / 1.03 / 0.99 s（稳态 1.2～1.35s），再跑 `verify` → exit 0、
DMG `fresh`、`Login smoke PASS user=admin`。所以第一次是门的问题，不是 Agent 挂了。

产物读回：`web/dist-desktop/assets/MaterialDetailDrawer-B2D08j6s.js`（构建时间 19:50，在本次
提交之后）里 `close-btn` 1 处、`关闭` **0 处**、`恢复使用` 2 处——后两者是这条读回自带的
对照：该在的字符串在，该没的字符串没了，说明读的确实是这个组件那份产物。

环境一致性复核（重建后）：`POST /api/v1/material-usages/3/restore` 无会话 → `401 11001`，
对照路径 `POST /api/v1/material-usages/3/nope` → `404`（401 说明路径存在，404 说明对照有
判别力）；`material_usages` 仍是 9 行全 `active`、0 行有 `removed_at`。
