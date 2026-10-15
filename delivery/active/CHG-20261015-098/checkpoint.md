# CHG-20261015-098 Checkpoint

## Completed

- M5-C1～C6 已归档，M5-C7 §6/§7/§8 是当前唯一未闭环阶段；Workspace、Cloud、Agent、Desktop 起点均为干净工作区。
- 已建立 M5-C7 单一全链验收 CHG，沿用 Cloud 合成、Agent 下载、Desktop 壳的现有职责。
- T-01：强制停止旧进程、迁移并重建 Cloud/Agent/Web/打包 Desktop，健康、BitBrowser、产物新鲜、登录及 DMG 启动 gate 全部 PASS；证据见 `evidence/T-01.md`。
- T-02：独立 Compose Scheduler/Worker 真实到点、容量与候选跳过、双 Scheduler 同槽去重、真实混合批次、成片对象 SHA256 与 FFprobe 对账通过；见 `evidence/T-02.md`。
- T-03：operator01 人工任务 252 → 真实 Worker 成片 42 → 打包 Desktop sidecar 经 `transfer_02cfdc38…` 实际落盘，声明 SHA = 校验 SHA = 本地 SHA，FFprobe 1.000s；自动成片 40/41 与人工成片 42 同表同链路读回；见 `evidence/T-03.md`。
- T-04：`production_rule`/`compose_pool_item` 三仓零命中（带阳性对照）、Agent 执行器仅下载、Desktop 无合成执行；T-02 临时关系 82/83/85 清理、策略全部停用、无残留进程；M5-AC-01～12 已收口 PASS；见 `evidence/T-04.md`。

## Current

- 等待用户最终走查签收（M5-AC-13 + M4-H2，同场完成）。

## Next

1. 用户按真实计划流程在 Cloud Web 与打包 Desktop 走查：策略页（启停/计划）、任务页（按触发方式筛人工/自动）、我的成片（预览自动成片 40/41 与人工成片 42）、下载中心（transfer_02cfdc38 进度与 hash 徽标、本地文件 `20261015/三角洲-42-成片-42.mp4`）。
2. 用户签收后：更新 M5-AC-13 与 M4-H2、归档本 CHG、按需处理归属事实（如需 senior/admin 本机演示自动成片下载，先做设备绑定供给）。

## Blockers

- None.（页面可视走查必须由用户完成，属于签收步骤而非阻塞。）

## Recent verification

- T-03：`transfer_02cfdc38af2b573063ab72de` success，278362/278362 字节；三方 SHA 闭合 `39025ff4…ca600`；FFprobe 1.000000 秒；重复下载幂等单行。
- T-04：三仓 `production_rule`/`compose_pool_item` 0 命中（阳性对照命中）；`compose_tasks` running=0；策略 23/24/25 `next_run_at=NULL`。
- 治理与产品主计划对齐校验在提交时随脚本复跑。
