---
id: CHG-20261125-110
parent: delivery/milestones/M7-batch-publishing.md#页面实施基线
status: VERIFYING
depends_on: []
affected_repos: ["wt-media-cloud", "wt-media-workspace"]
risk: M
---

# CHG-20261125-110：发布准备原型一致性修复与完整运营验收

## Change

修复已交付批次/计划页面偏离已确认原型的问题，以原型代码的结构、交互、样式承接正式数据和服务，在全新桌面安装包及Web中完成可用的准备—执行—结果路径。不改已确认业务闭环。用户2026-11-25授权自行修复、完整E2E、运营视角走查至交付。

继承Cloud本地b84de4b、1b31e79、db6109e作为已完成但未整体验收的修复，不把这些提交或旧测试通过当成本项完成。

## References

- docs/design/publishing.md §1、§2、§4；原型Cloud 930553217cf5a3c8a1750178da4974d5b46dfeac 的 web/example/proto/publishing-design 与 common。
- docs/product/prd/详细文档/第六章_发布管理.md §6.2、6.3、6.5、6.8。
- docs/engineering/specs/publishing-management.md §1.3、2、4—6。
- delivery/milestones/M7-batch-publishing.md#页面实施基线；M-publishing-plan闭环为计划回归依据。

## Constraints

保存不建正式任务/占用；启动一次建单；本人账号；固定组与Profile互斥；组间集中处理；计划启动冻结全部安排；10%自动衔接不变。接口冲突由实现修复，新增信息纳入原框架；仅真实业务规则改变需人工决策。正式运行不依赖example演示数据/代码。

## Tasks

1. 逐区核对原型与真实页面，登记缺口、接口适配及运营风险。
2. 按原框架修复资源/内容/总览/详情及计划入口，完成针对性自测。
3. 先跑逻辑/组件测试与构建，再跑完整受控浏览器回归，修复失败；明确fixture不证明真实发布。
4. 强制重建四端环境与DMG，使用operator01/operator123走真实准备、保存/编辑/续编、启动及计划推进路径；已有公开证据与新动作区分，真实AI仅使用此前授权范围。
5. 产品运营视角同尺寸对照、异常/返回/未保存保护/角色只读核验；PR问题修复与最终证据收口。

## Done When

- [ ] 批次/计划关键页面按实际原型框架落地；逐项差异有修复或已确认范围依据。
- [ ] 代码自测与Cloud/Desktop构建通过；准备、执行、计划受控浏览器场景全部通过。
- [ ] 新环境所有门禁通过，安装包版本与本项源码一致。
- [ ] 真实本人资源的准备—保存零任务/占用—读取编辑—启动—结果，以及计划顺序推进可核实；不使用mock替代真实结果。
- [ ] 最终产品运营走查问题关闭，提交/PR/检查状态真实记录；用户最终签收另行。

## Current facts / blockers

- Cloud/Workspace 当前分支均为 `chg/CHG-20261125-110`；Cloud d659a34 在继承三次修复后补齐推荐、行内匹配、封面预览与分区。
- 全Web167文件/1242测试通过；受控批次/执行/计划回归通过，异常矩阵与原型缺口记录在evidence；不代表真实发布完成。
- SSH读远端已成功；gh token/HTTPS认证失败不作为停止交付的理由，后续用SSH推送及已登录浏览器PR。
- 正在强制重建完整环境；新的真实资源与两批顺序闭环、产品运营走查及PR尚未完成。
- Workspace docs/design 和 Cloud example 中存在其他会话原型工作，保持原样，不纳入本项提交；本项采用 References 指定原型基线。
