# Task 24 证据：分片 part 文件的存储层支持

- 日期：2026-10-01
- CHG：CHG-20260930-069（并行分片折进本 CHG，用户裁定）
- 仓库：`wt-media-agent`（一提交）
- 提交：`d5cf2a7`（`feat(agent): 分片 part 文件的存储层支持（任务 24）`）

## 背景

诊断证据 `download-slow-diagnosis-experiment.md` 的结论：对象存储对**每条 TCP 流**限速 ~112–160 KB/s，聚合随连接数线性增长（8 流 8.44×、64 流 80 Mbps 撞线路），且全程回 206 —— **分片不必动基建**。Agent 的下载引擎严格单连接串行，46 MB 素材要 ~8 分钟、只用掉线路 0.9%。任务 24 只做存储层：让 N 条连接各写自己的 part 文件。**本任务没有任何调用方**（执行器在任务 25 才接上），所以它只增加 API 与测试。

## 设计取舍：分片 part 文件 + 收尾拼装，不是「预分配 + 定位写」

既有不变式是**磁盘文件大小是唯一的续传依据**（`download_sink.py` `resume_offset` docstring 明写「不信 checkpoint」）。定位写进一个预分配文件会让大小在第一次 `truncate` 后就恒定，只能靠一份持久化的分片账本续传 —— 正是这条不变式要防的「账本超前于磁盘 → 跳过丢失的字节」。所以每个分片写自己的 `<safe_task_id>.part.<k>`，各自**只追加**，各自的大小就是它自己的续传依据：**零新增持久化**，崩溃一致性与改动前相同。代价是拼装期间磁盘峰值 2×。

## 新增 API

`part_path(task_id, shard=None)`（`None` 保持 `<safe>.part`，负序号 `ValueError`）、`shard_offset`、`append_shard`、`assemble_shards(task_id, count, consume)`（`"wb"` 打开、顺带截断上次中断的合并；哈希留在执行器，存储层不做哈希）、`written_bytes`（失败上报用）、`shard_indices`。`discard` 扩展为连所有分片一起去掉；`commit` 在 `replace` **之后**清理分片（先删会把 re-merge 需要的字节丢掉）。

匹配一律用**精确词干**（`name == f"{safe}.part"` 或 `f"{safe}.part." + 数字`），不用 `glob(f"{safe}.part*")` —— 任务 `a` 不能删掉任务 `a1` 的文件。

## 先红

命令：`PYTHONPATH=src .venv/bin/python -B -X pycache_prefix=/tmp/wtmedia-pycache -m unittest tests.test_download_sink`

红：`AttributeError`（`part_path(t, 1)` / `shard_offset` / `assemble_shards` / `written_bytes` / `shard_indices` 都不存在）。**红本身什么都证明不了**，见下变异。

## 我在自己刚写的代码里改到的一个缺陷

`written_bytes` 第一版把该任务拥有的**所有** part 文件大小相加，于是「拼装完成、尚未 commit」这个窗口里它是 `2 × total`，而 `_report_failure` 把 `completed_bytes` 直接取自它 → 上报给 Cloud 的进度超过总长。抓法不是推演生产者，而是**跟着消费者走**（读 `_report_failure` 的调用点）。两条红用例（`8 != 4`、`5 != 4`）后改成 `max(合并文件, 分片之和)`：分片划分对象，合并是它们拼接的前缀，所以「看得见的更多的那一份」就是答案。修正后 amend 进任务 24 的提交。

## 变异（13 条，全部先红后还原）

每条新断言配一个能把它变红的变异；还原后逐文件 sha256 与变异前一致。覆盖：分片命名互不相同、负序号拒绝、合并按序号、合并截断陈旧 part、`shard_indices` 三臂、`written_bytes` 三臂（含**不重复计数已完成的合并**）、`discard` 不动邻居任务、`commit` 连分片与目录一起收。

**登记一条等价变异**：`_task_parts` 里那个 `.isdigit()` 子句在任何输入下都不可达（前缀 `f"{stem}."` 之后必然全是数字）。与其为它编一个夹具，不如**把匹配器简化掉**。这不是「测试漏了」，是那段代码本身多余。

## 全量回归

- 定向：`tests.test_download_sink` + `tests.test_material_download_executor` 共 **138 用例 OK**；
- 全量：`PYTHONPATH=src python3 -B -X pycache_prefix=<空目录> -m unittest discover -s tests -p 'test_*.py'` → **677 用例 OK，rc=0**；
- ADR-0016 边界套件 `tests.test_dependency_boundaries` **33 用例 OK**（`threading` / `concurrent.futures` 不在 `EXECUTOR_DENIED_MODULES` 里；HTTP 仍只经由 `clients/transfer`）。

（以上计数均在最后一次改动之后重跑，不是从上一任务搬来的读数。）

## 未做

不引入任何持久化的分片账本；不改 `LocalLease`、契约、`info.version`、`contract-map.yaml`、`REQUIRED_LEASE_FIELDS`（分片只是对同一个 signed URL 发 N 条带 `Range` 的 GET，契约里没有任何一条承诺或禁止单流/连接数）。
