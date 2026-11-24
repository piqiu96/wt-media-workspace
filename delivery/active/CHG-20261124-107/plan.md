# CHG107执行落地清单：批次配置与内容准备

## 交付结果与范围

运营能准备并保存一批本人账号的发布配置，在发布前继续增删候选、换账号/视频、排序、修改内容和设置。保存只写批次配置，不生成publication_task、不占用成片。已保存未执行批次进入列表；未提交的本机续编不入列表。实际任务创建与发布由[108](../../planned/CHG-20261124-108/plan.md)交付，计划由[109](../../planned/CHG-20261124-109/plan.md)组织。

新建“保存批次／创建并发布”，已有编辑“保存修改／开始发布”；107先交付保存，发布动作接108后开放，不放假成功入口。不提供独立“确认批次”动作。保存允许内容不完整，但基础身份/数据结构合法；每次发布前必须完整检查。

## 执行约定

本文件是2026-11-25实施与验收基线，与change.md配套；状态只在change.md，用户已授权全流程执行，本项VERIFYING，代码须经依赖与分支预检后实施。任务按顺序执行，勾选表示需检查的交付项，不预填完成事实。依赖CHG归档、各仓合入main、范围review及CHG预检满足后才开始运行代码。路径由config/repository-map.yaml定位。

产品以PRD第六章、对应Milestone及本次已确认裁定为准；页面继承Cloud既有publishing-design原型，公共布局/行为/Token分别遵循AdminUI、交互和视觉规范。本轮配置准备原型固定Cloud提交dabc473786098d8215a6db7e332d927d13fc8d96，隔离预览?review=chg107；工程视觉/三角色入口及窄窗已核对，见设计入口§4.3。该原型fixture不代替正式Web和安装版验收，用户仍最后统一验收。

Cloud内部按Handler→Service→Repository落位，跨模块复用所属Service；共用Vue只在Cloud维护，Agent管本机，Desktop管桥。正式OpenAPI/枚举/错误码由提供方维护，本稿API字段是定版输入，不是第二份可写契约。接口省略/api/v1；session/AgentToken/本地受信身份按调用链区分。ID/revision字符串、RFC3339时间，沿用errcode/message/data/logid；查询先授权再分页聚合。保存用revision，创建/启动用请求键与服务端摘要防重，同键异输入拒绝；结果未知先查询原结果，不换键重试。

每步交付填写：修改文件/对应功能与API/实际验证命令和结果/PR或commit/未验收边界。多仓提供方先行，消费生成及Desktop契约锁同步；净差异review通过再按CHG独立PR合入main，用户验收后才关闭。文档检查不代替运行测试，模拟不代替真实平台验收。

## 1. 业务、页面、API对应

| 功能 | 页面/动作 | API | 验收结果 |
| --- | --- | --- | --- |
| B01 批次列表/详情 | BatchManager、BatchDetailContent；搜索/筛选/返回 | A01/02/11 | 已保存未执行配置可查，权限/分页正确 |
| B02 新建与复制 | BatchWorkbench | A03/09 | 复制不继承授权/结果/请求键/占用，创建新身份 |
| B03 资源盘点 | 资源配置 | A04/05/06 | 本人账号，零/未知/读取失败分开 |
| B04 配对/增删/顺序 | 账号顺序、每号上限、类目优先级及人工分配 | A07/10 | 同账号跨类目共用本批上限；目标不随候选删减降低 |
| B05 内容准备 | BatchContentWorkspace/Table/Configuration；单条和批量编辑 | A10/12 | 发布账号/视频明确，变更只使受影响确认失效 |
| B06 图片/模板/封面 | 原封面编辑及批量配置 | A13/14/15 | 全部必需规格真实产物，样例不能发布 |
| B07 预览检查 | 结果总览，不单独弹确认批次 | A08 | 定位不完整、资源变化与缺口；返回保留内容 |
| B08 执行设置 | 结果总览 | A09/10 | 并发数、组间发布间隔、组间处理、异常任务上限一致保存 |
| B09 续编与保存 | 新建未提交恢复、已有记录保存Cloud | L01/02/03及A09/10 | 本机输入和已保存批次分开，已有编辑无第二份草稿 |

组间处理固定文案“自动继续、异常暂停”；异常任务上限说明“异常任务达到该数量时，暂停发布，人工决定继续或终止”。异常上限正整数，具体默认数值不伪装为已确认；并发初值5仅建议，实际允许范围由提供方能力及验证定版。

## 2. API实施清单

| 编号/变更 | 方法/路径 | 输入→返回；写入与限制 |
| --- | --- | --- |
| A01 新增 | GET /publication-batch | 搜索/平台/配置或执行状态/分页，request_key精确找回→items/total；只返回权限内记录 |
| A02 新增 | GET /publication-batch/{id} | id→基础/targets/候选config/设置/就绪问题/revision/允许动作；候选配置受体积限制 |
| A03 新增 | GET /publication-batch/{id}/copy | expected_revision→允许复用配置与来源；重新检查资源、清授权和键，不生成任务 |
| A04 新增 | GET /publication/resource | 平台/类目→数量/可用性/缺口/as_of；无占用、真实错误不转0 |
| A05 新增 | GET /publication/account | 平台/类目/搜索/分页→本人账号/资格/原因；禁止选择其他用户账号 |
| A06 扩展 | GET /publication/output | 原筛选及带入ID→真实成片/缩略图/当前occupied；不返回他人任务细节 |
| A07 新增 | POST /publication-batch/allocate | targets/账号顺序和上限/成片/人工映射→候选配对/逐格差额；无写入/预留 |
| A08 新增 | POST /publication-batch/validate | 平台/目标/候选/内容/设置，已有编辑携带batch_id/expected_revision→发布前就绪及逐行issues/缺口；只读不签许可，已采用文件按受权保存记录复查 |
| A09 新增 | POST /publication-batch | request_key/name/platform/targets/config/execution_setting→id/revision/配置就绪；只保存batch/文件引用/审计，不写task/占用 |
| A10 新增 | PUT /publication-batch/{id}/configuration | expected_revision/完整允许配置→新revision/就绪问题；首次启动前允许候选增删/替换/重排，本批或所属计划已启动均拒绝；计划继承目标不改 |
| A11 新增 | GET /publication-batch/{id}/record | 分页→时间/操作者/事件；不泄露本地凭据 |
| A12 扩展 | POST /publication/generate | items行键/输入版本/字段版本/成片/所选字段/要求→SSE逐行建议或错误；不采用、不确认、不建task；保持原单条兼容 |
| A13 复用 | POST /image-asset/select | 用途/类目/比例→固定选择和元信息；无任务/占用 |
| A14 复用 | GET /cover-template | 平台规格/启用条件→发布模板和修订 |
| A15 扩展 | POST /cover/render | 按行模板修订/短标题/底图/规格→真实文件/输入摘要/SSE问题；事务外渲染，不替用户确认 |
| L01 扩展 | GET /publication-draft/batch | 受信当前用户→未提交新建输入/revision |
| L02 扩展 | PUT /publication-draft/batch | expected_revision/payload→新revision；只限未提交续编，沿用体积限制 |
| L03 扩展 | DELETE /publication-draft/batch | expected_revision→空输入/新revision；Cloud保存成功后清对应新建续编，防迟到复活 |

config的候选使用row_key/input_revision/field_revisions，保存账号/成片ID、内容和已采用封面引用、排序。前端勾选/排序/采用建议不单独建API；保存以服务端资格和输入结构检查为准，发布完整校验由108再做。旧稿/{id}/content不能承担启动前整体编辑，由configuration替代新增设计，不删除现有单任务路由。

## 3. 数据与事务

- 新建publication_batch：id、team_id/operator_id/created_by、name/platform、targets_json、config_json、concurrency_limit、group_interval_seconds、between_group_policy、exception_task_limit、配置/执行控制、revision、request_key/hash、审计时间。字段名为提供方定版输入。
- config_json保存候选而非正式任务；当前目标与候选数分开，排序修改候选order。UNIQUE(created_by,request_key)，团队/所属用户+时间查询索引；ID/FK类型按已有提供方核对。
- 本CHG不迁移task关联，不生成task/attempt/成片占用；这些属于108。计划表及关联在109，不建立悬空FK。
- 无成片占用不等于无文件引用：已保存采用的封面/图片/模板产物要受正式文件删除保护；引用的建立/替换和batch配置/审计同事务，物理文件与渲染不在事务内。
- SQLite沿现有publication_draft开放batch，环境/用户/type唯一，revision保护。Cloud保存成功后编辑以Cloud为准，不新增云端草稿表。

## 4. 执行落地步骤

- [x] T01 Workspace产品/架构：同步PRD/M7/工程设计的保存不占用、本人账号、候选编辑、四项设置；固定调整后的原型SHA。产物：无旧口径冲突的基线。
- [x] T02 Cloud契约：定版A01–15的DTO/OpenAPI/错误和兼容，明确基础保存合法性与发布完整校验区别。产物：生成/契约检查结果。
- [x] T03 Cloud migrations/model/repository：batch迁移、唯一键、修订保存、文件引用事务。产物：隔离MySQL新建/回滚/旧系统兼容证据。
- [x] T04 Cloud service/handler：本人资源查询、分配、validate、保存/编辑/复制/记录。产物：功能与A接口逐项对应，保存后task/占用增量为0。
- [x] T05 Cloud publish/image：AI/封面批量SSE、字段版本、取消/断流/逐条失败。产物：真实依赖成功和明确失败、单条兼容。
- [x] T06 Agent/Desktop：本机未提交batch续编、受控桥、提供方版本/消费锁同步。产物：重启恢复/修订竞争/身份切换证据；若无契约变更不制造空改动。
- [x] T07 Cloud共用Vue：列表、三段工作区、候选整体编辑、批量审阅、配置区和返回。产物：Web/Desktop同源码，发布按钮待108接通。
- [x] T08 联调/独立review：按以下V清单验证，净差异review并修复。产物：evidence摘要、未验收范围；不预填发布成功。
- [ ] T09 各仓PR：提供方先行合并main，回写merge证据/用户验收，满足change后归档。

## 5. 验收与证据

- [x] V01 保存60条候选后batch存在、task/attempt/占用增量均0；未完善内容能保存且标出问题，非法身份/结构仍拒绝。
- [x] V02 编辑增删/换账号视频/重排，row_key稳定；目标60删至58仍目标60、缺口2；没有级联删除正式任务；109接入后，所属计划已启动而本批未启动也禁止配置修改。
- [x] V03 只选本人账号，成员和管理员不能通过直调绕过边界；资源冲突/未知/读失败准确显示。
- [x] V04 同键同输入返回原batch、异输入冲突、响应丢失找回；旧revision编辑全拒绝并保留输入。
- [x] V05 AI旧响应/换视频/字段人工改动、仅改封面、断流重试；逐行采用与内容确认分开，正式封面缺规格/样例/过期拒绝。
- [x] V06 批次文件引用与删除竞争，配置修改/审计同事务；无成片占用不丢封面引用保护。
- [x] V07 四项设置保存、编辑、恢复一致；已有编辑只保存Cloud，新建续编不混成正式批次。
- [x] V08 固定原型逐页/三角色/窄窗/键盘/返回上下文，Web和安装版均核对；留真实检查证据。

## 事实源

- [PRD第六章](../../../docs/product/prd/详细文档/第六章_发布管理.md)
- [发布工程设计](../../../docs/engineering/specs/publishing-management.md)
- [前端规范](../../../docs/standards/frontend/README.md)
- [设计入口](../../../docs/design/publishing.md)

## 本轮验收读数（2026-11-25）

V01/V02的60→58及事务竞争由实际隔离MySQL验证；真实运行库两端验证批次2：目标60、候选1、缺口59，修订1→2，任务7→7、尝试34→34、成片134始终未占用。V05真实AI及实际3:4渲染/采用、V07本机重启续编和成功保存清理、V08两端页面已完成，三角色入口为固定原型fixture，服务端权限由角色负例测试核对；详见evidence/installed-e2e.json及backend-verification.md。109所属计划启动冻结在109集成时复验，107不提前实现。复制仅允许已结束/取消批次，与PRD一致，当前服务受控终态用例覆盖，真实执行结束由108提供。用户仍最后统一整体验收。
