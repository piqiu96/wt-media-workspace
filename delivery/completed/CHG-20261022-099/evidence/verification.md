# CHG-20261022-099 验证记录

- 日期：2026-10-22
- 分支：`chg/CHG-20261022-099`（T-09 从 `codex/CHG-20261022-099` 本地改名；未推送）
- 环境：macOS arm64；Workspace 工作树；三个运行仓同级的 `wt-media/` 根
- 实现提交：`e4347c9`（原治理实现）、`3112d22`（CHG 分支命名）、`d2d826d`（稳定版发布分支）、`735dafe`（文档链接与替代指针检查）、`12017ad`（文档事实治理规范与入口收敛）；本记录单独提交

## 1. 单元测试与门禁

| 判据 | 命令 | 读数 |
|---|---|---|
| 全量单测 | `uv run --with pyyaml==6.0.3 --no-project python -B -X pycache_prefix=/tmp/wtmedia-pycache -m unittest discover -s tests -q` | `Ran 174 tests` → `OK`（T-08 基线 158，T-09–T-11 +10，T-12 +6；最后一次文档改动后重跑） |
| 定向单测 | 同解释器 `-m unittest tests.test_wt_cli tests.test_submit_tag tests.test_tag_transport -q` | `Ran 37 tests` → `OK` |
| 文档检查单测 | 同解释器 `-m unittest tests.test_docs_check -q` | `Ran 19 tests` → `OK` |
| 契约与配置 | `python3 scripts/verify/verify_m0_config.py` | exit 0；`Workspace config verification ok` |
| 交付治理 | `python3 scripts/verify/verify_delivery_governance.py` | exit 0；Active CHGs: `CHG-20261015-098`, `CHG-20261022-099` |
| AI 入口 | `python3 scripts/verify/verify_ai_workspace.py` | exit 0；快照在 8000 字符预算内，0 warnings |
| Skill 源 | `python3 scripts/verify/verify_skills.py` | exit 0；`verified 10 skill source files` |
| 状态词与主计划 | `python3 scripts/verify/verify_product_master_alignment.py` | exit 0 |
| M2 静态矩阵 | `python3 scripts/verify/verify_m2_acceptance.py` | exit 0 |
| 文档治理 | `python3 scripts/docs/check.py` | exit 0；`docs governance ok (16 indexes)`；扫描 91 篇当前文档，0 断链 |
| `control.sh` 判别式 | `bash scripts/verify/verify-control.sh` | PASS；usage 逐字、status 六行（cloud/agent/worker/compose-worker/web-dev/desktop-dev）、无端口字面量 |
| Skill 分发 | `python3 scripts/sync_skills.py check` | `sync` 后 exit 0；`skill outputs are up to date` |

## 2. CLI 与上下文演练

| 判据 | 读数 |
|---|---|
| `python3 scripts/wt.py status` | 选中 `CHG-20261022-099`；两个 Active CHG；四仓 branch/status 输出 |
| `chg start CHG-20261015-098 --plan` | 三个 legacy WARN；`PLAN ONLY`；未切分支；推荐 `fast, integration` |
| `chg start CHG-20261022-099 --plan` | 脏树 WARN；`PLAN ONLY`；推荐 `repo` |
| `chg verify CHG-20261022-099 --plan` | 单测、五个治理门禁、`docs/check.py`、`verify-control.sh` |
| `chg resume` 连续两次 | `.ai/CURRENT_CONTEXT.md` 两次 `shasum` 一致 |
| 快照字段 | 含 `Current CHG`、`Current Branch`、`CHG Location`、`Affected Repositories`、`Required References`、`Repository Status`、`Recommended Verification`；无独立 `Status:` 行 |
| `.ai/WORK_STATE.md` | `git check-ignore` 命中 `.gitignore:3`；`git status` 不显示；`resume` 能读出自定义标记；测试后删除 |
| `wt dev/test --plan` | `fast`/`repo`/`integration`/`e2e`/`real` 均映射到现有入口；`dev repo` 只接受三个运行仓 |

## 3. 入口与路径

| 判据 | 读数 |
|---|---|
| 纯转发脚本 | `test ! -e scripts/m2b-local-acceptance.sh` 通过 |
| `bin/control.sh help/status` | usage 不变；status 六行；可用 `WT_MEDIA_M2B_PYTHON_BIN` 指定解释器 |
| 任意 cwd 直接执行 | `cd /tmp && python3 <workspace>/scripts/dev/local_env.py --help` 与 `scripts/docs/check.py` 均成功 |
| `verify_m0_local.sh` | `bash -n` 通过；路径改为 `scripts/verify/…` 并纳入 `docs/check.py`；未整跑（需三仓构建与 MySQL 环境） |
| 旧路径清扫（活文件） | 0 命中。分母：已暂存的 `git grep` 全树，排除 `delivery/completed/`、`docs/superpowers/`、`delivery/reports/`、`delivery/active/CHG-20261015-098/`、`delivery/planned/CHG-20260923-054/` 与 `scripts/README.md` 的旧→新映射表 |
| 阳性对照 | 同一模式在历史叙述中命中 25 个文件，证明清扫不是空转 |
| 新路径接通 | 39 个不同引用；5 个非 Workspace 目标（Cloud 工作目录的 `build-release-linux.sh`/`package_release_linux.py`/`smoke_frozen_sidecar.py`，以及测试夹具文本中的 `test-control.sh`/`writer.py`），其余 34 个 Workspace 目标全部存在 |

## 4. 文档治理正反例

`tests/test_docs_check.py`（19 项）覆盖：合规树为绿；缺索引、缺标记、`historical` 配 `task`、未登记顶层目录、登记目录缺 README、`AGENT-INDEX` 缺路径、历史目录未被默认排除、断链、specs 未登记、`delivery/completed` 缺 READ-ONLY 各为红；`#anchor`、目录链接、`https://` 与代码块内断链不误报。新增 6 项：`index/never` 为绿；非索引当前文档断链为红；`SUPERSEDED` 无替代为红、有可解析替代为绿；历史目录与 `docs/decisions` 的 `SUPERSEDED` 不误报。

`tests/test_scripts_index.py`（3 项）覆盖：每个脚本已登记；从 README 删除 `scripts/docs/check.py` 后能被检出；必需条目存在。

## 5. 分支与发布收口（T-09–T-11）

| 判据 | 读数 |
|---|---|
| CHG 分支改名 | `git branch --show-current` = `chg/CHG-20261022-099`；`git branch --list 'codex/*'` 无输出；无 upstream，未推送 |
| 旧前缀清扫 | 活引用 0 命中；本记录保留 2 处改名叙述（checkpoint 与本节分支行），不计为活引用；阳性对照 `codex/m4-a-` 排除本记录后命中 6 个历史文件（全树 7，含本行自引用），证明模式可命中 |
| 远端 ref | `git ls-remote --heads origin` 仅 `refs/heads/main`，没有新增分支或 Tag |
| 发布分支单测 | `tests.test_submit_tag` 覆盖：稳定版创建 `release/<tag>` 且与 Tag 同 commit；非 `main` 拒绝；本地/远端分支指向其他 commit 拒绝；同 commit 幂等复用；分支推送失败走 GitHub API 兜底；RC 不建发布分支；dry-run 不建 ref |
| 发布分支 API 兜底 | `tests.test_tag_transport` 覆盖 `create_branch_by_api` 的 ref/SHA payload、响应不一致与非法仓库/分支/SHA |
| GitHub Compare（v0.1.1 → v0.1.2） | Workspace `48 files / 13 commits`；Cloud `29 / 9`；Agent `24 / 3`；Desktop `9 / 4`。四个 `gh api repos/piqiu96/<repo>/compare/<from>...<to>` 均 exit 0 |
| 真实发布 | 未执行真实 `--push`，未创建发布分支或产品 Tag，未触发 `release.yml` |

## 6. 未执行与已知阻塞

| 项 | 状态 | 原因 |
|---|---|---|
| `verify_m1_integration.py` | 未运行 | 结构性阻塞：① `start_cloud` 设 `WT_MEDIA_CLOUD_HTTP_ADDR`，Cloud 只读 `WT_MEDIA_CLOUD_CONFIG_PATH`/`WT_MEDIA_CLOUD_HOME`（`internal/config/root.go:13-17`），实际监听 `config/app.toml` 的 `8188`；② 断言契约 `2026.07.14.4`，运行时常量为 `2026.10.01.1`；③ 跑 `npm run verify`，Desktop 无 `package.json`。修它须同时裁定契约语义，超出本 CHG |
| 契约版本冲突 | 未裁定 | `compatibility.go`=`2026.10.01.1`、`compatibility.openapi.yaml`=`2026.07.14.6`、`runtime-binding.openapi.yaml`=`2026.10.01.1`、`file-transfer.openapi.yaml`=`2026.10.13.1`、`config/contract-map.yaml`=`2026.10.13.1` |
| 三个运行仓业务测试套件 | 未重跑 | 本 CHG 未改运行时代码；四仓 `bin/control.sh` 入口契约由 `tests/test_bin_control_entry.py` 覆盖（包含在 158 项内） |
| `e2e` / `real` | 未实跑 | 方案明确不自动启动外部效应；留待真实走查 |
| 真实双执行器并行 | 未演练 | 当前无真实瓶颈；规则、重叠警告与依赖校验已由单测覆盖 |
| 本机已运行服务 | 未停止 | `bin/control.sh status` 显示 cloud/worker/compose-worker/web-dev/desktop-dev 均为本轮之前已存在的开发进程，本轮未启动、未停止 |

## 7. 与 Done When 的对应

- 最小元数据与 `Change`/`Done When`：模板与 `scripts/lib/change_metadata.py`；旧格式兼容由 `tests/test_change_metadata.py` 覆盖。
- 多 Active CHG：`verify_delivery_governance.py` 与 `tests/test_wt_cli.py` 覆盖选择、依赖与重叠警告。
- `CURRENT_CONTEXT` 可再生、非第二状态事实：生成器、忽略规则、两次 `resume` 一致与无 `Status:` 均已实测。
- 新 CHG 分支为 `chg/<CHG-ID>`：`scripts/chg/start.py` 与 `tests/test_wt_cli.py` 覆盖，分支已本地改名。
- 稳定版发布分支：`submit_tag.py` 预检 `main`、先建/推 `release/<产品Tag>` 再推 Tag；RC 不建分支；单测覆盖幂等、冲突与 API 兜底。
- 发布前 Review：`scripts/release/README.md` 固定四个 GitHub Compare 页面；`v0.1.1 → v0.1.2` 四个端点实测可解析。
- 文档生命周期：`docs/` 只保留当前事实，目录位置表达生命周期，不新增长期状态字段；`SUPERSEDED` 只作临时迁移标记。
- 冲突裁定：按事实归属确定 SSOT，不设产品/工程/实现全局顺序；用户裁定回写正式事实源。
- 文档机检：当前文档相对链接、`SUPERSEDED` 替代指针、索引标记和 specs 索引均由 `scripts/docs/check.py` 检查；历史目录不追改。
- 历史目录：`docs/superpowers/` 改为 `index/never` 并按内容判断；`delivery/completed/`、`delivery/reports/` 职责收敛；不新增 `archive/`。
- 既有入口未破坏：全量单测 174 项、六个门禁、`verify-control.sh` 与四仓入口测试覆盖。

## 8. 文档与知识事实治理（T-12）

### 8.1 实现与范围

| 项 | 结果 |
|---|---|
| 权威规范 | 新增 `docs/standards/文档与知识事实治理规范.md`，覆盖分类、事实归属、冲突裁定、生命周期、历史处置、关闭检查、默认加载、治理节奏与质量判据 |
| 目录职责 | `docs/` 当前事实；`delivery/active/` 当前 CHG；`delivery/planned/` 未启动；`delivery/milestones/` 当前闭环；`delivery/completed/` 有追溯价值的完成记录；`delivery/reports/` 有独立价值的报告；不新增 `archive/` |
| 状态模型 | 不新增 Draft / Current / Superseded / Historical 状态字段；目录位置表达生命周期；`SUPERSEDED` 仅临时迁移标记且必须指向替代文档 |
| 冲突裁定 | 先确定事实所属领域与 SSOT，再按“当前正式事实 > 上层摘要 > CHG 临时描述 > 历史/AI 临时内容”裁定；跨领域冲突不由 AI 合成第三种解释 |
| 机检 | `docs/check.py` 扩展当前文档断链、`SUPERSEDED` 替代指针、`index/never`；保留原索引、标记、目录注册、`AGENT-INDEX` 路径和 specs 检查 |
| 未做 | 未迁移或合并 `docs/superpowers/`、`delivery/reports/`、`delivery/completed/`；未删除任何现有文档；未新增 CHG、检查脚本或 workflow；未推送、未建 PR、未打 Tag |

### 8.2 链接与 `SUPERSEDED` 读数

| 判据 | 命令 | 读数 |
|---|---|---|
| 当前文档链接 | `python3 scripts/docs/check.py` | exit 0；扫描 91 篇当前文档，0 断链 |
| 断链阳性对照 | 临时在 `docs/product/` 放一篇指向不存在文件的文档后运行检查器 | `ERROR broken relative link: docs/product/__link_probe__.md -> __missing_probe__.md`；exit 1 |
| `SUPERSEDED` 阳性对照 | 同一轮放一篇无替代链接的 `SUPERSEDED` 文档 | `ERROR SUPERSEDED document must name a replacement: docs/product/__superseded_probe__.md`；exit 1 |
| 清理后复验 | 删除两篇探针后运行检查器 | `docs governance ok (16 indexes)`；exit 0 |
| `SUPERSEDED` 当前分布 | 当前文档扫描 | 仅 `docs/product/prd/详细文档/第四章_内容发现.md` 文首带标记，替代链接可解析；`docs/decisions` 按 ADR 约定豁免 |
| 旧路径清扫 | `git grep -E 'engineering-evolution-standard|web-desktop-visual-system'` 限定当前文档 | 93 个跟踪文件 0 命中（exit 1） |
| 旧路径阳性对照 | 同一模式扫全树 | 13 个历史文件命中（exit 0），证明模式不是空转 |

### 8.3 结构与环境

| 判据 | 读数 |
|---|---|
| 目录未迁移 | `git diff --name-status b59b889..HEAD`：M 18 / A 1 / D 0 / R 0；新增仅为治理规范 |
| 归档只读 | `verify_delivery_governance.py`：扫描 34 个脚本，0 个写操作到达 `delivery/completed/` |
| 远端 ref | `git ls-remote --heads origin` 仅 `refs/heads/main`；未推送分支或 Tag |
| 快照 | `python3 scripts/wt.py chg resume CHG-20261022-099` exit 0；`Current Branch: chg/CHG-20261022-099`；快照在 8000 字符预算内 |

### 8.4 本轮登记、不处置

- `docs/superpowers/` 30 篇旧计划/设计（另 README）的逐项内容处置（删除 / 提升为当前方法 / 移入 completed 或 reports）。
- `docs/engineering/specs/2026-09-23-launch-engineering-optimization-program.md` 是否移出 specs；本轮仅在索引中标注“已结束，非当前设计”。
- `delivery/reports/` 11 篇报告的“结论已回写、无长期价值则删除”审计。
- 第四章等 `SUPERSEDED` 文档在引用迁移后的最终删除。
- 固定 20 篇 / 20k 字默认阅读上限已在 T-13 取消；仅保留 `.ai/CURRENT_CONTEXT.md` 的 8000 字符工具预算。

## 9. 治理规范收敛（T-13）

### 9.1 规则变化

| 项 | 结果 |
|---|---|
| 结构 | 规范收敛为 9 节：核心原则、文档与事实归属、当前事实与历史退场、冲突裁定、AI 默认加载与 Plan 规则、CHG / Milestone 收口、AI 对话与代码注释、自动检查、质量判据 |
| 事实边界 | 明确“Git / PR 保存历史与变更证据，不是当前事实的 Owner”；当前事实由各自正式 SSOT 保存，代码只证明当前实现 |
| 文档粒度 | 一份文档负责一个边界清晰、Owner 单一的主题；拆文件由可维护性决定，不按需求或问题数量机械拆分 |
| CHG 文件 | `change.md` 必需；`evidence/` 按风险；`plan.md`、`checkpoint.md`、`.ai/WORK_STATE.md` 均可选；证据按 L / M / H 分级 |
| 历史处置 | 默认退场；KEEP / MERGE / MOVE / DELETE / SUPERSEDE / REVIEW 六选一；`docs/superpowers/` 不作为自动归档，也不整体迁移 |
| 治理节奏 | 事件驱动：CHG Close、Milestone Done 强制；CI / docs check 自动；Fact Drift、大 Milestone、大版本、文档显著增长时人工专项；月度检查仅推荐 |
| 阅读预算 | 删除固定篇数与字数门槛，改为渐进式加载；8000 字符仅是 `.ai/CURRENT_CONTEXT.md` 的工具配置 |
| AI Plan | 限定默认决策来源，禁止把 completed / reports / 历史 Milestone / `SUPERSEDED` / 旧 AI 材料作为当前需求依据；规定五段式 Plan 输出与四类事实区分 |
| 代码注释 | 项目维护的注释默认中文；只保留非显然的 Why、业务 / 安全约束、并发与副作用风险、兼容性条件和易误改边界；删除代码复述、变更史、过程叙述、AI 痕迹与失效 TODO |
| 去重 | `代码演进评估规范` §4 的注释规则改为指向本规范 §7，避免同一事实两处定义 |

### 9.2 冲突同步与验证

| 判据 | 读数 |
|---|---|
| `verify_delivery_governance.py` | 删除 Active CHG 必须存在 `checkpoint.md` 的硬检查；`test_active_change_without_checkpoint_is_valid` 覆盖缺失仍有效 |
| 入口文档 | `AGENT-INDEX.md`、`docs/README.md`、`docs/engineering/README.md`、`docs/engineering/specs/README.md`、`delivery/MASTER_IMPLEMENTATION_PLAN.md`、根 `README.md` 同步可选 checkpoint 与 `WORK_STATE` 边界 |
| Skill | `executing-wt-media-change` 的 checkpoint 段改为可选；`sync_skills.py check` 输出 `skill outputs are up to date` |
| `scripts/wt.py` | verify 完成提醒改为对照 evidence 与验收记录，checkpoint 仅在存在时读取，不再暗示必需 |
| Workspace 全量单测 | `Ran 174 tests — OK`（最后一次改动后重跑） |
| 定向单测 | `Ran 47 tests — OK`（`test_docs_check` + `test_verify_delivery_governance` + `test_wt_cli`） |
| `scripts/docs/check.py` | `docs governance ok (16 indexes)`，exit 0 |
| 治理门禁 | `verify_m0_config`、`verify_delivery_governance`、`verify_ai_workspace`（660 字符）、`verify_skills`（10 个源）、`verify_product_master_alignment` 均 exit 0；`verify-control.sh` PASS |
| 未执行 | 本轮未重跑 `verify_m2_acceptance.py` 与三个运行仓业务套件；未改运行时代码 |
| 提交 | 工具改动 `88a8a5c`；规范、入口文档与 CHG 记录随 T-13 文档提交；未推送、未建 PR、未打 Tag |
