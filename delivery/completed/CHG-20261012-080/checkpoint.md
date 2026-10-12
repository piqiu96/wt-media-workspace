# CHG-20261012-080 Checkpoint

## Completed

- T-01：FFmpeg/FFprobe 配置与启动校验；部署测试夹具补齐新增变量（Cloud commit `058d411`），证据见 `evidence/T-01.md`。
- T-02：模板版本注册表和 `basic_cut` v1 固定参数，证据见 `evidence/T-02.md`。
- T-03：隔离运行目录、输入/输出 FFprobe 校验、固定切段执行；异常输入、执行失败和输出时长异常均失败。Cloud commit `5e28c51`，证据见 `evidence/T-03.md`。
- T-04：跨进程单任务锁与独立 `cmd/compose-worker`；缺凭据或工具时启动检查失败。Cloud commit `f179d6e`，证据见 `evidence/T-04.md`。
- T-05：临时键上传、Stat、签名 GET 读回 SHA256、清理；模拟未配置、上传失败和读回不一致。Cloud commits `67bfd65`、`869120c`，证据见 `evidence/T-05.md`。
- T-06 完成：真实测试视频切为 7.007 秒 H.264/AAC MP4，`compose-worker` 两次完成 Garage 上传/签名 GET 哈希比对；独立 Stat 确认临时键 `NoSuchKey`，本地运行目录也已删除。Cloud 全量 Go、Web 507 项测试和 Cloud 构建通过。证据见 `evidence/T-06.md`。

## Current

全部 T-01～T-06 已完成，CHG 已归档。

## Next

下一独立结果是 M4-C2 策略交付，需另立 CHG。

## Blockers

None.

## Recent verification

- `go test ./... -count=1`：全部包通过。
- `npm test -- --run`：独立重跑 55 个文件、507 项测试通过；并行首次运行有 1 项 5 秒超时。
- `npm run build:cloud`：通过；Vite 报已有的大 chunk 提示。
- 本机 FFmpeg/FFprobe：真实 67.754 秒、21,358,859 字节输入切为 7.007 秒、3,619,554 字节 H.264/AAC MP4。
- `compose-worker` 真实 Garage 链路两次成功；对象临时键独立 Stat 返回 `NoSuchKey`；本地运行目录清理完成。
