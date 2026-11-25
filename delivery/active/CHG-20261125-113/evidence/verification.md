# CHG113 详情验收

## 数据与原型差距

2026-11-25只读SQL：批次1为QA CHG107 配置保存1125-015314，已取消、started_at为空、目标三角洲60、candidates_count及JSON候选长度均0、task0；批次2才是目标60/候选1/task1且已结束。截图不是60条内容丢失。

固定原型9305532的BatchDetailContent/BatchContentTable以四列只读内容展示；正式BatchReadonlyBody另写原生六列表，无空态、无分页，额外堆积目标/缺口；取消前未启动也显示执行统计并重复执行设置。按原框架修复这些差异，批次目标、候选和task事实均保留。

新增生产路由浏览器先失败：未开始即取消仍显示执行情况，1!=0（/tmp/chg113-detail-before.log）。修复共享主体用于独立详情及计划Drawer，验证结果收齐后在此记录，不把既有测试数量当作本次详情已验收。

## 自测与受控浏览器

生产详情矩阵12类全部PASS（/tmp/chg113-detail-final.log）：未开始即取消且零内容、未开始零内容、config缺失不伪造0、未完善内容、13条分页及超长名称、多类目守恒明细、占用、资源目录失败、running/paused/stopping/ended。1440与390宽验证只读四列、无变更命令、文本夹行/完整title、空态及执行设置不重复。

计划详情三角色Drawer与返回位置PASS（/tmp/chg113-plan-drawer.log）；G1计划骨架配置/冻结及正式任务回链PASS（/tmp/chg113-plan-g1.log）。完整批次与112向导8组、执行baseline及列表状态/跨成员回归PASS（/tmp/chg113-batch-regression.log、/tmp/chg113-wizard-regression.log、/tmp/chg113-execution-regression.log、/tmp/chg113-list-regression.log）。本次Web168文件1244项PASS（/tmp/chg113-web-tests.log）。

生产源码提交bf6b2d1；新安装包与实际原数据走查正在完成，尚不以受控fixture认定安装版已通过。

## 安装版走查发现与修复

第一次新DMG只读走查operator01：原批次1取消前未启动，取消原因清晰、60/0/60/0真实数量保留，空态不再显示原生六列表头，无重复目标区及虚假执行统计；批次2首次执行时间及正式任务12/真实公开1条保留。误点列表组合AX单元格进入复制后立即返回，未保存任何业务对象。

已执行批次操作记录另发现publication_batch.group_assigned/ended直接泄露技术事件，统一为安排本组任务/批次执行结束；共享格式器亦覆盖组结束、终止落定和计划骨架，未知事件显示批次业务记录，不暴露原始事件。提交9da63af。新12类浏览器增加实际record API中文断言后PASS（/tmp/chg113-detail-records.log）；最后Web168文件1244测试PASS（/tmp/chg113-web-final.log），Cloud构建PASS（/tmp/chg113-cloud-build-final.log）。

最终环境强制重启、重新build-dmg、wt.py chg verify113全部PASS（/tmp/chg113-environment-final.log、/tmp/chg113-chg-verify-final.log）。正式verify含Go模块、Workspace220测试、Cloud/Agent/BitBrowser/双dev/新鲜资源/DMG/CORS与operator01真实登录。先校验再launch转交Agent，未绕过Desktop凭证保护。

Cloud PR56：https://github.com/piqiu96/wt-media-cloud/pull/56；Workspace PR69：https://github.com/piqiu96/wt-media-workspace/pull/69。最终源码9da63af30324880690c2a4810b1d2d38b162fa2a；DMG SHA256 bf9621679e97c47bed4b1aa809ae01231a7df7d702f8cefd3cb176637931ccf9。最终安装版复核及远端CI仍待完成。

## 最终安装版结果

已挂载且实际启动0.1.0+9da63af.dirty（dirty仅其他会话example改动），operator01/operator123登录成功。初次工作环境弹层赶在Sidecar启动完成前显示未连接，点击重新检查即三项全绿：本机服务已连接、比特浏览器已登录指定账号、执行凭证已配置，这台电脑可以工作。

实际只读走查PASS：计划2→批次5详情Drawer展示实际任务15、公开1/1、设置仅一次及中文创建计划批次/安排本组任务/批次执行结束；关闭回原计划2、无路由跳转。独立批次2正式任务12及中文事件全部可读。最后原批次1详情再次核对取消原因、60/0/60/0及明确空态，无裸表头/重复目标区/虚假执行区，应用保留此处供用户复查。

数据库复查仍2计划/7批次/12任务；本轮没有保存复制、新建批次、计划或发布任务，没有AI及发布调用。生产diff只含共享详情内容/记录呈现与定向回归，无Contract/DB/Agent/Desktop业务修改。自review按Done When逐项核对：原型信息结构、异常/未知、长内容/分页/窄屏、只读无副作用及正式任务投影均已测。远端最新CI正在原型交互步骤，暂不宣称合入。
