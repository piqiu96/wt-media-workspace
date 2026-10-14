# CHG-20261014-092 Checkpoint

## Completed

- T-01：迁移 058 增加计划时间槽唯一键、调度运行记录和逐素材跳过原因。
- T-02：事务锁定策略、按创建人的有效“我的素材”筛选、单次/每日限额、到点入队与下次计划推进。
- T-03：独立 Compose Scheduler、立即执行 API、运行记录 API、任务触发方式筛选与策略详情读回。
- T-04：本地 MySQL 的两进程并发和重启仅创建一条任务；事务边界、限额、跳过原因读回、Cloud/Desktop 构建均通过。

## Current

- Cloud `d6aad32` 已提交；CHG 归档。

## Next

- M5-C3 Worker 资源控制；另按用户新增要求规划引导视频上传与合成模板能力。

## Blockers

None.

## Recent verification

- `WT_MEDIA_TEST_SCHEDULER_PROCESS=1 ... go test ./internal/modules/production/repository -run TestLiveComposeSchedulerProcessesDeduplicate -v`：两进程 1 run / 1 task，重启仍 1 task。
- `WT_MEDIA_TEST_LIVE_DB=1 ... go test ./internal/modules/production/repository -run TestLiveComposeScheduleDueAndRepeatScan -v`：限额与跳过理由通过。
- Production Go 定向测试、35 个 Web 测试、Cloud/Desktop 双构建、Linux 打包测试、Contract YAML 校验通过。
