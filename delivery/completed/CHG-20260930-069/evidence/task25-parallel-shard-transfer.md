# Task 25 证据：执行器并行分片

- 日期：2026-10-01
- CHG：CHG-20260930-069
- 仓库：`wt-media-agent`（一提交）
- 提交：`ac2ed81`（`feat(agent): 下载并行分片（任务 25）`）

## 改动

`executors/material_download.py` 新增常量 `DEFAULT_SHARD_COUNT = 8`、`MIN_SHARD_BYTES = 4 MiB`、`DEFAULT_SHARD_POLL_SECONDS = 0.5`（都是构造函数可注入的模块常量，对齐既有 `DEFAULT_CHUNK_BYTES` 范式 —— **不是**契约字段，也不是配置项）。

- `_attempt` 拆出 `_classify_transfer_error` 供线程体复用同一套分类；
- `_transfer` 成为分派器，原主体**原样**搬进 `_transfer_single`；
- `_plan` 判定顺序（**这个顺序是对的，别换**）：`count == 1` → 单流；存在分片 part（含序号 ≥ count 的残留）→ 分片；否则存在正式 `.part` → 单流（改动前就在下载中的旧任务，不能静默丢用户进度）；否则 → 分片；
- `_transfer_sharded` + `_shard_worker`：`ThreadPoolExecutor`（stdlib，ADR-0016 禁的是 `os/socket/http/urllib/subprocess/sqlite3/ctypes/requests`，**没禁 `threading`/`concurrent.futures`**；HTTP 仍只经 `clients/transfer.open_source`）。分片线程只做「读网络 + 追加自己的 part + 累加一个加锁的总数」；**主线程独占** `_Progress.note`，所以进度上报与心跳仍是既有的 ~2 秒窗口语义；
- 收尾：逐分片校验 `size == region_len`，再 `assemble_shards` 顺序拼装，同一次读里算整份 sha256（sha256 不可由分片摘要合成，这一遍躲不掉）。
- `_prepare` 的 `require_room` 在分片路径上按 **2×** 申请；`_report_failure` 的 `completed_bytes` 改用 `written_bytes`。

## 三种情况回退到单流，且服务端不认 Range 的回退**在同一次尝试内**

`200` 不是故障，不该吃掉 attempt 预算。判据落在**任何 `offset > 0` 的分片拿到 `range_honoured == False`**（分片 0 本来就不发 Range 头、拿 200 整份，它只读自己那一段，这是正确的）。

「206 但 `Content-Range` 起点不符」判 `SourceUnavailable`（非 retryable）而不是 `Integrity`，是**照既有**：`clients/transfer/source.py` 已经这么判，任务 18 也定过「resume 落点不符非 retryable」。一致性优先于自创。

## 先红

命令：`PYTHONPATH=src .venv/bin/python -B -X pycache_prefix=/tmp/wtmedia-pycache -m unittest tests.test_material_download_executor`

红：`TypeError`（`shards=` 不存在）。同样，**红本身什么都证明不了** —— 真正的判据是下面 22 条变异。

## 计划里那条「隐藏必改项」，实测不是隐藏的

计划要求「`DownloadTest.executor` 必须显式传 `shards=1`，否则既有单流臂会静默切到分片路径」。实测：既有臂的 body 是 4096 字节，`4096 // 4 MiB == 0` → 分片数本来就是 1，**不会**静默切换。仍然显式钉上 `shards=1`，但理由写成「这些臂说的是单流路径，一个只是**碰巧**单流的臂，会在阈值移动的那天开始量另一条路」，而不是报告一次险情。

计划另要求给 `ServingOpener` 的 `pop(0)`/`append` 加锁（分片臂会并发调用）。**没有加**：`list.append`/`pop` 在 GIL 下本就是原子的，加一个从不获取的 `threading.Lock` 是装饰。先确实写了那把锁和一段「防日志交织」的注释，自查时发现从没 acquire，改回成一句实话 —— 那些按调用次序写的脚本（n 次调用返回第 n 个）要求**单一调用者**，这才是真的约束。

## 变异（22 条，全部先红后还原）

覆盖的关键性质：分片区间**无缝隙无重叠**（不均分 `[0, 4096, 8191, 12286]`）、拼装按序号、每分片独立续传、`written_bytes` 不误伤 `a`/`a1`、Range 盲真的回退、旧 `.part` 真的走单流、`require_room` 真的按 2× 拒、混合故障的仲裁（非 retryable 优先、非 `DownloadFault` 原样抛）、合并被中断后重做、计划漂移两个方向（分片数变多/变少）。

**并发要真的并发**：`threading.Barrier(SHARDS)` 放进假 opener —— 串行实现会超时失败，这条臂不是「睡一会儿看看」的时序测试。

## 全量回归（均在最后一次改动之后重跑）

- 定向 `tests.test_download_sink` + `tests.test_material_download_executor`：**138 用例 OK**；
- 全量 `PYTHONPATH=src python3 -B -X pycache_prefix=<空目录> -m unittest discover -s tests -p 'test_*.py'` → **677 用例 OK，rc=0**（连跑三次一致）；
- ADR-0016 边界套件 **33 用例 OK**。

## 未做的端到端（登记为待执行，见 checkpoint）

计划要求的真实链路验证（重启 8765 上带 runner 的 Agent、下一个已就绪素材、量分片文件数/速率时间序列/最终文件名与 sha256、判据是相对今天的单流 94.6 KB/s 的 ~8×）**尚未执行**。原因与处置见 checkpoint 的 Blockers：那条链路要重绑节点，而重绑只能由用户在 App 里点。

本任务能提供的最强替代读数在任务 26 证据里：**同一个对象、同一条链路、今天**，生产适配器签发的地址 Range GET 回 `206 bytes 0-1023/48511909`，而同一 key 的**无签名**地址回 403 —— 分片所依赖的 Range 前提与签名前提都是今天现测的，不是引用昨天的实验。**但「8 条流聚合到 ~8×」这一条仍未在真机整链上量过。**

## 已知代价（写进证据，不埋在代码里）

故障时的一次尝试最多多等**一个 socket 超时**：`shutdown(wait=True)` 会等运行中的分片在下一块察觉 `stop`。未启动的 future 靠 `cancel_futures=True` + worker 开头查 `stop` 收掉。
