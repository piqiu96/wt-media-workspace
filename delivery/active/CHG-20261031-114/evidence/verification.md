# CHG-20261031-114 验证

2026-10-31；固定 MySQL `127.0.0.1:3306/wt_media_cloud`；业务验收仅操作本地授权测试用户 12。

| 验证 | 预期 | 实际 | 结果 |
| --- | --- | --- | --- |
| 社媒账号 Go 模块 | 同 UID 多窗口检查、Cookie 结算和批次完成；真实异 UID、重报、过期结果维持原语义 | `go test ./internal/modules/mediaaccount/...` 全部通过；覆盖两行同 UID 独立记录、后续继续、重复回报无重复记录、旧跳过恢复无执行授权 | PASS |
| Cloud 模块 | 无移除符号残留及调用回归 | `go test ./internal/modules/...` 通过 | PASS |
| 真实 MySQL | UID 非唯一、窗口平台仍唯一；迁移不伪造正常、不损坏批次数组 | `WT_MEDIA_MYSQL_TEST_DSN=... go test ./internal/modules/mediaaccount/...` 通过；隔离表迁移保留行号 9/3/5、原操作与凭证；原错误重复回到待检查，旧批次待核实，跳过项保持跳过 | PASS |
| 读取投影 | 仅本人同平台同 UID 的不同窗口提示；不更改登录和 Cookie | MySQL 临时表回归覆盖其他用户不暴露、双向提示及各自窗口/凭证/正常结果保留 | PASS |
| 共用前端 | 列表常规操作、详情可选入口、接入成功计数与查看当前记录 | 全量 110 文件 / 939 项通过；末次接入说明调整后相关测试再次通过；Cloud Web 构建通过 | PASS |
| Workspace | 当前事实和交付一致 | 179 项测试、docs governance、config verification、Delivery governance、原型 JS 语法通过 | PASS |
| 最新安装包 | 新源码构建，Cloud/Agent/BitBrowser/双前端/DMG/登录正常 | `bin/control.sh start` 全流程通过，迁移 086 实际应用；挂载私有目录并运行最新 DMG | PASS |
| 两个真实已有窗口 | 相同 UID 不误判，分别可检查和打开 | ID 12 从待识别回填「菠萝爱玩洛克」/ UID 3706991279082195；ID 10 同 UID，两者检查正常，分别成功打开 CHG110验收-bilibili-7-1 / -7-3 | PASS |
| 详情与列表 | 顶部公共样式提示，只详情保留可选入口 | 原生安装包截图显示顶部蓝色提示；ID 12 可选查看 ID 10，当前记录状态正常；列表无专门“查看已有账号”按钮 | PASS |
| 历史只读核实 | 不创建新窗口或重写 Cookie，使用原操作结算 | 批次 17 / 行 4，原窗口 941 / CHG110人工继续-17，通过核实结果完成，新增本窗口记录 ID 13，百度 UID 6572476037，状态正常 | PASS |
| 真实两行新接入 | 同 UID 新窗口自动完成并继续下一行 | 批次 22 / 行 1、2 自动成功，账号 ID 14、15，窗口 ID 952、959（账号接入 22-1、22-2）；两行均“已存在，本窗口已接入”；查看第一行打开 ID 14 | PASS |
| 已有记录不受影响 | 不修改其他窗口关联与凭证 | 前后比对 ID 10、11、12 的 browser_profile_id、original_cookie、active_cookie 的 SHA-256：全部相同（不保存明文到 evidence） | PASS |

Cloud 核心提交 `9b3b4bf`，末次页面说明提交 `2ab4b4a`；Agent `6fb30d9`、Desktop `bd10f0d` 未修改运行协议与代码。前端唯一源码仍在 Cloud。Cloud API / business schemas / enums / errors revision 为 `2026.10.31.1`；Agent/Desktop 消费的本机协议和锁未变化。

截图位于 `/Users/aqiuye/Downloads/社媒账号样式走查-20261031/CHG114-同账号多窗口/`：

- `01-详情顶部提示.png`
- `02-旧记录核实后正常接入.png`
- `03-两行同账号自动接入完成.png`

人工复核入口：[manual-checklist.md](manual-checklist.md)。本次自行验证不代替运营最终产品走查，M2-D 总体仍按人工验收状态维护。

末次复核：`bin/control.sh start` 再次全流程通过，最终包前端版本 `0.1.0+2ab4b4a`。原生界面确认接入说明已更新；按窗口名综合搜索 ID 12，列表仍无专门跳转，详情顶部提示与正常状态一致。补充截图 `04-最终包列表无专门跳转.png`、`05-最终包详情顶部提示.png`。授权临时 Cookie 输入文件已删除；evidence 不包含明文凭证。
