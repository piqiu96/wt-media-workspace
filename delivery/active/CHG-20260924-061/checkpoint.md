# Checkpoint: CHG-20260924-061

- CHG: `CHG-20260924-061`（M4-A 素材库、我的素材与原素材懒加载下载）
- Level: M
- Updated: 2026-09-26

## 状态

`IMPLEMENTING`（2026-09-26 激活）

## Completed

- **T-00 激活与基线盘点**：确认 M3 为 `DONE`、`delivery/active` 为空、M4/M5 的 Product、Engineering、ADR-0017 与 CHG-061 一致；061 从 `planned/` 移至 `active/`，M4 更新为 `IN_PROGRESS`，M5 保持 `NOT_STARTED`。未修改任何运行时代码。基线记录见 `evidence/20260926-activation-baseline.md`。

## Current

Task 0 进行中：冻结由 Cloud 提供的正式传输合同，并盘点真实来源读取、对象存储测试环境、Local Agent 节点身份与本地下载授权。

## Next

1. **Task 0**：在 Cloud 合同中定义 `material`、`material_usage` 与 `file_transfer_task` 的 DTO、枚举、错误码和兼容规则；验证 Cloud 准备与 Local Agent 下载是否能复用已准备对象，禁止无界重复任务。
2. **Task 1**：先编写迁移与 Repository 的失败测试，再以实际可用迁移号实现数据对象、约束与原子 SQL。

## Blocked

- None. 真实来源、对象存储和下载授权是后续产生外部副作用前必须实测的前提，不阻止合同冻结。

## Recent verification

| 判据 | 读数 |
|---|---|
| `python3 scripts/verify_delivery_governance.py`（激活后） | `exit=0`；active CHG 为 `CHG-20260924-061` |
| `python3 scripts/verify_product_master_alignment.py`（激活后） | `exit=0` |
| `python3 -m unittest tests.test_prepare_ai_workspace tests.test_verify_delivery_governance tests.test_verify_product_master_alignment -q` | `Ran 28 tests / OK` |
