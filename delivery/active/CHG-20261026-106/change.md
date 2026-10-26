---
id: CHG-20261026-106
parent: none
status: IMPLEMENTING
depends_on: []
affected_repos: ["wt-media-cloud"]
risk: M
---

# CHG-20261026-106：前端状态色语义表收口

## Change

审计 `web/src/shared/styles/tokens.css` 中的 `--wt-status-*` 语义色表：该文件未被任何入口引入（`apps/cloud/main.ts`、`apps/desktop/main.ts` 只加载 `design-token.css`），表内颜色从未生效。二选一收口：删除死表，或只把实际需要的 `--wt-status-*` 迁入真正被加载的 `design-token.css`；同步 `ComposeTasksPage.vue` 中指向 `--wt-danger` 的注释，并对合成任务、成片页面做视觉核对。默认不改 TDesign 全局 success/error 色。

## Done When

- 全站样式入口与 `tokens.css` 的引用关系有读回证据：要么文件及其状态色表不再存在，要么状态色只存在于已加载样式表中。
- `--wt-status-*` 不再存在“定义了但没有任何入口加载”的状态；有断言锁住入口真正加载的样式表。
- 合成任务、成片管理页面的成功/失败/警告状态色与改动前一致，或有明确差异说明。
- Cloud Web 构建、测试与视觉核对通过；不引入新的全局主题覆盖。

## Constraints / Not In Scope

- 不改 TDesign 组件库默认 success/error 色，不做主题体系重构。
- 不触碰 M3–M5 业务逻辑、接口或合同。

## References

- `web/src/shared/styles/tokens.css`
- `web/src/shared/styles/design-token.css`
- `web/src/modules/compose/pages/ComposeTasksPage.vue`
