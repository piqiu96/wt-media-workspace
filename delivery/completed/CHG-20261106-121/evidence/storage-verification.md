# 存储迁移验证

日期：2026-11-06。

- Cloud `666833b`：新s3位置解析、legacy旧位置、不可变对象条件写与全字节核验；`9abde5d`：素材ID键及成片ID预分配。模板/前端未在本CHG修改。
- `go test ./...`：PASS，本次全包退出码0；日志在本机临时目录，不提交原始输出。
- `WT_MEDIA_STORAGE_LIVE=1 go test ./internal/infra/storage -run TestLivePrimaryStoreImmutableRoundTrip -v -count=1`：新bucket实际写入、同内容幂等、不同内容冲突、原字节读取及清理通过。进一步直接测试发现后端忽略条件PUT：此处原有条件写方案不充分。已改为数据库永久绑定路径与摘要/大小，再执行写入；两个独立客户端同时写不同内容，一个成功、一个冲突，实际读回完整。
- `go run ./cmd/migrate`：PASS，应用20261106_096_compose_output_allocations，98个迁移。后续应用097_storage_content_claims，合计99个迁移。旧16个成片ID先进入分配表；没有预生成正式成片。
- `go run ./cmd/storage-migrate -inventory -report ...`：118处引用（16成片、34素材、68传输），53个不同位置，SHA256全部已记录。引用总大小9897273585字节，包含同一对象重复引用。
- `go run ./cmd/storage-migrate -apply -report ...`：FAIL，118处旧data读取均AccessDenied；未切换任何失败引用，未覆盖或删除旧对象。等待用户提供旧bucket读取权限，已发异步问题。旧数据迁移保持未完成，不记PASS。
- 本地相关服务已通过Workspace控制入口停止，待复制/环境复起；没有更换数据库。

独立审查未确认新增重要缺陷。针对同attempt重复执行的清理前提，已核实现有领取事务只领取pending、原子增加attempt_count；单slot顺序调用执行，只有等待素材时重复且未开始渲染；进程锁防同节点重复worker。正常旧租约/新领取使用不同分配ID。没有新增允许同attempt双执行的入口。

后续独立审查：新claim保护未发现阻断缺陷；按审查提醒去掉endpoint参与身份计算，以持久s3 bucket/fullkey为准，避免域名/协议别名绕过。缺少共享claim适配器拒绝正式写入。历史复制/切换明确移交CHG125，未被记为成功。

- `bin/control.sh start`：从源码重建Cloud/Worker/前端/DMG，Cloud、前端与BitBrowser通过。DMG交还Agent端口后未启动sidecar；没有据此声称桌面链路通过。通过环境实现入口up恢复开发Agent，再运行`bin/control.sh verify`：全部检查PASS，登录admin通过；桌面实际业务验收仍由CHG125完成。
- `wt.py chg verify CHG-20261106-121`：190项Workspace测试与Cloud模块测试PASS；首次环境门禁因上面Agent端口失败，恢复后单独重跑同一环境verify全部PASS。
- Cloud PR33 CI verify：SUCCESS；完整Go回归PASS。远程git连接不稳定，使用GitHub Git Database API逐项同步blob/tree/commit，所有提交SHA与本地严格相等，没有重写提交。
- 用户确认目标bucket为wt-media；实际列举仅6个0字节目录，并检查旧逻辑路径、旧prefix路径和新ID路径均NoSuchKey。已请用户提供历史文件来源；仍不假定历史对象已在目标bucket。
