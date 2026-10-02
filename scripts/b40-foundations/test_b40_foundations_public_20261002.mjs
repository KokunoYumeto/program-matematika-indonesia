import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {createServer} from 'node:http';
import {resolve,dirname,extname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const base=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const work=resolve(base,'b40-foundations-public-20261002'),root=resolve(work,'public');
const require=createRequire(import.meta.url);
assert.ok(process.env.OPEN_COURSES_NODE_MODULES);
const {chromium}=require(resolve(process.env.OPEN_COURSES_NODE_MODULES,'playwright'));
const mime={'.html':'text/html; charset=utf-8','.tex':'text/plain; charset=utf-8','.json':'application/json','.txt':'text/plain; charset=utf-8','.zip':'application/zip'};
const server=createServer(async(req,res)=>{try{const url=new URL(req.url,'http://127.0.0.1');let path=decodeURIComponent(url.pathname);if(path.endsWith('/'))path+='index.html';const full=resolve(root,'.'+path);assert.ok(full.startsWith(root+'/')||full.startsWith(root+'\\'));const b=await readFile(full);res.writeHead(200,{'Content-Type':mime[extname(full)]??'application/octet-stream'});res.end(b);}catch{res.writeHead(404);res.end('File not in selected reading edition');}});
await new Promise(done=>server.listen(0,'127.0.0.1',done));const origin='http://127.0.0.1:'+server.address().port;
await mkdir(resolve(work,'visual'),{recursive:true});
const checks=[],captures=[];let browser;
const sections=['gr1','gr3','vs1','vs2','vs3','fields'];
const anchor='r005.hefferon-linear-algebra.unit.file.src.vs.vs3.tex.corollary.label.b186ad4cc75572f666a6';
try{
 browser=await chromium.launch({executablePath:resolve(process.env['ProgramFiles(x86)'],'Microsoft/Edge/Application/msedge.exe'),headless:true,args:['--disable-gpu','--no-first-run','--disable-background-networking']});
 for(const width of [1280,390,320]){
  const context=await browser.newContext({viewport:{width,height:900},javaScriptEnabled:false});
  await context.route('**/*',r=>r.request().url().startsWith(origin)?r.continue():r.abort());
  const page=await context.newPage();
  for(const section of sections){
   await page.goto(origin+'/semantic-pilot-'+section+'/'+section+'.reader-pilot.html',{waitUntil:'load'});
   const o=await page.evaluate(()=>({inner:innerWidth,document:document.documentElement.scrollWidth}));
   assert.ok(o.document<=o.inner+1,'Overflow: '+section+' '+width);
   assert.ok(await page.locator('main math').count()>0);
   assert.equal(await page.locator('script,iframe').count(),0);
   assert.equal(await page.locator('a[href="../index.html"]').count(),2);
   assert.equal(await page.locator('a[href="https://kokunoyumeto.github.io/program-matematika-indonesia/en/programme/"]').count(),2);
   assert.ok(!(await page.locator('header').innerText()).includes('not yet published'));
   if(section==='vs3'){
    const proofSpace=await page.locator('.proof>p:first-child>em:first-child').first().evaluate(e=>parseFloat(getComputedStyle(e).marginInlineEnd));assert.ok(proofSpace>0,'Proof label must not run into its opening word');
    await page.locator('[id="'+anchor+'"]').scrollIntoViewIfNeeded();
    assert.ok((await page.locator('[id="'+anchor+'"]').innerText()).includes('basis'));
    if(width!==320){const path='visual/basis-extension-'+width+'.png';const b=await page.screenshot({path:resolve(work,path)});captures.push({path,bytes:b.length,sha256:createHash('sha256').update(b).digest('hex')});}
   }
   checks.push({section,width,mathml:true,horizontal_overflow:false,return_navigation:true,remote_runtime_blocked:true});
  }
  await page.goto(origin+'/index.html',{waitUntil:'load'});
  await page.getByRole('link',{name:'Extending a linearly independent set to a basis',exact:true}).click();
  assert.ok(page.url().endsWith('#'+anchor));
  await page.getByRole('link',{name:'Foundation contents',exact:true}).first().click();
  assert.ok(page.url().endsWith('/index.html'));
  checks.push({width,index_to_result_and_return:true});
  await context.close();
 }
}finally{if(browser)await browser.close();await new Promise(done=>server.close(done));}
const result={schema:'b40-foundations-headless-reader-check/1',state:'PASS',checks,captures,engine:'Microsoft Edge, headless; no visible browser window',visual_inspection:'pending',mathematical_certification:false};
await writeFile(resolve(work,'BROWSER_QA.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({state:'PASS',checks:checks.length,captures:captures.length,no_visible_window:true}));
