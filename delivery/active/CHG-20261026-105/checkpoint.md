# CHG-20261026-105 Checkpoint

日期：2026-10-27 04:00（T-01～T-07 完成并有证据，文档与记录已同步，待门禁/PR/归档）

## 已完成

- Cloud 实现与合同：迁移 075 两表 `material_usage_id` 可空（`3fe596b`）；团队素材候选（`ac3a776`）；高级运营团队策略范围（`f9c3114`）；`/runs/tasks` 与批次合同（`fbbda88`）；实时用例夹具同步（`c4ade76`、`1052975`、`5b94676`）。
- T-01 激活与素材夹具 176（来源 906，无任何 `material_usage`）；T-02～T-05 证据分别见 `evidence/T-02`～`T-05`。
- T-06 真实定时全链：独立 `compose-scheduler`、Cloud `worker`（`material_source_prepare`）与 `compose-worker`，任务 350 → 成片 77；任务/成片 `material_usage_id` 为 NULL、负责人 3、创建者 1；对象 Stat/SHA-256/FFprobe 与 DB 一致。
- T-07 立即执行与并发：真实 HTTP run-now（同 key 重放同一 run、换 key `previously_run`）、双 scheduler + 重启（1 run/1 task、0 新增）、双 worker 抢同一素材（node 1/2 各 1 次 attempt，成片 78/79 对象键不同）、额度/负责人失效/跨团队/人工入口与重试回归；同步四个 live 用例，全量测试全绿。
- 文档：PRD §5.6.1/§5.7.4、工程规格 §12.1、ADR-0023 2026-10-27（CHG-105）追加决议；M5-F 与 MASTER 在归档时置 DONE/计数。

## 当前工作

记录为 `VERIFYING`；代码、合同、文档与证据完成。执行收尾门禁后推送 Cloud 分支开 PR，再合并、归档。

## 下一步

1. 运行 Cloud `go test ./...`、Cloud Web Vitest、Workspace 全量与 `verify_m0_config.py`、`wt chg verify`。
2. 推送 Cloud `chg/CHG-20261026-105`，开 PR，CI 通过后合并并记录 merge SHA。
3. Workspace：`change.md` 置 `DONE` 并登记 Cloud merge SHA；`git mv` 到 `delivery/completed/`；LEDGER 删行；M5-F 置 `DONE`（M5 总体保持 `IN_PROGRESS`）；MASTER §3 按目录实测重算；跑治理与产品对齐校验；推送 PR、合并。
4. 归档后清理夹具：策略 93～98、66；任务 387～391、350；成片 77～79；素材 176；来源 906 恢复 `pending`/`material_id=NULL`；相关 run/task/output/attempt/usage 行；删除 `/tmp/chg105-*`、会话令牌与探针；保留审计日志与对象存储对象；停 scheduler/worker 进程。

## 阻塞

无。

## 夹具与清理

- 策略：93、94、95、96、97、98（本 Task 新建）、66（T-06 建）；任务：387、388、389、390、391（本 Task）、350（T-06）；成片：77（T-06）、78、79（T-07）。
- 素材 176 与来源 906：素材行删除，来源恢复 `pending`、`material_id=NULL`、`video_status` 清理；`material_usage` 未新增。
- 保留：审计日志、对象存储对象（`compose-outputs/350/…`、`387/…`、`388/…`、`…/389` 若有）、`/tmp/chg105-t07` 中的下载副本与日志在归档后删除。

## 最近验证

```text
Cloud go test ./...                       全绿（T-04 读数 72 包 ok）
Cloud Web（web/ 下）Vitest                 80 文件 / 737 用例通过（T-04 读数）
Cloud live（LIVE_DB=1 + SCHEDULER_PROCESS=1）全绿，四个改造用例 PASS
```
