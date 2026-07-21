# M2 交付治理纠偏设计

> 日期：2026-07-22
> 范围：只调整 M2 的规划、CHG 边界、上下文和 Skill 约束；不修改业务代码

## 1. 目标

恢复 M2 的可控交付节奏，避免继续用一个巨型 CHG 同时实现和验收 M2-A～M2-E。

本次不重写 PRD、ARCH、MASTER PLAN 或既有 M2 Completion Design，也不新增重复的设计体系。现有 AI Spec 继续作为分析和实施参考；人工确认后的 M 级业务闭环统一收敛到 `delivery/milestones/`。

## 2. 最小结构

```text
docs/product/                         产品事实
docs/engineering/                     工程事实
docs/contracts/                       契约事实
docs/decisions/                       决策事实
docs/superpowers/specs/               AI 分析与设计材料

delivery/MASTER_IMPLEMENTATION_PLAN.md 项目总路线
delivery/milestones/M2-account-runtime.md
                                      M2 唯一业务闭环基线
delivery/active/<CHG>/change.md        当前小范围执行合同
delivery/active/<CHG>/evidence/        本次验证事实
delivery/LEDGER.md                     唯一 Active CHG 索引
```

`delivery/milestones/M2-account-runtime.md` 不复制 PRD 或技术设计，只将已确认的 M2-A～E 收敛成五张闭环卡。每张卡只记录：

- 用户目标；
- 前置条件；
- 用户操作顺序；
- 系统、Cloud、Agent、Desktop 和外部依赖动作；
- 成功必须同时满足的真实结果；
- 失败时不得产生的假成功；
- 对应 CHG。

## 3. 文档权责

| 内容 | 唯一职责 | 何时修改 |
|---|---|---|
| `docs/product` | 产品目标与规则 | 产品规则变化时 |
| `docs/engineering` | 系统职责、边界和原则 | 工程原则变化时 |
| `docs/superpowers/specs` | AI 推演、设计和实施参考 | 需要分析或形成方案时 |
| `MASTER_IMPLEMENTATION_PLAN.md` | M0～M10 路线、依赖和总退出条件 | 项目路线变化时 |
| `delivery/milestones/M*.md` | 人工确认的 M 级业务闭环 | 业务闭环或验收结果变化时 |
| `change.md` | 本次实现哪一段闭环 | 当前实现范围变化时 |
| `evidence/` | 实际执行和验证事实 | 验证发生后 |

同一业务流程不在 PRD、Milestone 和 CHG 中重复维护。CHG 通过文件路径和章节锚点引用闭环卡，仅补充当前差距、工程范围、任务和本次验收方法。

## 4. M2 纠偏方案

### 4.1 基线收敛

以以下内容为输入：

- `delivery/MASTER_IMPLEMENTATION_PLAN.md`；
- `docs/superpowers/specs/2026-07-21-m2-completion-design.md`；
- `delivery/active/M2-PLAN-20260716/plan.md` 中仍有效的业务内容；
- 当前代码、测试和 Evidence 事实。

生成一份中文、可人工维护的 `delivery/milestones/M2-account-runtime.md`，包含 M2-A～E 五张闭环卡。原文件保留其历史或 AI 分析职责，不做破坏性迁移。

### 4.2 CHG-020 收口

`CHG-20260721-020` 不再继续扩大。先审计其已经真实完成并有 Evidence 支撑的内容，然后选择可追溯的收口方式：

- 已达到独立验收条件的部分，作为阶段性基础工作完成；
- 未达到闭环验收的内容，不因代码存在而声明完成；
- 剩余工作按 M2-A～E 闭环边界进入后续独立 CHG；
- 不删除已有代码、Evidence 或历史记录。

### 4.3 顺序执行

```text
M2-A 权限与可信验收基础
→ M2-B 媒体账号与 Profile
→ M2-C 代理与 Profile
→ M2-D Cookie 与开户
→ M2-E Desktop、安全与综合验收
```

任何时刻只允许一个 M/L CHG 出现在 `delivery/active` 和 `delivery/LEDGER.md`。一个 CHG 对应一张闭环卡；若一张卡仍过大，可拆成多个顺序 CHG，但每个 CHG 必须交付可独立验证的纵向结果。

## 5. 完成判断

每个 M2 CHG 的完成必须同时证明：

1. 用户能够从页面发起目标操作；
2. Cloud/MySQL 形成正确的正式事实；
3. Agent/BitBrowser 或其他真实依赖产生预期外部副作用；
4. 外部状态被读回并验证，不以“任务已创建”代替成功；
5. 业务结果回写，用户在原业务页面看到最终状态；
6. 失败、部分成功和结果不确定不会形成假成功；
7. 自动测试、真实环境验证和脱敏 Evidence 满足闭环卡要求。

只有代码、接口、页面或任务类型存在，均不能单独作为闭环完成证据。

## 6. Skill 收敛

只保留两个用户入口，避免 Skill 选择成本和职责重叠。

### 6.1 `planning-wt-media-delivery`

负责规划和纠偏，不负责业务代码实现：

- 根据 PRD、ARCH、MASTER PLAN、AI Spec 和当前实现拆分或修正 M；
- 生成或维护 `delivery/milestones/M*.md`；
- 根据闭环卡创建、拆分或调整 CHG；
- 对字段修改、Bug、业务变化、架构变化做影响判断；
- 发现 M 做偏时，从代码和 Evidence 逆向核对，但由 Milestone 记录最终业务结论；
- 在写文件前先输出影响范围和拟修改清单，涉及业务取舍时等待人工补充。

### 6.2 `executing-wt-media-change`

保留现有执行协议并轻量增加 Start Gate：

- CHG 必须引用 MASTER PLAN 或对应 Milestone 闭环卡；
- 必须指出本次交付的是哪段纵向结果；
- 必须从闭环卡继承真实验收条件；
- 禁止用局部代码完成替代业务闭环完成；
- 发现业务闭环或架构冲突时停止执行，回到规划入口，不在代码中打补丁推断需求。

不新增单独的 Impact、Spec、Milestone、CHG Planning Skill。它们属于同一个规划与纠偏过程。

## 7. 人工参与点

人工不需要从零写文档，只在规划 Skill 给出结构化内容后补充或修正四类信息：

1. 用户最终要完成什么；
2. 必要前置条件和真实操作顺序；
3. 哪些数据与外部副作用必须发生；
4. 什么是假成功、什么情况下不能验收。

这些确认写入 Milestone 后，Codex 负责生成 CHG、实现、测试和 Evidence。开发中若只是实现错误，留在 CHG 修复；若业务闭环错误，更新 Milestone；若工程原则错误，更新 ARCH/Decision 后再调整 Milestone 和 CHG。

## 8. 当前上下文修复

根目录 `.ai/CURRENT_CONTEXT.md` 当前仍指向已完成的 `CHG-20260715-010`，与 `delivery/LEDGER.md` 和实际 Active CHG 不一致。本次治理实施必须同步修复，并建立校验：

- Current Context、Ledger 和实际 `delivery/active` 指向同一个 CHG；
- 不允许上下文引用不存在或已完成的 Active CHG；
- 执行 Skill 启动时必须报告三者一致性。

## 9. 实施边界

本次治理纠偏只允许修改 Workspace 治理文件和 Workspace Skill：

- 新增 M2 Milestone 闭环卡；
- 收口或拆分 CHG 记录；
- 修复 Current Context 与 Ledger；
- 新增规划 Skill；
- 轻量升级执行 Skill；
- 添加必要的治理校验与说明。

不修改 Cloud、Agent、Desktop 业务代码，不删除用户现有未提交文件，不把 M2 标记为 `DONE`，不自动开始下一个业务 CHG。

## 10. 成功标准

治理纠偏完成后应满足：

- M2 只有一个人工可读、可维护的业务闭环基线；
- AI Spec 被保留但不会绕过 Milestone 直接驱动完成判断；
- CHG-020 不再作为 M2-A～E 的无限扩张容器；
- Ledger、Current Context 和 Active 目录一致；
- 规划与执行只有两个明确 Skill 入口；
- 下一个 M2 CHG 范围清楚、验收真实，且能立即进入执行。
