# CHG-20260923-056：联合工程优化 A——结构审计、Config 与 Client 解耦

## 1. Basic Information

- Level: L
- Status: DONE（2026-09-24 归档；见文末「关闭记录」）
- Created: 2026-09-23
- Current repository: wt-media-workspace（治理）；运行时改动分布于 wt-media-agent、wt-media-desktop、wt-media-cloud
- Affected repositories: wt-media-agent（主）、wt-media-desktop（主）、wt-media-cloud（仅 `web/src/apps/desktop` 的两个生产文件 + 两个测试文件）、wt-media-workspace（治理记录与基线回写）

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
- 不改 Cloud Web 模块结构与 API 层（只动 desktop app 的两个生产文件与其两个测试文件，见 §9）。

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
| D-08 | T-05 把 D-06 的例外落成机器规则时发现**第三条**越序边：`local_api/server.py → bootstrap.app`（T-04 引入，`server.main` 需要装配组件）。ADR-0016 §1 把 `local_api/` 与 `runner` 并列为平行层，§2 又称 `bootstrap/` 是唯一生产初始化入口——照 §2 取；且这条例外**只对 `local_api/server.py` 这一个文件**成立，不放开整条 `local_api → bootstrap`。与 D-06 同法：白名单收窄到单文件，机器规则的例外收窄测试证明「把例外放宽到整层会被抓住」。**ADR-0016 零修订**，此为实现对既有条款的一处单文件收敛 | CONFIRMED（2026-09-23，T-05 执行时依 ADR-0016 §2 判定；证据 `task-05-boundary-tests.md` §3） |
| D-09 | Desktop 的 `RELEASE_FAILED`（「释放账号检查本机授权失败」，`preflight.rs:80`）在 **Cookie 读取**流程里也报「账号检查」。这是它**一直**的说法：T-06 合并两处重复 preflight 时实测两条流程各自内联的这行文案**本来就相同**，故合并后保持逐字不变，由 `release_text_still_names_the_account_check_flow` 钉住现状。改成按流程取名（`释放{noun}本机授权失败`）是一词之改，但**刻意不塞进一个承诺「无用户可见文案变更」的 commit**——用户可见文案的变更应单独可见、单独可回滚。登记为待决，不在本 CHG 修 | CONFIRMED（2026-09-24，T-06 执行时实测；证据 `task-06-desktop-split.md` §9.3） |

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
| T-04 | Agent bootstrap + executors 注入（吸收 053 Task 4，按 D-04 偏差执行）：`bootstrap/{local,cloud,sidecar,app}.py` 真实组装（接通 TaskRunner，runner 默认关闭）；删除 5 处 os.getenv 自建 client；CloudAgentClient timeout 接入配置；sidecar_main 瘦身为受控环境变量传参（`WT_MEDIA_LOCAL_API_HOST/PORT`、`WT_MEDIA_AGENT_RUNTIME_TOKEN`、`WT_MEDIA_AGENT_DATA_DIR`），pyproject 入口重指；`test_sidecar_entry.py` 断言调整 | DONE | bootstrap 组装测试（FakeClient）；grep 证明 executors 无 os.getenv；sidecar 参数测试。**Goal 里的「pyproject 入口重指」未发生**：T-10 核对时发现 `pyproject.toml` 在本 CHG 全程**未被改动**（最后一次改它是 M2 的 `01fe41e`），四个 console script 早已指向 `local_main:main`/`cloud_main:main`/`local_api.server:main`/`storage.migration:main`——T-04 实际做的是把前两个模块改成真实委托，使既有条目**首次真正可用**，无需改 pyproject |
| T-05 | Agent AST 边界测试（ADR-0016 第 3 条机器校验，含 `test_patch_targets.py`）+ 平台 URL 常量化 | DONE | R1–R10 全绿且每条有控制组证明「能红」（规则放在任务前的树上实跑转红并点名六处）；patch 目标可解析且在别名重构下转红；`executors/`+`local_api/` 无内联 URL 字面量（grep 0 命中 / 对照树 2 命中） |
| T-06 | Desktop 拆分 main.rs：config/paths/state/commands；17 命令原样迁移；account_check/cookie_read 重复 preflight 提取共用 | DONE | `cargo test` 全绿（42 passed）；`cargo build` 通过；`main.rs` 1570 → 89 行；`generate_handler!` 17/17 逐字同序；9 条既有测试逐字不变、17 命令的 7 处改动逐条归因 |
| T-07 | Desktop Cloud 地址链路 + sidecar 传参 + 配置接线：`bootstrap.rs`（把已就位的 `config.rs`/`paths.rs` 接到 `main`）；移除 `Client::new()` 的无超时与 `main.rs:1534` 的 `8765`；CSP 改运行时注入；`uuid` per-launch token；sidecar 两条 path 同一组环境变量；`get_public_config` command（含 `dto/config.rs`、`commands/public_config.rs`）；生产模式忽略整个 `WT_MEDIA_DESKTOP_*` 命名空间 | DONE | config loader 单测（默认/文件/env/非法/生产忽略）；T-06 遗留的 23 条「从未使用」告警（`config.rs` 16 + `paths.rs` 7）归零 |
| T-08 | Cloud Web 两文件：init.js cloudBaseUrl 改 invoke（带回退）；LocalLogsPage healthz 改走 command | DONE | desktop 前端既有测试全绿 |
| T-09 | 联调回归 + 证据落盘：dev 模式跑通 sidecar 启动（传参生效、鉴权生效）、bind/account_check/cookie_read/profile 链路、`/healthz` curl、Agent 独立启动 | DONE | AC-01…AC-11 逐条 PASS 且各有阳性对照（`evidence/task-09-acceptance.md`）；Desktop 侧四次真实启动见 `evidence/task-09-desktop-launch.md`。**AC-05 方法与计划不同**：计划写「dev 模式断点/日志」，实际改为把探针页经 `TAURI_CONFIG` 嵌进真二进制，因为断点只能证明调用发生了、不能证明**页面拿到的就是配置里的值**，而后者才是这条 AC 要的 |
| T-10 | 模块分工回写 + 收尾：三仓 AGENT-INDEX/DIRECTORY_MAP、workspace 基线核对、LEDGER/CURRENT_CONTEXT 同步、DONE Gate | DONE | 三仓文档各一 commit（agent `ba179ed`、desktop `5c74ca1`+`2599819`、cloud `f89467f`），判据为退役名扫描带阳性对照；基线核对逐节判据与两处偏离见 `evidence/task-10-baseline-check.md`；`verify_agent_entry.py` + `verify_delivery_governance.py` 均 0 ERROR / exit=0；快照已再生成 |

## 9. Repository Checklist

### wt-media-workspace

- [x] 程序总纲 `docs/engineering/specs/2026-09-23-launch-engineering-optimization-program.md`
- [x] planned 登记 CHG-20260923-057/058/059（三目录均存在）
- [x] LEDGER 与 CURRENT_CONTEXT 同步（本次收尾提交，含快照再生成）
- [x] evidence/ 记录齐全（task-02…task-10 共 9 份 + `artifacts/` 运行产物 + `tools/`）

### wt-media-cloud

- [x] 四个文件：生产 `web/src/apps/desktop/features/local-agent/init.js`、`features/local-logs/LocalLogsPage.vue`；测试 `web/src/localAgentBoundary.test.js`、`web/src/localAgentService.test.js`（后两者是前两者的常驻守护，与改动同批提交 `305d002`）

### wt-media-agent

- [x] runtime/、bootstrap/、clients/、services/、config/、config_online/ 落地
- [x] runtimes/、config.py、log_setup.py 删除
- [x] 全部测试绿（`bash scripts/test.sh` → Ran 253 tests OK）

### wt-media-desktop

- [x] bootstrap.rs、config/、paths/、state/、commands/ 落地
- [x] main.rs 收缩（1570 → 115 行，AC-04 上限 300）
- [x] cargo test / build 绿（63 passed；`cargo build` 成功，4 条告警全部来自本 CHG 明示不动的三个空壳 `filesystem`/`secure_store`/`updater`/`system`）

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | Agent 脱离 Desktop 独立启动，`/healthz` 200 | 手动启动 + curl，evidence 记录 | **PASS** `tools/ac01_ac09_agent_modes.py`（四棵树证明配置文件真被读；`/healthz` 200、`/api/v1/status` 200、真实 BitBrowser 40 profiles）→ `evidence/task-09-acceptance.md` AC-01 |
| AC-02 | Agent executors 无 os.getenv 自建 client，Client 全构造注入 | AST 测试 + grep 证据 | **PASS** `tools/ac02_agent_boundary.sh`（grep 带分母与活对照：`executors/` 0/395、`local_api/` 0/714；`os.environ` 2 命中均落在 `runtime/config.py`）+ AST 29 tests OK |
| AC-03 | sidecar 以受控参数启动且鉴权生效（无 token 请求 401） | 手动验证 + evidence | **PASS** 两处：工具 MODE 3（直接启动）与 Desktop 真实拉起（AC-05 的 M3）。三态齐备 200/401/401，且端口来自当次配置（非 8765） |
| AC-04 | Desktop `cargo test` 全绿，main.rs < 300 行 | 命令输出 + wc -l | **PASS** `tools/ac04_desktop.sh`：63 passed；`main.rs` **115 行**（T-06 时 89，T-07 接线后 115） |
| AC-05 | Vue 从 `get_public_config` 获取 Cloud 地址（无硬编码 18080） | dev 模式断点/日志 + 代码 grep | **PASS** 运行期改由**真 WebView 内的探针页**取证（比断点更强：页面自己调 `get_public_config` 并回报值），四次启动均返回当次配置的值；静态面 `grep 18080 src/apps/desktop/` **0 命中 / 分母 9 文件**（阳性对照命中 `init.js`）→ `evidence/task-09-desktop-launch.md` |
| AC-06 | 既有 M2 链路 dev 回归通过（bind/account_check/cookie_read/profile） | 手动回归 + evidence | **PASS（16 exercised / 3 not，逐条枚举）** `tools/ac06_local_chains.py`：真实 bilibili 账号识别、36 个真实 cookie 且值不入日志（含「profile id 在日志中可见」的阳性对照）、profile open/close 使 BitBrowser 自身 status 0→1→0 并复原；3 条未做连同理由列在输出末尾 |
| AC-07 | 三仓既有测试全绿（unittest 85+ 迁移后、cargo test、web 测试） | 命令输出 | **PASS** `tools/ac07_three_repos.sh`：agent **253 tests OK**（基线 85）、desktop 63 passed、web 21 files / 101 tests passed |
| AC-08 | 治理校验通过（verify_agent_entry、verify_delivery_governance） | 脚本输出 | **PASS** `tools/ac08_governance.sh`：两者 0 ERROR，**且同对校验器在故意弄坏的副本上 exit=1**（0 ERROR 只在「校验器会红」被证明后才有意义） |
| AC-09 | Local / Cloud / sidecar 三种模式各有一次真实启动与健康输出记录（吸收 053 验收 1） | 手动启动 + evidence | **PASS** 三模式各一次（cloud 0.09s 退出 0、对死地址无出站请求；local 连真实 BitBrowser 40 profiles；sidecar 见 AC-03），另加 Desktop 真实拉起的 4 次 |
| AC-10 | 任务链路 e2e：Cloud Task → runner → executor → client/service → 结果上报 → checkpoint 落库 → 重启恢复，至少跑通一次（吸收 053 验收 2） | 手动回归 + evidence | **PASS** `tools/ac10_task_chain.py` 两 leg：LEG A 全链 `succeeded`/`progress=100` 且 checkpoint 已清；LEG B 中途 SIGKILL → 盘上留 `running` → 重启 `recovering 1 incomplete task(s)` + `resuming task <id>`。隔离 Cloud（独立实例 + 独立 schema，空表起步），**不碰**开发者 :18080 的积压任务表 |
| AC-11 | 新增一个 executor + 一个 client 的 demo 证明无需改 runtime（吸收 053 验收 3） | demo 代码 + evidence | **PASS** 常驻测试 `tests/test_new_task_type.py`（产品代码零改动，经公开缝 `register_executor` 装入）+ 失败验证 `evidence/artifacts/ac11-mutants.py`：**6/6 CAUGHT，0 SURVIVED**，含探测器自检 |

## 11. Evidence

Evidence files live in `evidence/`，按 Task 编号记录事实。

- `evidence/task-02-baseline.md`：Agent 测试基线实测（85 tests OK，含解释器版本矩阵）。
- `evidence/task-02-structure-migration.md`：T-02 结构迁移取证——14 个 commit 的逐 commit 测试矩阵（均 ≥85 且 OK）、冻结导入 sha256 恒等、冻结路径与符号清单、22 条跨层边全集与**仅有**的两条 ADR-0016 例外、PyInstaller 产物 PYZ 模块清单。
- `evidence/task-03-runtime-config.md`：T-03 配置/路径取证——10 个 commit 的逐 commit 测试矩阵（107→172，单调不减）、`log_setup.py → runtime/logging.py` 的 blob 级纯移动证明（`R100`）、冻结导入 sha256 与 T-02 同值、`src/` 环境变量读取点归零（带阳性对照）、19/19 变异对照（并**作废**本会话早先因变异脚本未分发而不可采信的一组记录）、`factory` 零覆盖缺口的补测、取证中发现的既有连接泄漏（`ResourceWarning` 20→0）与修复、唯一行为变更的记录、以及**已枚举的未覆盖面**。
- `evidence/task-04-bootstrap-injection.md`：T-04 bootstrap/注入取证——4 个 commit 的逐 commit 测试矩阵（184→204，单调不减；「移动文件」与「改逻辑」分列两个 commit）、冻结导入 sha256 与 T-02/T-03 同值、7/7 变异对照（其中 2 条初跑**不可判别**，各暴露一个真实测试缺口：`_as_bool` 的假值拼写与 `agent_id` 的**空断言**，补测后全部可判别）、AC-09 三模式真实进程输出（cloud 只报告 / local 连到真实 BitBrowser 40 个 profile / sidecar 401-401-200 token 矩阵且 token 不入 `ps`）、冻结入口脚本 ×3、静态扫描含阳性对照、PyInstaller 产物 PYZ 模块集 28→53（`runner`/`executors` 首次进包）、以及**已枚举的未覆盖面**（`bootstrap/local.py` 无单测、打包产物未重签时无法启动这一既存问题归 CHG-D(059)）。
- `evidence/task-05-boundary-tests.md`：T-05 AST 边界取证——3 个 commit 的逐 commit 测试矩阵（214→249，单调不减）、冻结导入 sha256 与 T-02/T-03/T-04 同值、**规则在任务之前的树上实跑转红**并逐行点名 `a4a43cc` 修掉的六处（R5 两处 `_post` + R9 四处 URL 字面量）、6/6 变异对照（含两处**我自己的脚本缺陷**已修正并披露）、`/tmp/t05patch.py` 的别名重构把 `test_patch_targets.py` 与**既有的** `test_proxy_check.py` 同时转红、AC-02 的 grep 双证据（HEAD 0 命中 / 对照树 2 命中，各带分母）与死 import 扫描的阳性对照、以及 **§9.1 逐条枚举的未覆盖面**（R10 只到层对、`from pkg import mod` 的保守、运行期拼装 URL、`patch.object/dict` 不解析、`clients/` 内硬编码值）。
- `evidence/task-06-desktop-split.md`：T-06 Desktop 拆分取证——11 个 commit 的逐 commit 测试矩阵（11→42，单调不减，且逐段能对上：+10 config、+8 preflight、−2 删死代码、+6 drain、+7 paths、+2 exit_report）、`main.rs` 1570→89 行（AC-04）、`generate_handler!` 17/17 逐字同序、**逐函数**的搬家核对（9 条既有测试 IDENTICAL / 10 条 BODY-SAME-SIG / 7 条 BODY-CHANGED 逐条归因）、CJK 字面量普查（99 条中 93 条逐字存在，6 条为模板分解，渲染由 16 行 `message_parity` 表钉住）、四份变异矩阵（config 12/12、drain 8/8、paths 7/7、exit_report 4/4）、**变异脚本自身错了五次**的完整披露、死代码删除带来的覆盖缺口（空票据守卫现在无覆盖）、Node 工具链的仓库级发现（CI 在任何分支上都不可能通过），以及 **§9.4 逐条枚举的未覆盖面**。

- `evidence/task-07-desktop-config.md`：T-07 Config 链路取证——7 个 commit 的逐 commit 测试矩阵（42→63 单调不减；告警 27→4 且**余 4 条为空壳**，不虚报为 0）、四份变异矩阵（CSP 6/6、`get_public_config` 6/6、`cloudBaseUrl` 5/5、sidecar 5/7 **+2 存活并登记**）、CSP 退役的三重证据（棘轮 + 金标 + `dev_csp` 保持 `None`）、**真实副作用**验证（真启动一次：`127.0.0.1:18766`、200/401/**401 三态齐备**、`<scratch>` 下三目录齐备且仓库 `.local/` 未被触碰、0 残留监听）、我自己的 data-dir 检查脚本缺陷（override 分支语义）**自查纠正**、一处计划偏差（CSP 注入点写浅了）与计划计数笔误（第 17/18 个命令）、以及**已枚举的未覆盖面**（两条 spawn 路径、`generate_handler!` 注册、`connect_timeout`）。
- `evidence/task-08-cloud-web.md`：T-08 Cloud Web 取证——单个 commit `305d002`、**行为性**的红输出（而非导入失败）、5/5 变异矩阵、`npm test` 96→**101**、AC-05 grep 升级为**常驻断言**（两条规则显式限定文件范围并注明理由）、一处**值级哨兵自查删除**（`"true"` 在红跑里从未触发，只为错误的理由匹配），以及**已枚举的未覆盖面**（`health()` 调用无单测、`bindTrustedLocalAgent()` 归 T-09）。
- `evidence/task-09-desktop-launch.md`：T-09 Desktop 真实启动取证——**四次**真实启动（M1 错 CSP / M2 Python fallback / M3 exe 旁 sidecar / M4 加 `ipc:` 的反事实），逐 leg 的实测输出；探针页如何经 `TAURI_CONFIG` 把 `devUrl` 置 `null` 而被嵌进真二进制（以及「首次构建疑似没生效」的判定过程）；T-07 遗留①②④的运行期闭合；**两向 CSP**（错地址 rejected+违规且 `originalPolicy` 逐字含该地址 / 对地址 resolved 零违规 / 按源精确：`localhost:18080` 四 leg 全拒）；**子进程环境从不读取**（`ps -wwE` 被拒后改为四项行为判据 + argv 的植入阳性对照）；三条实测发现（`development.python_fallback` 是装饰键、`connect-src` 缺 `ipc:`、`reqwest` 默认读 macOS 系统代理导致回环请求被接管）与**已枚举的未覆盖面**。
- `evidence/task-09-acceptance.md`：T-09 AC-01…AC-11 验收矩阵——逐条命令与实测输出、每条的**阳性对照**、环境事实表（含「为什么另建隔离 Cloud」）、以及 §覆盖边界 **7 条未覆盖项**（真实前端 bundle 未被驱动、只有 macOS、BitBrowser 链路依赖真实账号状态、`profile-create/update/delete` 与 bind 的 Cloud 往返未驱动、`connect_timeout` 不闭合、两处待裁定的产品决定、Cloud 仓 Go 测试不在验收面内）。
- `evidence/task-10-baseline-check.md`：T-10 入口文档回写 + 架构基线核对——三仓各自的**退役名扫描**（带分母与阳性对照）、`core/` 撤销的登记（代码追上基线，而非基线被违反）、§5.2/§5.4/§5.5/§5.8 与 ADR-0016 层表**逐节**的对照判据、**两处偏离**（§5.2 的 7 项差集，其中 `modes/`/`generated/` 是基线与实现正面冲突故留作待裁定；`runtime/paths.py` 无平台分支，§5.8 的 Windows 路径未实现）、一处 overstated 能力描述（文档与两条代码注释把「HTTP 桥」写成「HTTP/SSE 桥」）的纠正、**一次自查纠正**（zsh 不对未加引号的变量做词分割，导致第一版退役名扫描得到假的「0 命中」）、以及 §覆盖边界 **5 条未覆盖项**。`core/` 与 `runtimes/` 的撤销、根级 `config.py`/`log_setup.py` 的删除在基线侧**无需改动**：§5.2 的 `:1040` 早已明写这三者不保留。

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
- T-04 Agent bootstrap + executors 注入完成，agent `d870d1f` → `7e19622` 共 **4** 个 commit：
  `f7ed012` 执行器注入链（4 个执行器必填第三参、registry 闭包绑 client、runner 收注入注册表）、
  `587496b` 纯移动（4 个 `LocalApiServer` 测试迁出 `test_app.py`）、
  `3e47985` `bootstrap/` 包 + 三个模式入口 + `LocalApiServer` 必填 client +
  `CloudAgentClient` 超时接配置 + 两个配置键 + 删 `app.py`、
  `7e19622` `DIRECTORY_MAP.md` 回写。
  5 处自建 client 清零且无新增构造点；未装配的 runner 走既有 `no_executor` 路径（fail-closed）；
  三个模式首次各有真实进程启动；测试 184 → 204。侧记：`sidecar_main.main()` **无参数**，
  这正是 token 不能经 argv 泄漏的机制（AC-03）。
- T-05 Agent AST 边界测试 + 平台 URL 常量化完成，agent `7e19622` → `87cde92` 共 **3** 个 commit：
  `a4a43cc` 平台 URL 迁入 `clients/platform_urls.py` + `BitBrowserClient.open_url()` 公开
  （executor 不再直连私有 `_post`）、`d00147b` `tests/test_dependency_boundaries.py`
  （R1–R10 + 15 个控制组）、`87cde92` `tests/test_patch_targets.py`（发现 + 解析 + 绑定规则）。
  十条规则**每条都有控制组**证明它「能红」；把规则放到任务之前的树上实跑，报出的正是
  `a4a43cc` 修掉的那六处。测试 214 → 249。侧记：`local_api/server.py → bootstrap.app`
  是本期发现的**第三条**越序边，按 D-08 以单文件粒度收窄（不放开整层）。

- T-06 Desktop 拆分 `main.rs` 完成，desktop `c03d244` → `4b3a7b4` 共 **11** 个 commit：
  `ec2d34b` DTO 迁出、`d4ab510` HttpClient 拆两型、`3bcf2c7` 17 命令迁出（含 `state.rs`）、
  `72095b9` `config.rs` + `resources/desktop.production.toml`、`e6842c1` `preflight.rs`（合并两处
  重复预检与三类守卫）、`30b9ebf` 删 `local_agent/mod.rs` 死代码、`0982fc3` sidecar 启停抽出、
  `5cddc4e` sidecar 输出环形缓冲、`38b97be` 修 `scripts/test.sh`、`19541b3` `paths.rs`、
  `4b3a7b4` 退出报告补持有行数。`main.rs` **1570 → 89 行**（AC-04），测试 **11 → 42**，
  `generate_handler!` 17/17 逐字同序，9 条既有测试逐字不变。

- T-07 Desktop Config 链路，desktop `4b3a7b4` → `35a2ee9` 共 **7** 个 commit：
  `1276e98` `RuntimeToken`（`Uuid::new_v4()`，无 `Debug`/`Display`/`Serialize`）、
  `b4d4dc4` 生产布局不再理会 `WT_MEDIA_DESKTOP_CONFIG`、`2afe1d9` `bootstrap.rs` 配置定位/载入 +
  CSP 注入时机 + 编译内置兜底、`d838ccd` 两个 client 接配置（超时来自 TOML）+
  `LocalAgentClient` 持有 token、`14ff67c` `tauri.conf.json` 的 CSP 字面量退役、
  `6f94cbb` 第 18 个命令 `get_public_config`、`35a2ee9` 两条 spawn 路径注入同一组四个变量、
  **token 成为强制**（与 T-08 同批）。`8765` 字面量与 `Client::new()` 的无超时同时退役；
  `resources/desktop.production.toml` 成为部署事实来源。测试 42 → 63、bin warnings 27 → 4
  （余 4 条即四个空壳）。
- T-08 Cloud Web 单个 commit `305d002`：`init.js::cloudBaseUrl()` 改问 `get_public_config`、
  `LocalLogsPage.vue` 改走 `createLocalAgentService().health()`。`npm test` 96 → 101。
- T-09 联调回归与证据落盘（**本 Task 不动产品代码**，全部工具位于 `evidence/tools/`）：
  AC-01…AC-11 逐条落到可重跑的工具上并附阳性对照，四次 Desktop 真实启动闭合 T-07 的三处
  运行期遗留并完成两向 CSP 检查。矩阵见 `evidence/task-09-acceptance.md`，Desktop 深挖见
  `evidence/task-09-desktop-launch.md`。
- T-10 三仓入口文档回写完成，一仓一 commit：agent `ba179ed`、desktop `5c74ca1`
  （另有 `2599819` 单改两处注释）、cloud `f89467f`。判据是**退役名扫描**（各带分母与阳性对照），
  不是「读了一遍觉得对」。
  - agent：旧树的 `app.py`/`runner.py`/`core/`/`runtimes/`/两个顶层模块从 `AGENTS.md` 的
    Structure 消失；`DIRECTORY_MAP.md` 那句「`executors/account_check.py` 尚余 4 处 URL 字面量
    未迁出」已被 `a4a43cc` 作废，改指 `clients/platform_urls.py` 与 `PROXY_PROBE_URL`，
    并补上缺失的 `clients/platform_urls.py` 行；`README.md` 的 Key Directories 不再列已删包。
  - desktop：`DIRECTORY_MAP.md` 补齐 `bootstrap.rs`/`config.rs`/`paths.rs`/`token.rs`/`state.rs`/
    `http/`/`dto/`/`preflight.rs`/`resources/`，并把 sidecar 启停从 `local_agent/` 改指 `sidecar/`
    （`local_agent/` 只余契约类型 `BoundNodeFacts`）；`README.md` 原称本仓有 `src/` Vue 页面、
    用 `npm test` 验证、`binaries` 是 future placeholders——三条全不成立，已改。
  - cloud：补 T-08 的缺口——Desktop 应用行下补 `features/local-agent/init.js`（地址来源）
    与仓库根的 `localAgentBoundary.test.js`（常驻边界断言），需求路由补对应一行。
- T-10 一处**被夸大的能力描述**：四处文字（desktop 的 `AGENT-INDEX.md`、`AGENTS.md`，
  以及 `main.rs` 头注释与 `commands/agent.rs:89` 的文档注释）写「Rust 代理 Local Agent
  HTTP 与 **SSE**」。实测：Agent 侧确有 `text/event-stream` 端点
  （`local_api/server.py:445`），Desktop 侧消费流的地方 **0 处**——`local_agent_task_status`
  打的是状态端点、返回快照。两份入口文档随各自的 T-10 文档 commit 改掉并注明「不要写成
  已实现」，产品代码里的两条注释单独一个 commit（`2599819`）改掉——文档 commit 与代码
  commit 分开走。
- T-10 **架构基线核对**（逐节给判据，见 `evidence/task-10-baseline-check.md`）：
  §5.4 与 §5.5 **一致**——§5.4 的依赖方向由 `tests/test_dependency_boundaries.py` 的
  R2 白名单 + R10 冻结边棘轮机器校验（全绿即满足，不靠约定），§5.5 点名的三个平台目录
  齐备且 `clients/douyin/` 按 ADR-0015 确实未建；§5.2 与 §5.8 **各有一处偏离**，逐条登记。
- T-10 **`core/` 撤销的登记**：`core/profile_guard.py` → `services/profile_guard.py`，
  物理 `core/` 已不存在。基线侧**无需改动**——§5.2 的 `:1040` 早已明写
  「不保留 `modes/`、`core/`、`communication/`、`runtimes/`、`platforms/`、`generated/`」，
  ADR-0016 的层表也无 `core/`。这条登记的含义是**代码追上了文档**：撤销之后基线不再被违反，
  而是被满足。同批消失的 `runtimes/`（拆入 `clients/` + `services/`）与根级
  `config.py`/`log_setup.py`（内容迁入 `runtime/`）同理。
- T-10 两处**基线偏离**（只登记未改）：
  ①§5.2 的树与实际差 7 项（`local_main.py`/`cloud_main.py` 两个入口、两个废弃 shim、
  `adapters/` 占位包，以及 `modes/`/`generated/` 两个占位包）。前三类与计划一致、
  照实登记；**后两者是基线与实现正面冲突**（基线明写不保留、计划定为不动），
  按纪律不擅自回写文档，留作待裁定项（见 Next 第三条）。
  ②§5.8 另外指定了 Windows 的 `%LOCALAPPDATA%\WTMedia\Agent\`，而 `runtime/paths.py`
  （124 行）**没有任何 `sys.platform`/`os.name` 分支**，installed 态无条件走 `Path.home()`
  + `("Library","Application Support",…)`，故在 Windows 上会落到
  `%USERPROFILE%\Library\Application Support\WTMedia\Agent`。基线 §1.4 把 Windows x64
  列为桌面首版支持范围之一。本 CHG 无判据（全部取证只在 macOS 上做过，T-09 覆盖边界第 2 条
  已声明不可外推），故只报静态机制、不报实测失败，也不在本次动手改。
- T-10 **一次自查纠正**：第一版退役名扫描写成 `for f in $files`（`$files` 来自 `ls`）。
  zsh **不对未加引号的变量做词分割**，`$f` 成了整个多行字符串，grep 拿到多行文件名报错、
  又被 `2>/dev/null` 吞掉，于是得到「0 命中」。用 `runtime/constants.py` 做阳性对照才暴露
  （同一模式手工跑有命中）。换成 glob 重跑后 agent 仓得到 3 条命中、逐条合法。
  **这次 0 命中是检查坏了，不是仓库干净**——与本 CHG 反复强调的「否定结论必须先证明
  检查会失败」是同一回事，记在此处作为它的一次真实触发。
- T-10 一处**数字自查纠正**：基线核对初稿把 `runtime/paths.py` 写成 343 行（那是 desktop 仓
  `paths.rs` 的行数，串了）。实测 124 行，已改，且平台分支扫描的分母随之写明。

Current:
- **T-10 收尾完成，本 CHG 达到 DONE Gate**：`change.md` §1/§5/§8/§9/§10/§11/§13、`status/*.md`、
  evidence 齐全；快照经 `prepare_ai_workspace.py` 再生成；§13 九项逐项签字。状态已置 `DONE`。
- 三仓文档回写与基线逐节核对已完成（见 Completed 末条）。

Next:
- **归档决定（待用户裁定）**：按 `executing-wt-media-change` 的 Completion Gate，已完成的记录
  应从 `delivery/active` 与 `LEDGER.md` 移出。但下面四项待裁定均引用本目录的文件，
  故**不擅自归档**，等裁定结果一并处理。
- 两处**待用户裁定的产品决定**（本 CHG 只登记未改，见 `task-09-desktop-launch.md` §Findings）：
  ①生产 CSP 是否把 `ipc:` 加进 `connect-src`（可只改 `config`，`csp_connect_src` 本就允许空格分隔多值）；
  ②回环 client 是否加 `.no_proxy()`（涉及 Cloud client 是否保留系统代理）。
- 第三处**待用户裁定**由 T-10 的基线核对新增（见 `task-10-baseline-check.md` §偏离 1）：
  基线 §5.2 `:1040` 明写「不保留 `modes/`、`generated/`」，而两者实际以一行 docstring 的
  占位包形式保留，本次计划亦定为「不动」。两者零实现、零引用，裁定成本很低：要么删掉，
  要么把基线那句改成「保留为占位」。
- 第四处**由我造成、待用户裁定如何处置**：开发者的 Cloud `:18080` 上有一个 T-09 AC-10
  早期调试时被误建的 `noop_task`（`task_b21340775ace100173202de3`，`pending`，
  created 2026-09-24T00:49:21）。它是惰性的（`claimTask` 按 `created_at ASC` 领取，被
  :18080 上更早的 7 月积压排在后面），但它确实是本 CHG 计划外的一次写入。
  **清除它要动开发者的 Cloud，超出本 CHG 的授权**（§9 的 cloud 清单只含四个源码文件），
  故只登记不处置。

Blocked:
- None.（T-07 遗留③ `connect_timeout` 的隔离量测**被②挡住**：`reqwest` 默认走 macOS 系统代理，
  回环请求到不了 connect 阶段。这不是阻塞项，已按实测机制登记。）

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
- T-04 逐 commit 测试矩阵（同样以 `git archive` 导出后各自实跑）：`f7ed012`/`587496b`
  为 184，`3e47985`/`7e19622` 为 204，全部 `OK`，单调不减，无一低于 T-03 收尾的 172。
- T-04 冻结导入：`tests/test_runner_session.py` sha256 在 4 个 commit 上恒为 `888113ca…`
  （与 T-02/T-03 记录同值）；本 CHG 范围（`99f408c^..7e19622`）内 `git log -- <该文件>`
  计数 **0**，全史仅 `1e3e96f` 一次（本 CHG 之前）。
- T-04 变异对照 7/7 全部「基线绿 → 转红 → 还原绿」，另加 `f7ed012` 的 5 条。其中
  **M-11/M-12 初跑不可判别**，各暴露一个真实测试缺口并已补测：`_as_bool` 未覆盖
  `"false"/"0"/"off"` 这类 shell 会写的假值（读错会把「别跑」变成「去轮询 Cloud」）；
  `agent_id` 断言是**空断言**（配置默认值与 dataclass 默认值恰好同为 `local-agent-dev`）。
- T-04 静态扫描：`src/` 环境变量读取点仍只有 `runtime/config.py` 一处；死 import 0 条，
  阳性对照植入的未使用 import 被报出（证明扫描器非空转）。
- T-04 真实进程（AC-09）：cloud 模式打印环境事实 JSON 并 `exit=0`、无出站请求；
  local 模式 `/healthz` 200、`/api/v1/status` 的 `bitbrowser_status=normal` 且
  `profile_count=40`（真实 BitBrowser，非 mock）；sidecar 模式 token 矩阵 401/401/200，
  `ps` 中无 token，数据目录生效。冻结脚本 `migrate-storage.sh` ×2 → `2 applied`/`0 applied`，
  `verify-health.sh` → `health ok`。
- T-04 打包重新取证：PyInstaller 6.22.2 实构建，PYZ 内 `wt_media_agent.*` 由 T-02 的
  **28 → 53**（`runner` 0→4、`executors` 0→8、`bootstrap` 3），T-02 遗留的
  「sidecar 够不到 runner/executors」已消除。未重签的产物启动失败（`different Team IDs`）
  属既存打包/签名问题，登记归 CHG-D(059)，不作为 T-04 的通过条件。
- T-05 逐 commit 测试矩阵（同样以 `git archive` 导出后各自实跑）：`a4a43cc` 为 214，
  `d00147b` 为 243，`87cde92` 为 249，全部 `OK`，单调不减，无一低于 T-04 收尾的 204。
- T-05 冻结导入：`tests/test_runner_session.py` sha256 在 3 个 commit 上恒为 `888113ca…`
  （与 T-02/T-03/T-04 记录同值）；本 CHG 范围（`99f408c^..87cde92`）内
  `git log -- <该文件>` 计数 **0**。
- T-05 **规则确能转红**（这是本期最重要的一条，因为「规则全绿」与「规则从不报错」在输出上
  无法区分）：把 `test_dependency_boundaries.py` 放到 `a4a43cc~1` 的源码树上实跑，
  R5/R9 两条失败并逐行点名六处——`account_check.py:65`/`:80` 的 `_post` 调用与
  `:29`/`:30`/`:31`/`:82` 的 URL 字面量；在 `a4a43cc` 的树上全绿。
- T-05 变异对照 6/6 全部「基线绿 → 转红 → 还原绿」。其中两条初跑的问题**判定为我的脚本
  缺陷而非测试缺口**并已披露：M-2 把常量替换成了它自己的字面量（等值替换，不构成变异）、
  M-5 锚点缩进写错（报 ANCHOR MISMATCH 而非静默跳过）。另发现 `open_url` 此前**无任何
  测试覆盖**，补 `OpenUrlTests` 2 例后 M-1/M-6 才可判别。
- T-05 patch 面：`/tmp/t05patch.py` 把 `local_api/server.py` 改成模块别名访问后，
  `test_patch_targets.py` 报 3 条失败、**既有的** `test_proxy_check.py` 报 1 条错误，
  还原后双双回绿——「凡测试 patch 的名字，源侧一律用 `from X import name`」这句
  由两个文件同时守着。
- T-05 AC-02 双证据：grep 在当前树 0 命中（分母 1109 行）、在 `7e19622` 对照树 2 命中
  （分母 1120 行，即 `account_check.py:65`/`:80`）——**有分母的对照组**，不是空转的 0。
  死 import 扫描 65 文件 0 条，阳性对照植入的 `import json` 被报出（该扫描器初版把每个
  `from __future__ import annotations` 都误报，排除后才归零；属扫描器缺陷，已记录）。
- T-05 冻结脚本：`migrate-storage.sh --data-dir /tmp/t05mig` ×2 → `2 applied`/`0 applied`；
  `verify-health.sh` → `wt-media-agent health ok`。
- T-06 逐 commit 测试矩阵（`/tmp/t06_matrix.sh`，逐个 checkout 后**强制重编**再量）：
  11/11/11/11/21/29/27/27/33/33/40/42，全部 `OK`，单调不减。逐段可对：
  +10（`config.rs`）、+8（`preflight.rs`）、−2（删 `local_agent` 的两条死代码测试）、
  +6（`drain`）、+7（`paths`）、+2（`exit_report`）。
- T-06 告警数（同一口径，cargo 自报的 `generated N warnings`）：bin 14 → 29（config 新增 16）
  → 20（删死代码 −9）→ 21（drain +1）→ 28（paths +7）→ **27**（`4b3a7b4` 让 `drain::len`
  不再是死函数 −1）；test target 12 → 4。**剩余 23 条**「从未使用」是 `config.rs` 16 +
  `paths.rs` 7，属 T-07 接线后即消除的中间态（已登记）。
- T-06 `main.rs` **1570 → 89 行**（`git show c03d244:… | wc -l` / `wc -l`），**< 300，AC-04 达成**。
- T-06 接线未动：`generate_handler!` 的 17 项在当前树与 `c03d244` 的裸名列表**逐字同序**
  （取末段比较，diff 为空）。
- T-06 **逐函数**搬家核对（`/tmp/t06_body_parity.py`，带阳性对照 `python_fallback_allowed`
  必须判 IDENTICAL，否则拒绝判定）：26 项 = 9 IDENTICAL（9 条既有测试）+ 10 BODY-SAME/SIG
  （`fn`→`pub fn`、`HttpClient`→`LocalAgentClient` 等机械改名）+ **7 BODY-CHANGED**，
  7 条逐条 diff 核对后全部对应计划内改动（3 条 sidecar 委托、4 条 preflight 去重）。
  **脚本第一版结论（13 条 BODY-CHANGED）已作废**：没抵消 `client.local_agent_base` →
  `client.base` 这类**函数体内**的机械改名，把拆型算成了逻辑改动。
- T-06 文案不漂的双证据：CJK 字面量普查（baseline `main.rs` 99 条含中文串，93 条在新树中
  **逐字存在**，6 条不存在的**恰好是**带 `{}` 占位符的模板，由 `{noun}` + 固定后缀拼出）；
  渲染由 `message_parity` 的 **16 行** `（流程规格, 失败形态, 历史那句话）` 精确相等表钉住。
- T-06 一处**我自己的判断错误被测试抓住**：`reqwest::StatusCode` 的 `Display` 带 reason
  phrase（`400 Bad Request`）。我先把测试写成期望 `400`，`message_parity` 报不一致；
  回查 `git show HEAD:…commands/account.rs` 确认原实现用 `{}`，即**测试错了不是代码错了**，
  改正期望值并给那条测试改名（原名断言的正是我误以为的那件事）。
- T-06 变异对照 31 条：`config.rs` 12/12、`drain.rs` 8/8、`paths.rs` 7/7、`exit_report` 4/4，
  全部 CAUGHT，撤红后 restore 逐字节复原。其中 **`exit_report` 的脚本自己错了五次**才跑对
  （每次都以「0/4 caught」这个**假结论**呈现，方向是「测试很弱」）；护栏拦下 3 次，
  另 2 次是**护栏挡不住**的「解析成功但解析错了」，详见 evidence §7。
- T-06 两处**被变异逼出来的真问题**（`paths.rs`）：M-07「读不出的文件改 panic」最初存活
  （该分支无测试，补非 UTF-8 用例后被杀）；`locate_takes_the_first_candidate_that_exists`
  原本只让一个候选存在，「取第一个」与「取最后一个」两种实现对它**都成立**（改为让所有
  候选都存在）。
- T-06 范围检查：`git diff --stat c03d244..HEAD` 27 文件（+3142/−1608），删除文件 0；
  `tauri.conf.json`(+1 `bundle.resources`) 与 `src-tauri/Cargo.toml`(+3 `toml="0.9"`) 均落在
  `72095b9` 且在计划 T-06 的提交序列文字内（该序列与 T-07 条目都提过 `bundle.resources`，
  实际落在 T-06 的 config commit，非越界）；`web/dist-desktop/`、`.generated/` 0 命中。
- T-06 发现并登记（不在本 CHG 修）：本仓 M0 时期的整套 Node 工具链（`.github/workflows/
  m0-desktop.yml` + 6 个 `npm` shell script + 2 个 mjs）引用的 `package.json` 不存在，
  **该 CI workflow 在任何分支上都不可能通过**——这也解释了坏掉的 `npm test` 为何一直没被发现
  （CI 在 `bootstrap.sh` 就失败了，从没走到 test 那一步）。
- T-07 逐 commit 实测（`/tmp/t07_matrix.sh`，每个 commit 后**强制重编**再量，非事后补记）：

      commit   | tests | bin warnings
      4b3a7b4  |  42   |  27     <- T-06 收尾基线
      1276e98  |  45   |  29
      b4d4dc4  |  46   |  29
      2afe1d9  |  52   |   7
      d838ccd  |  55   |   6
      14ff67c  |  56   |   6
      6f94cbb  |  59   |   6
      35a2ee9  |  63   |   4

  测试 **42 → 63 单调不减**；告警**先升后降**（A/B1 新增的类型尚无消费者故 +2；B2 接线后
  一次降到 7，D 到 4）。**余下 4 条是 `filesystem/`/`secure_store/`/`system/`/`updater/`
  四个空壳**——CHG-056 §5 明写本 CHG 不动，故告警收口到此为止，**不虚报为 0**。
- T-07 变异矩阵四组（每组先跑未变异阳性对照；锚点必须**恰好命中一次**，否则硬停）：
  CSP 棘轮+金标 6/6 杀、`get_public_config` 6/6 杀、`cloudBaseUrl`+边界 5/5 杀（属 T-08）、
  sidecar 环境变量 **5/7 杀 + 2 存活（预期内）**。逐条明细见 `evidence/task-07-desktop-config.md`。
- T-07 的 **2 条存活变异是登记项而非遗漏**：`Command` 需 `AppHandle` 才能构造，
  「两条 spawn 路径注入同一组变量」是**结构性**性质，`cargo test` 看不见。对策是只有
  **一处** `with_vars` 绑定、两条路径各用一次；运行期补位归 **T-09**（bundled 路径 +
  dev Python fallback 路径各一次真实启动）。**不写成「已覆盖」**。
- T-07 的 D（`35a2ee9`）前提**不是靠读源码断言的**：变量名漂了不是编译错误，而是一个静默
  401 或一个没人调用的端口，故**真启动一次**（`PYTHONPATH=src` + 四个变量，端口 18766）：
  监听 `127.0.0.1:18766`（**不是**默认 8765）；`/healthz` 带对 token **200** / 不带 **401** /
  带错 **401**（三态齐备——缺第三态时「不带得 401」也可能只是「healthz 恰好要求别的什么」）；
  `<scratch>` 下出现 `local-agent.sqlite3`/`logs`/`versions` 而仓库 `.local/` **未被触碰**。
  四次启动断言后自行停止，实测 **0 个残留监听**，未动用户既有的 :8765 dev Agent。
- T-07 一处**自查纠正**：第一版 data-dir 脚本断言 `$SCRATCH/data` 存在，报 `exists=no`。
  查下去是**脚本的问题**——`RuntimePaths.resolve` 的 override 分支把 `<override>` **本身**
  当 data_dir（`runtime/paths.py:64-71`），只有 dev/installed 分支才拼 `data/`。改正后如上。
- T-07 的 AC-04 前置风险**静态闭合**：命令层请求的 6 个 `State<'_, T>` 类型与 `.manage()`
  的 6 次调用**精确相等**，故不留下一个等 T-09 才炸的 "state not managed" 运行时 panic。
- T-07 的 CSP 退役**不靠「删掉即通过」**：退役的是文件里那条**字面量**，不是策略本身。三重
  证据——棘轮 `tauri_conf_carries_no_policy_of_its_own`（禁 `csp` 与 `devCsp` 回归）+
  金标 `the_policy_is_shape_for_shape_the_literal_it_replaced`（把**原字面量逐字**钉进测试）+
  `apply_csp_writes_the_field_a_dev_build_would_otherwise_prefer_over`（钉住 `dev_csp`
  保持 `None`）。即「策略搬家了，它没变」成为一条**永久主张**，改一个指令就必须**故意**改那个字符串。
- T-07 与计划的偏差（1 处，已披露）：计划写「CSP 改为运行时经 `ctx.config_mut()` 注入」，
  `ctx` 指对了但**注入点写浅了**。实测 Tauri 源码：`AppManager` 持有 config 的**拷贝**
  （`manager/mod.rs:39`），`Manager::csp()` 从那份拷贝读（`:369-380`）；`App` 没有
  `config_mut`；`.setup()` 更晚，在**配置声明的窗口全部建好之后**（`app.rs:2524` 然后
  `:2531`）。故唯一可行注入点是 `Builder::run` **之前**对 `Context` 施加，调用链逐行写在
  `bootstrap.rs` 头部。另：计划 T-07 行写「第 17 个命令 `get_public_config`」，实际是**第 18 个**
  `generate_handler!` 条目（既有 17 个位置不变），属计划计数笔误。
- T-07 未覆盖面（已枚举，不以「测试通过」代替）：`generate_handler!` 的**注册本身**测试看不到
  （写了忘注册则 `cargo test` 全绿，只有运行期以「命令不存在」暴露）；`connect_timeout`
  未单独验证（`reqwest` 不把已建成 `Client` 的超时读回来，单独失效需黑洞地址，CI 不稳定）；
  `.setup()` 与 `run()` 的先后**链**、以及 `bindTrustedLocalAgent()` 本身，均归 T-09 真实启动。
- T-08 单个 commit `305d002`（`wt-media-cloud`）：`init.js::cloudBaseUrl()` 不再返回
  `http://127.0.0.1:18080` 改问 `get_public_config`（AC-05），`LocalLogsPage.vue` 不再
  `fetch('…:8765/healthz')` 改走 `createLocalAgentService().health()`。
- T-08 的红是**行为性**的：先只把 `cloudBaseUrl` 导出、函数体一字不改，让失败来自
  `expected 'http://127.0.0.1:18080' to be ''` 与边界规则的 `not to match /127\.0\.0\.1/`，
  而不是「函数不存在」导致的导入失败。变异矩阵 **5/5 杀，0 存活，0 无效**。
- T-08 实测 `cd wt-media-cloud/web && npm test` → **21 files / 101 tests passed（改动前 96）**。
  缓存语义的三条测试各自 `vi.resetModules()` 后重新 import——`init.js` 的缓存是**模块级**的，
  共用一个实例会让它们依赖执行顺序。
- T-08 把 AC-05 的**一次性 grep 升级为常驻断言**：`localAgentBoundary.test.js` 新增
  `carries no hard-coded Cloud address`（`not.toMatch(/18080/)`）与
  `does not let the local-logs page reach the Agent port itself`；两条规则**显式限定文件范围**，
  理由写在测试注释里（全树规则今天就会红，只能靠删规则来通过）——三个残留 18080 站点
  （`AccountsPage.vue`/`ProfilesPage.vue`/`shared/api/http.js`）按用户裁定登记为遗留、本 CHG 不改。
- T-08 一处**值级哨兵被我自查删除**：原想用 `"true"` 覆盖 `development.python_fallback`，
  但它在红跑里**从未触发**（当时的稻草人漏的是 `data_dir` 不是 `python_fallback`），
  且布尔只有两种拼写、都不是哨兵——`"true"` 会为**错误的理由**匹配到将来的任何字段。
  已删除，并把该字段的保证明确划给**键集棘轮**（属 T-07 F 的测试）。
- T-08 未覆盖面（已枚举）：`LocalLogsPage` 的 `health()` 调用**没有单元测试**（只断言了它不再
  直连）——断言「用的是 `health()` 而不是 `status()`」属对实现细节过拟合，且两者都经桥、
  都不越界，无可断言的行为差异；运行期由 T-09 覆盖。
- T-09 四次 Desktop 真实启动（`tools/ac05_desktop_launch.py`，`evidence/artifacts/ac05-run5.log` = PASS）：
  M1 错 CSP / M2 Python fallback / M3 exe 旁 sidecar / M4 加 `ipc:` 的反事实。每 leg 独立
  scratch 端口（**四次都未触碰开发者 :8765 的 dev Agent**）、独立配置与数据目录、退出后
  实测**零残留监听**。
- T-09 探针页**怎么进到真 WebView**：Tauri 的 CSP 只管它自己发出的资源
  （`Manager::get_asset` → `protocol/tauri.rs:182`），**外部 `devUrl` 的页面完全没有策略**——
  所以 `tauri dev` 测不了 CSP，是机制而非配置问题。办法是 `TAURI_CONFIG` 把 `devUrl` 置
  `null`（RFC 7386 里 `null` 即删键），`tauri-codegen` 便会嵌 `frontendDist`
  （`context.rs:178`），得到一个服务于任意页面且带运行期 CSP 的 debug 二进制。
  **未改动任何受版本管理的文件**（desktop 工作树在落盘时 clean）。
- T-09 首次构建曾被误判「没生效」（6.9s、体积不变、二进制里搜不到探针字符串）。判据不是再猜
  一次，而是拿**不存在的 `frontendDist`** 去编——报 `proc macro panicked … this path doesn't
  exist`，证明 `TAURI_CONFIG` 确实抵达 codegen；再用嵌入资源的**键名**（`/index.html`、
  `/probe.js`）确认；原先搜不到是 brotli 压缩所致。
- T-09 **两向 CSP 成立**：错地址 `http://127.0.0.1:19998` → `rejected` + 违规，且违规的
  `originalPolicy` **逐字含该地址**；对地址 → `resolved` 且**零违规**；M4 只加
  `ipc: http://ipc.localhost` 便把 `ipc://` 拒绝从 3 降到 **0**（反事实）。另：
  `localhost:18080` 在**四个 leg 全部被拒**——策略是按**源**精确的，不是「大概放行了回环」。
  生效 header 是 Tauri 渲染后的版本（`connect-src` 逐字来自配置；多出的 `script-src 'self' 'sha256-…'`
  是 Tauri 给自己注入的引导脚本加的，`csp_policy()` 里没有）。
- T-09 T-07 遗留①②④的运行期闭合：①M2/M3 两条 spawn 路径的**四个变量全部由行为反推**
  （HOST/PORT 看监听地址、DATA_DIR 看 scratch 下的 sqlite、token 看 **401/错 401/Desktop 自己 200**
  ——空 token 对一切放行，故 401 是非空 token 已抵达的正向证明），两 leg 的 `ppid` 均等于
  Desktop 的 pid；②四次启动 `get_public_config` 都被调用并返回（漏注册只会以「命令不存在」出现）；
  ④策略**在页面里真的生效**，这正是注入点在 `Builder::run` 之前的唯一运行期信号。
- T-09 **子进程的环境从不读取**：最直接的读法（`ps -wwE -p <pid>`）被自动模式分类器**正确地
  拒绝**——它会把开发者的 Agent runtime token 物化进转写文本。拒绝被接受，**没有绕路**，
  改为上面那套行为判据；D-04 的否定面（token 不经 argv）另有取证：读 argv 断言无 token 形状
  参数，并用一次**植入阳性对照**（种下 `--token 9f2ac41d…`）证明这个检查会失败。
- T-09 三条**实测发现**（均只登记未改）：①`development.python_fallback` 是**装饰键**——
  M1（文件 `true`、环境变量未设）失败，M2（文件 `false`、环境变量 `1`）走 Python 路径，
  真门是 `development_python_fallback_enabled()`（`commands/agent.rs:64`）；②`connect-src`
  不含 `ipc:`，Tauri 的**首选** IPC 传输（`fetch(ipc://localhost/<cmd>)`）每启动被拒 3 次，
  之后全程走 `postMessage` 回退——**既有事实**（退役的 `tauri.conf.json` 字面量同缺此源，
  T-07 逐字保留），修法可只改配置；③`reqwest` 默认读 **macOS 系统代理**
  （`reqwest-0.12.28/Cargo.toml:105,180` → `hyper-util/client-proxy-system`；mac 分支只读
  `HTTPEnable/HTTPProxy/HTTPPort`，**不读 `ExceptionsList`**），故本机回环请求被 Clash 接管
  （裸 connect 挂起 vs 同一个 client 拿到 `502`，两者对照 + `curl -x` 复现同形 502）。
  后果：系统设置里开了代理的 macOS 上，`LocalAgentClient` 的每个请求（含 per-launch token）
  都会交给该代理——本机因代理在回环才「能用」，远端代理会让 Desktop 完全够不到自己的 sidecar。
  这也是 **T-07 遗留③查不下去的真实原因**：`connect_timeout` 要隔离量测必须让 reqwest 不走代理。
- T-09 一处**工具自身的断言错误**被抓住并改正：健康检查最初断言响应体是裸词 `ok`，而 Agent 答的是
  JSON `{"status":"ok",…}`——**是断言错了，不是 Agent 坏了**。同类还有一处：第一版把 CSP 违规
  **平摊计数**，M3 因此误报失败（`ipc://localhost/log_js_error` 的违规被算到 Cloud 的 fetch 头上）；
  改为按前缀分区、只断言被测 URL 自己的 `refusals`，并补 M4 作反事实。
- T-09 一处**文本与证据不同步**的处置：加完 M4 后 docstring/表头/PASS 串仍写「three」，
  改完措辞后**没有重跑**，故 `/tmp/ac05-run4.log` 里的 PASS 行属于旧文本；证据因此改用
  **`evidence/artifacts/ac05-run5.log`**（原 `/tmp/ac05-run5.log`；与当前工具文本一致的那一次），run1–run4 留在记录里作为调试过程。
- T-09 AC-01…AC-11 逐条判据与阳性对照见 `evidence/task-09-acceptance.md`：AC-07 = agent
  **253 tests OK** / desktop 63 passed / web 21 files·101 tests；AC-08 = 两个校验器 0 ERROR
  **且同对校验器在弄坏的副本上 exit=1**；AC-10 = 两 leg（全链 `succeeded`+`progress=100` 且
  checkpoint 已清；中途 SIGKILL → 盘上留 `running` → 重启 `recovering 1 incomplete task(s)`）；
  AC-11 = 常驻测试 + **6/6 CAUGHT / 0 SURVIVED**（含探测器自检）。AC-10 另建实例与 schema
  跑，因为 `claimTask` 无 type/agent 过滤（`repository/mysql_task_store.go:123-126`），
  在开发者的表上起 runner 会打开真实 profile 并把 7 月的积压任务标成失败。
- T-09 未覆盖面（已枚举，不以「测试通过」代替）：**真实前端 bundle 未被驱动**——仓内快照
  `.generated/frontend`（Sep 23 18:26）早于 T-08 的 `init.js` 改动（`305d002`，Sep 24 00:34），
  跑它等于测旧代码，故 `bindTrustedLocalAgent()`/`cloudBaseUrl()` 在真 WebView 里**没有端到端证据**，
  只有 `npm test` 的单元与变异证据；**只测了 macOS**；探针用 `mode:"no-cors"` 故只量策略放行与否、
  不量 HTTP 状态；`profile-create/update/delete` 与 bind 的 Cloud 往返未驱动；
  `connect_timeout` 不闭合（原因如上）。
- T-10 **收尾清理已完成**（T-09 落盘时登记为「待收尾」的三项）：
  - 隔离 Cloud（PID 21224，cwd `/tmp/ac10/root`）`kill -TERM` 停止 → `18199` 无监听、
    进程已退出（实测）。**开发者的 `:18080`（PID 55442）与 dev Agent `:8765`（PID 55443）
    全程未触碰**，停止前后两次 `lsof` 均在。
  - scratch schema `wt_media_cloud_ac10`：**删前先看**——`information_schema` 显示除
    `schema_migrations`（39）外唯一有数据的是 `tasks`（2 行），逐行读出为
    `noop_task` / `agent_id=ac10-agent` / `created_at 2026-09-24 00:55:30`（`succeeded`）与
    `…00:55:31`（`leased`），正是 AC-10 的 LEG A 与 LEG B，确认为本次自己的产物后才 `DROP`。
    删后复查：该库名 0 命中，**且同一条查询能看见 `wt_media_cloud`**（阳性对照，证明 0 是真 0）。
    连接密码从隔离实例自己的 `config/database/primary.toml` 读出后经 `MYSQL_PWD` 传入，
    **不进转写文本、不进任何输出**。
  - `/tmp/ac10/`（39M，含 `server`/`migrate` 二进制与 `root/config`）、`/tmp/wt-ac05/`（四次
    启动的 scratch）等 scratch 目录：随 T-10 清除。
- T-10 **把证据从 `/tmp` 收回本 CHG**：`/tmp` 重启即清空，而 `task-07`/`task-09` 的证据文件
  引用的是 `/tmp/…` 路径——那等于把证据寄存在会消失的地方。收回 `evidence/artifacts/`
  （6 个运行输出，逐字节 `shasum` 两两相等）与 `evidence/tools/`（T-07 的两个脚本，同样逐字节），
  引用逐处改指，原始 `/tmp` 路径保留在括号里作为出处。清单与**唯一一处脱敏**见
  `evidence/artifacts/README.md`：`ac06.out` 里 `bind` 响应打出的 64 位会话 token 已按名
  替换为 `<redacted-local-session-token>`（`diff` 只有那一行），理由是它虽属已退出的一次性
  scratch 实例、不构成在用凭据，但与约束禁止的形状同类；同一份输出里的 cookie **名称**清单
  则刻意保留——AC-06 要证的恰是「值没泄漏」。
- T-09 遗留一项**未收尾、待用户裁定**：**开发者的 Cloud `:18080` 上被误建的一个 `noop_task`**
  （`task_b21340775ace100173202de3`，`pending`，created_at 2026-09-24T00:49:21，AC-10 工具早期
  调试所留）。该行**无害**（`claimTask` 取 `created_at` 最早者，7 月的积压排在其前），
  但它是本次误写，且写开发者的 Cloud 不属本 CHG 授权范围，故**不擅自删**，登记待用户决定。

## 13. DONE Gate

- [x] Scope completed. —— T-01…T-10 全部 DONE（§8）。Add/Modify/Delete 三节逐条有落点：
  Agent 的 `runtime/`+`bootstrap/`+`clients/`+`services/`+`config{,_online}/`、Desktop 的
  bootstrap/config/paths/state/commands/`get_public_config`、Cloud Web 的四个文件（§9），
  删除项的 `config.py`/`log_setup.py`/`runtimes/` 均已消失（T-10 退役名扫描，附分母与阳性对照）。
  超范围的 T-07 遗留③与两处产品决定**未擅自闭合**，登记在 §12 待裁定。
- [x] No blocking `Q-xx`. —— 唯一的 Q-01（生产真实 Cloud 地址）为 `NO`（不阻塞开发默认值与机制实现），
  本次未产生新的 `Q-xx`；三仓实现只依赖已定的部署模型「本机 Cloud」。
- [x] Acceptance matrix all PASS. —— AC-01…AC-11 共 11 条全 PASS，逐条判据见 §10 与
  `evidence/task-09-acceptance.md`（每条附阳性对照；16 项真实链路 exercised，未覆盖项逐条列在
  §覆盖边界，未以「测试通过」替代真实副作用证据）。
- [x] Automated tests passed or justified. —— agent `bash scripts/test.sh` **253 tests OK**（起点 85，
  单调不降）；desktop `cargo test --workspace` **63 passed**；cloud web `npm test`
  **21 files / 101 tests passed**。CI 固定 Python 3.12，未用 3.13+ 语法。
- [x] Manual verification evidence recorded where required. —— T-09 的**四次**真实 Desktop 启动
  与两向 CSP（`evidence/task-09-desktop-launch.md`）；T-07 的真实副作用（带 token 200 / 无 token 401、
  数据目录实际落点）；T-09 三模式各一次真实启动；AC-10 的隔离 Cloud 任务链与 SIGKILL 恢复。
- [x] Diff checked for out-of-scope changes. —— 逐仓枚举了 CHG 区间的完整改动面：agent 的非源码改动
  全部在 §5 内；desktop 的非 Rust 改动（`Cargo.lock`/`Cargo.toml`/`resources/*.toml`/`tauri.conf.json`/
  `scripts/test.sh`/四份文档）全部在 §5 内；cloud 实为 **4 个代码文件**（2 生产 + 2 测试），
  §1/§5/§9 原先写的「两文件」是低估，**本次已按实际改写**（不是改了实现去迁就文档）。
  无范围外的产品行为变更。
- [x] Runtime repositories touched only if listed in scope. —— 三个运行仓均在 §1 的受影响仓库内；
  `wt-media-workspace` 只做治理记录与基线核对，未成为运行时依赖（未新增任何跨仓 import/引用）。
- [x] Required baselines updated. —— 架构基线已按 ADR-0016 在程序启动时改写完毕，本次**逐节核对**
  §5.2/§5.4/§5.5/§5.8 与 ADR-0016 层表（`evidence/task-10-baseline-check.md`），
  其中 §5.4/§5.5 是**机器强制**的一致（R2 白名单 + R10 冻结边棘轮）；**两处偏离如实登记未改**：
  §5.2 的 7 项差集（其中 `modes/`/`generated/` 是基线与实现正面冲突，按纪律留待裁定）、
  §5.8 的 Windows 路径在 `runtime/paths.py` 中无平台分支。三仓 AI 入口文档按实际新布局回写完毕。
- [x] Affected repositories committed independently. —— 一仓一提交：agent `ba179ed`；
  desktop `5c74ca1`（文档）+ `2599819`（注释，与文档分开提交）；cloud `f89467f`；
  workspace 本次收尾提交（治理记录、evidence、状态、快照再生成）。
  全程遵守「移动文件与改逻辑不进同一 commit」。

## 关闭记录（2026-09-24）

- **关闭依据是 DONE Gate，不是用户签收**（如实登记，勿读成后者）：本 CHG 的授权来自用户
  2026-09-23 对执行计划的批准与「继续完成任务」的指示；执行期间**没有**针对本 CHG 的用户
  验收轮次。§13 九项由我逐项签字，判据逐条写在签字行里。若需要用户签收口径，请在此追加。
- **关闭时的验证快照**：agent `bash scripts/test.sh` → **Ran 253 tests OK**（起点 85，全程单调不降）；
  desktop `cargo test --workspace` → **63 passed; 0 failed**，`cargo build` 成功
  （4 条告警全部来自本 CHG 明示不动的空壳模块）；cloud `cd web && npm test` →
  **21 files / 101 tests passed**；`verify_agent_entry.py` → **0 warning**（快照 1668 字符）；
  `verify_delivery_governance.py` → **ok, Active CHG: none**。
- **提交**：agent `ba179ed`（入口文档）及其之前的 T-02…T-08 全链；desktop `5c74ca1`（文档）+
  `2599819`（注释，单独提交）；cloud `f89467f`（入口文档与边界测试登记）；
  workspace 本次收尾提交（§1/§5/§9/§13 回写、evidence 与运行产物、三仓 status、快照再生成）。
- **归档动作**：记录由 `delivery/active/CHG-20260923-056/` 移入 `delivery/completed/`，
  `delivery/LEDGER.md` 的活动行移除并补关闭说明。归档**连带修掉 5 处失效指针**——
  `planned/README.md`（2 处）、`planned/CHG-20260923-053/change.md`、程序总纲（2 处）原先都指向
  `delivery/active/CHG-20260923-056/`；这正是本 CHG 反复处理的「文档落后于事实」形态，
  用带阳性对照的扫描确认 0 残留（模式在别处有命中，故 0 是真 0）。
  快照用 `prepare_ai_workspace.py --no-active` 再生成（该模式由 CHG-055 关闭时补上，
  本次无需再补工具缺口），快照现为 `Active CHG: none` / `Status: NONE`。
- **遗留（四项，随记录归档，不阻塞本次关闭）**：见 §12「Next」——①生产 CSP 是否加 `ipc:`；
  ②回环 client 是否加 `.no_proxy()`；③`modes/`+`generated/` 占位包与基线 §5.2「不保留」的冲突；
  ④T-09 期间在开发者 Cloud `:18080` 上被误建的惰性 `noop_task`（`task_b21340775ace100173202de3`）
  如何处置。四者全是计划明示的范围外事项或新增发现，故不构成未完成的 scope。
- **上述四项遗留的裁定与处置（2026-09-24 追加，由 `CHG-20260924-060` 承接）**：本段是归档后的
  收尾追加，**不改上文原文**。
  - ①生产 CSP 加 `ipc:` → **加**。`wt-media-desktop` `9945f58`。取值是
    `ipc: http://ipc.localhost http://127.0.0.1:18080`，**不是裸 `ipc:`**——`ipc:` 是 scheme-source、
    只匹配 `ipc:` 方案的 URL，而 macOS 上 Tauri 的 IPC fetch 目标是 `http://ipc.localhost`（方案 `http`）。
    真实启动判据：`ipc://` 拒绝数 **3 → 0**（同一二进制、同一探针页，只有那一行配置不同）。
  - ②回环 client 是否加 `.no_proxy()` → **按回环目标禁用，远程 Cloud 保留系统代理**。
    `wt-media-desktop` `d329abc`。`reqwest` 0.12.28 没有「系统代理，但排除这些主机」这个表达
    （`proxy()` 与 `no_proxy()` 都会关掉 `auto_sys_proxy`，且无公开方式设回），
    故拆成两个 client 按 URL 选。
  - ③`modes/`+`generated/` 与基线 §5.2「不保留」的冲突 → **删**。`wt-media-agent` `c33680f`
    （删包 + 收紧 `PLACEHOLDER_PACKAGES`）与 `4d8e9ab`（文档回写）。**基线无需回写**——§5.2 `:1040`
    早已明写不保留这两者，是目录一直没跟上；`adapters/` 不在该名单里，保留。
  - ④开发者 Cloud 上被误建的惰性 `noop_task` → **暂时不处理**。该项**至今未处置**，
    且不在 `CHG-20260924-060` 的授权内（清除它要动开发者的 Cloud，该 CHG 明示不碰）。
  - **一处派生更正**：上文 `Blocked` 记的「T-07 遗留③ `connect_timeout` 隔离量测被②挡住」，
    ②落地后**并未闭合**，应改记为**改写**——回环上的关闭端口由内核立刻 `ECONNREFUSED`
    （实测 405µs），产生不了「SYN 无人应答」这个 `connect_timeout` 存在的条件，**有无代理都如此**。
    准确表述：「回环请求不再被系统代理截获；`connect_timeout` 在回环上仍不可触发。」
  - **本目录一处证据缺口已修补**：`evidence/artifacts/ac05-run5.log`（8975 字节）原先
    **被引用但未入库**——本仓 `.gitignore` 第 3 条 `*.log` 在 `git add -A` 时静默吃掉它。
    引用它的有**六处、四个文件**：`change.md` 两处、`evidence/task-09-desktop-launch.md` 两处、
    `evidence/artifacts/README.md` 与该目录的表格、`status/desktop.md` 各一处。后果是换一个
    clone 打开这份归档，「四次真实启动全部 PASS」这条最强证据会指向一个不存在的文件。
    本次以 `git add -f` 补入，**内容一字未改、结论未改**。补入前已扫过凭证特征
    （Bearer/Authorization/token/password/Cookie/UUID 均无值命中）。
- **明确不在本次关闭内**：本 CHG 未实现日志轮转/清理/脱敏、用户设置 UI、端口就绪通知、
  打包完整性校验与升级回归——这些按程序总纲分属 CHG-057/058/059，**不得**据本记录的 DONE
  推断它们已完成。
