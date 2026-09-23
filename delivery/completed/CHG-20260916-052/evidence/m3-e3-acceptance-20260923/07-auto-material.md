# 阶段 7：自动转素材规则矩阵

> 由 `tools/render-evidence.py` 从 `run-manifest.json` 渲染，每一步可回溯。
> 判定分布：PASS=8。

| 步骤 | 判定 | 请求 | 期望 | 实际 |
| --- | --- | --- | --- | --- |
| 7.0 | PASS | 策略 config={"auto_material": false, "keyword": "王者荣耀"} -> 任务 76 | 落库统计 = 库内素材行数 = 逐条谓词复算； | stats={"scanned": 20, "found": 20, "added": 20, "duplicate": 0, "failed": 0, "auto_materialized": 0, "pending": 20} 库内素材行=0 逐条谓词比对=全部一致 |
| 7.0.1 | PASS | 从真实 like_count 选定阈值 | 选一个能同时产生命中与未命中的阈值 | like 分布=[3, 4, 6, 22, 39, 97, 107, 449, 465, 569, 658, 854, 1099, 2612, 7360, 8620, 9933, 23499, 110192, 186399]，取中位数=658 |
| 7.1 | PASS | 策略 config={"auto_material": false, "material_rule": "AND", "like_threshold": 0, "favorite_threshold": 0, "keyword": "王者荣耀"} -> 任务 77 | 落库统计 = 库内素材行数 = 逐条谓词复算； | stats={"scanned": 20, "found": 20, "added": 20, "duplicate": 0, "failed": 0, "auto_materialized": 0, "pending": 20} 库内素材行=0 逐条谓词比对=全部一致 |
| 7.2 | PASS | 策略 config={"auto_material": true, "material_rule": "AND", "like_threshold": 658, "favorite_threshold": 0, "keyword": "王者荣耀"} -> 任务 78 | 落库统计 = 库内素材行数 = 逐条谓词复算； | stats={"scanned": 20, "found": 20, "added": 20, "duplicate": 0, "failed": 0, "auto_materialized": 12, "pending": 8} 库内素材行=12 逐条谓词比对=全部一致 |
| 7.3 | PASS | 策略 config={"auto_material": true, "material_rule": "OR", "like_threshold": 0, "favorite_threshold": 2000000000, "keyword": "王者荣耀"} -> 任务 79 | 落库统计 = 库内素材行数 = 逐条谓词复算； | stats={"scanned": 20, "found": 20, "added": 20, "duplicate": 0, "failed": 0, "auto_materialized": 0, "pending": 20} 库内素材行=0 逐条谓词比对=全部一致 |
| 7.4 | PASS | 策略 config={"auto_material": true, "material_rule": "AND", "like_threshold": 0, "favorite_threshold": 1, "keyword": "王者荣耀"} -> 任务 80 | 落库统计 = 库内素材行数 = 逐条谓词复算； | stats={"scanned": 20, "found": 20, "added": 20, "duplicate": 0, "failed": 0, "auto_materialized": 17, "pending": 3} 库内素材行=17 逐条谓词比对=全部一致 |
| 7.5 | PASS | 策略 config={"auto_material": true, "material_rule": "OR", "like_threshold": 2000000000, "favorite_threshold": 1, "keyword": "王者荣耀"} -> 任务 81 | 落库统计 = 库内素材行数 = 逐条谓词复算； | stats={"scanned": 20, "found": 20, "added": 20, "duplicate": 0, "failed": 0, "auto_materialized": 17, "pending": 3} 库内素材行=17 逐条谓词比对=全部一致 |
| 7.6 | PASS | 策略 config={"auto_material": true, "material_rule": "AND", "like_threshold": 658, "favorite_threshold": 0, "published_within_days": 1, "min_duration": 99999, "keyword": "王者荣耀"} -> 任务 82 | 落库统计 = 库内素材行数 = 逐条谓词复算； | stats={"scanned": 20, "found": 20, "added": 20, "duplicate": 0, "failed": 0, "auto_materialized": 12, "pending": 8} 库内素材行=12 逐条谓词比对=全部一致 |
