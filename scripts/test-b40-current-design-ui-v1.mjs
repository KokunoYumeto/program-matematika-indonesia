import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {createServer} from 'node:http';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {resolve,dirname,extname,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const docs=resolve(root,'docs'), output=resolve(root,'outputs/b40-design-ui-v1');
assert.ok(process.env.OPEN_COURSES_NODE_MODULES,'Use the supplied runtime; do not install dependencies');
const require=createRequire(import.meta.url);
const {chromium}=require(resolve(process.env.OPEN_COURSES_NODE_MODULES,'playwright'));
const server=createServer(async(req,res)=>{
  try{
    let pathname=decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname);
    if(pathname.endsWith('/'))pathname+='index.html';
    const path=resolve(docs,'.'+pathname);assert.ok(path.startsWith(docs+sep));
    const type={'.html':'text/html; charset=utf-8','.json':'application/json','.js':'text/javascript','.css':'text/css'}[extname(path)]??'application/octet-stream';
    const body=await readFile(path);res.writeHead(200,{'Content-Type':type});res.end(body);
  }catch{res.writeHead(404);res.end('Not in the test fixture');}
});
await mkdir(output,{recursive:true});
await new Promise(done=>server.listen(0,'127.0.0.1',done));
const origin='http://127.0.0.1:'+server.address().port, checks=[];
let browser;
try{
  browser=await chromium.launch({headless:true,executablePath:process.env.OPEN_COURSES_BROWSER_EXECUTABLE??resolve(process.env['ProgramFiles(x86)'],'Microsoft/Edge/Application/msedge.exe'),args:['--disable-gpu','--no-first-run','--disable-background-networking']});
  for(const width of [1280,390,320]){
    const context=await browser.newContext({viewport:{width,height:900},javaScriptEnabled:false});
    await context.route('**/*',route=>route.request().url().startsWith(origin)?route.continue():route.abort());
    const page=await context.newPage(), errors=[];
    page.on('pageerror',error=>errors.push(String(error)));
    await page.goto(origin+'/backend/coverage.html',{waitUntil:'load'});
    await page.locator('#role-B40 > td > details > summary').click();
    await page.locator('#role-B40').getByRole('link',{name:'Penilaian desain saat ini',exact:true}).click();
    const panel=page.locator('[data-current-native-design="B40"]');
    assert.ok(await panel.isVisible());
    const panelBounds=await panel.boundingBox();
    assert.ok(panelBounds.width>=Math.min(width-56,500),'Current design squeezed into a table column');
    assert.match(await panel.innerText(),/LaTeX modular/);
    assert.match(await panel.innerText(),/1035|1\.035/);
    assert.match(await panel.innerText(),/program lanjutan/);
    assert.equal(await panel.locator('li').count(),6);
    assert.equal(await page.locator('tr[id^="role-"]').count(),40);
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Overflow outside scrollable coverage table');
    for(const link of await panel.locator('a').all()){
      const href=await link.getAttribute('href');
      assert.equal((await context.request.get(new URL(href,origin+'/backend/coverage.html').href)).status(),200);
    }
    await panel.scrollIntoViewIfNeeded();
    if(width!==320)await panel.screenshot({path:resolve(output,'B40-'+width+'.png')});
    await panel.getByRole('link',{name:'Pemakaian dalam program lanjutan'}).click();
    assert.ok(await page.locator('#core-B40').isVisible());
    assert.ok(page.url().endsWith('#core-B40'));assert.deepEqual(errors,[]);
    checks.push({width,visible_current_design:true,source_links:3,advanced_use_link:true,roles:40,page_errors:0});
    await context.close();
  }
}finally{if(browser)await browser.close();await new Promise(done=>server.close(done));}
const receipt={schema:'b40-current-design-browser-check/1',state:'pass',checks,personal_browser_used:false};
await writeFile(resolve(output,'validation.json'),JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify(receipt));
