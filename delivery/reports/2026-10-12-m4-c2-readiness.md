# M4 下一项开发核对（2026-10-12）

## 当前结论

下一项是 M4-C2：交付可保存、可读回、可版本化且受权限约束的合成策略。M4-C3 才让运营从“我的素材”选择策略并创建任务，同时验证任务保存的不可变快照。这个边界已回写到 `delivery/milestones/M4-content-production.md` §3.1。

当前不能激活 M4-C2：`CHG-20260930-070` 仍是唯一 active CHG，等待内容池页面的用户走查；M4-A 的 `061-AC-12` 用户签收和 T-07 八条走查臂仍未闭合。`CHG-20260930-069` 的走查关闭不等同于 M4-A 里程碑签收。两项门槛分别见 CHG070 checkpoint、M4 §3.1 和 `delivery/MASTER_IMPLEMENTATION_PLAN.md` 的 M4 段。

M4-A 未覆盖的操作见 [CHG-061 走查证据](../completed/CHG-20260924-061/evidence/20260927-walkthrough-defects.md) §5：心跳过期时点击与错误文案；保存目录同步、旧目录文件定位与迁移提示；下载的“点击→取消→再点”、取消后重下、依赖未交付时的具名拒绝。这些仍不能按自动测试通过来判为用户走查通过。

## 已有实现与缺口

| 位置 | 当前事实 | M4-C2 需要补的内容 |
| --- | --- | --- |
| Cloud `internal/modules/production/` | 已提供素材、使用关系与下载接口 | 策略模型、数据访问、业务校验和 API |
| Cloud `migrations/` | 已有 M4-A 的素材与传输任务表 | 策略及不可变版本记录 |
| Cloud `contracts/{cloud-api,business-schemas,business-enums,cloud-error-codes}/v1/` | 内容生产合同只覆盖 M4-A | 策略请求、响应、枚举和错误；Cloud 作为提供方维护 |
| Cloud `web/src/apps/{cloud,desktop}/router.ts` | `/compose-strategy` 指向 `ComingSoon.vue` | 两端共用的策略页面；Desktop 不复制业务源码 |
| Cloud `web/src/modules/materials/pages/MyMaterialsPage.vue` | 已有“我的素材”列表 | M4-C3 再接入策略选择与任务提交 |

Cloud 是策略与权限事实来源。Desktop 只显示共享页面；Agent 不参与策略保存或合成。M4-C2 不增加 `compose_task`、FFmpeg、定时触发或本机执行路径。

## M4-C2 待激活任务

1. 确定首个**可在后续 Worker 中真实执行**的模板版本、参数范围及普通运营可覆盖项。PRD 中的 `high_light` 和视觉稿是示例，不能直接当作已实现模板。
2. 新增策略与版本数据，保证每次修改生成可读的历史版本；复制形成新策略，不改写原策略版本。
3. 发布 Cloud 合同，实现创建、列表、详情、修改、复制与只读可用策略查询；服务端校验角色、团队/游戏范围和参数，不依赖前端隐藏按钮。
4. 实现 Cloud Web/Desktop 共用的策略页面。高级运营可维护有权管理的策略；普通运营只读可用策略。页面反馈遵循 `docs/standards/feedback-system.md`。
5. 验证数据库读回、版本递增、越权拒绝、错误参数拒绝、两端页面和双构建。分别提交数据与合同、业务实现、共享页面、验收记录。

启动前需要完成 CHG070 与 M4-A 的用户验收裁定。裁定后建立一份正式 M4-C2 CHG，再按上述顺序实施；不能用本报告代替 CHG 或验收记录。
