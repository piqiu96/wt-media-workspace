# M4-M5 Cloud 内容生产文档收敛 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 M4-M5 的产品、工程、交付与视觉参考统一为 Cloud Scheduler + Worker + FFmpeg 内容生产方案，并生成可执行的 M4/M5 Milestone 与 planned CHG-061。

**Architecture:** Cloud MySQL 保存 `material`、`material_usage`、`compose_strategy`、`compose_task`、`composite_output` 与 `file_transfer_task` 正式事实；独立 Scheduler 只创建 pending 任务，Worker 通过数据库原子领取执行 FFmpeg。Desktop / Local Agent 不合成视频，只处理浏览器自动化、发布互动和运营电脑上的文件落地。

**Tech Stack:** Markdown、Go/Hertz 模块化单体约束、MySQL 任务租约、FFmpeg、对象存储、Vue 3/TDesign 信息架构。

**Spec:** `docs/superpowers/specs/2026-09-24-m4-m5-cloud-content-production-design.md`

## Global Constraints

- 不修改当前 active CHG-057、`delivery/LEDGER.md` 或 `.ai/CURRENT_CONTEXT.md`。
- 保留 Workspace 已有未提交改动，不覆盖无关文件。
- 不创建 `production_rule`、`compose_pool_item` 或 `material_usage` 替代表。
- 不引入 MQ、微服务、动态插件或工作流引擎。
- Cloud HTTP Server 不启动 Scheduler 或 Worker；生产进程由独立入口和 bootstrap 装配。
- 六张 PNG 只作为 Cloud 仓库 UI 参考资产，Workspace 仍是产品与工程事实源。

## Review Focus

- “下载原视频”与“合成前准备源文件”必须共用 `file_transfer_task`，但执行位置和用途可区分。
- `compose_task` 必须同时承担生产业务状态与 Worker 领取恢复，不得再套一层通用 Agent task。
- `compose_strategy.schedule` 必须是 M5 自动生产规则的唯一归属，M4 仍允许人工使用策略。
- `composite_output` 只能在输出文件校验和对象存储落盘后创建，失败不得出现假成片。
- Agent 移除 FFmpeg 后，发布/互动/本机文件能力仍保持，不得误删 Agent 整体执行边界。

---

### Task 1: 保存并索引六张 UI 参考图

**Files:**
- Create: `../wt-media-cloud/docs/product/m4-m5-content-production/README.md`
- Create: `../wt-media-cloud/docs/product/m4-m5-content-production/assets/01-material-library.png`
- Create: `../wt-media-cloud/docs/product/m4-m5-content-production/assets/02-my-materials.png`
- Create: `../wt-media-cloud/docs/product/m4-m5-content-production/assets/03-compose-strategies.png`
- Create: `../wt-media-cloud/docs/product/m4-m5-content-production/assets/04-compose-tasks.png`
- Create: `../wt-media-cloud/docs/product/m4-m5-content-production/assets/05-my-outputs.png`
- Create: `../wt-media-cloud/docs/product/m4-m5-content-production/assets/06-download-center.png`

**Interfaces:**
- Consumes: 用户提供的六张 PNG。
- Produces: 产品与工程文档可引用的稳定视觉资产路径。

- [ ] **Step 1: 记录资源目录尚不存在的失败基线**

Run: `test -d ../wt-media-cloud/docs/product/m4-m5-content-production`

Expected: FAIL，目录尚不存在。

- [ ] **Step 2: 创建目录并复制图片为稳定文件名**

按图片顺序复制，保持 PNG 原始字节不变。

- [ ] **Step 3: 创建 README 索引**

README 必须说明“仅为视觉参考，不是产品事实源”，并按六个页面嵌入图片。

- [ ] **Step 4: 校验图片**

Run: `file docs/product/m4-m5-content-production/assets/*.png && shasum -a 256 docs/product/m4-m5-content-production/assets/*.png`

Expected: 6 个 PNG 均可识别，Hash 与原图逐一一致。

### Task 2: 建立 Decision 与专项工程设计

**Files:**
- Create: `docs/decisions/0017-m4-m5-cloud-owned-content-production.md`
- Create: `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md`
- Modify: `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md`
- Modify: `docs/engineering/architecture/社媒运营平台模块分界分层和通信规约.md`

**Interfaces:**
- Consumes: Spec §2.3、§5。
- Produces: Product、Milestone 和 CHG 可引用的正式架构边界。

- [ ] **Step 1: 运行旧边界扫描**

Run: `rg -n '本地 FFmpeg|云端 FFmpeg|Cloud Agent.*生产|本地合成|Agent 负责.*合成' docs/engineering/architecture`

Expected: 命中现有 Agent 合成边界。

- [ ] **Step 2: 新增 ADR-0017**

必须写明 Cloud-owned 合成、Agent 保留边界、被取代文档、代价和后续 Contract。

- [ ] **Step 3: 新增专项工程设计**

必须覆盖进程、模块、状态机、原子领取、租约、heartbeat、超时、重试、并发、FFmpeg、对象存储、文件传输和验证。

- [ ] **Step 4: 增量更新两份架构基线**

使用“2026-09-24 M4-M5 调整”标记；删除有效正文中的 Agent 合成职责，保留发布、互动和本机文件能力。

- [ ] **Step 5: 校验工程边界**

Run: `rg -n 'ADR-0017|compose_strategy|compose_task|file_transfer_task|Compose Worker' docs/engineering docs/decisions/0017-m4-m5-cloud-owned-content-production.md`

Expected: 新边界在 Decision、专项设计和两份架构基线中均可定位。

### Task 3: 更新第五章产品需求

**Files:**
- Modify: `docs/product/prd/详细文档/第五章_素材生产.md`
- Modify: `docs/product/prd/社媒运营平台_产品需求说明书_V1.md`

**Interfaces:**
- Consumes: ADR-0017、工程专项设计、六页信息架构。
- Produces: M4/M5 Milestone 的稳定产品事实。

- [ ] **Step 1: 记录旧对象命中数**

Run: `rg -n 'production_rule|compose_pool_item|composite_output_pool|composite_output_claim|本地 Agent.*合成|云端 Agent' docs/product/prd/详细文档/第五章_素材生产.md`

Expected: 命中旧方案。

- [ ] **Step 2: 按原章节结构更新详细第五章**

保留 5.1～5.10；将章节内容调整为素材库、我的素材、合成策略、合成任务、我的成片、下载中心及 M4/M5 验收。

- [ ] **Step 3: 同步总 PRD 第五章摘要**

摘要必须与详细章使用相同对象、状态和执行边界。

- [ ] **Step 4: 校验禁止对象**

Run: `rg -n 'production_rule|compose_pool_item|composite_output_pool|composite_output_claim|本地 Agent.*合成|云端 Agent.*合成' docs/product/prd/详细文档/第五章_素材生产.md docs/product/prd/社媒运营平台_产品需求说明书_V1.md`

Expected: 只允许出现在“旧方案已废弃/禁止新增”的变更说明中，不得作为有效流程。

### Task 4: 更新 Master Plan 并建立 M4/M5 Milestone

**Files:**
- Modify: `delivery/MASTER_IMPLEMENTATION_PLAN.md`
- Create: `delivery/milestones/M4-content-production.md`
- Create: `delivery/milestones/M5-automatic-production.md`
- Modify: `delivery/milestones/README.md`

**Interfaces:**
- Consumes: Product 第五章与 ADR-0017。
- Produces: CHG-061 的精确闭环锚点与后续 CHG 顺序。

- [ ] **Step 1: 记录旧 M4/M5 目标**

Run: `sed -n '408,530p' delivery/MASTER_IMPLEMENTATION_PLAN.md`

Expected: 显示本地 Agent M4、Cloud Agent M5 和旧对象链路。

- [ ] **Step 2: 重写 M4/M5 路线和候选 CHG**

M4 聚焦人工闭环；M5 聚焦策略自动调度与资源控制；同步 M10 中 FFmpeg 交付位置。

- [ ] **Step 3: 创建两份闭环 Milestone**

每份包含用户目标、前置、操作顺序、系统动作、成功事实、禁止假成功、CHG 顺序和验收矩阵。

- [ ] **Step 4: 更新 Milestone 索引**

标记 M4/M5 均为 DRAFT / NOT_STARTED，不影响 M3 DONE 与当前工程优化 Milestone。

- [ ] **Step 5: 校验闭环引用**

Run: `rg -n 'M4-content-production|M5-automatic-production|ADR-0017|CHG-20260924-061' delivery/MASTER_IMPLEMENTATION_PLAN.md delivery/milestones`

Expected: Master、两个 Milestone 和索引之间引用完整。

### Task 5: 生成 planned CHG-061

**Files:**
- Create: `delivery/planned/CHG-20260924-061/change.md`
- Modify: `delivery/planned/README.md`

**Interfaces:**
- Consumes: `delivery/milestones/M4-content-production.md` 的首个闭环锚点。
- Produces: 当前 CHG-057 完成后可被激活的首个 M4 纵向实施单元。

- [ ] **Step 1: 确认编号未占用**

Run: `find delivery -maxdepth 2 -type d -name 'CHG-20260924-061'`

Expected: 无输出。

- [ ] **Step 2: 创建 CHG-061**

目标限定为“素材库 → 我的素材 → 懒加载原素材准备/下载”的首个独立闭环；包含明确排除项、任务、验收和证据要求。

- [ ] **Step 3: 更新 planned 索引**

不得把 CHG-061 写入 `delivery/LEDGER.md` 或激活。

- [ ] **Step 4: 校验状态与锚点**

Run: `rg -n 'Status: PLANNED|M4-content-production.md#|CHG-20260924-061' delivery/planned/CHG-20260924-061/change.md delivery/planned/README.md`

Expected: planned 状态和精确 Milestone 锚点均存在。

### Task 6: 全量一致性与治理验证

**Files:**
- Modify: only files listed in Tasks 1-5 if verification exposes contradictions.

**Interfaces:**
- Consumes: Tasks 1-5 全部产出。
- Produces: 可交付的文档一致性证据。

- [ ] **Step 1: 扫描旧有效方案残留**

Run: `rg -n 'production_rule|compose_pool_item|Cloud Agent.*合成|Local Agent.*合成|本地合成' delivery/MASTER_IMPLEMENTATION_PLAN.md delivery/milestones/M4-content-production.md delivery/milestones/M5-automatic-production.md docs/product/prd/详细文档/第五章_素材生产.md docs/product/prd/社媒运营平台_产品需求说明书_V1.md docs/engineering/architecture docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md docs/decisions/0017-m4-m5-cloud-owned-content-production.md`

Expected: 仅保留带有“旧方案/废弃/禁止”的迁移说明；不存在有效流程残留。

- [ ] **Step 2: 运行文档与治理校验**

Run: `python3 scripts/verify_agent_entry.py`

Expected: exit 0；已有不相关 WARN 如存在则记录，不冒充本次新增失败。

- [ ] **Step 3: 检查 Markdown 链接、图片数量和目标 Diff**

Run: `test "$(find ../wt-media-cloud/docs/product/m4-m5-content-production/assets -type f -name '*.png' | wc -l | tr -d ' ')" = 6 && git diff --check && git -C ../wt-media-cloud diff --check`

Expected: exit 0。

- [ ] **Step 4: 审查范围**

Run: `git status --short && git -C ../wt-media-cloud status --short`

Expected: 只新增/修改计划列出的文件以及用户原有未提交文件；不得覆盖后者。

