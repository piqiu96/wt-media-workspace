---
id: CHG-20261026-102
parent: delivery/milestones/M3-content-discovery-v2.md#m3-f-public-content-scope
status: DONE
depends_on: ["CHG-20261023-101"]
affected_repos: ["wt-media-workspace", "wt-media-cloud", "wt-media-desktop"]
risk: H
merge_commits: {"wt-media-cloud": "cb26c66e69f7f476b3405db5a7018d9a0ddd6bef"}
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

## Verification

- Cloud 以 PR [#8](https://github.com/piqiu96/wt-media-cloud/pull/8) 合入 `main`，CI `verify` pass（2m39s），merge commit `cb26c66`；Desktop 无源码改动，构建产物只用于入口验证。
- 收尾重跑：Cloud Go 72 包 ok / 0 FAIL / 11 无测试文件；Cloud Web Vitest 79 文件 / 720 用例；`test-control.sh` 12/12；Workspace 174 用例与治理、AI 工作区、技能、产品对齐、M0、文档、control 校验全部通过。
- 真实读回：API 38/38 PASS（角色拒绝、团队边界、游戏筛选、游戏目录、Desktop 登录与 Agent Token）；Cloud／Desktop 页面 10/10 PASS；拒绝前后 `discovery_strategies` 4→4、`crawl_tasks` 73→73、`source_contents` 664→664；迁移重跑 `0 applied, 75 total`，手工重放 073 两次后 `other` 仍 1 行且不覆盖既有字段。
- Desktop 前端戳 `source_commit=1f54e42`、`source_dirty=false`，二进制资产表命中当前前端文件名；Tauri GUI 走查留给用户。
- 逐项证据见 `evidence/T-01-role-gates.md`、`T-02-game-filter.md`、`T-03-catalog-and-pages.md`、`T-04-desktop-boundary.md`、`T-05-acceptance.md`。
- `wt chg verify` 的跨端集成步仍调用已退役的 `verify_m1_integration.py` 并报 `ModuleNotFoundError`；该脚本在 `scripts/README.md` 已标注“行为已知阻塞”，与本 CHG 无关。
- 未覆盖：普通运营 Desktop 会话换 Agent Token 的现场正向链路（开发库仅一条属于用户本机的真实会话，由单测覆盖）；管理员跨团队编辑／启停／删除／执行的逐入口现场请求（现场实测创建与列表）；真实外部抓取未触发。

## Constraints / Not In Scope

- 不重开 M3 或 M2 旧验收；不建设第二套内容池或团队领取；只解除 Desktop 的整角色登录拦截以开放共用 Cloud 页面，不放宽 Desktop/Agent 本机资源边界。
- `/material-library` 对正式 `material` 的归位由 M4-J（CHG-104）交付；跨团队昂贵资源复用属 P1，先有成本和缓存现状证据后另立 CHG。
- 启动时只检查本 CHG 涉及的 Cloud API、授权点和共用页面；如发现提供方合同或跨仓接线变化，先回 Workspace 更新范围。

## References

- `docs/product/prd/详细文档/第四章_内容挖掘.md`
- `docs/decisions/0023-m3-m5-team-resources-and-production-operator.md`
- `delivery/milestones/M3-content-discovery-v2.md#m3-f-public-content-scope`
