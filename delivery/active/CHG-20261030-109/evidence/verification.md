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

- B站「测试账号」，序号 51，Cloud 窗口 10、账号 1：PASS。使用实时读出的自身 Cookie 值进行实际更新，Cloud 肯定允许前核实数据库完整写前值；真实平台 UID/昵称和读回一致。其他域 50 条 Cookie 的完整指纹不变；输入约 9,016 字节。
- 百度「路-华为」，序号 46，Cloud 窗口 37、账号 9：PASS。同样验证真实写入、身份和读回；其他域 60 条 Cookie 指纹不变；输入约 21,643 字节。该窗口存在浏览器合法的空名称 Cookie，修正 JSON 输入兼容并回归后通过；第一次校验拒绝时未授予写入。
- 两个平台均验证原始值不被后续更新覆盖、普通详情无凭证、重复起始/重复写前回报不再次授予执行、处理中解绑冲突、迟到编号冲突。模拟一次回报丢失后只读核实并结算，未重放写入。
- 验证通过生产 LocalApiServer/BitBrowser Client/CDP 实现与真实 Cloud API/MySQL 完成；不等同于已完成安装包点击路径。凭证值仅在进程内及业务数据库保存，不进入证据文件。

## 清理与组合门槛

旧 read-sync、旧 Cloud cookies 接口/DTO/全行更新、旧 Desktop Cookie-read 命令、Agent 保存值读取回退及无调用的 `/browser/cookie/save` 客户端已移除。提供方和直接消费者协调切换，Cloud API/Schema/Error 为 2026.10.30.3，Local API/Error 为 2026.10.30.2。

原 `wt chg verify` 集成步骤仍调用已退役 M1 noop 注册/租约链路，实测 import 已不存在；其脚本与现行产品无消费者，已移除，场景统一复用现有 `bin/control.sh verify`。没有以跳过失败冒充通过。

安装包已构建和挂载；移交 8765 端口后需运营桌面会话启动 Sidecar。当前 Mac 锁屏，CUA 明确要求人工解锁，已请求用户解锁。因此最终最新源组合重建、安装包登录/凭证/更新界面与红色失败反馈仍 PENDING，当前运行环境就绪检查也尚不能记 PASS。CHG-109 保持 VERIFYING，未合并/归档；CHG-110 尚未启动。
