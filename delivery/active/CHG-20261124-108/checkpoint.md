# CHG108 执行检查点

## 已完成

- 107四仓已合入本地main并归档；108唯一Active VERIFYING，109未启动。用户授权依次完整交付107–109，最终统一人工验收。
- 按用户要求采用Cloud web/example/proto/publishing-design及common，108原型固定2512d342，映射见原型README。未建立第二套原型。
- Cloud最终fe741fe9db64111c7a75885e1bcc293154f33c95：首次原子建单/占用/授权、固定组、双容量、实际Profile互斥、可靠停车/原线程恢复、暂停/终止与公开核验。最终CloudAPI2026.11.25.3，Cloud-Agent/错误码.2、LocalAPI.1。ADR0037与迁移117切换证据已记录。
- Agent最终0d507e1f7440841c4081c8fb1b289325eff24ae1完整949项、独立审查通过；Desktop ca44cba8eb5782d08bf6e2b0d7f8ec8e1eabf826完整560项/6既有ignore，协议锁及打包回归通过。
- Cloud全部独立审查及PR51四条已知P2已修复、复验和resolved：原key不可由row_keys冒认；组及实际queued扫描越过100个无效候选；批次无操作JSON显式[]而独立任务可省略；公开核验keyset越过20个失效输入，保留原key优先及满窗口早停。
- Go完整全套与隔离MySQL补测通过；前端164文件1220测试、双构建及Chromium权限/竞态/空操作负例通过。真实HTTP .3另key启动409明确未生效，task集合不变，见start-receipt-http.json。
- Workspace挂载helper380b5d8/63de2d2及文档2186239：detach失败停止、attach须真挂载、唯一canonical同名与完整versions一致才open，独立审查通过；相关22项、全套220通过。source Skill更新并由sync工具同步副本。

## 真实验证

- 现有本人百度Profile只有1个，配置并发5，按用户确认向下兼容实际group1成员1。batch2目标60、候选1、明确确认缺口59后仅建task12/attempt35/output134；真实submission1882771499985646302，generation2核验公开并关联唯一work5，平台ID11733113375672752567。重启后仍一次attempt，不重复投稿。原attempt保留completed/reviewing投稿历史，后续公开观察更新task与work。
- 最终fe741fe完整all PASS，日志/tmp/chg108-final-fe741fe-bringup.log。最新挂载frontend0.1.0+fe741fe与构建一致；路径/Users/aqiuye/Develop/workspace/wt-media/.local/m2b/desktop-review-mount/起飞.app。
- 最终Web及安装版实际走查均为1/60·1.67%、待公开0、差额59、任务行已发布。原任务/作品关联及返回分页正确；真实Web零候选批次1禁止start，带原因终止后cancelled且零task。开始后配置冻结；复制显示原成片已占用。
- 正式wt chg verify在Cloud7ba/Agent0d/Desktopca44退出0，215/949/560及全部环境门禁通过；后续最终Go、前端1220、Workspace220和fe741fe全环境分别验证通过，范围如实列于证据。Windows及真实多Profile未宣称已跑，受控并发/故障与真实单Profile分列，V01–V11见acceptance-matrix.md。

## 当前与下一步

四仓PR为Cloud51、Agent19、Desktop18、Workspace64。尚未合并；Cloud最新CI204运行中，Agent72/Desktop64绿；Workspace待提交最终证据并ready。接着检查所有最新CI/review thread，更新PR，合入运行仓并确认本地main，最后Workspace归档合入，再按依赖门禁启动109。不再次要求已授权权限或逐CHG用户签收。

## 现场与限制

旧核验安全切换：旧服务停止、8188/8765无监听，原Profile正式API两次读回closed后才按117 README开放cutover，UTC2026-11-24 20:03:40.261007；未改业务结果。详见legacy-cutover.md。

旧dmg-mount遗留只读ghost未被当最新包使用；canonical改同Runtime根desktop-review-mount并逐次验证挂载来源。3fc构建临时image校验失败已精确卸载本次临时镜像后完整重跑，没有跳过门禁。

CUA无活动/无takeover，最后completion为Verified final cross-client public results。现有browserForFinalWeb/browserForFinalReadback实际变量为browserForFinalWeb及webForFinalReadback，tab1最终batch2；acceptedDesktop为新路径App。公开作品临时tab3已关闭。IAB避免getTab/reload/goto的focus超时，使用browser.tabs.get('1')与Playwright。原生截图2560坐标直接使用。

凭据仅用会话值不落仓；DeepSeek只发送用户允许的标题/文案/要求/目标资源数，不发送视频或凭证。没有阻断业务疑问；剩余仅PR交付步骤。用户107–109整体最终验收尚未发生。
