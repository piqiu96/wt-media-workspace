# CHG108 执行检查点

## 已完成

- 107四仓PR50/18/17/63已合入并归档；本项激活be58b71，唯一执行CHG108，109尚未启动。
- 用户明确要求example原型作为输入：Cloud web/example/proto/publishing-design复用既有BatchManager/BatchDetailContent/PublishComposer/common，108基线2512d342，页面映射见该目录README；根已看启动范围、单Profile、可信公开统计和稳定启动弹窗截图。
- Cloud API/Cloud-Agent/发布错误2026.11.25.2；最低新工作Agent同版本，Local API仍.1。提供方契约独立审查关闭；Workspace contract-map、Desktop ca44cba和Agent消费同步。ADR-0037记录协调升级与原核验安全结算。
- Cloud运行时7b4f523：原子start、固定组/暂停依据、Profile实际互斥、双容量、原键结算及迁移117。实现方Go全套及隔离MySQL发布/图片回归通过；独立Go源码审查无P1/P2。
- Vue89f49b6：164文件1212测试、Cloud/Desktop构建及受控Chromium通过，前端两轮发现已关闭。包括原版本/导航启动绑定、两标签原命令占有、未知重放与正式拒绝、stopping持续读回。
- Agent新增有界原线程执行、多现场可靠停车/恢复、跨scope原子Profile登记、核验原键Strict恢复、真实开窗前屏障、观察ACK hash和慢字节read1。独立审查8项及跟进发现均已分修，最终受控与真实验收仍未完成。

## 当前

Agent0d507e1最终949项通过，独立限定复审无阻断；Cloud7ba7844修真实安装版浮层“当前无任务”误导，23项定向和双构建通过，根已核对窄diff。四仓PR Cloud51、Agent19、Desktop18、Workspace64均已建立；前三项ready，Workspace待最终证据。Agent CI72、Desktop64和Workspace161通过，Cloud201执行中。

真实安装版批次2已显式确认60目标/1候选/59缺口，创建唯一task12/attempt35/group1，实际百度投稿1882771499985646302进入reviewing，自动步骤结束、批次ended，公开仍0/60。Web同批读回/复制占用提示/1024视口通过；批次1零候选start被阻止，填写原因终止后cancelled且0正式任务。总task7→8、attempt34→35，重建后仍唯一原attempt。

## 下一步

最新Cloud7ba7844的完整环境all已通过并重包；正在独立Agent稳定环境重跑正式wt chg verify（此前并发build移除DMG时检查器报no dmg，未掩盖）。随后launch-dmg重新登录，核对新浮层文案和实际公开结果。补齐V证据、CI/PR问题、main合入归档108后才启动109。用户授权完整流程持续有效。

## 升级现场

2026-11-25旧DB存在5个核验task（3/7/8/10/11），均涉及实际Profile dadb60405c354150a42811540654814f。已执行统一local_env.py stop，旧Cloud/Agent/Desktop及Worker/开发服务停止；8188/8765无监听。随后通过正式BitBrowserClient.is_profile_closed只读查询，返回closed=true。117实际迁移后legacy_check_count=5且门禁关闭，活跃holder0；再次核实原Profile关闭与旧PID退出后按README单行开放。DB UTC2026-11-24 20:03:40.261007读回verified，引用evidence/legacy-cutover.md，后续最新all门禁全部通过。

## 授权与限制

用户授权编码/测试/PR修复/真实E2E及最终走查，107–109由用户最后统一验收；测试凭据仅用会话指定值、不落仓。真实DeepSeek只发送已授权的标题/文案/要求/目标和资源数，不发送视频或凭证。实际仅1个本人百度账号，按用户确认少于N向下兼容；受控多Profile与真实单Profile证据分列。批次2修订2、目标60/候选1/缺口59，已保存真实AI与双封面、尚未启动，可供108使用。
