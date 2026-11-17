# M6-B 本地执行安全验证

日期：2026-11-18。Agent 实施提交 `6046a789fe53530f75673c4706ebdfea6decc1ed`，地址别名修复 `eb49901`、CI 争锁修复 `f663af1`。此单元只是首次自动投稿的前置安全能力，不代表平台投稿或 M6 完成。

| 检查 | 实际结果 |
| --- | --- |
| 定向故障测试 | PASS：16 项执行边界及 3 项连接初始化测试；先出现缺失实现的失败，再实现并通过。地址别名回归先失败，再统一大小写与默认端口；最终定向复验通过 |
| SQLite 并发与隔离 | PASS：8 个线程争抢同一 attempt 只有一个首次登记；同号下载、不同环境/用户不覆盖；输入与结果不可改写；实际 Profile 的未知现场跨用户/环境互斥 |
| 突然退出与恢复 | PASS：3 个实际子进程分别在 submitting、click_started、result_saved 后直接退出；重开 SQLite 可读到此前阶段，重复调度没有再次准备或点击。结果保存后退出仍保留原 outbox |
| 事务回滚与补报 | PASS：SQLite 触发器注入 outbox 写失败，checkpoint 更新一并回滚；断网、错误确认及跨用户/环境发送均不结算；确认只标记原结果投递，不自动释放未知现场；明确安全结算后仍保留防重记录 |
| Agent 标准回归 | PASS：`bash scripts/test.sh`，695 项；既有架构边界、下载、迁移、身份与本地接口验证保留，未降低断言、未向 checkout .local 写测试数据 |
| 装配 | PASS：14 项；安全组件与既有 checkpoint 使用同一数据库，构造本身不启动发布循环 |
| Workspace | PASS：211 项；交付索引、Milestone/MASTER 归属、配置与差异检查通过 |
| 实际环境预检 | 账号 9、Profile 37 的本机百度 UID 实读匹配，登录正常；浏览器实际打开百家号后台并点击「发布视频」，空上传表单可见。未上传或点击发布，不作为本单元端到端投稿证据 |
| 页面与正式平台验收 | 本单元不改变页面。M6-A 两端实际表单证据见前置 CHG；首次真实自动投稿尚未接入，不声称通过 |

复现：Agent `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -p test_publication_execution.py`；`bash scripts/test.sh`。均使用临时 SQLite，不连接 Cloud MySQL、不以测试回调充当真实平台成功。

Agent PR：[wt-media-agent#9](https://github.com/piqiu96/wt-media-agent/pull/9)。依赖 M6-A [Cloud#44](https://github.com/piqiu96/wt-media-cloud/pull/44) 与 [Workspace#52](https://github.com/piqiu96/wt-media-workspace/pull/52)；本 Workspace PR 以 #52 的分支为基线，只显示本单元差异。用户本次已允许堆叠，未修改长期规则；标准 start 因前置未合并拒绝，本次仅按明确授权继续，未绕过或削弱校验脚本。

CI 在 Linux/Python 3.12 首次 WAL 初始化并发测试失败，保留原并发断言；新增实际 SQLite 读锁测试确定性复现，只修复连接初始化的争锁重试与错误关闭；3 项定向测试及 695 项完整回归通过。不是重跑 CI 碰运气，也没有给平台操作增加自动重试。最终 GitHub CI PASS（run 44188903102）；`wt chg verify CHG-20261118-102` PASS，包含 Workspace 211 项与 Agent 695 项及配置/运行环境检查。当前安装包重建、签名与组件版本校验通过，包内 Agent 来自 `f663af1`；不据此宣称原生页面走查或平台投稿通过。实际平台领取、适配和最终提交继续留在后续 M6-B 范围。
