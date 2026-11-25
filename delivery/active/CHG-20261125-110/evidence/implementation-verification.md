# 实现与受控回归

关联运行时提交：Cloud `d659a34`（继承b84de4b、1b31e79、db6109e）。以下都是本次执行事实，fixture不证明真实平台发布。

| 检查 | 预期 | 实际 |
|---|---|---|
| `cd web && npm test` | 全Web自测通过 | PASS，167文件/1242测试；最终日志 `/tmp/chg110-web-final.log` |
| `npm run build:cloud` / `npm run build:desktop` | 两端生产构建通过 | PASS，前一轮构建均通过；d659a34最终包构建正在统一环境入口执行 |
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

## 尚不能据此认定的内容

新安装包门禁、真实AI与发布、两批顺序推进和最终产品运营视觉走查继续执行；没有用旧109结果替代本轮验证。
