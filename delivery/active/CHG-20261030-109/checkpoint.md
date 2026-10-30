# CHG-109 接续

## 已完成

- 108 已合入四仓 main 并归档；109 四仓分支为 `chg/CHG-20261030-109`，当前 VERIFYING。
- Cloud `bfe7691`：迁移 084、凭证与单条 Cookie 当前处理、窗口占用、界面/编排及旧链路清理。Agent `ef645d0`：真实 prepare/apply/inspect、域隔离、完整属性和实时读取。Desktop `0c89ca9`：新命令、DTO、契约锁。
- 真实 B站（账号 1 / 窗口 10 / 测试账号）及百度（账号 9 / 窗口 37 / 路-华为）写入/平台/Cloud/MySQL 已验；其他域 50 / 60 条 Cookie 不变。详见 evidence。
- Vue 883、Agent 662、Desktop 535、Workspace 179 测试通过；修正新增重复 UID 用例的 fixture 后，账号模块重新全通过。当前运行仓提交已推送，Draft PR 已发起。
- 旧 M1 noop 验证脚本仍调用已退役模块，已移除；`wt test integration` 统一使用现有 `bin/control.sh verify`。

## 当前与阻塞

Mac 锁屏；CUA 明确无法操作，已异步请求用户解锁。新 DMG 已构建挂载，移交 8765 后桌面运营会话尚未启动 Sidecar，所以不能记环境或最终界面 PASS。不得使用旧 UI、直接 Service 实测或代码存在冒充安装包点击验证。最终源组合还需重建。

## 下一步

1. 用户解锁后，运行 `bin/control.sh start` 全量刷新当前组合，必要时在新安装包登录已约定运营测试账号；确认 Sidecar 与就绪门槛。
2. 最终源真实窗口 prepare/apply/inspect（仍只用上述授权窗口，使用自身实时值，不触及其他窗口），验证原始/当前凭证、失败红色反馈与核实交互；重跑当前集成门槛。
3. 核查四仓 Draft PR 的 CI 与 diff，证据全部 PASS 后转正式 PR、merge commit、更新本地 main、归档 109。
4. 按依赖启动 110，完成批量 JSON 接入和最终废弃代码/文档清理，再交人工走查。未获依赖闭环前不提前建立批次业务对象。

## 工作区注意

Workspace 原有 `example/README.md`、`example/proto/README.md`、`example/proto/publishing-interaction/` 为用户发布原型改动，保持未提交，不覆盖或混入 CHG。
