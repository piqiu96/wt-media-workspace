# M0 工程基线复验报告（最终版）

> 执行时间：2026-07-16
> 修复：profilebinding 测试编译错误（缺少 DeleteProfile 方法）、Agent 测试数据未随 BitProfile 字段扩展

## Cloud Go 后端

| 项 | 结果 |
|---|------|
| go build ./cmd/server/ | ✅ PASS |
| go build ./cmd/migrate/ | ✅ PASS |
| go build ./... | ✅ PASS |
| go vet ./... | ✅ PASS |
| go test ./... | ✅ **全部 10 个测试模块 PASS**（无 FAIL） |

## Web 前端

| 项 | 结果 |
|---|------|
| npm run build:cloud | ✅ PASS（8.06s） |
| npm run build:desktop | ✅ PASS（6.90s） |

## Agent

| 项 | 结果 |
|---|------|
| pip install -e . | ✅ PASS |
| python -m wt_media_agent.local_main | ✅ PASS（可启动，mode=local） |
| pytest tests/ | ✅ **40/40 PASS，8 subtests PASS** |

## Desktop Tauri

| 项 | 结果 |
|---|------|
| cargo build | ✅ PASS（dev profile，18 warnings 无 error） |
| cargo test | ✅ PASS（2/2 测试通过） |

## 结论

**M0 工程基线复验通过。** 三端均能真实构建、测试、启动。
