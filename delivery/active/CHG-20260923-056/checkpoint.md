# CHG-20260923-056 Checkpoint

## 2026-09-23

Completed:
- 三仓结构审计（Desktop/Agent/治理），现状事实录入 change.md §4。
- 用户裁定：融合方案一（ADR-0016 目录 + 新方案内容）；本会话仅 CHG-A；模块分工多文件同步回写。
- 治理工件：程序总纲、CHG-056 change.md、planned 057/058/059 登记、LEDGER 同步。
- T-01：四仓 AI 入口文档各自独立提交（desktop `47a6263`、cloud `3b733ff`、workspace `e0444cd`；agent 上一轮 `d3ab02f` 已提交）；配置格式按 D-05 回写为 TOML（`change.md` §6 D-01/§2/§5/§7/§8 + 程序总纲 §2 + planned CHG-059）；测试基线证据按模板规范化。

Current:
- T-03 Agent runtime/config + paths（`runtime/{paths,config,logging}.py`、`config/agent.toml` + `config_online/agent.toml` 镜像、删除 `config.py`/`log_setup.py`、`storage.migration.default_data_dir` 委托 `RuntimePaths`）。

Next:
- T-04 Agent bootstrap + executors 注入。

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
