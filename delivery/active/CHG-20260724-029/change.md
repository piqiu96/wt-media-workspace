# CHG-20260724-029：M2-B5 浏览器窗口真实操作与台账收口

> 日期：2026-07-24  
> 状态：ACTIVE  
> 所属 Milestone：M2-B 浏览器窗口与媒体账号真实闭环  
> 关联闭环：`delivery/milestones/M2-account-runtime.md#M2-B-浏览器窗口与媒体账号真实闭环`  
> 当前仓库：`wt-media-workspace`  
> 预计影响仓库：`wt-media-cloud`、`wt-media-agent`、`wt-media-desktop`

## 1. 用户可见目标

普通运营在 Desktop 可以对本人授权的浏览器窗口完成真实本机操作：

```text
进入浏览器窗口
→ 查看Cloud已保存窗口镜像和本机状态
→ 扫描本机窗口并查看Diff
→ 无Diff时只提示无需处理
→ 有Diff时接受本地变化或恢复Cloud配置
→ 新建窗口时选择真实BitBrowser分组并调用BitBrowser创建
→ 打开/关闭窗口时同步调用BitBrowser并读回结果
→ 页面显示窗口正式状态、代理摘要、备注、标签和最近同步结果
```

本 CHG 只收口浏览器窗口本身，不处理媒体账号新增/标签/游戏绑定返修，不处理代理写入闭环，不处理Cookie上号。

## 2. 当前背景

已完成/继承：

- M2-A 已完成用户、权限、会话和本机可信基础；
- M2-B1/B2 已具备 Desktop 扫描、Diff、接受本地变化、恢复Cloud配置基础；
- `CHG-20260724-028` 已修复本机可信刷新、重绑、账号检查基础链路，并由用户人工验收通过；
- 用户确认：Cloud Web 对所有角色只展示Cloud保存数据；Desktop才展示和操作Local Agent / BitBrowser；
- 用户确认：打开、关闭、新建、扫描等BitBrowser单项操作是同步操作，不创建Cloud异步任务。

## 3. 本 CHG 范围

### 包含

- 浏览器窗口页面命名和字段收口：
  - 菜单/页面使用“浏览器窗口”；
  - 列表展示系统自增ID、BitBrowser Profile ID、比特序号、名称、分组、代理摘要、比特备注、比特标签、Cloud备注、授权运营、Cloud镜像状态、本机运行状态和最近同步时间；
  - 搜索至少覆盖系统记录ID、BitBrowser Profile ID、名称、分组、备注和标签；
  - 列表具备分页和必要状态筛选。
- 打开/关闭窗口同步操作：
  - Desktop Vue 通过 Tauri/Rust 调 Local Agent；
  - Local Agent 同步调用 BitBrowser打开/关闭接口；
  - 成功后读回或刷新窗口运行状态；
  - 失败显示运营可理解原因；
  - Cloud Web 不展示打开/关闭入口。
- 新建窗口真实创建：
  - Desktop 读取BitBrowser分组列表；
  - 用户选择真实分组ID并填写BitBrowser必要字段；
  - Agent调用BitBrowser创建Profile；
  - 创建成功后读回Profile并更新Cloud镜像；
  - 不允许只创建Cloud记录冒充新建窗口成功。
- 窗口停用语义：
  - 不真实删除BitBrowser本地Profile；
  - “删除”如需要出现，只表现为Cloud镜像停用/归档；
  - 停用不删除账号历史、本机窗口或BitBrowser数据。
- Diff交互收口：
  - 无Diff时不出现接受/恢复/取消变更，只提示无需处理；
  - 有Diff时“接受本地变化”只更新Cloud允许字段；
  - “恢复Cloud配置”必须写回BitBrowser并读回验证；
  - “取消变更”只放弃本次扫描Diff，不修改Cloud和BitBrowser。

### 不包含

- 不修改媒体账号新增、标签、游戏绑定、登录状态和业务状态规则；
- 不执行媒体账号检查、批量检查或手动登录同步；
- 不写入、更换或解绑代理；
- 不导入、写入、读取或导出Cookie；
- 不做CK上号、接码链接、人工验证码或人工接管；
- 不建设通用任务中心；
- 不实现跨重启持久化保存Desktop执行凭证；该问题后续单独CHG处理。

## 4. 关键规则

- Cloud Web 不能调用 Local Agent 或 BitBrowser；
- Desktop Vue 不能直接访问 Local Agent 动态端口或持有动态凭据；
- 打开、关闭、新建、扫描、恢复都必须通过 Tauri/Rust → Local Agent → BitBrowser；
- HTTP成功、命令已发送、Cloud记录已创建都不等于窗口操作成功；
- 只有BitBrowser真实执行并读回一致，才算成功；
- BitBrowser主账号不一致时必须阻断，不允许静默改绑；
- Cloud授权用户、媒体账号绑定、游戏、标签、Cookie和业务状态不能被扫描覆盖；
- 归档/停用窗口不能作为新的媒体账号绑定目标。

## 5. 执行任务

### Task 1：Start Gate 与现状审计

- 核对 `CURRENT_CONTEXT`、`LEDGER`、active CHG 和 M2-B milestone；
- 审计当前浏览器窗口Cloud模型、Web页面、Desktop页面、Agent BitBrowser适配器和Tauri命令；
- 明确已有实现、缺口、可复用代码和风险；
- 记录文件映射和测试计划。

### Task 2：Cloud窗口模型与列表查询收口

- 补齐浏览器窗口字段投影、状态枚举、搜索、筛选和分页；
- 保证系统记录ID使用数据库自增主键，BitBrowser Profile ID作为外部ID；
- Cloud Web只展示Cloud保存镜像和只读摘要。

### Task 3：Desktop打开/关闭窗口同步链路

- 新增或修正Desktop打开/关闭入口；
- Tauri/Rust调用Local Agent；
- Local Agent调用BitBrowser接口并返回结构化结果；
- 页面展示成功、失败和运行状态读回结果。

### Task 4：Desktop新建窗口真实创建链路

- 读取BitBrowser分组；
- 按BitBrowser字段建模新建表单；
- 调用BitBrowser创建Profile；
- 读回新Profile并更新Cloud镜像；
- 失败不得创建正式Cloud假窗口。

### Task 5：停用/归档和Diff交互收口

- 不做真实删除；
- 需要删除语义时统一为Cloud停用/归档；
- 无Diff不显示保存类操作；
- 有Diff的接受、恢复、取消语义与Milestone一致。

### Task 6：验证与Evidence

- 自动测试覆盖Cloud查询、字段、状态、页面边界；
- 单项BitBrowser操作用Local Agent mock或真实环境可控验证；
- 记录无法真实验证的外部前置；
- 更新checkpoint。

## 6. 验收标准

- Cloud Web浏览器窗口页没有扫描、打开、关闭、新建、恢复等本机操作入口；
- Desktop浏览器窗口页展示完整窗口字段、搜索、筛选和分页；
- 无Diff扫描结果只提示无需处理，不出现保存类按钮；
- 打开/关闭窗口同步调用BitBrowser，成功/失败结果可见；
- 新建窗口必须真实调用BitBrowser创建并读回后才写入Cloud镜像；
- 停用/归档不删除BitBrowser本地窗口、不删除账号历史；
- BitBrowser主账号不一致时阻断；
- 失败不得产生Cloud假成功记录。

## 7. Evidence 要求

完成后在 `evidence/` 中至少提供：

- `start-gate.md`：当前事实、缺口、文件映射；
- `cloud-window-query.md`：Cloud列表/字段/状态/搜索分页验证；
- `desktop-open-close.md`：Desktop打开/关闭同步调用验证；
- `desktop-create-profile.md`：新建窗口真实创建和读回验证；
- `diff-and-archive.md`：无Diff、接受、恢复、取消、停用语义验证；
- `tests.md`：自动测试和构建记录。

## 8. 交付边界

本 CHG 完成后，M2-B 的“浏览器窗口”部分应具备真实可用闭环。

后续独立 CHG 继续处理：

- M2-B6：媒体账号新增、标签、游戏绑定、状态、打开/关闭入口和手动登录后同步账号信息收口；
- M2-C：代理资源与窗口真实绑定闭环。

## 9. Checkpoint

- Completed：已创建CHG，等待Start Gate。
- Current：准备执行Task 1。
- Next：审计Cloud/Web/Desktop/Agent现状，确定实现文件映射。
- Blockers：无。
- Recent verification：继承`CHG-20260724-028`，用户已人工验收本机可信刷新/重绑路径。

## 10. Pending Questions

None.
