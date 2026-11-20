# CHG101 最终验证结论

日期：2026-11-20。仅保留最终结论；过程数据、截图与调试输出不进入归档。本轮重新验证现有四仓代码并集中合入；真实投稿证据继承前轮，没有重复投稿。未完成业务全部移交CHG106，M6仍为IN_PROGRESS。

## 提交与合入

| 仓库 | 可核验提交 | PR |
| --- | --- | --- |
| Workspace | `447b6c56e792841ff14f2e4cbe54af471eff3bcf` | [#58](https://github.com/piqiu96/wt-media-workspace/pull/58) |
| Cloud | `df5cb11da6ed2a451786e5a90598669846f463b7` | [47](https://github.com/piqiu96/wt-media-cloud/pull/47) |
| Agent | `2a3a372cfc975c8f19d1851035b1bceca8a3f638` | [14](https://github.com/piqiu96/wt-media-agent/pull/14) |
| Desktop | `61010d61adba51b2c311aacfb989d30944e7799d` | [14](https://github.com/piqiu96/wt-media-desktop/pull/14) |

Workspace指针为同一PR包含的契约/工程提交，避免归档文件引用自身最终merge SHA；完整收口及最终merge提交以#58为准。Cloud、Agent、Desktop上表为实际merge提交，均已同步本地main；Workspace在#58合并后同步。新CHG启动门禁必须确认四个指针都已进入本地main。

Cloud旧审查工作树的48项修改逐文件及暂存树核对，与Cloud提交ba984cb完全一致；已整理为该提交的干净工作树并删除旧103分支，目录保留。各PR合并后删除对应短期分支。

## 本轮验证

| 范围 | 命令或操作 | 预期与实际 |
| --- | --- | --- |
| Cloud后端、前端及控制入口 | `bash scripts/test.sh` | PASS；71个Go包、146个前端文件1062项、控制12项 |
| 正式占用与并发/故障 | `WT_MEDIA_CLOUD_HOME="$PWD" WT_MEDIA_TEST_LIVE_DB=1 go test ./internal/modules/publish/... -count=1` | PASS；仅创建/销毁隔离schema，不修改业务任务 |
| 正式页面及入口 | `test-publication-visual-browser.mjs`、`test-vite-entry-isolation-browser.mjs` | PASS；123项宽窄屏、4组Cloud/Desktop冷启动与刷新，零页面错误、零业务写入 |
| Web构建 | `npm run build:cloud`、`npm run build:desktop` | PASS；两类共用页面产物可构建 |
| Agent执行及SQLite补报 | `bash scripts/test.sh` | PASS；797项 |
| 百度隔离浏览器 | `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/browser -p test_baidu_publisher_browser.py` | PASS；31项，不连接真实投稿现场 |
| Desktop | `bash scripts/test.sh` | PASS；Rust547项、原6项忽略，控制12项、发布版本20项 |
| Workspace | `python3 -m unittest discover -s tests`；docs、Delivery、产品总计划、AI、skills、config检查及diff检查 | PASS；211项，测试夹具仅补齐真实引用文件，校验规则不变 |
| 独立Review | 四仓全部改动及Cloud13个新增文件、范围移交与夹具 | PASS；无阻断正确性或安全问题；归档后再次复核链接和状态 |
| 远端CI | Cloud#47、Agent#14、Desktop#14；Workspace#58 | 合并前全部必须通过；Cloud包含23组原型浏览器、迁移、发布构建和打包校验 |

## 真实投稿结果

| 任务 / attempt | 平台稿件回执 | 实际结论 |
| --- | --- | --- |
| 7 / 21 | `1882359387756944157` | 2026-11-20 14:56平台接收，审核中；未核实公开 |
| 8 / 27 | `1882371730190912814` | 2026-11-20 18:12平台接收，Cloud与App均审核中；work_url为空 |

任务8原结果 SHA256：`4b71e86f551093022d64e340b14a2897d7a6c162521ccfafab701c02dc2b47d0`；Cloud/Agent一致，report_seq=6、scene_closed=true、settled、delivered=1、report_pending=0。任务7原结果 SHA256：`2146f5275cf680ed554ed48febb49727b579c478a275adf9a9cdbd1abf4287a3`，同样已补报并结清。失败尝试保留在正式任务历史，不通过新任务绕开占用，不重复投稿来取得截图。

## 已移交的范围与验收限制

[CHG106](../../../active/CHG-20261120-106/change.md)统一承接图片库、封面模板与真实渲染、快速发布AI、续编、真实成片缩略图、安全终止/人工继续、四种核实/补录、公开作品关联、放弃/条件复制与成功统计，保持一个业务闭环，不按接口或按钮另拆CHG。

尚无已核验公开作品链接，审核中不计公开成功。用户对完整M6的最终验收尚未完成。CHG101关闭只代表本轮现有代码与基线收口，不表示上述功能或M6完成。
