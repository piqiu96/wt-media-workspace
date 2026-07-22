# M2 账号运行环境详细实施计划

> 日期：2026-07-23
> 依据：
> - `delivery/milestones/M2-account-runtime.md`
> - `delivery/MASTER_IMPLEMENTATION_PLAN.md`
> - `delivery/LEDGER.md`
> - 当前代码与 `CHG-20260722-021` Evidence

## 1. 执行原则

M2 不再按“账号中心模块”整体推进，而按业务闭环逐段交付：

```text
M2-A 用户、权限、会话与运行环境可信
→ M2-B 浏览器窗口与媒体账号真实闭环
→ M2-C 代理资源与窗口真实绑定
→ M2-D 账号上号与Cookie闭环
→ M2-E Desktop本地执行投影与安全收口
```

每次只激活一个 CHG。一个 CHG 只能交付一个闭环卡，或闭环卡中的一个可独立验证纵向切片。

## 2. 横切规则

### 2.1 同步与批量边界

单项短 BitBrowser 操作不创建异步 task：

```text
页面发起
→ Cloud权限与环境预检
→ Desktop/Tauri调用Local Agent
→ Agent同步调用BitBrowser
→ Agent读回真实结果
→ Cloud保存正式结果
→ 原业务页面展示结果
```

批量或等待人工流程使用专用业务 `batch/item`：

```text
业务页面创建batch/item
→ Agent逐项同步操作BitBrowser
→ Cloud持续回写item和batch
→ 原业务详情页展示进度、人工处理、失败与重试
```

发布、互动、合成等后续长流程才使用正式异步 `task`，不纳入 M2。

### 2.2 假成功禁止

以下都不能判定业务成功：

- HTTP 200；
- 命令已发送；
- 任务已创建；
- Agent已调用接口；
- 只写Cloud数据库但没有外部读回；
- 只通过Mock或单元测试。

涉及 BitBrowser、代理、Cookie、登录身份的操作，必须读回真实状态。

### 2.3 Desktop边界

完整业务过程属于原业务页面。本机执行只做当前电脑的提醒与跳转：

- 正在执行；
- 等待人工；
- 结果待确认；
- 最近失败。

本机执行不创建任务、不编辑业务配置、不建设第二套业务详情页。

## 3. 当前状态

### 3.1 Active CHG

当前 Active：

```text
CHG-20260722-021：M2-A1 用户领域模型迁移
```

状态：`VERIFIED`。

已完成：

- 自增UID；
- 管理员 / 高级运营 / 普通运营；
- 运营分组；
- 用户、分组、游戏交集权限；
- 用户管理API与Web；
- 真实MySQL迁移；
- 运行中Cloud API矩阵；
- 真实Web页面走查。

剩余动作：

- 将 CHG-20260722-021 从 `delivery/active` 关闭并归档；
- 更新 `delivery/LEDGER.md`；
- 更新 `.ai/CURRENT_CONTEXT.md` 指向下一个 CHG。

## 4. CHG执行顺序

## CHG-M2-A2：确认式会话与Desktop环境可信

关联闭环：

```text
delivery/milestones/M2-account-runtime.md#M2-A
```

用户结果：

用户登录后，系统能确认当前会话、Desktop、Local Agent 和 BitBrowser 主账号树可信；不可信时阻断后续本地敏感操作。

范围：

- 登录时发现旧会话，需要用户确认是否替换；
- 替换后旧Web、Desktop、Agent不能继续发起新敏感操作；
- Desktop展示Cloud、Local Agent、BitBrowser、`main_user_id`和身份匹配状态；
- 通过真实Profile扫描验证`main_user_id`一致和`profile_user_id`完整；
- 用户确认绑定`main_user_id`；
- 绑定只验证身份，不应用Profile同步结果。

不包含：

- Profile正式同步；
- Profile授权分配；
- 代理、Cookie、上号；
- FFmpeg、本地业务目录、发布或互动。

验收：

- 用户取消会话替换时旧会话不受影响；
- 用户确认替换后旧会话不能继续发起敏感操作；
- Desktop能显示Agent、BitBrowser和主账号匹配结果；
- `main_user_id`不匹配、多个主账号或身份字段缺失时阻断本地敏感入口；
- Evidence包含真实Desktop/Agent/BitBrowser读回结果。

## CHG-M2-B1：Profile扫描、Diff与主账号绑定

关联闭环：

```text
delivery/milestones/M2-account-runtime.md#M2-B
```

用户结果：

普通运营可以扫描自己BitBrowser窗口，看到差异，选择接受本地变化或恢复Cloud配置。

范围：

- Desktop发起真实Profile扫描；
- Cloud生成新增、变更、缺失、代理变化、运行状态和已绑账号影响Diff；
- 接受本地变化更新Cloud镜像；
- 恢复Cloud配置写回BitBrowser并读回；
- 扫描不覆盖账号、标签、备注、Cookie、业务状态和Cloud授权。

验收：

- Diff未确认时Cloud正式镜像不变；
- 接受变化后Cloud镜像与BitBrowser一致；
- 恢复配置后BitBrowser读回一致；
- 外部删除只标记Cloud镜像失效/归档，不远程删除本地Profile。

## CHG-M2-B2：浏览器窗口生命周期与授权

用户结果：

用户可以单个或批量创建、编辑、打开、关闭、检查窗口，并由管理员分配未授权窗口。

范围：

- 单窗口创建、编辑、打开、关闭、检查同步调用Agent并读回；
- 批量创建使用业务批次逐项执行；
- 一个Profile只授权一个系统用户；
- 高级运营只能看同组授权Cloud状态，不能操作他人本地窗口；
- 管理员可以分配未授权Profile。

验收：

- 单个窗口真实创建并读回；
- 批量创建展示逐项成功/失败和失败项重试；
- 授权后普通运营只能操作自己授权窗口；
- 结果待确认时先扫描真实Profile，不能重复创建。

## CHG-M2-B3：媒体账号台账、绑定与真实检查

用户结果：

账号可以作为台账存在，也可以绑定Profile后通过真实检查获得平台身份和登录状态。

范围：

- 媒体账号创建、编辑、标签、备注、业务状态；
- 账号绑定、解绑、换绑Profile；
- 一个账号最多绑定一个Profile；
- 一个Profile可绑定多个不同平台账号，同平台最多一个；
- 单个和批量账号检查；
- 检查回填平台UID、名称、头像、登录状态和最近检查时间。

验收：

- 未绑定Profile的账号明确不可执行本地任务；
- 手工补录不能授予执行资格；
- 换绑后登录状态变为`unknown`并必须重新检查；
- 实际账号与Cloud记录不一致时由用户选择更新或重新登录。

## CHG-M2-C1：代理台账与无副作用导入

关联闭环：

```text
delivery/milestones/M2-account-runtime.md#M2-C
```

用户结果：

用户可以通过Excel、CSV、TXT和多行粘贴导入代理，先预览和修正，确认后才入库。

范围：

- 代理字段：协议、Host、Port、用户名、密码、地区、出口IP、供应商、到期时间、状态、检测结果、刷新URL、标签、备注；
- 导入解析、逐行预览、错误提示、重复提示；
- 确认前零副作用。

验收：

- 预览不写数据库；
- 确认后才创建代理；
- 密码不在普通列表、日志和Evidence中展示；
- 误建且无历史代理可删除，有历史代理只能停用。

## CHG-M2-C2：代理真实检测与统一窗口配额

用户结果：

代理可以真实检测，并按统一`max_profile_count`计算可分配窗口数量。

范围：

- 单代理检测同步调用Agent；
- 批量检测使用业务批次逐项执行；
- 代理状态、检测结果、出口IP和到期规则；
- 统一窗口配额，不再按平台配额。

验收：

- 只推荐已启用、检测正常、未到期、有剩余配额的代理；
- 停用代理不自动清空现有Profile，但页面提示仍在使用；
- 刷新URL调用后重新检测出口，不自动修改Profile绑定。

## CHG-M2-C3：代理写入Profile并读回

用户结果：

用户确认代理分配后，代理真实写入BitBrowser Profile，读回一致后Cloud才更新正式关系和配额。

范围：

- 推荐方案和人工调整；
- 单项写入、更换、解绑同步调用Agent；
- 批量分配使用业务批次逐项执行；
- 写入、新旧代理配额切换和读回验证；
- BitBrowser外部代理变化进入Profile Diff。

验收：

- 写入失败不更新Cloud正式绑定；
- 更换时新代理读回成功后才释放旧配额；
- 解绑时读回无代理后才清除Cloud关系；
- 外部未知代理生成待补充记录，补齐并检测前不参与推荐。

## CHG-M2-D1：凭据、Cookie与账号事实模型

关联闭环：

```text
delivery/milestones/M2-account-runtime.md#M2-D
```

用户结果：

媒体账号能够保存上号所需凭据，并区分原始Cookie和真实Cookie。

范围：

- `media_account`保存`login_username`、`login_phone`、`login_password`、`sms_receive_url`、`sms_receive_expires_at`、`original_cookie`、`active_cookie`；
- 管理员和账号所有者可查看、复制登录密码和完整Cookie；
- 高级运营只看已配置状态；
- 原始Cookie长期保留，真实Cookie只能从窗口读取。

验收：

- 普通列表、日志、错误和Evidence不泄露密码、Cookie、验证码；
- 不因为存在Cookie判定登录正常；
- 密码和Cookie查看权限正确。

## CHG-M2-D2：批量CK上号

用户结果：

用户可以批量导入CK，系统逐项完成窗口、代理、Cookie写入、登录检查和账号回填。

范围：

- CK批次独立入口；
- 预览账号、窗口和代理，确认前零副作用；
- 确认后创建`media_account`和`account_login_batch/item`；
- Agent逐项检查窗口当前登录账号；
- 写入Cookie、打开平台、检查登录、读取真实Cookie；
- 上号任务详情展示批次统计、单项步骤、失败和重试。

验收：

- 创建`media_account`不能称为上号成功；
- 部分成功、等待人工、冲突、取消、结果待确认和失败项精确重试成立；
- 成功后账号业务状态`enabled`、登录状态`normal`，且Profile和代理预检通过。

## CHG-M2-D3：接码链接上号

用户结果：

用户可以通过接码链接完成账号登录，并在失败、过期或需要更新链接时继续处理。

范围：

- 接码链接独立批次；
- 发送、轮询、到期、更新链接、重试；
- 登录成功后读取平台身份和真实Cookie；
- 接码过程写入batch/item，长期账号事实只写`media_account`。

验收：

- 链接过期阻止继续使用；
- 更新链接后可重试；
- 失败不回滚已成功项；
- 结果待确认不自动重新发码。

## CHG-M2-D4：人工验证码与人工接管

用户结果：

自动化失败后，用户可以人工完成登录，然后点击同步账号信息，系统读回真实身份和Cookie。

范围：

- 人工验证码独立批次；
- 等待输入、重发、错误、过期、取消、继续；
- 自动失败后保留并打开对应BitBrowser窗口；
- 用户人工登录后点击“同步账号信息”；
- Agent同步读取平台UID、名称、头像、登录状态和Cookie。

验收：

- 自动或人工登录成功具有相同使用资格；
- 记录完成方式；
- 实际账号不一致时不自动覆盖，由用户选择更新当前记录或重新登录；
- 当前用户下相同平台UID复用已有账号，避免重复正式记录。

## CHG-M2-D5：Cookie导出、换绑并清理

用户结果：

用户可以分别查看/导出原始Cookie和当前真实Cookie，并在换绑时安全清理原窗口目标平台Cookie。

范围：

- 单个和批量读取当前Cookie；
- 原始Cookie与真实Cookie分别导出；
- 换绑并清理只清除原窗口目标平台Cookie；
- 读回成功后才更新绑定。

验收：

- 导出逐项反馈；
- 清理不影响其他平台；
- 读回失败不更新正式绑定；
- Cookie敏感值不进入普通Evidence。

## CHG-M2-E1：Desktop Sidecar、环境状态与同步安全桥

关联闭环：

```text
delivery/milestones/M2-account-runtime.md#M2-E
```

用户结果：

用户打开Desktop后，可以看到当前电脑是否具备本地执行条件，以及为什么不可执行。

范围：

- Tauri管理Local Agent Sidecar生命周期；
- Vue不持有动态Agent凭据，不直接访问Agent端口；
- 环境状态展示Cloud、Local Agent、BitBrowser、`main_user_id`和当前节点可执行状态；
- 提供重新检测、启动/重启Agent、打开BitBrowser、恢复提示；
- Web只能做Cloud操作，Desktop承载本地短操作。

验收：

- 真实打包环境下Sidecar启动、健康、停止、重启和清理通过；
- 环境状态能说明可执行性和恢复方式；
- 单项短操作同步执行、读回并更新原业务对象。

## CHG-M2-E2：本机执行抽屉与业务跳转

用户结果：

普通运营能通过顶部“本机执行”看到当前电脑正在执行、等待人工、结果待确认和最近失败，并跳回原业务页面处理。

范围：

- 本机执行只在普通运营Desktop可见；
- 展示当前电脑摘要，不上传为另一套Cloud历史；
- 点击跳转到浏览器窗口、代理、媒体账号、上号任务详情或Cookie弹窗；
- 不编辑业务配置，不建设第二套任务中心。

验收：

- 批量创建、批量检查、批量Cookie和上号过程均有原业务详情页；
- 本机执行只投影摘要并准确跳转；
- 验证码、账号冲突、代理调整、Cookie修改和失败项重试均回原业务页面处理。

## CHG-M2-E3：互斥、安全退出与综合真实验收

用户结果：

所有M2本地敏感操作有一致互斥、恢复和安全退出规则，M2可以在真实环境完整演示。

范围：

- 同一Profile同时只能执行一个M2敏感操作；
- 同一媒体账号同时只能执行一个账号敏感操作；
- Agent最小未完成操作标记；
- 中断后先读回真实状态；
- Desktop关闭时按是否存在敏感操作提示安全停止；
- M2-A～D真实综合验收矩阵。

验收：

- 中断恢复不重复外部副作用；
- 无法判断时进入结果待确认；
- 本地未完成标记正常完成后清理；
- M2-A～D可以在真实Desktop、Local Agent、BitBrowser、代理、Cookie环境完整演示。

## 5. 下一步执行

当前最小下一步：

```text
关闭 CHG-20260722-021
→ 激活 CHG-M2-A2
→ 执行确认式会话与Desktop环境可信闭环
```

关闭 CHG-20260722-021 前必须完成：

- `change.md` 状态从 `VERIFIED` 归档为完成记录；
- `delivery/LEDGER.md` 移除该 Active 记录；
- `.ai/CURRENT_CONTEXT.md` 指向新 Active CHG；
- 不触碰 `wt-media-cloud/internal/modules/proxy/service.go` 和现有 `web/dist-*` 未提交变更。

## 6. M2最终完成条件

M2只有在以下同时满足后才能标记`DONE`：

- M2-A～E所有CHG关闭；
- 真实MySQL、Desktop、Local Agent、BitBrowser、代理、Cookie和适用平台资源通过；
- 所有外部副作用都有读回；
- 页面不存在假成功；
- 本机执行只承担提醒和跳转；
- Evidence和人工验收覆盖完整纵向链路。
