# CHG126 验证

- Cloud后端提交8eab381；共享前端b4cc51a，上传区全宽视觉调整待补充提交。
- 新URL函数与前端copy行为先确认RED（函数缺失），实现后定向Go config/storage/files和8项前端测试PASS。完整前端134文件1000项PASS。
- go test ./... 首轮仅原有jobs等待重试测试出现时序失败（实际claim2）；源码该测试等待第三次返回后取消，轮询可能先发起下一次领取，与本次files无调用关系。该测试独立连续20次PASS，完整Go复跑PASS（/tmp/wt-media-chg126-go-final.log）。未修改无关worker行为。
- 独立审查review_cloud_pending：未发现P1/P2；独立19项前端和定向Go PASS，实际提取页面脚本检查失败保留、并发防重、busy禁止重选和预览释放PASS；不冒充真实视觉验收。
- bin/control.sh start 从b4cc51a强制重建Cloud/worker/Agent/两端前端/DMG，所有freshness、health、BitBrowser、CORS、login gates PASS；见本地/tmp/wt-media-chg126-bring-up.log。
- 浏览器文件列表测量：常规行操作rgb(0,82,217)、透明底；删除rgb(38,52,73)、透明底；均32px热区。文件预览/下载已统一文字按钮。上传弹窗已实看选择区、名称及禁用提交。
- 浏览器扩展未开本地文件读取，chooser.setFiles被明确拒绝；未扩大扩展权限。系统选择器验收暂受Mac锁定影响，已请求用户解锁；后续以系统选择器继续。

- 真实接口验收：图片7（88字节）和视频8（317515字节）上传成功；匿名公共域名GET200、逐字节与SHA256一致；包含中文/空格/%/#，改名后URL完全不变，旧入口附件下载同摘要且使用新名。无效PNG返回400且不出现在列表。两条测试资产已删除，绕缓存后的源路径与旧入口均404。
- 删除调查：公共域名前置nginx缓存会对删除后的同URL返回X-Cache:HIT与旧字节；使用唯一查询参数在删除前读取相同源内容，删除后404，证明源对象已删除。产品/ADR与契约明确缓存副本按缓存规则失效；未修改缓存或bucket权限。首轮测试5/6也已全部清理，不触碰既有文件3/4。
- 首轮治理检查暴露本次LEDGER格式不匹配：修正为纯CHG ID，并使当前仓与affected_repos首项一致；重新执行整体检查。
