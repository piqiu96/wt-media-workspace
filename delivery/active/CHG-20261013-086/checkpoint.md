# CHG-20261013-086 Checkpoint

## Completed

- CHG 记录已建立（本文件与 `change.md`）。CHG-20261013-085（M4-C7）已于同日归档（四门全绿：Go exit 0 / Agent 705 OK / web 536 全绿 / governance exit 0）。
- T-01 环境基线与素材盘点完成（`evidence/T-01.md`）：server=4a3bee6、迁移至 054、agent-node_b27e0f251ffb07c2ae9a5da4 信任成立、三会话就绪、盘点 171/32/1/2/0/35；改动面核对——production 模块新增全在 compose 面（082～085 自有证据），素材四态与 usage SQL 零改动（061 机器读数可引用），web 素材页被 082/083 改过（UI 腿归用户签收）。

- T-02 素材库与 my-materials 机器读数完成（`evidence/T-02.md`）：AC-02 七探针全过（越权/恢复/幂等/8并发去重/可见/移出/201创建）、AC-03 两半均为本轮真实链路实测（素材 157 not_downloaded→downloading→ready，本地 sha=声明 sha）、AC-04 快照不变实测、AC-01 机器腿实测（409→200 video-url）；UI 腿移交用户。

- T-03 合成链真实复测完成（`evidence/T-03.md`）：真实 FFmpeg 成片（h264+aac，1s 快照切段，sha 三方一致）、成片只在落盘校验后创建（前后对照 0→1 + S3 206）、AC-07 四臂抽测（pending 取消/running 取消/失败/kill -9 重启各臂零假成片、无双执行）；披露：任务 18 源对象缺失为 061 期清零残留、dev 无 v2 模板二进制（快照钉住机制 + 082 停用探针作判据）。

- T-04 我的成片与下载中心机器腿完成（`evidence/T-04.md`）：列表/过滤/详情/追溯/归档/预览签名 URL 全对应；下载链 202 → integrity_sha=声明 sha=本地 sha 三方闭合、幂等去重单行。

## Current

T-05 权限矩阵与边界扫描、三仓测试与提交核对（AC-10/11/12）。

## Next

T-06 十二项汇总对账、用户签收清单、governance verify、归档提交。

## Blockers

None.

## Recent verification

- T-01 全部读数见 `evidence/T-01.md`（health errcode 0、迁移 054、节点信任四条件、盘点 171/32/1/2/0/35、改动面 git log/diff 0 backend commits）。
- T-02 读数见 `evidence/T-02.md`（usage 七探针、8 并发去重单行、素材 157 真实采集下载 sha 闭合、快照不变）；本轮启动 `cmd/discovery-worker`（含 material-prepare-worker）。
