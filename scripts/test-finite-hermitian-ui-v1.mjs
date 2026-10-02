import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {createServer} from 'node:http';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {resolve,dirname,extname,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..'),docs=resolve(root,'docs');
const output=resolve(root,'outputs/finite-hermitian-ui-v1');
assert.ok(process.env.OPEN_COURSES_NODE_MODULES);
const require=createRequire(import.meta.url),{chromium}=require(resolve(process.env.OPEN_COURSES_NODE_MODULES,'playwright'));
const published='https://kokunoyumeto.github.io/program-matematika-indonesia/';
async function response(pathname){
  if(pathname.endsWith('/'))pathname+='index.html';
  const path=resolve(docs,'.'+decodeURIComponent(pathname));assert.ok(path.startsWith(docs+sep));
  return {body:await readFile(path),contentType:{'.html':'text/html; charset=utf-8','.json':'application/json','.js':'text/javascript','.css':'text/css'}[extname(path)]??'application/octet-stream'};
}
const server=createServer(async(req,res)=>{try{const r=await response(new URL(req.url,'http://localhost').pathname);res.writeHead(200,{'Content-Type':r.contentType});res.end(r.body);}catch{res.writeHead(404);res.end('Not a local fixture');}});
await mkdir(output,{recursive:true});await new Promise(done=>server.listen(0,'127.0.0.1',done));
const origin='http://127.0.0.1:'+server.address().port,checks=[];let browser;
try{
  browser=await chromium.launch({headless:true,executablePath:resolve(process.env['ProgramFiles(x86)'],'Microsoft/Edge/Application/msedge.exe'),args:['--disable-gpu','--no-first-run','--disable-background-networking']});
  for(const width of [1280,390,320]){
    const context=await browser.newContext({viewport:{width,height:900},javaScriptEnabled:false});
    await context.route('**/*',async route=>{
      const url=route.request().url();if(url.startsWith(origin))return route.continue();
      if(url.startsWith(published)){try{return await route.fulfill(await response('/'+url.slice(published.length).split('#')[0]));}catch{return route.fulfill({status:404,body:'Missing local route'});}}
      return route.abort();
    });
    const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(String(e)));
    for(const locale of ['en','id']){
      await page.goto(origin+'/'+locale+'/programme/#advanced-RT-FIN');
      const status=page.locator('#advanced-RT-FIN [data-current-proof-requirements="RT-FIN"]');
      assert.ok(await status.isVisible());
      assert.ok((await status.innerText()).includes(locale==='en'?'four recorded uses':'empat penggunaan'));
      assert.equal(await status.locator('a[hreflang="en"]').count(),2);
      assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Programme has viewport overflow');
      if(locale==='en' && width===390)await page.screenshot({path:resolve(output,'current-status-390.png')});
      const panel=page.locator('#advanced-RT-FIN [data-hermitian-prerequisite="consumer"]');
      assert.ok(await panel.isVisible());assert.equal(await panel.locator('a[hreflang="en"]').count(),2);
      await panel.locator('a[hreflang="en"]').first().click();
      assert.ok(await page.locator('#gramschmidt-with-the-coefficients-in-the-correct-order').isVisible());
      assert.equal(await page.locator('math').count(),144);assert.equal(await page.locator('html').getAttribute('lang'),'en');
      assert.equal(await page.locator('h1').count(),1);
      const headings=await page.locator('h1,h2,h3').evaluateAll(rows=>rows.map(r=>r.tagName));
      assert.equal(headings[0],'H1','Reader starts with a lower-level heading');
      assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Reader has viewport overflow');
      assert.ok(await page.locator('a[href="00-finite-hermitian.tex"]').isVisible());
      if(locale==='en' && width!==320){await page.locator('#orthogonal-projection-and-decomposition').scrollIntoViewIfNeeded();await page.screenshot({path:resolve(output,'proof-'+width+'.png')});}
      await page.locator('nav').first().getByRole('link',{name:'Linear algebra',exact:true}).click();
      const provider=page.locator('#core-B40 [data-hermitian-prerequisite="provider"]');
      assert.ok(await provider.isVisible());
      checks.push({width,programme_locale:locale,current_requirements_notice:true,consumer_to_proof_to_provider:true,formulas:144,language:'en'});
    }
    assert.deepEqual(errors,[]);await context.close();
  }
}finally{if(browser)await browser.close();await new Promise(done=>server.close(done));}
const receipt={schema:'finite-hermitian-browser/1',state:'pass',checks,personal_browser_used:false,external_network:false};
await writeFile(resolve(output,'validation.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify(receipt));
