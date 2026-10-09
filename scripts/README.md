# WT Media Workspace Scripts

本目录是 `wt-media-workspace` 的脚本索引。本文件只做**分类**与**落位规则**，
不做逐文件说明，也不记录任何运行参数。

## 分类

| 用途 | 判据（这一类回答什么问题） | 脚本（仅文件名） |
| --- | --- | --- |
| 运营 | 把本地环境跑起来 / 确认在跑 / 停下 | 见 [`../bin/control.sh`](../bin/control.sh) |
| 开发 | 改完东西之后重建 / 重生成 / 迁移 / 分发 | `sync_skills.py`、`prepare_ai_workspace.py`、`build-desktop-frontend.sh` |
| 验收 | 证明某件事成立 / 不成立 | `verify_delivery_governance.py`、`verify_ai_workspace.py`、`verify_skills.py`、`verify_m0_config.py`、`verify_product_master_alignment.py`、`verify_m1_integration.py`、`verify_m2_acceptance.py`、`verify_m3_acceptance.py`、`verify_m0_local.sh`、`verify-control.sh` |
| 发布 | 固定产品版本并提交 Tag | `release/submit_tag.py`；使用方式见 `release/README.md` |
| 运行台 | 上面几类共用的执行体，本身不是入口 | `m2b-local-acceptance.sh`、`m2b_local_acceptance.py`（含 `start` 与 `verify` 两类动词，故同时属运营与验收）、`workspace_config.py` |

多归属是特性，不是错误：`verify-control.sh` 是 `bin/control.sh` 的验收件；
`m2b_local_acceptance.py` 既供运营（`status`）也供验收（`verify`）。

## 新脚本落在哪

- 新产生的**开发**脚本 → `scripts/dev/`。
- 新产生的**验证 / 验收**脚本 → `scripts/verify/`。
- **启停与健康检查一律进 [`bin/`](../bin/)**，不得新增在 `scripts/` 下。
- **现存脚本不迁移**：本目录下的扁平文件是历史落点，按「不动」处理。`dev/` 与 `verify/`
  只承接此后新写的脚本，不是「把现有文件搬一遍」的目标形态。

两个子目录目前各只有一枚 `.gitkeep`。

## 本文件不拥有什么

逐文件事实不在这里。常用校验命令见 [`README.md`](../README.md) 的“Verification”；跨仓环境手册归
`skills/common/environment-bring-up/SKILL.md`。

**数值型运行参数——端口、地址、凭据、超时与保留期默认值——的唯一落点是配置文件**，
本文件与 [`../bin/control.sh`](../bin/control.sh) 都不得复述；`bin/control.sh` 只分派动词，
端口由它调用的运行台读取。这条约束由 `verify-control.sh` 机检。
