# M2-A～E 当前代码差距审计

> 日期：2026-07-22  
> 基线：`delivery/milestones/M2-account-runtime.md`、产品第三章、工程架构、ADR-0008/0009  
> 范围：Cloud/Web、Local Agent、Desktop 当前代码；本报告不修改运行时代码。

## 1. 结论

当前实现保留了较多可复用基础，但仍不能按新基线验收 M2。主要问题不是缺少 CRUD，而是旧领域规则和执行模型仍在代码中：用户采用字符串 ID 和 `technician` 角色、没有运营分组；代理采用平台配额；媒体账号仍有 `retired`；Profile、代理、Cookie 等短操作主要创建异步任务；Web 仍直接访问固定 Agent 端口；账号开户仍以创建账号记录为主。

| 闭环 | 可复用基础 | 关键冲突或缺失 | 当前判断 |
|---|---|---|---|
| M2-A | 用户、游戏范围、会话、审计、Agent会话替换、BitBrowser身份扫描 | 自增UID、`admin`、运营分组、交集权限、确认式替换、身份扫描不应用Profile | 基础存在，领域模型必须迁移 |
| M2-B | Profile镜像、扫描/Diff、生命周期API、Agent BitBrowser适配器、账号台账 | Web直连8765、单项异步任务、Diff仅接受本地、授权/批量/真实检查UI不闭环 | 骨架可复用，纵向闭环未完成 |
| M2-C | 代理台账、解析、检测、assign接口、代理变更适配器 | 预览有副作用、平台配额、无完整分配UI、异步写入、缺少强制读回 | 台账可用，真实绑定未完成 |
| M2-D | original/active Cookie、Cookie读写和账号检查执行器 | 凭据字段、三类batch/item、接码/人工验证码、人工接管同步、冲突和恢复 | 未形成上号闭环 |
| M2-E | Tauri Agent生命周期、健康/绑定命令、Cloud任务与Agent运行基础 | 缺少通用同步安全桥、Web仍直连端口、开发fallback、打包/恢复/综合验收未证明 | 部分基础存在，产品化未完成 |

## 2. M2-A 差距

### 可复用

- `wt-media-cloud/internal/modules/identity` 已有用户创建、登录、游戏范围、密码变更、禁用和审计基础；
- `user_sessions`、Agent会话替换和失效节点停止领取任务已有代码与测试；
- `profilebinding` 与 Agent `BitBrowserClient.scan_profiles()` 已能读取并校验 `main_user_id`、`profile_user_id`。

### 必须迁移或补齐

- `migrations/20260714_001_identity.sql` 的 `users.id`、外键仍为 `VARCHAR(64)`，不符合自增主键UID；
- 角色仍为 `operator/senior_operator/technician`，服务和测试大量依赖 `RoleTechnician`，没有 `admin`；
- 没有运营分组表、`team_id`、转组历史归属和“同组∩授权游戏”权限模型；
- `Service.Login` 当前直接使旧会话失效，没有“发现旧会话—用户确认—再替换”；
- Profile扫描确认会写入正式Profile镜像，M2-A要求身份绑定阶段只验证主账号身份；
- Web用户管理尚未覆盖分组、管理员无分组、一次性展示新密码和确认式会话替换；
- 现有业务模块多数按 `user_id` 或旧角色判断，尚未统一接入管理员/同组/本人和游戏交集授权。

## 3. M2-B 差距

### 可复用

- `profilebinding` 已有扫描候选、Diff、确认后更新Cloud镜像和本地缺失标记；
- Cloud已有创建、打开、关闭、更新Profile入口，Agent已有对应BitBrowser适配器；
- `mediaaccount` 已有账号台账、标签、Profile唯一关系、Cookie字段和账号检查任务基础。

### 必须迁移或补齐

- `web/src/modules/profiles/pages/ProfilesPage.vue` 直接请求 `http://127.0.0.1:8765`，不符合Desktop/Tauri安全桥；
- 创建、打开、关闭页面只提示“已创建任务”，与单项短操作同步返回最终结果的新原则冲突；
- Diff只有接受本地变化，缺少恢复Cloud配置并写回、读回；
- 缺少管理员分配未授权窗口、用户授权边界、Profile编辑/分组/代理/账号影响的完整UI；
- 缺少单个和批量窗口操作的逐项最终结果与结果待确认；
- `AccountsPage.vue` 仍允许手工“保存识别”，没有完整账号检查入口和真实身份回填闭环；
- `media_accounts.business_status` 和页面仍包含 `retired`，需移除；
- 现有平台约束仍含抖音，M2 P0应以哔哩哔哩、百家号真实样例验收。

## 4. M2-C 差距

### 可复用

- `proxy_configs`、代理CRUD、文本解析、同步连通性检测和后台检测基础存在；
- Agent已有代理检测与Profile代理变更适配器；
- Cloud已有代理分配入口和Profile代理快照字段。

### 必须迁移或补齐

- `proxy_platform_quotas` 和服务仍按平台记录配额，需迁移为代理统一 `max_profile_count`；
- 缺少刷新URL、代理标签及对应生命周期；
- `ProxyPage.vue` 的“预览解析”实际调用导入接口，预览阶段并非零副作用；
- 文件导入没有可靠Excel结构解析，新增/编辑表单和重复项人工修正不完整；
- 页面没有选择Profile、推荐方案、人工调整、确认分配和占用可视化闭环；
- assign与Agent变更仍以异步任务为主，不符合单项同步调用；
- 写入、更换、解绑后没有强制读回再更新正式关系和配额；
- 外部代理变化、新发现代理和停用但仍被使用的提示未产品化。

## 5. M2-D 差距

### 可复用

- `media_accounts` 已保存 `original_cookie`、`active_cookie` 和登录/检查状态；
- Agent已有Cookie写入、读回验证和账号检查执行器；
- Cloud已有Cookie任务结果投影的局部逻辑。

### 必须迁移或补齐

- `media_accounts` 缺少 `login_username`、`login_phone`、`login_password`、`sms_receive_url`、`sms_receive_expires_at`；
- 没有 `account_login_batch/item` 领域模型和三类独立批次；
- `AccountOpeningPage.vue` 当前主要批量创建待识别账号，前端代理预览未形成真实副作用；
- 没有接码发送/轮询/过期/更新链接流程；
- 没有人工验证码等待、重发、继续、取消流程；
- 自动失败后“保留并打开窗口—人工登录—同步账号信息”的用户入口和Cloud回填接口缺失；
- 缺少上号前现有账号检测、账号不一致人工选择、同用户同平台UID去重；
- 单账号Cookie与检查仍依赖通用异步task，不符合短操作同步原则；
- 缺少批次取消、重启恢复、结果待确认和精确重试的统一实现。

## 6. M2-E 差距

### 可复用

- Desktop `src-tauri/src/main.rs` 已有Local Agent启动、停止、健康、状态和绑定命令；
- Agent本地API和BitBrowser适配器已覆盖部分Profile、代理、Cookie操作；
- Cloud已有任务租约、状态、结果和敏感Profile保护基础。

### 必须迁移或补齐

- Tauri尚无承载Profile、代理、Cookie、账号检查的统一同步安全桥；
- Vue页面仍直接访问固定Agent端口，端口和凭据边界不统一；
- Desktop仍包含Python开发fallback，真实打包Sidecar、启动清理和升级路径未证明；
- 同步调用超时后的读回、`result_uncertain`和幂等Cloud投影尚未形成统一模式；
- batch/item与异步task的恢复边界尚未在Desktop产品中落地；
- 缺少M2-A～D真实MySQL、Desktop、Agent、BitBrowser、代理和账号资源的综合证据矩阵。

## 7. 推荐实施顺序

1. **A1 用户领域迁移**：自增UID、三角色、运营分组、游戏交集权限及迁移测试；
2. **A2 会话与环境可信**：确认式会话替换、身份扫描只验证、Desktop确认重绑；
3. **E1 同步安全桥前置切片**：先提供B/C/D共用的Tauri→Agent同步调用、读回和结果投影边界；
4. **B1～B4**：Profile Diff双向、生命周期/授权、账号台账绑定、真实检查；
5. **C1～C4**：无副作用导入、统一配额、真实写入读回、外部变化；
6. **D1～D6**：凭据模型、三类批次、人工接管、冲突/导出/恢复；
7. **E2～E3**：打包Sidecar、恢复、安全与M2综合真实验收。

一次只激活一个CHG。共享同步安全桥可以作为M2-E的前置技术切片，但验收必须由首个实际B/C/D业务操作证明，不能单独以接口存在判定完成。

## 8. CHG-021 处置建议

当前CHG-021按旧M2-A口径只做验收收口，已不足以覆盖新确认的用户模型。应暂停原任务列表并重新收敛为 **A1 用户领域迁移**，先完成自增UID、`admin/senior_operator/operator`、运营分组及权限交集；A2会话和BitBrowser身份可信另建后续CHG。未完成A1前不得执行旧“三角色验收收口”，否则验收的是已废弃模型。
