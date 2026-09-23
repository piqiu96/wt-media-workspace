# Delivery Ledger

This file lists active delivery records. It is not a historical archive.

Completed delivery records are removed after their final product, engineering, contract, and decision outcomes have been reflected in the stable baseline and committed to Git.

| Change | Title | Status | Current Repository |
|---|---|---|---|

No active M/L CHG（2026-09-24：CHG-20260923-056 关闭归档后，active 名额为空；联合工程优化程序的后续阶段 CHG-057/058/059 已在 [planned/](planned/README.md) 登记，待用户裁定后激活）。

[CHG-20260923-056](completed/CHG-20260923-056/change.md)（联合工程优化 A——结构审计、Config 与 Client 解耦）已于 2026-09-24 关闭归档为 `DONE`：按 ADR-0016 与架构基线完成 Agent 的目录迁移与 `runtime/` 配置收口、`bootstrap/` 真实装配链、两端 Client 的构造注入，Desktop 从 1570 行单文件拆为分层模块并以配置驱动启动 sidecar，Cloud Web 的地址链路改由 `get_public_config` 提供。§13 DONE Gate 九项逐项签字；AC-01…AC-11 全 PASS（agent 253 tests / desktop 63 passed / cloud web 21 files-101 tests）。**四项待用户裁定随记录一并归档**（生产 CSP 是否加 `ipc:`、回环 client 是否加 `.no_proxy()`、`modes/`+`generated/` 占位包与基线 §5.2 的冲突、以及 T-09 期间在开发者 Cloud 上被误建的一个惰性 `noop_task` 如何处置），详见该记录 §12。归档**未**阻塞于这四项：它们全部是计划明示的范围外事项或新增发现，不属本 CHG 的未完成范围。

M2 已由用户验收通过。M3-A 的闭环记录已随其并入门槛转出活动目录，归档在 [completed/CHG-20260915-044](completed/CHG-20260915-044/change.md)（`Status: HANDOFF`，未改写为 DONE）；M3-B～E 已在 [CHG-20260916-052](completed/CHG-20260916-052/change.md) 收敛并实施，该记录已于 2026-09-23 以 `Status: HANDOFF` 归档（照 CHG-044 先例，未写 DONE）。

M3 当前阶段状态（2026-09-23 同步）：**M3 已由用户签收，状态为 `DONE`**。A～E1 有真实证据；C2、E2（博主搜索与作者策略）已暂停，本期不做、移出验收范围；E3 综合验收已在 CHG-052 内执行并经同日补验收口——验收矩阵第 1～7 项全部通过，无 FAIL、无 NOT VERIFIED，**用户于 2026-09-23 就此签收**。独立验收草案 CHG-20260915-051 保持 DISCUSSION、不激活：E3 的验收与签收由 CHG-052 承载，不据此判定 CHG-051 已完成。逐阶段状态与证据指向见 [M3-content-discovery-v2.md](milestones/M3-content-discovery-v2.md) 第 2.1 节。

[CHG-20260923-055](completed/CHG-20260923-055/change.md)（Desktop 原生应用呈现修复）已于 2026-09-23 关闭归档为 `DONE`：处置 E3 验收之后、用户在生产形态 DMG 原生应用上报出的呈现问题（CSP 未放行图片、标题省略号漏了 `<a>` 渲染分支、图标 sprite 被 CSP 拦掉、minWidth-only 列在 WebKit 下被压没），以及三页时间列与计数块的呈现调整。它不在 M3 里程碑范围内，不改 M3 的验收结论；其缺陷**不**在 [CHG-20260923-054](planned/CHG-20260923-054/change.md) 内跟踪，避免重复登记。

> 归档状态词的差异（登记以免被读成疏漏）：044 与 052 写 `HANDOFF`，055 写 `DONE`。前者是**「工作并入后续门槛、其门槛本身尚未验收」**——045～050 并入 052，而 052 承载的 E3 当时待签收，故不写 DONE；055 **没有后续门槛**，它自身被用户当轮复核确认即告完成，按完成闸门写 `DONE` 才是准确状态。E3 签收已于 2026-09-23 完成，**是否因此把 044/052 也由 `HANDOFF` 改判 `DONE`，属治理口径决定，本次不动**，留待统一处理。

验收期间只登记未修的缺陷与安全问题已按用户裁定移入 planned（[CHG-20260923-054](planned/CHG-20260923-054/change.md)）。

待规划/待决记录见 [Planned index](planned/README.md)，不计为正在执行的变更。
