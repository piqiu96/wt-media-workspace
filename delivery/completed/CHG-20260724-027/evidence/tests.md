# CHG-20260724-027 验证记录

> 日期：2026-07-24  
> 范围：M2-B3 媒体账号台账与 Profile 真实绑定闭环

## 1. 后端模块测试

命令：

```bash
GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build \
go test ./internal/modules/mediaaccount ./internal/modules/profilebinding ./internal/modules/identity ./internal/modules/migration
```

期望：

- 媒体账号创建、筛选、绑定、解绑、换绑规则通过；
- Profile 授权校验、同窗口同平台唯一性、换绑后登录状态回到 `unknown` 通过；
- 身份、迁移模块未被破坏。

实际结果：

- PASS。

## 2. 前端单元测试

命令：

```bash
npm --prefix web test -- --run mediaAccounts profileBindings usersApi
```

期望：

- `mediaAccounts` API 参数映射、创建/更新/解绑客户端方法通过；
- `profileBindings`、`usersApi` 既有行为未被破坏。

实际结果：

- PASS，10 个测试通过。

## 3. Cloud / Desktop Web 构建

命令：

```bash
npm run build:cloud --prefix web
npm run build:desktop --prefix web
```

期望：

- Cloud Web 构建成功；
- Desktop Web 构建成功；
- 构建产物同步更新，避免人工验收时仍加载旧页面。

实际结果：

- `build:cloud` PASS；
- `build:desktop` PASS。

## 4. 数据库迁移

命令：

```bash
./scripts/migrate.sh
```

期望：

- `20260724_015_media_account_binding_fields` 可应用到固定本地库 `wt_media_cloud`；
- `media_accounts.remark` 和业务/登录状态索引存在。

实际结果：

- PASS；
- 迁移输出显示新增迁移已应用，累计 16 个迁移。

## 5. 本地 API Smoke

动作：

- 启动本地 Cloud API；
- 使用 `operator01 / operator123` 登录；
- 调用浏览器窗口列表接口。

期望：

- 登录成功；
- Cloud API 可以返回当前用户可见的 Cloud Profile 镜像；
- 如果当前用户没有已授权窗口，返回空列表也属于正确业务状态，不影响 B3 规则验证。

实际结果：

- 登录 PASS；
- `GET /api/v1/browser-profiles` PASS；
- 当前本地数据返回空列表，说明还没有可用于真实绑定 smoke 的授权窗口数据。真实窗口授权和同步已由 B1/B2 负责，本 CHG 只验证 B3 绑定规则和页面边界。

## 6. Diff Check

命令：

```bash
git -C wt-media-cloud diff --check
git -C wt-media-workspace diff --check
```

期望：

- 无空白错误。

实际结果：

- PASS。

## 7. 结论

CHG-20260724-027 自动验证通过。

本 CHG 完成的是媒体账号台账与 Cloud 授权 Profile 的业务绑定关系，不执行账号检查，不调用 BitBrowser，不读写 Cookie。后续 B4 继续处理账号检查与身份回填。
