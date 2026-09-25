# M4 Cloud 内容生产闭环

- Milestone status: `IN_PROGRESS`
- Product baseline: `docs/product/prd/详细文档/第五章_素材生产.md`
- Engineering baseline: `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md`
- Decision: `docs/decisions/0017-m4-m5-cloud-owned-content-production.md`
- Confirmed: 2026-09-24，用户确认按 Cloud Scheduler / Worker / FFmpeg 方案直接更新并实施

## 1. 里程碑目标

运营可以从素材库把素材加入“我的素材”，选择合成策略创建任务；Cloud 在运营电脑离线时仍能准备源视频、执行真实 FFmpeg、上传对象存储并生成成片；运营随后可以预览、下载或进入发布管理。

```text
material
→ material_usage
→ compose_strategy
→ compose_task
→ Cloud Compose Worker + FFmpeg
→ composite_output
→ file_transfer_task
→ 运营电脑本地文件 / 去发布
```

M4 不包含定时自动创建合成任务；自动调度属于 M5。

## 2. 前置条件

- M3 为 `DONE`，`source_content → material` 已有真实闭环；
- Cloud 模块化单体、MySQL、独立 Scheduler/Worker CMD 模式可复用；
- M2 用户、业务范围、Desktop 和 Local Agent 基线保持可用；
- ADR-0017 已接受；
- 当前活动工程优化 CHG 已完成；M4-A 于 2026-09-26 激活，继续保持任一时刻仅一个 active CHG。

## 3. 闭环拆分与 CHG 顺序

| 阶段 | 独立结果 | CHG | 状态 |
| --- | --- | --- | --- |
| M4-A | 素材库、“我的素材”和原素材懒加载准备/下载 | CHG-20260924-061 | `IMPLEMENTING` |
| M4-B | `compose_strategy` 模板、参数、版本、快照和人工选择 | M4-C2 | `NOT_STARTED` |
| M4-C | `compose_task`、对象存储、Cloud Worker 与真实 FFmpeg | M4-C3～M4-C5 | `NOT_STARTED` |
| M4-D | 我的成片、下载中心与 Local Agent 本地文件落地 | M4-C6～M4-C7 | `NOT_STARTED` |
| M4-E | 真实视频、故障恢复、Cloud Web/Desktop WebView 综合验收 | M4-C8 | `NOT_STARTED` |

后续 M4-C2～M4-C8 在前置闭环真实验收后逐个建立 CHG，不预先创建多个 active 记录。

## 4. 闭环卡 M4-A：素材库与我的素材

### 用户目标

运营能判断哪些素材可以用于生产，把素材加入自己的生产集合，并在需要时准备或下载原视频。

### 前置条件

- 用户已登录且拥有素材对应的团队/游戏范围；
- `material` 有来源链接与来源快照；
- Cloud 和 Local Agent 分别具备受控的 Cloud 文件准备、本地文件落地能力。

### 用户操作顺序

1. 打开“内容生产 → 素材库”；
2. 查看来源和视频状态；
3. 点击“加入我的素材”；
4. 在“我的素材”查看新关系；
5. 可选：点击“下载原视频”，在顶部下载中心查看进度；
6. 可选：移出后恢复同一素材关系。

### 系统与外部动作

- Cloud 校验权限和素材可用性；
- 原子创建或恢复 `material_usage`；
- 用户下载创建 `file_transfer_task(asset_type=material, purpose=user_download, execution_scope=local_agent)`；
- Local Agent 使用短时受控下载信息写入运营电脑，校验大小/Hash 并回报进度；
- 合成前准备使用同一任务对象但 `purpose=compose_input_prepare, execution_scope=cloud`。

### 成功必须同时满足的事实

- 同一用户、同一素材只有一个有效 `material_usage`；
- 素材进入库时未下载视频仍是合法事实，页面准确显示 `not_downloaded`；
- 下载中心的进度、速度、剩余时间和完成结果来自真实传输；
- 下载成功后本地文件存在且完整性校验通过；
- 移出/恢复不删除历史关系 ID、任务或成片；
- 无权限素材不能被查看、加入或下载。

### 失败时禁止出现的假成功

- 只创建 `material_usage` 就显示源视频已就绪；
- API 返回 200 但未创建关系或下载任务；
- 下载任务标记成功但文件不存在、字节不足或 Hash 不一致；
- 重复点击产生多条有效关系；
- 取消任务后临时文件被当作完整文件打开。

### 对应 CHG

- `delivery/active/CHG-20260924-061/change.md`

## 5. 闭环卡 M4-B：人工 Cloud 合成

### 用户目标

运营从“我的素材”选择策略创建任务，无需保持 Desktop 在线，即可得到可播放、可追溯的成片。

### 前置条件

- M4-A 已验收；
- 至少一个可用 `compose_strategy` 和模板版本；
- Cloud Worker 的 FFmpeg / FFprobe、临时目录和对象存储健康。

### 用户操作顺序

1. 在“我的素材”选择一条或多条素材；
2. 选择 `compose_strategy` 并确认允许覆盖的参数；
3. 创建任务；
4. 在“合成任务”查看排队、阶段、进度和结果；
5. 成功后进入“我的成片”预览、下载或去发布。

### 系统与外部动作

- Cloud 为每个素材创建独立 `compose_task` 和不可变策略快照；
- 源视频未就绪时创建/复用 Cloud 文件准备任务；
- Worker 原子领取任务、持有租约并写 heartbeat；
- Worker 执行 FFprobe 输入校验、FFmpeg 合成、FFprobe 输出校验和对象存储上传；
- Cloud 在文件校验与对象存储落盘后事务创建 `composite_output`。

### 成功必须同时满足的事实

- HTTP 创建请求快速返回，不同步等待 FFmpeg；
- 同一任务同时只有一个 Worker；
- 来源素材、`material_usage`、策略快照、任务和成片可互相追溯；
- 成片文件真实存在、可播放且对象存储校验通过；
- Desktop 退出不影响 Cloud 任务继续完成；
- 页面状态与数据库、Worker 执行和对象存储事实一致。

### 失败时禁止出现的假成功

- 源视频未就绪仍直接运行 FFmpeg；
- FFmpeg 非零退出、输出损坏或上传失败仍创建 `composite_output`；
- 只更新任务状态而遗留运行中的 FFmpeg 进程；
- Worker 重启后同一任务出现两个并行执行；
- 页面有演示成片但对象存储无真实文件。

### 对应 CHG

- M4-C2～M4-C6（待按独立结果建立）。

## 6. 闭环卡 M4-C：下载与发布衔接

### 用户目标

运营在全局下载中心统一管理原素材和成片下载，并把成片带入第六章发布流程。

### 前置条件

- 至少一个可下载 `material` 或 `composite_output`；
- Desktop、Local Agent 和本地保存目录可用。

### 用户操作顺序

1. 点击顶部“下载”打开右侧 Drawer；
2. 查看进行中与最近完成；
3. 取消失败/不需要的任务，或重试失败任务；
4. 成功后打开文件/目录；
5. 从“我的成片”点击“去发布”。

### 系统与外部动作

- Cloud 创建并持久化 `file_transfer_task`；
- Local Agent 下载、原子落盘并上报进度和 Hash；
- “去发布”把 `composite_output` 引用传入发布管理，但不提前创建成功发布事实。

### 成功必须同时满足的事实

- 原素材和成片共用相同下载任务和 Drawer；
- Cloud 不保存运营电脑绝对路径；
- 本地文件删除不删除 Cloud 素材或成片；
- 下载成功不创建 `publication`；
- 发布入口能读取成片来源和文件事实。

### 失败时禁止出现的假成功

- 前端模拟进度而执行器没有传输；
- 清理下载记录同时删除素材、成片或本地文件；
- 下载完成被标记为已发布；
- Cloud 尝试直接写运营电脑文件系统。

### 对应 CHG

- M4-C7～M4-C8（待按独立结果建立）。

## 7. M4 验收矩阵

| AC | 验收要求 | 最低证据 | 状态 |
| --- | --- | --- | --- |
| M4-AC-01 | 素材库展示真实来源与四态视频状态 | MySQL + API + UI 截图 | `TODO` |
| M4-AC-02 | `material_usage` 创建、去重、移出和恢复正确 | 并发测试 + UI 走查 | `TODO` |
| M4-AC-03 | 原素材只按需准备或下载 | 转素材后无文件、触发后有任务的对照 | `TODO` |
| M4-AC-04 | 人工任务保存策略快照 | Migration/API/数据库证据 | `TODO` |
| M4-AC-05 | Cloud Worker 使用真实 FFmpeg 生成可播放视频 | 媒体探针 + 真实文件 | `TODO` |
| M4-AC-06 | 成片只在对象存储落盘和校验后创建 | 故障注入对照 | `TODO` |
| M4-AC-07 | 取消、失败、超时和 Worker 重启无双执行/假成片 | 受控故障证据 | `TODO` |
| M4-AC-08 | 我的成片可预览、追溯、下载和去发布 | Cloud Web + Desktop WebView | `TODO` |
| M4-AC-09 | 下载中心显示真实进度并完成本地 Hash 校验 | Local Agent + 本地文件证据 | `TODO` |
| M4-AC-10 | Desktop / Agent 不存在合成执行路径 | 边界扫描 + Contract 测试 | `TODO` |
| M4-AC-11 | 三角色和业务范围正确 | 权限矩阵 + 越权测试 | `TODO` |
| M4-AC-12 | Cloud、Agent、Desktop 各自测试与独立提交完成 | 测试摘要 + Git 提交 | `TODO` |

## 8. M4 DONE Gate

M4 只有在 M4-AC-01～12 全部 PASS、自动测试与真实依赖验证完成，并经用户按真实操作链路签收后才能进入 `DONE`。页面存在、任务记录存在、API 200、Mock 视频或构建成功都不能单独证明 M4 完成。
