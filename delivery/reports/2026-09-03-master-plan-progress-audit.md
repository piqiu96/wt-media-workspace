# 2026-09-03 MASTER 实施计划完成度审计

## 1. 结论

按 `MASTER_IMPLEMENTATION_PLAN.md` 的正式里程碑状态计算：

- `DONE`：M0、M1，共 2/11（18.2%）
- `IN_PROGRESS`：M2，共 1/11（9.1%）
- `NOT_STARTED`：M3-M10，共 8/11（72.7%）

该比例只表示正式里程碑状态，不把继承代码量折算成虚假的线性完成率。旧的 M2“47%”已被主计划明确废弃，不能继续引用。

## 2. 决策优先的 M2 事实

1. Decision 0008：本机 BitBrowser 短操作走 Desktop → Tauri/Rust → Local Agent 同步执行并读回，不能以 Cloud 异步任务创建代替成功。
2. Decision 0009：角色、团队、用户数字 ID 与游戏授权范围采用当前固定模型。
3. Decision 0010：媒体账号业务状态只有 `enabled`/`disabled`；账号页唯一批量入口是批量检查。
4. Milestone M2 是当前业务闭环基线；最终 PRD 只在不与 Decision/Milestone 冲突时提供细节。

## 3. M2 子闭环完成度

| 子闭环 | 当前判定 | 已完成 | 尚未关闭 |
|---|---|---|---|
| M2-A | CLOSED | 用户、角色、团队、游戏范围、会话和本机身份可信链路 | 无当前阻塞 |
| M2-B | IN_PROGRESS | Profile 扫描/Diff/确认、窗口生命周期、账号 CRUD/绑定/检查控制流、账号组、Cookie 读取、P0 平台身份、8 项明细骨架、页面 GUI | 账号—游戏基数冲突；检查项 7/8 缺真实受限样本；检查项 3/4 依赖 M2-C；最终收口矩阵 |
| M2-C | PLANNED | 继承代理 CRUD、文本解析、TCP 检测、旧异步分配任务、Agent mutation executor、基础页面 | 六个正式任务均未形成当前闭环，详见 CHG-20260805-033 |
| M2-D | NOT CLOSED | 只有 M2-B 范围内的 Cookie 查看/导出/从 Profile 读取 | Cookie 写入、开户、接码、人工接管和批量恢复闭环 |
| M2-E | NOT CLOSED | 主计划记录 7/10，且 Profile 互斥已在 M2-B 验证 | E2/E6 及最终安全/恢复验收 |

## 4. M2-B 剩余工作

1. 形成 durable decision，解决 Milestone“账号可绑定多个游戏”和最终 PRD“首版单游戏”的冲突；若按 Milestone 执行，需要关系表、迁移、服务/API、权限过滤和页面多选改造。
2. 用真实验证码/安全验证账号和真实受限账号校准检查项 7/8；当前 `na` 骨架不能算功能完成。
3. 在 M2-C 建立真实代理读回后补齐检查项 3/4。
4. 更新 M2-B 收口矩阵和稳定产品/工程基线，完成真实人工验收后才能判定 CLOSED。

## 5. M2-C 剩余工作与启动条件

CHG-20260805-033 共有六个交付任务：

1. 单个代理新增；Parse/Import 分离，预览零副作用。
2. 统一 `max_profile_count`，删除按平台配额模型，页面显示已用/剩余。
3. Desktop 分配入口、Tauri 桥、Agent 同步 mutation、Profile 互斥。
4. Cloud broker、分配/更换/解绑、先读回后写正式关系。
5. 仅从启用、检测正常、未过期且有余量的代理中推荐，并允许人工调整确认。
6. 外部代理 Diff、账号检查项 3/4、真实代理全链路验收和收口矩阵。

M2-C 没有可信的日历日期承诺。它可以在当前 Active CHG 完成治理转换后立即激活；在此之前只能修订计划，不能写 M2-C 运行时代码。当前治理转换依赖账号—游戏基数决策，以及检查项 7/8 的真实样本或明确延期决策。

## 6. 本次已核验和修正

- 主计划 Active CHG 从已完成的 CHG-031 修正为 CHG-20260805-032。
- 当前源码环境重建通过 Cloud、Agent、真实 BitBrowser、Desktop assets、DMG 和登录冒烟。
- 迁移 024 已恢复标签跨账号复用所需的唯一键。
- Decision 0010 的历史 `draft` 检查分支已删除并回归通过。
- M2-C 计划已消除检查项 3/4 的循环描述，并补入 Desktop 影响边界与外部代理 Diff 的必做范围。
