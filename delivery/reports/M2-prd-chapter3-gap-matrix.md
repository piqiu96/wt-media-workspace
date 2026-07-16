# M2 PRD 第三章功能差距审查矩阵

> 生成日期：2026-07-16
> 方法：逐条对照 PRD 第三章《用户与账号管理》详细文档
> 状态：PASS / BROKEN / NOT_IMPLEMENTED / BLOCKED

## 汇总

| 闭环 | 功能点 | PASS | BROKEN | NOT_IMPLEMENTED | 完成率 |
|------|:-----:|:----:|:------:|:---------------:|:------:|
| A：用户与权限 | 12 | 8 | 2 | 2 | 67% |
| B：媒体账号与 Profile | 20 | 10 | 5 | 5 | 50% |
| C：代理 | 11 | 3 | 3 | 5 | 27% |
| D：Cookie与开户 | 11 | 2 | 0 | 9 | 18% |
| E：Desktop与安全 | 10 | 7 | 2 | 0 | 70% |
| **合计** | **64** | **30** | **12** | **21** | **47%** |

## M2-A：用户与权限闭环（12 项）

| # | PRD 功能 | UI | API | DB | Agent | 真实依赖 | 完整跑通 | 状态 | 备注 |
|---|----------|:--:|:---:|:--:|:-----:|:--------:|:--------:|:----:|------|
| A1 | 技术创建用户（用户名+密码） | ✅ | ✅ | ✅ | — | MySQL | ✅ | PASS | |
| A2 | 分配角色（operator/senior_operator/technician） | ✅ | ✅ | ✅ | — | MySQL | ✅ | PASS | |
| A3 | 分配游戏范围（多游戏） | ✅ | ✅ | ✅ | — | MySQL | ✅ | PASS | |
| A4 | 用户登录 → 会话 → Cookie | ✅ | ✅ | ✅ | — | MySQL | ✅ | PASS | |
| A5 | 数据权限正确（技术全量、运营限游戏） | — | ✅ | ✅ | — | 多用户 | ⚠️ | BROKEN | `mediaaccount` 等模块未在每个业务接口调用 `CanAccessGame()` |
| A6 | 修改用户角色/状态/游戏范围 | ✅ | ✅ | ✅ | — | MySQL | ✅ | PASS | |
| A7 | 停用用户 → 禁止登录、不删数据 | ✅ | ✅ | ✅ | — | MySQL | ✅ | PASS | |
| A8 | 重置密码 / 修改密码 | ✅ | ✅ | ✅ | — | MySQL | ✅ | PASS | |
| A9 | 审计日志（创建/修改/角色/状态/密码） | ✅ | ✅ | ✅ | — | MySQL | ✅ | PASS | |
| A10 | 单会话限制（新登录踢旧会话） | — | ✅ | ✅ | — | MySQL | ⚠️ | BROKEN | 前端无 401 自动跳登录 |
| A11 | Agent 被踢后停止领任务+安全停止执行中 | — | — | — | ❌ | — | ❌ | NOT_IMPLEMENTED | Agent 无会话失效检测 |
| A12 | 审计日志"重新绑定比特账号"事件 | — | ❌ | — | — | — | ❌ | NOT_IMPLEMENTED | 日志事件未注册 |

## M2-B：媒体账号与 Profile 闭环（20 项）

| # | PRD 功能 | UI | API | DB | Agent | 真实依赖 | 完整跑通 | 状态 | 备注 |
|---|----------|:--:|:---:|:--:|:-----:|:--------:|:--------:|:----:|------|
| B1 | 创建 media_account（归属当前用户） | ✅ | ✅ | ✅ | — | MySQL | ✅ | PASS | |
| B2 | 指定平台 + 游戏 | ✅ | ✅ | ✅ | — | MySQL | ✅ | PASS | |
| B3 | pending_identification → 登录后回填信息 | ✅ | ✅ | ✅ | — | MySQL | ⚠️ | BROKEN | 前端无"登录后自动回填"流 |
| B4 | original_cookie + active_cookie 双字段 | — | ✅ | ✅ | — | MySQL | ✅ | PASS | |
| B5 | 用户级去重 | — | ✅ | ✅ | — | MySQL | ✅ | PASS | |
| B6 | 重复标记 | — | ✅ | ✅ | — | MySQL | ✅ | PASS | |
| B7 | 标签：批量添加/移除 | ✅ | ✅ | ✅ | — | MySQL | ✅ | PASS | |
| B8 | 按标签筛选 | ✅ | ✅ | — | — | MySQL | ✅ | PASS | |
| B9 | 绑定 Browser Profile（同平台最多一个） | ✅ | ✅ | ✅ | — | MySQL | ✅ | PASS | |
| B10 | 一个 Profile 绑定多个平台账号 | ✅ | ✅ | ✅ | — | MySQL | ✅ | PASS | |
| B11 | 绑定 BitBrowser 主账号 | — | ✅ | ✅ | ✅ | BitBrowser | ⚠️ | BROKEN | 无完整前端绑定引导 |
| B12 | 首次绑定 6 步流程 | ❌ | — | ✅ | ✅ | BitBrowser | ❌ | NOT_IMPLEMENTED | |
| B13 | 同步前强校验 main_user_id + 不一致阻断 | — | — | — | ✅ | BitBrowser | ⚠️ | BROKEN | 后端未在所有接口二次校验 |
| B14 | 页面强提醒文案 | ❌ | — | — | — | — | ❌ | NOT_IMPLEMENTED | |
| B15 | Profile 扫描 → Diff 生成 | ✅ | ✅ | ✅ | ✅ | BitBrowser | ⚠️ | BROKEN | 确认后无"应用→验证"闭环 |
| B16 | Diff 展示全部变化类型 | ✅ | — | ✅ | ✅ | BitBrowser | ⚠️ | BROKEN | 代理变化未展示详情 |
| B17 | Diff 确认"接受/恢复"二选一 | ❌ | — | — | — | — | ❌ | NOT_IMPLEMENTED | 只有"接受" |
| B18 | 扫描不覆盖运营字段 | — | — | ❌ | — | — | ❌ | NOT_IMPLEMENTED | 无字段保护清单 |
| B19 | 账号检查：单条+批量（8 项） | ❌ | ❌ | — | ❌ | BitBrowser | ❌ | NOT_IMPLEMENTED | |
| B20 | 登录状态 8 种 | — | ✅ | ✅ | — | MySQL | ✅ | PASS | |

## M2-C：代理与 Profile 闭环（11 项）

| # | PRD 功能 | UI | API | DB | Agent | 真实依赖 | 完整跑通 | 状态 | 备注 |
|---|----------|:--:|:---:|:--:|:-----:|:--------:|:--------:|:----:|------|
| C1 | 代理 CRUD | ✅ | ✅ | ✅ | — | MySQL | ✅ | PASS | |
| C2 | 列表筛选 | ✅ | ✅ | — | — | MySQL | ✅ | PASS | |
| C3 | 文本批量导入+解析预览 | ✅ | ✅ | — | — | — | ✅ | PASS | |
| C4 | Excel/CSV/TXT 文件上传解析 | ❌ | ❌ | — | — | — | ❌ | NOT_IMPLEMENTED | |
| C5 | 代理检测（连通性） | ✅ | ✅ | — | — | 真实代理 | ⚠️ | BROKEN | 接口存在但未验证真实执行 |
| C6 | 平台配额 + 配额校验 | — | ✅ | ✅ | — | MySQL | ⚠️ | BROKEN | 分配 Profile 时未校验配额 |
| C7 | 全局平台默认配额 | — | ❌ | ❌ | — | — | ❌ | NOT_IMPLEMENTED | |
| C8 | 代理写 BitBrowser → 读回验证 | — | — | — | ❌ | BitBrowser | ❌ | NOT_IMPLEMENTED | |
| C9 | 自动分配代理 + 分配预览 | ❌ | ❌ | — | — | — | ❌ | NOT_IMPLEMENTED | |
| C10 | Diff 发现新代理→创建记录→提示补充 | — | — | — | — | — | ❌ | NOT_IMPLEMENTED | |
| C11 | 代理到期提醒 | ❌ | ❌ | — | — | — | ❌ | NOT_IMPLEMENTED | |

## M2-D：Cookie 与开户闭环（11 项）

| # | PRD 功能 | UI | API | DB | Agent | 真实依赖 | 完整跑通 | 状态 | 备注 |
|---|----------|:--:|:---:|:--:|:-----:|:--------:|:--------:|:----:|------|
| D1 | 单条 CK 导入 | — | ✅ | ✅ | — | MySQL | ✅ | PASS | |
| D2 | 批量 CK 导入 → 创建 media_account | ✅ | ✅ | ✅ | — | MySQL | ✅ | PASS | 当前实现止步于此 |
| D3 | 批量 CK → 创建 Profile + 分配代理 + 写 CK + 检查 + 回填 | ❌ | ❌ | — | ❌ | BitBrowser | ❌ | NOT_IMPLEMENTED | |
| D4 | CK 导出（原始CK/真实CK 双选项） | ❌ | ❌ | — | — | — | ❌ | NOT_IMPLEMENTED | |
| D5 | 从 Profile 读取真实 CK | — | — | — | ❌ | BitBrowser | ❌ | NOT_IMPLEMENTED | |
| D6 | CK 写入 Profile | — | — | — | ❌ | BitBrowser | ❌ | NOT_IMPLEMENTED | |
| D7 | 接码链接上号完整流程 | ❌ | ❌ | — | ❌ | 接码平台 | ❌ | NOT_IMPLEMENTED | |
| D8 | 接码到期提醒 | ❌ | ❌ | — | — | — | ❌ | NOT_IMPLEMENTED | |
| D9 | 人工验证码上号 | ❌ | ❌ | — | ❌ | BitBrowser | ❌ | NOT_IMPLEMENTED | |
| D10 | 批量操作部分成功+失败项重试 | ❌ | — | — | — | — | ❌ | NOT_IMPLEMENTED | |
| D11 | 代理容量不足时执行前提示 | ❌ | ❌ | — | — | — | ❌ | NOT_IMPLEMENTED | |

## M2-E：Desktop 与安全闭环（10 项）

| # | PRD 功能 | UI | API | DB | Agent | 真实依赖 | 完整跑通 | 状态 | 备注 |
|---|----------|:--:|:---:|:--:|:-----:|:--------:|:--------:|:----:|------|
| E1 | Desktop 启动 | ✅ | — | — | — | Desktop | ✅ | PASS | |
| E2 | Local Agent Sidecar 启动 | — | — | — | ✅ | Desktop | ⚠️ | BROKEN | 命令返回"start_requested"但未验证实际启动 |
| E3 | 登录 Cloud | ✅ | ✅ | — | — | Cloud | ✅ | PASS | |
| E4 | 查看本地环境状态 | ✅ | — | — | ✅ | Desktop | ✅ | PASS | |
| E5 | 执行账号/Profile 操作（通过 Cloud API） | ✅ | ✅ | ✅ | — | Cloud | ✅ | PASS | |
| E6 | 查看进度与错误 | ✅ | ✅ | — | — | Cloud | ⚠️ | BROKEN | Dashboard 硬编码 0，TasksPage 未接入路由 |
| E7 | 未授权操作被阻止 | — | ✅ | — | — | — | ✅ | PASS | |
| E8 | 同一 Profile 敏感任务不能并发 | — | ✅ | ✅ | ✅ | — | ✅ | PASS | |
| E9 | Tauri 不直接写 SQLite | — | — | — | — | — | ✅ | PASS | |
| E10 | Agent 只监听 127.0.0.1 | — | — | — | ✅ | — | ✅ | PASS | |
