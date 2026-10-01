# CHG-20260930-071 核验登记（2026-10-01）

- Status: `PLANNED`（保持；§0 明确 Q-01～Q-06 关闭前不激活，本记录无可执行范围）。
- 本文件是 2026-10-01 对「是否已执行」的核验结论登记，**不是**实施 checkpoint，也不改变本 CHG 状态。

## 2026-10-01 核验：未执行，仍被 Q-01 / Q-04 阻塞

用户以为本 CHG 已执行过；对 `wt-media-cloud` main（`594a99c`）只读核验结论如下：

- **素材状态写路径不存在**：`internal/modules/production/router.go` 仅有 6 条素材路由（`GET /api/v1/materials`、`GET /api/v1/materials/:material_id`、`GET /api/v1/materials/:material_id/video-url`、`POST /api/v1/materials/:material_id/usages`、`POST /api/v1/materials/:material_id/downloads`、`GET /api/v1/my-materials`），**没有任何改状态的口**；`handler.go` 里也没有暂停/下架的写操作。
- **使用情况统计无数据源**：全库没有素材维度的成片数 / 发布数 / 最近生产 / 最近发布聚合（依赖未落地的 M4-B `compose_task` 与 M4-C 成片/发布记录，见 §4 `Q-04`）。
- **读侧已交付**：`materials.status`（`available / paused / delisted`，`NOT NULL DEFAULT 'available'`）、Business Schema `Material.status`、投影与 `wire_test` 分母、两处页面读真值，已由 CHG-20260930-069 任务 12 交付（cloud `71deb48`）。用户印象可能与此混淆。

## 阻塞项（激活前必须逐条关闭）

- `Q-01`：写入口未裁定——谁来暂停/下架、在哪一页操作（069 归档遗留项 c 指向本项）。
- `Q-03`～`Q-06`：见 change.md §4，其中 `Q-04` 依赖 M4-B/C 落地。

## 用户裁定（2026-10-01）

保持 `PLANNED` 阻塞、登记本次核验；等 Q-01 裁定 + M4 依赖落地再激活。
