# CHG-117 前端与真实成片验证

时间：2026-11-05。Chrome headless 复用授权管理员会话，访问最新本地 Web（5173）与真实 Cloud / Worker；没有替换登录、没有修改策略、没有创建演示数据。关联本 CHG 待提交的 Cloud UI／API client 差异。此记录不替代人工签收或 Desktop 本机下载验收。

## 自动验证

- `npm test`：PASS，116 个测试文件、946 项测试；最终运行 04:36:23，9.61 秒。
- `npm run build:cloud`：PASS，10.57 秒。
- `npm run build:desktop`：PASS，10.51 秒。两种构建仅出现既有的大分块提示。
- `git diff --check`：PASS。
- 新增行为覆盖：原模板版本和原最终参数、仅原组一份、仅 editable 覆盖、固定引导地址不提交；确认加入成功后才创建、加入失败零任务；同一提交在响应丢失后复用已确认状态及 request_key；默认名称 60 个 Unicode 字符并保留再次制作后缀；对象与设备状态分离及缺失事实不补造。

## 真实创建与资产回读

从旧成片 82 点击再次制作。打开及调整参数时写请求为 0；确认后先 `POST /materials/161/usages`（strategy 140、owner 3），成功后 `POST /compose-tasks`，仅提交 `source_output_id=82`、任务名、request_key、remake_confirmed 与 `default.end_seconds=4` 的 editable 覆盖。没有提交 material_ids、固定参数、平台或份数。

实际返回批次 **41**、任务 **671**，创建 1 项、失败 0 项。Worker 成功生成成片 **104**：

| 回读事实 | 实际结果 |
| --- | --- |
| 原素材／负责人／原组 | 素材 161／pika／default 默认成片，copy_index=1 |
| 最终参数 | 开始 1 秒、结束 4 秒；basic_cut v1 |
| 新名称 | 素材标题 · 默认成片（持久化 name） |
| 新文件名 | 同名加 `-104.mp4`（持久化 file_name） |
| 媒体数据 | 3000ms、640×360、53707 字节 |
| 对象实际读取 | HTTP 200、video/mp4、读到 53707 字节，与存储 SHA-256 一致 |
| 旧产出 | 成片 82 保留 |
| 聚合／分页 | 素材聚合 2 组；全部成片共 4 个；素材 161 精确明细为 [104,82]、total=2 |

再打开 104 的再次制作表单，参数为 **1／4**；当前策略 140 仍为 **1／5**，表单未使用当前策略默认值。原素材固定、原组仅一份、不可换策略／平台／组结构；调参后取消写请求为 0。精确脱敏事实见 [readback.json](ui/readback.json)，未保存认证信息或视频访问地址。

## 最终浏览器检查

| 检查 | 实际结果 | 截图 |
| --- | --- | --- |
| 默认素材聚合，行仅详情 | 正确，按真实素材 ID 汇总跨任务批次产出 | [01](ui/01-output-materials-1440.png) |
| 公共高级筛选及日期 | 1440／1280 可读；页面宽度=scrollWidth=1280，无页面横向溢出 | [02](ui/02-output-filters-1440.png)、[03](ui/03-output-filters-1280.png) |
| 素材明细分页、多选、返回 | exact material_id；选择 1 项后打开／关闭成片详情，选择仍保留；抽屉宽度=scrollWidth=1120 | [04](ui/04-material-outputs-selected-1440.png)、[05](ui/05-material-outputs-1280.png) |
| 成片详情四区 | 无播放器／封面占位；蓝色真实文件链接，元数据合为一行；发布能力如实不可用，不造未安排／已安排 | [06](ui/06-output104-detail-1280.png)、[07](ui/07-output104-detail-1440.png)、[08](ui/08-output104-source-publishing-1440.png) |
| 原配置再次制作 | 固定来源；参数为原 1／4；长标题不撑开布局；抽屉 width=scrollWidth=880，1280 时底部操作可见 | [09](ui/09-source104-seed-1440.png)、[10](ui/10-source104-original-params-1440.png)、[11](ui/11-source104-seed-1280.png) |
| 成片列表与公共选择栏 | 无文件技术列；视频状态直接可见；物理选择列实测 44px；行最多详情／下载／再次制作 3 项；去发布只在选择栏且禁用说明真实 | [12](ui/12-output-list-selected-1280.png)、[13](ui/13-output-list-selected-1440.png) |

最终浏览器 pageerror=0；上述查看／选中／打开及取消源表单的复查脚本写请求为 0。

## 下载受理边界

迁移修复后 `GET /file-transfer-tasks` HTTP 200。点击成片 104 的下载：HTTP **202**，真实任务 `transfer_0ac9d9ec92c7e924d52267eb`，pending、total_bytes=53707、completed_bytes=0。页面显示下载中并收回重复下载按钮，见 [14](ui/14-output104-download-1440.png)。这仅证明受理，**未验证原生接管或本机完成**。

按主执行者要求取消本次管理员测试任务时，同会话取消请求返回 HTTP 404／errcode 15101，列表仍返回 pending；未声称取消成功。主执行者已定位为既有管理员 TeamID 为空导致的取消作用域问题，明确跟踪到 CHG-118 修复管理员本机下载资格与本人任务取消；按指示保留此 pending 记录待修复后通过 API 清理，未直接删库。记录见 [download-readback.json](ui/download-readback.json)。Desktop / 普通运营的实际本机下载闭环留给后续验收，不能以本次 Web 202 代替。

本轮未提交 Git，未修改原型目录、后端或 contracts。
