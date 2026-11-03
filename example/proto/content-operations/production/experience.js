/* 在既有生产能力上补齐体验；新增关联只用于本地原型，不代表后端字段。 */
(() => {
  const C=CP,O=OPS,{copy,table}=C.prod;
  if(!C.db.productionRevision){
    C.db.usages={陈小雨:(C.db.mine||[]).map(materialId=>({materialId,status:'active',download:'notDownloaded',added:'10-31 09:00'})),林予安:[{materialId:104,status:'active',download:'downloaded',added:'10-30 10:00'}]};
    if(!C.db.usages.陈小雨.some(u=>u.materialId===105))C.db.usages.陈小雨.push({materialId:105,status:'removed',download:'missing',added:'10-29 10:00'});
    C.db.strategies.forEach(s=>Object.assign(s,{executionMode:s.auto||s.schedule.includes('每天')?'scheduled':'manual',scheduleMode:'daily',dailyTime:'09:00',interval:60,timeZone:'Asia/Shanghai',singleLimit:3,dailyLimit:12,team:'内容运营一组',templateVersion:'v1',rules:[{action:'match',logic:'all',conditions:[{field:'likes',operator:'gte',value:3000}]}]}));
    C.db.tasks.forEach(t=>{t.snapshot={strategyName:C.get('strategies',t.strategyId)?.name,template:C.get('strategies',t.strategyId)?.template,...copy(t.version)};t.finished=t.status==='success'?'10-30 14:20':'—';t.error=t.status==='failed'?'合成中断，未生成成片。可在检查素材后重试。':'';});
    C.db.runs=[];C.db.productionRevision=4;C.save();
  }
  C.canManage=()=>O.actor==='陈小雨';
  C.usages=(owner=O.actor)=>C.db.usages[owner]||=[];
  C.usage=(id,owner=O.actor)=>C.usages(owner).find(x=>x.materialId===id);
  C.mine=()=>C.db.materials.filter(m=>C.usage(m.id)?.status==='active');
  C.join=(ids,owner=O.actor)=>{ids.forEach(id=>{const u=C.usage(id,owner);if(u)u.status='active';else C.usages(owner).push({materialId:id,status:'active',download:'notDownloaded',added:'11-01 09:00'});});C.save();};
  C.downloadText=s=>({notDownloaded:'未下载',downloading:'下载中',downloaded:'已下载',failed:'下载失败',missing:'文件缺失',unverified:'待校验'})[s]||'未下载';
  C.batchKey=t=>t.runKey?'run:'+t.runKey:t.batchId||'single:'+t.id;
  C.batchRows=key=>C.db.tasks.filter(t=>C.batchKey(t)===key);
  C.time=()=>new Date().toLocaleString('sv-SE',{timeZone:'Asia/Shanghai'}).slice(5,16);
  C.submitTasks=({strategy,ids,vs,owner,trigger='人工创建',name,runKey,followup,replicationId})=>{
    const batchId=C.id(),created=C.time(),made=[];
    ids.forEach(materialId=>vs.forEach(v=>{for(let n=1;n<=v.qty;n++){
      const t={id:C.id(),materialId,strategyId:strategy.id,name:v.name+(v.qty>1?' · 第'+n+'份':''),batch:name||strategy.name+' · '+created,batchId,runKey,status:'pending',owner,version:copy(v),snapshot:{strategyName:strategy.name,template:strategy.template,guideUrl:strategy.guideUrl||strategy.intro||'',...copy(v)},created,trigger,attempt:1,finished:'—',followup:followup||'',replicationId:replicationId||null,events:[{text:'任务已创建',time:created}]};C.db.tasks.unshift(t);made.push(t.id);
    }}));C.save();return made;
  };
  C.filterProduction=type=>{
    const f=C.read(),strategy=C.select('strategy','合成策略',f.strategy,C.db.strategies.map(s=>[s.id,s.name])),owner=C.select('operator','负责人',f.operator,O.peopleOptions()),category=C.select('category','类目',f.category,O.categories),dates=C.field('创建日期起','from',f.from,{type:'date'})+C.field('创建日期止','to',f.to,{type:'date'}),trigger=C.select('trigger','创建方式',f.trigger,['人工创建','策略执行','策略自动']);
    const primary=type==='strategies'?category+C.select('status','状态',f.status,[['enabled','启用'],['disabled','停用']])+owner:type==='tasks'?C.select('status','任务状态',f.status,[['pending','排队中'],['running','运行中'],['success','已完成'],['failed','失败'],['cancelled','已取消']])+strategy+owner:category+C.select('platform','适用平台',f.platform,O.platforms)+C.select('availability','发布情况',f.availability,[['available','可发布'],['reserved','已安排'],['published','已发布']]);
    const more=type==='tasks'?category+trigger+dates:strategy+owner+trigger+C.select('download','下载状态',f.download,[['downloaded','已下载'],['notDownloaded','未下载']])+dates;
    return `<form class="ex-filters" data-list-filter>${C.field('综合搜索','q',f.q,{placeholder:'名称 / 素材 / ID'})}${primary}<button class="ex-button primary" type="submit">查询</button>${C.btn('重置',()=>{C.ui.filters[C.route]=null;C.ui.page=1;C.ui.selected.clear();C.render();})}${type==='strategies'?'':`<details class="ops-more-filters" ${f.from||f.to||f.trigger||f.download||f.category&&type==='tasks'||f.strategy&&type==='outputs'||f.operator&&type==='outputs'?'open':''}><summary>高级筛选</summary><div class="ops-filter-grid">${more}</div></details>`}</form>`;
  };
  C.match=(x,type)=>{const f=C.read(),t=type==='tasks'?x:C.get('tasks',x.taskId),s=type==='strategies'?x:C.get('strategies',t?.strategyId),m=C.get('materials',x.materialId),date='2026-'+(x.created||x.date||'').slice(0,5);return (!f.availability||x.platforms?.some(p=>(!f.platform||f.platform===p)&&(f.availability==='available'?O.availability(x.id,p).ok:O.availability(x.id,p).text===(f.availability==='reserved'?'已安排':'已发布'))))&&(C.canManage()||(x.owner||s?.operator)===O.actor)&&(!f.q||`${x.id} ${x.name} ${x.batch||''} ${m?.title||''}`.includes(f.q))&&(!f.category||(m?.category||s?.category)===f.category)&&(!f.strategy||s?.id===+f.strategy)&&(!f.operator||(x.owner||s?.operator)===f.operator)&&(!f.status||(type==='strategies'?(x.enabled?'enabled':'disabled'):x.status)===f.status)&&(!f.platform||x.platforms?.includes(f.platform))&&(!f.trigger||t?.trigger===f.trigger)&&(!f.download||(x.downloaded?'downloaded':'notDownloaded')===f.download)&&(!f.from||date>=f.from)&&(!f.to||date<=f.to);};
  C.notice='';C.noticeHTML=()=>C.notice&&C.noticeRoute===C.route?`<div class="ops-result" role="status">${C.notice}</div>`:'';
})();
