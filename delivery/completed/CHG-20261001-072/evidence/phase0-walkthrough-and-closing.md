# CHG-072/073 阶段 0 走查修正与关闭读数（2026-10-02）

范围：072 的「样式与即时修复」批（工作台菜单隐藏、数据分析移位、移除环境检测页、顶栏工作环境胶囊、http 401、PersonalInfoPage 状态、保存按钮、登录页文案/品牌），073 的品牌与图标。

## 阶段 0 改动（wt-media-cloud `a88604c`，2026-10-02）

- 隐藏 工作台 菜单项；数据分析 移到 运营资源 下方；移除 环境检测 子菜单并删除 `AgentStatusPage.vue` 与路由（desktop router / main allowlist / cloud router 注释）。
- 顶栏 `WorkEnvPill.vue` + `work-env-status.js` 聚合（绿点=工作环境，橙点=需检查），30s 轮询、隐藏时暂停。
- `http.js` 401 重定向移到 parseResponse 之前（登录页除外），避免非 401 路径误触发。
- `PersonalInfoPage.vue`：Local Agent 行改为 可用/当前不可用（idle/running 视为可用）；移除 查看 Agent 状态 按钮；按钮文案 保存个人信息→保存。
- `LoginPage.vue`：登录页 slogan 与品牌（敢想，真干 / 下次起飞，从一个想法开始）。
- 顶栏品牌区新增版本号（共享 `shared/utils/appVersion.js`：Desktop 读 Tauri 真实版本、Web 回落 package.json），登录页同步改用同一工具。

## 走查结论（用户自报）

用户走查后确认：样式与即时修复已生效；**联动功能（阶段 1-3）未实现**，是 074 的范围，不在此处验收。

## 关闭读数（最后一次代码改动 `a88604c` 之后重跑）

| 仓 | 读数 |
| --- | --- |
| `wt-media-cloud/web` | `npx vitest run`（cwd 必须为 `web/`）**49 文件 / 448 用例通过** |
| `wt-media-cloud` | `go test -count=1 ./internal/modules/identity/... ./internal/modules/runtimebinding/... ./internal/modules/cloudagent/...` **全部 ok** |
| `wt-media-cloud/web` | `npm run build:cloud` **通过**（仅既有 chunk 体积提示） |

Desktop `.generated/frontend/` 快照与各仓 SKILL 副本的提交在归档前由用户执行（见命令清单）。

## 遗留（登记，不阻塞关闭）

- **联动功能未实现**：client_type 会话解耦、执行凭据独立 + 落盘、node 两层、下载去重 node→device、解绑重分配、DownloadCentre 重取、profilebinding 自助确认、23002/23003——全部归入 `delivery/planned/CHG-20261002-074`。
- WorkEnvPill 的「重新同步本机环境」是阶段 2 前的过渡入口，凭据持久后在 074 收尾清理。
- desktop release 打包线（`build/package/verify-release-macos.sh` 等）仍硬编码 `WT Media.app`，是否跟随「起飞」改名是产品决策，另行确认。
- agent `tests/test_runtime_config.py:411` 的 `WT Media.app` 是夹具，非 bug，不动。
