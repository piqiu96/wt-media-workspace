# 宝塔 Cloud 部署目录与进程管理设计

- 日期：2026-10-04
- 状态：已确认
- 关联交付：`CHG-20261003-077`

## 1. 目标

Cloud 通过 GitHub 生成 Linux amd64 部署包，由操作者上传宝塔服务器。服务器使用固定路径配置三个常驻进程，并允许按产品 Tag 安装、切换和保留少量历史版本。运行密钥只存在服务器，不进入 Git、GitHub Release Manifest 或构建制品。

本设计优先降低首次上线和后续人工发布的操作复杂度，同时保留清晰的版本回退入口。

## 2. 已确认方案

1. Cloud 安装根目录固定为 `/www/wt-media-cloud`。
2. 每个版本完整安装到 `/www/wt-media-cloud/releases/<product-tag>/`。
3. `current` 是唯一运行入口，原子指向一个完整版本目录。
4. 不使用 `shared/`。每个版本自行包含实际 `config/`、`logs/` 和 `data/tmp/`。
5. GitHub 部署包只携带带变量占位符的配置模板和渲染/校验工具；部署时按显式环境拉取变量表，在目标版本内生成实际 `config/`，真实变量不能进入制品。
6. Server 由宝塔 Go 项目管理；Discovery Scheduler 和 Discovery Worker 由宝塔进程管理器分别管理。
7. 三个进程都使用 `www` 用户和 `/www/wt-media-cloud/current` 工作目录。
8. 不再使用 systemd 管理这三个进程，也不为 Scheduler 或 Worker 配置虚假监听端口。
9. 为了让宝塔 Go 项目统一管理域名、反向代理和 HTTPS，Cloud Server 同时提供包内 Cloud Web 静态文件，并支持 Vue history 路由回退。`/api/` 和 `/healthz` 继续由原有 API 路由处理。

## 3. 目录结构

```text
/www/wt-media-cloud/
├── releases/
│   ├── v0.1.0-rc.8/
│   │   ├── bin/
│   │   │   ├── server
│   │   │   ├── discovery-scheduler
│   │   │   ├── discovery-worker
│   │   │   ├── migrate
│   │   │   ├── ffmpeg
│   │   │   └── ffprobe
│   │   ├── web/
│   │   ├── migrations/
│   │   ├── deploy/
│   │   ├── config/
│   │   ├── logs/
│   │   ├── data/tmp/
│   │   └── release-info.json
│   └── v0.1.0-rc.9/
└── current -> releases/v0.1.0-rc.8
```

`bin/`、`web/`、`migrations/`、`deploy/` 和 `release-info.json` 来自构建制品。`config/`、`logs/` 和 `data/tmp/` 在服务器安装时创建，不由 GitHub 打包真实内容。

不在根目录分别创建 `bin`、`web` 等多个软链。一个 `current` 软链保证程序、Web、Migration 和配置属于同一版本，避免部分路径已经切换、部分路径仍指向旧版本。

## 4. 宝塔进程配置

### 4.1 Server

宝塔 Go 项目使用：

- 可执行文件：`/www/wt-media-cloud/current/bin/server`
- 启动命令：直接执行上述文件
- 工作目录：`/www/wt-media-cloud/current`
- 运行用户：`www`
- 应用端口：`8080`
- 对外域名：实际 Cloud 域名
- HTTPS：由宝塔站点配置和续期
- 防火墙：不直接向公网开放 `8080`

Server 必须同时提供 `current/web` 中的 Cloud Web。访问真实静态文件时返回文件；访问 `/login` 等前端路由时回退到 `index.cloud.html`；API 和健康接口不能被前端回退覆盖。

### 4.2 Scheduler 与 Worker

宝塔进程管理器创建两个独立条目：

| 名称 | 启动命令 | 工作目录 | 用户 |
| --- | --- | --- | --- |
| `wt-media-cloud-scheduler` | `/www/wt-media-cloud/current/bin/discovery-scheduler` | `/www/wt-media-cloud/current` | `www` |
| `wt-media-cloud-worker` | `/www/wt-media-cloud/current/bin/discovery-worker` | `/www/wt-media-cloud/current` | `www` |

两个条目必须开启开机启动和异常退出自动拉起。它们是无监听端口的后台进程，不绑定域名，不开放防火墙端口。

## 5. 配置与密钥

配置模板以 `.toml.tpl` 进入制品，使用显式占位符引用环境变量。预发和生产共用同一套模板与渲染工具，部署时通过 `--environment staging|production` 和对应远程变量表生成目标版本的 `config/`。Tag 标识代码版本，部署参数决定运行环境，不能根据 RC 或正式 Tag 隐式猜测环境。

部署脚本支持 HTTPS 拉取远程变量表，也支持已下载的本地变量表用于故障恢复。变量表作为数据解析，不能使用 Shell `source` 执行；替换工具只接受模板实际声明的变量，缺少变量、存在未知变量、残留占位符或生成非法 TOML 时必须失败。生成后还必须调用 Cloud 自身的配置解析和业务校验入口，校验不通过时不能迁移或切换。

每次升级都使用所选环境的变量表重新渲染，不能默认复制 `current/config/`。这样同一制品可以部署到预发和生产，并避免把某一环境的数据库、对象存储或认证信息继承到另一环境。渲染记录只保存环境名、变量表摘要和时间，不保存变量值。

私有配置目录和文件要求：

- 所有者和所属组统一为 `www:www`；
- 目录权限为 `0700`；
- 文件权限为 `0600`；
- 数据库密码、对象存储密钥、平台凭据和初始管理员口令不能写入命令历史、Git、Manifest、Artifact 或交付记录；
- 保留用于回退的旧版本也会保留一份私有配置，因此密钥轮换时必须同步更新所有仍允许回退的版本，或取消对应旧版本的回退资格。

配置属于具体版本，回退 `current` 时程序与匹配的旧配置一起切回。配置变更应记录版本、修改时间和操作者，但记录中不保存密钥值。

## 6. 发布与切换

一次正常升级按以下顺序执行：

1. 下载并校验 GitHub Artifact 和 SHA-256。
2. 解压到新的 `releases/<product-tag>/`；已存在的同名版本不得覆盖。
3. 创建该版本的 `config/`、`logs/` 和 `data/tmp/`，设置所有者和权限。
4. 指定 `staging` 或 `production`，拉取对应变量表，在新版本内渲染配置并执行语法与业务校验。
5. 在维护状态下备份 MySQL 和需要保护的对象存储数据。
6. 使用新版本的 `bin/migrate` 对显式目标数据库执行 Migration；重复执行应为零个新增迁移。
7. 依次停止 Scheduler、Worker、Server，等待进程完全退出。
8. 原子地把 `current` 切换到新版本。
9. 依次启动 Server、Worker、Scheduler。
10. 验证本机健康接口、外部 HTTPS、Cloud Web 首页和深层路由、管理员登录、数据库版本及两个后台进程。
11. 所有验收通过后解除维护状态。

切换 `current` 本身不会替换已经运行的进程。发布和回退都必须停止并重新启动三个进程。

## 7. 失败与回退

- 解压、配置校验或 Migration 失败时，不切换 `current`，保持旧版本运行或维持维护状态。
- 切换后运行验证失败时，先停止三个新进程。
- 只有数据库和外部数据仍与旧版本兼容时，才允许把 `current` 切回旧版本并重新启动。
- 存在不兼容 Migration 或外部副作用时，不能只切换软链；必须恢复事先验证过的数据库和对象存储一致快照。
- 回退完成后重新验证 HTTPS、Web、API、登录和后台进程，才允许解除维护状态。

服务器至少保留当前版本和上一个已验收版本。清理脚本不得删除 `current` 实际指向的目录；删除旧版本会同时删除该版本的配置和日志，执行前必须确认其已不再承担回退和审计用途。

## 8. 验证要求

实现和服务器验收至少覆盖：

- 安装脚本生成自包含版本目录，且制品不含真实凭据；
- `current` 原子切换，不产生多路径混合版本；
- 三个宝塔进程从固定路径以 `www` 用户启动；
- Server 提供 Cloud Web、Vue 深层路由、`/healthz` 和 `/api/v1/health`；
- Scheduler 和 Worker 无监听端口也能被进程管理器正常启停、自动拉起和查看日志；
- 同一套模板能分别使用预发和生产变量表生成有效配置，且生成结果经过占位符、TOML、Cloud 业务规则和权限校验；
- 首次 Migration、重复 Migration、管理员登录和回退边界符合预期；
- 外部只能访问宝塔公开的 HTTP/HTTPS 入口，MySQL 和 Server 内部端口不直接暴露公网。

## 9. 明确排除

- 不使用 `shared/` 目录。
- 不使用 systemd 管理 Cloud 三进程。
- 不把 Scheduler 或 Worker注册成带虚假端口的宝塔 Go 项目。
- 不在服务器现场编译 Go 或 Web。
- 不自动 SSH 部署。
- 不承诺软链切换能够撤销数据库 Migration 或已经发生的外部业务副作用。
