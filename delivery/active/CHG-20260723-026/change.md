# CHG-20260723-026：M2-B2 窗口同步应用、恢复与授权闭环

> 日期：2026-07-23  
> 状态：ACTIVE  
> 所属 Milestone：M2-B 浏览器窗口与媒体账号真实闭环  
> 关联闭环：`delivery/milestones/M2-account-runtime.md#M2-B-浏览器窗口与媒体账号真实闭环`  
> 当前仓库：`wt-media-workspace`  
> 预计影响仓库：`wt-media-cloud`、`wt-media-agent`、`wt-media-desktop`、`wt-media-workspace`

## 1. 用户可见目标

在 B1 已能从 Desktop 扫描 BitBrowser 并生成只读 Diff 的基础上，B2 让用户可以安全处理这些 Diff：

```text
Desktop扫描窗口
→ 查看Diff
→ 接受本地变化，更新Cloud窗口镜像
或
→ 恢复Cloud配置，写回BitBrowser并读回验证
→ Cloud窗口列表、授权关系和页面结果一致
```

本 CHG 只处理浏览器窗口同步应用、恢复和授权，不处理媒体账号绑定、账号检查、代理写入和 Cookie。

## 2. 当前背景

已完成/继承：

- M2-A 已完成用户、会话和本地环境可信基础；
- CHG-20260723-025 已实现 B1：Desktop 通过 Rust/Local Agent 扫描 BitBrowser，Cloud 生成只读 Diff，Cloud Web 不展示本机扫描入口；
- 用户确认：Cloud Web 对所有角色只展示 Cloud 已保存数据，Desktop 才处理 Agent / BitBrowser 能力；
- 用户确认：比特账号绑定信息展示先并入 M2-B 同步/详情设计，不在本机状态修复中单独补页面。

## 3. 本 CHG 范围

### 包含

- 审计 B1 的扫描结果、Diff 数据结构、Cloud 镜像字段和页面展示；
- Desktop 展示“接受本地变化”和“恢复 Cloud 配置”的明确入口；
- 接受本地变化：
  - 只在用户确认后应用 Diff；
  - 新增窗口写入 Cloud `browser_profiles`；
  - 名称、分组、代理摘要、运行状态等允许字段更新到 Cloud 镜像；
  - 本地缺失窗口按规则标记失效/疑似缺失，不物理删除历史；
  - 不覆盖 Cloud 授权用户、媒体账号绑定、游戏、标签、备注、Cookie 和业务状态；
- 恢复 Cloud 配置：
  - 仅在 Desktop 执行；
  - 通过 Tauri/Rust 调用 Local Agent 写回 BitBrowser；
  - 写回后必须重新读回验证；
  - 读回一致后才展示成功；
- 窗口授权：
  - 管理员可将未授权窗口分配给目标普通运营；
  - 高级运营只查看授权范围内 Cloud 状态，不操作他人本地窗口；
  - 普通运营只能处理本人授权窗口；
- 比特账号绑定摘要展示：
  - 在用户管理或窗口详情中提供只读摘要入口；
  - 仅展示绑定状态、绑定时间、最近验证时间和脱敏主账号标识；
  - 不展示 Agent 凭据、本地端口、Token 或完整诊断信息；
- 生成自动测试和 evidence，证明应用 Diff 和恢复配置不会产生越权或假成功。

### 不包含

- 不绑定、解绑或换绑媒体账号；
- 不执行账号检查；
- 不写入、读取或修改 Cookie；
- 不写入或更换代理；
- 不建设完整上号任务；
- 不做发布/互动预检；
- 不把 Cloud Web 变成本机 BitBrowser 操作入口；
- 不远程删除 BitBrowser 本地窗口。

## 4. 关键规则

- B2 可以应用 B1 生成的 Diff，但必须由用户明确确认；
- Diff 未确认前不得修改 Cloud 正式窗口镜像；
- 接受本地变化只更新 Cloud 允许字段，不覆盖业务字段；
- 恢复 Cloud 配置必须真实写 BitBrowser 并读回，不能用“请求成功”代替业务成功；
- Cloud Web 只能展示 Cloud 已保存的窗口与绑定摘要；依赖 Agent / BitBrowser 的处理入口只在 Desktop 展示；
- 管理员的 Cloud 权限不能绕过目标运营本机 Desktop、Local Agent 和 BitBrowser 边界；
- 窗口被媒体账号、代理或历史记录引用时，不能物理删除，只能标记失效/归档/待确认。

## 5. 执行任务

### Task 1：Start Gate 与 B1 继承审计

- 核对 `CURRENT_CONTEXT`、`LEDGER`、当前 active CHG 和 M2-B milestone；
- 审计 B1 产生的 scan / diff / page / Rust / Agent 链路；
- 明确可复用、需修正、需新增的文件映射；
- 确认 CHG-20260723-025 已完成 diff review / 提交 / 关闭后再激活本 CHG。

### Task 2：接受本地变化应用 Cloud 镜像

- 实现或修正 Diff 应用逻辑；
- 新增、变更、缺失窗口按 M2-B 规则写入 Cloud 镜像；
- 保证授权、账号绑定、游戏、标签、备注、Cookie 和业务状态不被扫描覆盖；
- 自动测试覆盖应用前后差异。

### Task 3：恢复 Cloud 配置写回 BitBrowser

- Desktop 提供恢复入口；
- Desktop Vue 经 Tauri/Rust 调用 Local Agent；
- Local Agent 同步写 BitBrowser；
- 写回后读回验证；
- 失败或结果不确定时进入可理解的待确认状态。

### Task 4：窗口授权与只读摘要展示

- 管理员可分配未授权窗口给普通运营；
- 普通运营、高级运营、管理员的 Cloud / Desktop 能力边界一致；
- 增加比特账号绑定摘要的只读展示入口；
- 避免暴露 Agent 凭据、Token、本地端口和完整诊断信息。

### Task 5：验证与 Evidence

- 自动测试覆盖 Diff 应用、业务字段保护、恢复读回、权限边界；
- 真实环境或明确 mock 证据覆盖 Desktop / Local Agent / BitBrowser 调用链；
- 页面 evidence 证明用户能看到应用结果、恢复结果和失败原因。

## 6. 验收标准

- Desktop 可以从已生成 Diff 进入“接受本地变化”；
- 接受后 Cloud 浏览器窗口镜像与本地扫描结果一致；
- 接受过程不覆盖授权、媒体账号绑定、游戏、标签、备注、Cookie 和业务状态；
- Desktop 可以发起“恢复 Cloud 配置”，并在 BitBrowser 写回后读回验证；
- Cloud Web 不展示依赖本机 Agent / BitBrowser 的处理入口；
- 管理员可以分配未授权窗口，普通运营只能处理本人授权窗口；
- 用户可查看必要的比特账号绑定摘要，但看不到本地凭据和技术细节；
- 失败、超时或读回不一致时不会显示假成功。

## 7. Evidence 要求

完成后在 `evidence/` 中至少提供：

- `start-gate.md`：B1 继承审计、文件映射和风险；
- `diff-apply-cloud-mirror.md`：接受本地变化前后 Cloud 镜像变化和业务字段保护；
- `restore-cloud-config-readback.md`：恢复写回 BitBrowser 和读回验证；
- `authorization-and-binding-summary.md`：窗口授权与比特账号绑定摘要展示验证；
- `tests.md`：自动测试和构建结果；
- `manual-acceptance.md`：人工验收步骤和结果。

## 8. 交付边界

本 CHG 完成后，M2-B 证明“窗口扫描 Diff 可以被安全处理”成立。

后续独立 CHG 继续处理：

- B3：媒体账号台账与 Profile 绑定；
- B4：媒体账号真实检查与身份回填。

## 9. Checkpoint

- Completed：CHG-20260723-025 已完成 diff review、验证和归档；本 CHG 已从 planned 激活为 active。
- Completed：Task 1 Start Gate 与 B1 继承审计已完成，见 `evidence/start-gate.md`。
- Completed：Task 2 接受本地变化应用 Cloud 镜像已完成，见 `evidence/diff-apply-cloud-mirror.md`。
- Completed：Task 3 恢复 Cloud 配置写回 BitBrowser 并读回验证已完成，见 `evidence/restore-cloud-config-readback.md`。
- Completed：Task 4 窗口授权与只读摘要展示已完成，见 `evidence/authorization-and-binding-summary.md`。
- Current：ACTIVE，已实现管理员分配 Cloud 窗口授权、已引用窗口阻断、浏览器窗口列表授权用户列、窗口详情只读绑定摘要。
- Next：执行 Task 5：验证与 Evidence 汇总。
- Blockers：无。
- Recent verification：`env GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build go test ./internal/modules/profilebinding ./internal/modules/identity` PASS；`npm --prefix wt-media-cloud/web test -- --run profileBindings usersApi` PASS；`npm run build:desktop --prefix wt-media-cloud/web` PASS；`npm run build:cloud --prefix wt-media-cloud/web` PASS；`git diff --check` PASS。
