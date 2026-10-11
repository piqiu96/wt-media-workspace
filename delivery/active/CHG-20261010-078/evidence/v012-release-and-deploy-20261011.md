# v0.1.2 发布与部署证据（2026-10-11）

- 组件 tag：cloud `v0.1.2-rc.1`（`bb4419d`，登录错误提示拆分 10005/10006/11004）、agent `v0.2.2-rc.4`（见下，tag 曾重钉）、desktop `v0.1.0-rc.9`（`29ee51e`）。产品 manifest `releases/manifests/v0.1.2.yaml`（stable / online / 线上 origin）随 workspace `024012e` 入库，产品 tag `v0.1.2` 触发 `release.yml` run 38138153403。
- 首跑失败与修复：Windows agent 臂在 `bundled_ca_args()` 抛「CA bundle SHA-256 does not match its pinned metadata」。根因：agent `.gitattributes` 的 `* text=auto` 把新入库的 `resources/ca-bundle.pem` 判为文本，Windows 检出 LF→CRLF 改写字节（本地以 `core.autocrlf=true`+`core.eol=crlf` 工作树复现：3959 行全转、哈希 MISMATCH）。修复：`resources/ca-bundle.pem -text`（agent `8e27531`，复验 CRLF=0、哈希 MATCH，agent CI 绿）。组件 tag 在无任何产物消费前同名重钉到 `8e27531`，manifest 与产品 tag 未动；`gh run rerun --failed` 后全链 success。
- 资产校验：Release 公开（draft=false，stable 自动公开按预期生效），六资产（三平台安装包 + build-info.json + SHA256SUMS + v0.1.2.yaml）SHA256SUMS 全 OK；build-info `product_tag v0.1.2`、`cloud_origin https://wt.longyanyue.cn`、四仓 source commits 与钉定一致。
- 部署链哈希：从 run artifact 取 `wt-media-cloud_v0.1.2_linux-amd64.tar.gz`，SHA-256 `2e0204e4c76d5fc823859a763ff24784c02685116af33b5ec71e935288763b48` 与 build-info 记录一致，包内 SHA256SUMS 复验 OK；同验 `desktop-web_v0.1.2.tar.gz` = `7b39bbb6…`。用户经宝塔完成部署（含预检与 Server→Worker→Scheduler 重启）。
- 部署前基线：线上 `desktop-downloads.json` 为 v0.1.1，`/api/v1/health`、`/` 均 200。
- 部署后探针（2026-10-11）：`desktop-downloads.json` 翻为 **v0.1.2** 且三 URL 指向本 Release；`/api/v1/health` 200；`/`、`/login`、`/home` 均 200；未认证 `GET /api/v1/auth/me` → 401 + `11001`；登录探针：空凭证 → `10005 请输入账号和密码`、65 位账号与 5 位密码 → `10006 账号最长 64 位，密码需为 6-72 位`、形状合规的错误凭证 → `11004 账号或密码不正确`。错误码为云端代码所拥有，线上生效即证明部署的是 `bb4419d` 构建。
- 边界一：build-info `source_commits.agent` 记 `1d6c883`（首跑读的 tag），Windows agent 实产自重跑的 `8e27531`；两提交仅差 `.gitattributes` 三行，不进任何产物字节。
- 边界二：`deploy plan` 期间服务器 `output/online.url` 预签名过期致 HTTP 400；用户重新预签并更新后恢复。预签名最长 7 天，属每次部署的常态物料（见 `~/.wt-media/upload-config-variables.py`）。
- 剩余人工验收：真实账号登录走查、官网视觉与滚动走查、目标用户网络三平台下载。
