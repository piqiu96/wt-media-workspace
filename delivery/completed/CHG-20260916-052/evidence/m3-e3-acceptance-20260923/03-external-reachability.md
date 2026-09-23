# 阶段 G4：外部可达性决策

> 由 `tools/render-evidence.py` 从 `run-manifest.json` 渲染，每一步可回溯。
> 判定分布：PASS=3。

| 步骤 | 判定 | 请求 | 期望 | 实际 |
| --- | --- | --- | --- | --- |
| G4.1 | PASS | POST /content-pool/search keyword=王者荣耀 limit=3 | 真实上游可达则 REAL-OK；不可达则 EXTERNAL-BLOCKED（不得用 mock 顶替） | branch=REAL-OK items=3 errcode=0 message=success |
| G4.2 | PASS | 搜索前后 source_contents 计数 | 搜索零写入 | before=319 after=319 |
| G4.3 | PASS | 取真实样本（入池与阈值依据） | 拿到真实 like/favorite 分布 | [{"platform_content_id": "7688456561111231914", "like_count": 24, "favorite_count": 5}, {"platform_content_id": "7688444829000691685", "like_count": 743, "favorite_count": 38}, {"platform_content_id": "7688444060881165550", "like_count": 481, "favorite_count": 43}] |

## 备注

- **G4.1**：搜索为同步只读，不应写入 source_contents
