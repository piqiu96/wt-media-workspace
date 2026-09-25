# `delivery/completed/` — 只读归档

- 归档边界：`READ-ONLY`

本目录是**已收口的交付记录**（Milestone／CHG 的 `change.md`、`checkpoint.md`、`evidence/`）的存放处。
它不是活文档树，也不承载任何当前事实。

## 边界

- **不默认加载**：除非当前任务明确指出某一篇记录，否则不进上下文（`AGENT-INDEX.md` §4「默认不加载」）。
- **不回改**：记录一旦归档即保持原样，不重写、不合并、不重排、不"内容整合清除"。历史状态词、过时读数、
  过去时叙述、已失效的路径一律**保留**——它们是当时事实的存档，不是待修的缺陷。（`MASTER_IMPLEMENTATION_PLAN.md` §3 历史词汇段）
- **不作为当前状态依据**：当前状态以 `.ai/CURRENT_CONTEXT.md`、`delivery/LEDGER.md`、`delivery/active/`
  与稳定基线（`docs/product`、`docs/engineering`、`docs/contracts`、`docs/decisions`）为准。
- **可整目录排除**：全仓范围的扫描（grep、索引、审计）可以且应当排除本目录，以免历史噪声淹没活文档。
  没有任何静态门禁因本目录的存在与否而改变结论（CHG-20260925-066 `evidence/artifacts/t01-f07-completed-moved.out`）。
- **归档 ≠ 删除**：收口一个 CHG 时，从 `delivery/active/` 与 `delivery/LEDGER.md` **移出**它，并把记录**移入**本目录。
  记录本身**不删除**。`README.md` §Rules 与 `LEDGER.md` 首段里的 "remove" 指的正是这次「移出」，不是删文件。

## 新增捕获的入库阈值

- **单个原始捕获文件超过 256 KB 的不入库**（日志、JSON 抓取、`.out` 原始输出等）。
  确需保留的，在所属记录的 evidence 中**显式写明理由**（例：`CHG-20260923-055` 的截图是 CSP 布局缺陷的
  唯一判据，故保留）。
- 记录应保存**可复现的命令 ＋ 结论摘要**，让读者能重跑，而不是保存整段原始输出。

## 已知例外（本边界不是绝对的）

- `scripts/verify_m3_acceptance.py` **读取** `CHG-20260916-052/evidence/m3-e3-acceptance-20260923/` 下的
  原始日志与快照（如 `raw/p10-*.log`）。该包因此必须留在原处，**不属可删范围**。
- 该脚本此前的**写入**面也指向同一目录（`state.json`、`run-manifest.json`、`proc-<component>.log`、
  基线快照、scheduler 日志），这使「已归档」在事实层面并非只读。写入面已由
  CHG-20260925-066 T-03 移出本目录。
- 因此本目录的只读性由 `scripts/verify_delivery_governance.py::check_archive_readonly` 强制：
  任何已跟踪脚本对本目录前缀的**写**操作都会被报出。

## 目录内不含什么

- 不存放运行时代码、构建产物或临时文件。
- 不存放当前有效的产品／工程／协议／决策基线——那些在 `docs/` 下。
