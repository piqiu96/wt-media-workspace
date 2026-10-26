# T-01 激活与素材夹具

日期：2026-10-27

## 激活

- 记录由 `delivery/planned/CHG-20261026-105/` 移入 `delivery/active/CHG-20261026-105/`，`PLANNED → IMPLEMENTING`。
- LEDGER、`delivery/planned/README.md`、M5 里程碑 M5-F、MASTER §3 同步；激活提交 `796751f`（在 `chg/CHG-20261026-105`，随 PR 合入 `main`）。
- `python3 scripts/wt.py chg start CHG-20261026-105`：依赖 CHG-103 的 workspace merge `f2d0e3b` 与 cloud merge `2cd341d` 已并入各自 `main`；workspace 与 cloud 均从 `main` 创建 `chg/CHG-20261026-105`，工作树干净。
- 启动前 `pgrep -fl 'compose-worker|compose-scheduler'` 为空。

## 夹具

团队 1 / `hy` 的 ready 素材都已有 `admin`(1) 或 `operator01`(3) 的 `material_usage`，无法用现有素材证明“创建者与负责人都未加入仍可选材”。使用内容池真实入库路径新建夹具：

```text
source_contents id=906（团队 1 / hy / like_count=258365，hy 内唯一；入库前 status=pending）
repository.Materialize(906, 3, now)  // 真实实现，非直接 INSERT
material id=176
```

读回：

```text
materials            176 / team=1 / source_content_id=906 / created_by=3 / status=available / video_status=not_downloaded
source_contents      906 / status=material_created / material_id=176 / game_id=hy / like_count=258365
material_usages      material_id=176 计数 0（创建者 1、负责人 3 均未加入）
```

执行方式：在 Cloud 仓根临时使用 `bootstrap.InitializeServer()` 初始化真实数据库连接，调用 `repository.Materialize`，运行后删除临时程序；未直接插入素材行。

## 清理登记

归档后删除 `materials` 176，并把 `source_contents` 906 恢复为入库前状态（`status=pending`、`material_id=NULL`）；同时删除本 CHG 产生的策略/任务/成片/usage。对象存储中的源文件与成片按用户口径不删除。

## 边界

- 夹具只在本机开发库；素材 176 在走查期间用于定时与立即执行选材。
- 该素材从未加入任何用户工作集；若后续自动任务需要源文件，由 Cloud `worker` 的 `material_source_prepare` 下载。
