# M6 当前验证结论

日期：2026-11-20。本文合并原页面整改、安装版走查与端到端记录，只保留最终事实和未验项；旧过程数据、重复截图与调试输出移除。本节业务验证继承本日前轮记录，本次清理没有重新投稿或重跑运行仓测试。

## 源码与合并基线

| 仓库 | 已进入远端 main 的基线 | 合并入口 |
| --- | --- | --- |
| Workspace | `e757ae7fb76fafb0f23e044de89af0f022decdef` | [#52](https://github.com/piqiu96/wt-media-workspace/pull/52)、[#53](https://github.com/piqiu96/wt-media-workspace/pull/53)、[#54](https://github.com/piqiu96/wt-media-workspace/pull/54)、[#55](https://github.com/piqiu96/wt-media-workspace/pull/55)；#56 经 #55 进入 main |
| Cloud | `c58711831440dd559e1e41920226ca37037bd43c` | [#44](https://github.com/piqiu96/wt-media-cloud/pull/44)、[#45](https://github.com/piqiu96/wt-media-cloud/pull/45)、[#46](https://github.com/piqiu96/wt-media-cloud/pull/46) |
| Agent | `2c7aef0f5a59cb19142f5363807745de6218f5a7` | [#9](https://github.com/piqiu96/wt-media-agent/pull/9)～[#13](https://github.com/piqiu96/wt-media-agent/pull/13)；#12 经 #11 进入 main |
| Desktop | `f6ffe3d6a1b18ba0e26f3656b16b91ab9164039e` | [#11](https://github.com/piqiu96/wt-media-desktop/pull/11)、[#12](https://github.com/piqiu96/wt-media-desktop/pull/12)、[#13](https://github.com/piqiu96/wt-media-desktop/pull/13) |

本次联网复核四仓 open PR 均为零，上表相关 PR 已合并且代码进入 origin/main。合并后的占用投影、媒体策略、分片上传、平台封面校验、账号摘要等修复仍为本地未提交修改，不能把上述 main SHA 当成已包含全部修复的发布版本。

## 已验证与继承边界

| 范围 | 最终事实 |
| --- | --- |
| 正式任务与文件安全 | 真实资源创建/编辑、请求键防重、修订检查、同平台占用及明确文件 ID 引用保护已有验证；文件删除以 deleted_at 为准，不反查生产 URL |
| 执行安全 | 所属用户领取、真实 UID/Profile 检查、提交许可、原结果持久化与补报、安全核实后重试已有隔离数据库、SQLite、故障和真实任务证据；不承诺多 Agent 进程同时操作同一库 |
| 合并前自动检查 | Cloud 前端 1037 项、原型 351 项、示例 21 项通过；Desktop Rust 545 项通过、6 项忽略；Workspace 211 项通过。仅对应当时集成版本 |
| 本地最终封面修复 | 39 项封面、68 项执行收尾、40 项页面、101 项隔离浏览器检查通过；安装版完整重建及环境门禁通过。图片内容摘要保护保留，不以地址相同冒充内容相同 |
| 账号摘要追加修复 | 60 项相关测试、123 项宽窄屏检查及 Cloud/Desktop 构建通过；安装版实际验证本人账号摘要、选择与查看分离、打开绑定窗口成功；无新增任务或投稿 |
| 运营链路 | 内容1046 → 素材188 → 原合成任务725 → 成片132 → 发布任务8。源视频上传413已通过分片上传及原任务重试处理；安装版真实播放30秒成片通过 |
| 上游故障 | 曾复现外部发现服务入口节点健康不一致，后续本次安装版搜索与导入成功；没有证据证明供应方整体故障已根治，不通过延长超时或固定IP掩盖 |

复现入口：Cloud `go test ./internal/modules/publish/...`，隔离数据库按本仓已有 `WT_MEDIA_TEST_LIVE_DB=1` 入口；前端使用 `web/package.json` 及 `web/scripts/test-publishing-browser.mjs`、`test-publication-visual-browser.mjs`；Agent `bash scripts/test.sh` 及百度隔离浏览器测试；安装版按 Workspace `environment-bring-up` 流程。不得用自动化夹具代替真实公开作品验收。

## 真实投稿结果

| 任务 / attempt | 平台稿件回执 | 实际结论 |
| --- | --- | --- |
| 7 / 21 | `1882359387756944157` | 2026-11-20 14:56平台接收，审核中；未核实公开 |
| 8 / 27 | `1882371730190912814` | 2026-11-20 18:12平台接收，Cloud与App均审核中；work_url为空 |

任务8原结果 SHA256：`4b71e86f551093022d64e340b14a2897d7a6c162521ccfafab701c02dc2b47d0`；Cloud/Agent一致，report_seq=6、scene_closed=true、settled、delivered=1、report_pending=0。任务7原结果 SHA256：`2146f5275cf680ed554ed48febb49727b579c478a275adf9a9cdbd1abf4287a3`，同样已补报并结清。失败尝试保留在正式任务历史，不通过新任务绕开占用，不重复投稿来取得截图。

## 未完成与验收限制

- 尚无已核验公开作品链接；审核中不计公开成功。完整核实、补录、作品关联与公开成功统计待实现/验收。
- 安全终止、原现场人工介入继续、放弃与条件复制、单任务续编尚未完整交付。
- 图片库、模板与真实渲染、快速发布AI及成片缩略图现归M6，不能由演示原型或现成文件选择代验。
- 用户对完整M6的最终验收尚未完成；当前本地修复尚未提交/Review，不宣称已经进入远端main。
- 新阶段范围见[当前CHG](../change.md)及[M6](../../../milestones/M6-single-publishing.md)。
