# ADR-0024：平台标识与展示文案的归属

- Status: Accepted
- Date: 2026-10-27
- Scope: 内容挖掘、社媒账号、账户开户、素材库与内容生产中的平台字段

## Context

内容池列表曾直接渲染存储值 `douyin`，素材库、素材详情、社媒账号、开户与游戏关联详情各自维护一份平台中文名映射，同一平台在不同页面显示为“哔哩”“B站”“百家号”“百度”。用户要求全系统平台展示统一，并询问展示文案应由后端还是前端统一。

平台事实同时跨 Cloud、Agent 与 Desktop Web 三处：Cloud 存平台代码并校验枚举，Agent 按平台选择登录校验与身份读取，Desktop 与 Cloud Web 共用同一份 Vue 源码。任意一处各自维护中文名，都会在新增平台或改名时重新分叉。

## Decision

1. **代码即标识，文案在客户端。** 数据库、OpenAPI、业务 Schema/Enum 与 Agent 任务只存稳定英文代码；中文展示文案由前端公共常量 `wt-media-cloud/web/src/shared/utils/platforms.js` 持有。理由是展示是客户端职责，Cloud Web 与 Desktop 共用同一份源码，一处修改全端生效；把中文写进 API 会让第二套客户端、导出和通知各自复制一份。
2. **平台代码集。** `douyin`、`bilibili`、`xhs`、`baidu`。`xhs` 取代外部常见的 `xiaohongshu`，`baidu` 取代此前的 `baijiahao`：代码按平台命名，不按该平台下的某个产品命名。`xhs` 目前没有采集与发布能力，只作为命名与常量占位。
3. **能力范围。** 挖掘与内容池只接抖音（`douyin`）；社媒账号只接 B站与百度（`bilibili`、`baidu`）；账户开户三平台都可导入。页面筛选与表单只列当前能力支持的平台，不显示“待接入”的伪选项。
4. **未知代码的处理。** `platformLabel` 对未知代码回退到调用方给出的文案或 `-`，不把原始代码直接渲染到页面。新增平台必须同时增加代码、中文标签与能力集，缺一不算完成。
5. **重命名是一次有意的 breaking 变更。** Cloud、Agent、Desktop 必须同批发布：Cloud 与 migration `20261027_076` 先上线（CHECK 约束换枚举并把历史 `baijiahao` 改写为 `baidu`），Agent 随后只接受 `douyin/bilibili/baidu`，Desktop 最后更新 `contracts.lock.json` 到 `local_agent_api v1@2026.10.27.1`。新旧版本混跑不被支持：新 Cloud 会拒绝旧 Agent 发来的 `baijiahao`。
6. **回滚。** 回滚需要先恢复旧 CHECK、执行反向 UPDATE（`baidu` → `baijiahao`），再一起部署旧 Cloud 与旧 Agent；只回退其中一个组件会留下无法互相识别的平台代码。发布登记见 `config/release-matrix.yaml` 的 `platform-identifier-rename-20261027`。

## Consequences

- Positive：平台展示只改一处；后端与合同保持稳定的英文标识；页面不再泄露存储代码。
- Positive：Agent 与 Cloud 使用同一套代码，登录校验按平台分派不再有别名分支。
- Negative：`baijiahao` → `baidu` 是破坏性枚举变更，三个组件必须同批发布，回滚也需要一次反向数据迁移。
- Negative：`xhs` 与 `baidu` 之外的平台若在外部数据中出现（例如历史 `xiaohongshu`），本决定不负责改写，需另开 CHG 处理数据。
- Follow-up：新增平台时同时更新 `platforms.js`、Cloud 的 `validPlatform`/CHECK、Agent 的登录 URL 与身份识别，以及四份合同。
