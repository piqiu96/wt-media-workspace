# M2 实施计划

> 基于 PRD 第三章功能差距矩阵（64 功能点，当前 47% PASS）
> 按五条业务闭环顺序执行：A → B → C → D → E

---

## M2-A：用户与权限闭环

**目标**：技术创建用户 → 分配角色和游戏范围 → 用户登录 → 数据权限正确 → 修改和停用生效 → 审计记录可查看

| 项 | 当前 | 目标 | 工作量 |
|----|:----:|:----:|:------:|
| A5 权限校验穿透各模块 | BROKEN | PASS | 小 — 在每个业务接口入口调用 `CanAccessGame()` |
| A10 前端 401 自动跳登录 | BROKEN | PASS | 小 — http.js 拦截 401 响应跳转 /login |
| A11 Agent 被踢后停止领任务 | NOT_IMPLEMENTED | PASS | 中 — Agent 端轮询检测会话状态 |
| A12 比特绑定审计日志 | NOT_IMPLEMENTED | PASS | 小 — 注册审计事件 |

**验证方式**：创建不同角色用户 → 验证各业务接口权限正确 → 前端 401 跳转 → 审计日志可查

---

## M2-B：媒体账号与 Profile 闭环

**目标**：绑定 BitBrowser 主账号 → 扫描 Profile → 展示差异 → 人工确认同步 → 创建媒体账号 → 绑定 Profile → 打开并检查真实账号

| 项 | 当前 | 目标 | 工作量 |
|----|:----:|:----:|:------:|
| B3 登录后自动回填 | BROKEN | PASS | 小 — 前端接入 identify 接口 |
| B11 BitBrowser 绑定引导 | BROKEN | PASS | 中 — 完整绑定 UI 流程 |
| B13 main_user_id 二次校验 | BROKEN | PASS | 中 — 后端各接口增加 main_user_id 校验 |
| B15 Profile 扫描确认后闭环 | BROKEN | PASS | 中 — 确认后写入 BitBrowser 并读回验证 |
| B16 Diff 代理变化详情 | BROKEN | PASS | 小 — Diff 字段扩展 |
| B12 首次绑定 6 步流程 | NOT_IMPLEMENTED | PASS | 大 — 全流程 UI |
| B14 页面强提醒文案 | NOT_IMPLEMENTED | PASS | 小 — 前端提示 |
| B17 恢复系统配置选项 | NOT_IMPLEMENTED | PASS | 小 — Diff 确认加选项 |
| B18 扫描不覆盖运营字段 | NOT_IMPLEMENTED | PASS | 小 — 字段保护清单 |
| B19 账号检查（单条+批量） | NOT_IMPLEMENTED | PASS | 大 — Agent 执行+前端 UI |

**验证方式**：绑定 → 扫描 → Diff → 确认 → 打开 Profile → 检查账号 → 全流程可操作

---

## M2-C：代理与 Profile 闭环

**目标**：导入代理 → 解析预览 → 检测可用性 → 分配给 Profile → 写入 BitBrowser → 回读确认

| 项 | 当前 | 目标 | 工作量 |
|----|:----:|:----:|:------:|
| C5 代理真实连通性检测 | BROKEN | PASS | 中 — Agent 端代理检测 executor |
| C6 平台配额校验 | BROKEN | PASS | 小 — 分配 Profile 时校验配额 |
| C4 Excel/CSV/TXT 文件上传 | NOT_IMPLEMENTED | PASS | 中 — 前端文件上传+后端解析 |
| C7 全局平台默认配额 | NOT_IMPLEMENTED | PASS | 小 — 配置表+默认值 |
| C8 代理写 BitBrowser + 回读 | NOT_IMPLEMENTED | PASS | 大 — Agent 端完整执行器 |
| C9 自动分配代理 + 预览 | NOT_IMPLEMENTED | PASS | 中 — 分配算法+前端预览 |
| C10 Diff 新代理创建记录 | NOT_IMPLEMENTED | PASS | 小 — Diff 处理扩展 |
| C11 代理到期提醒 | NOT_IMPLEMENTED | PASS | 小 — 定时扫描+前端提示 |

**验证方式**：导入代理 → 检测 → 分配 → 写 BitBrowser → 回读 → Profile 可打开

---

## M2-D：Cookie 与开户闭环

**目标**：三种开户方式（批量 CK/接码链接/人工验证码）全部可工作

| 项 | 当前 | 目标 | 工作量 |
|----|:----:|:----:|:------:|
| D3 批量 CK → Profile → 代理 → 写 CK → 检查 → 回填 | NOT_IMPLEMENTED | PASS | 大 — Agent 端完整开户 executor |
| D4 CK 导出（原始/真实双选项） | NOT_IMPLEMENTED | PASS | 小 — 后端接口+前端 |
| D5 从 Profile 读取真实 CK | NOT_IMPLEMENTED | PASS | 中 — Agent 端读取 |
| D6 CK 写入 Profile | NOT_IMPLEMENTED | PASS | 中 — Agent 端写入 |
| D7 接码链接上号 | NOT_IMPLEMENTED | PASS | 大 — Agent 端接码流程 |
| D8 接码到期提醒 | NOT_IMPLEMENTED | PASS | 小 — 定时提醒 |
| D9 人工验证码上号 | NOT_IMPLEMENTED | PASS | 中 — 前端+Agent |
| D10 批量部分成功+失败重试 | NOT_IMPLEMENTED | PASS | 中 — 前端批量结果展示 |
| D11 代理容量不足提示 | NOT_IMPLEMENTED | PASS | 小 — 前端预检提示 |

**验证方式**：三种方式各跑通一条完整开户链路，批量部分成功可重试

---

## M2-E：Desktop 与安全闭环

**目标**：Desktop 端可完成本地管理操作

| 项 | 当前 | 目标 | 工作量 |
|----|:----:|:----:|:------:|
| E2 Local Agent Sidecar 真实启动 | BROKEN | PASS | 中 — Tauri sidecar 配置+验证 |
| E6 Dashboard 动态数据+路由 | BROKEN | PASS | 小 — 对接后端 API |

**验证方式**：Desktop 启动 → Agent 启动 → 状态展示 → 操作可执行

---

## 执行顺序与依赖

```text
M2-A（权限基础，无外部依赖）
  ↓
M2-B（媒体账号+Profile，依赖 M2-A）
  ↓
M2-C（代理，依赖 M2-B 的 Profile）
  ↓
M2-D（Cookie+开户，依赖 M2-B 的 Profile + M2-C 的代理）
  ↓
M2-E（Desktop，依赖其余全部）
```

## 验收标准

每条闭环完成后，必须满足：

1. 所有功能点从 PASS → 仍 PASS，BROKEN → PASS，NOT_IMPLEMENTED → PASS
2. 完整用户操作链路可跑通（不是只测 API）
3. 真实依赖可用（MySQL 持久化）
4. Evidence 写入对应 CHG 目录
5. 已有功能回归通过
