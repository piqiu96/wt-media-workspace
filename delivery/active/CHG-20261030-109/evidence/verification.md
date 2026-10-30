# CHG-109 验证事实

代码提交：Cloud `bfe7691`、Agent `ef645d0`、Desktop `0c89ca9`。

2026-10-30，本机固定数据库 `wt_media_cloud`。当前为 VERIFYING，尚未归档。

| 验证 | 实际结果 |
| --- | --- |
| 追加迁移 084 | PASS；仅账号 before_cookie/cookie_update 和窗口 cookie_operation_id；未新增版本/历史/明细表 |
| Cloud 账号模块定向测试 | PASS；当前请求去重、同 key 不同输入冲突、写前拒绝、明确失败保留、未知占用、旧结果、重复结算、重复 UID 定位已有账号、旧检查失效 |
| MySQL 临时表集成 | PASS；从真实表 DDL 建临时表验证保存/回滚、跨账号跨平台占用和绑定阻断；不改现有业务记录 |
| Vue | PASS；101 文件、883 测试；含未获 can_apply 不写、重复起始不执行、丢失写回报为未知、恢复只 inspect |
| Agent | PASS；662 测试；实时域隔离、完整属性、写前指纹变化拒绝、读回/身份、跨域不变、只读 inspect、大响应分帧读取；移除存量 Cookie 回退和无消费者写入接口 |
| Desktop | PASS；535 测试、6 个既有 ignore；受控 prepare/apply/inspect 命令和 DTO；无前端直连本机端口 |
| Workspace | PASS；179 测试、契约映射、Delivery、文档、控制脚本校验 |

## 真实平台读写

只使用用户明确指定的两个窗口。没有向其他窗口写 Cookie，没有清空窗口或全域 Cookie。

- B站「测试账号」，序号 51，Cloud 窗口 10、账号 1：PASS。使用实时读出的自身 Cookie 值进行实际更新，Cloud 肯定允许前核实数据库完整写前值；真实平台 UID/昵称和读回一致。其他域 50 条 Cookie 的完整指纹不变；最终源复验输入约 9,030 字节。
- 百度「路-华为」，序号 46，Cloud 窗口 37、账号 9：PASS。同样验证真实写入、身份和读回；其他域 60 条 Cookie 指纹不变；最终源复验输入约 21,337 字节。该窗口存在浏览器合法的空名称 Cookie，修正 JSON 输入兼容并回归后通过；第一次校验拒绝时未授予写入。
- 两个平台均验证原始值不被后续更新覆盖、普通详情无凭证、重复起始/重复写前回报不再次授予执行、处理中解绑冲突、迟到编号冲突。模拟一次回报丢失后只读核实并结算，未重放写入。
- 验证通过生产 LocalApiServer/BitBrowser Client/CDP 实现与真实 Cloud API/MySQL 完成；不等同于已完成安装包点击路径。凭证值仅在进程内及业务数据库保存，不进入证据文件。

## 四仓评审

四仓 Draft PR 的 CI 均为 SUCCESS：

- [Cloud #18](https://github.com/piqiu96/wt-media-cloud/pull/18)：完整 Go/Vue、重复迁移与发布构建通过。
- [Agent #6](https://github.com/piqiu96/wt-media-agent/pull/6)：测试、SQLite 迁移与构建通过。
- [Desktop #8](https://github.com/piqiu96/wt-media-desktop/pull/8)：原生及发布脚本测试通过。
- [Workspace #20](https://github.com/piqiu96/wt-media-workspace/pull/20)：治理验证通过。

最终提交的 B站/百度真实链路及 MySQL 两组集成均再次通过。

## 最新安装包走查

用户解锁后执行 `bin/control.sh start`，迁移、最新源构建、Cloud/Agent/worker/BitBrowser、两种前端、运行时 origin、DMG 和登录门槛全部 PASS，随后由新 DMG 接管 Agent。运营账号登录后，桌面「工作环境」显示“这台电脑可以工作 / 本机服务已连接 / 比特浏览器已登录指定账号 / 执行凭证已配置”。

- B站：在新安装包打开账号凭证，确认当前/首次 Cookie 默认遮罩、可复制且没有写前备份等技术操作。应用内复制当前值后，经更新表单和目标确认实际调用 Sidecar；完成后表单关闭、列表正常，重新打开凭证，最近同步时间从 16:42:56 更新至 19:16:52。PASS。
- 无效输入：输入 `INVALIDCOOKIEINPUT` 并确认，显示红色错误 toast 和红色表单提示“Cookie 格式不正确，请检查后重试”，输入保留；未获写入授权。PASS。
- 百度：用此前保存的完整 Cookie 在同账号同窗口更新，进入待确认，界面只提供打开窗口/核实；点击核实后返回明确失败并恢复重新输入。只读核查发现旧输入的 `ab_sr` 已过期消失，其余 63 项值一致；系统没有将未完整生效报成功，也没有在核实时重写。随后桌面手动检查返回“登录正常”，UID 保持一致。PASS。两平台真实成功写入已由上节实时样本验证。
- `bin/control.sh verify` 在移交端口后按既有设计拒绝无 token 检查桌面 Agent；这不是环境就绪 PASS。组合命令在移交前的各门槛已通过，移交后的认证就绪以安装包工作环境及实际 Cookie 桥接操作验证，未修改鉴权或伪造检查结果。

## 清理与组合门槛

旧 read-sync、旧 Cloud cookies 接口/DTO/全行更新、旧 Desktop Cookie-read 命令、Agent 保存值读取回退及无调用的 `/browser/cookie/save` 客户端已移除。提供方和直接消费者协调切换，Cloud API/Schema/Error 为 2026.10.30.3，Local API/Error 为 2026.10.30.2。

原 `wt chg verify` 集成步骤仍调用已退役 M1 noop 注册/租约链路，实测 import 已不存在；其脚本与现行产品无消费者，已移除，场景统一复用现有 `bin/control.sh verify`。没有以跳过失败冒充通过。

最新源组合构建、桌面认证就绪、成功更新、红色失败反馈、真实待确认及只读核实均已完成。最终人工产品走查由用户进行。
