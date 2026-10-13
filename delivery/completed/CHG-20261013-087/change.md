# CHG-20261013-087：M4 下载走查缺口修复

- Status: DONE
- Level: M
- Milestone: `delivery/milestones/M4-content-production.md`
- Closure anchor: §3.1 M4-C7；§6 下载与发布衔接；§7 M4-AC-08/09；§8 DONE Gate
- Product: `docs/product/prd/详细文档/第五章_素材生产.md` §5.9.1、§5.9.9
- Affected repository: `wt-media-cloud`（Cloud API、MySQL、Cloud Web/Desktop 共用 Vue）

## 结果

运营能在“我的成片”首次发起成片下载；下载中心能清理自己的已结束下载记录，清理后列表不再显示该记录，但下载任务事实、素材、成片和本地文件仍保留。素材与成片即使数字 ID 相同，也各占一行。

## 设计边界

- “首次下载”复用已验收的 `POST /compose-outputs/{id}/downloads` 和 `createOutputDownload`，成功后打开现有下载中心；不另建下载流程。
- “清理显示记录”只允许任务发起者清理 `purpose=user_download` 的 `success/failed/cancelled` 终态。新增 `file_transfer_tasks.hidden_at`；会话列表过滤隐藏行，任务读回、执行、审计和素材下载状态投影不受影响。新增会话端点 `POST /file-transfer-tasks/{task_id}/hide`，旧客户端兼容。
- 下载中心按 `(asset_type, asset_id)` 收敛行，避免同数字 ID 的素材与成片互相覆盖。
- 不删除数据库任务、不删除本地文件或对象、不触碰 Agent/桌面原生执行路径；“去发布”仍只传 `output_id`，发布属于 M6。

## 有序任务

| Task | 结果 | 验证 |
| --- | --- | --- |
| T-01 | 修正里程碑状态并新增 Cloud 合同、迁移 | 合同解析；迁移可重复检查且不改变旧任务事实 |
| T-02 | Cloud 软隐藏 Repository/Service/Handler | 权限、终态限制、列表隐藏、下载状态保持、真实 MySQL/API 读回 |
| T-03 | 共用 Vue 首次下载、清理显示和行键修复 | 页面接线与交互测试；Cloud/Desktop 构建 |
| T-04 | 真实环境走查与回归、交付收口 | 成片首次下载→同 Drawer→本地文件；清理前后 DB/API/UI 对照，三仓事实不受影响 |

## 验收

1. 从“我的成片”点击下载可创建真实任务，下载中心出现 `composite_output` 行，本地文件大小和 SHA256 与成片一致。
2. 同数字 ID 的素材与成片下载记录同时可见；重下仍按各自资产类型调用对应端点。
3. 本人终态用户下载可隐藏且列表读回不见；他人、未结束或 Cloud 准备任务不可隐藏。隐藏不改任务状态、资产、对象和本地文件，也不改变素材下载状态。
4. Cloud Web/Desktop 共用页面与合同、迁移、测试通过；M4 仍须用户完成 UI 签收才可标 DONE。

## Pending Questions

None.

## 验收结论

T-01～T-04 均已完成，证据见 `evidence/`。成片首次下载、本人显示记录清理、权限边界和本地文件完整性通过机器验收。M4 的人工页面走查与用户签收继续按里程碑 §8 执行。
