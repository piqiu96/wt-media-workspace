# M2-B 浏览器窗口收口矩阵

日期：2026-08-05
CHG：CHG-20260725-031（M2-B 浏览器窗口收口，原"M2-B7 批量账号检查与 M2-B 综合收口"拆分收窄）
所属 Milestone：M2-B 浏览器窗口与媒体账号真实闭环

> 本矩阵只判定**浏览器窗口**这一垂直切片。社媒账号侧（账号台账/绑定/检查真实回填/功能缺口）见 `delivery/planned/CHG-20260805-032`。历史 M2-B 综合快照见 `m2-b-closure.md`。

## 完成标准对照

| M2-B 窗口完成标准 | 状态 | Evidence |
|---|---|---|
| 单个和批量窗口真实创建、逐项读回、部分成功和失败项重试成立 | **PASS**（API/自动验证）；A3 新建窗口 GUI 复验待用户 | B5、`manual-acceptance-profile-create-tested.md`、`manual-acceptance-20260803-runtime.md`（真实创建 `9e6c697c…` 读回 seq/group/proxy）、`browser-window-product-optimization.md` 第二轮（批量开/关实现） |
| 自动与手工扫描均只产生 Diff，用户可以接受或恢复且读回一致 | **接受方向 PASS**（用户 GUI 确认）；**恢复方向 DEFER**（A2 已实现、待真实环境验收） | `browser-window-product-optimization.md`「Diff 闭环修复批」；A2 链路见 change.md §0/§6 |
| 不真实删除 BitBrowser Profile；窗口退役走业务状态（停用影响账号匹配/执行资格；停用+本机已删→同步删除 Cloud 镜像） | **PASS**（API 实测 + 语义修订） | Milestone `M2-account-runtime.md` L229；`browser-window-product-optimization.md` 第一轮 |
| 管理员可分配未授权 Profile；高级运营只查看同组授权范围的 Cloud 状态 | **PASS** | B2 `authorization-and-binding-summary.md`；profilebinding service 测试（admin assign / senior 只读） |
| 页面、Cloud 镜像、Agent 读回和 BitBrowser 实际状态一致 | **部分 PASS**：窗口创建/读回/开/关已读回一致；平台身份一致性属账号侧（移交账号 CHG） | `manual-acceptance-20260803-runtime.md`（profile-create/read-back/open/close 真实读回一致） |
| Cloud Web 与 Desktop 页面边界清晰 | **PASS** | `batch-account-check.md`（Cloud Web 不展示本机入口）、`login-blocks.md`（Desktop 经 Tauri 调 Agent，cloudBaseUrl 指向 127.0.0.1:18080） |
| 窗口业务状态/停用（business_status）、自增主键迁移、编辑 Cloud 备注 | **PASS**（API 实测） | `browser-window-product-optimization.md` 第一轮（016 迁移）、第二轮（017 迁移） |

## 待用户 GUI 确认项（回填后转 PASS）

| 项 | 验收动作 | 预期结果 |
|---|---|---|
| A3 新建窗口 | 打包 Desktop「浏览器窗口」页新建窗口 | 新窗口出现在列表（ID/seq/名称/分组），无"已创建任务"式假成功 |
| A4 批量开/关 | 多选窗口→批量打开/关闭 | 运行状态列随操作切换，失败项有原因 |
| A2 恢复 Cloud 配置 | Diff 抽屉「恢复Cloud配置并读回验证」 | BitBrowser 被写回 Cloud 配置，重扫读回一致 |
| Agent 状态页 | 打包 Desktop 登录后进入 Agent 状态页 | 环境状态正常（Agent/比特浏览器/主账号） |

## 已记录的已知缺口（不属于窗口收口阻断项）

- `RejectScan` 后端为空操作、「取消变更」仅前端关抽屉——符合 Milestone L209「关闭≠取消，未处理 Diff 保持待处理」，不视为缺陷；
- ProfilesPage 无组件测试（前端回归主要依赖 `profileBindings.test.js` API-client 测试 + 后端 17 service + 11 route + 4 store 测试）——记为已知缺口，后续评估补测；
- 窗口编辑写回（Agent update_profile 写回名称/分组/代理）、标签展示/搜索、历史同步记录独立查询 → 后续 CHG，不属于窗口收口范围。

## 收口结论

窗口收口的**工程实现与自动/API 验证已全部完成**，真实 BitBrowser 窗口创建/读回/开/关、Diff 接受方向、停用、批量开/关控制流均 PASS，打包 Desktop 登录链路可用，`m2b-local-acceptance.sh all` + `verify` 保持 PASS。

**尚待用户 GUI 确认**的 4 项（A3/A4/A2/Agent 状态页）为纯验收动作，功能均已实现。用户确认回填后，本矩阵全部 PASS，窗口收口判定 DONE，作为社媒账号收口与后续里程碑的依赖环境。若 GUI 验收发现真实读取/读回不一致，应创建窗口修复 CHG。
