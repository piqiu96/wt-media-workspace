# CHG108 旧核验安全切换

2026-11-25，本地固定数据库 `wt_media_cloud`。依据 migration117 README 与 ADR-0037 执行，未以超时或旧代次代替关闭证明。

1. 只读旧 task：3/7/8/10/11 存在核验代次，关联原 browser_profile 37，实际 BitBrowser Profile `dadb60405c354150a42811540654814f`。没有活跃 running/awaiting_human；旧 interrupted 均为历史 finished 阶段，未直接更改任务或 attempt。
2. 执行 `python3 scripts/dev/local_env.py stop`，日志 `/tmp/chg108-legacy-stop.log`。Desktop 已先关闭；旧 Agent41530、Cloud37519/37539、worker37598、compose-worker37630、scheduler37671、开发服务37754/37812退出。8188/8765 无监听，后续 `ps` 原 PID 查询无结果。
3. 使用正式 `BitBrowserClient.is_profile_closed` 只读 `/browser/ports`，实际原 Profile 返回 `true`。未读取 Cookie、未开窗、未通过业务改写把旧未知强制当成功。
4. 统一 `all --force-restart` 按最终源码执行实际 migration117，查询 `publication_admission_cutover` 为 `id=1, legacy_check_count=5, verified_at=NULL`；实际活跃 Profile holder 数为0。证明门禁没有因迁移完成自动开放。
5. 迁移后再次查询原 Profile 仍 `closed=true`，原旧 PID 仍不存在。只有这些实际核实成立后，才可按 README 执行以本证据为引用的单行 verified 更新。实际更新后读回：legacy_check_count=5，verified_at=2026-11-24 20:03:40.261007（DB UTC），verification_reference 为本文件的停止旧进程/实际闭窗核实引用。门禁开放 PASS。

本证据只涉及本地升级安全；新安装包、真实批次启动和公开结果仍另行验收。
