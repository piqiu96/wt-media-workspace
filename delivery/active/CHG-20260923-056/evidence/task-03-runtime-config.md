# Evidence: Agent 运行时配置、路径与配置目录（T-03）

- CHG: `CHG-20260923-056`
- Task: `T-03`
- Date: 2026-09-23
- Type: test + command + diff
- Status: PASS

## Purpose

证明 T-03 把「Agent 的配置与写入位置」收敛为单一事实源，且收敛过程中**没有
顺手改变既有行为**：

1. `runtime/config.py` 是 `src/` 里唯一读环境变量的模块，键集由 `_SPEC` 表穷举；
2. `runtime/paths.py` 是写入位置的唯一事实源（override / dev / installed 三态）；
3. 死代码 `config.py` 被删、`log_setup.py` **零字节改动**迁入 `runtime/`
   （「移动文件」与「改逻辑」不同 commit）；
4. 凭据只从环境变量来：TOML 里的任何敏感键被忽略，且**按名报告、绝不按值**；
5. 5 处自建 `BitBrowserClient` 改由 `factory` 统一构造，超时 `max` 语义逐字保留；
6. 唯一的行为变更（`default_data_dir` 默认值）被显式记录并有测试钉住。

## Method

### 1. 提交序列

`wt-media-agent`，`main`，基线 `b1233cc`（T-02 收尾）→ `d870d1f`，共 **10** 个 commit：

| # | commit | 内容 |
|---|---|---|
| 1 | `9c7d3db` | 新增 `runtime/paths.py` 三态解析 |
| 2 | `2e7afa3` | `config/` + `config_online/` 落地；声明式配置加载器 `runtime/config.py` |
| 3 | `416a56a` | `log_setup.py` → `runtime/logging.py`（纯移动）；删除零引用 `config.py` |
| 4 | `4e7ecb8` | 日志初始化接配置；`local_api/server.py:main` 不再读环境变量 |
| 5 | `3bfc66b` | 两个超时覆盖移出客户端，改由构造注入（`timeouts.py` + `factory` 前置） |
| 6 | `3d1be25` | 5 处自建 `BitBrowserClient` 改由 `bitbrowser_from_config` 构造 |
| 7 | `ad066e5` | `default_data_dir()` 委托 `get_config().paths.data_dir`，记录默认值变更 |
| 8 | `6f987a7` | docs：`DIRECTORY_MAP.md` 按 T-02/T-03 后实际布局重写 |
| 9 | `54e2636` | test：补 `factory` 装配测试（此前零覆盖） |
| 10 | `d870d1f` | fix：`apply_migrations` 连接泄漏（取证中发现，见 §7） |

第 8～10 个不在计划条目内：8 是计划要求 T-10 才做的路由文档回写，因该文件是
`CLAUDE.md` 指定的入口、T-03 后已列 5 个已删模块，提前回写；9 与 10 的理由见
§6、§7 与 Follow-Up。

### 2. 逐 commit 测试矩阵

用 `git archive` 把 10 个 commit 各自导出到 `/tmp` 独立目录后**逐个实跑**，
而非采信执行当时的记录：

```bash
for c in $(git log --format=%h --reverse b1233cc..HEAD); do
  d=/tmp/t03-final/$c; mkdir -p $d; git archive $c | tar -x -C $d
  (cd $d && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src "$VENV_PY" -m unittest discover -s tests)
done
```

### 3. 冻结导入

```bash
for c in $(git log --format=%h --reverse b1233cc..HEAD); do
  git show "${c}:tests/test_runner_session.py" | shasum -a 256
done
git log --oneline b1233cc..HEAD -- tests/test_runner_session.py | wc -l
```

### 4. 纯移动证明（blob 级）

```bash
git show --raw -M --format='' 416a56a
git rev-parse 416a56a^:src/wt_media_agent/log_setup.py
git rev-parse 416a56a:src/wt_media_agent/runtime/logging.py
```

### 5. 环境变量与死 import（各带阳性对照）

```bash
grep -rn 'os\.environ\|os\.getenv' src/wt_media_agent/ --include='*.py' | grep -v runtime/config.py
python3 /tmp/deadimports.py src tests     # AST 扫描，__all__ 字面量算使用
```

两个否命题检查都先植入对照再采信：环境变量检查的对照是 `runtime/config.py`
自身（必须命中）；死 import 检查的对照是往 `utils/time.py` 追加
`import socket` 与 `import json  # noqa`，两者都必须被报出。

### 6. 变异对照

`/tmp/mutations.py`：19 条变异，每条破坏一个承重断言，跑对应测试文件必须转红；
每条在应用前先确认基线为绿、应用后还原并再跑一次确认回到绿。

### 7. 真实进程

```bash
bash scripts/migrate-storage.sh --data-dir /tmp/wt-agent-t03     # 两次
bash scripts/verify-health.sh
bash scripts/migrate-storage.sh                                  # 不给 --data-dir
```

## Expected

1. 10 个 commit 逐个 `Ran N tests` 且 `OK`，`N` 不低于 T-02 收尾的 94；
2. `tests/test_runner_session.py` 的 sha256 在 10 个 commit 上恒定，且 ≠ 空串哈希；
3. `log_setup.py → runtime/logging.py` 在 blob 级完全相同（`R100`），
   `config.py` 同 commit 删除；
4. `src/` 中 `runtime/config.py` 之外读环境变量的模块数为 **0**，死 import 为 0；
5. 19/19 变异全部转红并还原为绿；
6. 配置镜像：`config/` 与 `config_online/` 文件名与键集一致；
7. 真实进程：迁移两次为 `2 applied` 后 `0 applied`；健康检查打印**配置格式的**
   日志行并 `health ok`。

## Actual

### 1. 逐 commit 测试矩阵（PASS）

| commit | tests | result |
|---|---|---|
| `9c7d3db` | 107 | OK |
| `2e7afa3` | 133 | OK |
| `416a56a` | 133 | OK |
| `4e7ecb8` | 145 | OK |
| `3bfc66b` | 155 | OK |
| `3d1be25` | 155 | OK |
| `ad066e5` | 163 | OK |
| `6f987a7` | 163 | OK |
| `54e2636` | 171 | OK |
| `d870d1f` | 172 | OK |

单调不减，无一个 commit 低于 T-02 收尾的 94。增量来源：
`test_runtime_paths` +13、`test_runtime_config` +26、`test_runtime_logging` +12、
`test_bitbrowser_timeouts` +10、`test_storage_migration_paths` +8、
`test_bitbrowser_factory` +8，以及 `test_bitbrowser_runtime` 的净增。

### 2. 冻结导入（PASS）

sha256 在 10 个 commit 上恒为
`888113caaf5bb970fa0637ffebac34e304f9ffad0a74508e9ea49fe9e59bb4b0`，
与 T-02 evidence 记录的**同一个值**；`git log -- tests/test_runner_session.py`
计数 **0**。阳性对照：空串 sha256 为 `e3b0c442...`，与上值不同，证明提取确实
读到了内容而非静默失败。

### 3. 纯移动（PASS，blob 级）

```
:100644 000000 948c1a5 0000000 D  src/wt_media_agent/config.py
:100644 100644 63c36d3 63c36d3 R100 src/wt_media_agent/log_setup.py src/wt_media_agent/runtime/logging.py
```

`R100` 且新旧 blob 同为 `63c36d33afd9fb83c9cf235b21c47af4ef4964b8`——该 commit
**没有改动任何一行**被移动的代码，删除 `config.py` 与移动 `log_setup.py` 同
commit 但两者都是纯操作，符合「移动与改逻辑不进同一 commit」。

### 4. 环境变量与死 import（PASS）

- `runtime/config.py` 之外的环境变量读取点：**0**；对照（该文件自身）：**2** 处命中。
- 死 import：**0**；对照植入 `socket` 与带 `# noqa` 的 `json` 两个未使用 import，
  两个都被报出，随后按字节还原（`git diff` 为空）。

### 5. 变异对照（PASS，19/19）

| # | 变异 | 目标测试文件 | 结果 |
|---|---|---|---|
| M01 | 超时 floor 由 `max` 改 `min` | `test_bitbrowser_timeouts.py` | 红 → 绿 |
| M02 | 超时函数改为晚读环境变量 | `test_bitbrowser_factory.py` | 红 → 绿 |
| M03 | 文件层压过环境层 | `test_runtime_config.py` | 红 → 绿 |
| M04 | 敏感键改从文件读取 | `test_runtime_config.py` | 红 → 绿 |
| M05 | 不再识别敏感键 | `test_runtime_config.py` | 红 → 绿 |
| M06 | 日志级别不再校验 | `test_runtime_config.py` | 红 → 绿 |
| M07 | 报错丢失键路径 | `test_runtime_config.py` | 红 → 绿 |
| M08 | 别名压过规范名 | `test_runtime_config.py` | 红 → 绿 |
| M09 | `log_file` 加上脚本别名 | `test_runtime_config.py` | 红 → 绿 |
| M10 | 可选超时改严格抛错 | `test_runtime_config.py` | 红 → 绿 |
| M11 | `data_dir` 覆盖被忽略 | `test_runtime_paths.py` | 红 → 绿 |
| M12 | production 不再选 installed | `test_runtime_paths.py` | 红 → 绿 |
| M13 | dev 也写日志文件 | `test_runtime_paths.py` | 红 → 绿 |
| M14 | logger 名回退为连字符形式 | `test_runtime_logging.py` | 红 → 绿 |
| M15 | 目录创建失败不再降级 | `test_runtime_logging.py` | 红 → 绿 |
| M16 | `default_data_dir` 回退旧默认值 | `test_storage_migration_paths.py` | 红 → 绿 |
| M17 | `main` 忽略 `--data-dir` | `test_storage_migration_paths.py` | 红 → 绿 |
| M18 | `factory` 硬编码 url | `test_bitbrowser_factory.py` | 红 → 绿 |
| M19 | `factory` 丢弃 create 覆盖 | `test_bitbrowser_factory.py` | 红 → 绿 |

**重要更正**：本会话先前记录的「14 条变异、12 条可判别、2 条为已知缺口」**不能
采信**。原因是变异脚本 `/tmp/mut.sh` 只定义了 `run`/`mut`/`clean` 三个函数却
**没有分发 `"$@"`**，因此以 `bash /tmp/mut.sh run X` 调用时它只定义函数便退出，
一切输出为空。无输出本不会被误读为通过，但无法确认当时的实际调用方式，故整组
结果作废并在此重做。本表 19 条是修复分发后、并要求「基线先绿、变异转红、还原
回绿」三步俱全才计数所得。M02 即原「缺口」中「客户端晚读环境变量」那一条，
现由 `test_a_variable_set_after_construction_is_not_observed` 覆盖。

### 6. `factory` 的覆盖缺口（PASS，原因与修复）

`git grep bitbrowser_from_config tests/` 在补测前命中 **0**：`factory.py` 作为
「唯一构造点」这一断言的载体，此前完全没有测试，于是「5 处自建 client 改由配置
构造」只被源码 diff 支撑、没有被会变红的测试支撑。补 `test_bitbrowser_factory.py`
（8 个测试）后，M18/M19 才有判别力。

### 7. 取证中发现的既有缺陷（PASS，已修）

`python3 -m unittest discover -s tests` 在 T-02 收尾（`b1233cc`）为 **0** 条
`ResourceWarning`，在 T-03 结束时为 **20** 条。用 `-X tracemalloc` 取分配回溯
定位到**既有**代码的三个站点，全部是 `with sqlite3.connect(...)`：

- `src/wt_media_agent/storage/migration.py:104`（生产代码）
- `tests/test_storage_migration.py:20`
- `tests/test_storage_sqlite.py:33`

`with connection` 提交事务但**从不关闭连接**，因此 `apply_migrations` 每次调用
泄漏一个连接——而它在 Agent 启动路径上。即泄漏本已存在，是 T-03 新增的
`test_storage_migration_paths.py` 多调了几次 `main()` 才把它推到可见阈值。
按「失败验证 → 最小实现」修复（`closing(...)` 负责关闭、`db` 负责事务），
计数 20 → 10 → **0**（`python3` 与 venv 两个解释器均为 0）。

### 8. 真实进程（PASS）

```
storage migration ok: 2 applied, 2 total      # 第一次
database /tmp/wt-agent-t03/local-agent.sqlite3
storage migration ok: 0 applied, 2 total      # 第二次，幂等
```

不带 `--data-dir` 时落在
`<repo>/.local/data/local-agent.sqlite3`，且 `git check-ignore` 命中
`.gitignore:2`（`.local/`），确认新默认值不会污染工作树。

`scripts/verify-health.sh`（`python3`，真实起进程）输出：

```
2026-09-23T23:00:37 [INFO] __main__: wt-media-agent local API listening on 127.0.0.1:18765
wt-media-agent health ok
```

时间戳 + `[INFO]` + logger 名正是 `runtime/logging.py` 配置的格式，证明
`configure_from` 在真实 `main` 里生效（而非仅在测试中）。

### 9. 配置镜像与凭据规则（PASS）

- `test_filenames_match` / `test_key_sets_match` 断言 `config/` 与 `config_online/`
  的文件名与键集一致（整目录替换的前提）。
- 凭据：`test_sensitive_keys_in_the_file_are_ignored`（文件里的敏感键被忽略）、
  `test_the_ignored_value_never_reaches_the_log`（**值不出现在日志**）、
  `test_runtime_token_does_come_from_the_environment`（仅环境变量可提供）、
  `test_unknown_keys_are_reported_by_name`（按名报告）。
- 核对**随发布走的** `config/agent.toml` 与 `config_online/agent.toml`：
  两者都**只以注释**提到 `runtime_token`，未声明任何凭据键，即发布产物本身
  不含凭据（grep 命中均为注释行）。

### 10. 唯一的行为变更（已记录）

`storage/migration.py:default_data_dir()` 在未设 `WT_MEDIA_AGENT_DATA_DIR`、
无 `--data-dir`/`--db-path` 时，旧行为是无条件返回 `~/.wt-media-agent`，新行为
跟随部署形态（checkout → `<repo>/.local/data`）。已核查 CI 与脚本不依赖旧行为：
`m0-agent.yml` 与 `verify_m0_local.sh` 都显式传 `--data-dir`。测试
`test_the_old_unconditional_home_directory_is_gone` 钉住该变更；
`README.md` 与其 docstring 均已记录，且迁移命令现在会打印所用路径使其可观察。

## Follow-Up

- **待登记 D 行（拟 D-07）**：ADR-0016 §7 允许凭据放在仓库配置中，而 T-03 的
  加载器忽略 TOML 里的一切敏感键。该收窄出自用户批准的程序总纲 §4，但需要一条
  显式 D 行，使 CHG-D(059) 知道 `config_online/` 的凭据通路**不可用**；
  两份 README 已经在声明这一收窄。建议在 `change.md` §6 补 D-07。
- **未被测试覆盖、已枚举**（不以「测试通过」代替）：
  1. 5 处 executor 的 `bitbrowser_from_config(get_config())` 调用点本身，以及
     `LocalApiServer` 的 `bitbrowser or bitbrowser_from_config(...)` 默认分支，
     **无测试断言其产物来自配置**——现有测试一律注入假 client 走另一分支。
     T-04 删除这 5 处改为注入后，由 `test_bootstrap.py` 的「executor 与
     `components.bitbrowser` 是同一实例」覆盖。
  2. 「`src/` 只有 `runtime/config.py` 读环境变量」目前是**手工 grep**，尚非测试；
     T-05 的 R6 才把它变成机器校验。在此之前，该规则的间接通路
     （任何模块调用 `get_config()`）在语法上不受约束。
- **`clients/bitbrowser/__init__.py` 的 docstring 自相矛盾**：既称「`clients/`
  之外不得构造 `BitBrowserClient`」，又称「由 bootstrap 构造一次」，而 bootstrap
  正在 `clients/` 之外。归 T-05 的 R1/R2 白名单解决。
- **打包产物需在 T-04 重新取证**：T-02 曾测得产物内 `runner` 与 `executors`
  均为 0 个模块。T-04 让 sidecar 委托 bootstrap 后该集合会变。
- **范围说明**：第 10 个 commit（连接泄漏修复）不在 T-03 计划条目内。就地修而
  非仅登记的理由是它是启动路径上的真实资源泄漏、修复仅一行、且有会变红的测试
  守着；已在 §7 与本节如实披露。
