---
id: CHG-20261026-102
parent: delivery/milestones/M3-content-discovery-v2.md#m3-f-public-content-scope
status: IMPLEMENTING
depends_on: ["CHG-20261023-101"]
affected_repos: ["wt-media-workspace", "wt-media-cloud", "wt-media-desktop"]
risk: H
---

# CHG-20261026-102：M3 内容池公共范围与策略职责

## Change

在已签收 M3 上交付一个验收后增量：普通运营可处理本团队所有游戏的公共 `source_content`，游戏多选初次默认其负责项；高级运营管理本团队所有游戏的 `discovery_strategy` 与 `crawl_task` 异常；管理员可跨团队选择目标团队。高级运营和管理员可登录 Desktop 使用 M3–M5 共用 Cloud 页面，M2 本机执行仍按原角色和本人身份拦截。服务端对列表、详情、写操作和任务入口统一裁决，Cloud Web/Desktop 共用页面使用同一授权。保留团队内来源唯一键和跨团队业务记录独立。内容池的忽略状态是团队级事实：来源被忽略后再次自动发现不改变忽略状态，只有人工恢复才改变；同团队运营共享同一内容池与审核权限（M3 V2-Q07，2026-10-26 确认）。

## Done When

- 普通运营能将本团队非本人负责游戏的内容入池、忽略／恢复、转素材；游戏筛选可多选并默认本人负责项，不因此读到其他团队。
- 普通运营伪造请求也不能创建、编辑、启停、执行挖掘策略或处置任务异常；高级运营仅本团队所有游戏可操作；管理员明确目标团队后可跨团队管理。
- 内容池、挖掘策略、挖掘任务在 Cloud Web 与 Desktop 共用页面显示和 API 权限一致，拒绝越权时没有业务写入或外部抓取。
- 管理员／高级运营能完成 Desktop 登录和 M3 页面操作，但不能借新入口访问普通运营的 BitBrowser、Profile、Cookie、本机文件或 M2 本机执行；Desktop 会话冲突和替换规则仍生效。
- `source_content` 团队唯一性、各团队独立处理状态、原有调度／任务恢复和 M3 已签收路径回归通过；记录真实请求、数据库和页面读回。

## Constraints / Not In Scope

- 不重开 M3 或 M2 旧验收；不建设第二套内容池或团队领取；只解除 Desktop 的整角色登录拦截以开放共用 Cloud 页面，不放宽 Desktop/Agent 本机资源边界。
- `/material-library` 对正式 `material` 的归位由 M4-J（CHG-104）交付；跨团队昂贵资源复用属 P1，先有成本和缓存现状证据后另立 CHG。
- 启动时只检查本 CHG 涉及的 Cloud API、授权点和共用页面；如发现提供方合同或跨仓接线变化，先回 Workspace 更新范围。

## References

- `docs/product/prd/详细文档/第四章_内容挖掘.md`
- `docs/decisions/0023-m3-m5-team-resources-and-production-operator.md`
- `delivery/milestones/M3-content-discovery-v2.md#m3-f-public-content-scope`
