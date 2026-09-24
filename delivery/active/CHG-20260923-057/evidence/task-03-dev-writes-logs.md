# Evidence: T-03 Agent dev/override 真落盘

- CHG: `CHG-20260923-057`
- Task: `T-03`
- Date: 2026-09-24
- Type: command（含一次真实启动）
- Status: PASS

## Purpose

把「dev/override 不写日志文件」改成真落盘，满足裁定十一第一条（`.local/logs` 不为空），
即里程碑成功事实 #5 的前半（「日志独立落盘」）。这是本 CHG 里唯一**推翻既有行为**的 Task。

## Method

```bash
# 1. 先把断言改掉（src 不动）→ 红
PYTHONPATH=tests .venv/bin/python -m unittest tests.test_runtime_paths tests.test_runtime_config tests.test_runtime_logging

# 2. 最小实现（paths.py 一行）后 → 绿；并跑全套（含 T-02 的 .local 守卫）
bash scripts/test.sh; echo "exit=$?"

# 3. 真实启动（判据不可用单元测试替代）
TMP=$(mktemp -d); rsync -a --exclude .local --exclude .venv --exclude .git ./ "$TMP/"   # 含未提交改动
cd "$TMP"
env -u WT_MEDIA_ENV -u WT_MEDIA_AGENT_DATA_DIR -u WT_MEDIA_LOG_FILE \
    PYTHONPATH="$TMP/src" WT_MEDIA_LOCAL_API_PORT=18765 .venv/bin/python -m wt_media_agent.local_main
curl -s http://127.0.0.1:18765/healthz
find "$TMP/.local" -mindepth 1 -maxdepth 3; cat "$TMP/.local/logs/agent.log"

# 4. 对照臂：同一启动，只把 default_log_file 回退为 T-03 之前的形式，端口 18766
```

**为什么不在真实检出里启动**：开发者的 dev Agent（PID 55443）正持着检出目录的 SQLite。
临时树跑的是**同一份未提交代码**（`rsync` 复制工作区），`repository_root()` 由 `__file__` 推导，
故它跑的就是真实的 **dev** 分支（不是 override）。已实测 `PYTHONPATH` 压过 venv 的
editable 安装（`_editable_impl_wt_media_agent.pth`）：`wt_media_agent.__file__` 落在临时树内。

## Expected

1. 改断言后**红**，且红的正是被推翻的那几条行为。
2. 实现后全套绿（253 → **259**，只增不减），T-02 的守卫不响。
3. 真实 dev 启动后 `<检出>/.local/logs/agent.log` **存在且非空**；stderr **同时**仍有记录。
4. **对照臂无该文件**——否则「文件出现」不能归因于本变更。

## Actual

**1. 先红：7 处，逐条点名（分母 55 条）**

```
FAIL: test_every_deployment_shape_writes_a_real_file (…) (origin={'data_dir': '/tmp/wt-override'})
FAIL: test_every_deployment_shape_writes_a_real_file (…) (origin={'environment': 'development', …})
FAIL: test_the_file_is_always_under_the_resolved_logs_dir (…) (origin={'data_dir': …})
FAIL: test_the_file_is_always_under_the_resolved_logs_dir (…) (origin={'environment': …})
FAIL: test_defaults_when_nothing_is_configured
FAIL: test_the_health_scripts_log_file_variable_is_not_agent_config
FAIL: test_a_development_run_writes_a_file_as_well_as_stderr
AssertionError: '' != '/repo/.local/logs/agent.log'
```

两个新测试的 **installed 子例仍绿**（装机态行为未变）——这正是「只推翻该推翻的」的证据。

**2. 实现比计划小：只改一行行为**

`configure_logging` 的 file 分支**一直存在**（`logging.py:48-55`，`RotatingFileHandler` 10MB×3），
只是 dev/override 时 `log_file` 恒为 `""` 而**永不可达**。故本 Task **没有新增任何写日志的代码**：
把 `paths.py:107` 的 `return "" if self.origin in {"dev","override"} else …` 改为
`return str(self.logs_dir / "agent.log")`，`logging.py` **零改动**。

**未被交换掉的东西**：`configure_logging` 的 stderr handler 是**无条件**安装的，所以 dev 现在
「文件 + 终端」两者都有，而不是二选一；日志目录建不出来时仍降级为仅 stderr（`configure_from`），
那条既有单测 `test_an_uncreatable_log_directory_degrades_to_stderr` **仍绿**。

同步改掉两处**已假**的注释：`config/agent.toml`（原写「a source checkout logs to stderr」）、
`config_online/agent.toml`（原写「for the same reason: a bundled sidecar has no terminal」）。

**3. 全套绿：259 tests OK，exit=0**（253 起点 → T-02 的 259，本 Task 不增不减，因改的是既有断言）。

**4. T-02 的规则**命中了我自己的 T-03 新代码**（如实登记）**

写测试时我在 `test_runtime_logging.py` 写了 `str(repo / ".local" / "logs" / "agent.log")`，
被 T-02 落下的规则（`<标识符> / ".local"`）拦下，恰好 1 处命中。**我没有放宽规则**：
该处 `repo` 是临时根、不是检出目录，属规则的**误报方向**，但它同时也是一处**真的重复推导布局**
（手写的 `.local/logs` 会与 `RuntimePaths` 漂移而测试照样通过）。故改测试而非改规则：
断言改为 `cfg.paths.origin == "dev"` + `cfg.paths.logs_dir` 在注入根内 + `cfg.log_file == str(cfg.paths.logs_dir / "agent.log")`。
规则保持原样，**它刚证明了自己会命中**。

**5. 真实 dev 启动（本 Task 的判据）**

```
$ curl -s http://127.0.0.1:18765/healthz
{"status":"ok","service":"wt-media-agent","mode":"m1"}

$ find "$TMP/.local" -mindepth 1 -maxdepth 3 | sort
/tmp/wt-t03-BCjGQB/.local/data
/tmp/wt-t03-BCjGQB/.local/data/local-agent.sqlite3
/tmp/wt-t03-BCjGQB/.local/data/versions
/tmp/wt-t03-BCjGQB/.local/logs
/tmp/wt-t03-BCjGQB/.local/logs/agent.log

$ ls -l .local/logs/agent.log
-rw-r--r--@ 1 aqiuye  staff  114 Sep 24 13:37 …/agent.log

$ cat .local/logs/agent.log
2026-09-24T13:37:00 [INFO] wt_media_agent.local_api.server: wt-media-agent local API listening on 127.0.0.1:18765
```

stderr 里**同时**有同一条（未交换）：
```
2026-09-24T13:37:00 [INFO] wt_media_agent.local_api.server: wt-media-agent local API listening on 127.0.0.1:18765
```

**6. 对照臂（决定归因）**

同一份树、同一 dev 形态、同一启动方式，只把 `default_log_file` 回退成 T-03 之前的形式：

```
running (pid 39631)                    ← 进程真的起来了
{"status":"ok",…}                      ← healthz 同样 ok
/tmp/wt-t03-ctrl-vKmAio/.local/data    ← data 树照建
/tmp/wt-t03-ctrl-vKmAio/.local/data/local-agent.sqlite3
/tmp/wt-t03-ctrl-vKmAio/.local/data/versions
/tmp/wt-t03-ctrl-vKmAio/.local/logs    ← 目录在（ensure() 早就在建）
$ ls .local/logs/agent.log
ls: … No such file or directory        ← 空目录，无文件
```

⇒ **`.local/logs/` 目录原本就存在且为空，文件是本变更带来的**。这同时**实测坐实**了本记录 §4 写下的
起点读数：「磁盘上 `.local/logs/` 是空的」——此前那是推断，现在是两侧对照过的实测。

**7. 连带面申报（不藏）**

- **正式包此前就写盘，dev 现在也写**：只读/沙箱文件系统上的降级路径未变（`configure_from` → 仅 stderr → 仍启动）。
- 磁盘占用：dev 开发树从此多出 `.local/logs/agent.log`（10MB×3 轮转，T-07 改为 20MB + 14 天 + 总量）。
- `logging.level` 从「只影响终端」变为「影响落盘内容」——T-04/T-07 承接。
- **T-09 ① 已被本 Task 顺手完成**：`paths.py` 那段已假注释（「Desktop currently discards the sidecar's
  stdout and stderr」）随本次 docstring 重写一并删掉。T-09 只需做 ②③④，已在其行内标注。

## Follow-Up

- T-04：`.local/logs/` 由 1 个文件变 3 个（`agent.log`/`task.log`/`error.log`）+ 两向路由断言。
  在 T-04 落地前，AC-01 只算**部分**成立（独立启动 ✓、agent.log 非空 ✓、三文件 ✗）。
- T-09 ① 划掉（见上 §7 末条）。
- 临时树已清理（`rm -rf`，2 棵，均建在 `/tmp`；开发者的检出目录与 `.local/` 全程未动）。
