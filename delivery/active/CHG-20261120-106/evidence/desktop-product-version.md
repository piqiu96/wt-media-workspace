# 客户端产品版本同步验证

日期：2026-11-24。关联 CHG106 Task 4，保持 IMPLEMENTING；本记录不代表 M6 签收。

## 修改及来源

- Workspace 校验 Manifest 后输出 product_tag，和独立 Desktop 组件 Tag／Commit 一并传给构建。保留官网下载清单中的客户端版本，不注入 Cloud Web 页面。
- Desktop 在 Tauri CLI 解析配置前生成版本覆盖层与派生 desktop-build.json。正式入口拒绝缺失产品 Tag、无效 Tag、来源 Tag／Commit 不匹配；未发布包带 dev／test／local 标识。版本记录、macOS 命名、挂载验证及 Windows 安装回归使用有效产品版本。
- Cloud 共用 Vue 登录页和侧栏仅在 Desktop 显示 getVersion() 返回值，Web 及原生调用失败不显示虚假版本。
- 此前工作区的发布流水线 prod/stable 门禁和 Windows 测试迁移路径属于本链路前置接线，一并保留；其他未提交的环境品牌、内容池、统计标签、架构及部署文档修改不纳入本次版本提交。

## 实际验证

- 失败验证：Cloud 新预期最初有2项失败，确实返回旧 Web 包版本；Desktop 新测试最初因版本覆盖工具不存在失败。补齐后均通过。
- Cloud：版本解析、AppLayout 和登录页定向测试共11项通过；Web、Desktop 前端生产构建通过。
- Playwright：实际启动本机已有 Chromium，拦截测试会话；Web 登录页／侧栏均无版本元素，模拟 Tauri 原生返回0.1.2时，两处均显示v0.1.2，4场景通过。没有登录或改动真实业务数据。
- Desktop：`python3 -m unittest discover -s tests/pack -p 'desktop_*test.py'` 共16项通过；同一组件源码构建0.1.2／0.1.3、旧记录不污染本地构建、缺失／错误输入拒绝、覆盖层／资源记录一致和原生版本不一致拒绝均覆盖。
- Desktop：既有 release-versions shell 回归20项通过；macOS package dry-run 使用临时组件 Tag v0.1.0-rc.9、产品 Tag v9.8.7，产物名称使用9.8.7，通过。未创建真实仓库 Tag。
- Desktop：Rust workspace 558项通过、6项原有忽略；修改的 build.rs 定向 rustfmt 检查通过。全仓 fmt 检查发现既有环境隔离代码格式差异，本次未混入无关格式修改。
- 实际macOS Apple Silicon开发app构建通过：`WT_MEDIA_RELEASE_PREBUILT=1 python3 scripts/build-desktop-environment.py --environment dev --profile debug --bundles app`。Info.plist、desktop-build.json、versions.json 三处均为 `0.1.0-dev.a6ff24dd19.dirty`；记录来源commit为a6ff24dd191990719d615cddbd32399ee2be3f0d，如实保留当前未提交修改标志。完整签名校验通过。产物在 Desktop `target/debug/bundle/macos/起飞 Dev.app`，未替换用户当前安装应用。
- Workspace：Manifest、资产汇总、配置、Cloud发布载荷和下载清单21项定向测试通过；工作区既有环境门禁测试同步构建入口后通过。全工作区215项测试通过（含既有未提交的门禁／控制入口测试），交付治理校验通过。

## 限制

- Windows安装后 ProductVersion／DisplayVersion／内置来源一致性已接入 release.yml 的既有安装／重装／卸载回归；本机为macOS，未实际执行Windows或Intel原生打包。
- 本次没有新建产品／组件 Tag、发布正式Release、部署线上或合并PR。现有已发布旧包不会被代码提交追溯改写。下一次Manifest需选择包含本改动的Desktop与Cloud组件Tag。

代码提交：[Desktop PR #16](https://github.com/piqiu96/wt-media-desktop/pull/16) `6523bfc`、[Cloud PR #49](https://github.com/piqiu96/wt-media-cloud/pull/49) `65cdbc2`、[Workspace PR #60](https://github.com/piqiu96/wt-media-workspace/pull/60) `536fdaf`。Workspace远端[PR checks #152](https://github.com/piqiu96/wt-media-workspace/actions/runs/45370154256)已通过；记录时Desktop #60与Cloud #192仍在运行，不计为远端全部通过。
