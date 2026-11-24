---
id: CHG-20261124-108
parent: delivery/milestones/M7-batch-publishing.md#批次执行与真实结果
status: DONE
depends_on: ["CHG-20261124-107"]
affected_repos: ["wt-media-workspace", "wt-media-cloud", "wt-media-agent", "wt-media-desktop"]
risk: H
merge_commits: {"wt-media-workspace": "0e3ea12fc2f6628fb7e266d81ba088280e2748df", "wt-media-cloud": "0d5667c87809696375d85ea2edf2a33dadc52a5c", "wt-media-agent": "dc6451a775f68a02dd6abd153c1f7d4e0e73535b", "wt-media-desktop": "b623b3c7d25a405aeb5f030ffd0c4d42d725e60a"}
dependency_merge_commits: {"CHG-20261124-107": {"wt-media-workspace": "ca4480aaec49ce0720ac64366e0fdbb13c1ec23a"}}
---

# CHG-20261124-108：批次启动、分组发布与结果

## Change

运营开始发布时，从107配置一次生成正式任务、取得占用并授权；本人不同账号按组并发、组间等待，支持组间处理【自动继续、异常暂停】、异常任务上限、人工继续/终止、全局Profile互斥和可信公开结果。

完整业务/API/数据库/步骤/证据见[执行落地清单](plan.md)。2026-11-25用户授权依次完成107→108→109的编码、测试、PR修复、E2E和走查。107已完成技术交付且四仓合入main；本项已完成实施和真实验证，运行仓PR及本地main已合入；Workspace以本关闭PR收口归档。必须以Cloud web/example现有原型为输入，先核对并固定108场景，再定版契约；实际Profile不足时按可用数向下兼容。状态只在本文件，清单按已验证事实回填。

## Done When

- 首次start原子建单/占用/授权，同键重放不重复，配置冲突不遗留半批。
- 分组、可靠人工挂起/未知占位、跨批Profile、异常暂停/继续/终止真实收敛；不自动重发，不无限开窗。
- 原task/attempt/observation/作品与公开统计一致；按现有本人Profile向下兼容完成真实发布与双端验收，多Profile受控证据分列，各仓main合并可查。

108技术交付DONE，证据见evidence/acceptance-matrix.md、installed-e2e.json与merge-and-verification.md。用户已指定107–109后统一整体验收，故本项技术归档为109提供依赖，不表示用户最终签收。
