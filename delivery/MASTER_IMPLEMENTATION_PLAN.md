# 模块化自媒体运营平台：代码实施总计划

> 日期：2026-07-14  
> 适用项目：WT Media 模块化自媒体运营平台  
> 执行方式：一个总路线、一个当前变更、一次只完成一个可验证闭环  
> 运行仓库：`wt-media-cloud`、`wt-media-agent`、`wt-media-desktop`  
> 治理仓库：`wt-media-workspace`

## 1. 总原则

本项目不按产品章节逐章编码，也不按“先写完 Cloud、再写 Agent、最后写 Desktop”的横向方式实施。

采用纵向闭环路线：

```text
M0 项目治理与工程基线
→ M1 Cloud-Agent-Desktop 最小任务闭环
→ M2 用户、角色、媒体账号与运行环境
→ M3 抖音内容发现到素材入库
→ M4 素材使用与本地合成闭环
→ M5 云端自动生产与云端成片池
→ M6 发布通用底座与 B站辅助发布
→ M7 百家号辅助发布
→ M8 互动管理闭环
→ M9 效果采集与数据统计
→ M10 打包、升级、诊断与稳定性验收
```

每个阶段都必须产生可以运行、可以测试、可以演示的闭环。M1 Cloud-Agent-Desktop 最小任务闭环完成前，不进入大规模业务模块开发。

## 2. 文档和事实源

```text
wt-media-workspace/
├── docs/
│   ├── product/                    # 当前有效产品事实
│   ├── engineering/                # 当前有效工程架构
│   ├── contracts/                  # 人类可读的跨仓库协议治理
│   └── decisions/                  # 少量重大决策及原因
├── delivery/
│   ├── MASTER_IMPLEMENTATION_PLAN.md
│   ├── LEDGER.md                   # 当前 Active CHG 索引，不是历史归档
│   └── active/
│       └── CHG-YYYYMMDD-NNN/
│           ├── change.md           # 当前变更唯一执行依据
│           └── evidence/           # 测试、Spike、Diff、人工验证事实
├── config/
│   ├── contract-map.yaml           # 机器可读协议归属和消费关系
│   └── release-matrix.yaml         # 已验证版本组合
├── skills/
├── scripts/
└── templates/
```

| 位置 | 保存内容 | 不保存内容 |
|---|---|---|
| `docs/product` | 当前系统应该做什么 | 每日开发进度 |
| `docs/engineering` | 当前系统应该如何设计 | 临时实施清单 |
| `docs/contracts` | 协议所有权、兼容性、变更流程和跨项目协作规范 | 完整 OpenAPI、Schema、DTO、事件定义 |
| `docs/decisions` | 重大且长期有效的取舍原因 | 普通功能讨论 |
| `delivery/MASTER_IMPLEMENTATION_PLAN.md` | 全系统实施顺序和执行纪律 | 代码级详细方案 |
| `delivery/active/<CHG>/change.md` | 当前变更范围、任务、验收和检查点 | 完整产品文档副本 |
| `delivery/active/<CHG>/evidence/` | 本次验证事实 | 第二份需求文档 |
| `delivery/LEDGER.md` | 当前 Active CHG 索引 | 已完成 CHG 历史归档 |

实际接口定义由接口提供方仓库持有：

- Cloud 相关 Contract 归 `wt-media-cloud`；
- Local Agent API 和 SSE 归 `wt-media-agent`；
- Workspace 不保存重复正式定义。

完成 CHG 后：

1. 必要产品结论回写 `docs/product`；
2. 必要架构结论回写 `docs/engineering`；
3. 必要协议治理结论回写 `docs/contracts`；
4. 重大取舍写入 `docs/decisions`；
5. 更新 `config/release-matrix.yaml` 中已验证组合；
6. 确认各仓库独立提交；
7. 从 `delivery/active` 和 `delivery/LEDGER.md` 移除已完成 CHG；
8. 由 Git 和 PR 保留执行历史。

## 3. 里程碑路线

每个里程碑只允许以下状态：

```text
NOT_STARTED
IN_PROGRESS
BLOCKED
VERIFYING
DONE
```

里程碑不能因为代码目录已经存在而标记为 `DONE`。必须逐项核验代码、自动测试、Contract、Evidence、人工验证、跨仓库集成、Git 提交和退出条件。

每个里程碑必须记录：

| 字段 | 内容 |
|---|---|
| 状态 | 当前里程碑状态 |
| 目标 | 完成后新增的可验证能力 |
| 依赖 | 必须完成的前置里程碑 |
| 候选 CHG | 规划中的变更单元，只记录，不自动激活 |
| Active CHG | 当前激活变更，没有则为 `None` |
| 退出条件 | 进入下一里程碑前必须满足的条件 |
| Evidence | 里程碑综合验证索引 |
| 完成日期 | `DONE` 后记录 |
| Commit/Tag | 相关提交和版本标签 |

### M0：项目治理与工程基线

| 字段 | 内容 |
|---|---|
| 状态 | `DONE` |
| 目标 | 建立四仓库协作、Codex 执行控制、基础构建、测试和质量门禁，为后续长期实施提供稳定环境。 |
| 依赖 | None |
| Active CHG | None |
| Evidence | CHG-002 执行控制提交；CHG-003 Master Plan 固化提交；CHG-004 工程骨架审计 evidence 与三端 M0 骨架提交；CHG-005 最小启动和健康检查 evidence；CHG-006 测试、CI、Contract Map 和版本矩阵 evidence；CHG-007 M0 综合验收 evidence。 |
| 完成日期 | 2026-07-14 |
| Commit/Tag | CHG-002 commits: `63092e8`, `1504355`, `e20f672`, `681d9c9`, `6e800a0`, `b439038`; CHG-003 commits: `a7d49fe`, `784b3b8`; CHG-004 runtime commits: Cloud `c28bd3d`, Agent `4ef0dfe`, Desktop `0774635`; Workspace evidence commit `67245d2`; CHG-005 runtime commits: Cloud `3bb6028`, Agent `2c2562f`, Desktop `54e6e70`; Workspace evidence commit `2442ba0`; CHG-006 runtime commits: Cloud `f00ae41`, Agent `1351f5f`, Desktop `54d7b6f`; Workspace evidence commit `a4d141e`; CHG-007 Workspace evidence commit `716c143`。 |

候选 CHG：

```text
M0-C1 项目 CHG 执行控制体系
M0-C1b M0-M10 Master Plan 固化
M0-C2 四仓库工程结构与规则基线
M0-C3 Cloud、Agent、Desktop 最小启动和健康检查
M0-C4 测试、CI、Contract Map 和版本矩阵
M0-C5 M0 综合验收
```

退出条件：

- Skill、Active CHG、Checkpoint、Q-xx、Evidence 和 DONE 门禁能实际使用；
- 从最外层 `wt-media/` 启动 Codex 能识别四仓库；
- Cloud、Agent、Desktop 能独立构建和测试；
- Workspace 不成为运行时依赖；
- Git 工作区、提交和交付历史可追踪；
- `contract-map.yaml` 和 `release-matrix.yaml` 符合当前已验证状态；
- M0 综合验收通过。

本阶段不做：

- 正式业务模型；
- 正式用户认证；
- 任务执行协议；
- FFmpeg 合成；
- 平台自动化；
- 正式安装包。

### M1：Cloud-Agent-Desktop 最小任务闭环

| 字段 | 内容 |
|---|---|
| 状态 | `DONE` |
| 目标 | 证明 Cloud、Agent、Desktop 三端技术主干能够真实运行。 |
| 依赖 | M0 `DONE` |
| Active CHG | None |
| Evidence | CHG-008 M1-C1 Cloud-Agent Contract 与版本兼容 evidence；CHG-009 M1-C2 Agent 注册和心跳 evidence；CHG-010 M1-C3 task 创建、领取、租约与幂等 evidence；CHG-011 M1-C4 noop Executor 和状态回传 evidence；CHG-012 M1-C5 Local Agent HTTP、SSE 与离线待回传 evidence；CHG-013 M1-C6 Desktop 启停 Agent 和状态展示 evidence；CHG-014 M1-C7 三端真实跨端集成验证 evidence。 |
| 完成日期 | 2026-07-14 |
| Commit/Tag | CHG-008 commits: Cloud `d2acf2a`; Agent `9a97b2d`; Workspace `fab15d3`, `1cac21f`, `559f907`; CHG-009 commits: Cloud `047d006`, `8cb351a`; Agent `eb5183d`, `482d1f8`; Workspace `e607c98`, `98220b3`; CHG-010 commits: Cloud `89d776b`; Agent `356aa3f`; Workspace `9a4ccf3`, `6e3d216`; CHG-011 commits: Cloud `90daf2e`; Agent `598e0eb`; Workspace `cdeb63c`, `100c09c`; CHG-012 commits: Agent `aaeabdb`; Workspace `edc5e14`, `c2aa5f8`; CHG-013 commits: Desktop `a8f8eef`; Workspace `cf0a49c`, `cd626c2`; CHG-014 commits: Workspace `8859162`, `b86e34c`。 |

目标闭环：

```text
Cloud 创建 noop_task
→ Agent 注册并领取
→ Agent 上报 started / progress / succeeded
→ Cloud 保存正式状态
→ Desktop 启动和观测 Local Agent
→ Desktop 页面显示任务进度
```

候选 CHG：

```text
M1-C1 Cloud-Agent Contract 与版本兼容
M1-C2 Agent 节点注册和心跳
M1-C3 task 创建、领取、租约与幂等
M1-C4 noop Executor 和状态回传
M1-C5 Local Agent HTTP、SSE 与离线待回传
M1-C6 Desktop 启停 Agent 和状态展示
M1-C7 三端真实跨端集成验证
```

退出条件：

- 同一个任务不会被两个 Agent 同时执行；
- Agent 中断后任务可恢复或释放；
- Cloud 暂时不可达时结果不会丢失；
- Desktop 不直接读取 Agent SQLite；
- Desktop Vue 不持有 Local Token；
- 三端有自动测试；
- 有真实跨端演示和 Evidence。

### M2：用户、角色、媒体账号与运行环境

| 字段 | 内容 |
|---|---|
| 状态 | `IN_PROGRESS` |
| 目标 | 建立发布、互动、任务分配和本地执行依赖的账号与运行环境基础。 |
| 依赖 | M1 `DONE` |
| Active CHG | `CHG-20260714-018` |
| Evidence | CHG-015 M2-C1、CHG-016 M2-C2、CHG-017 M2-C3 已完成；CHG-018 M2-C4 Agent 节点、Profile 属主和运行环境上报进行中。M2-C6 需补充真实 MySQL/比特浏览器集成验收。 |
| 完成日期 | None |
| Commit/Tag | CHG-015 commits: Cloud `50b5c8d`, `03b0dcc`; Workspace `f3e7d1a`, `51ab7de`, `e79db94`, `6576c44`, `a1f12d7`。CHG-016 commits: Cloud `18f687a`, `8eb70ba`; Workspace `266595f`, `3c65f6e`, `92c4565`。CHG-017 commits: Agent `14e51be`, `f0257b5`; Cloud `bba30ef`, `727ad9e`; Workspace `0bb7ba8`, `b67d493`。 |

候选 CHG：

```text
M2-C1 用户认证、单活会话和三角色权限
M2-C2 媒体账号模型和分配
M2-C3 比特浏览器用户与 Profile 绑定
M2-C4 Agent 节点、Profile 属主和运行环境上报
M2-C5 Profile 并发控制与敏感任务校验
M2-C6 用户账号运行环境综合验收
```

退出条件：

- 可以创建和分配媒体账号；
- Agent 能确认 Profile 和账号归属；
- 非属主不能执行敏感任务；
- 同一 Profile 的敏感任务被拒绝或串行；
- Cloud 是正式账号事实来源；
- Desktop 不复制账号业务规则。

### M3：抖音内容发现到素材入库

| 字段 | 内容 |
|---|---|
| 状态 | `NOT_STARTED` |
| 目标 | 打通链接导入、关键词搜索、作者监控到素材入库的首条业务数据闭环。 |
| 依赖 | M2 `DONE` |
| Active CHG | None |
| Evidence | None，未进入里程碑验证。 |
| 完成日期 | None |
| Commit/Tag | None |

目标闭环：

```text
链接导入 / 关键词搜索 / 作者监控
→ 抓取任务
→ crawl_result
→ source_content
→ content_lead
→ material
```

候选 CHG：

```text
M3-C1 抓取任务 Contract 和基础模型
M3-C2 抖音多链接导入
M3-C3 抖音关键词搜索
M3-C4 抖音作者监控和定时任务
M3-C5 crawl_result 与 source_content 去重
M3-C6 content_lead 查看、筛选和领取
M3-C7 精准词规则与 material 转化
M3-C8 内容发现真实业务闭环验收
```

明确不做：

- B站搜索；
- 小红书搜索；
- 百度搜索；
- Excel 导入；
- 竞品账号监控；
- 动态抓取工作流平台。

退出条件：

- 重复作品不会重复创建 `source_content`；
- 抓取失败不会产生正式素材；
- 精准词和泛化词行为明确不同；
- 原始抓取数据可追溯；
- 一次真实关键词或作者任务能够生成可用 `material`。

### M4：素材使用与本地合成闭环

| 字段 | 内容 |
|---|---|
| 状态 | `NOT_STARTED` |
| 目标 | 打通素材领取、合成任务、本地 Agent FFmpeg 执行和成片元数据闭环。 |
| 依赖 | M3 `DONE` |
| Active CHG | None |
| Evidence | None，未进入里程碑验证。 |
| 完成日期 | None |
| Commit/Tag | None |

目标闭环：

```text
material
→ material_usage
→ compose_pool_item
→ task
→ Local Agent + FFmpeg
→ composite_output
```

候选 CHG：

```text
M4-C1 material_usage 与素材领取
M4-C2 合成模板、版本与参数 Schema
M4-C3 合成策略、版本和快照
M4-C4 compose_pool_item 与合成任务台
M4-C5 Agent FFmpeg 环境和能力检查
M4-C6 本地视频合成 Executor
M4-C7 composite_output、失败重试和强制中断
M4-C8 本地合成真实视频闭环验收
```

关键约束：

- 正式运行不依赖系统 Python；
- FFmpeg 不依赖系统 PATH；
- Agent 不自行创建正式业务任务；
- 失败任务不进入成片列表；
- 成片默认保存在本地；
- Cloud 保存正式元数据和必要引用。

退出条件：

- 能从一个真实素材生成可播放视频；
- 来源素材、模板版本、策略版本和参数快照可追溯；
- FFmpeg 不兼容时禁止执行；
- 失败和重试状态明确；
- 成功成片能够进入发布流程。

### M5：云端自动生产与云端成片池

| 字段 | 内容 |
|---|---|
| 状态 | `NOT_STARTED` |
| 目标 | 复用本地合成核心，打通 Cloud Agent 生产、云端成片池、领取、下载和清理。 |
| 依赖 | M4 `DONE` |
| Active CHG | None |
| Evidence | None，未进入里程碑验证。 |
| 完成日期 | None |
| Commit/Tag | None |

目标闭环：

```text
production_rule
→ Cloud Agent
→ composite_output
→ composite_output_pool
→ composite_output_claim
→ 下载到本地
```

候选 CHG：

```text
M5-C1 production_rule 与调度
M5-C2 Cloud Agent 合成模式和对象存储
M5-C3 composite_output_pool 和范围策略
M5-C4 自动分配、人工分配与独占领取
M5-C5 云端下载和本地成片记录
M5-C6 7 天清理与重复风险提示
M5-C7 云端生产和成片池综合验收
```

明确不做：

- 独立生产规则管理平台；
- 动态工作流引擎；
- 独立策略组表；
- `composite_output_download_task`；
- 独立 `pool_policy` 表。

退出条件：

- Local Agent 和 Cloud Agent 复用同一合成核心；
- 同一成片不会被多人重复领取；
- 领取失败不会永久锁死；
- 下载后能进入本地成片管理；
- 清理任务和重复风险提示可验证。

### M6：发布通用底座与 B站辅助发布

| 字段 | 内容 |
|---|---|
| 状态 | `NOT_STARTED` |
| 目标 | 先建立发布通用模型，再完成第一个真实平台发布闭环。 |
| 依赖 | M5 `DONE` |
| Active CHG | None |
| Evidence | None，未进入里程碑验证。 |
| 完成日期 | None |
| Commit/Tag | None |

目标闭环：

```text
composite_output
→ publication
→ 发布任务
→ Agent 打开指定 Profile
→ 上传和填写
→ waiting_manual_submit
→ 运营人工提交
→ 链接补录和结果回写
```

候选 CHG：

```text
M6-C1 publication 模型和正式状态
M6-C2 发布任务 Contract 和串行队列
M6-C3 平台 Adapter 通用接口
M6-C4 B站固定流程与元素 JSON
M6-C5 单条发布
M6-C6 批量配置和串行执行
M6-C7 人工提交、链接补录和手工补录
M6-C8 失败、丢弃、重试和 result_uncertain
M6-C9 B站真实辅助发布验收
```

关键约束：

- Agent 不点击最终发布按钮；
- 同一 Profile 一次只执行一个敏感任务；
- 结果不明确时不得盲目重试；
- 不建设运营可视化流程编排器。

退出条件：

- 完成一条真实 B站辅助发布；
- 批量任务严格串行；
- 异常状态和重试行为明确；
- 人工提交后可以补录链接；
- Agent 重启后可以识别未完成任务。

### M7：百家号辅助发布

| 字段 | 内容 |
|---|---|
| 状态 | `NOT_STARTED` |
| 目标 | 通过第二个平台验证 Adapter 边界，而不是复制一套发布系统。 |
| 依赖 | M6 `DONE` |
| Active CHG | None |
| Evidence | None，未进入里程碑验证。 |
| 完成日期 | None |
| Commit/Tag | None |

候选 CHG：

```text
M7-C1 百家号字段和元素配置
M7-C2 百家号 Adapter
M7-C3 百家号单条和批量辅助发布
M7-C4 百家号真实发布与 B站回归验收
```

退出条件：

- 没有复制 B站通用发布逻辑；
- Cloud 不包含页面元素操作细节；
- Adapter 不直接修改 Cloud 正式状态；
- 百家号真实辅助发布完成；
- B站功能回归通过。

### M8：互动管理闭环

| 字段 | 内容 |
|---|---|
| 状态 | `NOT_STARTED` |
| 目标 | 完成点赞、收藏和评论任务闭环。 |
| 依赖 | M7 `DONE` |
| Active CHG | None |
| Evidence | None，未进入里程碑验证。 |
| 完成日期 | None |
| Commit/Tag | None |

核心对象：

```text
interaction_batch
→ tracked_object
→ interaction_task
→ interaction_item
→ task
```

候选 CHG：

```text
M8-C1 互动核心模型
M8-C2 目标圈定和 interaction_item 生成
M8-C3 公共模板和个人模板
M8-C4 DeepSeek 评论生成
M8-C5 点赞和收藏 Executor
M8-C6 评论 Executor
M8-C7 窗口粒度、风控和异常处理
M8-C8 互动真实业务闭环验收
```

明确不建设：

- 关注；
- 转发；
- 私信；
- 主动搜索互动作品。

这些不是暂缓功能，不允许创建占位接口或未来状态。

退出条件：

- 一个 `tracked_object` 对应一个 `interaction_task`；
- 每个账号生成一个 `interaction_item`；
- 每次真实执行和重试产生新的 `task`；
- 个人模板仅本人可见；
- 高风险结果不确定时停止自动重试；
- 不存在明确排除能力的残留实现。

### M9：效果采集与数据统计

| 字段 | 内容 |
|---|---|
| 状态 | `NOT_STARTED` |
| 目标 | 让发布、互动、素材和策略形成可追踪的数据闭环。 |
| 依赖 | M8 `DONE` |
| Active CHG | None |
| Evidence | None，未进入里程碑验证。 |
| 完成日期 | None |
| Commit/Tag | None |

候选 CHG：

```text
M9-C1 跟踪对象和 metric_snapshot
M9-C2 B站效果采集
M9-C3 百家号效果采集
M9-C4 素材、策略、账号和平台聚合
M9-C5 基础运营看板
M9-C6 生产信号与重复风险数据
M9-C7 统计闭环验收
```

关键约束：

- Analytics 只读取正式业务事实；
- 统计异常不能修改原始业务数据；
- 原始快照和聚合结果分离；
- 首版不建设复杂实时数仓。

退出条件：

- 发布链接可以建立跟踪对象；
- 定时采集生成不可变快照；
- 可以按主要业务维度查询效果；
- 采集失败不影响发布业务；
- 可以形成最小再生产信号。

### M10：打包、升级、诊断与稳定性验收

| 字段 | 内容 |
|---|---|
| 状态 | `NOT_STARTED` |
| 目标 | 将开发环境可运行升级为运营人员可安装、可升级、可诊断、可恢复。 |
| 依赖 | M9 `DONE` |
| Active CHG | None |
| Evidence | None，未进入里程碑验证。 |
| 完成日期 | None |
| Commit/Tag | None |

候选 CHG：

```text
M10-C1 Agent 正式打包和受控依赖
M10-C2 FFmpeg 分发、校验和许可证
M10-C3 Desktop 三平台安装包
M10-C4 版本兼容和更新机制
M10-C5 日志脱敏和诊断包
M10-C6 中断恢复、安全和故障演练
M10-C7 全系统发布验收
```

退出条件：

- 用户不需要安装系统 Python；
- 不依赖系统 FFmpeg；
- 三种桌面目标可以构建；
- 不兼容版本禁止执行敏感任务；
- 普通日志不存在敏感信息；
- 可以导出诊断信息；
- 关键中断恢复场景通过；
- `release-matrix.yaml` 存在正式可用版本组合；
- 全系统最终验收通过。

## 4. CHG 粒度

一个里程碑不是一个巨大 CHG。每个 CHG 应满足：

- 单一明确目标；
- 可单独审查；
- 有自动测试或人工验证；
- 能独立提交；
- 不包含未确认的产品或架构分叉；
- 发现范围扩大时立即拆分。

一次只允许一个 Active CHG。普通 S 级变更可以走 Issue/Commit/测试；M/L 级必须有 `delivery/active/<CHG>/change.md`。

## 5. Codex 执行协议

执行、恢复、审查或完成 CHG 时，必须使用 `executing-wt-media-change` Skill。

会话启动建议：

```bash
cd wt-media
python3 wt-media-workspace/scripts/prepare_ai_workspace.py --change CHG-YYYYMMDD-NNN
codex
```

Codex 每次必须按顺序读取：

1. 根 `AGENTS.md`；
2. 根 `.ai/CURRENT_CONTEXT.md`；
3. 当前 `delivery/active/<CHG>/change.md`；
4. CHG 引用的产品、工程、协议和决策基线；
5. 受影响仓库各自的 `AGENTS.md`；
6. 各仓库 `git status`、当前分支和相关测试。

编码前必须输出：

```text
当前事实
与本 CHG 的差距
真实文件映射
有序 Task 清单
每个 Task 的测试与验收方式
风险和阻塞
建议 Commit 边界
```

每个 Task 必须遵循：

```text
失败验证或测试
→ 最小实现
→ 测试
→ Diff 检查
→ Evidence
→ Checkpoint
→ 独立 Commit
```

必须暂停并写入 `Q-xx` 的情况：

- 需要改变“明确不做”；
- 需要新增核心对象、状态或 Contract；
- 需要改变事实来源；
- 需要跨越 Cloud、Agent、Desktop 既定职责；
- 需要引入新的基础设施；
- 需求和现有代码无法兼容；
- 测试只能通过修改验收标准通过。

## 6. DONE 门禁

一个 CHG 只有满足以下条件才能标记为 `DONE`：

- 范围内实现完成；
- 自动测试通过；
- 必要人工验证完成；
- 验收矩阵全部关闭；
- Contract 归属和兼容关系一致；
- Git Diff 无越界修改；
- 旧路径、旧状态和旧方案残留扫描完成；
- 必要产品、工程、协议和决策基线已回写；
- 受影响仓库独立 Commit；
- `delivery/active` 和 `delivery/LEDGER.md` 不保留已完成 CHG 作为长期归档。

## 7. 下一步选择规则

执行控制体系完成后，不直接锁定 Cloud 用户与账号模块。下一项 CHG 必须根据 `MASTER_IMPLEMENTATION_PLAN.md` 和当前真实代码状态判断。

通常推荐顺序：

```text
三仓库最小工程骨架
→ Cloud-Agent Contract 与版本
→ Agent 注册、心跳、任务领取
→ Desktop 启停 Agent 和状态展示
→ 跨端闭环验收
→ 用户与账号/Profile
```

若工程骨架或最小跨端任务闭环未真实完成并通过验收，不得跳到用户与账号模块。
