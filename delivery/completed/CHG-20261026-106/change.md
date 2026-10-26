---
id: CHG-20261026-106
parent: none
status: DONE
depends_on: []
affected_repos: ["wt-media-cloud"]
risk: M
merge_commits: {"wt-media-cloud": "d793d922465a24b0b9ed603dba907ea072dc30c9"}
---

# CHG-20261026-106：前端状态色语义表收口

## Change

审计 `web/src/shared/styles/tokens.css` 中的 `--wt-status-*` 语义色表：该文件未被任何入口引入（`apps/cloud/main.ts`、`apps/desktop/main.ts` 只加载 `design-token.css`），表内颜色从未生效。二选一收口：删除死表，或只把实际需要的 `--wt-status-*` 迁入真正被加载的 `design-token.css`；同步 `ComposeTasksPage.vue` 中指向 `--wt-danger` 的注释，并对合成任务、成片页面做视觉核对。默认不改 TDesign 全局 success/error 色。

## Done When

- 全站样式入口与 `tokens.css` 的引用关系有读回证据：要么文件及其状态色表不再存在，要么状态色只存在于已加载样式表中。
- `--wt-status-*` 不再存在“定义了但没有任何入口加载”的状态；有断言锁住入口真正加载的样式表。
- 合成任务、成片管理页面的成功/失败/警告状态色与改动前一致，或有明确差异说明。
- Cloud Web 构建、测试与视觉核对通过；不引入新的全局主题覆盖。

## Verification

- Cloud 以 PR [#9](https://github.com/piqiu96/wt-media-cloud/pull/9) 合入 `main`，CI `verify` pass（2m59s），merge commit `d793d92`。
- 删除前审计：`tokens.css` 不在两个入口的 import 链上；`var(--wt-status-` 无消费方；运行时只加载 `design-token.css`，根变量 `--wt-status-*` 为空，`--td-success-color` 仍是 TDesign 默认 `#2ba471`。
- 删除前后同一浏览器读回：合成任务与成片管理两页的行数、五种状态徽标计算色、加载资源全部一致；唯一差异是合成页注释不再提及旧前缀。
- 新断言：状态色定义在入口加载的 `design-token.css`；`web/src` 递归扫描 192 个文件，`--wt-status-*:` 定义 0 处；旧文件阳性对照命中 6 次。
- 门禁：`npm run build` 成功且产物 0 命中旧前缀；Vitest 79 文件 / 722 用例；Go 72 包 ok / 0 FAIL；Workspace 174 用例与治理校验通过。
- 未覆盖：失败/警告色来自真实徽标组件的克隆节点（operator 可见数据无失败行，管理员凭据不可得）；未做 GUI 截图比对。
- `wt chg verify` 的跨端集成步仍因已退役的 `verify_m1_integration.py` 报 `ModuleNotFoundError`，与 CHG-102 收尾现象相同，不属本 CHG 回归。

## Constraints / Not In Scope

- 不改 TDesign 组件库默认 success/error 色，不做主题体系重构。
- 不触碰 M3–M5 业务逻辑、接口或合同。

## References

- `web/src/shared/styles/tokens.css`
- `web/src/shared/styles/design-token.css`
- `web/src/modules/compose/pages/ComposeTasksPage.vue`
