const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});const page=await browser.newPage({viewport:{width:1600,height:1000},deviceScaleFactor:1});
 const url='file://'+process.cwd()+'/example/common/index.html',checks=[],failures=[],errors=[];
 page.on('pageerror',e=>errors.push(e.message)); const check=(n,b)=>{checks.push(n);if(!b)failures.push(n)};
 await page.goto(url+'#list');const first=page.locator('[data-resource-row]').first(),actions=first.locator('.ex-row-actions');
 check('主要行操作位于首位',await actions.locator('button').first().innerText().then(s=>s.includes('打开')));
 const main=actions.getByRole('button',{name:'打开',exact:true});
 const before=await main.evaluate(e=>({bg:getComputedStyle(e).backgroundColor,height:e.getBoundingClientRect().height}));
 check('主要动作浅蓝底且32px热区',before.bg==='rgb(234, 241, 252)'&&before.height>=32);
 const edit=actions.getByRole('button',{name:'编辑',exact:true});
 check('次动作清晰品牌蓝',await edit.evaluate(e=>getComputedStyle(e).color)==='rgb(0, 82, 217)');
 await edit.hover();check('次动作悬停有浅蓝背景',await edit.evaluate(e=>getComputedStyle(e).backgroundColor)==='rgb(234, 241, 252)');
 check('停用默认深色',await actions.getByRole('button',{name:'停用',exact:true}).evaluate(e=>getComputedStyle(e).color)==='rgb(38, 52, 73)');
 const disabled=page.locator('[data-resource-row]').nth(5).getByRole('button',{name:'打开',exact:true});check('禁用保持真实不可执行',await disabled.isDisabled());
 const dir=path.join(process.cwd(),'delivery/active/CHG-20261028-099/evidence/row-action-priority');fs.mkdirSync(dir,{recursive:true});
 if(!failures.length){
   await page.screenshot({path:path.join(dir,'list-1600.png'),fullPage:true});
   for(const viewport of [{width:1366,height:900},{width:390,height:844}]){
    await page.setViewportSize(viewport);await page.goto(url+'#list');
    check(viewport.width+'页面无横向溢出',await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
   }
   await page.setViewportSize({width:1600,height:1000});await page.goto(url+'#foundations');
   const groups=page.locator('#scene-foundations .ex-row-actions');
   check('5项操作仍全平铺',await groups.first().locator('button').count()===5);
   const more=page.locator('[data-menu-trigger]');check('更多为蓝色且热区32px',await more.evaluate(e=>getComputedStyle(e).color==='rgb(0, 82, 217)'&&e.getBoundingClientRect().height>=32));
   await page.screenshot({path:path.join(dir,'actions-1600.png'),fullPage:true});
   await more.click();check('更多菜单仍可用',await page.locator('[data-menu-popup]').evaluate(e=>e.matches(':popover-open')));
   await page.keyboard.press('Escape');check('菜单关闭恢复焦点',await more.evaluate(e=>e===document.activeElement));
 }
 check('无脚本错误',!errors.length);
 const result={checks:checks.length,results:checks,failures,errors,checkedAt:new Date().toISOString()};
 console.log(JSON.stringify(result,null,2));
 fs.writeFileSync(path.join(dir,failures.length?'red-results.json':'results.json'),JSON.stringify(result,null,2)+'\n');
 await browser.close();if(failures.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
