# Evidence: Agent Bootstrap、执行器注入与真实入口（T-04）

- CHG: `CHG-20260923-056`
- Task: `T-04`
- Date: 2026-09-23
- Type: test + mutation + command + real-process + packaging
- Status: PASS

## Purpose

证明 T-04 达成了两件事，并且**没有顺手改变既有行为**：

1. **Agent 可以脱离 Desktop 独立启动并跑通真实装配**：`bootstrap/app.py` 成为
   唯一的生产装配入口，`local` / `cloud` / `sidecar` 三个模式首次真的能起。
2. **「谁构造客户端」这件事被收走**：执行器与 `LocalApiServer` 都不再能从环境
   变量里自取一个 BitBrowser client；未装配的 runner **fail-closed**。

具体判据：

- 5 处自建 client（4 个 executor 共 5 个类 + `LocalApiServer` 的默认分支）清零；
- `runner/runner.py` 不再自建默认注册表，未注入即走既有 `no_executor` 路径；
- `CloudAgentClient` 的 `timeout=10` 接配置；
- sidecar 的 token 只经环境变量，`ps` 里不可见；
- 三个模式各有一次真实进程启动与健康输出，打包产物重新取证。

## Method

### 1. 提交序列

`wt-media-agent`，`main`，基线 `d870d1f`（T-03 收尾）→ `7e19622`，共 **4** 个 commit：

| # | commit | 内容 | 测试 |
|---|---|---|---|
| 1 | `f7ed012` | 执行器注入链：4 个执行器必填第三参、registry 闭包绑 client、runner 收注入注册表 | 184 OK |
| 2 | `587496b` | 纯移动：4 个 `LocalApiServer` 测试迁出 `test_app.py` | 184 OK |
| 3 | `3e47985` | `bootstrap/` 包、三个模式入口、`LocalApiServer` 必填 client、`CloudAgentClient` 超时接配置、两个配置键、`app.py` 删除、测试重组 | 204 OK |
| 4 | `7e19622` | docs：`DIRECTORY_MAP.md` 按 T-04 后布局回写 | 204 OK |

第 2 个 commit 单独存在是**纪律要求**：「移动文件」与「改逻辑」不进同一 commit。
若合并，`test_app.py` 被删的 diff 会盖住 `LocalApiServer` 签名变更的 diff。

逐 commit 测试矩阵（`git archive` 导出后在副本内实跑）：

| commit | 结果 |
|---|---|
| `f7ed012` | `Ran 184 tests` / `OK` |
| `587496b` | `Ran 184 tests` / `OK` |
| `3e47985` | `Ran 204 tests` / `OK` |
| `7e19622` | `Ran 204 tests` / `OK` |

单调不减（184 → 204）；基线 184 ≥ T-02 的 94、T-03 的 172。

### 2. 冻结项逐字节未动

`tests/test_runner_session.py` 在 T-04 的 4 个 commit 上 sha256 前三段恒为
`888113ca…`，与 T-02、T-03 记录同值：

```
d870d1f  888113caaf5bb970   ← T-03 收尾
f7ed012  888113caaf5bb970
587496b  888113caaf5bb970
3e47985  888113caaf5bb970
7e19622  888113caaf5bb970
```

`git log -- tests/test_runner_session.py` 至今只命中 `1e3e96f`（本 CHG 之前）。

其它冻结项：`sidecar_main.py` 路径与 `local_api_server` 属性名保留；
`local_api/server.py:main` 符号保留；`storage/migration.py` 六符号未动；
pyproject 四个 console script 未动。

### 3. 默认注册表不再是隐式行为（变异对照）

`runner/runner.py` 第 4 参 `executors` 关键字可选、默认空字典：

```python
self._executors: dict[str, ExecutorFactory] = dict(executors or {})
```

未装配时走既有 `runner.py:107-110` 的 `no_executor` 路径 —— **fail-closed**。
`tests/test_runner_registry.py` 用 `_poll_once` 驱动真实分派路径断言：
`report_task("task-1", "agent-1", "failed", 0, "no_executor")` 且
`remove_checkpoint` 未被调用。

### 4. 变异对照

`/tmp/t04mut.py`：每条变异先跑一次基线（非绿则拒绝记录）、植入后跑、还原后再跑。
锚点必须唯一匹配，否则硬报错 —— 静默空转的变异不得被记成「测试抓住了」。

结果 **7/7 全部「基线绿 → 转红 → 还原绿」**（另加 `f7ed012` 的 5 条，见 §5）：

| # | 变异 | 命中 |
|---|---|---|
| M-6 | 装配时给 registry 传一个**新建的** `BitBrowserClient` 而非第 4 步那个 | `test_bootstrap.py::test_every_browser_driven_executor_shares_the_assembled_client` |
| M-7 | `cloud.py` 的 `if not run_runner: return 0` 改成 `if False:` | `test_bootstrap.py::test_cloud_mode_reports_and_returns_without_starting_the_runner` |
| M-8 | `LocalApiServer` 的 `bitbrowser` 重新给默认值 `None` | `test_local_api_server.py::test_the_bitbrowser_client_must_be_supplied` |
| M-9 | `CloudAgentClient` 的 `timeout=self.timeout` 改回 `timeout=10` | `test_cloud_agent_client.py::test_the_configured_timeout_reaches_the_request` |
| M-10 | `bootstrap/sidecar.py` 传 `auth_token=""` 而非配置值 | `test_sidecar_entry.py::test_the_four_controlled_variables_reach_the_api_surface` |
| M-11 | `_as_bool` 把 `"false"`/`"0"`/`"off"` 读成真 | `test_runtime_config.py::RunRunnerSwitchTest` |
| M-12 | 装配里 `state = LocalAgentState()`（忽略配置的 agent_id） | `test_bootstrap.py::test_the_state_reports_the_configured_agent_id` |

**M-11 与 M-12 第一次跑出来是「不可判别」，暴露了两个真实缺口，不是形式问题：**

- M-11：脚本写这个变量的方式恰恰是 `WT_MEDIA_AGENT_RUN_RUNNER=false`。若把假值读成
  真，一个说「别跑」的变量会把 Agent 拉起来去轮询 Cloud。原测试只用 `"true"`，
  补 `RunRunnerSwitchTest` 覆盖六种假值拼写与一种非法拼写。
- M-12：原断言把 `state.agent_id` 与 `config.agent_id` 比较，而配置默认值
  `local-agent-dev` 与 `LocalAgentState` 的 dataclass 默认值恰好相同 —— **空断言**。
  改为显式配 `WT_MEDIA_AGENT_ID=agent-7f3c` 后再比。

`f7ed012` 的 5 条（执行器注入链）同样全部可判别，其中 M-2 第一次植入时脚本用
`str.partition` 定位第二处出现，实际改到了第一处，报出的失败项也落在读执行器 ——
**属脚本写错而非测试有洞**，改为按 `index` 定位后失败项正确落在 `CookieWriteExecutor`。

### 5. 真实进程（AC-09 三模式）

命令与输出原文见下方；环境：BitBrowser :54345、本机 macOS 15.x。

**cloud（默认只报告）**

```
$ WT_MEDIA_AGENT_DATA_DIR=/tmp/t04run/data python -m wt_media_agent.cloud_main
{"agent_id": "local-agent-dev", "cloud_base_url": "http://127.0.0.1:18080",
 "data_dir": "/tmp/t04run/data", "database_path": "/tmp/t04run/data/local-agent.sqlite3",
 "environment": "development", "log_file": "", "mode": "cloud",
 "run_runner": false, "version": "0.2.2"}
exit=0
```

无任何出站请求：未启动 runner，未 claim，未 heartbeat。`runtime_token` 不在输出中
（有测试钉住：`test_the_token_stays_out_of_the_environment_facts`）。

**local**

```
$ WT_MEDIA_LOCAL_API_HOST=127.0.0.1 WT_MEDIA_LOCAL_API_PORT=18766 \
    WT_MEDIA_AGENT_DATA_DIR=/tmp/t04run/data python -m wt_media_agent.local_main
healthz: {"status":"ok","service":"wt-media-agent","mode":"m1"}
status : {'agent_id': 'local-agent-dev', 'status': 'idle', 'bitbrowser_status': 'normal'}
log    : local_api.status.success duration_ms=1473 bitbrowser_status=normal
         main_user_id=2c9bc06191effa4e0191f9589996619f profile_count=40
```

注意 `profile_count=40` 与 `main_user_id` 有值：这是**真实的 BitBrowser**，不是 mock。
装配第 4 步构造的 client 真的连上了本机 BitBrowser 并核验了主身份。

**sidecar（Desktop 传的四个受控环境变量）**

```
$ WT_MEDIA_LOCAL_API_HOST=127.0.0.1 WT_MEDIA_LOCAL_API_PORT=18770 \
  WT_MEDIA_AGENT_RUNTIME_TOKEN=launch-token-e2e WT_MEDIA_AGENT_DATA_DIR=/tmp/t04run/sc4 \
    python -m wt_media_agent.sidecar_main
no token        -> 401
wrong token     -> 401
correct token   -> 200 body={"status":"ok","service":"wt-media-agent","mode":"m1"}
status no token -> 401
status w/ token -> 200
argv: .venv/bin/python -m wt_media_agent.sidecar_main     ← 无 token 踪迹
data dir: local-agent.sqlite3 local-agent.sqlite3-shm local-agent.sqlite3-wal logs versions
```

token 走环境变量、四变量全部生效；`ps -o command=` 里看不到 token（AC-03）。

### 6. 冻结入口脚本

```
$ bash scripts/migrate-storage.sh --data-dir /tmp/t04run/mig
storage migration ok: 2 applied, 2 total
$ bash scripts/migrate-storage.sh --data-dir /tmp/t04run/mig
storage migration ok: 0 applied, 2 total
$ bash scripts/verify-health.sh
2026-09-23T23:13:53 [INFO] __main__: wt-media-agent local API listening on 127.0.0.1:18765
wt-media-agent health ok
```

表落盘核验：`['agent_metadata', 'offline_results', 'schema_migrations', 'sqlite_sequence', 'task_checkpoints']`。

### 7. 静态扫描（含阳性对照）

- **环境变量读取点**：`grep -rn "os\.environ\|os\.getenv" src/` → 只有
  `runtime/config.py:291` 一处真实读取（`:330` 是 docstring 里提到该词）。
  同一命令在 T-03 后的命中数相同，故 T-04 没有新增读取点。
- **死 import**：AST 扫描 `src/` → 0 条。阳性对照：临时目录里植入
  `import os`（`json` 被使用、`os` 未使用）→ 扫描器报出
  `/tmp/ctl04/planted.py:2: unused import os`，证明扫描器确实在工作而非空转。

### 8. 打包产物重新取证

`scripts/build_desktop_sidecar.py`（PyInstaller 6.22.2，`--onefile`）实构建成功：

```
$ python scripts/build_desktop_sidecar.py --output-dir /tmp/t04build --manifest /tmp/t04build/manifest.json
/tmp/t04build/wt-media-agent-aarch64-apple-darwin
{"component": "wt-media-agent", "version": "0.2.2", "target": "aarch64-apple-darwin",
 "filename": "wt-media-agent-aarch64-apple-darwin",
 "sha256": "5399355c83b28d8b5b8fa868a0b92bf68996985ca0e113d272a007c5e44550a6"}
```

PYZ 内 `wt_media_agent` 模块清单（`CArchiveReader` 取出 `PYZ.pyz` 后用
`ZlibArchiveReader` 读 toc）：

| 前缀 | T-02 取证 | T-04 |
|---|---|---|
| `wt_media_agent.*` 合计 | 28 | **53** |
| `wt_media_agent.runner` | 0 | 4 |
| `wt_media_agent.executors` | 0 | 8 |
| `wt_media_agent.bootstrap` | — | 3（`__init__`/`app`/`sidecar`） |
| `wt_media_agent.local_api` | 2 | 4 |
| `wt_media_agent.clients` | — | 14 |
| `wt_media_agent.services` | — | 6 |

T-02 遗留的「sidecar 只经 `local_api.server`，够不到 `runner`/`executors`」已消除。
`bootstrap.local` / `bootstrap.cloud` 不在包内是**预期的**：`sidecar_main` 只 import
`bootstrap.sidecar`，PyInstaller 不会收未被引用的兄弟模块。

## Expected

- 5 处自建 client 全部消失，且没有新的构造点；
- 未装配的 runner fail-closed；
- 三个模式各自能起并给出健康输出；
- 测试数 ≥ 184 且 OK；冻结文件逐字节未改；
- 产物里 `runner`/`executors` 进包。

## Actual

全部达成，但有三项需要如实记录：

### 8.1 打包产物直接运行失败（既存问题，非本 Task 引入）

未重签的产物启动即失败：

```
[PYI-4734:ERROR] Failed to load Python shared library
  '/var/folders/.../_MEI.../libpython3.14.dylib': ...
  (code signature in ... not valid for use in process:
   mapping process and mapped file (non-platform) have different Team IDs)
```

产物签名为 `flags=0x10002(adhoc,runtime)`（含 hardened runtime 位）而 Team ID 为空，
故加载内嵌的 adhoc 签名 python 动态库被拒。`codesign --force --sign -` 重签后可正常运行：

```
$ codesign --force --sign - wt-media-agent-aarch64-apple-darwin
$ WT_MEDIA_LOCAL_API_HOST=127.0.0.1 WT_MEDIA_LOCAL_API_PORT=18772 \
    WT_MEDIA_AGENT_RUNTIME_TOKEN=frozen-token WT_MEDIA_AGENT_DATA_DIR=/tmp/t04run/frozen2 \
    ./wt-media-agent-aarch64-apple-darwin
code: 200  body: {"status":"ok","service":"wt-media-agent","mode":"m1"}
data: local-agent.sqlite3 logs versions
```

**判断**：这与 T-04 的改动无关（改动没有触及打包脚本或签名），是打包/产物校验
范围的问题，按计划归 CHG-D(059)。此处只记录不修，并且**不把它当作 T-04 的通过条件**
—— T-04 的冻结产物判据只主张「模块集合正确」，运行判据由源码态 sidecar 承担。

### 8.2 未覆盖面（枚举，不以「测试通过」代替）

- **`bootstrap/local.py` 无单元测试**。`wt-media-local-agent` 那条路径只有 §5 的
  真实进程取证。它与 `bootstrap/sidecar.py` 结构同构（都只差一行开关分支），
  但这是现状而非已覆盖。同理 `bootstrap/local.py` 的 `serve()` 调用参数只有
  sidecar 一侧被断言。
- **`local_api/server.py:main` 的 `--host`/`--port` 默认值改用配置**（`""` / `0`
  表示「未指定，取配置」）。`scripts/verify-health.sh` 显式传两个参数故不受影响，
  但「不传参数时取配置值」本身没有测试；真实取证走的是显式传参那条。
- **`_as_bool` 只覆盖 English 拼写**，`"是"/"真"` 之类不在集合内会报 `ConfigError`。
  这是有意选择（报错优于猜），但未在文档外记录。
- `bootstrap/sidecar.py` 的 runner 守护线程分支（`run_runner` 为真）**未被真实进程
  走过**：AC-10 的任务链路整体归 T-09。
- 打包产物运行失败（§8.1）在 T-04 内未修复。

### 8.3 一处偏离计划的实现选择

计划写「`sidecar_main.py` 保持原位与 `local_api_server` 模块属性名，改为读四个受控
环境变量后委托 `bootstrap.sidecar`」。实际实现里**读环境变量的动作不在 sidecar_main**，
而在 `runtime/config.py` —— 四个变量都是 `_SPEC` 里已登记的键
（`local_api.host` / `local_api.port` / `runtime_token` / `agent.data_dir`），
sidecar 只是消费解析结果。这样做的理由是 R6（全 `src/` 只有 `runtime/config.py`
读环境变量）：若 sidecar_main 自己读一遍，T-05 的 AST 规则立刻会把 `sidecar_main.py`
列为违规。行为与计划等价，且少一处读取点。

## Follow-Up

- **`config/agent.toml` 与 `config_online/agent.toml` 各新增两个键**
  （`agent.id`、`agent.run_runner`），两侧注释同步。镜像测试
  （`test_runtime_config.py::ConfigMirrorTest`）仍绿。
- **`agent.run_runner` 是新的行为开关**，默认 `false`。`scripts/start-health.sh`
  与 m2b 目前不设它，故它们的 Agent 不会轮询 Cloud —— 与 T-04 之前一致
  （此前根本没有生产入口构造 runner）。T-09 的 AC-10 需要显式打开它。
- **`bootstrap/local.py` 的测试缺口**（§8.2 第 1 条）留给 T-09/T-10 评估是否补。
- **打包签名问题**（§8.1）进 CHG-D(059) 的范围，本 Task 只登记。
- **`clients/bitbrowser/__init__.py` 的 docstring 自相矛盾**（T-03 遗留③）仍在，
  由 T-05 的 R1/R2 白名单收口。
- **`local_api/server.py:340` 的 `check_items` 契约分歧**（计划细节 11）未动。
