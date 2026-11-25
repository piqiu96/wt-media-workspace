# CHG128 自测与回归

- 启动预检通过，选定128，复核113已在两仓main。Cloud原型输入基线69e865c03e5c90c4c9107ee2faf2323e3f753e8a，修复c3d3a75。其他会话的未提交原型和设计改动未纳入本次提交。
- 旧普通计划路径在执行完成后仍能追加批次，新断言先失败（/tmp/chg128-before.log）。统一拒绝追加并保留原目标和批次后，原型31文件377项通过（/tmp/chg128-prototype.log）。
- 原型浏览器12项通过。新增未启动计划批次抽屉的空态、无执行统计、关闭保持原路由，详情组六项全过（/tmp/chg128-prototype-final.log、/tmp/chg128-drawer-final.log）。首次启动因缺少自带Chromium失败，选用本机Chrome复跑通过。
- 正式批次第二步显示「下一步」。Web168文件1244项通过（/tmp/chg128-web.log）。
- 受控生产路由浏览器覆盖三角色、计划范围和推进控制、返回位置、列表、单向向导、续编、12类详情、保存、启动及四种人工结果（/tmp/chg128-{plan-final,editor-list,batch-final,execution,plan-g1-final}.log）。G1首次引用旧按钮文字，更新跨页测试后复跑通过。
- 正式安装版逐页走查与远端CI仍在完成。
