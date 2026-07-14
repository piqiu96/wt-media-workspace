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
工程骨架
→ 最小跨端任务闭环
→ 用户、账号与运行环境
→ 内容发现与素材
→ 本地合成
→ 云端生产与成片池
→ B站辅助发布
→ 百家号辅助发布
→ 互动
→ 数据统计
→ 打包、更新与稳定性收口
```

每个阶段都必须产生可以运行、可以测试、可以演示的闭环。M1 最小跨端任务闭环完成前，不进入大规模业务模块开发。

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

### M0：工程工作区与质量门禁

目标：让四个仓库具备可重复构建、测试和 AI 执行的基本条件。

范围：

- 四仓库目录和规则文件；
- Workspace Skills 唯一源码、同步和校验；
- 根 `.ai/CURRENT_CONTEXT.md` 生成；
- Cloud、Agent、Desktop 最小启动入口；
- 基础日志、配置、错误结构；
- 测试命令和 CI；
- Contract 目录、版本文件和锁定机制。

验收：

- 三个运行仓库能独立构建和测试；
- 从最外层 `wt-media/` 启动 Codex 能识别四仓库边界；
- 运行仓库不依赖 Workspace 才能启动。

### M1：最小跨端任务闭环

目标：先证明 Cloud、Agent、Desktop 三端主链路可运行。

最小演示：

```text
Cloud 创建 noop_task
→ Agent 注册节点并领取任务
→ Agent 上报 started / progress / succeeded
→ Cloud 保存任务状态
→ Desktop 启动 Agent
→ Desktop 通过 Rust 代理读取 Agent 状态和 SSE
→ 页面展示任务进度
```

M1 拆分建议：

```text
三仓库最小工程骨架
→ Cloud-Agent Contract 与版本
→ Agent 注册、心跳、任务领取
→ Agent noop Executor 与结果回传
→ Local Agent HTTP + SSE
→ Desktop 启停 Agent 和状态展示
→ 三端跨端集成验证
```

验收：

- 同一任务不会被两个 Agent 同时执行；
- Agent 中断后任务可以超时释放或恢复；
- Agent 无法连接 Cloud 时，结果进入本地待回传；
- Desktop 不直接访问 Agent SQLite；
- Desktop Vue 不直接持有 Local Token；
- 三端分别有自动测试；
- 完成一次真实跨端演示。

### M2：用户、角色、媒体账号与运行环境

目标：建立后续发布、互动和任务分配依赖的账号基础。

关键约束：

- 单用户只允许一个活跃系统会话；
- `owner_user_id` 必须硬校验；
- 同一 Profile 不允许并发执行敏感任务；
- Cloud 保存正式账号事实；
- Agent 只上报 Profile 和运行环境事实；
- Desktop 不复制账号业务规则。

进入条件：M1 技术主干真实完成并通过验收。

### M3：内容发现与素材入库

目标：打通关键词、链接、作者监控到素材入库的首条业务数据闭环。

首版不做 B站、小红书、百度搜索和 Excel 导入。

### M4：本地视频合成闭环

目标：打通 `material → task → Agent + FFmpeg → composite_output`。

关键约束：正式运行不依赖系统 Python，不依赖系统 PATH 中的 FFmpeg。

### M5：云端自动生产与云端成片池

目标：复用 M4 合成核心，支持 Cloud Agent 生产、对象存储、成片池、领取和下载。

### M6：B站辅助发布闭环

目标：打通 `composite_output → publication → Agent 辅助填写 → waiting_manual_submit → 人工最终提交`。

关键约束：Agent 不点击最终发布按钮，同一 Profile 一次只执行一个敏感任务。

### M7：百家号辅助发布

目标：验证平台 Adapter 边界，复用 publication、task、队列和人工提交逻辑。

### M8：互动管理闭环

目标：完成点赞、收藏、评论，不建设关注、转发、私信和主动搜索互动作品。

### M9：效果采集与数据统计

目标：发布和互动结果形成可追踪数据闭环。Analytics 只读正式业务事实。

### M10：交付、更新、诊断与稳定性收口

目标：让“开发环境能运行”升级为“运营人员可安装和长期使用”。

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

