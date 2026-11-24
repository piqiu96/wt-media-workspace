# CHG108 执行检查点

## 已完成

- 107四仓PR50/18/17/63已合入并归档；本项激活be58b71，唯一执行CHG108，109尚未启动。
- 用户明确要求example原型作为输入：Cloud web/example/proto/publishing-design复用既有BatchManager/BatchDetailContent/PublishComposer/common，108基线2512d342，页面映射见该目录README；根已看启动范围、单Profile、可信公开统计和稳定启动弹窗截图。
- Cloud API/Cloud-Agent/发布错误2026.11.25.2；最低新工作Agent同版本，Local API仍.1。提供方契约独立审查关闭；Workspace contract-map、Desktop ca44cba和Agent消费同步。ADR-0037记录协调升级与原核验安全结算。
- Cloud运行时7b4f523：原子start、固定组/暂停依据、Profile实际互斥、双容量、原键结算及迁移117。实现方Go全套及隔离MySQL发布/图片回归通过；独立Go源码审查无P1/P2。
- Vue89f49b6：164文件1212测试、Cloud/Desktop构建及受控Chromium通过，前端两轮发现已关闭。包括原版本/导航启动绑定、两标签原命令占有、未知重放与正式拒绝、stopping持续读回。
- Agent新增有界原线程执行、多现场可靠停车/恢复、跨scope原子Profile登记、核验原键Strict恢复、真实开窗前屏障、观察ACK hash和慢字节read1。独立审查8项及跟进发现均已分修，最终受控与真实验收仍未完成。

## 当前

Agent0d507e1正在收口最终全套和有限复审。最新定向18轮询、37核验、19装配、8下载与24Source通过；此前091b333全套运行日志/tmp/chg108-agent-final-091b333.log待核对完整结果。Desktop既有Rust/打包/协议锁测试已通过。本项各仓尚无108PR，验收清单保持未勾选。

## 下一步

最终复审/全套→提交Workspace共同定义与证据→四仓PR/CI→最新全流程环境重建及旧核验安全门禁→Web/安装版真实单Profile和故障验收→修复→main合入归档108→启动109。用户已授权整个流程，不重复请求106签收或AI许可。

## 升级现场

2026-11-25旧DB存在5个核验task（3/7/8/10/11），均涉及实际Profile dadb60405c354150a42811540654814f。已执行统一local_env.py stop，旧Cloud/Agent/Desktop及Worker/开发服务停止；8188/8765无监听。随后通过正式BitBrowserClient.is_profile_closed只读查询，返回closed=true。尚未运行117实际迁移或写开放门禁，后续必须记录迁移后状态及证据引用，不能依代次/超时放行。

## 授权与限制

用户授权编码/测试/PR修复/真实E2E及最终走查，107–109由用户最后统一验收；测试凭据仅用会话指定值、不落仓。真实DeepSeek只发送已授权的标题/文案/要求/目标和资源数，不发送视频或凭证。实际仅1个本人百度账号，按用户确认少于N向下兼容；受控多Profile与真实单Profile证据分列。批次2修订2、目标60/候选1/缺口59，已保存真实AI与双封面、尚未启动，可供108使用。
