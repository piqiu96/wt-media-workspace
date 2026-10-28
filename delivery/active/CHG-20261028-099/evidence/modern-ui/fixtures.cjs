const proxies=[{id:3,name:'沪线 · 日常运营',team_id:1,team_name:'星河运营组',source_type:'static',proxy_protocol:'socks5',host:'203.0.113.18',port:1080,business_status:'active',last_check_result:'ok',last_check_at:'2026-10-28T10:32:00+08:00',assigned_profile_count:2,max_profile_count:8,remaining_profile_count:6,region:'上海',supplier:'星云网络',remark:'主力线路，每周检查可用性',tags:['华东'],username:'demo_operator',password:'example-only'},{id:5,name:'沪线 · 备用线路',team_id:1,team_name:'星河运营组',source_type:'static',proxy_protocol:'socks5',host:'203.0.113.52',port:1080,business_status:'active',last_check_result:'conn_failed',assigned_profile_count:1,max_profile_count:6,remaining_profile_count:5,region:'上海',supplier:'星云网络',remark:'先检测，再分配窗口',tags:[]},{id:8,name:'粤线 · 动态代理',team_id:1,team_name:'星河运营组',source_type:'api',proxy_protocol:'http',host:'198.51.100.35',port:9090,business_status:'paused',last_check_result:'ok',assigned_profile_count:0,max_profile_count:3,remaining_profile_count:3,region:'广州',supplier:'云桥网络',remark:'活动备用线路',expires_at:'2026-10-26T23:59:00+08:00',tags:['动态']}];
const profiles=[{id:328,name:'B站主号 · 上海01',group_name:'主力账号组',bit_profile_id:'bit-328',user_id:1,team_id:1,team_name:'星河运营组',proxy_id:3,proxy_type:'socks5',proxy_host:'203.0.113.18',proxy_port:1080,local_status:'active',business_status:'enabled',last_synced_at:'2026-10-28T10:32:00+08:00',remark:'创作专用窗口',cloud_remark:'每日发布前检查账号状态'},{id:332,name:'B站备用 · 华东03',group_name:'备用账号组',bit_profile_id:'bit-332',user_id:1,team_id:1,team_name:'星河运营组',proxy_id:5,proxy_type:'socks5',proxy_host:'203.0.113.66',proxy_port:1080,local_status:'active',business_status:'enabled',last_synced_at:'2026-10-28T10:32:00+08:00',cloud_remark:'代理变更后请先核实'},{id:335,name:'百家号 · 广州01',group_name:'华南账号组',bit_profile_id:'bit-335',user_id:1,team_id:1,team_name:'星河运营组',proxy_id:null,proxy_type:'noproxy',local_status:'active',business_status:'disabled',last_synced_at:'2026-10-28T10:32:00+08:00',cloud_remark:'活动结束后停用，资料保留'}];
const accounts=[{id:208,name:'星河玩游戏',platform:'bilibili',browser_profile_id:328,login_status:'normal',platform_account_id:'star-game'},{id:216,name:'星河游戏资讯',platform:'baidu',browser_profile_id:328,login_status:'normal'},{id:220,name:'星河观察',platform:'bilibili',browser_profile_id:332,login_status:'normal'}];

async function setupPage(page,{role='senior_operator',desktop=true,checkDelay=400}={}) {
 const calls=[],attempts={};
 if(desktop)await page.addInitScript(()=>{window.__TAURI_INTERNALS__={invoke:async(cmd)=>{if(cmd==='plugin:app|version')return '0.1.0';if(cmd==='local_agent_profile_scan')return {main_user_id:'demo-main',profiles:[{bit_profile_id:'bit-328',status:'1'},{bit_profile_id:'bit-332',status:'0'},{bit_profile_id:'bit-335',status:'0'}]};if(cmd==='local_agent_profile_groups')return {groups:[{id:'g1',name:'主力账号组'}]};return {status:'running',bitbrowser_status:'normal',version:'test'}},transformCallback:()=>1};});
 await page.route('**/api/v1/**',async route=>{
  const request=route.request(),u=new URL(request.url()),p=u.pathname;calls.push({method:request.method(),path:p,body:request.postDataJSON()});let data=[];
  if(p.endsWith('/auth/me'))data={id:1,role,nickname:'陈以宁',username:'review-user',team_id:1,team_name:'星河运营组'};
  else if(p.endsWith('/browser-profiles'))data=profiles;
  else if(p.endsWith('/media-accounts'))data=accounts;
  else if(p.endsWith('/proxies'))data=proxies;
  else if(/\/proxies\/\d+$/.test(p))data=proxies.find(x=>x.id===Number(p.split('/').pop()));
  else if(p.endsWith('/bindings'))data=profiles.filter(x=>x.proxy_id===Number(p.split('/').at(-2)));
  else if(p.endsWith('/check')){const id=Number(p.split('/').at(-2));attempts[id]=(attempts[id]||0)+1;await new Promise(r=>setTimeout(r,checkDelay));data={...proxies.find(x=>x.id===id),last_check_result:id===5&&attempts[id]===1?'conn_failed':'ok',assignment_blocker:id===5&&attempts[id]===1?'连接失败，请检查线路后重试':''};}
  else if(p.endsWith('/users'))data=[{id:1,nickname:'陈以宁',role:'senior_operator',team_id:1,team_name:'星河运营组'},{id:2,nickname:'林予安',role:'operator',team_id:1,team_name:'星河运营组'}];
  else if(p.endsWith('/operation-teams'))data=[{id:1,name:'星河运营组'},{id:2,name:'晨曦运营组'}];
  else if(p.endsWith('/bit-account'))data={main_user_id:'demo-main',main_user_id_masked:'demo****main'};
  else if(p.endsWith('/discovery-strategies'))data=[{id:19,name:'游戏热点 · 日常挖掘',team_id:1,game_id:1,strategy_type:'keyword',config:{keywords:['王者荣耀','高光'],material_rules:[]},schedule:'manual',status:'enabled',updated_at:'2026-10-28T01:30:00Z',updated_by_name:'陈以宁'}];
  else if(p.endsWith('/compose-strategies'))data=[{id:26,name:'游戏高光 · 日常切片',compose_template_id:1,game_id:1,team_id:1,operator_name:'陈以宁',status:'enabled',config:{},schedule:{mode:'manual'}}];
  else if(p.endsWith('/compose-templates'))data=[{id:1,name:'高光混剪',version:1,status:'enabled',schema:{}}];
  else if(p.endsWith('/games'))data=[{id:1,name:'王者荣耀',status:'enabled'}];
  else if(p.endsWith('/import/preview'))data={rows:[{line:1,raw:'203.0.113.101:1080',parsed:{host:'203.0.113.101',port:1080}},{line:2,raw:'203.0.113.102:1080',parsed:{host:'203.0.113.102',port:1080}},{line:3,raw:'203.0.113.18:1080',duplicate:true,duplicate_reason:'团队已存在相同资源',parsed:{host:'203.0.113.18',port:1080}}]};
  else if(p.endsWith('/import')){await new Promise(r=>setTimeout(r,checkDelay));const rows=request.postDataJSON().rows;data={imported:rows.filter(x=>x.selected).length,skipped:rows.filter(x=>!x.selected).length,failed:0,rows:rows.map(x=>({line:x.line,status:x.selected?'imported':'skipped',reason:x.selected?'已创建':'未选择或重复'}))};}
  else if(p.endsWith('/parse'))data={proxy_protocol:'socks5',host:'203.0.113.101',port:1080,username:'',password:''};
  else if(request.method()!=='GET')return route.fulfill({status:400,json:{errcode:400,message:'隔离评审未定义此写入场景',data:null}});
  await route.fulfill({json:{errcode:0,message:'success',data,logid:'isolated-ui-review'}});
 });
 return calls;
}
module.exports={proxies,profiles,accounts,setupPage};
