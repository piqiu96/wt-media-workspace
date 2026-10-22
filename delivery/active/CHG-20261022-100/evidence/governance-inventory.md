# 存量治理机器清单

> 本文件是 CHG-20261022-100 的执行清单，不是长期事实源。路径与判定只对应当次处置；现行事实以各 Owner 为准。
> 判定词只有 KEEP / MERGE / MOVE / DELETE / SUPERSEDED / REVIEW。

## 1. 计数

| 判定 | 数量 | 对象 |
| --- | --- | --- |
| KEEP | 3 | `delivery/reports/README.md`、`2026-09-14-m2-final-acceptance.md`、`2026-10-12-m4-a-signoff.md` |
| MERGE | 18 | 见 §3；事实并入既有 SSOT 或就地压缩为当前描述 |
| MOVE | 0 | 无需要以文件形式长期保留的参考材料 |
| DELETE | 42 | 31 篇 `docs/superpowers/` ＋ 9 篇 `delivery/reports/` ＋ 第四章 ＋ launch-engineering 程序规格 |
| SUPERSEDED | 1 | 第四章_内容发现（唯一临时标记文；引用迁移后删除，现存 0） |
| REVIEW | 0 | 原计划的五个条件项均完成覆盖确认，未留下不确定项 |

`delivery/completed/` 整体 KEEP：72 篇记录、1,089 个文件不迁移、不重写、不参与当前裁定。上述计数不按目录整体展开。

## 2. DELETE（42）

最后所在提交＝删除前最后一次改动该文件的提交。`git show <sha>:<path>` 可读回原文。

### 2.1 `docs/superpowers/`（31）

| 文件 | 最后所在提交 | Owner（当前事实位置） |
| --- | --- | --- |
| `README.md` | 735dafe | 无；集合已清空 |
| `plans/2026-07-16-m2-gap-plan.md` | a0327fe | `delivery/milestones/M2-account-runtime.md`、ADR-0001/0002/0003/0004 |
| `plans/2026-07-21-m2-a-implementation-plan.md` | e77b40d | 同上 |
| `plans/2026-07-21-m2-b-e-execution-plan.md` | 456ac9f | 同上 |
| `plans/2026-07-21-m2-completion-program.md` | 97288c0 | 同上 |
| `plans/2026-07-21-sync-fast-path-plan.md` | 7b1da15 | 同上 |
| `plans/2026-07-22-m2-a1-user-domain-migration.md` | ff64fb5 | 同上 |
| `plans/2026-07-22-m2-delivery-governance-correction.md` | cfb696a | 同上 |
| `plans/2026-07-22-m2-milestone-refinement.md` | 97288c0 | 同上 |
| `plans/2026-07-23-m2-account-runtime-detailed-implementation-plan.md` | 97288c0 | 同上 |
| `plans/2026-09-03-m2-b-multi-game-implementation.md` | cd0f674 | 同上 |
| `plans/2026-09-04-m2-b-game-scope-and-reference-management.md` | 6a0b181 | 同上 |
| `plans/2026-09-12-m2-c-proxy-closure.md` | 4a3d9ec | 同上 |
| `plans/2026-09-13-m2-e-sidecar-private-distribution.md` | 6683c0d | 同上 |
| `plans/2026-09-14-operation-resources-design-system-implementation.md` | ec2e399 | 同上；视觉 token 以 `docs/standards/frontend/前端架构与视觉规范.md` 为准 |
| `plans/2026-09-24-m4-m5-cloud-content-production-docs.md` | 31c18a0 | `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md`、ADR-0017/0021、PRD 第五章 |
| `plans/2026-10-08-windows-desktop-console-logging-plan.md` | 4bcaa92 | architecture §6.8 Desktop、Desktop `system_paths.rs`、`M-first-production-release.md` §Windows |
| `plans/2026-10-10-public-home-and-desktop-downloads.md` | 879f7cb | `docs/product/公开官网与桌面下载.md`、`M-first-production-release.md` |
| `specs/2026-07-21-m2-completion-design.md` | e264fc5 | M2 Milestone、ADR-0001/0002/0003/0004 |
| `specs/2026-07-21-sync-fast-path-design.md` | 7b1da15 | 同上 |
| `specs/2026-07-22-m2-delivery-governance-correction-design.md` | 63d4212 | 同上 |
| `specs/2026-09-03-m2-b-multi-game-design.md` | 74200b2 | 同上 |
| `specs/2026-09-04-m2-b-game-scope-and-reference-management-design.md` | 52b204f | 同上 |
| `specs/2026-09-14-operation-resources-design-system-design.md` | ec2e399 | 同上 |
| `specs/2026-09-16-m3-cloud-owned-discovery-design.md` | f86623c | `docs/product/M3-content-mining-v2.md`、ADR-0013/0014/0015 |
| `specs/2026-09-24-m4-m5-cloud-content-production-design.md` | 31c18a0 | M4/M5 spec、ADR-0017/0021、PRD 第五章 |
| `specs/2026-10-02-first-production-deployment-plan.md` | 36e66cf | `docs/devops/服务部署.md`、ADR-0020 |
| `specs/2026-10-03-github-packaging-trial-plan.md` | 7ca1cd5 | 同上 |
| `specs/2026-10-04-baota-cloud-deployment-layout-design.md` | 36e66cf | 同上；只采用现行 `/home/www/wt-media-cloud` |
| `specs/2026-10-08-windows-desktop-console-logging-design.md` | 4bcaa92 | architecture §6.8 Desktop、Desktop 日志实现、M-first §Windows |
| `specs/2026-10-10-public-home-and-desktop-downloads-design.md` | caaf367 | `docs/product/公开官网与桌面下载.md`、M-first |

### 2.2 `delivery/reports/`（9）

| 文件 | 最后所在提交 | Owner |
| --- | --- | --- |
| `2026-07-21-current-system-assessment.md` | 97288c0 | MASTER、M2 Milestone |
| `2026-07-21-m2-module-business-flow-current-state.md` | e81ba86 | M2 Milestone、ADR-0001/0002/0003/0004 |
| `2026-07-22-m2-a-e-code-gap-audit.md` | 25033c9 | 同上 |
| `2026-07-22-m2-milestone-refinement-comparison.md` | 97288c0 | 同上 |
| `2026-09-03-master-plan-progress-audit.md` | 56f899c | `delivery/MASTER_IMPLEMENTATION_PLAN.md` |
| `2026-09-14-m3-requirements-analysis.md` | 3a3a6bb | `docs/product/M3-content-mining-v2.md`、M3 Milestone |
| `2026-09-29-ledger-historical-notes.md` | c0b8bea | `delivery/LEDGER.md`（已移除历史叙述行）；叙述由 Git 承担 |
| `2026-10-12-m4-c2-readiness.md` | 2e764d3 | M4 Milestone、MASTER |
| `M2-prd-chapter3-gap-matrix.md` | 1e41cd9 | M2 Milestone、PRD 第三章 |

### 2.3 其他（2）

| 文件 | 最后所在提交 | 判定与 Owner |
| --- | --- | --- |
| `docs/product/prd/详细文档/第四章_内容发现.md` | 735dafe | SUPERSEDED → DELETE。全部当前引用改指 M3 V2、ADR-0013/0014/0015；PRD 第四章正文改为指针 |
| `docs/engineering/specs/2026-09-23-launch-engineering-optimization-program.md` | 77d79e6 | DELETE。TOML 配置约定先补入 architecture §3/§5，其余四个阶段已归档 DONE |

## 3. MERGE（18）

| 文件 | 合并/压缩内容 |
| --- | --- |
| `delivery/MASTER_IMPLEMENTATION_PLAN.md` | 删除五条就地勘误与词汇历史；状态表按门禁读取器实测重写（active 2／planned 4／archived 72） |
| `delivery/milestones/M2-account-runtime.md` | 日期化轮次叙述改为当前能力与签收事实 |
| `delivery/milestones/M3-content-discovery-v2.md` | 草案 CHG 引用归一为 CHG-052；状态表改为当前状态 |
| `delivery/milestones/M4-content-production.md` | 删除与 change/evidence 重复的 C2～C8 叙述与对账日期前缀；保留全部 AC 与 H2 规则 |
| `delivery/milestones/M5-automatic-production.md` | 压缩 C1/C2 验证叙述；保留全部 AC 与 Done Gate |
| `delivery/milestones/M-first-production-release.md` | “当前实施单元”改为“实施记录” |
| `delivery/milestones/M-launch-engineering.md` | 删除规格指针与 CHG 映射；保留四条归档链接、三个例外与 Q-05 |
| `docs/decisions/0013-m3-content-mining-entry.md` | 删除会话来源措辞与已不成立的 SUPERSEDED 保留说明 |
| `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md` | 删除行内 provenance；TOML 配置约定与日志读数口径成为正文 |
| `docs/engineering/specs/README.md` | 移除已结束程序条目 |
| `docs/product/M3-content-mining-v2.md` | “本轮实测/本轮验收”改为状态事实或缺陷指针；保留确认要求与待决项 |
| `docs/product/README.md` | 删除“旧第四章仅保留历史”的并行事实 |
| `docs/product/prd/社媒运营平台_产品需求说明书_V1.md` | 第四章正文改为 M3 V2 指针；两处链接改指当前基线 |
| `docs/product/prd/详细文档/第五章_素材生产.md` | 2026-10-18 页面裁定并入 §5.9 正文；删除“旧描述暂作历史” |
| `docs/product/prd/详细文档/第七章_互动管理.md` | 跨章引用改指内容挖掘 |
| `docs/reference/state-models/README.md` | 移除已删除章节链接 |
| `skills/workspace/executing-wt-media-change/SKILL.md` | 删除 legacy root docs 表述；Plan 五段式改为引用规范 §5 |
| `skills/workspace/planning-wt-media-delivery/SKILL.md` | Authority 第 5 项移除 `docs/superpowers/specs` |

## 4. KEEP（3）

| 文件 | 理由 |
| --- | --- |
| `delivery/reports/README.md` | 目录索引；保持 `historical/never` |
| `delivery/reports/2026-09-14-m2-final-acceptance.md` | MASTER 引用的 M2 最终验收证据 |
| `delivery/reports/2026-10-12-m4-a-signoff.md` | MASTER、M4 Milestone、planned 记录引用的签收证据 |

## 5. 代码注释（按仓独立提交）

| 仓库 | 文件 | 删除/改写内容 |
| --- | --- | --- |
| Cloud `ff1bf90` | `internal/modules/cloudagent/repository/mysql_registry.go`、`web/src/modules/transfer/downloadErrors.js`、`web/src/apps/desktop/features/local-agent/work-env-status.js`、`web/src/modules/materials/pages/MyMaterialsPage.test.js` | 测试轮次/CHG 编号/“曾经是缺陷”叙述；保留会话与注册表分离的安全理由 |
| Agent `5c61f95` | `tests/test_dependency_boundaries.py`、`src/wt_media_agent/clients/cloud/client.py` | T-04/T-05/T-09/CHG-057/CHG-061 修改史；保留边界规则与规则为何收窄 |
| Desktop `81d8ea0` | `src-tauri/src/logging/rolling.rs`、`src-tauri/src/logging/test_support.rs`、`scripts/build-release-macos.sh` | 手写轮转器、改名事故、变异实验故事；保留当前轮转/截断/打包规则 |
| Workspace `668e47a` | `scripts/verify/verify_m2_acceptance.py`、`verify_m3_acceptance.py`、`verify_product_master_alignment.py`、`verify_delivery_governance.py` | CHG 删除断言记录、T-04/T-08/T-09 现场笔记、旧路径故事；保留断言范围与判据理由 |

violation/diagnostic 字符串中的 CHG 编号未改：它们是测试输出，不是注释，部分被断言匹配。

## 6. 引用闭合

- `docs/superpowers/`、已删除报告的路径在当前文档中 0 命中；阳性对照在 `delivery/completed/` 命中（归档只读，不回改）。
- `SUPERSEDED` 文档标记 0；`docs/` 中仅剩规范词汇与检查器说明。
- `delivery/completed/` 链接均为追溯引用；核心规则已写入正式 SSOT。
- 校验读数见 `verification.md`。
