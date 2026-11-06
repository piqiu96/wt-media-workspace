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

- 当前整体验证发现策略页旧静态断言仍期待原按钮顺序；本轮按规范将主要轻按钮「立即执行」前置，更新该已有列宽断言，使其与实际可见顺序一致后复测。前述1000项通过为前置测试，不当作最终head证据。

## 最终页面验收

- 用户回复ok后通过系统文件选择器完成，不更改Chrome扩展权限。实际不可读PNG上传返回错误，选中文件与编辑名称完整保留；移除后上传不可点。重选可读PNG，缩略图与大小、预填可编辑名显示正确。实际上传中「正在上传并校验」和选择/移除/取消/提交禁用；成功后弹窗关闭、列表出现文件9。
- 点击文件9的复制链接，浏览器剪贴板为 `https://wt-media.bucket.oss.longyanyue.cn/file-ku/files/9_CHG126_UI%E5%BC%80%E5%A4%B4%20100%25%231.png`；UI改名为CHG126_UI改名验证后再次复制完全相同。匿名读回88字节/SHA256与原图一致。系统选择器另选视频，实际显示VideoIcon、原文件名和大小，不加载图片预览；取消成功。
- 真实hover计算样式：普通操作品牌蓝rgb(0,82,217)，悬停rgb(38,111,232)+rgb(234,241,252)浅底；删除默认正文rgb(38,52,73)，悬停rgb(213,73,65)+rgb(255,240,237)浅底。热区32px。策略页实际「立即执行」在首位、浅品牌底；详情/编辑/复制透明蓝字；任务及成片列表当前可见详情同样32px品牌蓝。
- 证明截图：本地/tmp/wt-media-chg126-upload.jpg、/tmp/wt-media-chg126-row-actions.jpg、/tmp/wt-media-chg126-strategy-actions.jpg；截图为验收时刻，测试文件随后清理。拖拽接线经TDesign实际源码及独立Review核对，未冒充操作系统真实文件拖拽实测。
- 文件9删除成功后的旧入口回读遇到环境重启，服务恢复后重新读取确认5～9所有本轮测试记录均不存在，文件9回源404；原有文件3/4仍保留。
- 补查素材列表前的源095cbf3：完整前端134文件1000项PASS（/tmp/wt-media-chg126-web-final.log）；最终完整bin/control.sh start所有gate PASS（/tmp/wt-media-chg126-final-bring-up.log），两端构建与DMG从最终源重建。整体CHG检查正在收口，不以前置测试代替最终结果。

## 最终检查

- `python3 scripts/wt.py chg verify CHG-20261107-126` 最终退出0，包含Cloud全Go、1000项前端、Cloud control检查、完整受管环境/BitBrowser验证、Workspace 190项、Delivery/AI/Skills/Product/Contract配置/文档/脚本检查全部PASS。最终日志/tmp/wt-media-chg126-verification.log。
- Cloud PR38，最终实现095cbf35c6326da39fafb5d7f5f20d64d3c0580f；独立Review未发现P1/P2。Workspace独立Review确认需求、契约及缓存边界一致；指出的旧顺序断言已修正并由最终全量检查通过。
- 本次验收是代码交付、自动检查和代理真实界面走查，不替代用户人工视觉签收；无未验证的执行承诺。等待各仓PR检查及合并后归档。

- 最终同类页面补查：素材库/我的素材仍有旧Secondary文字按钮类，我的素材「放弃」未显式标记危险行操作；仅移除两处旧类、将放弃改为公共is-danger，保留权限/回调/业务行为。复用已经实测的同一ResourceRowActions颜色和热区，不新增页面色值。该三处类名调整后重新运行共享前端测试及双端构建，不重复无关后端实测。最终源提交及本地组合随后同步。

- 素材列表颜色补充提交c4e02c5bb7e5a5c9a0d8a55a9a9559f8a51fb520；完整前端再次134文件/1000项PASS（/tmp/wt-media-chg126-final-web.log），新增类全部复用已验收公共组件，不新增业务路径。最终本地组合固定该提交。

- 补充3处素材类名独立Review PASS，无P1/P2；权限/条件/禁用/回调均未改变。最终c4e02c5 Cloud CI全部通过（PR38，run42284994544：测试、MySQL迁移、发布二进制及Cloud/Desktop双端构建、打包脚本）。本地Cloud build:cloud PASS，最终DMG及其共享前端从c4e02c5重建成功；最终完整CHG检查再次运行。
