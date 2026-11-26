# CHG131 验证记录

2026-11-27，隔离工作树基于已推送origin/main；无依赖130提交，不触碰原工作树设计修改。

- `WT_MEDIA_TEST_LIVE_DB=1 WT_MEDIA_CLOUD_HOME=<131 Cloud> go test ./internal/modules/work/... -count=1 -v`：PASS。隔离MySQL schema，应用真实112作品DDL（仅移除不相关外键）和119迁移并验证重放；覆盖双领取竞争/本人类目、手动合并、成功和失败、旧值保留、快照、超时重领及迟到回报。
- `go test ./internal/modules/work/... ./internal/modules/cloudagent ./internal/bootstrap`：PASS。
- Web `npm test`：168文件/1247项PASS；按原型改为紧凑列后作品9项定向PASS。
- Agent `PYTHONPATH=src .../python -m unittest discover -s tests -q`：955项PASS，含六项API parser/身份、缺字段、类型/范围、限流、Cloud claim和轮询token切换测试；Local/Sidecar装配22项PASS。
- Workspace `verify_m0_config.py`：PASS。

初次提交时的待验项目由下方后续实测承接；这些项目已完成，见文末最终交付。

## 真实链路与浏览器

- 原始公开作品16，aid117683798410574，原任务30/尝试82/成片153。生产Agent `read_metrics` 无Cookie读取并校验aid/UID，经真实HTTP领取、回报到Cloud；7/1/2/0/0/0与独立公开API读取一致（real-e2e-result.json）。
- 五个已有B站作品均取得真实六项，包含作品12投币2、收藏1；见five-real-works.json。不是只用零值fixture验证。
- 手动POST刷新先queued，再实际Agent采集为ready，成功时间更新，发布事实不变；百度metrics为null（manual-refresh-result.json）。
- CUA实际打开in-app浏览器5173/work，以operator01正常登录，1440×900核对列表六项和更新时间、详情六张卡片、原任务30/尝试82/成片153回链。
- 首轮发现右侧操作栏遮挡指标；f77ebcc前移紧凑指标组并合并更新时间，实际截图已核实六项同时可见。
- 明确故障注入：测试驱动让Agent collector返回rate_limited（不代表真实B站限流），Cloud保存失败但不覆盖旧值/成功时间；浏览器详情仍显示7/1/2/0/0/0并提示平台请求受限。随后用真实API恢复ready（02:33:31），发布时间/来源不变。
- PR审查指出同一详情替换会重置滚动，24bac48修复；自动/手动刷新保留滚动回归PASS。取消手动请求额外30秒冷却，仅合并活动租约和队列；实际平台读取仍由Agent正常30秒轮询限制。
- 最终定向作品页10项PASS。Web全量168文件1248项PASS（--maxWorkers=2，30.46s）；曾在并行打包时发生既有localSettingsWiring导入测试5秒超时，单独重跑9项PASS，随后全量PASS，未修改超时阈值。
- Cloud模块全量PASS；Workspace220项PASS；Desktop契约锁同步，配置/架构边界校验PASS。

PR：Cloud60（当前70f0282）、Agent22（ca10699）、Desktop21（仅契约锁）、Workspace73。四仓CI均已PASS，最终环境和浏览器/安装版恢复均通过。当前验证组合同时包含未合并130，采集本身只读已有B站公开work；新作品入库继续由130提供，不增加手工导入或冒充新发布。

## 最终源码复验（8c0b121）

- 130+131组合 `npm test -- --maxWorkers=2`：174文件/1285项PASS。
- 130+131组合 Agent 全量：1001项PASS（53.867s）。
- 130+131组合 Cloud所有module与隔离MySQL Work测试PASS；`verify_m2_acceptance.py`静态跨仓矩阵PASS。
- 最终作品11项：返回列表立即带回详情最新数值与状态，避免已更新仍显示缓存队列；PASS。
- 实际浏览器最后一轮：列表刷新→详情读回ready（02:35），详情下滚505.5→再次刷新→自动读回ready，滚动仍505.5。六张卡片7/1/2/0/0/0，原任务30/尝试82/成片153保留。
- Cloud PR60最新8c0b121自动Code Review completed，has_any_findings=false、has_unresolved_findings=false。旧滚动问题已修；已有作品来源的范围及130新投稿入口已在PR描述和本证据说明，没有扩建导入入口。

## 最终安装版与正式Sidecar（非测试驱动）

最终冻结组合完整环境exit0，全部gate PASS；包、源码及SHA见final-environment.json。通过CUA按明确挂载路径选择新包，正常operator01登录并替换本轮测试Desktop会话；环境弹层显示本机服务已连接、比特浏览器已登录指定账号、执行凭证已配置。安装版作品16点击刷新，正式包内Sidecar按生产轮询自动完成，页面成功更新时间02:45，六项仍7/1/2/0/0/0；详情来源/真实UID不变，返回列表状态和更新时间一致。此项不依赖前面的短轮询测试驱动。

名称选择曾打开output目录旧副本；通过进程可执行路径确认并用既有launch-dmg入口重启，最终进程位于desktop-review-mount。没有修改登录逻辑或使用旧包冒充本轮验证。浏览器走查也已完成，临时1440断点已恢复默认。

## 最终交付

Cloud 8c0b121 的完整CI45877466848成功（含原型、迁移重放、release binaries和双Web构建、打包校验）；Agent22、Desktop21和Workspace73检查绿色。Cloud/Agent最新自动Code Review均无新发现。运行仓分别合入main：Cloud ca49da81、Agent e7889f98、Desktop 5753a81e；本地main确认包含功能提交。Workspace的521d2ed是最终验收证据提交，随PR73进入main。

当前新包已正常登录并停留作品列表。只交付B站六项指标，未测试Windows/x86安装包，不改变130的待验事项。
