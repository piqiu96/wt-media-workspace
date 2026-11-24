# CHG107 合入与验证核对

- Cloud PR50：60847fdeda19ef4d889de3ded3be2e9521ba6d93；Agent PR18：7c87673ac389ec37f198a384405a7e8ce4dfae03；Desktop PR17：e31e352d028034088985fdcd66d6f6eee11fd0c6。均使用merge commit，按提供方先行合入，本地main已快进，运行仓短期分支退场。
- Workspace PR63记录本项。自身关闭PR无法自包含最终合并SHA，元数据中Workspace34713f7563675803bf572b63118d202361c72ff9是本PR内已审查技术证据提交；PR63合并后它必须存在于本地main。后继108记录PR63实际合并SHA，不回改归档。
- Cloud最终候选27b8aca CI M0 Cloud #198、Agent44c7b81 #70、Desktop99b0e12 #62通过；Workspace最终证据/归档继续在PR63运行治理检查。
- 测试：Workspace215、Agent892、Desktop560通过/6既有忽略；前端163文件1195项、两端构建、受控Chrome回归及原型352项通过。Go完整初版、修复后模块及实际隔离MySQL通过。独立后端两轮及前端修复限定复审闭环。
- 真实完整环境与最新arm64 DMG、CORS、登录、受信工作环境通过；实际本机续编、退出重登恢复、真实AI/竖版渲染采用、Cloud保存清理和Web修改/原生读回通过。任务7、尝试34保持不变、成片134未占用，批次2修订2。详见installed-e2e.json。
- 实际只有1个本人账号；多行与并发/失败/角色负例由受控或实际隔离数据库验证，不冒称真实多账号发布。107没有启动任务或平台投稿；108/109及最终用户整体验收继续执行。
