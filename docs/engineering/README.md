<!-- governance: class=stable default_load=task -->

# Engineering Documents

Current effective engineering facts live here.

Rules:

- Engineering design used for implementation must reference this directory.
- Long-lived engineering specs may live under `specs`.
- Temporary execution state belongs in `.ai/WORK_STATE.md` (optional, gitignored). A CHG's formal record is `../delivery/active/<change-id>/change.md`, with `evidence/` only when needed; do not place plans or progress in this directory.
- Do not change engineering conclusions as part of delivery bookkeeping.

## 技术设计写作要求

- **结论先行。** 先说明采用什么设计，再按「整体架构 → 服务交互 → 核心模型 → 必要接口细节 → 技术验证」展开，让读者先理解系统如何协作，再查看局部实现。
- **同一主题集中维护。** 优先合并相关设计；只有职责或维护边界明确不同才拆分文档，避免理解一项能力需要反复跳转。
- **详略随复杂度决定。** 简单设计直接说明，复杂交互、状态和并发关系用图表表达；不机械套用全部章节，也不在图表后重复完整流程。
- **引用已有定义。** PRD 中的业务规则、Contract 中的协议和 ADR 中的决策只引用，Spec 说明如何实现及必要约束，不复制维护另一套定义。
- **原位整合有效结论。** 已确认的新设计融入所属章节，删除被替代的旧方案和重复解释，不持续追加补丁或保留讨论过程。
- **设计与执行记录分开。** 技术验证说明要证明什么、如何验证及通过条件；开发计划、任务排期、实施过程和测试流水账放在 Delivery 或相应执行记录中，不写入 Engineering Spec。
