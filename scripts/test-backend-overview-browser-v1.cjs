/* Isolated headless browser; never uses the user's browser profile or desktop. */
const assert=require('node:assert/strict'), fs=require('node:fs/promises'), http=require('node:http'), path=require('node:path'), crypto=require('node:crypto');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE_PATH||'playwright');
const root=path.resolve(__dirname,'..'), docs=path.join(root,'docs');
const out=path.join(root,'outputs/backend-overview-111138796');
(async()=>{
  await fs.mkdir(out,{recursive:true});
  const server=http.createServer(async(req,res)=>{try{
    const relative=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
    const filename=path.resolve(docs,'.'+relative);assert.ok(filename.startsWith(docs+path.sep));
    const type={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json','.css':'text/css'}[path.extname(filename)]||'application/octet-stream';
    res.writeHead(200,{'Content-Type':type});res.end(await fs.readFile(filename));
  }catch{res.writeHead(404);res.end();}});
  await new Promise(r=>server.listen(0,'127.0.0.1',r));
  const origin='http://127.0.0.1:'+server.address().port, cases=[], errors=[];
  let browser;
  try{
    browser=await chromium.launch({headless:true,executablePath:process.env.PLAYWRIGHT_BROWSER_PATH,args:['--disable-gpu','--disable-background-networking']});
    for(const width of [1280,390,320])for(const javaScriptEnabled of [true,false]){
      const context=await browser.newContext({viewport:{width,height:900},javaScriptEnabled});
      await context.route('**/*',r=>r.request().url().startsWith(origin)?r.continue():r.abort());
      const page=await context.newPage();page.on('pageerror',e=>errors.push(String(e)));
      await page.goto(origin+'/backend/index.html');
      if(javaScriptEnabled)await page.waitForFunction(()=>!document.querySelector('#course-search').disabled);
      const card=page.locator('#current-backend-coverage');
      assert.match(await card.innerText(),/40 dari 40 peran kurikulum/);
      assert.match(await card.innerText(),/terverifikasi untuk 16 dari 40 peran/);
      assert.equal(await page.locator('#course-grid article').count(),40);
      await card.scrollIntoViewIfNeeded();assert.ok(await card.isVisible());
      assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
      assert.equal(await card.locator('a[href="coverage.html"]').count(),1);
      if(width===390&&javaScriptEnabled)await card.screenshot({path:path.join(out,'overview-390.png')});
      cases.push({width,javaScriptEnabled,course_cards:40,current_counts:true,overflow:false});
      await context.close();
    }
    assert.deepEqual(errors,[]);
  }finally{if(browser)await browser.close();await new Promise(r=>server.close(r));}
  const b=await fs.readFile(path.join(docs,'backend/index.html'));
  const receipt={schema:'backend-overview-browser/1',state:'pass',cases,errors,external_network_blocked:true,personal_browser_used:false,page:{bytes:b.length,sha256:crypto.createHash('sha256').update(b).digest('hex')}};
  await fs.writeFile(path.join(out,'BROWSER.json'),JSON.stringify(receipt,null,2)+'\n');
  console.log(JSON.stringify({state:'pass',cases:cases.length,errors:errors.length}));
})().catch(e=>{console.error(e);process.exitCode=1;});
