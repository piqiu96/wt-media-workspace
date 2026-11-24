# 发布执行缓存清理验证

2026-11-24；CHG106 Task 3用户确认补充。Agent独立提交 `6d27ca5`，CHG和M6保持进行中。

## 变更与审查

- 新增受限本地缓存清理，接在原结果投递/结算恢复后；启动首次扫描，随后每10分钟补扫当前用户和Cloud环境的已结束记录。
- 复用原检查点JSON保存pending/failed/complete及时间，结算前保留文件摘要；无数据库迁移、Cloud接口、平台上传/投稿行为或业务状态裁决变化。
- 删除前重查原尝试的确认、无待补报及安全结束证据。旧记录缺少明确状态时只读查询对应原尝试，严格匹配attempt和已有hash，不借用后续尝试结果。
- 仅逐文件删除指定缓存及对应临时文件，最后移除空目录；拒绝未知项、子目录、符号链接和目录联接。POSIX使用目录描述符固定范围，并验证并发替换父目录不能把删除重定向至其他目录。Windows采用逐文件删除/空目录移除分支，不递归。
- 删除错误独立记录并等待补清，不改原结果、outbox或占用，不触发平台重入。其他任务、云端原件、用户下载、Profile及持久证据保留。

## 验证记录

| 操作 | 预期 | 实测 | 结果 |
|---|---|---|---|
| 实现前：`PYTHONPATH=src:tests .venv/bin/python -m unittest test_publication_cache` | 缺少清理能力时失败 | 新测试因缺少publication_cache模块失败 | PASS（失败验证） |
| 实现后：缓存、执行日志、协调器、轮询、准备5组测试 | 安全条件满足才删除，异常可恢复 | 90项通过 | PASS |
| 最终定向回归（下列命令） | 覆盖新增删除与现有发布/接口/启动能力 | 167项通过，0失败，约8秒 | PASS |
| Agent `git diff --check` | 无空白错误 | 通过 | PASS |
| Workspace文档、Delivery及产品计划对齐校验 | 索引/相对链接/交付边界一致 | 15个文档索引通过，Delivery和产品计划对齐通过 | PASS |

最终Agent命令：

```sh
PYTHONPATH=src:tests .venv/bin/python -m unittest test_publication_cache test_publication_execution test_publication_job test_publication_loop test_publication_preparation test_publication_check_job test_publication_check_session test_publication_close test_publication_run_api test_publication_api test_publication_draft test_publication_draft_api test_bootstrap test_bootstrap_loops test_storage_migration test_storage_migration_paths
```

Workspace校验：`python3 scripts/docs/check.py`、`python3 scripts/verify/verify_delivery_governance.py`、`python3 scripts/verify/verify_product_master_alignment.py`。

关键覆盖：已确认并关闭的原尝试实际删除；未确认、未关闭、失败和活动记录保留；其他尝试和用户目录保留；删除权限错误后重启补清；已删除但完成状态未写入后恢复；旧尝试错误hash/attempt、未解现场或查询失败不清理；后续尝试成功不授权旧失败记录；链接/未知项拒绝；父目录并发替换保护；10分钟节流；当前登录身份装配；结果补报后删除失败重试，平台点击次数仍为1。

## 证据边界

测试使用真实临时目录和SQLite，确有文件删除/保留和持久状态回读；Cloud、浏览器及平台回执为受控替身，不是新的真实投稿或平台成功证据。兼容分支在macOS上强制无dir_fd运行，未冒充Windows原生实测。本轮未清理运营电脑的实际缓存、未重打安装包；安装版需包含此Agent提交后才启用新逻辑。未关闭CHG/M6或自动合并其他在途修改。
