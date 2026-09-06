# 代理台账操作与待同步安全收口（Task 8）

日期：2026-09-06  
CHG：CHG-20260805-033

## 自动验证

| 操作 | 实际 | 结果 |
| --- | --- | --- |
| Cloud `go test ./internal/modules/proxy ./internal/modules/profilebinding -count=1` | 代理资格、编辑后失效检测、关联删除保护、绑定与解绑读回通过 | PASS |
| Cloud Web `npm test -- --run` | 12 文件、46 测试通过 | PASS |
| Cloud Web `npm run build:desktop`、`npm run build:cloud` | 两种前端产物构建通过 | PASS |
| Agent `.venv/bin/python -m unittest discover -s tests` | 79 测试通过；包含直连解绑的显式 `noproxy`/`proxyMethod=2` 写入和残留Host/Port拒绝 | PASS |
| `scripts/m2b-local-acceptance.sh all` 与运行态检查 | 迁移27条已就绪；最新DMG于2026-09-06 11:01生成、挂载并启动；Cloud health、Agent health与`bitbrowser_status=normal`均通过 | PASS |

## 覆盖事实

- 批量检测逐条复用已有检测接口；代理管理没有BitBrowser写入入口。
- 连接字段变化会清空检测结果和出口IP；空编辑密码保留既有密钥，到期时间不会因前端未传字段被清空。
- 有绑定窗口的代理由Cloud接口拒绝删除；浏览器窗口页以正式关系与当前代理台账地址比较，显示“代理配置待同步”。
- 新绑定由Cloud接口校验启用、检测正常、未到期与配额；前端仅显示同样条件的候选。
- 解绑只有Agent写入直连并读回`noproxy`、空Host、空Port时才成功。

## 待人工验证

真实代理记录目前仍需由管理员在代理管理页修正为独立Host与Port并检测成功；不得用现有错误格式记录执行真实BitBrowser写入验收。
