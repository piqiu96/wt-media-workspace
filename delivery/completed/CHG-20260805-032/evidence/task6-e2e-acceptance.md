# Task 6 证据：端到端验收（检查链路 + 8 项明细）

日期：2026-08-06
CHG：CHG-20260805-032（M2-B 社媒账号收口）
状态：端到端验证通过

## 环境

- `m2b-local-acceptance.sh all --force-restart` 重建，内嵌 Task1-5 全部新代码
- Agent PID 79081 启动 00:28:42 > 提交 7ad508c（00:26:10）✓
- 门禁全 PASS：Cloud health / Agent health / BitBrowser / Desktop assets / DMG / login smoke

## 验证 1：Agent 真实检查返回 check_items（真实 B站 窗口 a24f40d9...）

`POST /api/v1/account-check {profile_id, platform: bilibili}`：
- platform_account_id: 3706971620379308 | name: 游戏魔王嘟嘟 | login_status: normal
- check_items（5-8）：platform_login=pass、account_match=pass、verification_needed=na（骨架）、account_restricted=na（骨架）

## 验证 2：Cloud 应用合并 + 持久化 8 项（经运行中 Cloud API）

- 创建账号（bilibili/game1，business_status=draft）
- `POST /media-accounts/:id/check/result` 传真实 check_items → errcode 0
- 读取账号确认：
  - **check_items 8 项**：
    1. [pass] 比特浏览器账号匹配
    2. [pass] 绑定窗口存在
    3. [na] 窗口代理正常（代理管理未接入 M2-C）
    4. [na] 代理到期/停用（代理管理未接入 M2-C）
    5. [pass] 平台登录状态
    6. [pass] 登录账号与台账一致
    7. [na] 需验证码/安全验证（需真实受限账号样本对齐）
    8. [na] 账号限制/封号（需真实受限账号样本对齐）
  - **business_status draft → enabled**（检查成功自动升级）
  - **login_status normal**

## 结论

账号检查完整链路（Agent 识别 → check_items 5-8 → Cloud 合并 1-4 → 持久化 → 读取展示）**端到端通过**，8 项明细真实生效。

## 已知待办

- 7/8 判定：需真实受限账号样本对齐（用户暂时无法提供）
- 代理项 3/4：na，待 M2-C 代理管理接入后回接
- 完整 GUI 验收（打包 Desktop 中人工点击检查按钮）待用户执行
