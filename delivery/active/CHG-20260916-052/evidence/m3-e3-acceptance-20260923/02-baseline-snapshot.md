# M3 验收基线快照 2026-09-22T21:14:30Z

> 本文件于 2026-09-23 由冻结的 max_id 重建：重跑 G1 时原文件被中途快照覆盖，
> 但基线区间内的行从未被删改（见 run-manifest 11.3.* 与 02-baseline-snapshot.sql.txt，
> 后者是 05:11 落的原件、未被覆盖）。下列各行均取 `id <= 冻结 max_id`。

既有数据必须在验收结束后逐项一致：

```json
{
  "captured_at": "2026-09-22T21:14:30Z",
  "tables": 26,
  "discovery_strategies": {
    "count": 3,
    "max_id": 3
  },
  "crawl_tasks": {
    "count": 11,
    "max_id": 33,
    "pending": 1
  },
  "source_contents": {
    "count": 109,
    "max_id": 165
  },
  "materials": {
    "count": 26,
    "max_id": 26
  },
  "users": 3,
  "operation_teams": 1
}
```

## crawl_tasks 全量（id<=33）
```
15	2	1	success	discovery_task	NULL	2026-09-16 13:54:05.334898
16	2	1	success	discovery_task	NULL	2026-09-17 01:00:40.588433
17	2	1	success	discovery_task	NULL	2026-09-19 01:00:52.190491
18	2	1	success	discovery_task	NULL	2026-09-19 12:24:44.548857
20	NULL	1	success	manual_discovery_task	NULL	2026-09-19 21:03:15.834380
21	NULL	1	success	manual_discovery_task	NULL	2026-09-19 21:06:22.078976
22	2	1	success	discovery_task	NULL	2026-09-19 21:25:11.930097
23	3	1	success	discovery_task	NULL	2026-09-21 23:06:55.802984
27	NULL	1	partial_success	manual_discovery_task	NULL	2026-09-22 10:37:03.495676
29	3	1	success	discovery_task	NULL	2026-09-22 10:43:49.278834
33	3	1	success	discovery_task	NULL	2026-09-22 22:20:03.330367
```

## discovery_strategies 全量（id<=3）
```
1	1	王者荣耀热点	keyword	enabled	manual	sjz
2	1	三角洲热点	keyword	enabled	daily 09:00	sjz
3	1	自动素材验证-0921	keyword	enabled	manual	sjz
```

## source_contents 按状态（id<=165）
```
pending	83
material_created	26
```
