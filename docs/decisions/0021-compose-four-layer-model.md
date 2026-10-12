# ADR-0021：合成四层模型——模板为带版本技术资产，策略为无版本业务配置

- Status: Accepted
- Date: 2026-10-12
- Scope: M4-M5 内容生产（`compose_template`、`compose_strategy`、`compose_task`、`composite_output`）
- Supersedes:
  - 工程规范 `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md` §3.3 中「策略版本和变更审计」——策略不再保存不可变版本记录；
  - 里程碑 `delivery/milestones/M4-content-production.md` M4-C2 的「查看版本记录」验收文本（已同步回写）；
  - CHG-20261012-079 中已实现的 `compose_strategy_versions`、`expected_version` 与版本历史页面（尚未签收，随本 CHG 重做移除）。
- Does not supersede: ADR-0017 的 Cloud 内部执行、固定业务对象与 MySQL 原子领取原则；`compose_task` 不可变策略快照（M4-C3 范围）。

## Context

M4-B 首版实现把「版本」建在策略层：策略每次修改追加不可变版本记录，修改用 `expected_version` 防覆盖。用户在 2026-10-12 提出模型修正并逐项裁定：

1. 合成域采用四层模型 `compose_template → compose_strategy → compose_task → composite_output`；
2. **模板是技术资产**：固定执行动作、定义参数 schema、绑定执行代码、管理版本；版本整数自增、`UNIQUE(code, version)`，升级只新增不覆盖；schema 属于模板，与代码一起发布；
3. **策略是业务配置**：引用一个固定版本的模板并填写 schema 允许的参数。修改策略是配置变化，**不需要策略版本记录**；历史追溯由 `compose_task` 的不可变快照（M4-C3）承担；
4. 策略的 `schedule` 字段**推迟到定时生产落地时**（M5）再引入，现在不留空转列；
5. 片头/片尾/BGM 等资产参数键**随模板新版本放开**：首个模板版本的 schema 只定义当前可执行参数；资产接入后在模板新版本中扩展，正好使用模板自身的版本机制；
6. 禁止动态工作流编排、用户自定义脚本、任意 FFmpeg 命令与泛化 `template` 表（保持 `compose_template` 领域命名）。

## Decision

1. `compose_template` 为 Cloud 维护的入库实体：`code`、`name`、`version`（整数自增）、`schema_json`、`executor`、`status`，唯一约束 `(code, version)`；旧版本永久保留，策略按 `(模板, 版本)` 绑定。
2. `compose_strategy` 不含版本机制：保存模板引用（模板 id + 模板版本）、业务参数 `config`（由所绑定模板的 `schema_json` 校验）、业务范围与启停状态；修改直接覆盖当前配置。策略变更审计走审计日志，不建版本快照表。
3. 修改策略不得影响历史任务：该保证由 `compose_task` 创建时保存的不可变快照承担（`template_code`、`template_version`、`config_snapshot`，M4-C3 实施），执行只读快照。
4. 模板升级不迁移旧策略：旧策略继续绑定旧版本模板；新策略可选新版本。
5. `executor` 在 Cloud 合成执行器（M4-C4/C5）落地前允许为占位值，但字段与唯一约束随首版表结构一次到位。

## Consequences

- 已交付未签收的策略版本机制（版本表、`expected_version`、409 冲突、版本历史页面）拆除；操作并发保护退化为「读-改-写」的常规表单行为，可接受的竞争由任务快照兜底。
- 模板目录从代码内目录改为数据库实体；模板的增版是数据操作，不再需要改代码发版。
- 普通运营可见的参数边界 = 所绑定模板版本的 `schema_json`；无资产合同的参数键在 schema 层就不存在，而不是「存在但被拒绝」。
