# 素材库 / 我的素材补充验收（2026-11-05）

本次验证实际 Cloud Vue 产品和共用 Desktop 前端。Cloud 提交：`94ed0e5`（数据与契约）、`350be8d`（界面与批量加入）。沿用 CHG120 和原有权限；未修改 example/ 的已有变更。

## 数据与接口

在原 `source_contents` 新增可空 `metrics_updated_at`，没有新表、新接口或定时刷新任务。本机 `wt_media_cloud` 已执行迁移 `20261105_095`，再次运行无待执行迁移。

成功采集结果携带采集时间，搜索/采集任务确认入库时沿用；重复入库仍返回 duplicate，但仅用较新的快照更新原记录的指标、原始响应和指标时间。保留来源归属、类目、审核状态、素材及使用关系。数值未变也推进采集时间，未知或较旧时间不覆盖较新值。历史时间未知保持空，不用素材修改时间补造。

Material 兼容返回平台作品 ID 与采集时间，列表接受来源平台筛选 `douyin`；API 和业务 schema 版本 `2026.11.05.5`，保留 `/api/v1`。

## 功能验收

| 操作 / 检查 | 实际结果 |
| --- | --- |
| 素材库基础筛选与表格 | 顺序为综合搜索、类目、平台、发布时间、我的使用、团队使用、加入状态；管理员额外团队筛选。平台独立列，作品 ID 收在详情；勾选列实测 44px；使用公共筛选、日期范围和批量栏。 |
| 来源平台查询 | 选择抖音后查询实际发送 `platform=douyin`；其他平台参数在后端解析测试中拒绝。 |
| 跨页选择 | 第 1 页选 1 条，第 2 页再选 1 条，工具条计数 2；新查询清空，避免操作上一查询结果。 |
| 批量加入与恢复 | 真实素材接口加入 1 条、跳过已加入 1 条；仅对另一条请求注入 403 验证部分失败，失败 1 条保留选择。撤除注入后重试，真实加入成功；三条关系回读均 active。 |
| 重复采集读回 | 控制样本首次捕获 `13:12:31Z`，再次 `13:14:01Z`；实际导入后指标由 12 变 19，较旧的 99 不覆盖 19；接口与详情显示最新采集时间。这里只验证本地 API→MySQL→Vue，没有调用线上付费抖音采集。 |
| 详情 | 原作品转发仅详情展示；平台作品 ID 复制成功；平台作品链接可点击；入库时间和操作人同一两列行；明确团队使用；隐藏准备完成时间。 |
| 我的素材 | 基础筛选为“视频状态”，无单字段高级筛选；行操作“放弃”，没有“放弃使用”。 |
| admin / operator01 / senior01 | 三个现有账号实测，无密码重置；普通运营仅看团队成片数和人数，使用人姓名仍按原权限限制；高权限角色可见已有人员明细。 |
| 宽窄布局与错误 | 两页实际页面、详情及团队弹窗检查；素材库三角色 1440 / 1024 无页面横向溢出，宽表在表内横滚；无 JS pageerror。 |
| 样本清理 | 3 条专用验收来源、素材及个人关系（1035–1037 / 182–184）按 ID、标题前缀和来源关联校验后删除。未删除其他业务数据。 |

## 自动检查

| 命令 / 范围 | 结果 |
| --- | --- |
| `go test ./internal/modules/contentpool/... ./internal/modules/production/... -count=1` | PASS；新增覆盖搜索捕获时间、延迟导入不重打时间戳、重复快照及字段投影。 |
| `WT_MEDIA_TEST_LIVE_DB=1 go test ./internal/modules/contentpool/repository -run TestLiveSourceMetricCaptureFreshness -count=1`（指定本机 Cloud runtime） | PASS；真实 MySQL 事务回滚：首次、新值、同值新时间、旧值、空时间、读取不改变时间，原审核与归属不变。 |
| Cloud/web `npm test` | PASS：127 个文件、970 项测试。 |
| `python3 scripts/verify/verify_m0_config.py` | PASS；提供方契约版本与 Workspace 映射一致。 |
| `python3 scripts/docs/check.py` | PASS；15 个索引。 |
| `git diff --check` | PASS。 |

## 截图

- [素材库 1440](120-materials-library-1440.png) / [1024](120-materials-library-1024.png)
- [详情与采集时间](120-materials-detail.png)
- [跨页选择](120-materials-cross-page.png)；批量部分失败与重试的实测结果见上表。
- [普通运营团队使用](120-materials-team-operator.png) / [管理员团队使用](120-materials-team-admin.png)
- [我的素材筛选](120-my-materials-filters.png)

截图中的专用验收样本已清理；部分失败截图为明确的单请求 403 注入，其他加入与数据读写均使用本机真实服务。旧素材采集时间仍显示“—”，等待后续成功采集；本轮不触发全库重采集。机器走查不代替用户人工视觉签收。


## 构建与环境

Cloud `350be8d` 的干净源码重建了 Cloud / Desktop 前端和 macOS DMG，打包清单 `source_commit=350be8d`、`source_dirty=false`。`bin/control.sh start` 完成迁移、重启、双前端构建、DMG 挂载与启动；重启后两页及清理结果再次实际读回，无 pageerror。

启动桌面后 Agent 端口交接仍出现已有的未监听问题，不能将此轮构建成功当作原生窗口功能验收。已用标准 `local_env.py up` 恢复独立 Agent，再运行 `local_env.py verify` 全部通过：Cloud、Agent、Worker、合成 Worker/调度、BitBrowser、双前端、打包资源、DMG 新鲜度及登录烟测。没有改动 Agent/Desktop Runtime 或用户绑定。原生窗口逐控件签收仍未完成；本轮 UI 验证来自实际浏览器运行的共用 Vue 源码。
