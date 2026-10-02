/* One isolated, headless browser. Never operates a user's browser or desktop. */
const assert=require('node:assert/strict'),fs=require('node:fs/promises'),http=require('node:http'),path=require('node:path'),crypto=require('node:crypto');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE_PATH||'playwright');
const root=path.resolve(__dirname,'..'),docs=path.join(root,'docs'),base=path.join(root,'backend/course-capsule-v1/adapters/d20-native-ledger-v1');
const site='backend/d20/native-ledger/';
const hosted=process.env.D20_HOSTED_TEST==='1';
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json'};
(async()=>{
 const server=http.createServer(async(req,res)=>{try{const filename=path.resolve(docs,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));assert.ok(filename.startsWith(docs+path.sep));res.writeHead(200,{'Content-Type':types[path.extname(filename)]||'application/octet-stream'});res.end(await fs.readFile(filename));}catch{res.writeHead(404);res.end();}});
 await new Promise(r=>server.listen(0,'127.0.0.1',r));const origin='http://127.0.0.1:'+server.address().port;
 let browser;const cases=[],errors=[];
 try{
  browser=await chromium.launch({headless:true,executablePath:process.env.PLAYWRIGHT_BROWSER_PATH,args:['--disable-gpu','--disable-background-networking']});
  for(const width of [1280,390,320])for(const locale of ['id','en']){
   const context=await browser.newContext({viewport:{width,height:900}});
   await context.route('**/*',r=>r.request().url().startsWith(origin)?r.continue():r.abort());
   const page=await context.newPage();page.on('pageerror',e=>errors.push(String(e)));
   if(hosted){
    await page.goto(origin+'/backend/d20/D20'+(locale==='en'?'.en':'')+'.html');
    await page.locator('nav[data-central-surface-navigation="v1"] a[href="native-ledger/'+(locale==='en'?'ledger-en.html':'ledger.html')+'"]').first().click();
   }else await page.goto(origin+'/'+site+(locale==='en'?'ledger-en.html':'ledger.html'));
   await page.waitForFunction(()=>document.querySelectorAll('.record').length===20);
   assert.equal(await page.locator('html').getAttribute('lang'),locale);
   assert.match(await page.locator('#count').innerText(),/425/);
   await page.locator('#search').fill('TERM-VECTOR-SPACE');
   assert.equal(await page.locator('.record').count(),1);
   assert.ok((await page.locator('.record').innerText()).includes('ruang vektor'));
   await page.locator('#language').click();await page.waitForFunction(()=>document.querySelector('#search').value==='TERM-VECTOR-SPACE');assert.equal(await page.locator('#search').inputValue(),'TERM-VECTOR-SPACE');
   await page.locator('#search').fill('');await page.locator('#kind').selectOption('segments');
   assert.match(await page.locator('#count').innerText(),/2196/);
   await page.locator('#chapter').selectOption('FAOA-2015-CH01');assert.match(await page.locator('#count').innerText(),/154/);
   assert.equal(await page.locator('.record a[hreflang="id"]').count(),20);
   await page.locator('.record details').first().locator('summary').click();assert.ok(await page.locator('.record pre').first().isVisible());
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
   await page.locator('#next').click();assert.ok(!(await page.locator('#previous').isDisabled()));
   await page.locator('#search').fill('<img src=x onerror=alert(1)>');assert.equal(await page.locator('.record').count(),0);assert.equal(await page.locator('#records img').count(),0);
   await page.locator('#search').fill('');await page.locator('#chapter').selectOption('');await page.locator('#kind').selectOption('corrections');assert.match(await page.locator('#count').innerText(),/286/);
   if(width===390&&locale==='id')await page.screenshot({path:path.join(base,'preview-en-390.png'),fullPage:false});
   cases.push({width,starting_locale:locale,search:true,language_state:true,chapter_binding:true,pagination:true,overflow:false});
   await context.close();
  }
  assert.deepEqual(errors,[]);
 }finally{if(browser)await browser.close();await new Promise(r=>server.close(r));}
 const files=[];for(const name of ['ledger.html','ledger-en.html','ledger-ui.js','ledger.css','data.js']){const b=await fs.readFile(path.join(docs,site,name));files.push({path:site+name,bytes:b.length,sha256:crypto.createHash('sha256').update(b).digest('hex')});}
 const receipt={schema:'d20-native-ledger-browser/1',state:'pass',cases,errors,input_files:files,external_network_blocked:true,personal_browser_used:false,hosted_navigation_tested:hosted};
 await fs.writeFile(path.join(base,hosted?'hosted-browser-tests.json':'browser-tests.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify({state:'pass',cases:cases.length,errors:errors.length,hosted_navigation_tested:hosted}));
})().catch(e=>{console.error(e);process.exitCode=1;});
