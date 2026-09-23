# CHG-20260923-056 Checkpoint

## 2026-09-23

Completed:
- 三仓结构审计（Desktop/Agent/治理），现状事实录入 change.md §4。
- 用户裁定：融合方案一（ADR-0016 目录 + 新方案内容）；本会话仅 CHG-A；模块分工多文件同步回写。
- 治理工件：程序总纲、CHG-056 change.md、planned 057/058/059 登记、LEDGER 同步。
- T-01：四仓 AI 入口文档各自独立提交（desktop `47a6263`、cloud `3b733ff`、workspace `e0444cd`；agent 上一轮 `d3ab02f` 已提交）；配置格式按 D-05 回写为 TOML（`change.md` §6 D-01/§2/§5/§7/§8 + 程序总纲 §2 + planned CHG-059）；测试基线证据按模板规范化。

Current:
- T-05 Agent AST 边界测试 + 平台 URL 常量化。

Next:
- T-05 `tests/test_dependency_boundaries.py`（R1–R10，含 D-06 两条例外的**单文件粒度**白名单、
  R6 环境变量规则、R10 冻结边集棘轮）、`tests/test_patch_targets.py`（固化
  `local_api.server.urlrequest.urlopen` 等三个 patch 目标）、
  `executors/account_check.py` 的平台 URL 移入 `clients/**` 并公开 `open_url()`。

Blocked:
- None.

Recent verification:
- 审计：源码级 grep/阅读，2026-09-23。
- 基线：`bash scripts/test.sh` → `Ran 85 tests in 1.628s` / `OK`（agent `HEAD=99f408c`）；见 `evidence/task-02-baseline.md`。
- TOML 裁定依据实测复核：Cloud `config/` 13 个 TOML / 0 个 YAML；agent `dependencies = []` 且 `uv.lock` 无 YAML 解析器（阳性对照 `grep -c name uv.lock` = 20）；`tomllib` 在 3.12 起为标准库。

### T-02 完成（agent `99f408c` → `b1233cc`，14 个 commit）

Completed:
- 目标树 29 文件齐备：`runtime/{__init__,constants,version,environment}.py`、
  `clients/{bitbrowser,cloud,bilibili,baijiahao}/` + `platform_identity.py`、
  `services/{browser/cdp,browser/cookies,net/proxy,profile_guard}.py`、
  `local_api/reporting.py`、`storage/sqlite.py`、`runner/{__init__,runner,config,registry}.py`、
  `utils/time.py`、`executors/protocol.py`。
- 撤销：`runtimes/`、`core/`、`constants.py`、`proxy_check.py`、`runner.py`。
- 保留：`cloud_agent_client.py`/`cloud_agent_contract.py` 作为 re-export shim
  （唯一理由：`tests/test_runner_session.py:7` 从旧路径 import 且须零改动；退役于 CHG-B/C）。
- 冻结项全部未动：`sidecar_main.py`、`local_api.server:main`、`storage.migration` 六符号、
  pyproject 四个 console script、`scripts/build_desktop_sidecar.py:115` 的入口路径。
- D-06 登记两条 ADR-0016 层级例外，待 T-05 白名单编码。

Verification（详见 `evidence/task-02-structure-migration.md`）:
- 逐 commit 测试矩阵（`git archive` 导出后各自实跑）：85×10、90×2、94×2，全部 `OK`，无一低于基线。
- 冻结导入 sha256 在 14 个 commit 上恒为 `888113ca…`；`git log -- <该文件>` 计数 0。
- `migrate-storage.sh` ×2（2 applied / 0 applied）+ `verify-health.sh`（裸 `python3` 3.14.6，自占 18765 端口）通过。
- PyInstaller 6.22.2 实构建：PYZ 含 28 个 `wt_media_agent` 模块；`runner`/`executors` 为 0（T-04 后需重新取证）。

Deviations（均已披露，非缩减产出）:
- 计划称 13 个移动 commit，实为 14 个：多出 `94750df`（删既有死 import）、
  `287bca3`（`utils/time` 收口，计划仅列在目标树而未列进提交序列）、`b1233cc`（补两个 `__init__.py`）。
- 计划称 `time.strftime` 重复 4 处，实测 6 处（漏算 `checkpoint_store.py` 2 处），按实测执行。
- 步骤 6/8 合并为一个 commit；步骤 13 中 `runner.py` 的部分并入三拆 commit。
- 发现并**证伪**一个怀疑：`clients/`、`services/` 缺 `__init__.py` 曾疑为 PyInstaller 漏收缺陷，
  实测补前补后 PYZ 清单逐项一致，故仅为一致性修复。

### T-03 完成（agent `b1233cc` → `d870d1f`，10 个 commit）

Completed:
- 新增 `runtime/paths.py`（override/dev/installed 三态，目录懒创建、失败降级）与
  `runtime/config.py`（声明式 `_SPEC` 表，env > file > default 共用一条解析路径）。
- `config/agent.toml` + `config_online/agent.toml` 1:1 镜像（各附 README），
  测试断言两目录文件名与键集一致；运行时代码零处引用 `config_online`。
- 删除零引用 `config.py`；`log_setup.py` 迁入 `runtime/logging.py`（blob 级零改动，`R100`）。
- `local_api/server.py:main` 不再读环境变量，改走 `configure_from(get_config())`。
- 两个超时覆盖移出 `BitBrowserClient`，改由构造注入（`clients/bitbrowser/timeouts.py`），
  `max(default, override)` 语义逐字保留；5 处自建 client 收口到 `bitbrowser_from_config`。
- `storage.migration.default_data_dir()` 委托 `RuntimePaths`（签名与模块路径不变）。
- D-07 登记：配置中的凭据通路收窄为仅环境变量。

Verification（详见 `evidence/task-03-runtime-config.md`）:
- 逐 commit 测试矩阵：107/133/133/145/155/155/163/163/171/172，全部 `OK`，单调不减。
- 冻结导入 sha256 恒为 `888113ca…`（与 T-02 同值），`git log -- <该文件>` 计数 0。
- `src/` 中 `runtime/config.py` 之外的环境变量读取点为 0（阳性对照 2 处命中）；
  死 import 扫描 0（对照植入 2 个未使用 import 均被报出）。
- 变异对照 19/19 全部「基线绿 → 转红 → 还原绿」。
- 真实进程：迁移 ×2 为 `2 applied`/`0 applied`；`verify-health.sh` 打印配置格式日志行并 `health ok`。

Corrections（本会话早先记录被作废或更正之处）:
- **变异对照结论作废重做**：`/tmp/mut.sh` 只定义 `run`/`mut`/`clean` 却未分发 `"$@"`，
  以 `bash` 调用时静默空转，故先前「14 条变异、12 条可判别」的记录不可采信；
  修复分发后重做为 19 条，全部可判别。
- **commit 计数更正**：先前记为「6 个 commit」，实为 10 个（漏记 `9c7d3db`
  `runtime/paths.py`，以及三条收尾 commit）。
- **未覆盖面已枚举**（不以「测试通过」代替）：5 处 executor 的
  `bitbrowser_from_config(get_config())` 调用点与 `LocalApiServer` 的同名默认分支
  均无测试断言其产物来自配置（现有测试一律注入假 client）；「只有 `runtime/config.py`
  读环境变量」目前仍是手工 grep，T-05 的 R6 才变成机器校验。

Scope addition（不在 T-03 计划条目内，已披露）:
- `6f987a7` DIRECTORY_MAP 回写（原计划归 T-10，因该文件是 `CLAUDE.md` 指定入口、
  T-03 后已列 5 个已删模块而提前）；`54e2636` 补 `factory` 测试（此前零覆盖）；
  `d870d1f` 修既有连接泄漏——`with sqlite3.connect(...)` 提交但不关闭，
  `apply_migrations` 每次调用泄漏一个，而它在启动路径上。三站点改 `closing(...)` 后
  `ResourceWarning` 由 20 条回到 0 条。

### T-04 完成（agent `d870d1f` → `7e19622`，4 个 commit）

Completed:
- 新增 `bootstrap/{__init__,app,local,cloud,sidecar}.py`：`app.py` 是**唯一**的生产装配
  入口（显式 9 步有序序列，无注册表/容器/locator），`local`/`cloud`/`sidecar` 三个模式面
  消费同一个 `Components`。
- 5 处自建 client 清零且无新增构造点：4 个 executor 的第三参 `bitbrowser` **必填**
  （可选默认值正是要消灭的注入缝），`LocalApiServer.bitbrowser` 改为关键字必填。
- `runner/registry.py::default_executor_factories(bitbrowser)` 用闭包绑 client；
  `TaskRunner` 第 4 参 `executors` 关键字可选、**默认空** ⇒ 未装配即 fail-closed
  走既有 `no_executor` 路径，不摸 Cloud 与 BitBrowser。
- `CloudAgentClient` 的 `timeout=10` 接配置（`cloud.timeout_seconds`），常量留作默认值。
- `local_main.py`/`cloud_main.py` 成 3 行委托；`app.py`/`test_app.py` 删除；
  `sidecar_main.py` 保留路径与 `local_api_server` 属性名，`main()` 改为 `return sidecar.run()`
  且**不接任何参数**——这是 token 不能经 argv 进入 `ps` 的机制。
- 新增配置键 `agent.id`、`agent.run_runner`（新增 `_as_bool`），两个 config 目录 1:1 同步；
  `run_runner` 默认 **false**（写错命令不会把 Agent 拉起来轮询 Cloud）。
- 新增 `tests/support.py`（`UnusedBitBrowser`：被触碰即断言失败）。

Verification（详见 `evidence/task-04-bootstrap-injection.md`）:
- 逐 commit 测试矩阵：`f7ed012`/`587496b` 184、`3e47985`/`7e19622` 204，全部 `OK`。
- 冻结导入 sha256 恒为 `888113ca…`（与 T-02/T-03 同值），`git log` 计数仍为 1。
- 变异对照 7/7（另 `f7ed012` 5 条）全部三步俱全；`/tmp/t04mut.py` 要求锚点唯一匹配。
- 真实进程三模式（AC-09）：cloud 打印事实 JSON 并 `exit=0`；local `/healthz` 200、
  `profile_count=40`（真实 BitBrowser）；sidecar 401/401/200 且 token 不入 `ps`。
- 冻结脚本 `migrate-storage.sh` ×2 → `2 applied`/`0 applied`，`verify-health.sh` → `health ok`。
- 打包重新取证：PYZ 内 `wt_media_agent.*` 28 → **53**，`runner` 0→4、`executors` 0→8。

Corrections（T-04 内暴露的测试缺口，均已补测而非记成通过）:
- **M-11**：`_as_bool` 把 `"false"/"0"/"off"` 读成真时无测试转红。这些恰是 shell 写这个
  变量的方式，读错会把「别跑」变成「去轮询 Cloud」。补 `RunRunnerSwitchTest`。
- **M-12**：`state.agent_id` 与 `config.agent_id` 的断言当时是**空断言**——配置默认值
  `local-agent-dev` 与 `LocalAgentState` 的 dataclass 默认值恰好相同。改为显式配
  `agent-7f3c` 后再比。

Deviations（已披露）:
- 计划写「sidecar_main 读四个受控环境变量」，实际读环境变量的动作仍在
  `runtime/config.py`（四个都是 `_SPEC` 已登记的键），sidecar 只消费解析结果。
  理由：R6 要求全 `src/` 只有该模块读环境变量，否则 T-05 的 AST 规则会立刻把
  `sidecar_main.py` 列为违规。行为与计划等价。
- 打包产物未重签时启动失败（`different Team IDs`）：与 T-04 改动无关的既存问题，
  登记归 CHG-D(059)，且**不作为 T-04 的通过条件**（T-04 只主张模块集合正确）。

Open（未覆盖面，已枚举）:
- `bootstrap/local.py` 无单元测试（只有真实进程取证）；`local_api/server.py:main` 的
  「不传 `--host/--port` 时取配置值」分支无测试；`bootstrap/sidecar.py` 的
  `run_runner=true` 守护线程分支未被真实进程走过（AC-10 归 T-09）。
