# Evidence: Agent 结构迁移（T-02 纯移动）

- CHG: `CHG-20260923-056`
- Task: `T-02`
- Date: 2026-09-23
- Type: diff
- Status: PASS

## Purpose

证明 T-02 的目录重构**只搬不改**：ADR-0016 的目标布局落地，且

1. 每个 commit 都过测试闸门（N ≥ 85 且 `OK`）；
2. 冻结导入未被破坏——`tests/test_runner_session.py` 逐字节未改，
   `TaskRunner(client, store, config)` 三位置参构造不变；
3. 冻结模块路径与符号未被破坏（`sidecar_main.py`、`local_api.server:main`、
   `storage.migration` 六符号、pyproject 四个 console script）；
4. 被删目录确已消失，且**只有已登记的例外**越过 ADR-0016 的层级下降序。

## Method

### 1. 提交序列

`wt-media-agent`，`main`，基线 `99f408c`（T-01 收尾）→ `b1233cc`，共 **14** 个 commit：

| # | commit | 内容 |
|---|---|---|
| 1 | `924e057` | `constants.py` → `runtime/`；`__version__` 提到 `runtime/version.py` |
| 2 | `4584591` | `runtimes/bitbrowser.py` → `clients/bitbrowser/` 包 |
| 3 | `86ed17b` | `runtimes/cdp_client.py` → `services/browser/cdp.py` |
| 4 | `b6dffc6` | `runtimes/environment.py` → `runtime/`；`runtimes/` 撤销 |
| 5 | `51f2ee4` | Cloud 客户端 → `clients/cloud/`，旧路径留 re-export shim |
| 6 | `5d3d6d2` | 代理解析与连通检查 → `services/net/proxy.py` |
| 7 | `233cb60` | `core/profile_guard.py` → `services/`；`core/` 撤销 |
| 8 | `da7183a` | `server.py` 响应装配辅助 → `local_api/reporting.py` |
| 9 | `daeb913` | 平台身份识别 + Cookie 读取 → `clients/` 与 `services/browser/` |
| 10 | `379a700` | `runner.py` 三拆为 `runner/` 包；`Executor` 协议下移 `executors/` |
| 11 | `4fff9cf` | `checkpoint_store` 连接策略 → `storage/sqlite.py` |
| 12 | `94750df` | 删除 5 个既有死 import |
| 13 | `287bca3` | 时间戳格式收口 → `utils/time.py` |
| 14 | `b1233cc` | 补齐 `clients/`、`services/` 的 `__init__.py` |

计划写「13 个移动 commit」（步骤 6 与 8 合并为一个）。实际 14 个：第 11 步之后
多出 12～14 三个非移动 commit（死 import、时间戳收口、`__init__.py` 补齐），
三者都独立成 commit 而未混进移动，理由见各 commit 正文。

### 2. 逐 commit 测试矩阵

用 `git archive` 把每个 commit 导出到 `/tmp` 独立目录后各自实跑，而非采信执行
当时的记录：

```bash
for c in $(git log --format=%h --reverse 99f408c..HEAD); do
  d=/tmp/t02-matrix/$c; mkdir -p $d; git archive $c | tar -x -C $d
  (cd $d && PYTHONPATH=src "$VENV_PY" -m unittest discover -s tests)
done
```

### 3. 冻结导入

```bash
for c in $(git log --format=%h --reverse 99f408c..HEAD); do
  git show "${c}:tests/test_runner_session.py" | shasum -a 256
done
git log --oneline 99f408c..HEAD -- tests/test_runner_session.py | wc -l
```

### 4. 层级边枚举

自写 AST 脚本：对 `src/wt_media_agent/**/*.py` 收集 `Import`/`ImportFrom`
（仅 `wt_media_agent.*`），按包路径首段归层，输出全部 `(源层 → 目标层)` 边。

### 5. 冻结路径与符号

```python
for mod, names in [("wt_media_agent.storage.migration", [...6 符号...]),
                   ("wt_media_agent.local_api.server", ["main"]),
                   ("wt_media_agent.sidecar_main", ["local_api_server", "main"]),
                   ("wt_media_agent.runner", ["TaskRunner", "TaskRunnerConfig"])]:
    ...
```

### 6. 打包产物

按 `scripts/build_desktop_sidecar.py:110-116` 同参数实跑 PyInstaller 6.22.2，
再用 `PyInstaller.archive.readers.CArchiveReader` 读**内嵌 PYZ**（不是外层
CArchive TOC）列出模块清单。

## Expected

1. 14 个 commit 逐个 `Ran N tests` 且 `OK`，`N ≥ 85`；
2. 冻结测试 sha256 在 14 个 commit 上恒为同一值，且该值 ≠ 空串 sha256；
3. 冻结路径与符号全部存在；`runtimes/`、`core/`、`constants.py`、
   `proxy_check.py`、`runner.py` 均已消失；
4. 越过层级下降序的边**只有已登记的两条**；
5. 打包产物含全部新包。

## Actual

### 1. 逐 commit 测试矩阵（PASS）

| commit | tests | result |
|---|---|---|
| `924e057` | 85 | OK |
| `4584591` | 85 | OK |
| `86ed17b` | 85 | OK |
| `b6dffc6` | 85 | OK |
| `51f2ee4` | 85 | OK |
| `5d3d6d2` | 85 | OK |
| `233cb60` | 85 | OK |
| `da7183a` | 85 | OK |
| `daeb913` | 85 | OK |
| `379a700` | 85 | OK |
| `4fff9cf` | 90 | OK |
| `94750df` | 90 | OK |
| `287bca3` | 94 | OK |
| `b1233cc` | 94 | OK |

无一个 commit 低于基线 85。增量来源：`storage/sqlite` +5（`test_storage_sqlite.py`）、
`utils/time` +4（`test_utils_time.py`）。

### 2. 冻结导入（PASS）

`tests/test_runner_session.py` 的 sha256 在全部 14 个 commit 上恒为
`888113caaf5bb970fa0637ffebac34e304f9ffad0a74508e9ea49fe9e59bb4b0`，
与基线 `99f408c` 相同；`git log -- tests/test_runner_session.py` 计数 **0**。

阳性对照：空串 sha256 为 `e3b0c442...`。第一次执行时因未给 `"${c}:path"`
加引号，shell 把 `:t` 当参数展开，`git show` 全部失败、14 行输出全是空串哈希，
看起来却像「14 个 commit 完全一致」。补引号后重跑得以上真实值，并用空串哈希
确认本次提取确实取到了内容。

### 3. 目录与符号（PASS）

- 目标树 29 个文件全部存在（含 `storage/sqlite.py`、`utils/time.py`、
  `executors/protocol.py`、`runner/{__init__,runner,config,registry}.py`）。
- 已消失：`runtimes/`、`core/`、`constants.py`、`proxy_check.py`、`runner.py`。
- 例外保留：`cloud_agent_client.py` / `cloud_agent_contract.py` 作为 re-export
  shim 存在，docstring 注明「退役于 CHG-B/C」。保留的唯一理由是
  `tests/test_runner_session.py:7` 从旧路径 import `SessionInvalidError`，而该
  文件必须零改动。
- 冻结符号：`storage.migration` 六符号、`local_api.server:main`、
  `sidecar_main:{local_api_server,main}`、`runner:{TaskRunner,TaskRunnerConfig}`
  全部 `hasattr` 为真。
- `pyproject.toml` 四个 console script 一字未改；
  `scripts/build_desktop_sidecar.py:115` 仍以 `sidecar_main.py` 为 PyInstaller 入口。

### 4. 层级边全集（PASS，附两条已登记例外）

共 **22** 条跨层边。多数落在 ADR-0016 的下降序
`bootstrap → runner → executors → {clients, services, storage}`（`runtime/`、
`utils/` 为横切与叶子，可从任意层引用）：

| 边 | 站点数 | 判定 |
|---|---|---|
| `runner → {clients, executors, runtime, storage, utils}` | 14 | 下降序，合规 |
| `executors → {clients, runtime, services}` | 16 | 下降序 + 横切，合规 |
| `local_api → {clients, runtime, services, storage}` | 8 | `local_api/` 与 `runner` 同级，可及下层，合规 |
| `storage → utils` | 1 | utils 为叶子，合规 |
| `utils → *` | 0 | utils 无出边，确为叶子 |
| **`runtime → clients`** | **1** | **例外 1** |
| **`clients → services`** | **1** | **例外 2** |

- 例外 1：`runtime/environment.py → clients.bitbrowser`。ADR-0016 §1 称
  `runtime/` 不引用业务层，§4 却把环境探测明确指派给 `runtime/environment.py`；
  该模块必须 import `clients.bitbrowser` 才能区分 `BitBrowserIdentityError`
  （→ `identity_unverifiable`）与 `BitBrowserError`（→ `unreachable`），
  此行为有测试覆盖。取 §4 这一更具体的规定，并据此要求 T-05 的白名单把许可
  **收窄为「仅 `runtime/environment.py` 可 import `clients.bitbrowser`」**，
  而非放开整条 `runtime → clients` 方向。
- 例外 2：`clients/bilibili/identity.py → services.browser`。ADR-0016 §1 把
  `{clients, services, storage}` 列为无序集合，§3 的明禁边只有
  `clients→executors`、`services→executors`、`utils→业务层`，故同级边被允许。
  已在模块 docstring 记录，并排队进 T-05 白名单显式编码，而非默认放行。

未观测到任何 `services→executors`、`clients→executors`、`utils→业务层` 边。

`executors → runtime.constants`（4 站点）与 `executors → services.net.proxy`
（1 站点）一度被怀疑越界，核对 ADR-0016 后确认合规：`runtime/` 是横切层，
`services/` 在下降序上位于 `executors` 之下。

### 5. 打包产物（PASS，且证伪一个怀疑）

按打包脚本同参数实跑 PyInstaller 6.22.2，读内嵌 PYZ：

- PYZ 模块总数 188，其中 `wt_media_agent.*` **28** 个；
- `clients` 9 个（含 `baijiahao`、`bilibili`、`bitbrowser` 及其子模块、
  `platform_identity`）、`services` 6 个（含 `browser.cdp`、`browser.cookies`、
  `net.proxy`）、`utils` 2 个、`runtime` 3 个、`storage` 3 个、`local_api` 4 个；
- 产物二进制跑到 `socketserver.bind` 才因 8765 被 dev agent 占用而失败
  （`OSError: [Errno 48] Address already in use`），说明 `server.py` 的模块级
  import 在冻结环境内全部解析成功。

`clients/` 与 `services/` 建包时漏了顶层 `__init__.py`，靠 PEP 420 隐式命名空间包
工作。我曾怀疑这会让 PyInstaller 漏收（一个「单测全过、打出的包在客户机崩」的
故障），**实测证伪**：补 `__init__.py` 前后两次构建的 PYZ 清单逐项一致（均 28 / 17），
故 `b1233cc` 只是一致性修复，不修任何故障。

顺带得到一条对 T-04 有用的事实：当前产物里 **`runner` 与 `executors` 均为 0 个模块**
——`sidecar_main` 只经 `local_api.server`，够不到它们。T-04 让 sidecar 委托
`bootstrap` 后该模块集合会变，届时需重新取证。

### 6. 包完整性（PASS）

18 个包目录全部具备 `__init__.py`（此前 `clients/`、`services/` 为仅有的两个例外）。

## Follow-Up

- **计划步骤合并，已披露**：计划的步骤 6/8（proxy + proxy-parse）同属一个新模块，
  合并为一个 commit 以免模块半填充；步骤 13（删重复 import）中 `runner.py` 的
  部分并入三拆 commit（`379a700`），因为把已证惰性的 import 搬进新模块等于在新
  文件里植入死代码。剩余 5 个既有死 import 另成 `94750df`。
- **计划计数与实测不符**：计划称 `time.strftime` 重复「4 处」，实测 6 处
  （计划漏算 `checkpoint_store.py` 的 2 处），按实测执行（`287bca3`）。
- 上述两条为 T-02 内自行判断的范围调整，非缩减：未删任何计划要求的产出。
- 待 T-05 编码进白名单的两条例外见 §4；`runtime → clients` 必须收窄到单文件粒度。
- 待 T-04 重新取证打包产物的模块集合（`runner`/`executors` 应首次进包）。
