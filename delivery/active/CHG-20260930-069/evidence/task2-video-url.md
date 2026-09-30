# Task 2 证据：稳定对象 URL 详情链接接口

- 日期：2026-09-30
- 范围：`wt-media-cloud` storage 边界、production service/handler/router、OpenAPI 与 Business Schema。

## 测试先行（红）

- 命令：`go test ./internal/infra/storage/... ./internal/modules/production/... ./internal/bootstrap/...`
- 预期：storage / production / service 编译失败（缺 `PublicURL`/`publicBaseOf`/`VideoURL`/`VideoLink`）；bootstrap 路由测试失败（新路由未注册）。
- 实际：四个包按预期 `[build failed]` / `FAIL: TestRegisterModuleRoutesReachesEveryModule`。
- 状态：PASS（失败形态正确）

## 实现后（绿）

- 命令：同上。
- 实际：storage、production、production/service、bootstrap 全部 `ok`。
- 命令：`go build ./... && go test ./...`
- 实际：全仓测试 0 失败。
- 状态：PASS

## 实现要点（对照 change.md §2）

- `infra/storage.PublicURL(key)`：由现有 endpoint/bucket/prefix/use_ssl 组合路径式稳定地址；`validateKey` 拒绝越界 key；无凭据也可组合（地址不是机密）；`Initialize` 两分支均发布 `publicBase`，`Close` 回收，未初始化即 panic。
- production service 经 `ObjectLinker`（consumer-side 接口，store_adapter 落地）注入；`VideoURL` 顺序：范围（403/404）→ 就绪（未 ready 一律 409 `material_unavailable`）→ `videoFacts` 完整性 → 组合。
- 新路由 `GET /api/v1/materials/:material_id/video-url`，handler 复用 `writeProductionError` 映射，无新 errcode。
- OpenAPI 新增该路径（版本 `2026.09.30.1`）；Business Schema 新增 `MaterialVideoLink`（required [url]），Material `forbidden_properties` 增 `video_url`；wire_test 钉住 body 键集。

## 边界确认

- 未动 Local Agent、任务记录、桶 ACL、presign 行为；素材列表与素材 body 不携带云端视频 URL（wire_test 禁携断言 + schema forbidden）。

## 相关提交

- `feat(chg-069): 详情链接接口返回稳定对象 URL（storage 组合 + service/handler + 契约）`
