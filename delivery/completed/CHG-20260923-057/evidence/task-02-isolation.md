# Evidence: T-02 Agent 测试目录隔离

- CHG: `CHG-20260923-057`
- Task: `T-02`
- Date: 2026-09-24
- Type: command
- Status: PASS
- Commit: `wt-media-agent` `7382fed`（test-only；`src/` 零改动）

## Purpose

让「测试不得把检出目录当运行时目录」（用户裁定十一 + 架构基线 §5.13）成为机器守的规则，
并给出测试拿临时运行树的唯一入口。这是 **T-03 的前置**：T-03 让 dev 默认真落盘后，
任何解析到真实检出的用例都会写进开发者自己的树、在干净克隆上则创建它。

## Method

```bash
# 0. 先量：跑套件前后，本机 .local/ 的路径/大小/mtime
find .local -mindepth 1 -printf '%p %s %T@\n' | sort > /tmp/before.txt
bash scripts/test.sh > /tmp/suite.out 2>&1
find .local -mindepth 1 -printf '%p %s %T@\n' | sort > /tmp/after.txt
diff /tmp/before.txt /tmp/after.txt

# 1. 干净克隆对照（不动开发者数据；开发者的 dev Agent 可能正开着 SQLite）
git archive HEAD | tar -x -C "$TMP"
cd "$TMP" && bash scripts/test.sh && ls -a            # .local/ 是否出现

# 2. 先红：新增 tests/test_test_isolation.py 的规则，扫 tests/test_*.py
PYTHONPATH=tests .venv/bin/python -m unittest discover -s tests -p 'test_test_isolation.py'

# 3. 最小实现后复跑；并做阳性对照（探针模块 + scripts/test.sh 的变异探针）
bash scripts/test.sh; echo "exit=$?"                  # 不经管道，取真 exit
```

**定向调用的可用形式**（本 Task 实测，后续 Task 沿用）：

```bash
PYTHONPATH=tests .venv/bin/python -m unittest tests.<模块>            # 需要 PYTHONPATH=tests
PYTHONPATH=tests .venv/bin/python -m unittest discover -s tests -p 'test_<模块>.py'
```

## Expected

1. 规则在修之前**红**，命中点恰好是 `tests/test_storage_migration_paths.py` 对真实检出的那条断言。
2. 修后转绿，且**不删断言**——同一条属性（dev 留在自己树内、不落 `$HOME`）仍在被断言。
3. 套件总数只增不减；`scripts/test.sh` 正常 `exit=0`，在有人写检出目录时 `exit=1` 并**点名路径**。
4. 所有否定结论配阳性对照；对照臂不出红即记「对照无效」，不得记为通过。

## Actual

**1. 先量后改：今天的隔离是真的，本 Task 是预防性的**

套件跑完后，本机 `.local/` 的路径、字节数、mtime **逐行全等**（`diff` 无输出）。
再用 `git archive HEAD` 造一棵**干净检出**（无 `.local/`，且不碰在跑的 dev Agent）跑同一套：
`Ran 253 tests ... OK`，且 `.local/` **仍未出现**。

⇒ 今天测试没有在写检出目录。故 T-02 的诚实定位是**「T-03 之前的守卫」**，不是「修一个当下的泄漏」。
计划里那句「跑完 `REPO_ROOT/.local/` 清单与 mtime 不变」若写成一条**测试**会自相矛盾——
一条断言检出目录的测试自己就解析进了检出目录，且在干净克隆上它要断言一个不存在的目录。
故落地为 `scripts/test.sh` 的守卫（见 4），并明确它的盲区。

**2. 先红（实测输出）**

```
FAIL: test_no_test_module_joins_a_derived_root_with_local
  test_storage_migration_paths.py:46: self.assertEqual(default_data_dir(), REPO_ROOT / ".local" / "data")
Ran 6 tests ... FAILED (failures=1)
```

**恰好 1 处命中**。分母：`tests/test_*.py` **34** 个，其中 `test_test_isolation.py`（规则自己，须能写出被禁形状）豁免，
**实扫 33** 个——这个分母由 `scanned()` 里的 `assertGreater(len(modules), 0)` 钉住，匹配集为空时测试自身失败，
规则不会因「扫到 0 个文件」而空转通过。

**3. 最小实现（未丢断言）**

- `tests/support.py`：新增 `isolated_paths()` 上下文管理器 + `IsolatedPaths` 数据类，建
  `tmpdir/data`、`tmpdir/logs`、`tmpdir/runtime` 三件套，设 `WT_MEDIA_AGENT_DATA_DIR` 并重置配置缓存，退出时恢复两者。
  `logs` 取 `<data>/logs`（**不是** `data` 的同级）——这是 `RuntimePaths.resolve` 的 override 契约钉住的形状；
  `runtime` 今天无消费者，登记在 docstring 里，不假装它已被用。
- `tests/test_storage_migration_paths.py:44-69`：删 `REPO_ROOT`，改由
  `load_config(config_dir=/nonexistent, env={}, frozen=False, home=/home/nobody, repo_root=/checkout)` 断言
  **同一条 dev 规则**，并加 `assertNotIn("nobody", …)` 钉住「dev 不落到 `$HOME`」。
  **无断言被删**：该文件原有的 override 优先级、production 装机路径、旧 `~/.wt-media-agent` 已消失
  三条断言全部保留，改动只把「真实检出」换成「注入的根」。

`src/` 在 T-02 **零改动**（`git status --porcelain` 仅 3 个测试文件 + 1 个新文件）。

**4. `scripts/test.sh` 的守卫（exit 码为判据）**

跑套件前后只比**新增**路径，命中则打印具体路径并 `exit 1`。只比新增，是因为开发者的 dev Agent
可能正在同一个 `.local/` 里写它的数据库——那不是测试的行为，把它算成违规会让守卫天天误报。

| 情形 | 结果 |
|---|---|
| 正常跑 | `exit=0`，套件 `259 tests OK`（253 → 259，只增不减） |
| 变异探针：某测试写入 `.local/__probe_must_be_flagged__` | `exit=1`，点名该路径 **且套件本身打印 `OK`** |
| 探针清理后复跑 | `exit=0`，残留 **0** 处 |

变异那一行是本 Task 最要紧的一条：守卫在**测试全绿**时照样报警 ⇒ 它**独立于测试结果**，
不是在转述套件已经发现的事，也不可能因套件变绿而失效。

**5. 阳性对照（两处，均实际出红）**

- **规则内**（`test_the_rule_can_flag_the_shape_it_forbids`）：正则能在 `x = REPO_ROOT / ".local" / "data"`
  与 `y = ROOT /  '.local'` 上命中——否则删掉正则会留下一条对着空匹配集通过的测试。
- **端到端**（本轮实跑）：把被禁形状放进探针模块 `tests/test_zz_probe_forbidden.py` 后跑规则，

  ```
  - ['test_zz_probe_forbidden.py:3: PROBE = REPO_ROOT / ".local" / "data"']
  + []
  Ran 6 tests ... FAILED (failures=1)
  ```

  删掉探针即 `OK`。⇒ 报出的是**带文件与行号的真实命中**，不是空转。

- **反向对照**（`test_the_rule_does_not_flag_an_injected_root`）：`Path("/repo/.local/data")` 这类**注入根**的写法
  **不得**被命中——它是 `tests/test_runtime_paths.py` 用来免除本机依赖的形式；误伤它等于把测试推回真实检出，
  与目的相反。

**6. 一处计划未预见、如实登记的发现**

定向调用 `python -m unittest tests.<模块>` **今天就是坏的**：`tests/` 无 `__init__.py`，
该形式把仓根而非 `tests/` 放上 `sys.path`，于是 `from support import …` 报
`ModuleNotFoundError: No module named 'support'`。分母：**34 个测试模块中 6 个 import `support`，
本 Task 只新增其中 1 个**（另 5 个是既有的 `test_bootstrap` / `test_local_api_server` / `test_new_task_type` /
`test_proxy_check` / `test_proxy_extract`）。⇒ 这是**既有的测试布局属性，不是 T-02 引入的回归**，
故本 Task 不改布局（不新增 `__init__.py`、不移动文件）；只把**可用的调用形式**记录下来供后续 Task 使用，
避免 T-04…T-09 的定向验证反复撞同一堵墙。

## Follow-Up

- **盲区（明写，不藏）**：守卫只比「新增路径」，**看不见就地修改**（开发者 dev Agent 在跑时对
  `.local/` 下已有文件的写入）。它守的是「测试在检出里**创建**运行时目录/文件」这一类，
  正是 T-03 之后最可能发生的那一类。
- T-03 现在可以安全动 `runtime/paths.py:107`：dev 真落盘后，任何解析到真实检出的用例会被规则拦下。
- 后续 Task 的定向验证一律带 `PYTHONPATH=tests` 前缀。
