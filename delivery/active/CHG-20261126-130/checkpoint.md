# CHG130 执行检查点

## 范围与授权

- 唯一状态change.md为VERIFYING；128/129已合入，当前单执行器，无子Agent并行。用户授权编码、自测、PR修复、真实发布/DeepSeek限定内容、完整E2E和主动浏览器/安装包走查，不逐项确认。整体最终验收由用户进行；没有完成条件不能标DONE或提前合并。
- 用户/数据：仅admin、senior01、operator01；沿原凭据，不重置、不写入文档。一级类目仅游戏。本人B站18/Profile967/窗口51/UID3706971620379308；百度19/#41、20/#39、21/#34。
- 最新确认：广告95三角洲微光.mp4；B站新建及副本固定内容无需标注，旧冻结/投稿记录不回写，权利勾选独立。AI按B站自然玩家表达/百度信息标题，去尾部源平台活动标签/引流、避免复制互动问句，不编造赛季/手游/战绩，不以广告作正片主题。
- 107保存零正式任务/占用；108启动原子建单/占用/授权；109执行后冻结、原10%推进与原批快捷操作。只走正常业务接口，不SQL修改业务事实。

## 当前源与运行组合

- Cloud55ca11c（含f05baae标题检索、ec79164普通/风格、bb9b9e6副本/源标签清理及55换平台清配置）；Agent58f8102；Desktop31fd8e1。工作分支均chg/CHG-20261126-130。
- 最新正确配置完整all exit0：WT_MEDIA_CLOUD_CONFIG_PATH=/tmp/chg130-cloud-config python3 scripts/dev/local_env.py all --force-restart；日志/tmp/chg130-weiguang-delivery-environment-all.log。挂载前端0.1.0+55ca11c.dirty，dirty仅未提交的他人原型，sidecarSHA256=5e1340e6747d91e1646f4a0729d1b8d1e05b9fe6cda5eeb81d96b89461308b49；最终包原路径target/release/bundle/dmg/起飞_0.1.0-local.31fd8e1950_aarch64.dmg。01:10安装版原运营正常登录，三项工作环境正常。
- 私有B站测试配置必须保留上述环境变量，默认生产开关仍false。单独verify无Sidecar key的ownership拒绝不是完整all通过证据，不反复重建来绕过保护。
- 保留Cloud web/example大量非本人改动与Workspace docs/design六文件，不暂存/还原/覆盖；只显式暂存本CHG路径。

## 真实业务结果

- 最新广告95：230741877字节、27.033秒/8K/音轨，SHA9c24396e88af86a6d14c1cb585b5d9273cf0831ce9a1f135b6f6fb24d25febee。正常admin更新1016顶层/全部输出；旧成片快照不回写。
- 新batch78/task754首次成功output153；源200/80.6秒＋广告27.033＋片尾6减交叠0.6=113.033秒，120是上限。实际视频SHA03f9ff5713c8193a280e1d0414e25fa001c13f7f2def03e9b5aaa55c5b08b512核对，20/65/110秒实际广告/正片/片尾图已实看，四段时间线无intro并从原插入点续播。广告中段PCM相关0.9540183，仅客观比对、不冒称主观听音。
- 153正常真实AI、asset7实际65秒游戏帧、双封面113/114均审阅通过。task30/attempt82一次投稿，普通声明、rightsfalse，受理117683798410574；01:04:38原自动检查published，实际pub00:59:45、work16、verification_requiredfalse，无人工补录/重投。最终安装版实查标题/简介/标签/普通声明、原UID、双封面、作品16→任务30回链；当前停在30详情，没有未保存的旧150走查输入。
- Plan4（旧网站广告56）原14/15→28/80、29/81，两条自动公开2/2、缺口0，系统正常自动推进；已正常finish为ended/achieved，仅复制/详情，最终安装版已核对。不得将它当95新广告两批验收。
- 原Plan3两次真实标签拒绝，无投稿，已正常unmet结束0/2/缺口2，原26/27历史保留，不重试。B站21/25经主动公开页核对后人工补录work12/13，不称自动成功，不重投。
- 百度batch12已结束target2/created2/published2/shortfall0：23/62公开8351506294205442839、24/60公开7277548266066867187；原生/Chrome正片、24PIP/片尾实查。22/56受理1882910900152502022但旧自动停止待核实，未证明公开，不重投/不补造结果。旧18/19放弃、20诊断取消，保留历史。
- 55换平台真实API核查Plan5/16、17：16从B站完整配置切百度后全部清账号/成片/候选/封面，重新保存百度成功、任务0，正常cancel5为ended；仅配置核查，无新投稿。

## 验证与PR

- 最新publish四包PASS；隔离MySQL标题检索7场景及权限PASS，换平台双向清配置/同平台目标保留及既有骨架约束PASS2.03秒。200发布Vue PASS，完整173文件1277Web PASS39.93秒；一次并发打包导致旧导入检查超5秒，限制2worker完整复验通过，未改断言或超时。文档/Delivery/master/M0检查PASS。
- 资源下载升序旧FAIL→19准备/997Agent单测PASS；公开bootstrap绑定旧FAIL→3浏览器用例、43完整B站浏览器PASS；广告持续下载旧FAIL→6定向及production/jobs/storage/完整业务模块Go PASS。既有百度52浏览器PASS，均见evidence。
- 真实AI首轮仍带原标签/问句不计质量通过，强化后B站/百度实际建议经核对；一次百度item_error未采用，明确字数预算后正常重新生成成功，无自动重放，不称零失败。
- PR：Agent21、Cloud59、Desktop20、Workspace72均open未合并。Cloud五条审查含4711312816及标题搜索均已修复并resolve；Agent八条旧讨论已resolve。Agent58/Desktop31 CI已PASS，Cloud55最新run45863579211已PASS12分15秒；不得冒称最新代码已独立review。

## 下一步与工具边界

1. 跟进最新CI/PR，补最终55安装版和源组合证据；按工具允许范围尝试本次精确公开作品主动浏览器检查，完整私有平台后台/主观听音未证明不能伪造。
2. 仍需满足CHG验收矩阵，完成各仓main merge commit、本地main确认和最终main新包组合；当前不得DONE/归档。
3. CUA此前拒绝私有BitBrowser平台页和某次Chrome当前URL；不以临时CDP/Playwright/私有Cookie读取绕过。正常产品Runner/API和隔离测试允许。最新原生起飞走查正常，CUA活动已结束，没有手动接管等待。后续公共原稿若也被工具拒绝，保留具体未验项，不绕过。
4. 私有证据根相邻.local/m2b/chg130-new-data；API helper /tmp/chg130_api.py（不输出凭据），8188/api/v1；attempt为/publication/:id/attempt。新微光证据weiguang-*，当前public task30/work16/aid117683798410574。起飞在相邻.local/m2b/desktop-review-mount/起飞.app。中文输入用paste。
