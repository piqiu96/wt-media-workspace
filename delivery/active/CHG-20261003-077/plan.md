# CHG-20261003-077 实施计划

## 技术方案

- Cloud Linux 包继续由既有 `build-release-linux.sh` 生成程序和 Web，再由 `package_release_linux.py` 组装。
- 包内新增 `migrations/`、`deploy/`、`config-template/` 和 `release-info.json`；敏感运行配置仍只在服务器 `shared/config` 注入，不由 GitHub 制品携带。
- 服务器采用固定安装根目录、按版本只读目录和 `current` 软链：
  - `releases/<product-tag>/`：包内容，不现场编译；
  - `shared/config/`：私有 TOML；
  - `shared/logs/`：进程日志；
  - `current`：当前版本软链。
- 数据库迁移使用包内 `bin/migrate --dir migrations --create-database=false`，目标库、账号和密码只来自服务器配置；数据库和账号由用户先用 SQL 模板创建。
- 初始管理员使用用户裁定的 RC 固定值 `admin / admin123`，由 `deploy/init-config.sh` 写入服务器私有配置，不在 Git 中保存口令。
- 进程管理提供 systemd 模板，分别守护 Server、Discovery Scheduler、Discovery Worker；宝塔反向代理只转发到 Server HTTP 地址。

## 有序任务

1. 记录 Q-01 裁定并激活 CHG。
2. 在 Cloud 新增部署脚本、配置初始化、进程模板、数据库 SQL 模板和部署手册，并扩展 Linux 包内容。
3. 增加包结构/脚本测试；在本地 MySQL 空库执行一次与重复迁移，启动 Server 验证健康和 `admin/admin123` 登录。
4. 提交并推送 Cloud 新组件 Tag；Workspace 固定新 Manifest 并推送产品 Tag，观察 GitHub Run。
5. 下载新 Cloud Artifact 核验包结构与摘要，输出服务器人工部署验收记录模板。
6. 用户在宝塔按手册执行；部署证据回填 CHG 后再判定是否完成。

## 验证计划

- Cloud 单元/脚本测试：包内容、无敏感配置、部署脚本语法与配置生成。
- 本地 MySQL：预先创建空库，执行迁移两次；查询 `schema_migrations` 与 `users`。
- 本地 Server：`/healthz`、`/api/v1/health`、`admin/admin123` 登录。
- GitHub：新组件 Tag 主干 CI 和产品 Tag Release Workflow 全部通过。
- 服务器人工验收：包摘要、配置权限、三进程状态、健康接口、登录和回退边界。
