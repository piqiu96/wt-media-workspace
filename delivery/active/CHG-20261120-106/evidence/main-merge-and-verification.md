# CHG106 main合并与验收核对

日期：2026-11-24。用户授权“全部合并main，然后开始处理chg106状态”。本记录核对PR、CI、本地main和既有验收证据；没有新增真实投稿、直接改业务数据或重新宣布旧公开结果。

## 合并基线

下表是本轮全部代码及记录合入后的main基线；本记录自身的状态回写由后续Workspace PR承接。

| 仓库 | 合并PR | main合并提交 | 对应最新提交CI |
| --- | --- | --- | --- |
| Cloud | [#49](https://github.com/piqiu96/wt-media-cloud/pull/49) | `ac29c1a7cefaace40501c61a10bb618309b39002` | [M0 Cloud #194](https://github.com/piqiu96/wt-media-cloud/actions/runs/45387627068)：PASS |
| Agent | [#17](https://github.com/piqiu96/wt-media-agent/pull/17) | `1b1d58efab5554a69c484f98e66fcd45bc4e9d59` | [M0 Agent #68](https://github.com/piqiu96/wt-media-agent/actions/runs/45386080391)：PASS |
| Desktop | [#16](https://github.com/piqiu96/wt-media-desktop/pull/16) | `4214b65f34bd8537a6a7e367700f8655f5b54a16` | [M0 Desktop #60](https://github.com/piqiu96/wt-media-desktop/actions/runs/45370019997)：PASS |
| Workspace | [#60](https://github.com/piqiu96/wt-media-workspace/pull/60) | `191b74de737844c686b18de265afb27801d36d41` | [PR checks #154](https://github.com/piqiu96/wt-media-workspace/actions/runs/45386778526)：PASS |

代码合并完成时，四仓已通过SSH抓取并以ff-only同步本地main，工作区干净；已确认合入的本轮短期分支删除。此前未提交但已获确认的环境品牌、内容池、架构、部署、发布门禁及测试均已收齐。代码基线无剩余待合并PR或未解决评审线程；本状态回写PR另行承接。

合并前审查发现的两条P2已先复现再修复：Agent `9a77962`恢复成功但旧包缺关窗证据时补查原attempt，不凭成功直接删文件；Cloud `26157a3`关联内容查询不附加默认pending。评审线程均已解决。

## Done When对照

| 条目 | 证据及本次核对结果 |
| --- | --- |
| Task 1：真实图片库与模板维护、渲染、引用保护 | [验证摘要](verification.md)的图片/模板增量：真实Web上传1200×900图片、实际1080×1440出图、溢出阻止、发布/启停分离；真实隔离MySQL生命周期/并发/保护通过。具备实际使用证据 |
| Task 2：真实AI、三种封面、缩略图、确认失效 | 同上真实成片首帧、快速发布模板、不同素材全自动闭环；真实DeepSeek、原封面与现成图/模板三路径及旧响应/受影响确认定向回归通过。原生模板生成和比例拒绝已实测 |
| Task 2：Desktop重启续编及Web暂存 | [最终安装包复验](verification.md#最终安装包复验2026-11-22)记录SQLite草稿跨重启恢复；正式源码覆盖创建成功清理、失败保留、结果未知先查询。保存返回不创建任务、不占成片 |
| Task 3：状态动作、原attempt、占用与异常 | [快速发布收尾](quick-publish-closeout.md)及[归属整改](publication-ownership.md)：实际隔离MySQL、原现场继续/安全停止、未知核实/补录、重试/放弃、并发与权限回归通过；取消保留占用，缺安全依据拒绝处置。模拟与真实GUI明确区分 |
| Task 4：至少一条真实公开作品及可信统计 | [不同素材全自动闭环](verification.md#不同素材的全自动新任务闭环2026-11-22)：2026-11-22素材188→合成729→成片136→真实AI/双封面33/34→任务11/attempt34，回执1882535465926339971；自动CheckJob核实作品12052878563859428344，登记作品4并投影统计。无人工补录或直接写库；2026-11-22累计4/今日2，不冒充今天数值 |
| Task 4：页面、原型、角色及安装版关键流程 | [视觉整改](visual-alignment.md)、[验证摘要](verification.md)、[归属整改](publication-ownership.md)：原生查看任务11、双封面/回执/关联作品4、列表/统计及草稿恢复通过；管理员原生发布页入口禁用已实测。后续正式Vue六组角色及图片库八场景走查通过 |
| Task 4：个人信息与桌面设置 | [设置验证](desktop-settings-account.md)：原生目录选择取消/打开/登记移除/TOML回读保留文件、资料取消、实际日志/诊断通过；失败/部分失败等受控回归通过 |
| 补充：桌面环境隔离 | [环境验证](desktop-environment.md)：dev/test/prod身份/数据目录、原生DEV/TEST、正式门禁、实际Agent启动与登录就绪通过；Cloud最终品牌初始化已收齐 |
| 补充：发布缓存清理 | [缓存验证](publication-cache-cleanup.md)：真实隔离文件和SQLite删除/保留/重启补清、失败独立重试通过；平台/Cloud响应模拟，按用户确认不追加真实投稿。本次137项发布回归及P2修复通过 |
| 补充：仅客户端显示真实产品版本 | [版本验证](desktop-product-version.md)：Manifest→CLI覆盖层→原生/内置记录/安装包/getVersion，组件来源独立；16项打包Python、20项shell、558项Rust及实际开发app签名/版本一致通过。Web不显示版本；缺正式输入拒绝交付 |
| 代码审查、main合入与用户签收 | 四仓审查修复及最新CI通过，全部进入本地main。**用户M6整体验收签收待完成**；本轮合并授权不等于整体签收 |

## 本轮实际验证

- Cloud：完整前端161文件1176项通过；双端生产构建、角色六组、入口冷启/刷新四场景通过；内容池初始/更改/重置及五类关联查询实测通过，无真实业务写入。关联查询回归先失败5项，修复后单文件30项通过。
- Agent：`PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -p 'test_publication*.py'`，137项通过；新增缺关窗依据恢复场景先失败后通过。
- Workspace：`python3 -m unittest discover -s tests` 215项、`python3 scripts/docs/check.py` 15索引、Delivery治理与产品计划对齐通过；状态回写后再次执行这些检查通过。`git diff --check`通过。
- 逐一核对四仓PR合并状态、对应头提交CI、本地main包含合并SHA及干净工作区；代码基线合入时四仓开放PR清单为空；其后仅创建本状态回写PR。

## 状态与边界

CHG106与M6转为VERIFYING，保持Active；尚未收到M6整体验收签收，不标记DONE、不归档、不启动M7。

生产远端代理实际出口尚未实测，保留验证限制；受控CONNECT成功与不可达不直连验证不替代真实出口。多账号联合执行和长期运行按已确认范围留待批量发布阶段。常见异常采用定向模拟，原生GUI不穷举。旧窄屏脚本390px分支未计PASS，本轮没有扩展该布局整改。

Windows／Intel原生安装构建、新正式产品/组件Tag、正式Release与线上部署未执行；本轮没有重建替换当前安装包或清理真实运营缓存。已安装旧包不会随main合并自动变化，下次Manifest需引用包含本次修改的组件来源。
