# 治理验证读数

执行日期：2026-10-22。分支：`chg/CHG-20261022-100`（Workspace、Cloud、Agent、Desktop 同名）。
Workspace 命令使用带 PyYAML 的 venv：`/private/tmp/wt-verify-venv/bin/python -B -X pycache_prefix=/tmp/wt-pyc-empty`。

## 1. 文档与门禁

| 检查 | 结果 |
| --- | --- |
| `python3 scripts/docs/check.py` | `docs governance ok (15 indexes)` |
| `tests.test_docs_check` | 19 tests OK（历史目录标记、`index/never`、`SUPERSEDED` 三类正反例保留） |
| `scripts/verify/verify_delivery_governance.py` | exit 0；归档写入 0 处；归档后 Active：098 |
| `scripts/verify/verify_product_master_alignment.py` | exit 0 |
| `scripts/verify/verify_ai_workspace.py` | exit 0；归档前快照 1050 字符，归档后指向 098（967 字符） |
| `scripts/verify/verify_skills.py` | exit 0；10 个源文件 |
| `scripts/sync_skills.py check` | `skill outputs are up to date` |
| `scripts/verify/verify_m0_config.py` | exit 0 |
| `python3 -m unittest discover -s tests` | 174 tests OK |
| `scripts/wt.py chg resume CHG-20261022-100`（归档前） | 快照只含当前 CHG 元数据与 References；不含 completed／reports／历史材料。归档后快照按唯一 Active CHG-098 重建（967 字符） |

## 2. 引用闭合

扫描范围：`docs delivery/active delivery/planned delivery/milestones AGENT-INDEX.md README.md scripts skills tests config templates`，先 `git add` 再 `git grep --cached`。

- 已删除路径（`docs/superpowers`、9 篇报告、第四章、launch-engineering 规格）：除本 CHG 记录外命中 **1** 处。
  - `docs/decisions/0013-m3-content-mining-entry.md:54`：指向 **Cloud 仓**的 `wt-media-cloud/docs/superpowers/...`，不是本次删除的 Workspace 目录，按决定保留。
- 阳性对照：同一模式在 `delivery/completed/` 命中 **34** 个文件。0 命中若无此对照不算证据。
- `SUPERSEDED` 状态标记：**0**（`docs/standards/...` 与 `docs/README.md` 中的 12 处均为词汇定义/检查器说明，不是文档标记）。
  - 阳性对照：`git show 4c7e960^:docs/product/prd/详细文档/第四章_内容发现.md` 第 3 行确有 `**SUPERSEDED**` 标记。
- 当前文档指向 `delivery/completed/` 的引用 **56** 处，逐条为目标记录的“实施记录／签收记录／依据证据”；核心规则均已在正式 SSOT 中，无一处需要读归档才能理解当前规则。

## 3. 运行仓

| 仓库 | 检查 | 结果 |
| --- | --- | --- |
| Cloud `ff1bf90` | `gofmt -l` | 无输出 |
| | `go build ./...` | exit 0 |
| | `go test ./internal/modules/cloudagent/repository/...` | ok |
| | `npx vitest run src/modules/materials/pages/MyMaterialsPage.test.js`（在 `web/` 下） | 23 passed |
| Agent `5c61f95` | `unittest tests.test_dependency_boundaries tests.test_cloud_agent_client tests.test_cloud_transfer_client` | 74 passed |
| Desktop `81d8ea0` | `rustfmt --edition 2021 --check src/logging/rolling.rs src/logging/test_support.rs` | 无差异 |
| | `cargo check` | exit 0 |
| | `cargo test --bin wt-media-desktop-shell logging::` | 103 passed |

三个运行仓的改动均为注释；`git diff -U0` 过滤后无代码/格式行变化。Desktop 未跑全仓 `rustfmt`（该仓本就不是 rustfmt-clean），只对改动文件做单文件检查。

## 4. 工作树

各仓提交后 `git status --short` 为空；未推送、未建 PR。远端对账在收尾时用 `git ls-remote` 复核。
