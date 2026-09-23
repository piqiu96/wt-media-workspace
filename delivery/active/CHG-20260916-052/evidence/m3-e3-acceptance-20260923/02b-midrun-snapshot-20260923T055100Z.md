# （说明）本文件是 2026-09-23 05:51 重跑 G1 时落下的中途快照，非首轮冻结基线。
# 首轮冻结基线见 02-baseline-snapshot.md（重建版）。

# M3 验收基线快照 2026-09-22T21:51:00Z

既有数据必须在验收结束后逐项一致：

```json
{
  "captured_at": "2026-09-22T21:51:00Z",
  "tables": 26,
  "discovery_strategies": {
    "count": 17,
    "max_id": 18
  },
  "crawl_tasks": {
    "count": 41,
    "max_id": 63,
    "pending": 0
  },
  "source_contents": {
    "count": 319,
    "max_id": 434
  },
  "materials": {
    "count": 87,
    "max_id": 87
  },
  "users": 3,
  "operation_teams": 12
}
```

## crawl_tasks 全量
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
34	NULL	2	failed	manual_discovery_task	NULL	2026-09-23 05:18:14.236507
35	NULL	2	success	manual_discovery_task	NULL	2026-09-23 05:25:33.537200
36	NULL	2	success	manual_discovery_task	NULL	2026-09-23 05:25:38.649507
37	NULL	2	success	manual_discovery_task	NULL	2026-09-23 05:25:43.732134
38	NULL	2	success	manual_discovery_task	NULL	2026-09-23 05:25:48.806095
39	NULL	2	success	manual_discovery_task	NULL	2026-09-23 05:26:38.450844
40	NULL	2	success	manual_discovery_task	NULL	2026-09-23 05:26:43.608674
41	NULL	2	success	manual_discovery_task	NULL	2026-09-23 05:26:48.703161
42	NULL	2	success	manual_discovery_task	NULL	2026-09-23 05:26:53.783048
43	NULL	2	success	manual_discovery_task	NULL	2026-09-23 05:26:58.867688
44	NULL	2	success	manual_discovery_task	NULL	2026-09-23 05:27:03.948863
45	NULL	2	success	manual_discovery_task	NULL	2026-09-23 05:27:09.035172
46	NULL	2	success	manual_discovery_task	NULL	2026-09-23 05:27:14.126249
47	NULL	2	success	manual_discovery_task	NULL	2026-09-23 05:28:06.929635
48	NULL	2	success	manual_discovery_task	NULL	2026-09-23 05:28:12.040695
49	10	2	success	discovery_task	interval:5:5967043	2026-09-23 05:38:17.961113
50	4	2	success	discovery_task	NULL	2026-09-23 05:38:28.204325
51	4	2	success	discovery_task	NULL	2026-09-23 05:38:28.208473
52	11	3	success	discovery_task	NULL	2026-09-23 05:39:18.761659
53	12	4	success	discovery_task	NULL	2026-09-23 05:39:48.351419
54	13	5	success	discovery_task	NULL	2026-09-23 05:39:56.436990
55	14	6	success	discovery_task	NULL	2026-09-23 05:40:00.518339
56	15	7	success	discovery_task	NULL	2026-09-23 05:40:04.583268
57	16	8	success	discovery_task	NULL	2026-09-23 05:40:12.661761
58	17	9	success	discovery_task	NULL	2026-09-23 05:40:20.739076
59	18	10	success	discovery_task	NULL	2026-09-23 05:40:28.809725
60	NULL	11	failed	manual_discovery_task	NULL	2026-09-23 05:40:58.438502
61	NULL	11	failed	manual_discovery_task	NULL	2026-09-23 05:41:08.472019
62	NULL	11	partial_success	manual_discovery_task	NULL	2026-09-23 05:41:13.495158
63	NULL	11	failed	retry_failed_task	NULL	2026-09-23 05:41:18.523777
```

## discovery_strategies 全量
```
1	1	王者荣耀热点	keyword	enabled	manual	sjz
2	1	三角洲热点	keyword	enabled	daily 09:00	sjz
3	1	自动素材验证-0921	keyword	enabled	manual	sjz
4	2	m3acc0923-合法-keyword-手动	keyword	disabled	manual	other
5	2	m3acc0923-author枚举保留	author	disabled	manual	other
7	2	m3acc0923-schedule无校验	keyword	disabled	garbage	other
8	2	m3acc0923-隔离组策略	keyword	disabled	manual	other
9	2	m3acc0923-周期触发-daily 05:33	keyword	enabled	daily 05:33	other
10	2	m3acc0923-周期调度-interval5	keyword	enabled	interval:5	other
11	3	m3acc0923-自动转素材探测	keyword	enabled	manual	other
12	4	m3acc0923-自动转素材探测	keyword	enabled	manual	other
13	5	m3acc0923-转素材-关闭	keyword	enabled	manual	other
14	6	m3acc0923-转素材-AND命中与未命中	keyword	enabled	manual	other
15	7	m3acc0923-转素材-OR非正阈值被跳过	keyword	enabled	manual	other
16	8	m3acc0923-转素材-AND单正阈值	keyword	enabled	manual	other
17	9	m3acc0923-转素材-OR不可达阈值	keyword	enabled	manual	other
18	10	m3acc0923-转素材-无关条件不参与	keyword	enabled	manual	other
```

## source_contents 按状态
```
material_created	87
pending	231
ignored	1
```
