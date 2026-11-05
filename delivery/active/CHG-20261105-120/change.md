---
id: CHG-20261105-120
parent: delivery/milestones/M4-content-production.md#m4-n-production-acceptance
status: VERIFYING
depends_on: []
affected_repos: ["wt-media-workspace", "wt-media-cloud"]
risk: M
---

# CHG-20261105-120: 内容生产公共交互与原型差距收口

## Change

按用户已确认走查清单，将实际 Vue 产品的内容生产五页与关联弹层统一到 common。先收敛 shared/ui 控件和筛选布局，再整理策略表单及详情操作归属，最后逐页接入、角色走查和构建验证。前置 CHG119 已合并；本次是交互视觉整改，不以其测试代替本次验收。

### Tasks（顺序执行，各自验证和提交）

1. shared/ui：统一筛选字段/动作的换行与间距、日期范围、多选摘要、两个高级筛选入口、排序动作。已有公共能力先复用；业务规则仍由模块负责。更正文档的详情操作准入规则。验证公共测试及代表页面窄宽布局。
2. 策略：新建/编辑基本信息→默认成片设置→执行设置→选材条件，team 在 owner 前，名称长字段；模板参数和解释归组；重要操作保留列表，详情只读；立即执行三种分支及下一步动作。验证滚动/草稿不丢、手动/定时字段、任务数口径和权限。
3. 素材/任务/成片：高频筛选基础展示；素材选择、参数弹层有效值与修改标记；任务主体/配置/执行记录分层；批次全局/筛选/选择范围；素材ID聚合详情继承查询范围；实体关联只读嵌套，不路由丢现场；详情不重复列表主动作。验证空态/查询/部分选择/跨页/嵌套返回与三角色。
4. 逐功能验收、必要自动测试、Cloud/Desktop 共用前端构建、独立 review，证据保存 evidence/。提交边界为公共能力、策略、素材任务成片、验收文档。

### Constraints

- 不修改已有 example/ 工作区变更，不修改 Agent/Desktop Runtime、API/DB、权限、真实重试取消/合成机制；不扩展发布模块。
- 素材来源抖音；目标平台 B站/百度/小红书。任务创建固定组只允许 schema 开放参数；无本地下载前提；估算不乘平台数。
- 先判断操作归属，再确定 Footer 位置；任务批次保留列表仅详情的已确认例外。
- 复用真实数据、真实执行记录与文件；不构造虚假状态、封面或发布成功。

## Done When

- [x] 公共筛选/日期/多选/排序控件被目标页面复用，宽窄布局和已应用筛选反馈一致。
- [x] 策略两个编辑入口、模板参数、执行预览和详情动作逐项对照通过。
- [x] 素材、任务、成片主次操作与只读关联详情一致；聚合下钻范围无静默扩大，模板参数调整可见。
- [x] admin/operator01/senior01 的权限与主要交互经过本次实际走查；测试及双前端构建通过，未验证项如实记录。
- [x] 独立 review 的重要问题修复；规范及交付状态回写，不将机器走查冒充人工签收。

## References

- docs/standards/frontend/AdminUI页面规范.md
- docs/standards/frontend/前端交互规范.md
- docs/standards/frontend/前端架构与视觉规范.md
- docs/product/prd/详细文档/第五章_素材生产.md
- example/proto/content-operations/design/content-production.md（辅助参照，以最新用户决定和正式规范为准）

## Acceptance / Handoff

实施和独立审查整改已完成，当前 `VERIFYING` 等待 PR 审阅及用户人工视觉签收。验收范围与截图见 [evidence/acceptance.md](evidence/acceptance.md)。原生窗口自动控制不可用，同源 Vue 界面已完成浏览器三角色检查；执行中预览采用明确标记的界面 fixture，仅验证动作及进度展示。未合并、不归档为 DONE。

Cloud PR：https://github.com/piqiu96/wt-media-cloud/pull/32。公共组件、策略、关联详情分别提交，验收记录对应最终 `b4e1bd0`。
