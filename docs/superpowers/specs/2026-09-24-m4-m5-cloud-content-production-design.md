# M4-M5 Cloud 内容生产收敛设计

> 日期：2026-09-24  
> 状态：APPROVED（用户已确认按本方案直接更新全部文档）  
> 性质：分析与落地设计；稳定事实最终写入 Product、Engineering、Decision、Milestone 与 CHG

## 1. 目标

将 M4-M5 从“Desktop / Agent 本地合成 + Cloud Agent 自动生产”收敛为一条 Cloud-owned 内容生产链路：

```text
内容池
→ material
→ material_usage
→ compose_strategy
→ compose_task
→ Cloud Compose Worker + FFmpeg
→ composite_output
→ publication
```

M4 交付人工内容生产闭环，M5 在同一业务对象和执行底座上增加策略自动调度。Desktop / Local Agent 不再执行视频合成。

## 2. 已确认范围

### 2.1 产品模块

内容生产固定为六个入口：

1. 素材库；
2. 我的素材；
3. 合成策略；
4. 合成任务；
5. 我的成片；
6. 下载中心（全局顶部入口，以右侧 Drawer 展示）。

用户提供的六张界面图保存到 `wt-media-cloud/docs/product/m4-m5-content-production/assets/`，用于上述页面和 Drawer 的视觉参考。Cloud 仓库只保存图片与索引，不成为产品需求事实源。

### 2.2 数据对象

以下对象名与职责冻结，不得用近义表替代：

| 对象 | 固定职责 |
| --- | --- |
| `material` | 公共素材实体及源视频准备状态 |
| `material_usage` | “我的素材”关系 |
| `compose_strategy` | 模板参数、视频参数及自动执行规则 |
| `compose_task` | 一次具体视频生产行为，也是 Worker 领取和恢复的业务任务 |
| `composite_output` | 成功生成的唯一成片资产 |
| `file_transfer_task` | 原素材或成片的横向文件传输任务 |

禁止新增：

- `material_user_relation`、`user_material`、`favorite_material`；
- `production_rule`；
- `compose_pool_item` 或另一张重复生产任务表；
- 为本次链路另建 `composite_output_download_task`。

当前 Cloud 代码只有 `materials` 表，其余对象尚未落库。本设计中的“保留已有对象语义”指冻结已经确认的业务名字和职责；后续实现仍需用增量 Migration 创建尚不存在的表和字段。

### 2.3 执行边界

Cloud 拥有：

- `compose_strategy`、`compose_task`、`file_transfer_task` 与 `composite_output` 正式事实；
- Scheduler 到期扫描和防重；
- Compose Worker 原子领取、租约、heartbeat、超时、重试和恢复；
- Cloud 运行环境中的 FFmpeg；
- 原素材准备、临时工作目录、对象存储上传和完整性校验。

Desktop / Local Agent 保留：

- 浏览器自动化、发布和互动；
- BitBrowser、Profile、Cookie 与本机安全能力；
- 把用户要求的原素材或成片下载并落到运营电脑；
- 本地文件打开、路径选择和下载进度展示。

Desktop / Local Agent 删除：

- 视频合成；
- FFmpeg 执行；
- 本地合成任务恢复。

## 3. M4 与 M5 边界

### 3.1 M4：内容生产闭环

M4 必须形成以下真实闭环：

```text
material
→ material_usage
→ 人工选择 compose_strategy
→ 创建 compose_task
→ 必要时准备原素材
→ Cloud Worker + FFmpeg
→ composite_output
→ 我的成片
→ 下载
```

M4 包含：

- 素材库和来源查看；
- 我的素材；
- 手工维护和选择合成策略；
- 人工创建、查看、取消与重试合成任务；
- Cloud Compose Worker；
- 我的成片；
- 全局下载中心；
- 原素材与成片下载。

M4 不要求 Scheduler 自动创建合成任务。

### 3.2 M5：自动生产

M5 在 M4 已验证底座上增加：

```text
compose_strategy.schedule
→ Scheduler
→ 幂等创建 compose_task
→ Worker Pool
→ composite_output
```

M5 包含：

- 策略启停和自动执行配置；
- 定时与周期触发；
- 单次和每日数量上限；
- 批量创建生产任务；
- Worker 并发与资源控制；
- 超时、heartbeat、重试和失败恢复；
- 调度重启恢复与同周期防重。

## 4. 状态机

### 4.1 原素材视频状态

```text
not_downloaded
→ downloading
→ ready

downloading
→ failed
→ downloading
```

内容池转为 `material` 时只要求保存源链接，不立即下载文件。用户主动下载或创建合成任务且源视频未就绪时，才创建 `file_transfer_task`。

### 4.2 合成任务

```text
pending
→ running
→ success

pending / running
→ failed

pending / running
→ cancelled
```

只有 `success` 且输出文件完成校验和对象存储落盘后，才创建 `composite_output`。失败、取消和超时不得生成假成片。

### 4.3 文件传输任务

```text
pending
→ running
→ success

pending / running
→ failed

pending / running
→ cancelled
```

`file_transfer_task` 至少区分：

- `asset_type`：`material` 或 `composite_output`；
- `purpose`：Cloud 合成前准备或本地下载；
- `execution_scope`：Cloud Worker 或 Local Agent；
- 文件大小、完成字节数、速度、预计剩余时间、错误信息；
- 重试次数和最终完整性校验结果。

这是一张任务表的不同用途，不拆成多张下载表。

## 5. Cloud 技术设计

### 5.1 进程与目录

沿用模块化单体，不引入 MQ、微服务或工作流引擎：

```text
cmd/compose-scheduler
cmd/compose-worker
cmd/file-transfer-worker（只有独立运行确有必要时才建立）

internal/scheduler
internal/jobs
internal/modules/production
internal/infra/storage
internal/infra/media
```

最终目录必须服从 Cloud 仓库实时 `AGENTS.md`：生产初始化只由 bootstrap 发起；Scheduler 只创建 pending 任务；Worker 原子领取任务后调用 Job；业务模块不启动后台 goroutine；SQL 只在 Repository。

### 5.2 Scheduler

Scheduler 只做：

- 扫描启用且到期的 `compose_strategy`；
- 计算本周期候选素材与数量上限；
- 以策略、计划周期和素材作为幂等键创建 `pending compose_task`；
- 推进下一次执行时间；
- 记录跳过与防重结果。

Scheduler 不下载文件、不执行 FFmpeg、不在同一调用栈内调用 Worker。

### 5.3 Worker Pool

Worker 使用数据库任务表实现领取和恢复：

- 原子领取 `pending` 或已过期可恢复任务；
- 有界并发，默认值通过 `config/scheduler` 配置；
- 每个任务持有租约并周期写 heartbeat；
- 超时后先终止本次 FFmpeg 子进程，再将任务置为可判定失败或可重试状态；
- 技术失败按上限退避重试，业务失败不盲目重试；
- Worker 崩溃后由租约过期恢复；
- 同一个 `compose_task` 同时只能有一个执行者。

首版不使用 MQ；Worker 通过数据库原子领取形成轻量队列。

### 5.4 FFmpeg 和文件

- FFmpeg 固定在 Cloud Worker 镜像或部署产物中，不依赖系统 PATH；
- 记录版本、SHA256、编码器、Filter 与许可证信息；
- 每个任务使用隔离临时目录；
- 输入准备完成后校验文件存在、大小、媒体可读性和必要 Hash；
- 输出先写临时文件，校验通过后上传对象存储；
- `composite_output` 与对象存储键在事务边界内形成可恢复关联；
- 进程退出、任务取消和失败后清理可再生临时文件，不删除正式对象存储资产。

## 6. UI 与下载中心

六张参考图确定以下信息架构，不冻结其中演示数字：

| 页面 | 关键动作 |
| --- | --- |
| 素材库 | 加入我的素材、下载原视频、查看详情 |
| 我的素材 | 创建合成任务、查看进度、下载原视频、移出 |
| 合成策略 | 新建、编辑、复制、启停自动执行、查看任务 |
| 合成任务 | 筛选、查看详情/日志、取消、重试、查看成片 |
| 我的成片 | 预览、下载、去发布、查看来源 |
| 下载中心 Drawer | 查看进行中和最近完成、进度、速度、剩余时间、暂停/取消/重试、打开文件 |

下载中心是横向能力，入口位于顶部导航，不挂在“素材库”子菜单下。

## 7. 文档落地

本次更新：

- `delivery/MASTER_IMPLEMENTATION_PLAN.md` 的 M4、M5 及受影响 M10 描述；
- 详细第五章和总 PRD 第五章摘要；
- 两份工程架构基线；
- 新 ADR 与专项工程设计；
- 新 M4、M5 Milestone 闭环；
- 新 planned CHG-061；
- Cloud 仓库 UI 图片资产及索引。

所有修改使用“2026-09-24 M4-M5 调整”标记。当前活动 CHG-057、`delivery/LEDGER.md` 和 `.ai/CURRENT_CONTEXT.md` 不修改。

## 8. 验证重点

1. 全部稳定文档只使用 `compose_strategy`、`compose_task` 和 `file_transfer_task` 作为新链路对象；
2. M4-M5 正文不再把 `production_rule`、`compose_pool_item`、本地 Agent 合成或 Cloud Agent 合成描述为有效方案；
3. M4/M5 Milestone 分别有用户目标、前置、操作、系统动作、成功事实、假成功禁止项和 CHG 顺序；
4. ADR 明确 supersede 的旧边界以及不受影响的发布/互动/本机能力；
5. 六张 PNG 在 Cloud 仓库有稳定文件名、可打开且与原图 Hash 一致；
6. 治理校验通过，且不覆盖 Workspace 现有未提交修改。

