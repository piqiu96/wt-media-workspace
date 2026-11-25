# CHG109 T04 查询配置与AI接口

2026-11-25，Cloud a269207b018d8eaf04e3559c02e967f07271e511，限定修复fc9f7ff9489ae04415bf4f29fc6cb0da84ed3967。

A01–08/A16九条路由接通；先scope再total/分页，所有goal类目鉴权，原key找回仍本人范围；页内批量读取batch。copy限ended及修订，只返回白名单骨架，不继承原batchID/日期/任务/占用/授权。AI服务端本人资源计数，外发仅目标/数量/合法数量安排/要求；不发names/rowkeys/账号或Profile身份。模型无配置、查询失败、非法/截断/不守恒、cancel均明确失败，不落计划/任务。

SSE草稿与既有Emitter字段不一致发现后，独立契约提交3b83cb5对齐row_key/input_revision/logid/start/progress/item_result/done再消费，不造第二流；正式schema9项根复验通过。

实现方完整Go通过/tmp/chg109-t04-go-full-final.log，定向publish/权限/SSE/AI负例通过，隔离TestPlan含scope/copy3.389s通过。独立审查2P2：admin ended展示不可能copy；batch name超过100字模型可采用但保存失败。fc9f7ff共用权限及Unicode长度校验，RED后GREEN；独立限定复验无剩余阻断。

根执行`go test ./internal/modules/publish/...`及`WT_MEDIA_TEST_LIVE_DB=1 WT_MEDIA_CLOUD_HOME="$PWD" go test ./internal/modules/publish/repository -run TestPlan -count=1`，分别通过，最终MySQL2.939s（/tmp/chg109-t04-p2-root.log及-root-mysql.log）。前轮根MySQL3.342s也通过。仅本仓隔离fixture，未改实际业务DB，模型测试为受控GenerateJSON，真实DeepSeek留T08。

T05执行和T06最终结果尚未交付，当前不宣称计划可真实执行或结束；正式页面/本机plan续编和真实双端闭环待后继步骤。
