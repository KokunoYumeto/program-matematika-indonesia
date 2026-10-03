const assert=require('node:assert/strict'),fs=require('node:fs/promises'),path=require('node:path'),http=require('node:http'),crypto=require('node:crypto');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE_PATH||'playwright');
const root=path.resolve(__dirname,'..'),docs=path.join(root,'docs'),out=path.join(root,'outputs/course-downloads-111390060');
(async()=>{
  await fs.mkdir(out,{recursive:true});
  const server=http.createServer(async(req,res)=>{try{
    let route=decodeURIComponent(new URL(req.url,'http://localhost').pathname);if(route.endsWith('/'))route+='index.html';
    const file=path.resolve(docs,'.'+route);assert.ok(file.startsWith(docs+path.sep));
    const data=await fs.readFile(file);res.writeHead(200,{'Content-Type':file.endsWith('.html')?'text/html; charset=utf-8':'application/octet-stream'});res.end(data);
  }catch{res.writeHead(404);res.end();}});
  await new Promise(r=>server.listen(0,'127.0.0.1',r));const origin='http://127.0.0.1:'+server.address().port;
  const cases=[],errors=[],files=[];let browser;
  try{
    browser=await chromium.launch({headless:true,executablePath:process.env.PLAYWRIGHT_BROWSER_PATH,args:['--disable-gpu','--disable-background-networking']});
    for(const locale of ['id','en'])for(const width of [1280,390,320])for(const javaScriptEnabled of [true,false]){
      const context=await browser.newContext({viewport:{width,height:900},javaScriptEnabled});
      await context.route('**/*',r=>r.request().url().startsWith(origin)?r.continue():r.abort());
      const page=await context.newPage();page.on('pageerror',error=>errors.push(String(error)));
      await page.goto(origin+'/'+locale+'/downloads/');assert.equal(await page.locator('[data-course]').count(),40);
      assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Horizontal overflow '+locale+' '+width);
      assert.ok(await page.locator('[data-course="A00"]').evaluate(el=>el.getBoundingClientRect().top<900),'First course must be reachable in the first screen');
      assert.equal(await page.locator('details.edition-notes').getAttribute('open'),null);
      if(javaScriptEnabled){
        await page.locator('#format').selectOption('pdf');assert.equal(await page.locator('[data-course]:visible').count(),locale==='en'?15:38);
        await page.locator('#search').fill('zzzz-no-course');assert.equal(await page.locator('[data-course]:visible').count(),0);assert.ok(await page.locator('#empty').isVisible());
        await page.locator('#reset').click();assert.equal(await page.locator('[data-course]:visible').count(),40);
        await page.locator('#search').fill('D10');assert.equal(await page.locator('[data-course]:visible').count(),1);
        await page.evaluate(()=>location.hash='#course-D10');
        await page.waitForFunction(()=>[...document.querySelectorAll('[data-language]')].every(a=>a.href.endsWith('#course-D10')));
        assert.ok((await page.locator('[data-language="'+(locale==='en'?'id':'en')+'"]').getAttribute('href')).endsWith('#course-D10'));
        await page.locator('#reset').click();await page.evaluate(()=>scrollTo(0,0));
      }else {assert.ok(!(await page.locator('.filters').isVisible()));assert.equal(await page.locator('[data-course]:visible').count(),40);}
      if(width===390&&javaScriptEnabled)await page.screenshot({path:path.join(out,locale+'-390.png')});
      cases.push({locale,width,javaScriptEnabled,courses:40,no_overflow:true,filter_tested:javaScriptEnabled});await context.close();
    }
    assert.deepEqual(errors,[]);
    for(const locale of ['id','en']){const relative=`docs/${locale}/downloads/index.html`,bytes=await fs.readFile(path.join(root,relative));files.push({path:relative,bytes:bytes.length,sha256:crypto.createHash('sha256').update(bytes).digest('hex')});}
  }finally{if(browser)await browser.close();await new Promise(r=>server.close(r));}
  const receipt={schema:'course-download-browser/1',state:'pass',cases,errors,files,network_blocked:true,personal_browser_used:false};
  await fs.writeFile(path.join(out,'BROWSER.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify({state:'pass',cases:cases.length,errors:errors.length,files}));
})().catch(error=>{console.error(error);process.exitCode=1;});
