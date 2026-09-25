# Product Documents

Current effective product facts live here.

Rules:

- Product requirements used for implementation must reference this directory.
- Do not store implementation plans, handoffs, progress notes, or temporary decisions here.
- Do not keep a legacy PRD copy outside this tree: the PRD lives under `prd/` below, and the execution root `wt-media/` carries no `docs/` directory of its own.

## Current M3 baseline

[M3 内容挖掘 V2](M3-content-mining-v2.md) 是当前 M3 产品事实源（ADR-0013）。旧第四章“内容发现”仅保留历史，不再作为 M3 实施依据。已确认方向与待决细节在 V2 中分别标注。

M3 范围内对旧规则的改动（2026-09-23：自动转素材、`partial_success`）先回写本基线与 ADR-0013。按 `delivery/milestones/README.md` 的 Milestone-first 规则，稳定产品规则在 M3 完整验收后再按需融合回 PRD；在此之前 PRD 第四章继续指向本基线。

## Current M4-M5 baseline

[第五章：素材生产](prd/详细文档/第五章_素材生产.md) 是 M4 内容生产与 M5 自动生产的产品事实源。2026-09-24 起视频合成统一由 Cloud Scheduler / Worker / FFmpeg 执行；`material_usage`、`compose_strategy`、`compose_task`、`composite_output` 语义冻结，文件传输统一使用 `file_transfer_task`。工程边界见 ADR-0017。
