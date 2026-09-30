# Task 3 证据：两列表行形状与共用详情抽屉

- 日期：2026-09-30
- 范围：`wt-media-cloud` web 素材模块（两个列表页、共用详情抽屉、MaterialCover 组件）与 materials API client。

## 测试先行（红）

- 命令：`npx vitest run src/modules/materials src/shared/api/materials.test.js`
- 预期：封面/ID 列断言、抽屉链接断言、getVideoUrl client 断言失败。
- 实际：4 条用例失败（6 文件红），失败点均为尚未实现的目标形态。
- 状态：PASS（失败形态正确）

## 实现后（绿）

- 命令：`npx vitest run src/modules/materials src/shared/api/materials.test.js`
- 实际：7 个测试文件 36 条用例全部通过。
- 状态：PASS

## 全量 Web 测试

- 命令：`npx vitest run`
- 实际：43 文件中 42 通过、321/322 用例通过；唯一失败 `src/localSettingsWiring.test.js`（"names a component file that exists, for every desktop route"：`loaders.length` 20，断言 >20）。
- 判定：**与本 CHG 无关的既有失败**。该测试读取 `web/src/apps/desktop/router.ts`，而本 CHG 未改路由；失败由工作区改动前已存在的脏改动造成（TasksPage 删除与路由调整，change.md §6 声明「保持原样」）。已用 `git diff src/apps/desktop/router.ts` 核实。
- 状态：CHG 范围内 PASS；范围外失败留待其归属的改动处理。

## 实现要点（对照 change.md §2/§4）

- 两列表列：封面（72px，MaterialCover 缩略图）、素材 ID（90px）、标题、来源平台、游戏、视频状态、入库/加入时间、操作；行内不再有作者、`source_url` 链接、体积列与发布时间。
- MaterialCover：无 `cover_url` 或 `<img>` `@error` 时显示「无封面」占位；换 url 重置失败标记。
- 详情抽屉：新增封面、作者（有 `author_home_url` 时为链接）、平台原视频页（`source_url`）、体积（formatBytes）；云端视频地址在 `video_status === 'ready'` 时调 `GET /materials/:id/video-url` 取一次，未就绪显示「视频未就绪」，取不到不打断详情。
- materials client 新增 `getVideoUrl`，路径钉在 client 测试里。

## 相关提交

- `feat(chg-069): 两列表以封面与素材 ID 识别，链接与体积移入共用详情抽屉`
