# WT Media Workspace 治理规范

## 一、定位与职责

本仓库是 WT Media 多项目系统的研发控制中心（Engineering Control Plane）。

负责管理：
- 产品需求
- 工程架构
- 跨仓库协议
- 技术决策
- 交付生命周期
- AI 开发协作规范

本仓库不是运行时代码仓库。

禁止存放：
- 业务代码
- 服务运行代码
- 构建产物
- 临时文件

运行时代码位于：
- ../wt-media-cloud
- ../wt-media-agent
- ../wt-media-desktop

------------------------------------------------------------------------

# 二、项目职责边界

## wt-media-cloud

负责：
- 后端服务
- HTTP API
- 业务编排
- 数据存储
- MySQL / Redis
- Scheduler
- Cloud Runtime

不负责：
- 浏览器自动化
- 本地机器操作
- Desktop UI

## wt-media-agent

负责：
- 本地执行能力
- 浏览器自动化
- Agent Runtime
- 系统级操作

不负责：
- Cloud业务逻辑
- 数据业务管理

## wt-media-desktop

负责：
- Desktop应用
- Tauri运行环境
- 用户交互
- 本地桥接能力

不负责：
- Cloud业务逻辑
- Agent内部执行能力

------------------------------------------------------------------------

# 三、Workspace知识管理

## 产品知识

位置：

docs/product

负责：
- 产品需求
- 用户场景
- 功能目标
- 验收标准

## 工程知识

位置：

docs/engineering

负责：
- 系统架构
- 技术规范
- 工程标准
- 开发约束

包含：

docs/engineering/

-   architecture
-   specs

## 跨项目协议

位置：

docs/contracts

负责： - API Contract - Cloud-Agent协议 - Cloud-Desktop协议 - Event
Schema

## 技术决策

位置：

docs/decisions

负责：
- 架构选择
- 技术取舍
- ADR记录

## 交付管理

位置：

delivery

负责：
- Milestone
- 实施状态
- 验证结果
- 完成交付

------------------------------------------------------------------------

# 四、AI知识读取优先级

处理需求时必须按照：

1.  delivery/active

理解：
- 当前目标
- 范围
- 验收标准

2.  docs/product

理解：
- 为什么做

3.  docs/engineering/architecture

理解：
- 系统设计
- 模块边界

4.  docs/contracts
理解：
- 跨项目通信

5.  docs/engineering/specs

理解：
- 实现规范

理解完成后再修改代码。

------------------------------------------------------------------------

# 五、端到端需求规则

涉及多个项目时：

例如：
- Cloud + Agent
- Cloud + Desktop
- Agent + Desktop

执行：

1.  分析影响范围

明确：
- Cloud修改点
- Agent修改点
- Desktop修改点
- Contract变化

2.  确认职责边界

禁止：
- 将Agent能力实现到Cloud
- 将业务逻辑实现到Desktop
- 将UI逻辑实现到Backend

3.  在对应项目执行代码修改

必须遵守：

-   wt-media-cloud/AGENTS.md
-   wt-media-agent/AGENTS.md
-   wt-media-desktop/AGENTS.md

4.  架构、协议变化同步回workspace。

------------------------------------------------------------------------

# 六、Delivery治理

以下情况必须创建：

delivery/active/`<change-id>`{=html}

包括：

-   中大型功能
-   跨项目修改
-   架构调整
-   Contract调整

至少包含：

-   change.md
-   checkpoint.md

小修改可直接执行： - 文档修正 - 小Bug - 不影响行为的重构

------------------------------------------------------------------------

# 七、变更规则

讨论、建议、假设不是正式需求。

只有记录在： - Delivery - Decision

中的确认内容可以驱动代码修改。

禁止实现： Delivery中明确标记为 Explicitly Not Doing 的内容。

结束开发任务前必须更新checkpoint：

记录： - 已完成 - 未完成 - 阻塞 - 下一步

------------------------------------------------------------------------

# 八、Workspace边界

禁止包含：

-   运行时代码
-   业务实现
-   编译文件
-   临时输出
-   自动生成产物

Workspace只保存：

-   知识
-   规范
-   决策
-   交付状态

------------------------------------------------------------------------

# 九、AI执行流程

收到端到端需求：

1.  理解产品目标
2.  查找Delivery
3.  分析影响项目
4.  阅读对应项目AGENTS
5.  在正确项目修改代码
6.  更新Delivery
7.  必要时更新工程文档

------------------------------------------------------------------------

# 十、唯一可信来源

产品：

docs/product

工程：

docs/engineering

协议：

docs/contracts

决策：

docs/decisions

交付：

delivery

其他历史文档不作为新开发依据。

------------------------------------------------------------------------

# 十一、完成检查

-   修改项目归属正确
-   跨项目协议正确
-   未破坏模块边界
-   Delivery已更新
-   Release Matrix已同步（如适用）
-   Skill源文件与生成副本关系正确

------------------------------------------------------------------------

# 十二、Agent 上下文与入口

## 固定入口

Agent 启动时默认读取：

1. `AGENTS.md`
2. `CLAUDE.md`
3. `AGENT-INDEX.md`
4. `.ai/CURRENT_CONTEXT.md`

`CLAUDE.md` 与 `AGENTS.md` 是平级入口，不允许互相软链或互相替代。

## 当前上下文

`.ai/CURRENT_CONTEXT.md` 只保存当前执行状态快照：

- 当前 Milestone
- 当前 CHG
- 当前状态
- 必读文件
- 关键稳定决策

禁止把历史记录、完整决策库或临时验证内容写入该文件。

该文件是**全项目唯一**的执行状态快照，且由脚本生成而非手工维护：

- 生成命令：`python3 scripts/prepare_ai_workspace.py --change <CHG>`
- 禁止手工编辑；禁止在父层执行根再放一份
- `scripts/verify_agent_entry.py` 会在父层重新出现副本时直接判错

Milestone 专属的决策不复制到该文件；由当前 CHG 指明其依赖的 Decision 记录，需要时直接读原文。

## 渐进式加载

1. 第一层：固定入口文件。
2. 第二层：当前 CHG 的 `change.md`、plan、spec、checkpoint。
3. 第三层：进入目标工程后读取其 `AGENT-INDEX.md`、`AGENTS.md`、`CLAUDE.md`，再进入代码。

默认禁止加载：

- `delivery/completed`
- 旧 evidence
- 历史 decisions
- 历史 specs
- 临时实验目录

除非当前任务明确需要。

## 仓库定位

关联工程路径以 `config/repository-map.yaml` 为准，不应在脚本或文档中重复硬编码。

`config/skills-distribution.yaml` 的 targets 与之重复声明同一批 path，两者必须一致；由 `scripts/verify_agent_entry.py` 强制。

## 多 Agent 并行

多工程并行执行时：

- 禁止多个 Agent 同时修改 `.ai/CURRENT_CONTEXT.md`。
- **仅当同一个 CHG 需要多个工程并行实施时**，才在该 CHG 下建立 `delivery/active/<change-id>/status/` 目录，并按 `<repo>.md` 逐仓记录执行状态（当前状态、修改内容、验证结果）；单仓实施的 CHG 不建该目录。
- 最终由 workspace 统一汇总，不引入第二套任务管理系统。

## 入口校验

`scripts/verify_agent_entry.py` 校验入口文件存在性、执行快照唯一性与体积预算、快照与 LEDGER/active 的一致性、配置文件 path 一致、以及各工程入口漂移（启发式 WARN）。本地手工执行；本仓库当前不设 CI。
