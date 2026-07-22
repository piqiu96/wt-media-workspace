# Dirty runtime ownership evidence

> 日期：2026-07-23  
> 范围：进入 Task 2 前处理 `wt-media-agent` / `wt-media-desktop` 未提交改动归属

## 1. 背景

Task 1 Start Gate 发现 `wt-media-agent` 与 `wt-media-desktop` 存在未提交 runtime 改动，且命中后续 Desktop / Local Agent 路径相关文件。

经复核，这批改动属于 M2-A 本地环境状态投影尾项，不属于 CHG-20260723-025 的 M2-B1 扫描与 Diff 只读闭环。

## 2. 处理结果

| 仓库 | 处理方式 | 提交 |
|---|---|---|
| `wt-media-agent` | 作为 M2-A 本地 Agent 环境状态投影收口提交 | `8eb5a82 Complete local agent environment status projection` |
| `wt-media-desktop` | 作为 M2-A Desktop 环境状态字段暴露收口提交 | `51c7ce3 Expose local agent environment status fields` |

## 3. 验证

### Agent

命令：

```text
python3 -m unittest tests/test_app.py tests/test_local_profile_scan.py
```

结果：PASS，8 tests。

### Desktop

命令：

```text
cargo check
```

结果：PASS。存在既有 warning，不阻断本次归属处理。

## 4. 结论

进入 Task 2 时，`wt-media-agent` 和 `wt-media-desktop` 的 M2-A 遗留 runtime 改动已独立提交，不再阻塞 CHG-20260723-025。

本 CHG 后续 runtime 改动必须重新按 M2-B1 范围产生，不得混入 M2-A 尾项。
