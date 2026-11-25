# CHG109 技术交付与主线核实

## 已验证源码及运行仓主线

2026-11-25，以下PR最终head的CI均实际显示All checks have passed，独立代码审查/限定复验无未关闭P1/P2；以merge commit合入。SSH fetch后先检查工作树clean、tested为origin/main祖先、git diff --exit-code tested origin/main无差异，再切本地main并ff-only，最后删除已包含的本地CHG分支。

| 仓库 | PR | 已验证source | 实际main merge |
| --- | --- | --- | --- |
| Cloud | https://github.com/piqiu96/wt-media-cloud/pull/52 | d853e24b0a4a9305ae780fc2a69341966af48022 | 6b9fdee7affd2741fb09083b7c1f37356b67ca4d |
| Agent | https://github.com/piqiu96/wt-media-agent/pull/20 | 81f6bf8c67b3f78eaa65b3282ac31eab69564cb9 | 8147f2fbcd017583488f0296bbc086b5eef94eb9 |
| Desktop | https://github.com/piqiu96/wt-media-desktop/pull/19 | 2e06487946c1384a080680f40df003bb4e4baf7a | 0764ec2ed73c117d54986a14ca61007cff704fb5 |

三仓命令均exit0，本地branch=main、clean=true、实际tree与对应tested完全一致。测试、安装包及真实结果的source仍保留原值，不以merge SHA冒充执行时source。正式实际运行安装包frontend=0.1.0+d853e24，代码tree与Cloud main一致。

## Workspace自身归档

Workspace PR65：https://github.com/piqiu96/wt-media-workspace/pull/65 。本记录与DONE/移出LEDGER/技术归档随该PR合入main一并生效；自身最终merge SHA由Git与PR记录权威提供，不能提前伪造自身哈希。PR包含的最终收口commit独立审查/治理检查通过后才合入，本地main随后以ff-only及精确tree核实；最终命令结果在本次执行工具记录中可追溯。

## 验证与例外

G1实现/隔离测试、G2真实AI及本人两批自动衔接公开/结束、G3最后Web/macOS安装版原型走查均PASS，详情分别见implementation-selftest-checklist.md、real-e2e.json、ui-walkthrough.md和final-acceptance-matrix.md。正式wt chg verify执行exit0；后续UI增量、隔离组合、最终1237全Web及实际最终all挂载另有对应source证据。

Cloud/Agent自动Codex review受用量上限未完成（重试后仍受限），不是code finding，不记bot通过；未改额度或权限，以已记录独立代码审查及实际复验完成review。Desktop自动Review Completed。首轮环境BitBrowser超时及root并发打包造成的既有测试超时均如实记录，修复/独立串行最终结果不覆盖初次失败。

用户107–109整体最终人工验收另行；Milestone保持VERIFYING。真实仅1个本人百度Profile，N5按现有Profile实际1；多Profile/复杂异常/多角色为受控验证，Windows及其他平台未实机验收。未增加计划内补量或执行后配置修改。最终Cloud仍plan1、4batch；计划1目标2/公开2/缺口0，原task13/14、attempt36/37、work6/7均唯一，没有重复发稿。
