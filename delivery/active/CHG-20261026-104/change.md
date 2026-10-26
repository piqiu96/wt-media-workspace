---
id: CHG-20261026-104
parent: delivery/milestones/M4-content-production.md#m4-j-material-usage
status: VERIFYING
depends_on: ["CHG-20261026-103"]
dependency_merge_commits: {"CHG-20261026-103": {"wt-media-workspace": "f2d0e3bfca3d3a732c0d65130b2a16383dd77a27"}}
affected_repos: ["wt-media-workspace", "wt-media-cloud"]
risk: H
---

# CHG-20261026-104：团队素材库的使用事实与个人下载

## Change

让正式 `material` 素材库成为团队公共挑选池：游戏多选初次默认本人负责项，列表分别显示“加入状态”“我的使用”“使用情况”；“我的素材”仍固定当前用户。个人原视频本机下载只能从当前用户有效的“我的素材”发起，Cloud Worker 源文件准备保持可用。`/material-library` 读正式 `material`，不再用内容池只读模式代替。

## Done When

- 普通运营可查看、加入本团队其他游戏素材而不能跨团队；高级运营本团队所有游戏，管理员按目标团队。游戏选择只影响筛选，列表、详情、加入与下载 API 均由服务端按团队和当前用户关系裁决。
- 加入／移出／恢复只改变当前用户“加入状态”；只有负责人为本人且存在成功 `composite_output` 才进入“我的使用＝已合成”；失败、取消、排队中和移出后的失败历史均为未使用。既有 `(策略, 素材)` 任务防重仍将用户带回原任务重试。
- “使用情况”仅按成功成片区分无人／有人使用；普通运营只能看到人数及成片数，高级运营和管理员仅在授权团队看姓名明细。同外部作品的不同团队素材不合并统计。
- 素材库列表、详情无本机下载入口；绕过页面直接发起个人原素材下载也要求当前用户有效 `material_usage`；从“我的素材”下载与失败重试、Cloud Worker 对未加入个人工作集素材的准备均实测通过。
- Cloud Web/Desktop 共用页面可直接判断未使用素材；“已发布”和发布次数仅记录 M6 口径，真实 `publication` 查询能力交付前不展示。原 M4-A 下载和 M5 生产回归。
- 高级运营的合成任务／成片管理负责人筛选只列本团队启用成员（含本人），不出现“我的／团队全部”伪选项；未选择即本团队全部，选中成员按 `operator_id` 收窄。高级运营可读可操作本团队所有游戏的任务／成片，普通运营与管理员范围不变。

## Constraints / Not In Scope

- 不新增平行素材、个人状态表或人工计数事实；不改变 `publication` 合同或发布流程。
- 若直接下载权限涉及 Agent 或 Desktop 合同改动，实施前更新本 CHG 的影响仓和验证边界，不在代码里绕过 Workspace 定义。
- 实施时同步合同缺口：`contracts/cloud-error-codes/v1/content-production.yaml` 未登记 `compose_task_not_retryable`（Cloud 已返回 HTTP 409／15217），补登记需 bump 该文件 revision。
- 下载端到端验收必须实测三条：素材库列表与详情无本机下载入口、从「我的素材」发起下载成功、无当前用户有效 `material_usage` 时直连下载 API 失败关闭。

## 验收修订（2026-10-27）

用户验收指出高级运营负责人筛选只有“我的／团队全部”两个伪选项，无法直接按团队成员筛选。修订为：

- 合成任务与成片管理的负责人下拉只列本团队启用成员（含本人），不注入伪选项；未选择发送空参数，选中成员只发 `operator_id`。
- 高级运营的任务／成片列表、详情、取消和重试按团队范围裁决，不再按本人负责游戏收窄；普通运营仍固定本人并保留负责游戏范围，管理员不变。
- 合成策略负责人“须负责该游戏”的硬匹配规则不变；`operator_scope` 保留兼容，页面不再发送，不新增合同参数。
- 同步更新 PRD 第五章、产品主文档与 M4 里程碑；原 103 记录不改写。

验收补充：高级运营空筛选看到团队全部游戏的任务／成片；选择任一团队成员按 `operator_id` 收窄；同团队跨游戏任务可读可重试，跨团队仍拒绝。

## References

- `docs/product/prd/详细文档/第五章_素材生产.md`
- `docs/decisions/0023-m3-m5-team-resources-and-production-operator.md`
- `delivery/milestones/M4-content-production.md#m4-j-material-usage`
