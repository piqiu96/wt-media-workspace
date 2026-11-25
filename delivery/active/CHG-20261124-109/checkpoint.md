# CHG109 执行检查点

## 已完成

108四仓PR51/19/18/64均合入本地main；Workspace实际merge bf190c945e3a34d3a9c79651df623055fef190a3，其余见108归档。109唯一Active IMPLEMENTING；用户授权完整自主交付及最后统一验收，已明确必须参考Cloud web/example原型。

## 当前

T01完成，Cloud example原型930553217cf5a3c8a1750178da4974d5b46dfeac，原型366/计划34/example21、浏览器16项及构建通过。根独立看16类关键截图并重跑366项通过。T02已完成提供方发布及独立审查，T03 f0f19b3迁移与数据层独立审查通过；T04 a269207及fc9f7ff两P2修复独立审查通过，当前T05由chg109_contract实施共享事务启动/首启冻结/顺序推进/控制/调度及全父级围栏；T06最终结果和Web未实现。计划只监控及推进准备好的批次，首次启动冻结全部配置，不追加补量；保留10%/零分母/未知阻断、人工暂停及原批次同名快捷操作。

## 下一步

依次T01原型/正式定义、T02契约、T03数据库、T04目标与AI、T05顺序推进、T06最终结果、T07共用Vue与plan本机续编、T08真实多批与双端、T09独立review/PR修复/合入归档。

## 验证与限制

启动前108四仓main与验收source tree一致。当前真实只有1个本人百度Profile，实际多批按此顺序执行，受控多Profile分列。109真实验收需通过合法成片生产流程准备新的本人可用输出，不能复用已占用output134或改库伪造。无阻断业务疑问；凭据不落仓，真实DeepSeek仅发送已授权文本/目标和资源数量。

T01独立预审发现三项实现定义遗漏，已在plan落字：全部已启动前缀未决、永久停止含report提交许可/心跳、每批选择范围与缺口持久冻结；确认绑定实时依据，takeover不可绕过首启。无新增产品决策。

T02本机提供方：Agent6f565d2发布LocalAPI2026.11.25.2追加plan enum；独立只读OpenAPI兼容性复审无P1/P2，契约文档8项通过。Desktop3f09248同步消费锁（仅锁，Plan桥运行分支留T07）；Workspace map同步，verify_m0_config通过。Cloud017b3b6发布API.4完整16操作及Task/Batch核实投影，根独立重跑8项OpenAPI/JSONschema通过；唯一P2由09ab0b3修复，根与独立审查者分别复验9项通过，完整POST/PUT拒绝6个父计划投影且响应字段齐全；无剩余T02阻断。当前开始T03隔离MySQL数据层，不修改真实DB。

T03完整repo隔离MySQL72.016s通过（修正pre118历史fixture Omit新字段后全重跑），fullGo通过；根独立4项TestPlan2.564s及审查者2.555s通过，无P1/P2。证据见evidence/t03-data-verification.md。

T04进行中发现recommend SSE草稿事件与既有StreamOneWithTimeout元信息不一致，已授权提供方在.4内定点对齐现有row_key/input_revision/logid/start/progress/done并先契约再消费，新增真实流断言；不造第二套流。T04尚未完成测试/审查，不冒称运行接口可用。

T04 root发布全包及隔离TestPlan2.939s通过；提供方SSE定点对齐3b83cb5，schema9PASS。独立审查两P2（admin copy动作、batchname上限）fc9f7ff已关闭。T05将隐藏Plan内部pause_reason对齐schema，不新增用户参数；执行范围较大按共享事务与命令分提交，不能将T04假当完整推进。
