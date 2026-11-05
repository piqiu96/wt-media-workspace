---
id: CHG-20261105-119
parent: delivery/milestones/M4-content-production.md#m4-n-production-acceptance
status: DONE
depends_on: ["CHG-20261105-118"]
affected_repos: ["wt-media-cloud", "wt-media-workspace"]
risk: M
dependency_merge_commits: {"CHG-20261105-118": {"wt-media-workspace": "b21564b2e1ead95d0b48e57088d143d28573573e"}}
---

# CHG-20261105-119: 内容生产实际产品与批准原型视觉交互对齐

## Change

用户反馈正式软件未达到已确认的内容生产原型。以当前 example/proto/content-operations 的内容生产页面、example/common 与正式 frontend 规范为参照，修正 Cloud web 的实际 Vue 页面；Desktop 复用同一业务源码。原型工作区已有修改作为只读参照，不覆盖或提交。

范围：素材库／我的素材、合成策略、合成任务与成片管理，以及相关筛选、选择器、表单、预览、详情和执行记录。复用 TDesign、resource 公共组件和主题 token，保留真实数据／权限／状态／快照／执行行为。无 Schema、API Contract 或数据库新增；不开放未实施的发布能力，不重置走查账号，不修改 Agent／Desktop Runtime。

## Done When

- 五个实际页面及其关联弹层逐功能对照原型；筛选、表格、选择条、字段帮助、配置分层、进度和记录符合 common／正式规范。
- 策略新增设置和条件不跳顶；参数权限、平台边界、执行预览依据与批次操作真实且可理解。
- 合成任务创建只能修改允许参数；任务主体、配置和执行记录分层，批次详情统一呈现进度与操作。
- 成片按素材聚合，列表／详情／视频信息无冗余状态或虚构预览，来源和文件操作真实。
- 用 admin、operator01、senior01 核对权限与主要流程；记录实际执行、读回和页面结果，无法验证项目明确保留。
- 定向前端测试、Cloud／Desktop 共用源码构建、实际浏览器的视觉和交互检查通过；证据不能以无溢出检查代替设计对齐。

## References

- docs/product/prd/详细文档/第五章_素材生产.md
- docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md
- docs/standards/frontend/README.md
- docs/standards/frontend/AdminUI页面规范.md
- docs/standards/frontend/前端架构与视觉规范.md
- docs/standards/frontend/前端交互规范.md
- example/common/index.html
- example/proto/content-operations/index.html

## Result

Cloud共享Vue实际产品实现已合并 [PR31](https://github.com/piqiu96/wt-media-cloud/pull/31)，main `4b921bb183e281772823188bb0d332cca0c0c04f`。五页与关联弹层按common／批准原型核对，三角色共享界面检查、原生senior01五页检查、真实3条任务／3个成片读回、953项前端测试与双端构建通过；独立审查反馈已修复。详细证据见 [verification.md](evidence/verification.md)。M4-N用户人工签收仍待完成，原生senior01比特账号绑定限制与未覆盖项已注明。
