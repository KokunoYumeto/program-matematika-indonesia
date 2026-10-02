/* Local headless-browser checks; no desktop window or external PDF requests. */
const assert=require('node:assert/strict');
const fs=require('node:fs/promises');
const path=require('node:path');
const http=require('node:http');
const crypto=require('node:crypto');
const playwright=require(process.env.C130_PLAYWRIGHT_PACKAGE||'playwright');
const root=path.resolve(__dirname,'..');
const base=path.join(root,'backend/course-capsule-v1/adapters/c130-teacher-v1');
const site=path.join(base,'site');
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json'};
const server=http.createServer(async(req,res)=>{
 try{
  const pathname=decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname);
  const file=path.resolve(site,'.'+pathname),relative=path.relative(site,file);
  if(relative.startsWith('..')||path.isAbsolute(relative)){res.writeHead(403);res.end();return;}
  res.writeHead(200,{'Content-Type':mime[path.extname(file)]||'application/octet-stream'});res.end(await fs.readFile(file));
 }catch{res.writeHead(404);res.end();}
});
let browser;
(async()=>{
 await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',resolve);});
 const origin='http://127.0.0.1:'+server.address().port;
 browser=await playwright.chromium.launch({headless:true,executablePath:process.env.C130_BROWSER_EXECUTABLE||undefined,args:['--disable-background-networking','--no-first-run']});
 const context=await browser.newContext({acceptDownloads:true});
 await context.route('**/*',route=>new URL(route.request().url()).origin===origin?route.continue():route.abort());
 const page=await context.newPage();page.setDefaultTimeout(12000);
 const errors=[];page.on('pageerror',error=>errors.push(error.message));
 const model=JSON.parse(await fs.readFile(path.join(site,'planner-model.json'),'utf8'));
 const checks=[];
 for(const locale of ['id','en']){
  await page.setViewportSize({width:1280,height:900});
  const suffix=locale==='en'?'.en':'';
  await page.goto(origin+'/C130.teacher'+suffix+'.html',{waitUntil:'networkidle'});
  assert.equal(await page.locator('html').getAttribute('lang'),locale);
  assert.equal(await page.locator('#questions tr').count(),227);
  const supplement=page.locator('main > details').last();
  await supplement.locator(':scope > summary').click();
  const links=supplement.locator('li > a.reader-reference');
  assert.equal(await links.count(),132);
  const observed=await links.evaluateAll(elements=>elements.map(a=>({page:Number(a.dataset.page),href:a.href,text:a.textContent})));
  assert.deepEqual(observed.map(a=>a.page),model.supplementary_solutions.map(s=>s.page));
  assert.ok(observed.every(a=>new URL(a.href).hash==='#page='+a.page));
  const startText=locale==='en'?'Open solution start':'Buka awal penyelesaian';
  assert.equal(observed.filter(a=>a.text.startsWith(startText)).length,14);
  assert.ok(observed.some(a=>a.page===617&&a.text.startsWith(startText)));
  assert.ok(observed.some(a=>a.page===621&&a.text.startsWith(startText)));
  assert.equal((await supplement.innerText()).includes(locale==='en'?'not yet mapped':'belum dipetakan'),false);
  await page.locator('#local').check();
  assert.ok((await links.evaluateAll(elements=>elements.map(a=>a.getAttribute('href')))).every(href=>/^reader\.pdf#page=\d+$/.test(href)));
  await page.locator('#kind').selectOption('learningcheckpoint');
  assert.equal(await page.locator('#questions tr').count(),12);
  await page.locator('#choose-visible').click();
  const downloadPromise=page.waitForEvent('download');await page.locator('#export').click();
  const download=await downloadPromise;assert.equal(await download.failure(),null);
  const text=await page.locator('#exchange-text').inputValue();
  assert.equal(JSON.parse(text).mapping_sha256,model.mapping_sha256);
  assert.equal(JSON.parse(text).questions.length,12);
  await page.locator('#clear').click();await page.locator('#load-json').click();
  assert.equal(await page.locator('#questions input:checked').count(),12);
  const tampered=JSON.parse(text);tampered.questions[0].page=1;
  await page.locator('#exchange-text').fill(JSON.stringify(tampered));await page.locator('#load-json').click();
  assert.ok((await page.locator('#message').innerText()).includes(locale==='en'?'Assignment rejected':'Tugas ditolak'));
  assert.equal(await page.locator('#questions input:checked').count(),12);
  await page.locator('#kind').selectOption('tryit');assert.equal(await page.locator('#questions tr').count(),12);
  const start=links.filter({hasText:startText}).last();
  await start.focus();await page.keyboard.press('Tab');
  assert.equal(await page.evaluate(()=>document.activeElement.tagName),'SUMMARY');
  for(const width of [1280,390]){
   await page.setViewportSize({width,height:900});await start.scrollIntoViewIfNeeded();
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
   if(process.env.C130_BROWSER_SCREENSHOTS){
    await fs.mkdir(process.env.C130_BROWSER_SCREENSHOTS,{recursive:true});
    await page.screenshot({path:path.join(process.env.C130_BROWSER_SCREENSHOTS,locale+'-'+width+'.png')});
   }
   checks.push({locale,viewport_width:width,supplementary_links:132,solution_start_links:14,local_links:true,checkpoint_json_roundtrip:true,tampered_page_rejected:true,no_horizontal_overflow:true});
  }
  const other=locale==='en'?'':'.en';
  await page.locator('header nav a[href="C130.teacher'+other+'.html"]').click();
  assert.equal(await page.locator('html').getAttribute('lang'),locale==='en'?'id':'en');
 }
 assert.deepEqual(errors,[]);
 const assets={};
 for(const name of ['C130.teacher.html','C130.teacher.en.html','teacher.js','teacher.css','planner-model.json'])
  assets[name]=crypto.createHash('sha256').update(await fs.readFile(path.join(site,name))).digest('hex');
 const source=await fs.readFile(__filename);
 const report={schema:'c130-browser-checks/1',state:'pass',scope:'Actual local headless-browser interactions; not public deployment or mathematical verification',
  test_kind:'actual_headless_browser',browser_version:browser.version(),mapping_sha256:model.mapping_sha256,assets,checks,
  test_source:{path:'scripts/test-c130-teacher-browser-v1.cjs',bytes:source.length,sha256:crypto.createHash('sha256').update(source).digest('hex')},
  external_requests_blocked:true,page_errors:errors,limitations:['No external PDF or visualization site was opened. Page bindings are checked separately against exact source/PDF bytes.','File-picker import and printed output were not exercised; the visible JSON-text import was exercised.','Screenshots require separate visual inspection; DOM overflow checks do not constitute a complete accessibility audit.']};
 await fs.writeFile(path.join(base,'browser-checks.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({state:'pass',checks:checks.length,links:132,solution_starts:14,language_switch:true}));
})().catch(error=>{console.error(error);process.exitCode=1;}).finally(async()=>{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));});
