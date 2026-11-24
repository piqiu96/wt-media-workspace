# 发布执行缓存清理验证

2026-11-24；CHG106 Task 3用户确认补充。原开发提交 `6d27ca5`；从最新远端main整理后，PR提交为 `77f1e30`（代码树一致），CHG和M6保持进行中。

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

测试使用真实临时目录和SQLite，确有文件删除/保留和持久状态回读；Cloud、浏览器及平台回执为受控替身，不是新的真实投稿或平台成功证据。兼容分支在macOS上强制无dir_fd运行，未冒充Windows原生实测。实现验证阶段未清理运营电脑的实际缓存；安装包更新的实测见下节。未关闭CHG/M6或自动合并其他在途修改。


## 安装包更新与PR（2026-11-24）

用户明确要求“更新安装包，并且提交pr”后执行。Agent从origin/main整理为`codex/chg106-publication-cache`，只含一个提交、7个文件；与原已验证开发提交代码树一致。最终分支重新运行上述167项测试，全通过（7.542秒），diff检查通过。

Agent PR：[CHG106：自动清理已确认投稿的本地缓存 #17](https://github.com/piqiu96/wt-media-agent/pull/17)。未自动合并。

| 操作 | 预期与实际 | 结果 |
|---|---|---|
| Desktop `python3 scripts/build-desktop-environment.py --environment dev --profile debug --bundles app,dmg` | 重新冻结Agent、构建前端/app、签名收尾并生成新DMG；退出0，镜像校验通过 | PASS |
| Desktop `python3 scripts/build-desktop-environment.py --environment prod --profile release --bundles app,dmg` | 正式身份release包生成并完成相同校验；退出0 | PASS |
| 只读挂载两个DMG | 环境分别dev/prod，签名及release-versions资源记录通过，镜像内Agent与构建app摘要一致 | PASS |
| 从包内提取PyInstaller模块并逐层比较字节码/常量 | publication_cache、publication_job、storage.publication与最终源码一致；两个包均通过 | PASS |
| 两个包内Agent以临时数据根/端口/运行令牌启动，run_runner=false | 开发包5.04秒、正式包2.83秒内healthz/status均HTTP200；正常关闭，不执行任务 | PASS |
| 更新当前使用的开发app | 更新前只读检查Dev数据库无执行检查点；停止旧进程，保留旧app备份，替换原位置，包内SHA匹配；启动后正确显示起飞Dev登录页 | PASS |

交付路径：当前既有`Documents/Codex/2026-11-23/sqlite-test-release-2-logo-3/outputs/`中的“起飞 Dev.app”已替换，同目录更新“起飞 Dev_0.1.0_aarch64.dmg”和“起飞_0.1.0_aarch64.dmg”。旧app保存在同目录`.previous-20261124-153313`后缀路径，未移除用户数据。

镜像SHA256：

- Dev：`09ea6eb6e5b45c6341262545b13f216d2164b0d8cbb048c001a44ecbbfebfc05`；82,534,924字节；包内Agent `50fdceb56d219ec26d16e6845aaa8b34d7ef9af1c265dda9bf4421920fba5052`。
- prod：`b2ee0b09ddb720707b9d7200a8839740b12f23cc13634d74104d071d4524e11d`；73,113,331字节；包内Agent `5911a789d134898e491a6be9b98377bc9cc5c66e78d456b6e9c6b6c1c23b147d`。

两个安装包取当前Cloud前端工作区构建，版本记录如实为`0.1.0+313aa57.dirty`，包含此前已确认的前端调整。本次PR只承接缓存清理，不提交Cloud已有其他修改；此处是本地重建包，不是已发布的正式产品Tag。Windows/Intel构建、线上更新渠道和真实发布后删除均未执行。

GUI登录时Cloud提示operator01已有桌面会话；“继续登录”会使另一台电脑退出。自动审批拒绝接管，未绕过，账号密码未写入证据或PR；已向用户请求明确接管授权。此项不影响安装包、签名或包内Agent独立启动验证，不将登录待确认写成通过。
