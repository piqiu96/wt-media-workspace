# CHG-20261003-077 追加部署逻辑实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 Cloud RC 部署改为版本自包含目录，并通过宝塔 Go 项目与进程管理器运行 Server、Scheduler、Worker，同时由 Server 提供 Cloud Web。

**Architecture:** 每个产品 Tag 安装为 `/www/wt-media-cloud/releases/<tag>`，内部包含程序、Web、Migration、按环境渲染的实际私有配置、日志和临时目录；`current` 是宝塔唯一稳定运行入口。预发与生产共用 `.toml.tpl`，部署工具通过显式环境和远程变量表渲染并调用 Cloud 自身校验。Server 在已有 API 路由之后为非 API GET/HEAD 请求提供静态资源和 SPA 回退；Scheduler/Worker 继续是无端口独立进程。

**Tech Stack:** Go 1.26、CloudWeGo Hertz、Bash、Python `unittest`、GitHub Actions、宝塔 Go 项目和进程管理器。

**Spec:** `docs/superpowers/specs/2026-10-04-baota-cloud-deployment-layout-design.md`

## Global Constraints

- 只修改 `wt-media-cloud` 和 Workspace 的 CHG-077/Release 记录。
- GitHub 制品不得包含数据库密码、对象存储密钥、平台凭据或实际管理员口令。
- 三个进程都使用 `/www/wt-media-cloud/current` 工作目录并以 `www` 用户运行。
- Server 由宝塔 Go 项目管理；Scheduler 和 Worker 由宝塔进程管理器管理。
- 不使用 `shared/`、systemd 或 Scheduler/Worker 虚假端口。
- 数据库迁移失败时不得切换 `current` 或启动新版本。
- 软链回退不能替代不兼容数据库 Migration 和外部数据的恢复。

## Review Focus

- 未构建或缺失 `web/index.cloud.html` 时 Server 必须启动失败并给出明确错误，不能只运行 API 后造成首页 404。
- `/api/` 未知路径必须保留 JSON/API 404 语义，不能被 SPA 回退为 HTTP 200 HTML。
- 静态文件请求必须阻止目录穿越，并且非 GET/HEAD 请求不能返回前端页面。
- 配置变量拉取、模板渲染、Cloud 校验失败，目标配置非空或版本目录已存在时都必须停止且不改变 `current`。
- 密钥轮换后旧版本是否仍具回退资格必须在部署验收中显式记录。

---

### Task 1: 固化 CHG-077 的部署裁定

**Files:**
- Add: `docs/superpowers/specs/2026-10-04-baota-cloud-deployment-layout-design.md`
- Modify: `delivery/active/CHG-20261003-077/change.md`
- Modify: `delivery/active/CHG-20261003-077/plan.md`
- Modify: `delivery/active/CHG-20261003-077/checkpoint.md`
- Modify: `delivery/active/CHG-20261003-077/status/cloud.md`
- Modify: `delivery/active/CHG-20261003-077/status/workspace.md`

**Interfaces:**
- Consumes: 用户确认的版本自包含目录、`current` 单入口和宝塔进程分工。
- Produces: 后续 Cloud 实现和 Release 验收的唯一执行合同。

- [x] 更新 CHG 范围、任务、验收和明确排除项。
- [x] 运行 `python3 scripts/verify_delivery_governance.py` 和 `python3 scripts/verify_ai_workspace.py`。
- [x] 提交 Workspace 规划变更。

### Task 2: Server 提供 Cloud Web 与 SPA 回退

**Files:**
- Create: `wt-media-cloud/internal/bootstrap/cloud_web.go`
- Create: `wt-media-cloud/internal/bootstrap/cloud_web_test.go`
- Modify: `wt-media-cloud/internal/bootstrap/routes.go`

**Interfaces:**
- Consumes: 包内工作目录下的 `web/index.cloud.html` 和现有 Hertz 路由。
- Produces: `registerCloudWeb(engine *server.Hertz, webRoot string) error`，在 API/健康/模块路由之后注册 NoRoute 处理器。

- [x] 先写失败测试：`/` 返回入口页、真实 asset 返回文件、`/login` 回退入口页、未知 `/api/` 返回 404、POST 深层路由不回退、目录穿越不读取根目录外文件、缺少入口页返回错误。
- [x] 运行 `go test ./internal/bootstrap -run 'TestCloudWeb|TestRegisterModuleRoutes' -count=1`，确认新增测试失败。
- [x] 实现安全的静态文件解析和 SPA 回退，并从 `registerRoutes` 调用 `registerCloudWeb(engine, "web")`。
- [x] 重新运行目标测试和 `go test ./internal/bootstrap -count=1`。
- [x] 提交 Cloud Web 服务变更。

### Task 3: 改为版本自包含安装和多环境配置渲染

**Files:**
- Modify: `wt-media-cloud/deploy/install.sh`
- Modify: `wt-media-cloud/deploy/init-config.sh`
- Create: `wt-media-cloud/deploy/render-config.py`
- Create: `wt-media-cloud/cmd/config-check/main.go`
- Modify: `wt-media-cloud/config_online/**`
- Modify: `wt-media-cloud/deploy/activate.sh`
- Modify: `wt-media-cloud/deploy/rollback.sh`
- Modify: `wt-media-cloud/deploy/verify-package.sh`
- Modify: `wt-media-cloud/scripts/dev/package_release_linux.py`
- Modify: `wt-media-cloud/scripts/verify/test_package_release_linux.py`
- Modify: `wt-media-cloud/scripts/verify/test_deployment_package.py`

**Interfaces:**
- Consumes: 仓库本地 `config/`、发布模板 `config_online/`、显式 `pre|online` 环境，以及 HTTPS 远程或本地 JSON 变量表。
- Produces: 打包时丢弃本地 `config/` 并将 `config_online/` 放入包内 `config/`；安装后拥有 `releases/<tag>/{config,logs,data/tmp}`；`init-config.sh` 拉取并调用 `render-config.py` 把模板状态的 `config/` 原子生成为运行配置，`bin/config-check` 使用 Cloud 同一套规则进行业务校验；`activate.sh` 只原子切换完整版本。

- [x] 先改测试断言：`config/` 与 `config_online/` 的归一化运行路径必须双向一一对应；打包器只把 `config_online/` 复制为包内 `config/`，不携带本地 `config/` 或 `config_test/`；安装后目录均为真实目录而非软链；同一模板可分别渲染 pre/online 变量；缺失、未知、残留变量、非法 TOML、Cloud 业务校验失败时停止且保留模板；安装不改变 `current`；切换和回退只改变单一软链；目录和文件归 `www:www`。
- [x] 运行 `python3 -m unittest scripts.verify.test_deployment_package -v`，确认旧实现失败。
- [x] 实现严格变量表解析、远程拉取、模板渲染、原子写入和 Cloud 配置校验；升级始终按目标环境重新渲染，不复制 `current/config`。
- [x] 更新激活/回退检查，要求目标版本拥有有效私有配置和必要目录。
- [x] 重新运行部署脚本测试和 `bash -n deploy/*.sh`。
- [x] 提交版本自包含部署脚本。

### Task 4: 替换宝塔部署手册和制品清单

**Files:**
- Modify: `wt-media-cloud/deploy/DEPLOYMENT.md`
- Delete: `wt-media-cloud/deploy/nginx-site-locations.conf.example`
- Delete: `wt-media-cloud/deploy/systemd/wt-media-cloud-server.service`
- Delete: `wt-media-cloud/deploy/systemd/wt-media-cloud-scheduler.service`
- Delete: `wt-media-cloud/deploy/systemd/wt-media-cloud-worker.service`
- Modify: `wt-media-cloud/deploy/config-template/credentials/object_storage.toml.example`
- Modify: `wt-media-cloud/scripts/dev/package_release_linux.py`
- Modify: `wt-media-cloud/scripts/verify/test_package_release_linux.py`
- Modify: `wt-media-cloud/scripts/verify/test_deployment_package.py`

**Interfaces:**
- Consumes: Tasks 2-3 的 Server/Web 和目录行为。
- Produces: 宝塔 Go 项目 Server 配置、进程管理器 Scheduler/Worker 配置、发布顺序和验收步骤；制品不再携带 systemd/Nginx 示例。

- [x] 先修改包和手册测试，要求新目录/宝塔进程说明存在，禁止 `shared/`、systemd、虚假端口和真实凭据。
- [x] 运行两个 Python 测试模块，确认旧手册与打包清单失败。
- [x] 更新手册、模板注释、打包必需文件和包结构校验。
- [x] 运行 `python3 -m unittest scripts.verify.test_package_release_linux scripts.verify.test_deployment_package -v`。
- [x] 提交宝塔部署文档和打包清单变更。

### Task 5: 重新执行 Cloud 端到端验证

**Files:**
- Create: `delivery/active/CHG-20261003-077/evidence/cloud-self-contained-deployment.md`
- Modify: `delivery/active/CHG-20261003-077/checkpoint.md`
- Modify: `delivery/active/CHG-20261003-077/status/cloud.md`

**Interfaces:**
- Consumes: 新 Cloud 包、空 MySQL 8.4 数据库和三个本地进程。
- Produces: 首次迁移、重复迁移、Server Web/API、管理员登录、Scheduler/Worker 存活和回退边界的事实证据。

- [x] 运行 Cloud Go 目标测试及两个部署/打包测试模块。
- [x] 构建 Linux 结构等价测试包并执行 `deploy/verify-package.sh`。
- [x] 在临时 MySQL 库执行首次和重复 Migration，确认管理员登录。
- [x] 从 `current` 路径启动三个进程，验证 `/`、`/login`、健康接口和后台进程；切换到第二版本后重启验证。
- [x] 删除临时数据库和账号，记录命令、预期、实际结果和结论。
- [ ] 提交 Workspace Evidence 和状态记录。

### Task 6: 生成新的 GitHub RC 候选

**Files:**
- Modify: `wt-media-workspace/releases/manifests/<new-product-rc>.yaml`
- Modify: `wt-media-workspace/scripts/release/package_assets.py`
- Modify: `wt-media-workspace/scripts/release/test_package_assets.py`
- Modify: `delivery/active/CHG-20261003-077/server-acceptance.md`
- Modify: `delivery/active/CHG-20261003-077/checkpoint.md`
- Modify: `delivery/active/CHG-20261003-077/status/workspace.md`

**Interfaces:**
- Consumes: 新 Cloud 组件 Tag、未变化的 Agent/Desktop 组件 Tag，以及产品 RC Tag。
- Produces: 新 Cloud Artifact、摘要、来源 Commit 和服务器验收记录；旧 RC8 保持不变。

- [ ] 更新 Workspace Cloud 包结构校验，移除旧 systemd/Nginx 文件要求，增加自包含部署文件要求。
- [ ] 运行 Manifest、Release 打包、Delivery 和 AI Workspace 校验。
- [ ] 提交并推送新的 Cloud 组件 Tag，不移动旧 Tag。
- [ ] 创建新的产品 Manifest 和产品 RC Tag，观察 GitHub Actions。
- [ ] 下载 Cloud Artifact，核对 SHA-256、Tag、Commit、架构、Migration、无敏感配置和包内验证脚本。
- [ ] 回写新的 Run、Artifact 和摘要，提交 Workspace 状态。

### Task 7: 宝塔服务器人工验收

**Files:**
- Modify: `delivery/active/CHG-20261003-077/server-acceptance.md`
- Modify: `delivery/active/CHG-20261003-077/checkpoint.md`

**Interfaces:**
- Consumes: Task 6 的新 Cloud Artifact 和用户持有的服务器、数据库、对象存储凭据。
- Produces: 真实宝塔部署、HTTPS、Web/API、登录、后台进程、回退边界和维护窗口证据。

- [ ] 用户按新手册上传并安装到新版本目录，配置宝塔 Go 项目和两个进程管理器条目。
- [ ] 用户执行数据库准备、Migration、`current` 切换和三个进程启动。
- [ ] 验证外部 HTTPS、Cloud Web、登录、数据库和后台进程，并回填验收记录。
- [ ] 只有实际服务器验收全部通过后，才评估 CHG-077 完成和归档。
