# Milestone-first 回写规范 Evidence

> 时间：2026-07-23  
> 范围：CHG-20260723-025 验收过程中沉淀的治理规则

## 1. 背景

人工验收中确认：执行过程中的小变更、页面口径、按钮语义和异常处理如果每次都立即回写 PRD，会导致 PRD 频繁打补丁，增加维护成本，也容易把执行细节写成长期产品事实。

最终规则调整为：

```text
小变更 / 验收细节 / 页面口径
→ 优先回写当前 Milestone
→ 同步当前 CHG checkpoint / evidence
→ 不立即回写 PRD

Milestone 完整验收后
→ 再按需把稳定产品规则整理回 PRD
```

## 2. 已沉淀位置

- `delivery/milestones/README.md`
  - 新增 `Milestone-first 更新规则`；
  - 明确 Milestone 是当前阶段业务闭环基线；
  - 明确 PRD 是长期产品事实，不承载执行中的频繁修订。

- `skills/workspace/planning-wt-media-delivery/SKILL.md`
  - 新增 `Product / Milestone Write-back Rule`；
  - 修改变更分类表；
  - 强制后续 planning 类工作先判断写入 Milestone、PRD、Engineering、Decision 还是 CHG。

- `.codex/skills/planning-wt-media-delivery/SKILL.md`
  - 通过同步脚本生成，保证后续 Codex 调用使用最新规则。

## 3. 验证

```text
python3 scripts/sync_skills.py sync --repo root --tool codex
```

结果：PASS，输出 `synced root/codex`。

```text
python3 scripts/sync_skills.py check --repo root --tool codex
```

结果：PASS，输出 `skill outputs are up to date`。

## 4. 后续执行要求

后续 M2-B / M2-C / M2-D / M2-E 执行中：

- 验收细节先进入 `delivery/milestones/M2-account-runtime.md`；
- 当前实现事实进入对应 CHG 的 `change.md` 和 `evidence/`；
- PRD 等 M2 完整收口或稳定产品规则需要沉淀时再统一更新；
- 如果是 Cloud / Desktop / Agent 职责边界变化，则不能只写 Milestone，必须同步 Engineering 或 Decision。
