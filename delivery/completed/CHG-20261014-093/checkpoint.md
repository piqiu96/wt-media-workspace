# CHG-20261014-093 Checkpoint

## Completed

- 用户确认首版范围：引导视频插入、插入位置、时长控制、画中画；后续改为策略填写可下载地址，转链接另放独立运营工具。
- Product、Engineering 与 M5 §4a 已同步；CHG092 已归档。
- T-01～T-04：HTTPS 地址校验及受限下载、两个固定 FFmpeg 模板、任务快照与策略页面已完成；Cloud `7beb3dd`。
- T-05：已先部署新 API 与 Worker，再发布 `guide_insert` / `guide_pip` v1；真实对象存储下载与合成读回通过。真实任务 36 成功，成片 13 可在“我的成片”查询，预览链接返回 206。

## Current

- Cloud `7beb3dd`、`93e6e94` 已提交；CHG 归档。

## Next

- 完成 CHG093 后按 M5-C3 继续 Worker 资源控制。

## Blockers

None.

## Recent verification

- `WT_MEDIA_LIVE_GUIDE=1 WT_MEDIA_LIVE_GUIDE_TASK=1 WT_MEDIA_LIVE_MATERIAL_ID=175 WT_MEDIA_LIVE_ACTOR_ID=3 go test ./internal/modules/production/service -run '^TestLiveGuideDownloadComposeAndStorageReadback$' -count=1 -v`：自动选择对象存在的素材 161，任务 36 成功、成片 13（68074 字节）、预览 206。
- 第一次真实任务使用素材 175，发现旧数据的源对象已不存在；任务 35 以 `storage_error` 失败且未产生成片。改用可读回素材后通过。
- `go test ./internal/modules/production/service ./internal/modules/production/compose ./internal/modules/production/executor` 通过；真实 FFmpeg 插入、画中画、时长和对象存储验证通过。
- Cloud `93e6e94` 提交真实链路验证代码，`git diff --check` 通过。
