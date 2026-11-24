# CHG107 执行检查点

## 已完成

- 用户授权107→108→109完整编码、测试、PR修复、自测、E2E及走查，最后统一用户整体验收；不逐项请求重复授权。
- 2026-11-25用户确认106验收通过；Workspace PR62已合并（0376fa2c3c6003bae96cf06a75da6ff6e31ea266），106与M6已归档DONE。
- 已批准保存/启动边界、本人账号、固定分组、计划全量准备/冻结、无补量、保留10%及原批次快捷操作的文档基线。
- `wt chg start CHG-20261124-107`四仓依赖与Git预检通过，四仓均为chg/CHG-20261124-107；CURRENT_CONTEXT由工具生成。

## 当前工作

T01/T02：核对原型与最新配置语义，定版Cloud批次配置/资源/批量流契约及Agent batch续编类型。提供方先行，Cloud提供方正在实施；Agent/Desktop续编与Vue客户端已完成定向验证，尚未做业务整体验收。

## 下一步

按plan的T顺序实施：配置与文件引用迁移/事务→资源与保存→批量内容→本地续编桥→共用Vue→真实联调/独立审查→各仓PR/main证据。107不生成task/attempt/成片占用；108、109尚未实施。

## 最近验证

- Workspace完整215项及docs/Delivery/产品对齐/上下文校验PASS，PR62 CI Workspace checks全部成功。
- Cloud `go test ./internal/modules/publish/...` PASS；Live DB用例未开启，不计真实MySQL验收。
- Agent `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -p 'test_publication_draft*.py' -q` 8项PASS；初次沙箱禁止socket.bind，获执行权限后实际HTTP/SQLite通过。
- 独立审查的旧补量索引已修复；治理测试暴露CHG表头误计候选及生命周期夹具依赖，先失败再修复，全量PASS。
- 106本轮归档merge_commits初写为多行YAML，现有解析器仅支持JSON式值；已用相同SHA作序列化纠正（ba2b081），预检通过，验收结论不变。

## 边界

用户指定operator01测试账号及其会话中提供的密码；密码不写入记录或代码。新原型视觉、业务MySQL、真实平台、安装版/E2E尚未验证，不能宣称通过。实际GUI测试前使用environment-bring-up重建并核对环境。

## 本地续编增量（2026-11-25）

- Agent提供方契约2026.11.25.1先行，batch类型复用现有SQLite CAS；先观察拒绝batch/HTTP400，再实现。定向10项、契约8项、完整892项PASS，提交44c7b81。
- Desktop受控DraftType枚举只支持task/batch，默认task兼容，受信当前用户校验不变；任意路径/plan负例先失败后通过。定向3项、完整560项PASS/6项既有忽略，提交99b0e12；既有9条dead_code编译警告保留。
- Vue客户端按用户/运行端/模块隔离，batch清除不影响task，受控桥透传draft_type；先失败2项后6项PASS；批次配置客户端先失败后通过，合计11项定向PASS。
- 独立审查：规格与质量均通过，无可操作问题；尚未验证安装版重启恢复或Cloud零占用完整闭环。

## 执行分工与PR（2026-11-25）

- Cloud契约已先定版落盘：contracts/cloud-api/v1/publication-batch.openapi.yaml；后端执行器 /root/chg107_cloud_backend 负责Go/迁移/正式契约，主会话不写这些文件。
- 共用前端执行器 /root/chg107_shared_frontend 仅拥有web/，保留已通过11项定向测试的批次客户端；两端路由约定/publish-batches。基础契约定版后前后端独立实现，主会话统一集成和净差异审查，不并行启动108。
- Agent PR18、Desktop PR17均为draft，远端M0 Agent #70与M0 Desktop #62已通过；待整体安装版/E2E后ready并按提供方先行合入。
- 只读现有资源盘点（准备用途，未作为新代码验收）：指定运营登录成功，7条可见任务，9个成片中2个未占用，百度本人账号1个。实发按用户已确认的可用Profile数降级；多账号/跨Profile逻辑需受控测试，不能把单账号实测写成多账号通过。未新增任务或投稿。
