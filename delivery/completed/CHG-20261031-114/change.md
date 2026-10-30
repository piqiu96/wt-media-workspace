---
id: CHG-20261031-114
parent: delivery/milestones/M2-account-runtime.md#m2-d1-maintenance
status: DONE
depends_on: []
affected_repos: ["wt-media-workspace", "wt-media-cloud"]
risk: M
---

# CHG-20261031-114：同账号多窗口正常检查与接入

## Change

按已确认规则修正“同 UID 即冲突”：同一用户的同平台 UID 可在不同窗口保留独立运营记录，身份、登录结论与 Cookie 按当前窗口维护；同窗口同平台仍唯一。其他窗口已有同 UID 仅作为详情顶部提示，列表恢复常规检查/详情操作，详情可选查看已有账号。批量已验证的同 UID 新窗口正常结算，不阻断后续项、不要求跳过、不写已有窗口。

先统一 PRD、M2-D、工程设计、ADR-0030、原型和 Cloud 提供方契约，再修改 Cloud 的唯一约束、检查/Cookie/批次结算与共用 Vue；Agent/Desktop 无受影响的 DTO/消费锁，复用原有本机协议并验证安装包，不复制业务判定。不新增账号主表/窗口关系表、合并向导或新的流程。清理旧重复状态/反向依赖及专门跳转主操作；旧错误重复结果不得直接冒充当前登录正常，须只读核实。

## Done When

- 真实数据库可保存同平台同 UID 不同窗口，仍拒绝同窗口同平台重复；UID/昵称可正常回填，同窗口真正异 UID 仍保留对照。
- 两个授权测试窗口同账号只读检查正常，可分别打开使用；详情顶部统一提示，不强制跳转；列表无查看已有账号按钮。
- 隔离测试及授权真实批量接入证明：同 UID 新窗口有正确账号关系和确认凭证、自动结算完成、后续项可继续，已有窗口关系/凭证不变；重入/重报不重放。
- 旧重复结果能只读核实并继续，不重复创建窗口或写 Cookie；覆盖历史异常、权限范围、计数与结果入口。
- 冲突当前文档、原型和旧逻辑清理；契约和消费者锁一致；定向测试、构建、最新 DMG 走查及 PR/CI 通过，保留人工复核清单。

References: docs/product/prd/详细文档/第三章_用户与账号管理.md §3.3；docs/engineering/specs/social-accounts.md；docs/decisions/0030-social-account-rebuild.md；example/proto/social-accounts/index.html。

验证事实与人工复核：见 [evidence/verification.md](evidence/verification.md)、[evidence/manual-checklist.md](evidence/manual-checklist.md)。

实施、真实验收和 PR/CI 均已完成并合入各仓 main；人工最终产品走查使用所附清单，M2-D 总体验收状态不在本次提前关闭。
