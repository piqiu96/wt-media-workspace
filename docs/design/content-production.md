# 内容生产：原型与落地入口

> 状态：产品规则与原型已由用户确认完成，正式产品文档已回写。运行能力与验收状态以正式工程和交付记录为准；本次迁移不重开已确认设计。

## 阅读入口

| 要了解的内容 | 唯一维护位置 |
| --- | --- |
| 用户流程、字段、权限、状态与动作、产品验收 | [PRD 第五章：素材生产](../product/prd/详细文档/第五章_素材生产.md) |
| 表结构、接口、Cloud 执行、幂等、并发与恢复 | [内容生产工程设计](../engineering/specs/2026-09-24-m4-m5-cloud-content-production.md) |
| 与旧规则的取舍及替代关系 | [ADR-0031](../decisions/0031-content-production-batches-and-manual-reproduction.md) |
| 操作与体验 | [完整原型](https://github.com/piqiu96/wt-media-cloud/blob/main/web/example/proto/content-operations/index.html#materials) · [内容生产逐页评审](https://github.com/piqiu96/wt-media-cloud/blob/main/web/example/proto/content-operations/review.html?scope=production#page-review) |
| 公共页面、视觉与交互规范 | [正式规范](../standards/frontend/README.md) · [common 示例](https://github.com/piqiu96/wt-media-cloud/blob/main/web/example/common/index.html) |

## 原型导航

| 页面 | 重点核对 |
| --- | --- |
| [素材库](https://github.com/piqiu96/wt-media-cloud/blob/main/web/example/proto/content-operations/index.html#materials)／[我的素材](https://github.com/piqiu96/wt-media-cloud/blob/main/web/example/proto/content-operations/index.html#mine) | 加入与准备分离、我的使用／团队使用、视频与本机状态 |
| [合成策略](https://github.com/piqiu96/wt-media-cloud/blob/main/web/example/proto/content-operations/index.html#strategies) | 多组成片设置、模板参数、选材依据、立即执行预览与防重复 |
| [合成任务](https://github.com/piqiu96/wt-media-cloud/blob/main/web/example/proto/content-operations/index.html#tasks) | 任务批次详情、整体进度、新建选材与参数调整、执行记录及恢复 |
| [成片管理](https://github.com/piqiu96/wt-media-cloud/blob/main/web/example/proto/content-operations/index.html#outputs) | 按素材 ID 聚合、成片列表、视频信息、再次制作及去发布 |

成片“去发布”和发布任务“新建发布任务”共用表单，区别是是否带入成片；其入口约定见 PRD §5.9.12。发布计划、后续执行与作品／互动的完整设计继续由各模块维护，不因内容生产完成而一并标记验收。

## 落地与维护边界

- 本文件仅作导航，不再保存已回写规则、逐轮走查、接口表清单及中间方案。历史由 Git 追溯。
- 工程设计已区分当前实现和待实施目标；数据库／接口收敛建议不等于已执行删除、迁移或发布。
- 启动正式落地时，在既有 Delivery 中定义 CHG 的范围、顺序和验收，引用 PRD 与工程设计；不在 `example/design` 新建实施计划或交付状态。
- 原型中的合成、转存、下载、发布和账号均为本地演示。真实 FFmpeg、对象存储、服务端授权、本机文件与平台执行须在正式软件验证。
- 人工评审意见保留在原评审工具中，页面改动不重置意见，不用本次文档回写改造历史评审证据。
