# Task 26 证据：video-url 改签发 presign + 前端点击时取址

- 日期：2026-10-01
- CHG：CHG-20260930-069（用户裁定：端点改签发 presign；抽屉里视频链接改成点击时取）
- 仓库：`wt-media-cloud`（一提交）
- 提交：`882258f`（`feat(production): 视频链接改签发 presign + 前端点击时取址（任务 26）`）

## 要修的是什么

诊断证据 `download-slow-diagnosis-experiment.md` 的附带发现：`GET /api/v1/materials/:id/video-url`（任务 2 落地）返回的是**无签名**的稳定对象地址（实测 `url_len=119`、`query_keys=[]`），而桶拒绝匿名读，实测 403 `Garage does not support anonymous access yet` —— 任务 2 的验收项「云端视频 URL 实际可访问性」在当前环境**不成立**。用户裁定由端点改签发 presign。

## 后端

`productionObjectLinker.PublicObjectURL`（`storage.PublicURL`，无签名、不过期）→ `PresignObjectURL(ctx, objectKey)`（`storage.PresignGet`，短时单对象 GET grant）。`ObjectLinker` 随接口改形；`Service.VideoURL` 与路由 helper `operations.VideoURL`、handler 增 `ctx` 并透传到签发方。

grant 的 `ExpiresAt` **不到达响应体**：契约的 `MaterialVideoLink` 只有 `url` 一条，抽屉改成点击时取址后没有任何持有中的地址需要过期信息。适配器的注释写明「过期信息就停在这里，和它不在契约 body 里是同一个理由：线上没人读它」。

## 前端

`MaterialDetailDrawer.vue` 去掉开抽屉时的预取、`videoUrl` ref 与「地址获取中」中间态；链接按 `video_status === 'ready'` 直接渲染，点击才取址。

**空标签页在 `await` 之前同步开出来**，`opener` 置空，拿到地址后 `location.replace`：跨过 `await` 之后浏览器不再算「用户手势」，那时才调的 `window.open` 会被拦（WebKit 一律拦，而打包的 Desktop 用的就是 WebKit）。同步 `window.open` 就被拦时**不发出**那次签名请求（没有可导航的标签页，取了也是白发一次凭证）。

## 契约

- `contracts/cloud-api/v1/content-production.openapi.yaml`：`info.version 2026.09.30.2 → 2026.10.01.1`；`summary` / `description` / `200` 改写 —— 原文写的是「it is not a presigned grant and carries no expiry」，改完就是**假话**，契约文本是本任务的核心之一，不是附注；
- `contracts/business-schemas/v1/content-production.yaml`：`MaterialVideoLink` 描述改写、`revision 2026.10.01.1 → 2026.10.01.2`；
- **不加 `expires_at` 字段**。

### 一处对计划的偏离（已登记）

计划写「同步 `config/contract-map.yaml business_schemas.schema_revision`」。**没有动**，仍是 `2026.07.14.4`。理由：`scripts/verify_m0_config.py:99-100` 把它钉成常量，任务 20 已确认那是**与业务 schema 文件 `revision` 独立的版本空间**，任务 21/23 改同类契约时同样只动前者。按计划改会同时打红校验器并覆盖一条已确认的裁定 —— 冲突回写到证据里，而不是回退实现。

## 验证（读数）

- `gofmt -l`（改动文件）空、`go build ./...` 干净、`go test -count=1 ./...` **66 包 ok / 0 FAIL**；
- 全量 `npx vitest run`（cwd = `web/`）**46 文件 / 430 用例全绿**；
- `npm run build:cloud` 与 `npm run build:desktop` 均 **rc=0**（都在 `web/` 下落跑；第一次用管道量退出码量到的是 `tail` 的，已用不带管道的方式重测）。
- 以上均在最后一次改动之后重跑。

## 变异（5 条，逐条变红后还原、还原后 sha256 逐文件一致）

| 变异 | 变红的用例 |
| --- | --- |
| 适配器回退成 `storage.PublicURL(key)` | 新增 wiring 用例：「the published address carries no signature」 |
| `VideoURL` 把 ctx 换成 `context.Background()` | 「the linker was called with a live context」 |
| 前端把窗口开在 `await` 之后 | 「opens the tab before awaiting the address」 |
| 重新加回 `videoUrl` ref | 「keeps no held address」 |
| 链接的 `v-if` 去掉（未就绪也渲染） | 「asks for the cloud video address on the click」的就绪判据 |

## 真实链路（不打印地址）

临时探针（**验证后已删除，不入库**）用**生产适配器**对真实配置签发，再发一条 Range GET，只打印状态码与字节数：

| 请求 | 期望 | 实测 |
| --- | --- | --- |
| 生产适配器签发的地址 + `Range: bytes=0-1023` | 206 | **206，`bytes 0-1023/48511909`** |
| 同一 key 的**无签名**地址（`storage.PublicURL`，即改前那条路径） | 被拒 | **403** |

对象是素材 30 的源视频（`materials/30/2afa51e6…mp4`），48511909 字节与诊断证据记录的尺寸逐字节一致。**阴性对照成立**：无签名地址今天仍 403，所以上面那条 206 确实来自签名，而不是「桶其实放开了」。

**尚未做的**：经 HTTP 路由 + 真实会话的 `curl`（要重启 Cloud 换上新编译产物、并登录拿会话）。路由的签名来源由 wiring 用例钉住，剩下的是「路由确实返回签名地址」这一步，归入 m2b 重建走查。

## 遗留（请用户另裁）

`storage.PublicURL` 改动后已无生产调用方。**本次不删**：诊断里「对象存储加 CDN」正是它的用途，且删它是本任务范围外的改动。但留一个会构造**已知 403 地址**的导出函数是个坑，是否删请用户另裁。

**后续（2026-10-01）**：用户裁定「删掉」，已落地 —— `public_url.go`、`registry.publicBase` 与 4 条相关用例删除，提交 cloud `594a99c`。本节的「本次不删」是任务 26 当时的决定，不回改。
