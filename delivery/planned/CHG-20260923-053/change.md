# CHG-20260923-053：Agent 运行时目录、依赖边界与生产运行能力

- Status: PLANNED
- Level: S
- 锚点：ADR-0016；工程架构基线 §5.2 / §5.4 / §5.5 / §5.6 / §5.8
- 日期：2026-09-23
- 基线：`docs/decisions/0016-agent-runtime-layering-and-dependency-boundaries.md`；`docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md` §5。
- 当前仓库：wt-media-agent；文档与治理记录在 wt-media-workspace。
- 未激活：本草案已获用户确认（2026-09-23），但按用户decision 排在 M3 收尾之后实施，不抢占当前 active 名额。激活前不得开始运行时代码实施。

## 独立目标与范围

把 `wt-media-agent` 从「功能可运行」调整为「可长期部署、维护、迭代」的小型生产级 Agent：

- 建立真实启动闭环：Local / Cloud / sidecar 三种模式各自有可运行入口；
- 补齐生产运行能力：分层配置加载、JSON 日志、生命周期与信号、聚合健康检查、版本单一来源；
- 按职责重切目录：`runtimes/` 撤销，BitBrowser / CDP / 平台身份 / 代理按「外部系统协议」与「本机公共能力」分别归入 `clients/` 与 `services/`；
- 让依赖方向可机器校验，而不是靠约定。

**影响分析（可引用 Engineering 规则的依据）：** 本 CHG 不改变业务行为、不改变任何既有 API contract 语义、不改变已有测试的断言含义。既有测试基线 85 个用例在本 CHG 全程保持全绿且数量不减少；`/healthz` 字段冻结；`/api/v1/health` 为纯新增路径。因此按 `planning-wt-media-delivery` 的「小变更可引用稳定 Engineering / Decision 规则」路径锚定 ADR-0016，不新增 Milestone。

## 明确不做

- 不引入 DDD、微服务、插件系统、事件总线、DI 容器或 Service Locator；
- 不创建未实现的空包（`executors/discovery/`、`clients/douyin/`、compose / publish / ffmpeg / file / process 等）；
- 不创建 `platforms/`：平台差异落 `clients/<platform>/`，`douyin` 内容发现按 ADR-0015 归 Cloud；
- 不改动既有任务类型、状态取值、错误码字符串或响应信封；
- 不以本次重构为名扩充 M2/M3 的业务能力。

## 顺序任务

### Task 1：目录与依赖基线

- 工作：`constants.py` → `runtime/`；新增 `runtime/{__init__,version}.py`；`clients/bitbrowser/` 拆分并新增公开 `open_url()`；落地零依赖的 AST 边界测试与 `test_patch_targets.py`。
- 验收：依赖规则可机器校验；executor 不再直连私有 `_post`；85 用例全绿。

### Task 2：外部客户端与公共能力分层

- 工作：`clients/cloud/` 迁移；`services/{browser,net}/` 建立；`runtime/environment.py` 委托 services 并撤销 `runtimes/`；`storage/` 整理（`checkpoint.py`、`sqlite.py`、`migration.py` 重导出）；新增 `utils/time.py`。
- 验收：`storage.migration` 的路径与符号不变，`migrate-storage.sh` 连续两次成功。

### Task 3：runner 与 Local API 拆分

- 工作：`runner/` 三拆并重导出 `TaskRunner` / `TaskRunnerConfig`（测试零改动）；`local_api/` 瘦身，平台身份与代理外迁，同 commit 更新 4 处 `urlrequest` patch 路径。
- 验收：`TaskRunner` 位置参数与 `_claim_task()` 语义不变；`verify-health.sh` 通过。

### Task 4：bootstrap 与运行时可达

- 工作：`bootstrap/{local,cloud,sidecar,app}.py`；`runtime/{config,logging,lifecycle,health}.py`；`sidecar_main.py` 变瘦 shim 并保住 `local_api_server` 属性与字面 argv；`pyproject.toml` 入口重指；删旧入口。
- 验收：三种模式各留一次启动与健康输出记录；runner 默认关闭。

### Task 5：配置约定对齐 Cloud

- 工作：`configs/` → `config/`；新增同构 `config_online/`；`runtime/config.py` 分层加载（env > file > default）与 `RuntimePaths`。
- 验收：运行时代码只读 `./config`，`src/` 下零处引用 `config_online`；同构校验测试通过。

### Task 6：数据目录、日志与健康检查

- 工作：OS 标准数据目录（内部 `data/ logs/ versions/`，懒创建且失败降级）；三个 JSON 日志文件 + stderr；`GET /api/v1/health` 与契约更新。
- 验收：聚合健康检查不抛异常、不触发对外写请求；`/healthz` 字段未变。

### Task 7：发布打包与文档同步

- 工作：`scripts/build_desktop_sidecar.py` 落地 `config_online -> 产物/config`（整目录替换）；`AGENTS.md`、`CLAUDE.md`、`README.md`、`scripts/README.md`、`contracts/*/README.md` 同步；workspace skill `agent-platform-adapter-change` 改指 `clients/<platform>` 并跑 `sync_skills.py`。
- 验收：产物 `config/` 与 `config_online/` `diff -r` 无差异；skill 生成副本同步。

## 验收口径

1. **三种模式可启动**：Local、Cloud、sidecar 各有一次真实启动与健康输出记录。
2. **任务链路清晰**：Cloud Task → runner → executor → client/service → result 至少跑通一次领取→上报→checkpoint 落库→重启恢复。
3. **新增能力简单**：以「新增一个 executor + 一个 client」的 demo 证明无需改动 `runtime/`。
4. **目录职责明确**：边界测试全绿，`AGENTS.md` 能让人直接判断写业务/调外部/公共能力/改 Agent 自身各自的落点。
5. **配置约定与 Cloud 一致**：只读 `./config`；`config_online` 仅出现在打包步骤；产物 `config/` 与 `config_online/` 无差异；发布凭据只随 Agent 产物分发。
6. **测试基线不降**：`Ran N tests` ≥ 85 且 OK，每一步都比对。

每步以 `bash scripts/test.sh` 验证；里程碑边界跑 `bootstrap.sh && test.sh && migrate-storage.sh ×2 && build.sh` 与 `verify-health.sh`。

## 提交边界

wt-media-agent 与 wt-media-workspace 分仓提交。wt-media-agent 一步一 commit，「挪文件」与「改逻辑」不混在同一提交。

## 激活前置

激活前必须确认：

1. `CHG-20260916-052` 已离开 `delivery/active/`（`delivery/active` 只允许一个 CHG，脚本硬校验）；
2. `wt-media-agent` 工作区干净，或既有脏文件已单独提交；
3. 重构前测试基线重新实测并记录（本草案作者实测：`Ran 85 tests ... OK`）。
