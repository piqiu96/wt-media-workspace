# T-08：真实链路回归与验收数据清理

原始数据见 `T-08-chain.json`。

## Worker／数据库／对象存储

三条真实任务（含一次代创建与同素材跨策略）全部由 Compose Worker 领取、Discovery Worker 准备输入并产出对象：

| 任务 | 策略 | 素材 | 负责人 | 创建人 | 成片 | 对象键 | 字节 | SHA256（DB＝下载） |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 325 | 44 | 170 | 3（pika） | 3 | 70 | `compose-outputs/325/3/output.mp4` | 329,883 | `9dd230fd…b969a4` |
| 326 | 44 | 175 | 3（pika） | 9（高级代创建） | 69 | `compose-outputs/326/3/output.mp4` | 213,187 | `b15601ae…eee18` |
| 327 | 45 | 170 | 9（高级） | 9 | 71 | `compose-outputs/327/1/output.mp4` | 329,883 | `9dd230fd…b969a4` |

- 同一素材 170 经策略 44／45 产出成片 70／71，负责人分别为 pika／CHG103高级；字节相同但归属不同，证明负责人不是从素材或创建人推断。
- 下载链接由 API 签发，三个对象均实际下载成功；下载文件的 SHA256 与数据库 `composite_outputs.sha256` 逐条一致。
- Worker 输入准备在修复 filetransfer INSERT 后恢复：修复前每次 transfer 创建都触发 MySQL 1136（列 19、值 20），修复提交 `97b9335` 并带“列值计数”回归测试；修复后用同一真实任务链复测。

## 防重、重试与下载

| 场景 | 实际 | 结果 |
| --- | --- | --- |
| `(策略 45, 素材 170)` 再次创建 | `created=[]`，`failed` 项 `15219 compose_task_conflict` | PASS |
| 对已成功任务 327 重试 | `15217 compose_task_not_retryable` | PASS |
| 成片 69 下载请求两次 | 两次返回同一 transfer id `transfer_01bc…`，未重复建任务 | PASS |
| 下载完成 | transfer 状态 success，213,187 bytes，SHA256 与对象／DB 一致 | PASS |

## 调度跳过

历史策略 42 无负责人：`compose_schedule_runs` 真实记录 `skipped_json=[{"reason":"operator_unavailable","material_id":0}]`，`created_count=0`，下一次运行时间正常推进；详见 `T-05-task-scope-and-snapshot.json`。

## 迁移与历史

- 收尾重跑迁移 `0 applied, 76 total`，074 已应用且不重复执行。
- 清理前 `compose_strategies/tasks/outputs` 为 9/22/19，负责人非空 2/3/3；其中历史段（策略 <44、任务 <325、成片 <69）非空计数均为 0。

## 验收数据清理

| 对象 | 处理 |
| --- | --- |
| 任务 325–327、尝试 249–255、成片 69–71、策略 44/45、使用记录 90/91 | 已删除 |
| 成片下载与两条素材准备 transfer | 已删除 |
| 临时用户 9/10 的会话与游戏范围 | 已删除 |
| 临时用户 9（chg103senior）／10（chg103admin） | 保留并置 `disabled`：`audit_logs` 仍有 33 条其操作记录，删除用户需连带删除审计行；未获授权删除审计，故保留身份记录但使其不可登录 |
| 清理后计数 | 策略 7、任务 19、成片 16，负责人非空均为 0；用户 5（含 2 个 disabled 验收账号） |
| 对象存储残留 | `compose-outputs/325|326|327/...` 三个开发桶对象未删除（数据库已无引用），登记在此 |

清理后历史列表、详情和“未记录”显示不受影响；本 CHG 新建的 44/45、325–327、69–71 不再出现在页面。
