import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createServer} from 'node:http';
import {createHash} from 'node:crypto';
import {resolve,dirname,extname} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'../..');
const docs=resolve(root,'docs'),out=resolve(root,'outputs/a00-portable-formats-v1');
const require=createRequire(import.meta.url);
assert.ok(process.env.OPEN_COURSES_NODE_MODULES);
const {chromium}=require(resolve(process.env.OPEN_COURSES_NODE_MODULES,'playwright'));
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json'};
const server=createServer(async(req,res)=>{try{
 let path=decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname);if(path.endsWith('/'))path+='index.html';
 const full=resolve(docs,'.'+path);assert.ok(full.startsWith(docs+'/')||full.startsWith(docs+'\\'));
 const bytes=await readFile(full);res.writeHead(200,{'Content-Type':mime[extname(full)]??'application/octet-stream'});res.end(bytes);
}catch{res.writeHead(404);res.end('Not found');}});
await new Promise(done=>server.listen(0,'127.0.0.1',done));const origin='http://127.0.0.1:'+server.address().port;
await mkdir(resolve(out,'hub-browser-captures'),{recursive:true});
const checks=[],captures=[];let browser;
try{
 browser=await chromium.launch({executablePath:resolve(process.env['ProgramFiles(x86)'],'Microsoft/Edge/Application/msedge.exe'),headless:true,args:['--disable-gpu','--no-first-run','--disable-background-networking']});
 for(const locale of ['id','en'])for(const width of [390,1280])for(const js of [false,true]){
  const context=await browser.newContext({viewport:{width,height:1000},javaScriptEnabled:js});
  await context.route('**/*',route=>route.request().url().startsWith(origin)?route.continue():route.abort());
  const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  for(const file of ['index.html','learning-map.html','learning-map-paired.html']){
   await page.goto(`${origin}/${locale}/${file}#course-A00`,{waitUntil:'load'});
   assert.equal(await page.locator('.course-card').count(),40);
   const set=page.locator('#course-A00 [data-access-group="paired-formats"]');
   assert.equal(await set.count(),1);assert.equal(await set.getAttribute('data-format-set-language'),'id');
   assert.deepEqual(await set.locator('[data-supplemental-reader]').evaluateAll(ns=>ns.map(n=>n.dataset.supplementalReader)),['pdf','tex','source','epub','record'].map(x=>'A00:id-format-'+x));
   assert.equal(await set.locator('.footnote').count(),1,'Shared explanation appears once');
   assert.equal(await page.locator('#course-B80 [data-access-group="paired-formats"]').count(),2);
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Horizontal overflow');
   assert.equal(await page.locator('html').getAttribute('lang'),locale);
   if(file==='index.html'&&width===390&&js){
    await set.scrollIntoViewIfNeeded();const path=`hub-browser-captures/${locale}-390-a00-formats.png`;
    const bytes=await page.screenshot({path:resolve(out,path),fullPage:false});captures.push({path,bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex')});
    const other=locale==='id'?'en':'id';await page.locator(`[data-locale-link="${other}"]`).click();
    assert.equal(await page.locator('html').getAttribute('lang'),other);assert.ok(page.url().includes('#course-A00'));
   }
   checks.push({locale,width,js,file,courses:40,a00_formats_ordered:true,b80_sets_preserved:true,horizontal_overflow:false});
  }
  await page.goto(`${origin}/${locale}/downloads/`,{waitUntil:'load'});
  assert.equal(await page.locator('[data-course]').count(),40);
  const files=page.locator('[data-course="A00"] a[href*="/00-a00-id.pdf"], [data-course="A00"] a[href*="/01-a00-id.tex"], [data-course="A00"] a[href*="/02-a00-id-source.zip"], [data-course="A00"] a[href*="/03-a00-id.epub"]');
  assert.equal(await files.count(),locale==='id'?4:0,'Actual content language controls download list');
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  assert.deepEqual(errors,[]);checks.push({locale,width,js,page:'downloads',actual_content_language:true,errors:0});
  await context.close();
 }
 const report={state:'pass',checks,captures,external_runtime_blocked:true};
 await writeFile(resolve(out,'HUB_BROWSER_CHECK.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({state:'pass',checks:checks.length,captures}));
}finally{await browser?.close();await new Promise(done=>server.close(done));}
