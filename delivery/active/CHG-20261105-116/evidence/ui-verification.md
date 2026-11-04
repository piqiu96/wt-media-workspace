# CHG-116 前端最终验证

验证时间：2026-11-05，现有授权管理员会话，Chrome headless；访问 `http://127.0.0.1:5173/compose`。未替换登录会话，最终复查未发送业务写请求。关联 Cloud 基线 `73e8d067ffe8fea8f7784b58c6e860ec818281be` 之上的 CHG-116 待提交工作区差异；此记录不是人工签收或 Desktop 实机验收。

## 自动检查

在 Cloud `web` 执行 `npm test -- --run src/modules/compose src/shared/api src/modules/materials`：**PASS，37 个文件、313 项测试**。覆盖合成、共享 API 和素材相关测试。`git diff --check`：PASS。本次按分工未重复构建，构建由主执行者汇总。

## 最终页面复查

| 操作／预期 | 实际结果 | 结果／截图 |
| --- | --- | --- |
| 默认任务批次，真实名称与负责人，行仅详情 | 批次 30 显示“CHG116-QA 独立选材检查”、CHG-098 人工验收、pika；全批已结束 1/1，成功 1 | PASS，[批次列表](ui/01-task-batches-1440.png) |
| 常用／高级筛选分层，日期可读 | 策略、触发方式和创建时间在高级区域；1440 与 1280 宽度可读 | PASS，[1440](ui/02-task-filters-1440.png)、[1280](ui/03-task-filters-1280.png) |
| 批次详情统计真实、状态筛选宽度合理 | 全批成功 1，进度 100%，任务状态控件约 220px，任务仅详情 | PASS，[批次详情](ui/04-batch30-detail-1440.png) |
| 任务 616 信息与执行记录来自真实任务 | 负责人 pika、批次 30、配置 1–5 秒；attempt 275 成功并展示四个真实步骤 | PASS，[任务信息](ui/05-task616-info-1440.png)、[执行记录](ui/06-task616-attempts-1440.png) |
| 新建任务名称首项，成片设置结构固定，参数按模板开放 | 默认成片继承 B站／百度、一份；实际 basic_cut v1 仅有开始／结束秒数两项可调整，值为 1／5 | PASS，[新建](ui/07-task-create-1440.png)、[参数弹窗](ui/08-task-params-1440.png) |
| 选材使用负责人工作集／素材库，公共日期／高级筛选／窄复选列 | 显示负责人 pika、默认运营组、三角洲；双来源可读；选择列实测 44px；1280 弹窗正文 clientWidth=scrollWidth=1238，scrollLeft=0，底部操作可见 | PASS，[我的素材](ui/09-selector-mine-1440.png)、[素材库1440](ui/10-selector-library-1440.png)、[素材库1280](ui/11-selector-library-1280.png) |

最终浏览器 `pageerror` 为 0，业务写请求为 0。界面显示的浏览量 0 对应接口 `metric_presence.view_count=true`，不是把缺失数据补为 0。

## 已执行的真实创建闭环及本轮回读

此前同一 CHG 实测跨页选中两项并切换来源，选择保持；取消选择器时素材写请求为 0。随后明确“使用所选”仅调用一次 `/materials/161/usages`，提交 QA 名称创建了批次 30、任务 616，返回创建 1 项、失败 0 项；不是空批次。本轮只读回查确认：

- 任务 616：`status=success`，`batch_id=30`，`composite_output_id=82`。
- attempt 275：第 1 次执行成功；prepare_input 461ms（473820 字节）、cut 229ms（4000ms 视频）、upload 182ms（69142 字节，含真实 SHA-256）、commit 48ms（output_id=82）。
- 成片 82：`compose_task_id=616`，`file_size_bytes=69142`，`media.duration_ms=4000`；视频地址接口 HTTP 200、errcode 0 且返回可用地址。证据不保存签名 URL 或认证信息。
- 精确回读字段保存在 [readback.json](ui/readback.json)。

本轮没有新增 117 代码、没有更改原型目录，也没有提交 Git。三角色、异常恢复和 Desktop 本机文件验证由其余 CHG-116 证据及主执行者统一核验，本记录不扩大声明。
