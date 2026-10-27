# T-22 管理员转素材去向与角色能力矩阵

日期：2026-10-27（Asia/Shanghai）
结论：转素材去向 PASS（机器腿）；角色能力矩阵登记完成。T-23 的行已在 `T-23-system-management-roles.md` 落地并回填；T-24 / T-25 的行在各自证据落地前仍是计划，不是既成事实

## 提交

| 仓 | 分支 | 提交 |
| --- | --- | --- |
| wt-media-cloud | `chg/CHG-20261015-098-round3` | `3ca6d09`（转素材去向 + `feedback.notice`） |
| wt-media-workspace | `chg/CHG-20261015-098-docs` | 本文件所在提交（PRD 第四章 §4.3.8 / §4.7.1、第五章 §5.3.2） |

## 一、管理员转素材去向

### 目标团队由来源内容决定（服务端事实）

`wt-media-cloud/internal/modules/contentpool/repository/store_mysql.go` 的 `materialize` 在事务里锁定 `source_contents` 行，并以 `INSERT INTO materials (team_id, ...) VALUES (source.TeamID, ...)` 落库。团队不是请求参数，管理员也没有团队选择入口。

### 前端反馈

| 场景 | 运营 / 高级运营 | 管理员 |
| --- | --- | --- |
| 单条转素材 | 原 toast「已转为素材，来源关系已保留」 | `feedback.notice`：「素材 {id}「{title}」已转入团队「{team}」的素材库」，单按钮「知道了」 |
| 批量转素材 | 原 toast「转素材成功 N 条，失败 M 条」 | 同一弹窗内先给成功/失败数，再按目标团队聚合：`团队「X」：N 条；团队「Y」：M 条` |
| 审核模式「转素材并下一条」 | 无提示（原有） | 非阻塞 toast 带出目标团队，不弹窗打断连续操作 |
| 失败 | 原错误 toast | 原错误 toast，不弹成功告知 |

实现位置：`wt-media-cloud/web/src/modules/contentpool/pages/ContentPoolPage.vue` 的 `teamName`、`announceMaterialized`、`materialize`、`batchMaterialize`、`reviewAction`；`wt-media-cloud/web/src/shared/ui/feedback/index.js` 的 `notice`（`DialogPlugin.alert`，库内会把 `cancelBtn` 置空，确认为单按钮）。

### 测试

| 项 | 读数 |
| --- | --- |
| `web/src/shared/ui/feedback/index.test.js` | 新增 `notice` 两条：单按钮/默认「知道了」、点击确认与右上角关闭只收口一次；自定义确认文案 |
| `web/src/modules/contentpool/pages/ContentPoolPage.test.js` | 新增「tells an administrator which team received the material」，断言团队名映射、单条弹窗文案、批量按团队聚合、审核模式 `modal: false`、失败仍走错误 toast |
| 全量 | `npx vitest run`（在 `wt-media-cloud/web` 下）85 文件 / 768 测试全绿 |

### 未覆盖

- 真实页面弹窗视觉与团队名文案由 T-26 三账号走查确认；本机无法程序化驱动 GUI。
- 开发库里管理员账号（admin）尚无本轮改动后的 API 进程，HTTP 读回并入 T-26 重启验证。

## 二、角色能力矩阵

口径：三角色 `operator`（普通运营）/ `senior_operator`（高级运营）/ `admin`（管理员）。「当前」为本文写作时 `chg/CHG-20261015-098-round3` 的代码事实；「本轮目标」是已拍定的第三轮口径，标注了承载任务。表内 `✅` 可操作、`👁` 只读可见、`✗` 不可见/被拒。除特别标注外，服务端都按团队边界强制执行。

10 秒自动刷新（T-25）是页面级行为，对三种角色一致，不改变任何授权；下表只在内容池与合成任务两行标出「当前有刷新按钮」这一事实，其余目标页同理。

### 2.1 内容挖掘

**内容池（source_content）**

| 操作 | operator | senior_operator | admin | 结论 |
| --- | --- | --- | --- | --- |
| 查看列表 / 详情 | ✅ 本团队 | ✅ 本团队 | ✅ 可选团队，未选为全部 | 保留 |
| 人工导入（ID/链接、关键词） | ✅ 团队锁定 | ✅ 团队锁定 | ✅ 可选择团队 | 保留 |
| 转素材 | ✅ | ✅ | ✅（本轮起弹窗告知目标团队） | 调整 T-22 |
| 批量转素材 | ✅ 上限 500 | ✅ | ✅（按团队聚合告知） | 调整 T-22 |
| 忽略 / 恢复 | ✅ | ✅ | ✅ | 保留 |
| 来源策略弹窗 | ✅ | ✅ | ✅ | 保留 |
| 审核模式 | ✅ | ✅ | ✅ | 保留 |
| 刷新按钮 | 有 | 有 | 有 | 调整 T-25：移除，10 秒自动刷新 |

服务端门禁：`contentService.scope`（非管理员必须属于本团队，请求他人团队即 403）、`get` 用来源行的团队复核；转素材只多一层可见性，不另设角色门禁。

**挖掘策略（discovery_strategy）**

| 操作 | operator | senior_operator | admin | 结论 |
| --- | --- | --- | --- | --- |
| 查看 | 👁 仅本人负责且启用的策略 | 👁 本团队全部 | 👁 跨团队 | 保留（ADR-0023） |
| 新增 / 编辑 / 启停 / 复制 | ✗ | ✅ 本团队 | ✅ 跨团队 | 保留 |
| 立即执行 | ✗ | ✅ | ✅ | 保留 |
| 自动转素材规则 | 👁 | ✅ 维护 | ✅ 维护 | 保留 |

服务端：`canManageDiscovery` = senior 或 admin；`canReadStrategy` 对 operator 要求启用且 `operator_id` 为本人，游戏限本人负责。

**挖掘任务（crawl_task）**

| 操作 | operator | senior_operator | admin | 结论 |
| --- | --- | --- | --- | --- |
| 查看 | 👁 本人在负责游戏内的任务 | 👁 本团队 | 👁 跨团队 | 保留 |
| 重试失败任务 | ✗ | ✅ | ✅ | 保留（异常处理归管理角色） |
| 定时 / 手动触发口径 | 👁 | ✅ | ✅ | 保留 |

服务端：`task.go:337` 对 operator 固定 `OperatorID` 与负责游戏；`requireDiscoveryManager` 管任务异常。

### 2.2 内容生产

**素材库（material）**

| 操作 | operator | senior_operator | admin | 结论 |
| --- | --- | --- | --- | --- |
| 查看本团队素材 | ✅ | ✅ | ✅ 可选目标团队 | 保留 |
| 加入 / 重新加入我的素材 | ✅ | ✅ | ✅（需本人关系） | 保留 |
| 使用情况列 | 👁 成功成片数 + 使用人数 | 👁 + 使用人姓名 | 👁 + 使用人姓名 | 保留 |
| 操作人列 | ✅ | ✅ | ✅ | 保留（T-21） |
| 本机下载 | ✗ 素材库不提供 | ✗ | ✗ | 保留（§5.3.4） |

服务端：`ListMaterialsFiltered` 对 operator / senior 强制本团队；`decorateMaterials` 仅对 senior / admin 保留使用人姓名；下载只从「我的素材」发起且要求本人 `active` 关系。

**我的素材（material_usage）**

| 操作 | operator | senior_operator | admin | 结论 |
| --- | --- | --- | --- | --- |
| 查看 | 👁 仅本人关系 | 👁 仅本人关系 | 👁 仅本人关系 | 保留（§5.4.3） |
| 移出 / 恢复 | ✅ 本人关系 | ✅ 本人关系 | ✅ 本人关系 | 保留 |
| 下载原视频 | ✅ | ✅ | ✅（均需本人关系） | 保留 |

服务端：`ListMyMaterials`、`FindUsageForUser` 都以当前用户 ID 为准，三种角色没有例外。

**合成策略（compose_strategy）**

| 操作 | operator | senior_operator | admin | 结论 |
| --- | --- | --- | --- | --- |
| 查看 | 👁 仅启用且指定本人的策略 | 👁 本团队全部游戏 | 👁 跨团队，可选团队 | 保留 |
| 新增 / 编辑 / 启停 / 复制 | ✗ | ✅ 本团队 | ✅ 跨团队 | 保留 |
| 立即执行 | ✗ | ✅ | ✅ | 保留 |

服务端：`canManageStrategies` = senior 或 admin；策略负责人须为团队内负责该游戏的有效运营（§5.6.2）。

**合成任务（compose_task）**

| 操作 | operator | senior_operator | admin | 结论 |
| --- | --- | --- | --- | --- |
| 查看 | 👁 本人负责、本人游戏内 | 👁 本团队 | 👁 跨团队 | 保留 |
| 创建人工任务 | ✅ 负责人固定本人 | ✅ 可代本团队运营创建 | ✅ 可选团队后代创建 | 保留 |
| 取消 | ✅ 本人可读任务 | ✅ 本团队 | ✅ 跨团队 | 保留 |
| 重试失败任务 | ✗ | ✅ | ✅ | 保留 |
| 异常结果人工核对 | ✗ 只看到失败事实与联系提示 | ✅ | ✅ | 保留（§5.8.6） |
| 列表刷新 | 5 秒轮询 + 刷新按钮 | 同左 | 同左 | 调整 T-25：列表改 10 秒自动刷新；任务详情抽屉仍单独轮询 |

服务端：`Create` 允许三角色（`task.go:181`），`resolveComposeListScope` 对 operator 固定本人；`Retry`、不确定执行核对都只给 senior / admin。

**成片管理（composite_output）**

| 操作 | operator | senior_operator | admin | 结论 |
| --- | --- | --- | --- | --- |
| 查看列表 / 详情 | 👁 本人负责、本人游戏内 | 👁 本团队 | 👁 跨团队 | 保留 |
| 预览 / 下载 | ✅ 可读范围内，下载到本人本机 | ✅ | ✅ | 保留 |
| 归档 | ✅ 可读范围内 | ✅ | ✅ | 保留 |

服务端：`canReadComposeOutput` 同任务口径；下载沿用 `user_download`，落到发起人自己的 Local Agent。

### 2.3 运营资源

**社媒账号（media_account）**

| 操作 | operator | senior_operator | admin | 结论 |
| --- | --- | --- | --- | --- |
| 查看 | 👁 仅本人账号 | 👁 本团队账号 | 👁 全部账号 | 保留 |
| 新增账号 | ✅ 仅本人 | ✅ 仅本人 | ✅ 可为指定用户创建 | 保留 |
| 编辑（业务状态 / 登录状态 / 备注 / 游戏 / 标签） | ✅ 本人账号 | ✅ 当前本团队账号 | ✅ 当前全部账号 | 与「他人 / 管理员只读」表面冲突，待裁定（见 §三-3） |
| 使用人列与筛选 | ✗ 无此列，服务端固定本人 | ✗ 当前无列 | ✗ 当前无列 | 调整 T-24：列表加「使用人」；高级运营默认本人、可切全部成员；管理员默认全部成员 |
| 绑定 / 解绑窗口 | ✅ 本人账号 | ✅ 当前本团队账号（只能绑到账号本人名下的窗口） | ✅ 当前全部账号 | 同上，待裁定（见 §三-3） |
| 本地检查 / 读 Cookie | ✅ 本人账号 | ✗ 当前服务端 403 | ✗ | 调整 T-24：高级运营本人账号可执行；他人账号只读；管理员恒不可执行 |
| 查看已存 Cookie | 👁 本人账号 | 👁 仅本人账号（他人被拒） | 👁 任意账号 | 保留但登记待裁定（见 §三-2） |
| 账号分组 | ✅ 本团队范围 | ✅ 本团队 | ✅ 全部 | 保留 |

服务端：`ListAccounts` 对 operator 固定 `user_id`，再按 `CanAccessOwnedResource` 过滤（本人 / 本团队 / 全部）；`StartLocalAccountCheck`、`StartCookieRead` 当前硬性 `role == operator` 且随后 `GetOwnedAccountRecord` 要求本人；`GetAccountRecord`（含 Cookie）允许本人或管理员。

**开户（account-opening）/ 浏览器窗口（browser-window）/ 代理（proxy）**

| 项 | operator | senior_operator | admin | 结论 |
| --- | --- | --- | --- | --- |
| Cloud Web 菜单 | ✅ 可见 | ✅ 可见（当前未隐藏） | ✅ 可见（当前未隐藏） | 待裁定（见 §三-1） |
| Desktop 菜单 | ✅ | ✗ 当前被 `localOnlyPaths` 隐藏 | ✗ 当前被 `localOnlyPaths` 隐藏 | 保留（本轮 T-23 只把 `accounts` 移出 localOnly，这三条继续仅普通运营） |
| 实际本地能力 | ✅ | ✗ | ✗ | 保留 |

服务端：Profile / Proxy 资源按 `CanAccessOwnedResource` 授权；Desktop 路由 `meta.localOnly` 仍拦非 operator。

### 2.4 系统管理

| 页面 / 操作 | operator | senior_operator | admin | 结论 |
| --- | --- | --- | --- | --- |
| 用户管理 | ✗ | ✗ | ✅ | 保留（本轮拍定） |
| 运营团队查看 + 人数 | ✗ | 👁 已实现（T-23）：可见只读，人数取服务端 `user_count` | ✅ | 调整 T-23 已完成 |
| 运营团队增改删 | ✗ | ✗ | ✅ | 保留 |
| 游戏管理查看 | ✗ | 👁 已实现（T-23）：`scope=management`，全部状态、无关联摘要 | ✅ 全部状态 + 关联摘要 | 调整 T-23 已完成 |
| 游戏增改删 / 关联情况 | ✗ | ✗ | ✅ | 保留 |
| Cloud Web 入口 | ✗ | ✅ 已实现（T-23）：团队 / 游戏对高级运营开放 | ✅ | 调整 T-23 已完成（`shared/utils/roles.js`） |
| Desktop 入口 | ✗ | ✅ 已实现（T-23）：三页进入 Desktop，共用 Cloud 组件 | ✅ 已实现（T-23） | 调整 T-23 已完成 |

服务端：`CreateUser`、`ForceLogout`、`SetUserStatus`、`ResetPassword`、`UpdateUser`、`DeleteUser`、`ListUsers`、团队的增改删、游戏的增改删与 `GameReferences` 都是 admin-only；`ListTeams` 任何登录用户可读，响应带 `user_count`。`ListGames` 默认非管理员只回启用且分给自己的游戏，`scope=all` 放开到全部启用游戏（作筛选用），`scope=management` 只给 senior + admin、返回全部状态且不含关联摘要（T-23 已实现）。

### 2.5 桌面环境与本地 Agent

| 项 | operator | senior_operator | admin | 结论 |
| --- | --- | --- | --- | --- |
| 本地日志 / 本机设置 | ✅ | ✅ 已实现（T-23）：菜单与路由都放行 | ✗ 已实现（T-23）：菜单隐藏且守卫退回内容池 | 调整 T-23 已完成 |
| sidecar 启动 | ✅ | ✗ 当前 `canUseLocalAgent` 仅 operator | ✗ | 调整 T-24：新增 `canRunLocalAgent`（operator + senior），管理员仍停止 |
| 工作环境胶囊（WorkEnvPill） | ✅ | ✗ | ✗ | 调整 T-24 同上 |

服务端：`AuthenticateAgentSession` 与 `syncLocalAgentFor` 的现有实现对非 operator 一律拒绝/停止；本轮只放开 senior 的本人账号本地操作，不放开 Cloud 数据权限。

## 三、待裁定

以下四项是当前代码事实与用户已拍定口径之间没有明确覆盖到的差异。矩阵先登记，不静默改：

1. **Cloud Web 上开户 / 浏览器窗口 / 代理对高级运营与管理员仍可见**：`apps/cloud/main.ts` 只拦系统管理三页；Desktop 才用 `localOnlyPaths` 隐藏。这些页面在 Cloud Web 没有本地能力，点进去是空转。是否也应在 Cloud Web 隐藏（按「本地执行面只属于普通运营」）？
2. **管理员可读取任意账号已存 Cookie**：`GetAccountRecord` 允许本人或管理员，`AccountsPage` 的 Cookie 弹窗对列表内任意行可用。这与「管理员对账号只读」字面一致（读操作），但涉及敏感数据。是否保留管理员读他人 Cookie 的能力？
3. **账号云端编辑与窗口绑定的「只读」边界**：`UpdateAccount`、`changeTags`、`BindProfile` / `UnbindProfile` 都走 `authorizedRecord`（本人 / 本团队 / 全部），所以高级运营能改本团队成员的备注、业务状态、登录状态、游戏、标签并绑定 / 解绑其窗口，管理员能改全部账号。用户拍定的是「其他成员的账号对高级运营只读，管理员对所有账号只读」，字面上与这些写操作冲突；但同一句里的「能操作」也可以只指本地操作。需要裁定：是收紧到「只有账号本人能改云端字段、管理员也只读」，还是保留管理角色的云端管理能力、只把本地执行限制为本人？
4. **普通运营在内容池可处理本团队全部来源**（可跨负责游戏），而挖掘任务 / 合成任务只给自己负责游戏范围内的行。这是既有 PRD 口径（内容池是团队公共池），登记为保留，不再改。

## 四、未覆盖

- T-23 已落地（`T-23-system-management-roles.md`），但真实页面读数仍并入 T-26 三账号走查；T-24 / T-25 的目标行只有代码位置与口径，各自证据文件落地后以那份为准。
- Desktop 菜单与禁用态的最终视觉无法程序化验证，交 T-26 用户按打包产物确认。
- 管理员转素材的真实弹窗与团队名文案并入 T-26 三账号走查。
