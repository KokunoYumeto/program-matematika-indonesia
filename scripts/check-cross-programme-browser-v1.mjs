import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createServer} from 'node:http';
import {createHash} from 'node:crypto';
import {resolve,dirname,extname} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const dir=resolve(root,'backend/cross-programme-v1');const docs=resolve(dir,'public-staging/docs');
const require=createRequire(import.meta.url);
assert.ok(process.env.OPEN_COURSES_NODE_MODULES,'Set OPEN_COURSES_NODE_MODULES to the supplied dependency runtime; no installation is needed');
const {chromium}=require(resolve(process.env.OPEN_COURSES_NODE_MODULES,'playwright'));
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json'};
const server=createServer(async(req,res)=>{try{let path=decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname);if(path.endsWith('/'))path+='index.html';const full=resolve(docs,'.'+path);assert.ok(full.startsWith(docs+'/')||full.startsWith(docs+'\\'));const b=await readFile(full);res.writeHead(200,{'Content-Type':mime[extname(full)]??'application/octet-stream'});res.end(b);}catch{res.writeHead(404);res.end('Not in the exact bounded test fixture');}});
await new Promise(done=>server.listen(0,'127.0.0.1',done));const origin='http://127.0.0.1:'+server.address().port;
await mkdir(resolve(dir,'browser-captures'),{recursive:true});let browser;
const checks=[],captures=[];
try{
  const browserPath=process.env.OPEN_COURSES_BROWSER_EXECUTABLE??resolve(process.env['ProgramFiles(x86)'],'Microsoft/Edge/Application/msedge.exe');
  browser=await chromium.launch({executablePath:browserPath,headless:true,args:['--disable-gpu','--no-first-run','--disable-background-networking']});
  for(const locale of ['en','id'])for(const width of [1280,390,320]){
    const context=await browser.newContext({viewport:{width,height:900},javaScriptEnabled:false});
    await context.route('**/*',route=>route.request().url().startsWith(origin)?route.continue():route.abort());const page=await context.newPage();
    await page.goto(origin+'/'+locale+'/programme/',{waitUntil:'load'});assert.equal(await page.locator('section[id^="core-"]').count(),40);assert.equal(await page.locator('section[id^="advanced-"]').count(),71);
    const overflow=await page.evaluate(()=>({inner:innerWidth,document:document.documentElement.scrollWidth}));assert.ok(overflow.document<=overflow.inner+1,'Horizontal overflow '+locale+' '+width);
    const proofNotice=await page.locator('.notice').innerText();assert.ok(proofNotice.length>100);
    if(width!==320){await page.locator('#core-B40').scrollIntoViewIfNeeded();const path='browser-captures/'+locale+'-'+width+'-core-B40.png';const b=await page.screenshot({path:resolve(dir,path),fullPage:false});captures.push({path,bytes:b.length,sha256:createHash('sha256').update(b).digest('hex')});}
    await page.locator('#core-B40 a[href="#advanced-RT-FIN"]').click();assert.ok(page.url().endsWith('#advanced-RT-FIN'));await page.locator('#advanced-RT-FIN a[href="#core-B40"]').click();assert.ok(page.url().endsWith('#core-B40'));
    checks.push({locale,width,mode:'javascript_disabled',course_sections:111,forward_reverse_clicks:'pass',horizontal_overflow:false,remote_runtime_blocked:true});await context.close();
  }
  for(const locale of ['en','id'])for(const name of ['index.html','learning-map.html','learning-map-paired.html']){
    const context=await browser.newContext({viewport:{width:390,height:900}});await context.route('**/*',route=>route.request().url().startsWith(origin)?route.continue():route.abort());const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(String(e)));
    await page.goto(origin+'/'+locale+'/'+name,{waitUntil:'networkidle'});assert.equal(await page.locator('a[data-cross-programme-course]').count(),40);assert.equal(await page.locator('.course-card').count(),40);
    await page.locator('#search').fill('linear');await page.waitForTimeout(150);assert.equal(await page.locator('#course-B40 a[data-cross-programme-course="B40"]').count(),1);
    assert.deepEqual(errors,[],'Current public runtime regression '+locale+' '+name);
    checks.push({locale,page:name,mode:'javascript_enabled',initial_links:40,re_render_B40_link:'pass',runtime_errors:0,remote_runtime_blocked:true});await context.close();
  }
}finally{if(browser)await browser.close();await new Promise(done=>server.close(done));}
const receipt={schema:'cross-programme-headless-browser-qa/1',status:'pass',engine:'Microsoft Edge, headless; no visible browser window',checks,captures,capture_inspection:'pending_actual_visual_inspection',native_readers_or_learner_state_modified:false};await writeFile(resolve(dir,'BROWSER_VALIDATION.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify({status:'pass',checks:checks.length,captures:captures.length,no_visible_window:true}));
