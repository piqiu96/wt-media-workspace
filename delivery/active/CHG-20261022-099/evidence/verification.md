# CHG-20261022-099 验证记录

- 日期：2026-10-22
- 分支：`chg/CHG-20261022-099`（T-09 从 `codex/CHG-20261022-099` 本地改名；未推送）
- 环境：macOS arm64；Workspace 工作树；三个运行仓同级的 `wt-media/` 根
- 实现提交：`e4347c9`（原治理实现）、`3112d22`（CHG 分支命名）、`d2d826d`（稳定版发布分支）；本记录单独提交

## 1. 单元测试与门禁

| 判据 | 命令 | 读数 |
|---|---|---|
| 全量单测 | `uv run --with pyyaml==6.0.3 --no-project python -B -X pycache_prefix=/tmp/wtmedia-pycache -m unittest discover -s tests -q` | `Ran 168 tests` → `OK`（T-08 基线 158，新增 10 项；记录变更后重跑） |
| 定向单测 | 同解释器 `-m unittest tests.test_wt_cli tests.test_submit_tag tests.test_tag_transport -q` | `Ran 37 tests` → `OK` |
| 契约与配置 | `python3 scripts/verify/verify_m0_config.py` | exit 0；`Workspace config verification ok` |
| 交付治理 | `python3 scripts/verify/verify_delivery_governance.py` | exit 0；Active CHGs: `CHG-20261015-098`, `CHG-20261022-099` |
| AI 入口 | `python3 scripts/verify/verify_ai_workspace.py` | exit 0；snapshot 701 characters，0 warnings |
| Skill 源 | `python3 scripts/verify/verify_skills.py` | exit 0；`verified 10 skill source files` |
| 状态词与主计划 | `python3 scripts/verify/verify_product_master_alignment.py` | exit 0 |
| M2 静态矩阵 | `python3 scripts/verify/verify_m2_acceptance.py` | exit 0 |
| 文档治理 | `python3 scripts/docs/check.py` | exit 0；`docs governance ok (16 indexes)` |
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

`tests/test_docs_check.py`（13 项）覆盖：合规树为绿；缺索引、缺标记、`historical` 配 `task`、未登记顶层目录、登记目录缺 README、`AGENT-INDEX` 缺路径、历史目录未被默认排除、断链、specs 未登记、`delivery/completed` 缺 READ-ONLY 各为红；`#anchor`、目录链接、`https://` 与代码块内断链不误报。

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
- 既有入口未破坏：全量单测 168 项、六个门禁、`verify-control.sh` 与四仓入口测试覆盖。
