# T-15 四仓合并与 CHG-101 收口

日期：2026-10-26

## 合并读回

| 仓库 | PR | CI | `main` 合并提交 | 结论 |
| --- | --- | --- | --- | --- |
| Cloud | [#6](https://github.com/piqiu96/wt-media-cloud/pull/6) | `verify` PASS | `5e19898dd11c32de952263042a45ab29df9149a4` | PASS |
| Agent | [#2](https://github.com/piqiu96/wt-media-agent/pull/2) | `verify` PASS | `f46476ce9ec676216f91532c31a5562ec105bfc4` | PASS |
| Desktop | [#4](https://github.com/piqiu96/wt-media-desktop/pull/4) | `verify` PASS | `4bf633c181d214a1c1aebe7a8f724c9107df0243` | PASS |
| Workspace | [#7](https://github.com/piqiu96/wt-media-workspace/pull/7) | `Workspace checks` PASS | `61fcc120910d819a38476c130363d5a28eff923e` | PASS |

四仓分别 `git fetch origin main` 后读回本地 `main` 为上表提交，且 CHG 分支提交均为该 `main` 的祖先。合并后 Cloud 与 Desktop 仍有未提交工作树改动：Cloud 的 7 个文件按用户指示并入本 CHG 收尾补提交（见下）；Desktop 的 3 个 Cargo 文件是 `[patch.crates-io] tauri = { path = "/private/tmp/tauri-patched" }` 本机构建补丁，绝对路径不能进 `main`，已保存在仅本地的 `wip/tauri-local-patch` 分支，不推送、不影响 CI。

## 2026-10-26 收尾补提交（Cloud）

| 项目 | 内容 |
| --- | --- |
| 范围 | 5 个 Go 文件纯 gofmt（`model/model.go`、`model/task.go`、`repository/store_mysql.go`、`repository/task_mysql_test.go`、`service/material_query.go`）；2 个登录品牌视觉文件（`web/src/modules/auth/pages/LoginPage.vue`、`web/src/shared/ui/BrandLogo.vue`） |
| 分支 / PR | `chg/CHG-20261023-101-closeout` / [#7](https://github.com/piqiu96/wt-media-cloud/pull/7) |
| 本地验证 | `bash scripts/test.sh`：Go 套件通过，Web 78 文件／712 项通过，control 12 项通过 |
| CI | `verify` PASS |
| 合并提交 | `8506aa27c879f90706830f1e72bd03de97ab99b5` |
| 结论 | PASS；`change.md` 的 `wt-media-cloud` 更新为该提交，原 `5e19898` 保留在上表 |

Desktop 的 `wip/tauri-local-patch` 只用于本机 macOS 构建，不进入任何远端；除该 3 个 Cargo 文件外，Desktop 工作树在合并后干净。

## 最终验证与接受

| 验证 / 行动 | 期望 | 实际 | 结论 |
| --- | --- | --- | --- |
| `python3 scripts/wt.py chg verify CHG-20261023-101` | 风险矩阵执行 | Workspace 174 项、Cloud Go 模块测试、Agent 728 项、Desktop Rust 540 项及其 shell 套件均通过；随后在旧 M1 集成脚本的导入阶段中止 | 部分通过，例外如下 |
| 隔离的 Cloud 已提交树 `bash scripts/test.sh` | 当前代码全量验证 | Go 套件、Web 78 文件／712 项、控制脚本 12 项通过 | PASS |
| 隔离的 Desktop 已提交树 `bash scripts/test.sh` | 当前代码全量验证 | Rust 540 项通过、6 项忽略；shell 套件通过 | PASS |
| `python3 scripts/verify/verify_m2_acceptance.py` 与 Workspace 文档、交付、产品对齐、配置门禁 | 当前 M2 契约与文档一致 | 均退出 0 | PASS |
| 用户 GUI 验收 | 用户确认 CHG-101 GUI 可接受 | 用户明确回复“chg101 gui已验收，合并你进行收尾处理”；见 T-14 | PASS（用户确认） |

`wt chg verify` 的最后一步仍固定调用历史 `verify_m1_integration.py`，该脚本导入已随本 CHG 退役的 `wt_media_agent.cloud_agent_client`，直接报 `ModuleNotFoundError`。该脚本在 `scripts/README.md` 已标注“行为已知阻塞”，属于旧 M1 验证入口，不是 CHG-101 的运行时回归结果。本 CHG 的当前跨端真实读数以 T-10 的 64/64、断网补报 17/17、T-13 的 BitBrowser 离线模拟、上述 M2 静态验收及四仓 CI 为依据。旧脚本未在本 CHG 范围内重写。

未覆盖的第二台物理 Desktop、真实发布／互动任务、真实下载双机交接、常驻调度器 tick 已在交付报告登记；不阻塞用户本次 GUI 验收和 CHG-101 合并。
