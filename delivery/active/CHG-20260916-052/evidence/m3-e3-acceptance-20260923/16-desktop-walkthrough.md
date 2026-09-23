# 补验：Cloud Desktop 走查

- 日期：2026-09-23
- 覆盖验收项：`14-verdict.md` 第 7 项（Cloud Web / Desktop 走查）之「Desktop 走查未做」
- 首轮状态：**未做** —— 见 `13-blocked-and-adjudicated.md` 第 3.5 节
- 本轮结论：**Desktop 走查已执行**，第 7 项由「部分通过」改判**通过**

## 一、环境（走端到端启动脚本，不用手工拼装）

```
bash scripts/local-control.sh start      # = m2b-local-acceptance.sh all --force-restart
```

检查点全部 PASS（`verify_all` + `verify_login`）：

| 检查点 | 结果 |
| --- | --- |
| Cloud health（18080） | PASS |
| Agent healthz（8765） | PASS |
| BitBrowser（经 Agent） | PASS |
| Desktop assets 新鲜 | PASS |
| DMG 新鲜 | PASS（构建于 2026-09-23 14:27） |
| 登录冒烟（admin） | PASS |

DMG 挂载后 Desktop shell 以 pid 55947 运行。

## 二、方法：为什么不是「截图原生窗口」

| 尝试 | 结果 |
| --- | --- |
| `screencapture` 抓原生 Tauri 窗口 | **失败**：`could not create image from display`——本环境未授予屏幕录制权限，原生窗口无法被程序化截取 |

因此在**不改变走查对象**的前提下改用下述办法：

1. **走查对象就是打包产物本身**：静态根取 `wt-media-desktop/.generated/frontend`，
   即打进 DMG 的同一份 Tauri 前端产物。走查的不是 dev 模式前端。
2. **必须落在 5174**（两处硬编码，无法换端口）：
   - `web/src/shared/api/http.js` 的 `defaultApiBase()` 只在 `window.location.port === '5174'`
     时保留相对基址 `/api/v1`，其他端口一律改用编译期写死的 `http://127.0.0.1:18080/api/v1`；
   - `internal/middleware/cors.go` 的 CORS 白名单只放行 `tauri.localhost` 与 `127.0.0.1:5174`。
3. **工具**：`tools/desktop-walkthrough-proxy.py`——在 5174 上同时提供静态服务与 `/api` 反向代理，
   代理转发时补 `Cookie`（与既有 `tools/cookie-proxy.py` 同一手法）。
4. **点击靠注入脚本**：无头 Chrome 不能点击。做法是在静态返回的 `index.html` 的 `</body>` 前插入
   **一个** `<script src="/__walk.js">`；`__walk.js` 只在 URL 带 `#walk=<场景>` 时动作，否则立即返回。
   **应用自身产物逐字节未改**（注入发生在 HTTP 响应阶段，磁盘文件未动）。
   交互后注入 `transition:none; animation:none` 冻结动画，避免把入场动画中途定格进截图。

## 三、走查中发现的产品事实（值得单独记录）

### 3.1　Desktop 拒绝管理员与高级运营角色

用 admin 会话打开时，界面显示：

> 当前角色不能登录 Desktop，请使用 Cloud Web 管理。

这是 `LoginPage.vue` 的真实产品规则，**不是缺陷**：Desktop 只允许**运营**角色登录。
故本次走查全程以 `operator01` 进行。首轮验收未记录此限制，后续做 Desktop 走查需以此为前置。

### 3.2　任务详情抽屉是**四个**标签页，不是三个

`13-blocked-and-adjudicated.md` 第 3.5 节原先按「三个标签页（统计 / 日志 / 处理项）」描述，
与实现不符。实测为**四个**：

| 实际标签 | 截图 |
| --- | --- |
| 结果概览 | `06-task-detail.png` |
| 发现内容 | `06-task-detail-items.png` |
| 执行过程 | `06-task-detail-process.png` |
| 异常记录 | `06-task-detail-errors.png` |

第 3.5 节已据此更正。

## 四、截图清单（11 张，`screenshots/desktop/`）

| 文件 | 内容 | 字节 |
| --- | --- | --- |
| `01-content-pool.png` | 内容池主页面，统计 `125 / 91 / 34 / 0` | 165143 |
| `02-material-library.png` | 素材库页面 | 182341 |
| `03-discovery-strategies.png` | 挖掘策略列表，3 个策略及规则渲染 | 108751 |
| `04-crawl-tasks.png` | 挖掘任务列表 | 150611 |
| `05-strategy-edit-author-disabled.png` | **交互 1**：编辑挖掘策略弹窗，关键词已带出，**「作者（维护中）」为禁用态** | 157583 |
| `06-task-detail.png` | **交互 2**：任务详情抽屉「结果概览」 | 127931 |
| `06-task-detail-items.png` | 同上，「发现内容」 | 162549 |
| `06-task-detail-process.png` | 同上，「执行过程」 | 137025 |
| `06-task-detail-errors.png` | 同上，「异常记录」 | 119858 |
| `07-review-mode.png` | **交互 3**：内容审核模式，`当前 1 / 91`，页脚四个按钮可见 | 109711 |
| `08-review-mode-skip-advance.png` | **交互 3**：点「跳过」后推进到 `当前 2 / 91` | 153880 |

三项点击交互（即 `13-blocked-and-adjudicated.md` 第 3.5 节列出的全部三项）已**逐项**取得视觉证据：

1. 策略编辑弹窗中「作者（维护中）」的禁用呈现 —— 服务端硬禁用另有 5.6 的恒返
   `400 / 14006「博主搜索接口维护中」`支撑，界面呈现与之一致；
2. 任务详情抽屉的全部标签页（实测 4 个，多于原记录的 3 个）；
3. 审核模式逐条流转：「转素材并下一条 / 忽略并下一条 / 跳过 / 取消审核」四按钮可见，
   且以「跳过」证明流转**真实推进**（`1/91 → 2/91`）。

## 五、只读声明

**整个 Desktop 走查在服务端是只读的**，逐条说明：

| 动作 | 是否有服务端写入 | 依据 |
| --- | --- | --- |
| 打开内容池 / 素材库 / 策略列表 / 任务列表 | 无 | 均为 GET |
| 打开策略编辑弹窗 | **无** | 只渲染表单，未点「保存」；未发出写请求 |
| 打开任务详情抽屉与各标签页 | 无 | 均为 GET |
| 进入审核模式 | 无 | 前端本地状态切换 |
| 点「跳过」 | **无** | `ContentPoolPage.vue:351-354`：`if (action === 'skip') { advanceReview(); return }` —— 在发出任何 `client.*` 调用**之前**就返回；`advanceReview()` 只改本地索引 |

未点的按钮：「转素材并下一条」与「忽略并下一条」会真实写库（`client.materialize` /
`client.setStatus`），**本轮未触发**；「保存」同样未触发。因此走查**未产生任何新增或修改行**。

## 六、服务端交叉核对

界面读数与接口读回一致：

| 量 | 界面（截图） | 接口读回 | 一致 |
| --- | --- | --- | --- |
| 内容池总数 | 125 | `material_created 34 + pending 91 = 125` | ✓ |
| 转入素材 | 34 | `GET /content-pool?status=material_created` → 34 | ✓ |
| 待处理 | 91 | `GET /content-pool?status=pending` → 91 | ✓ |
| 已忽略 | 0 | — | ✓ |
| 审核模式进度 | `1 / 91 → 2 / 91` | 分母等于 pending 数 91 | ✓ |

（上表为走查当时的值；其后 `material_failed` 注入新增 19 条来源，池变为
`material_created 37 + pending 107 = 144`，见 `17-material-failed-injection.md` 第六节。）

## 七、覆盖范围与未覆盖

**已覆盖**：

- 四个页面（内容池 / 素材库 / 挖掘策略 / 挖掘任务）在**打包产物**上的真实渲染，真实登录态、真实数据。
- 三项点击交互的视觉证据（策略编辑禁用项、任务详情四标签页、审核模式流转推进）。
- 运营角色登录 Desktop 的完整链路；管理员/高级运营被拒的界面提示。
- 界面读数与接口读数的交叉一致。

**未覆盖**（据此**不**外推为已验证）：

1. **原生 Tauri 窗口**：因屏幕录制权限缺失，未对原生窗口取图；本轮取图对象是打进 DMG 的
   前端产物在 Chromium 中的渲染。原生外壳（窗口装饰、菜单、托盘等）**未取证**。
2. **写操作**：如上，凡会写库的按钮均未点击。Desktop 侧「转素材 / 忽略 / 保存策略」的
   端到端效果**未在 Desktop 上取证**（其服务端语义已由 9.9、5.5 等接口级证据覆盖）。
3. **审核模式其余分支**：只验了「跳过」，「转素材并下一条」与「忽略并下一条」**未验证**。
4. **异常态界面**：网络中断、权限不足、空数据等异常态下的界面呈现**未取证**。
5. **窗口尺寸/分辨率适配**：只在 `1280×800`、`device-scale-factor=1` 下取图。

## 八、残留与安全

- 走查本身**未产生服务端行**（第五节）；未新增策略、任务、来源或素材。
- **走查代理已停止、5174 已释放**（无监听），无头 Chrome 无残留进程；
  代理内存中曾持有的运营会话 cookie 随之消失。5174 上的第三方 vite（pid 3121）经用户许可停止后未重启。
- **仍在本机运行**（`scripts/local-control.sh start` 的正常产物，未做收尾）：Cloud `18080`、
  Agent `8765`、Desktop shell（DMG 挂载运行，pid 55947）。二者健康检查均为 `200`。
- Cookie 只存在于 shell 变量与代理进程内存中，**未落盘、未写入证据目录**；
  本文档与全部截图**不含任何凭据值**（无 Cookie、无 api_key）。已用真实凭据值反查整个证据目录：
  **0 命中**；按 `wt_media_session=<值>` 形态反查：**0 文件**。
- 工具脚本 `tools/desktop-walkthrough-proxy.py` 已随证据入库，便于复现；
  其文档字符串中说明的注入方式不改变被走查产物的字节，且 cookie 只从环境变量读入，不落盘、不打印。
