# M-launch-engineering：上线前联合工程优化

- 日期：2026-09-23
- 状态：执行中（CHG-A、CHG-B 已于 2026-09-24 归档 `DONE`、**C 已于 2026-09-25 归档 `DONE`**；
  **成功事实 #5 由 CHG-B 达成**（见 [CHG-20260923-057](../completed/CHG-20260923-057/change.md)）、
  **#6 由 CHG-C 达成**（见 [CHG-20260923-058](../completed/CHG-20260923-058/change.md)）；
  用户操作第 2 条的本机设置入口也已由 C 交付；D 仍 planned 待激活）
- 程序总纲：`docs/engineering/specs/2026-09-23-launch-engineering-optimization-program.md`
- 关联 CHG：CHG-20260923-056（A）、CHG-20260923-057（B）、CHG-20260923-058（C）、CHG-20260923-059（D）
- 性质：工程加固（非业务里程碑）；不改变 M2/M3 已验收业务闭环

## 闭环卡

### 用户目标

Desktop 与 Agent 在正式上线前达到可长期部署、可诊断、可升级的工程形态：配置可换环境、Client 可注入可测试、日志独立落盘按天保留、运行目录按环境隔离、正式安装包可脱离开发环境运行，且运营能安全查看与清理本机文件和日志。

### 前置

- M2、M3 已验收（业务基线冻结，本程序不改变业务闭环）。
- ADR-0016 已 Accepted（Agent 分层与配置目录基线）。

### 用户操作（验收形态）

1. 开发者：以配置文件+环境变量切换环境，无需改代码；跑全部测试不误连真实外部服务。
2. 运营：安装正式包后正常启动使用；在本机设置中查看/修改保存位置、查看日志、清理缓存与旧日志、导出脱敏诊断信息。
3. 升级安装不丢用户配置、SQLite、检查点与待回传结果。

### 系统与外部动作

- Agent：runtime 收口、bootstrap 真实组装、clients/services 分层、配置目录 config/+config_online/、日志落盘轮转清理脱敏。
- Desktop：模块拆分、强类型配置、AppPaths、用户设置持久化、本机管理命令与页面、Sidecar 生命周期与受控传参。
- Cloud Web（仅 desktop app）：Cloud 地址改受控获取、healthz 改走 command。
- 打包：PyInstaller 产物完整、config_online 替换、版本兼容校验。

### 成功事实（全部成立）

1. Agent 可脱离 Desktop 独立启动；三种模式（Local/Cloud/sidecar）各有真实启动与健康输出记录。
2. 已审计确认的硬编码（端口 8765/18080、超时、BitBrowser 地址散落）全部进配置或常量，grep 无残留。
3. Desktop `cargo test`、Agent unittest（基线 ≥85 且不减少）、Web 测试全绿。
4. 既有 M2 链路（bind/account_check/cookie_read/profile）dev 模式回归通过。
5. 日志独立落盘、按小时轮转、**按天保留**（超过保留天数的归档自动删除；不控总量）；敏感信息（Cookie/Token/代理密码）不进日志与诊断包。
6. 清理缓存/旧日志不删业务文件与运行数据；读取失败不显示 0 MB。
7. 正式安装包脱离开发源码/venv/开发机路径可运行；发布可追溯五类版本（Desktop/Agent/前端/Contract/资源）。
8. 升级不覆盖用户配置、SQLite、检查点与待回传结果。

### 失败行为（不得出现）

- 因普通用户设置环境变量将正式包重定向到未知服务。
- 测试误连真实外部服务产生副作用。
- 配置写入一半损坏用户设置且静默清空。
- 执行成功被当作业务成功上报；外部副作用操作盲目重试。
- 升级或清理删除业务数据。
