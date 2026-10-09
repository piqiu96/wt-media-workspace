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
- [x] 提交 Workspace Evidence 和状态记录。

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

- [x] 更新 Workspace Cloud 包结构校验，移除旧 systemd/Nginx 文件要求，增加自包含部署文件要求。
- [x] 运行 Manifest、Release 打包、Delivery 和 AI Workspace 校验。
- [x] 提交并推送新的 Cloud 组件 Tag，不移动旧 Tag。
- [x] 创建新的产品 Manifest 和产品 RC Tag，观察 GitHub Actions。
- [x] 下载 Cloud Artifact，核对 SHA-256、Tag、Commit、架构、Migration、无敏感配置和包内验证脚本。
- [x] 回写新的 Run、Artifact 和摘要，提交 Workspace 状态。

### Task 7: 宝塔服务器人工验收

**Files:**
- Modify: `delivery/active/CHG-20261003-077/server-acceptance.md`
- Modify: `delivery/active/CHG-20261003-077/checkpoint.md`

**Interfaces:**
- Consumes: Task 6 的新 Cloud Artifact 和用户持有的服务器、数据库、对象存储凭据。
- Produces: 真实宝塔部署、HTTPS、Web/API、登录、后台进程、回退边界和维护窗口证据。

- [x] 用户于 2026-10-09 确认部署和宝塔运行验收完成；实际服务器 Tag、命令输出与路径未提供，见 `evidence/2026-10-09-manual-acceptance.md`。
- [x] 用户确认数据库当前态与三个进程正常；真实跨版本升级及回退延期至下次升级。
- [x] 用户确认外部 HTTPS、Web、登录与后台进程正常；详细服务器输出未提供，验收边界记录在 `server-acceptance.md`。
- [x] 已按用户人工确认、CI 与正式版回读证据评估 CHG-077 完成和归档；延期的跨版本升级不记作通过。

### Task 8: 用 wtmctl 收敛部署控制面并发布 RC12

**Files:**
- Add: `wt-media-cloud/cmd/wtmctl/main.go`
- Add: `wt-media-cloud/internal/deploy/*.go`
- Add: `wt-media-cloud/deploy/config-variable-schema.toml`
- Add: `wt-media-cloud/deploy/examples/*.toml.example`
- Delete: `wt-media-cloud/deploy/init-config.sh`、`render-config.py`、`install.sh`、`activate.sh`、`rollback.sh`、`migrate.sh`、`verify-package.sh`、`verify-database.sh`、`verify-runtime.sh`
- Delete: `wt-media-cloud/scripts/verify/test_deployment_package.py`
- Modify: `wt-media-cloud/README.md`、`deploy/DEPLOYMENT.md`、`.github/workflows/m0-cloud.yml`、`scripts/dev/build-release-linux.sh`、`scripts/dev/package_release_linux.py`、`scripts/verify/test_package_release_linux.py`
- Add: `wt-media-workspace/releases/manifests/v0.1.0-rc.12.yaml`
- Modify: `delivery/active/CHG-20261003-077/plan.md`、`checkpoint.md`、`server-acceptance.md`、`status/cloud.md`、`status/workspace.md`

**Interfaces:**
- Consumes: 用户确认的 wtmctl 收敛方案、TOML 变量表、online 预签名 URL。
- Produces: Cloud `v0.1.0-rc.9`（wtmctl 自包含部署）与产品 `v0.1.0-rc.12` Artifact、SHA-256 和服务器一键部署命令。

- [x] 实现并测试 `bin/wtmctl`：远程变量拉取、Schema/取值校验、Artifact 校验、渲染、Migration、数据库验证、安装、`current` 原子切换、只读验收、回退。
- [x] 移除依赖 Python/curl/mysql CLI 的逐条部署脚本；包内不再包含 `deploy/*.py`、`deploy/*.sh`。
- [x] 变量文件切换为 TOML，迁移本地 helper 与 `~/.wt-media/vars/cloud/{online,pre}.toml` 并上传，远端回读 SHA-256 一致。
- [x] 更新 Cloud `README.md` 与 `deploy/DEPLOYMENT.md`，新增 `/home/www/wt-media-cloud/output` 一键部署命令，目录可配置不写死。
- [x] 运行 Cloud Go/打包测试、变量拉取渲染端到端验证和 `git diff --check`。
- [x] 提交并推送 Cloud 组件 Tag `v0.1.0-rc.9`，`M0 Cloud` CI `37182796598` 通过。
- [x] 创建产品 Manifest `v0.1.0-rc.12` 与产品 Tag，Run `37182978601` 全绿。
- [x] 核对 Cloud Artifact：`bin/wtmctl`、无 `deploy/*.py|*.sh`、SHA-256 `90026317...6fb6`、Tag、Commit 均由 `package` 作业与 `build-info.json` 确认。
- [x] 回写 Run、Artifact 摘要与服务器一键部署命令。

### Task 9: 修正线上启动路径、二进制名与认证日志并发布 RC13

**Files:**
- Modify: `wt-media-cloud/internal/config/{root.go,config.go}`、`internal/bootstrap/routes.go`、`cmd/config-check/main.go`
- Modify: `wt-media-cloud/scripts/dev/*`、`internal/deploy/*`、`deploy/examples/online-deploy.toml.example`、`deploy/DEPLOYMENT.md`
- Modify: `wt-media-cloud/internal/middleware/identity.go`、`internal/modules/identity/handler.go`
- Add: `wt-media-cloud/internal/middleware/identity_test.go`、`internal/modules/identity/login_log_test.go`
- Add: `wt-media-workspace/releases/manifests/v0.1.0-rc.13.yaml`

**Interfaces:**
- Consumes: 用户报告的线上启动失败与 `auth/me` 401。
- Produces: Cloud `v0.1.0-rc.11` 与产品 `v0.1.0-rc.13`。

- [x] Server/Worker/Scheduler 从 `WT_MEDIA_CLOUD_HOME` → 二进制所在 `<home>/bin` → cwd 解析绝对根路径；`config/log/web` 由根路径派生并可用 `WT_MEDIA_CLOUD_{CONFIG,LOG,WEB}_PATH` 覆盖。
- [x] 发布二进制改名 `bin/server` → `bin/wt-media-cloud`（`cmd/server` 源目录不变），同步更新打包、包结构校验、`wtmctl` 进程检查与手册。
- [x] 相对 logger 路径锚定到日志目录，模板由 `logs/x.log` 改为 `x.log`。
- [x] 登录成功/失败与鉴权失败写入稳定 reason（invalid_credentials、session_replace_needed、session_invalid、missing_credential），带 IP/Origin/路径，不写密码或 token。
- [x] `wtmctl` 从包的 `release-info.json` 推导 `release`/`package_root`，安装类命令回退 `current`，示例 profile 不再固化版本。
- [x] 发布 Cloud `v0.1.0-rc.11` 与产品 `v0.1.0-rc.13`，回读 Artifact 摘要；RC13 Cloud tar SHA-256 见 `evidence/rc14-manual-tag-and-build.md`，服务器候选已升级为 RC14。

### Task 10: 固定运行根路径并补全启动诊断

**Files:**
- Modify: `wt-media-cloud/internal/config/root.go`、`root_test.go`、`config.go`
- Modify: `wt-media-cloud/internal/bootstrap/resource.go`、`bootstrap_test.go`
- Modify: `wt-media-cloud/cmd/migrate/main.go`、`cmd/config-check/main.go`
- Modify: `wt-media-cloud/deploy/DEPLOYMENT.md`、`README.md`
- Modify: `delivery/active/CHG-20261003-077/checkpoint.md`、`status/cloud.md`

**Interfaces:**
- Consumes: Task 9 的 `WT_MEDIA_CLOUD_HOME` 与 `WT_MEDIA_CLOUD_{CONFIG,LOG,WEB}_PATH`。
- Produces: 单一绝对 Cloud 根路径；默认 `config/`、`logs/`、`web/`、`migrations/` 均由该根路径派生，子路径覆盖值相对根路径解析；启动错误和成功路径可在宝塔进程日志与应用日志中定位。

- [x] 先写失败测试：发布目录 `bin/` 内缺少 `config/app.toml` 时仍从二进制位置确定根路径；任意 cwd 下相对子路径覆盖值锚定根路径；根路径覆盖值必须是绝对路径；迁移默认目录不依赖 cwd；资源初始化错误带步骤名。
- [x] 运行目标测试，确认针对上述缺口失败。
- [x] 实现路径解析与显式错误，不在发布布局中静默退回 cwd；本地开发继续使用 cwd；将迁移默认目录锚定根路径。
- [x] 启动时记录解析后的根、配置、日志、Web 路径，资源步骤失败时记录步骤与错误；日志不得包含口令、令牌或配置内容。
- [x] 运行目标 Go 测试、全仓 Go 测试、静态检查及部署包测试；核对从其他 cwd 启动的实际错误路径和日志。
- [x] 回写 Cloud 状态与 Evidence；发布新组件/产品 Tag 由本次验证结果和服务器验收决定，不移动既有 Tag。

### Task 11: 启动时一次初始化运行路径

**Files:**
- Modify: `wt-media-cloud/internal/config/root.go`、`config.go` 及对应测试
- Modify: `wt-media-cloud/internal/bootstrap/resource.go`、`routes.go`、`bootstrap_test.go`
- Modify: `wt-media-cloud/cmd/migrate/main.go`、`cmd/config-check/main.go`
- Modify: `wt-media-cloud/README.md`、`deploy/DEPLOYMENT.md`
- Modify: 本 CHG 的 Evidence、checkpoint 和 Cloud status

**Interfaces:**
- Consumes: Task 10 的单一根路径解析规则。
- Produces: 启动时解析并保存一次路径，运行代码通过 `config.GetRuntimePaths()` 读取；解析失败 panic，未初始化读取 panic。

- [x] 先写失败测试，确认未初始化的 `Load()` 不能回退到 cwd，根路径无效时启动资源必须 panic。
- [x] 使用进程级缓存与 getter 替换运行调用方的按需解析；保留现有 Server、Worker、Scheduler、Migration、配置检查入口的相同根路径规则。
- [x] 验证环境变化不会改变已保存路径；执行目标与全仓 Go 测试、静态检查、任意 cwd 的实际二进制启动检查。
- [x] 回写部署说明、Evidence、checkpoint 和 Cloud status；新发布与宝塔验收仍按 CHG 原有门槛处理。

### Task 12: 提交新组件 Tag 并手动触发产品打包发布

**Files:**
- Add: `wt-media-workspace/scripts/release/submit_tag.py`、`tests/test_submit_tag.py`
- Add: `wt-media-workspace/releases/manifests/v0.1.0-rc.14.yaml`
- Modify: 本 CHG 的 Evidence、checkpoint、status 与服务器验收版本信息

**Interfaces:**
- Consumes: Cloud Task 10/11 commits、已有 Agent/Desktop 固定 Tag、产品 Tag push 触发的 `release.yml`。
- Produces: Cloud `v0.1.0-rc.12` 与产品 `v0.1.0-rc.14`，后者由手动脚本提交 Tag，触发既有 GitHub Actions 构建/打包/预发布流水线。

- [x] 先写失败验证：未提交或未推送的 Manifest、重复 Tag、缺失组件 Tag 不得推送产品 Tag；显式 `--push` 时才提交 Tag。
- [x] 实现 Tag 提交脚本并验证 dry-run 和本地裸仓库的真实推送。
- [x] 校验并推送 Cloud 源码分支和新组件 Tag；校验并推送 Workspace 源码分支、新 Manifest 与产品 Tag。Cloud `v0.1.0-rc.12` 指向 `be1d1a1`，产品 `v0.1.0-rc.14` 指向 `7a781c3`。
- [x] 回读 GitHub Actions Run `37581481877`、全部构建结果、Cloud Artifact 和摘要，回写 `evidence/rc14-manual-tag-and-build.md`。

### Task 13: 宝塔服务器直拉固定 Cloud Artifact

**Files:**
- Modify: `delivery/milestones/M-first-production-release.md`
- Modify: `delivery/active/CHG-20261003-077/change.md`、`server-acceptance.md`、`checkpoint.md`、`status/workspace.md`
- Add: `delivery/active/CHG-20261003-077/evidence/server-direct-pull.md`

**Interfaces:**
- Consumes: 成功的 RC14 Run `37581481877`、私有 Workspace 仓库 Actions 只读权限、固定 Cloud tar SHA-256。
- Produces: 用户在服务器通过 GitHub CLI 直接拉取、核验和解压 Cloud 包，再执行现有 `wtmctl` 的可操作步骤。

- [x] 明确服务器直拉仍使用固定 RC14 Cloud Artifact；不在服务器重新编译源码或改变产品 Tag。
- [x] 在服务器验收记录中加入只读凭据、Run/Artifact 固定值、两层摘要核验和失败停止命令。
- [x] 执行文档命令的静态及本地制品核验，回写 `evidence/server-direct-pull.md` 和 checkpoint。
- [x] 用户于 2026-10-09 确认服务器部署验收完成；直拉命令与摘要的服务器输出未提供，见 `evidence/2026-10-09-manual-acceptance.md`。


## 2026-10-04 最终部署收敛方案（用户已确认）

- 部署控制二进制命名为 `bin/wtmctl`，不得使用 `wt-media-cloud`，避免与 Server 混淆。
- 变量文件从 JSON 改为 TOML：`online.toml`、`pre.toml`；支持注释和完整性 Schema。
- 服务器输出目录统一为 `/home/www/wt-media-cloud/output`，不再使用 `incoming`。
- `wtmctl` 支持远程变量拉取、变量完整性校验、Artifact 校验、配置渲染、Migration、数据库验证、版本安装、`current` 原子切换、只读部署验收和回退。
- `deploy apply` 是一键部署入口，内部自动拉取远程 TOML 变量；不启动、停止或重启任何服务。
- Server、Worker、Scheduler 继续由宝塔管理，`wtmctl` 不实现进程守护或 service 子命令。
- Cloud README 增加 `wtmctl` 部署命令；旧 Python 渲染器和逐条 shell 部署入口不再作为发布路径。
- 发布前必须完成变量 Schema 与模板一致性检查；部署前必须检查实际 TOML 必填值和 Secret。
