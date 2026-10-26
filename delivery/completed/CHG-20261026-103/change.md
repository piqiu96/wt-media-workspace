---
id: CHG-20261026-103
parent: delivery/milestones/M4-content-production.md#m4-i-production-operator
status: DONE
depends_on: ["CHG-20261026-102"]
dependency_merge_commits: {"CHG-20261026-102": {"wt-media-workspace": "55ee841606131633bca353c829dd8d80aa7a686d", "wt-media-desktop": "4bf633c181d214a1c1aebe7a8f724c9107df0243"}}
affected_repos: ["wt-media-workspace", "wt-media-cloud"]
merge_commits: {"wt-media-cloud": "2cd341d56ead14254243cf0932298ef8c5910c7c"}
risk: H
---

# CHG-20261026-103：合成策略到成片的运营负责人

## Change

交付一条可验收的负责人链路：合成策略必须指定团队、一个游戏和该团队有效的运营负责人；人工任务分别保存创建人与负责人，成功成片继承负责人。普通运营仅为自己使用指定策略；高级运营和管理员可从**自己的**“我的素材”代创建，负责人必须匹配策略。合成任务与成片管理在同一页面体系按负责人查询，服务端授权与页面筛选一致。

## Done When

- Cloud 正式 migration、提供方合同、API 和共用页面有负责人字段；历史任务／成片只在可核实依据存在时回填，无法确认的保持未知并限制展示，不以 `created_by` 冒充。
- 高级运营创建策略时团队自动为本团队，管理员选择目标团队；团队、游戏、负责人有效性和引导配置的一致性在服务端校验。普通运营只能使用指定给自己的已启用策略。
- 普通运营仅从自己的“我的素材”为本人创建；高级运营／管理员可从自己的工作集为有权管理的运营代创建。任务保存创建人和负责人快照，策略负责人之后变化不改历史，成片继承任务负责人。
- 普通运营伪造负责人或查询参数被拒绝；高级运营默认“我”且可筛本团队全部／指定运营，不能跨团队；管理员按目标团队查看。代创建后能直达任务与成片，普通运营不被他人任务干扰。
- 同一素材经不同策略可产生归不同负责人的成片，既有 `(策略, 素材)` 防重、重试、下载与 M4/M5 Worker 链路回归；数据库、API、Cloud Web/Desktop 页面和真实成片逐层对账。

## Verification

- Cloud 以 PR [#10](https://github.com/piqiu96/wt-media-cloud/pull/10) 合入 `main`，CI `verify` pass（2m58s），merge commit `2cd341d`；合并后本地 `main` 与 `origin/main` 同为该提交，工作树干净。
- 自动门禁：Cloud `go test ./... -count=1` 为 72 包 ok、0 FAIL、11 个无测试文件包；Cloud Web `npx vitest run` 79 文件 / 725 用例通过；Cloud `test-control.sh` 12/12；Workspace 175 用例与治理、AI 工作区、技能、产品对齐、M0 配置、文档、control 校验全部通过。
- 真实链路：任务 325/326/327 由真实 Worker 产出成片 70/69/71，负责人分别继承 3/3/9，下载文件 SHA256 与 DB 一致；代创建、同素材跨策略、防重 15219、成功任务重试 15217、下载 transfer 幂等、调度 `operator_unavailable` 均现场读回。见 `evidence/T-08-real-chain.md`。
- 页面：三种角色真实浏览器读回列表、筛选、表单与详情抽屉；历史负责人显示“未记录”且不被创建人冒充。Desktop 由 Cloud `54c0e87` 构建，前端戳 `source_dirty=false`，当前负责人页面资产在二进制中命中。见 `evidence/T-07-pages-and-desktop.md`。
- 合同：Cloud OpenAPI `2026.10.26.1` 与 Workspace `contract-map.yaml` 同版；M0 配置校验通过。见 `evidence/T-06-contract.md`。
- `python3 scripts/wt.py chg verify CHG-20261026-103`：Workspace 175 用例与 Cloud `internal/modules/...` 全部通过；最后固定调用 `verify_m1_integration.py`，因导入已退役的 `wt_media_agent.cloud_agent_client` 报 `ModuleNotFoundError` 退出 1。该脚本在 `scripts/README.md` 已标注“行为已知阻塞”，与 CHG-102 收尾现象相同，不属于本 CHG 运行时回归。
- 未覆盖：Tauri 安装包 GUI 走查留给用户（本机不能程序化驱动 GUI，二进制只做到资产锚定）；清理后三个开发桶成片对象未删除；两个验收临时账号因审计外键保留为 `disabled`。见 T-08。
- 原始读回摘录：`evidence/T-03-operator-directory.json`、`T-04-strategy-operator.json`、`T-05-task-scope-and-snapshot.json`、`T-07-pages.json`、`T-08-chain.json`。

## Constraints / Not In Scope

- 不建立成片池、领取或新任务对象；不开放他人的 `material_usage`、BitBrowser、Profile、Cookie 或本机文件。
- 不改变 Scheduler 候选来源；它由 M5-F（CHG-105）单独交付。M6 发布流程和统计不在本 CHG。
- 启动前定向核实当前 Schema、合同和调用方，确认迁移及历史兼容策略；发现跨仓合同变化先回 Workspace。

## References

- `docs/product/prd/详细文档/第五章_素材生产.md`
- `docs/decisions/0023-m3-m5-team-resources-and-production-operator.md`
- `delivery/milestones/M4-content-production.md#m4-i-production-operator`
