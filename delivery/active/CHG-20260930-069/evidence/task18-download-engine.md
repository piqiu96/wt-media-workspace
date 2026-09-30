# Task 18 证据：下载引擎故障分类硬化

- 日期：2026-09-30
- CHG：CHG-20260930-069（并进任务 18/19，用户裁定）
- 仓库：`wt-media-agent`
- 提交：见文末

## 背景

到对象存储 `s3.oss.longyanyue.cn` 的链路丢包 16.5%，两个故障分类把坏链路变成终态：流被截断（提前干净 EOF）→ `Integrity`（`discard=True`，part 被丢弃从头重下）；连接失败 → `SourceUnavailableError` → 非 retryable 终态。续传机制本身是好的（本次 `transfer_47b242f1…` 第 3 次尝试从 7.25MB 续到完成并 `success`），缺的是分类。

## 测试先行（红）

- 命令：`PYTHONPATH=src python3 -B -m unittest tests.test_transfer_source tests.test_material_download_executor`
- 预期：三个改动点先红 —— 短读仍 `download_integrity_failed`；unreachable host 仍 `download_source_unavailable`；`URLError(OSError)`/`OSError` 仍抛 `SourceUnavailableError`（secret-policy 用例报类型不符）。
- 实际：
  - `test_a_source_shorter_than_the_task_declared_is_a_resumable_stall`：`'download_integrity_failed' != 'download_stalled'`
  - `test_an_unreachable_host_is_retried_then_filed_as_a_stall`：`'download_source_unavailable' != 'download_stalled'`
  - `test_no_error_message_carries_the_address`：`SourceUnavailableError` 与 `SourceStalledError` 类型不符
- 状态：PASS（失败形态正确，共 78 个用例中 3 处红）

## 实现后（绿）

- 命令：`PYTHONPATH=src python3 -B -m unittest tests.test_transfer_source tests.test_material_download_executor`
- 预期：78 全绿。
- 实际：`Ran 78 tests ... OK`
- 状态：PASS

## 全量回归

- 命令：`PYTHONPATH=src python3 -B -m unittest tests/test_*.py`（55 个模块）
- 预期：全绿，尤其 `ContractVocabularyTest`（:1096，错误码词表）不变、`test_an_expired_address_is_not_retried` 仍非 retryable、`test_no_failure_message_carries_the_directory_or_the_address` 不泄露。
- 实际：`Ran 625 tests in 26.3s OK`
- 状态：PASS

## 改动

- `executors/material_download.py`：末尾大小校验 `written < total`（流提前干净结束）→ `Stalled`（`retryable=True`、`discard=False`），part 保留供续传；`written > total` 仍由循环内联 `Integrity` 拦截；摘要不符仍 `Integrity`。
- `clients/transfer/source.py`：`URLError` 非超时分支与 `OSError` 分支改抛 `SourceStalledError`；`HTTPError`（签名过期/403）、`ValueError`（畸形地址）、resume 落点不符保持 `SourceUnavailableError` 非 retryable。
- `clients/cloud/client.py`：`_http_transfer_transport` 增加 `URLError`/`TimeoutError` → `TransferUnavailableError`（executor 已映射 `LeaseUnconfirmed`，retryable）；bind/status 那条不动。
- 错误码词表 `local-error-codes/v1/transfer.yaml` 未动（复用 `download_stalled`，不新增 code）。

## 相关提交

- `wt-media-agent` `01bb2c3`（`feat(chg-069): 任务 18 落档——下载引擎故障分类硬化（早断流可续传、连接失败可重试）`）
