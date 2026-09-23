# CHG-20260923-056：联合工程优化 A——结构审计、Config 与 Client 解耦

## 1. Basic Information

- Level: L
- Status: IMPLEMENTING
- Created: 2026-09-23
- Current repository: wt-media-workspace（治理）；运行时改动分布于 wt-media-agent、wt-media-desktop、wt-media-cloud
- Affected repositories: wt-media-agent（主）、wt-media-desktop（主）、wt-media-cloud（仅 web/src/apps/desktop 两文件）、wt-media-workspace（治理记录与基线回写）

## 2. Change Goal

完成上线前工程优化第一阶段：以 ADR-0016 为目录基线，把 Agent 的配置、日志、路径收口到 `runtime/` 并接通真实组装链（bootstrap）；把 Desktop 从 1570 行单文件 `main.rs` 拆为 bootstrap/config/paths/state/commands 分层并建立强类型配置；两端 Client 全部改为构造注入；消灭已审计确认的硬编码（端口 8765/18080、超时、BitBrowser 地址散落 `os.getenv`）；建立 Desktop → Vue 的受控 Cloud 地址链路。

用户可见的独立可验证结果：
1. Agent 可脱离 Desktop，用 `config/agent.toml` + 环境变量独立启动，`/healthz` 可访问；Cloud Agent 入口真实接通 TaskRunner 领取循环。
2. Desktop 以配置驱动启动 sidecar 并传入受控参数（端口/数据目录/token），sidecar 鉴权生效。
3. Desktop Vue 从 `get_public_config` command 获取 Cloud 地址，不再硬编码。
4. 既有 M2 链路（bind/account_check/cookie_read/profile）dev 模式回归不回退。

## 3. Baseline References

- Milestone: `delivery/milestones/M-launch-engineering.md`
- Engineering baseline: `docs/engineering/specs/2026-09-23-launch-engineering-optimization-program.md`（程序总纲与融合裁定）
- Decisions: ADR-0016（Agent 运行时分层）；架构基线 §5.8（本地目录和日志）
- 里程碑说明：属上线前联合工程优化里程碑（M-launch-engineering），不属 M2/M3；CHG-20260923-053 已并入本程序（见 D-04）
- 用户原始方案：2026-09-23 会话《WT Media Desktop × Agent 联合上线工程优化》

## 4. Current Facts

（三仓审计结论，证据将落入 `evidence/`）

- Desktop：`main.rs` 1570 行承载 17 个 `#[tauri::command]`；`commands/`、`filesystem/`、`secure_store/`、`system/`、`updater/` 均为 3 行空壳；无日志/配置框架；reqwest 无超时；端口 8765（main.rs:1534）与 18080（前端 init.js:24、CSP）独立写死；sidecar stdout/stderr 丢弃（main.rs:406）；`local_agent_account_check` 与 `local_agent_cookie_read` 各含 ~115 行重复 preflight。
- Agent：`config.py`/`log_setup.py` 零引用死代码；`executors/{profile,cookie,account_check,proxy_mutation}.py` 与 `local_api/server.py:57-60` 共 5 处 `os.getenv` 自建 BitBrowserClient；`local_main.py`/`cloud_main.py` 空壳（`app.py` 只打印 scaffold）；`sidecar_main.py:15` 硬编码 `["--host","127.0.0.1","--port","8765"]` 且 auth_token 为空；`cloud_agent_client.py:195` timeout=10 写死；日志变量名三分裂（`WT_MEDIA_LOG_LEVEL` / `WT_MEDIA_AGENT_LOG_LEVEL` / shell 脚本第三种）；数据目录逻辑在 `config.py:36` 与 `migration.py:77-81` 双实现。
- Cloud Web：`apps/desktop/features/local-agent/init.js:24-29` `cloudBaseUrl()` 无条件返回 `http://127.0.0.1:18080`；`features/local-logs/LocalLogsPage.vue:8` 前端直连 `fetch('http://127.0.0.1:8765/healthz')`（会被 CSP 拦截）。

## 5. Scope

### Add

- Agent：`src/wt_media_agent/runtime/`（config/context/paths/environment/logging）、`bootstrap/`（local/cloud）、`clients/`、`services/`、`config/agent.toml`、`config_online/agent.toml`、AST 边界测试、config/bootstrap/sidecar 参数测试。
- Desktop：`src-tauri/src/bootstrap.rs`、`config/`、`paths/`、`state/`、`commands/agent.rs`、`resources/desktop.production.toml`、`get_public_config` command、config/paths 测试。
- 治理：程序总纲文档、CHG-057/058/059 planned 登记。

### Modify

- Agent：executors 改构造注入、`local_api/server.py` 接受注入、`sidecar_main.py` 受控参数、`local_main.py`/`cloud_main.py` 接真实 bootstrap、平台 URL 常量化、受目录迁移影响的既有测试。
- Desktop：`main.rs` 收缩为入口、HttpClient 显式超时、`local_agent_start` 传参、既有单测随模块迁移。
- Cloud Web：`init.js`（地址改 invoke + 回退）、`LocalLogsPage.vue`（healthz 改走 command）。
- 模块分工回写：agent/desktop/cloud 三仓 `AGENT-INDEX.md`+`DIRECTORY_MAP.md`。

### Delete

- Agent：`config.py`、`log_setup.py`（演化迁入 runtime 后删除原文件）、`runtimes/`（ADR-0016 第 4 条撤销，内容迁入 clients/services/runtime）。

### Explicitly Not Doing

- 不做日志轮转/保留/脱敏完整实现、测试目录隔离、operation_id 关联（CHG-B）。
- 不做用户设置 UI、清理与诊断导出（CHG-C）。
- 不做端口就绪通知、实例身份验证、退出 draining、打包完整性校验、升级回归（CHG-D）。
- 不引入 DI 容器、配置中心、日志数据库、第二套 Agent Runtime。
- 不改 Cloud 业务逻辑、API 契约语义、既有 M2 业务行为。
- 不动 reqwest native-tls→rustls。
- 不改 Cloud Web 模块结构与 API 层（仅 desktop app 两文件）。

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | 基线融合采用方案一：目录收口遵循 ADR-0016（runtime/、clients/、services/、撤销 runtimes/），配置组织 config/+config_online/ 镜像、env>file>default、**TOML 格式**（措辞由 D-05 更正）；ADR-0016 零修订 | CONFIRMED（2026-09-23 用户裁定） |
| D-02 | 本会话仅执行 CHG-A；B/C/D 登记 planned 不激活 | CONFIRMED（2026-09-23 用户裁定） |
| D-03 | 模块分工回写采用多文件同步：每 CHG 完成即更新各仓 AGENT-INDEX/DIRECTORY_MAP 与 workspace 职责基线 | CONFIRMED（2026-09-23 用户裁定） |
| D-04 | CHG-20260923-053 并入本程序：其 Task 1～5 并入本 CHG（采纳其更细目录方案：`clients/bitbrowser/` 包并新增公开 `open_url()`、`services/{browser,net}/`、`runner/` 三拆并重导出保住 `TaskRunner` 语义、storage 整理重导出、`utils/time.py`、executor 不直连私有 `_post`、`test_patch_targets.py`）；Task 6 归 057、Task 7 归 059；唯一偏差：sidecar 按**受控环境变量传参**执行（不保字面 argv），`test_sidecar_entry.py` 断言相应调整 | CONFIRMED（2026-09-23 用户裁定） |
| D-05 | Agent 配置文件格式定为 **TOML**（`config/agent.toml` + `config_online/agent.toml`），用标准库 `tomllib` 解析，不引入 YAML 依赖；D-01 与程序总纲 §2 的「YAML」措辞据此回写 | CONFIRMED（2026-09-23 用户裁定，替代原表述） |
| D-06 | T-02 实测得 22 条跨层边，其中**仅两条**越过 ADR-0016 的层级下降序，二者均照此执行并需进 T-05 白名单：①`runtime/environment.py → clients.bitbrowser`（§1 称 runtime 不引用业务层，§4 却把环境探测指派给该模块；它必须区分 `BitBrowserIdentityError` → `identity_unverifiable` 与 `BitBrowserError` → `unreachable`，此行为有测试覆盖。取 §4，并把白名单**收窄到单文件粒度**，不放开整条 `runtime → clients`）；②`clients/bilibili/identity.py → services.browser`（§1 将 `{clients, services, storage}` 列为无序集合，§3 明禁边只有 `clients→executors`、`services→executors`、`utils→业务层`，同级边被允许） | CONFIRMED（2026-09-23，T-02 执行时依 ADR-0016 判定，计划已载明；证据 `task-02-structure-migration.md` §4） |
| D-07 | Agent 配置中的凭据通路**收窄为仅环境变量**：`config/agent.toml` 与 `config_online/agent.toml` 里出现的任何敏感键（token/password/secret/cookie 等）一律被加载器忽略，并按**键名**告警（绝不输出值）；`runtime_token` 只能来自 `WT_MEDIA_AGENT_RUNTIME_TOKEN`。依据是用户批准的程序总纲 §4「敏感与临时运行上下文不混进部署配置」，与 ADR-0016 §7（允许凭据放在仓库配置中）取**更严**者，**ADR-0016 本身不改**。后果：`config_online/` 的「整目录替换」分发机制不承载凭据，CHG-D(059) 的发布校验不得依赖该通路；`config/README.md` 与 `config_online/README.md` 已声明此收窄 | CONFIRMED（2026-09-23 用户批准的程序总纲 §4；T-03 落地，证据 `task-03-runtime-config.md` §9） |

## 7. Pending Questions

| ID | Question | Blocking |
|---|---|---|
| Q-01 | `config_online/agent.toml` 与 Desktop `resources/desktop.production.toml` 的**生产真实 Cloud 地址**待发布前确认（当前部署模型为「本机 Cloud 服务 127.0.0.1:18080」还是远程 Cloud，决定发布配置值与 CSP 策略） | NO（不阻塞开发默认值与机制实现；阻塞 CHG-D 发布验证） |

## 8. Implementation Tasks

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | 治理工件就绪：本 change.md、checkpoint、status×3、planned 057/058/059、LEDGER、CURRENT_CONTEXT 再生成；CHG-053 标注 SUPERSEDED 并入 | DONE | `verify_agent_entry.py` 通过；CURRENT_CONTEXT 指向本 CHG |
| T-02 | Agent 结构迁移（吸收 053 Task 1-3）：`constants.py`→`runtime/`（含 `runtime/version.py`）；`clients/bitbrowser/` 包拆分并新增公开 `open_url()`，executor 不再直连私有 `_post`；`clients/cloud/` 迁移；`services/{browser,net}/` 建立；`runtime/environment.py` 委托 services 并撤销 `runtimes/`；`storage/` 整理（checkpoint/sqlite/migration 重导出，`storage.migration` 路径与符号不变）；`runner/` 三拆并重导出 `TaskRunner`/`TaskRunnerConfig`（测试零改动）；`local_api/` 瘦身；`utils/time.py`；既有 85 用例随迁全绿 | DONE | `bash scripts/test.sh`（≥85 OK）；`migrate-storage.sh` 连续两次成功；`verify-health.sh` 通过 |
| T-03 | Agent runtime/config + paths（吸收 053 Task 5）：强类型 AgentConfig（env>file>default，TOML/`tomllib`，测试目录接缝）；`configs/`→`config/` + `config_online/` 同构镜像；RuntimePaths 三态；统一 `WT_MEDIA_LOG_LEVEL`；删除 config.py/log_setup.py 死代码与目录双实现 | DONE | config loader 测试（默认/文件/env/非法/凭据忽略）全绿；运行时代码零处引用 `config_online`（打包校验除外） |
| T-04 | Agent bootstrap + executors 注入（吸收 053 Task 4，按 D-04 偏差执行）：`bootstrap/{local,cloud,sidecar,app}.py` 真实组装（接通 TaskRunner，runner 默认关闭）；删除 5 处 os.getenv 自建 client；CloudAgentClient timeout 接入配置；sidecar_main 瘦身为受控环境变量传参（`WT_MEDIA_LOCAL_API_HOST/PORT`、`WT_MEDIA_AGENT_RUNTIME_TOKEN`、`WT_MEDIA_AGENT_DATA_DIR`），pyproject 入口重指；`test_sidecar_entry.py` 断言调整 | TODO | bootstrap 组装测试（FakeClient）；grep 证明 executors 无 os.getenv；sidecar 参数测试 |
| T-05 | Agent AST 边界测试（ADR-0016 第 3 条机器校验，含 `test_patch_targets.py`）+ 平台 URL 常量化 | TODO | AST 测试全绿；server.py/account_check.py 无内联 URL 字面量 |
| T-06 | Desktop 拆分 main.rs：bootstrap/config/paths/state/commands/agent.rs；17 命令原样迁移；account_check/cookie_read 重复 preflight 提取共用；HttpClient 超时；端口进配置 | TODO | `cargo test` 全绿；`cargo build` 通过 |
| T-07 | Desktop Cloud 地址链路 + sidecar 传参：`get_public_config` command；`resources/desktop.production.toml`；`local_agent_start` 传环境变量；生产模式忽略地址类 env 覆盖 | TODO | config loader 单测（默认/文件/env/非法/生产忽略） |
| T-08 | Cloud Web 两文件：init.js cloudBaseUrl 改 invoke（带回退）；LocalLogsPage healthz 改走 command | TODO | desktop 前端既有测试全绿 |
| T-09 | 联调回归 + 证据落盘：dev 模式跑通 sidecar 启动（传参生效、鉴权生效）、bind/account_check/cookie_read/profile 链路、`/healthz` curl、Agent 独立启动 | TODO | evidence/ 各项记录 PASS |
| T-10 | 模块分工回写 + 收尾：三仓 AGENT-INDEX/DIRECTORY_MAP、workspace 基线核对、LEDGER/CURRENT_CONTEXT 同步、DONE Gate | TODO | `verify_agent_entry.py`+`verify_delivery_governance.py` 通过 |

## 9. Repository Checklist

### wt-media-workspace

- [ ] 程序总纲 `docs/engineering/specs/2026-09-23-launch-engineering-optimization-program.md`
- [ ] planned 登记 CHG-20260923-057/058/059
- [ ] LEDGER 与 CURRENT_CONTEXT 同步
- [ ] evidence/ 记录齐全

### wt-media-cloud

- [ ] 仅 `web/src/apps/desktop/features/local-agent/init.js` 与 `features/local-logs/LocalLogsPage.vue` 两文件

### wt-media-agent

- [ ] runtime/、bootstrap/、clients/、services/、config/、config_online/ 落地
- [ ] runtimes/、config.py、log_setup.py 删除
- [ ] 全部测试绿

### wt-media-desktop

- [ ] bootstrap.rs、config/、paths/、state/、commands/ 落地
- [ ] main.rs 收缩
- [ ] cargo test / build 绿

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Agent 脱离 Desktop 独立启动，`/healthz` 200 | 手动启动 + curl，evidence 记录 | TODO |
| AC-02 | Agent executors 无 os.getenv 自建 client，Client 全构造注入 | AST 测试 + grep 证据 | TODO |
| AC-03 | sidecar 以受控参数启动且鉴权生效（无 token 请求 401） | 手动验证 + evidence | TODO |
| AC-04 | Desktop `cargo test` 全绿，main.rs < 300 行 | 命令输出 + wc -l | TODO |
| AC-05 | Vue 从 `get_public_config` 获取 Cloud 地址（无硬编码 18080） | dev 模式断点/日志 + 代码 grep | TODO |
| AC-06 | 既有 M2 链路 dev 回归通过（bind/account_check/cookie_read/profile） | 手动回归 + evidence | TODO |
| AC-07 | 三仓既有测试全绿（unittest 85+ 迁移后、cargo test、web 测试） | 命令输出 | TODO |
| AC-08 | 治理校验通过（verify_agent_entry、verify_delivery_governance） | 脚本输出 | TODO |
| AC-09 | Local / Cloud / sidecar 三种模式各有一次真实启动与健康输出记录（吸收 053 验收 1） | 手动启动 + evidence | TODO |
| AC-10 | 任务链路 e2e：Cloud Task → runner → executor → client/service → 结果上报 → checkpoint 落库 → 重启恢复，至少跑通一次（吸收 053 验收 2） | 手动回归 + evidence | TODO |
| AC-11 | 新增一个 executor + 一个 client 的 demo 证明无需改 runtime（吸收 053 验收 3） | demo 代码 + evidence | TODO |

## 11. Evidence

Evidence files live in `evidence/`，按 Task 编号记录事实。

- `evidence/task-02-baseline.md`：Agent 测试基线实测（85 tests OK，含解释器版本矩阵）。
- `evidence/task-02-structure-migration.md`：T-02 结构迁移取证——14 个 commit 的逐 commit 测试矩阵（均 ≥85 且 OK）、冻结导入 sha256 恒等、冻结路径与符号清单、22 条跨层边全集与**仅有**的两条 ADR-0016 例外、PyInstaller 产物 PYZ 模块清单。
- `evidence/task-03-runtime-config.md`：T-03 配置/路径取证——10 个 commit 的逐 commit 测试矩阵（107→172，单调不减）、`log_setup.py → runtime/logging.py` 的 blob 级纯移动证明（`R100`）、冻结导入 sha256 与 T-02 同值、`src/` 环境变量读取点归零（带阳性对照）、19/19 变异对照（并**作废**本会话早先因变异脚本未分发而不可采信的一组记录）、`factory` 零覆盖缺口的补测、取证中发现的既有连接泄漏（`ResourceWarning` 20→0）与修复、唯一行为变更的记录、以及**已枚举的未覆盖面**。

## 12. Current Checkpoint

Completed:
- 三仓审计（现状事实已录入 §4）。
- T-01 治理工件就绪：四仓 AI 入口文档各自独立提交（desktop `47a6263`、cloud `3b733ff`、workspace `e0444cd`；agent 上一轮已提交）；配置格式措辞按 D-05 回写为 TOML；测试基线证据规范化。
- T-02 Agent 结构迁移完成，agent `99f408c` → `b1233cc` 共 14 个 commit：
  `924e057` constants→runtime/、`4584591` bitbrowser 拆包、`86ed17b` cdp→services/、
  `b6dffc6` environment→runtime/（`runtimes/` 撤销）、`51f2ee4` cloud+shim、
  `5d3d6d2` proxy→services/net/、`233cb60` profile_guard→services/（`core/` 撤销）、
  `da7183a` reporting→local_api/、`daeb913` 平台身份+Cookie→clients/&services/、
  `379a700` runner/ 三拆（冻结导入证明点）、`4fff9cf` storage/sqlite 抽取、
  `94750df` 删死 import、`287bca3` utils/time 收口、`b1233cc` 补两个 `__init__.py`。
  目标树 29 文件齐备；`runtimes/`、`core/`、`constants.py`、`proxy_check.py`、
  `runner.py` 均已删除；冻结路径/符号/console scripts 全部未动。
- T-03 Agent runtime/config + paths 完成，agent `b1233cc` → `d870d1f` 共 **10** 个 commit：
  `9c7d3db` RuntimePaths 三态、`2e7afa3` config/ + config_online/ 与声明式加载器、
  `416a56a` log_setup.py 纯移动入 runtime/ 并删死代码 config.py、`4e7ecb8` 日志接配置
  （`server.main` 不再读环境变量）、`3bfc66b` 两个超时覆盖改构造注入、`3d1be25` 5 处
  自建 client 改由 factory 构造、`ad066e5` `default_data_dir` 委托 RuntimePaths、
  `6f987a7` DIRECTORY_MAP 回写、`54e2636` 补 factory 测试、`d870d1f` 修既有连接泄漏。
  新增 `runtime/paths.py`；`src/` 中 `runtime/config.py` 之外的环境变量读取点为
  **0**；`config.py` 删除、`log_setup.py` 迁移（blob 级零改动）；测试 107 → 172。

Current:
- T-04 Agent bootstrap + executors 注入。

Next:
- T-04 Agent bootstrap + executors 注入（`bootstrap/{app,local,cloud,sidecar}.py`、删除 5 处 `os.getenv` 自建 client、`sidecar_main.py` 受控环境变量传参、`test_bootstrap.py`）。

Blocked:
- None.

Recent verification:
- 审计结论来自源码 grep/阅读（2026-09-23）。
- T-02 逐 commit 测试矩阵（`git archive` 导出后各自实跑，非采信当时记录）：
  10 个 commit 为 `Ran 85 tests OK`，`4fff9cf`/`94750df` 为 90，`287bca3`/`b1233cc` 为 94；
  无一低于基线 85。
- 冻结导入：`tests/test_runner_session.py` sha256 在 14 个 commit 上恒为
  `888113ca…`，`git log -- <该文件>` 计数 0。
- `bash scripts/migrate-storage.sh --data-dir /tmp/wt-agent-ci` ×2 → 首次 2 applied、
  二次 0 applied；`bash scripts/verify-health.sh` → 测试 OK + health ok
  （该脚本用裸 `python3` 3.14.6、自占 18765 端口，独立于 venv 复现）。
- 打包：PyInstaller 6.22.2 实构建，PYZ 含 28 个 `wt_media_agent` 模块；
  `runner`/`executors` 为 0（sidecar 尚够不到，T-04 后需重新取证）。
- TOML 裁定的三条依据均已实测复核（见 D-05 与程序总纲 §2）。
- T-03 逐 commit 测试矩阵（同样以 `git archive` 导出后各自实跑，非采信当时记录）：
  107/133/133/145/155/155/163/163/171/172，全部 `OK`，单调不减，无一个低于 T-02 收尾的 94。
- T-03 冻结导入：`tests/test_runner_session.py` sha256 在 10 个 commit 上恒为
  `888113ca…`（**与 T-02 记录同值**），`git log -- <该文件>` 计数 0；对照空串哈希
  `e3b0c442…` 证明提取未静默失败。
- T-03 纯移动：`416a56a` 的 `--raw -M` 为 `R100`，新旧 blob 同为 `63c36d3…`，
  即「移动」与「删死代码」同 commit 但均未改一行逻辑。
- T-03 环境变量收口：`runtime/config.py` 之外读取点 0，对照（该文件自身）2 处命中；
  死 import 扫描 0，对照植入 `socket`/`json` 均被报出。
- T-03 变异对照 19/19 全部转红并还原为绿。**本会话早先记录的一组变异结果已作废**：
  脚本 `/tmp/mut.sh` 当时只定义函数未分发 `"$@"`，以 `bash` 调用时静默空转；
  修复分发后整组重做，并要求「基线先绿 / 变异转红 / 还原回绿」三步俱全才计数。
- T-03 真实进程：`migrate-storage.sh --data-dir` ×2 → `2 applied` 后 `0 applied`；
  不带 `--data-dir` 落在 `<repo>/.local/data/`（已被 `.gitignore:2` 覆盖）；
  `verify-health.sh` 输出配置格式日志行 `2026-09-23T23:00:37 [INFO] __main__: …` 与
  `wt-media-agent health ok`。
- T-03 取证中发现并修复既有缺陷：`with sqlite3.connect(...)` 不关连接，`apply_migrations`
  每次调用泄漏一个（启动路径上）。`ResourceWarning` 由 T-02 收尾的 0 条升到 20 条是
  因为 T-03 新测试多调了几次才使其可见；三站点改用 `closing(...)` 后回到 **0** 条，
  且迁移的提交语义经真实进程复核未变。

## 13. DONE Gate

- [ ] Scope completed.
- [ ] No blocking `Q-xx`.
- [ ] Acceptance matrix all PASS.
- [ ] Automated tests passed or justified.
- [ ] Manual verification evidence recorded where required.
- [ ] Diff checked for out-of-scope changes.
- [ ] Runtime repositories touched only if listed in scope.
- [ ] Required baselines updated.
- [ ] Affected repositories committed independently.
