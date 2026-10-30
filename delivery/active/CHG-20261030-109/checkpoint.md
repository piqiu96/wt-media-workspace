# CHG-109 接续

## 已完成

- 108 已合入四仓 main 并归档；109 四仓分支为 `chg/CHG-20261030-109`，当前 VERIFYING。
- Cloud `bfe7691`：迁移 084、凭证与单条 Cookie 当前处理、窗口占用、界面/编排及旧链路清理。Agent `ef645d0`：真实 prepare/apply/inspect、域隔离、完整属性和实时读取。Desktop `0c89ca9`：新命令、DTO、契约锁。
- 真实 B站（账号 1 / 窗口 10 / 测试账号）及百度（账号 9 / 窗口 37 / 路-华为）写入/平台/Cloud/MySQL 已验；其他域 50 / 60 条 Cookie 不变。详见 evidence。
- Vue 883、Agent 662、Desktop 535、Workspace 179 测试通过；修正新增重复 UID 用例的 fixture 后，账号模块重新全通过。四仓 Draft PR（Cloud #18 / Agent #6 / Desktop #8 / Workspace #20）的 CI 均 SUCCESS。最终源 B站/百度真实链路和 MySQL 集成再次通过。
- 旧 M1 noop 验证脚本仍调用已退役模块，已移除；`wt test integration` 统一使用现有 `bin/control.sh verify`。

## 当前与下一步

用户已解锁；最新组合完整重建、DMG 登录、认证 Sidecar 就绪与凭证界面均已验。B站桌面真实更新成功；无效输入为红色错误；百度旧样本的过期项产生待确认，实际只读核实收敛明确失败，随后检查登录正常。详见 evidence。

四仓 CI 通过。提交最终证据后合并四仓 PR、同步 main 并归档；然后按用户指令启动 110。无当前阻塞。

## 工作区注意

Workspace 原有 `example/README.md`、`example/proto/README.md`、`example/proto/publishing-interaction/` 为用户发布原型改动，保持未提交，不覆盖或混入 CHG。
