# T-01 本地启动环境遗漏合成 Worker 的补验

Date: 2026-10-21
Status: WORKER_RUNNING；用户页面走查仍待签收

## 触发与根因

- 用户在合成任务页看到 316～319 持续「排队中」。检查本机进程时，Cloud HTTP（PID 87921）与 Discovery Worker（PID 87936）运行，但没有 `compose-worker` / `compose-scheduler` 进程。
- MySQL 中 316～319 均为 `pending`、`attempt_count=0`，`running=0`。Cloud `/api/v1/health` 正常，不能证明合成队列有人领取。
- `scripts/m2b_local_acceptance.py` 的 `up` / `all` 只启动 Discovery Worker；`verify` / `status` 也只检查这个 Worker，所以本地环境可报健康而合成队列无人消费。Cloud 的 Linux 发布构建、打包与部署清单已有 `compose-worker`，遗漏仅在 Workspace 本地启动脚本。

## 修复与读回

- 本地启动脚本增加从当前 Cloud 源码构建并托管 `./cmd/compose-worker`；`up` 和 `all` 均启动它，`verify` 与 `status` 均检查它，`stop` 在清理 PID 文件前发送 SIGTERM 并等待进程退出。
- 先运行 `scripts/m2b-local-acceptance.sh status`，返回 exit 1，指明 `compose-worker: pid=- alive=no`。随后单独调用新启动函数，不重启当前 Cloud/Desktop；构建的 worker 以 PID 91351 运行。再次执行 `status` 返回 exit 0，`compose-worker: pid=91351 alive=yes`。
- 启动后 MySQL 同时读到 316、317 两条 `running`，两者 `started_at=22:35:10`、`attempt_count=1`；316 于 22:35:38 `success`，318 于 22:35:40 占用空出的槽并于 22:36:44 `success`。319～321 在 22:36:46～50 依次被领取，均以 `input_missing` 结束；至此这些任务已离开队列。
- 319（素材 154）、320（素材 160）、321（素材 159）的 `error_message` 均明确为 `source object is gone` / `object storage key does not exist`，分别指向 `materials/<素材ID>/...mp4`。这是源对象缺失的数据问题，不能通过增加并发或重启 Worker 解决；如要重试，先恢复对象或改用仍存在的素材。
- 317 的 FFmpeg 子进程已启动，命令计划生成约 376 秒视频；记录时它仍在运行，不能将剩余任务写成成功。

## 并发与限制

- `config/scheduler/compose.toml` 与 `config_online/scheduler/compose.toml` 均为 `node_id=1`、`concurrency=2`、`global_concurrency=2`；数据库 `compose_worker_capacity.id=1` 的 `max_running=2`。真实领取过程也观察到同时最多两条 `running`。
- 本地脚本此次只补合成 Worker。`compose-scheduler` 仍未由本地脚本托管；这不影响截图中的人工创建任务，但自动定时触发仍需独立 Scheduler 才能执行。

## 验证

- 新生命周期单测先红（三项：启动、状态、验收），修复后通过；启动断言同时覆盖 `up` 与 `all`。
- Workspace 全套 `/tmp/wt-media-workspace-verify-20261021/bin/python -m unittest discover -s tests -q`：121 项通过（扩大 `all` 断言后复跑）。
- `python3 scripts/verify_delivery_governance.py`、`python3 scripts/verify_ai_workspace.py`、`git diff --check` 均 exit 0。
- 本次没有重新打包 Desktop、没有执行 `all --force-restart` 全量验收，M5-AC-13 与 M4-H2 继续等待用户页面走查结论。
