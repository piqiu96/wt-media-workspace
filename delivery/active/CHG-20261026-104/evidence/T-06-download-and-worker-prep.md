# T-06 真实链路：下载门槛、我的素材下载、Worker 源准备

环境：Cloud API `127.0.0.1:8188`，用户 `operator01`（id=3，团队 1，普通运营）；本机 Local Agent 轮询同一 Cloud；对象存储为远端 S3（配置在 `config/storage/object_storage.toml`，不记录凭据）。

## 直接下载无有效 `material_usage`：失败关闭

素材 2（团队 1，`other`，当时未加入我的素材）直接调用：

```text
POST /api/v1/materials/2/downloads
HTTP 403
{"errcode":15007,"message":"没有权限操作该素材关系","data":null,"error":{"type":"material_usage_forbidden"}}
```

同一门槛对已移出的关系同样生效（素材 17 的 usage 94 移出后，见下）。`material_usage_forbidden` 与 `cloud-error-codes/v1/content-production.yaml` 的登记一致。

## 从“我的素材”下载：真实文件落盘

素材 1（已加入，usage 92 `active`）：

```text
POST /api/v1/materials/1/downloads  → 202
transfer_0d360318b42988025d13e803  purpose=user_download  status=success
total_bytes=transferred_bytes=33993858   finished_at=2026-10-26 22:56:08
file_name=20261026/其他-1-…虞姬！.mp4
```

本机文件 `/Users/aqiuye/Develop/workspace/wt-media/wt-media-download/20261026/其他-1-…虞姬！.mp4`：

```text
size=33993858
format_name=mov,mp4,m4a,3gp,3g2,mj2
duration=176.100000
```

素材 2 的页面点击（见 T-07 页面记录）同样走真实链路：

| 步骤 | 事实 |
| --- | --- |
| 加入 | `POST /materials/2/usages` → 201，usage 93 `active`（2026-10-26 23:02:25） |
| 页面点击“下载” | Toast“已开始下载，可在下载中心查看进度” |
| Cloud Worker 准备 | `transfer_1ebcb0c0000be41a24e1d43a` `compose_input_prepare`：23:04:51 创建，23:06:25 成功，82,356,001 字节 |
| 本机下载 | `transfer_dfbfe83780fa1a54b04499c8` `user_download`：依赖上述准备任务，23:06:58 成功，同一字节数 |
| 本机文件 | `wt-media-download/20261026/其他-2-…云木木电竞.mp4`，82,356,001 字节，ffprobe `duration=368.9` |

## Cloud Worker 对未加入个人工作集的素材准备

素材 17（团队 1，`other`，合成任务 329 由 Worker 认领）。为了让“准备时不在个人工作集”成为可核实事实：

| 时间 | 事实 |
| --- | --- |
| 23:07:44 | `POST /materials/17/usages` → usage 94 `active`（仅用于建立任务快照） |
| 23:08:14 | `DELETE /material-usages/94` → 204，usage 94 `removed` |
| 23:08:21 | Worker 为任务 329 创建 `compose_input_prepare`：`transfer_bb82d5b504857aff93524793` |
| 23:09:27 | 准备任务 `success`，`total_bytes=143,290,139` |
| 读回 | `materials.id=17`：`video_status=ready`、`video_size_bytes=143290139`；API `usage_status=removed`、`my_usage=unused` |

即：准备任务是在关系已移出（`removed`）之后由 Worker 创建并完成的；Worker 的 `PreparationSource`/`EnsureMaterialSourcePrepare` 不经过用户 `material_usage` 校验，个人下载门槛没有误伤 Cloud 源准备。准备任务完成后，合成任务 329 进入 `waiting_input`，本次因验收只需证明准备链路而停止 Worker；任务 329 的清理见收尾记录。

## 结果

PASS：无有效关系直连下载 403；从我的素材下载真实落盘（两次、不同素材）；Cloud Worker 在关系移出后仍完成源准备并读回 `ready`。
