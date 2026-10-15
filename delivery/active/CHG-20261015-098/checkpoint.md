# CHG-20261015-098 Checkpoint

## Completed

- M5-C1～C6 已归档，M5-C7 §6/§7/§8 是当前唯一未闭环阶段；Workspace、Cloud、Agent、Desktop 起点均为干净工作区。
- 已建立 M5-C7 单一全链验收 CHG，沿用 Cloud 合成、Agent 下载、Desktop 壳的现有职责。
- T-01：强制停止旧进程、迁移并重建 Cloud/Agent/Web/打包 Desktop，健康、BitBrowser、产物新鲜、登录及 DMG 启动 gate 全部 PASS；证据见 `evidence/T-01.md`。
- T-02：独立 Compose Scheduler/Worker 真实到点、容量与候选跳过、双 Scheduler 同槽去重、真实混合批次、成片对象 SHA256 与 FFprobe 对账通过；见 `evidence/T-02.md`。

## Current

- T-03：Cloud Web、打包 Desktop、Local Agent 下载和 M4 人工链路。

## Next

1. 在当前真实成片 40/41 上验证 Cloud Web 与打包 Desktop 页面及 Local Agent 实际下载。

## Blockers

- None.

## Recent verification

- `delivery/LEDGER.md` 和 `.ai/CURRENT_CONTEXT.md` 在激活后按脚本校验；治理与产品主计划对齐 PASS。
- T-01 `scripts/m2b-local-acceptance.sh --force-restart all` 退出码 0，全部 gate PASS；脚本不包含 Compose Scheduler/Worker。
- T-02 任务 249/251 的真实对象大小、SHA256、FFprobe 通过；混合批次任务 250/251 的 API 统计为成功 1、失败 1，同槽运行记录 1 条。
