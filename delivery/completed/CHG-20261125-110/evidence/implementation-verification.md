# 实现与受控回归

关联运行时提交：Cloud `787d4e1`（继承b84de4b、1b31e79、db6109e，后续d659a34、549cab4、522d644）。以下都是本次执行事实，fixture不证明真实平台发布。

| 检查 | 预期 | 实际 |
|---|---|---|
| `cd web && npm test` | 全Web自测通过 | PASS，167文件/1242测试；最终日志 `/tmp/chg110-web-final.log` |
| `npm run build:cloud` / `npm run build:desktop` | 两端生产构建通过 | PASS，787d4e1最终构建及DMG门禁通过 |
| publication batch browser | 配置保存、恢复、批量内容、请求恢复与内容版本保护；原型三分区及推荐、账号切换 | PASS，`/tmp/chg110-batch-fixed.log` |
| batch execution browser | 启动、组间操作、恢复与结果 | PASS，`/tmp/chg110-final-batch-execution.log` |
| plan / plan-editor / plan-g1-matrix / plan-controls / plan-stale browser | 计划准备与守恒、10%推进、冻结、控制、过期数据保护 | PASS；plan及plan-editor在编号aria修复后重跑通过，`/tmp/chg110-rerun-plan.log`、`/tmp/chg110-rerun-plan-editor.log` |
| 批次异常11场景 | changed-revision、abandoned-navigation、rejected-replay、different-start-rejected、different-start、cross-tab、failed-task-actions、senior、manual-publication、late-publication、stopping | PASS；stopping修复测试等待请求时序后重跑通过，`/tmp/chg110-rerun-batch-execution.log` |
| `git diff --check` | 无格式错误 | PASS；无关example修改未加入提交 |

## 实测发现与修复

- 新增计划分区编号影响heading可访问名称：编号设aria-hidden；两个计划用例重跑通过。
- 终止筛选断言早于请求发出：先建立精确请求等待再导航，业务断言保留。
- 资源表账号第一次更换成功后无法切回：TDesign表格slot事件保留旧行对象；按row_key查最新候选后进行校验与修改，浏览器来回切换断言通过。
- 之前一次全Web测试发现查询按钮未显式primary，已修正并完整回归。

## 证据边界

本文件记录逻辑与受控浏览器回归；本轮真实AI、两批实际公开与结束见real-operations.md，新安装包见environment.md。未使用旧109结果替代本轮验收。

## 真实走查后的追加修复

Cloud `549cab4`：成片API已返回media.duration_ms，旧模板硬编码“时长：—”；改用共用formatDurationMs，真实未知仍显示—。batch-stack通用label规则误把TDesign确认checkbox排成上下两行，排除checkbox/radio根节点。完整自测再次167文件/1242通过（`/tmp/chg110-operations-web.log`）；批次浏览器新增真实30秒字段断言并通过（`/tmp/chg110-duration-browser.log`）。549cab4安装版走查通过，后续787d4e1最终包同样已验证。

## 运营与审阅发现的最后两处修正

- Cloud522d644：计划内未开始批次的fallback候选表沿用了nowrap，长成片名把封面/确认列挤出；限定列宽并两行省略，横滚区域可聚焦。三角色plan浏览器新增120字成片名的宽度断言，通过。批次浏览器增加替换成片后移出，确认当前manual_pair清除，通过。
- Cloud787d4e1：真实Web连续勾选两类目时，盘点锁表造成checkbox已选但目标表缺项；已用延迟300ms的真实Vue浏览器场景复现失败（/tmp/chg110-fast-category-repro.log）。只读盘点不再冻结编辑，旧响应由已有sequence隔离，修后完整批次浏览器通过（/tmp/chg110-fast-category-fixed.log）；完整Web167/1242通过（/tmp/chg110-post-category-tests.log）。
- 一轮全Web运行在localSettingsWiring模块导入超过5秒；未改测试超时/断言，重跑全量167/1242通过（/tmp/chg110-final-ui-tests-rerun.log），后续787d4e1全量也通过。
- Workspace用户新规则已回写但治理脚本仍要求旧“人工裁定”短语，另有Active CHG归属/状态索引不一致；19dc809同步校验器与总计划/索引，220 Workspace测试通过。wt chg verify在独立Agent阶段串行重跑退出0（/tmp/chg110-governance-serial.log），全部门禁通过。未改保护或提取Token。

## 最终审阅

独立于实现的收口检查：逐项核对本CHG范围、21个Cloud文件diff、正式资源校验/内容版本保护/请求恢复/错误与只读分支；未新增Contract或Backend行为，未引入example运行时依赖，git diff --check通过。最后发现并修正的522d644与787d4e1问题均有新增受控浏览器断言和安装包复验。Cloud PR53最新787d4e1检查1/1通过，无未处理评论、无冲突；合并状态另见最终交付记录。
