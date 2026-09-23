# M3 Cloud-owned 内容挖掘纠偏设计

> 2026-09-23 注：本文为 2026-09-16 的设计稿，其中博主搜索、自动转素材、任务状态等表述已被 docs/product/M3-content-mining-v2.md 与 ADR-0013/0015 取代；保留原文以存史。

## 已确认目标

M3 只交付“内容自动发现 → 内容池 → 人工转素材”的最小闭环，包含内容池、挖掘策略、挖掘任务三个页面。链接导入直接入池；关键词/博主搜索先保存查询结果，运营选择后入池；所有入口都不自动创建素材。（2026-09-23 注：博主搜索已暂停且服务端硬禁用，不在本期范围，`author` 枚举取值保留；「所有入口都不自动创建素材」已被取代——本期按 `auto_material` / `material_rule` / `like_threshold` / `favorite_threshold` 条件化自动转素材，仅命中项入池后自动生成 `material`，未命中项留在内容池待人工处理。）

## 运行边界

M3 不使用 Cloud Agent、Local Agent、Desktop、BitBrowser、工作流引擎、MQ 或可视化调度器。Cloud Scheduler 扫描到期策略并调用 Cloud-owned `Crawler`；Crawler 通过服务端环境变量访问渠道接口，DiscoveryService 持有 `crawl_task`、`source_content` 和统计事实。M2 的浏览器、文件、FFmpeg、发布和互动执行边界不变。（2026-09-23 注：Cloud 运行时只读 `config/` 下的 TOML 凭据，如 `config/credentials/douyin.toml`，全仓零 `os.Getenv`，`WT_MEDIA_DOUYIN_*` 环境变量与 `.env.local` 对 Cloud 运行时无效；Scheduler 与 Worker 为独立 CMD 进程 `cmd/discovery-scheduler` / `cmd/discovery-worker`。）

## 组件与数据流

```text
discovery_strategy
        ↓ Cloud Scheduler
     crawl_task
        ↓ Crawler
  source_content
        ↓ 人工转素材
      material
```

`Crawler` 以 `(platform, operation, config)` 为输入，当前只实现 `douyin`；未来渠道通过同一接口增加适配器，不改变内容池/策略/任务模型。查询凭据不能进入请求体、日志、Web 或数据库快照。

## 状态与失败

`crawl_task` 使用 `pending/running/success/partial_success/failed`（2026-09-23 注：原设计为四态，实际实现为五态，新增 `partial_success`，判定为 `processed = added + duplicate + pending + auto_materialized` 且 `failed > 0` 时 `processed > 0`）；部分成功保留已发现/已入池结果并增加失败计数，全部失败为 `failed`。重复来源由内容池唯一键与幂等入池处理；搜索未选结果不写正式来源。

## 验证

Cloud 单元测试验证接口映射、凭据边界、批量部分失败、策略执行与团队权限；Cloud/Web 全量测试和构建必须通过。真实 Douyin 验收仅在 Cloud 配置合法服务端凭据与授权样本后进行，mock 只能证明契约，不替代外部读回。
