const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const path=require('node:path');
const fs=require('node:fs');
const base=process.cwd();
const url=pathToFileURL(path.join(base,'example/common/index.html')).href;
const evidence=path.join(base,'delivery/active/CHG-20261028-099/evidence/frontend-examples');
fs.mkdirSync(evidence,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 const page=await browser.newPage({viewport:{width:1600,height:1000},deviceScaleFactor:1});
 const errors=[],network=[],checks=[];
 page.on('pageerror',e=>errors.push(e.message));
 page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 page.on('request',r=>{if(!r.url().startsWith('file:'))network.push(r.url())});
 const ok=(name,condition=true)=>{assert.ok(condition,name);checks.push(name)};
 const scene=async s=>{await page.goto(url+'#'+s);await page.locator('[data-scene="'+s+'"]').waitFor({state:'visible'});};
 const close=async()=>{await page.locator('dialog[open]').last().locator('[data-close]').first().click()};
 const box=()=>page.locator('dialog[open]').last().boundingBox();
 const fit=async name=>{
   const d=await page.evaluate(()=>({w:innerWidth,s:document.documentElement.scrollWidth}));
   ok(name+'：页面无横向溢出',d.s<=d.w+1);
 };
 await scene('list');
 ok('离线加载8行',await page.locator('[data-resource-row]:visible').count()===8);
 ok('每行5个文字动作',await page.locator('[data-resource-row]').first().locator('.ex-row-actions button').count()===5);
 await page.locator('[data-row-check]').first().check();
 ok('选择工具栏出现',await page.locator('[data-selection]').isVisible());
 await page.getByRole('button',{name:'高级筛选',exact:true}).click();
 await page.locator('#list-group').selectOption('备用账号组',{force:true});
 await page.locator('[data-filter-form]').getByRole('button',{name:'查询',exact:true}).click();
 ok('高级分组筛选有效',await page.locator('[data-resource-row]:visible').count()===3);
 await page.locator('[data-filter-form]').getByRole('button',{name:'重置',exact:true}).click();
 await page.locator('#list-search').fill('没有这个窗口');
 await page.locator('[data-filter-form]').getByRole('button',{name:'查询',exact:true}).click();
 ok('无匹配只呈现恢复空态',await page.locator('[data-list-empty]').isVisible());
 await page.getByRole('button',{name:'清除筛选',exact:true}).click();
 ok('重置恢复8行',await page.locator('[data-resource-row]:visible').count()===8);
 await page.screenshot({path:path.join(evidence,'list-1600.png'),fullPage:true});
 // 短表单名称校验、内容保留、实际radio键盘、非业务保存。
 await page.getByRole('button',{name:'新增窗口',exact:true}).click();
 let dialog=page.locator('dialog[open]').last();
 ok('短Dialog宽560',Math.round((await box()).width)===560);
 await dialog.getByRole('button',{name:'保存演示输入'}).click();
 ok('空名称就近报错',await dialog.locator('#window-name-error').isVisible());
 await dialog.locator('#window-name').fill('新原型测试窗口');
 await dialog.locator('#window-note').fill('保留的输入');
 await dialog.locator('input[value="self"]').focus();await page.keyboard.press('ArrowRight');
 ok('卡片使用真实键盘单选',await dialog.locator('input[value="managed"]').isChecked());
 await dialog.getByRole('button',{name:'保存演示输入'}).click();
 ok('保存只给本地演示回执',await dialog.locator('[data-form-receipt]').isVisible());
 ok('保存后保留内容',await dialog.locator('#window-note').inputValue()==='保留的输入');
 await dialog.locator('#window-note').fill('再次编辑');
 ok('再次编辑清除旧回执',!(await dialog.locator('[data-form-receipt]').isVisible()));
 await page.screenshot({path:path.join(evidence,'short-dialog-1600.png')});
 await close();
 ok('关闭返回原入口焦点',await page.getByRole('button',{name:'新增窗口',exact:true}).evaluate(e=>e===document.activeElement));
 // 勾选后的演示过程必须保持所选范围。
 await page.locator('[data-row-check]').first().check();
 await page.locator('[data-selection]').getByRole('button',{name:'批量检测代理'}).click();
 dialog=page.locator('dialog[open]').last();
 ok('批量演示尊重所选1项',await dialog.locator('[data-metric="总数"] strong').textContent()==='1');
 await dialog.getByRole('button',{name:'推进到结果'}).click(); await close();
 // 内容宽度和密度共同决定详情布局。
 await scene('details');
 const columns=()=>page.locator('#detail-preview .ex-description-list').evaluate(e=>getComputedStyle(e).gridTemplateColumns.split(' ').length);
 ok('800容器密集字段双列',await columns()===2);
 await page.locator('#detail-width').selectOption('560',{force:true});ok('560容器自然单列',await columns()===1);
 await page.locator('#detail-width').selectOption('800',{force:true});await page.locator('#detail-density').selectOption('sparse',{force:true});
 ok('宽容器稀疏字段仍单列',await columns()===1);
 await page.locator('#detail-density').selectOption('dense',{force:true});
 ok('长字段满行',await page.locator('#detail-preview .ex-desc-item.full').first().evaluate(e=>getComputedStyle(e).gridColumn)==='1 / -1');
 await page.screenshot({path:path.join(evidence,'detail-adaptive-1600.png'),fullPage:true});
 await page.getByRole('button',{name:'查看详情 Drawer'}).click();
 ok('只读详情Drawer宽800',Math.round((await box()).width)===800);
 ok('只读详情无Footer',await page.locator('dialog[open] .ex-overlay-footer').count()===0);await close();
 // 资源选择嵌套回退保留输入和选择。
 await scene('overlays');
 await page.getByRole('button',{name:'可用与不可用资源'}).click();
 dialog=page.locator('dialog[open]').last();
 ok('资源选择宽960',Math.round((await box()).width)===960);
 await dialog.locator('#picker-q').fill('沪线');
 await dialog.locator('input[name="proxy-choice"]').first().check();
 await dialog.getByRole('button',{name:'详情',exact:true}).click();
 ok('少量代理信息当前层展开',await page.locator('dialog[open]').count()===1 && await dialog.locator('[data-proxy-preview]').isVisible());
 await dialog.getByRole('button',{name:'查看完整代理详情',exact:true}).click();
 ok('完整详情嵌套两层',await page.locator('dialog[open]').count()===2);
 ok('下层不重复加深遮罩',await page.locator('dialog.ex-underlay').count()===1);
 await close();dialog=page.locator('dialog[open]').last();
 ok('嵌套返回保留搜索',await dialog.locator('#picker-q').inputValue()==='沪线');
 ok('嵌套返回保留选择',await dialog.locator('input[name="proxy-choice"]').first().isChecked());
 ok('不可用资源真实禁用',await dialog.locator('input[value="沪线 · 静态02"]').isDisabled());
 await dialog.locator('#picker-q').fill('no-match');ok('选择器筛选空态',await dialog.locator('[data-picker-empty]').isVisible());
 await dialog.getByRole('button',{name:'清除筛选'}).click();
 await dialog.getByRole('button',{name:'演示应用代理'}).click();ok('演示应用关闭容器',await page.locator('dialog[open]').count()===0);
 await page.getByRole('button',{name:'空资源',exact:true}).click();
 ok('空资源宽560',Math.round((await box()).width)===560);
 await close();
 await page.getByRole('button',{name:'复杂详情 · 960px'}).click();
 ok('复杂详情Drawer宽960',Math.round((await box()).width)===960);await close();
 // 长配置组合与错误保存。
 await scene('forms');await page.getByRole('button',{name:'新建代理',exact:true}).click();
 dialog=page.locator('dialog[open]').last();
 ok('长Drawer宽800',Math.round((await box()).width)===800);
 ok('长表单相关短字段双列',await dialog.locator('.ex-form-grid').first().evaluate(e=>getComputedStyle(e).gridTemplateColumns.split(' ').length)===2);
 await dialog.getByRole('button',{name:'保存演示输入'}).click();
 ok('长表单就近名称校验',await dialog.locator('[data-name-error]').isVisible());await close();
 await page.getByRole('button',{name:'组合短表单 · 640px'}).click();
 dialog=page.locator('dialog[open]').last();
 ok('组合短Dialog宽640',Math.round((await box()).width)===640);
 ok('640短Dialog相关字段双列',await dialog.locator('.ex-form-grid').evaluate(e=>getComputedStyle(e).gridTemplateColumns.split(' ').length)===2);await close();
 // 批量7指标对应6类互斥状态；操作不串类。
 await scene('batch');
 for(const c of ['processing','success','failed','partial','uncertain','interrupted']) {
  await page.locator('#batch-case').selectOption(c,{force:true});
  const counts=await page.locator('[data-batch-preview] [data-metric] strong').allTextContents();
  ok(c+'计数互斥且总数8',Number(counts[0])===8 && counts.slice(1).reduce((sum,x)=>sum+Number(x),0)===8);
 }
 await page.getByRole('button',{name:'打开处理过程'}).click();dialog=page.locator('dialog[open]').last();
 await page.keyboard.press('Escape');ok('处理中Esc关闭被阻断',await page.locator('dialog[open]').count()===1);
 ok('处理中X禁用',await dialog.locator('.ex-close').isDisabled());
 await dialog.getByRole('button',{name:'推进到结果'}).click();
 ok('结果后可关闭',!(await dialog.locator('.ex-close').isDisabled()));
 const before=await dialog.locator('[data-metric="待确认"] strong').textContent();
 await dialog.getByRole('button',{name:'演示重试失败项'}).click();
 ok('重试只处理失败项',await dialog.locator('[data-metric="失败"] strong').textContent()==='0' && await dialog.locator('[data-metric="待确认"] strong').textContent()===before);
 await page.screenshot({path:path.join(evidence,'batch-result-1600.png')});
 await dialog.getByRole('button',{name:'演示核实待确认项'}).click();
 ok('待确认独立核实',await dialog.locator('[data-metric="待确认"] strong').textContent()==='0');await close();
 // 各模式和状态在三类视口中不导致页面横向溢出。
 for(const viewport of [{width:1600,height:1000},{width:1366,height:900},{width:390,height:844}]) {
  await page.setViewportSize(viewport);
  for(const s of ['list','details','forms','overlays','feedback','batch','foundations']) { await scene(s);await fit(viewport.width+'-'+s); }
  await scene('feedback');for(const c of ['empty','filtered','unavailable','error','denied','loading']) {await page.locator('#empty-case').selectOption(c,{force:true});await fit(viewport.width+'-feedback-'+c);}
  await scene('list');await page.getByRole('button',{name:'新增窗口',exact:true}).click();
  const b=await box();ok(viewport.width+'-弹窗受视口约束',b.x>=0 && b.y>=0 && b.x+b.width<=viewport.width+1 && b.y+b.height<=viewport.height+1);
  dialog=page.locator('dialog[open]').last();await dialog.locator('#window-name').fill('窄屏演示');await dialog.getByRole('button',{name:'保存演示输入'}).click();
  ok(viewport.width+'-弹窗操作可达',await dialog.locator('[data-form-receipt]').isVisible());
  if(viewport.width===390)await page.screenshot({path:path.join(evidence,'short-dialog-390.png')});await close();
  await scene('forms');await page.getByRole('button',{name:'新建代理',exact:true}).click();
  dialog=page.locator('dialog[open]').last();
  await dialog.getByRole('button',{name:'保存演示输入'}).click();
  ok(viewport.width+'-长抽屉Footer可达',await dialog.locator('[data-name-error]').isVisible());
  if(viewport.width===390)ok('窄抽屉相关字段退单列',await dialog.locator('.ex-form-grid').first().evaluate(e=>getComputedStyle(e).gridTemplateColumns.split(' ').length)===1);
  await close();
 }
 // 结构可查看/复制；独立起始页无目录依赖。
 await page.setViewportSize({width:1366,height:900});await scene('forms');
 await page.getByRole('button',{name:'查看 / 复制结构'}).click();
 ok('结构查看包含模式内容',(await page.locator('#example-code').inputValue()).includes('ex-form-container'));
 await page.getByRole('button',{name:'复制结构',exact:true}).click();
 ok('复制提供实际结果或手动恢复',!!(await page.locator('[data-copy-status]').textContent()));await close();
 await page.goto(pathToFileURL(path.join(base,'example/proto/starter.html')).href);
 await page.getByRole('button',{name:'新建资源'}).click();
 await page.locator('#resource-name').fill('业务原型资源');
 await page.getByRole('button',{name:'保存演示输入'}).click();
 ok('原型起始页共用资源并独立运行',await page.locator('[data-form-receipt]').isVisible());await close();
 ok('无外部网络依赖',network.length===0);ok('无脚本或资源控制台错误',errors.length===0);
 fs.writeFileSync(path.join(evidence,'browser-results.json'),JSON.stringify({checkedAt:new Date().toISOString(),browser:await browser.version(),checks:checks.length,results:checks,errors,network},null,2)+'\n');
 console.log(JSON.stringify({checks:checks.length,errors,network,evidence},null,2));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
