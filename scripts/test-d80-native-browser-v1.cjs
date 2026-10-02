/* Serial local headless QA; never opens or operates the user's desktop browser. */
const assert=require('node:assert/strict'), fs=require('node:fs/promises'), http=require('node:http');
const path=require('node:path'), crypto=require('node:crypto');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE_PATH || 'playwright');
const root=path.resolve(__dirname,'..'), docs=path.join(root,'docs');
const relative='docs/backend/d80/native-ledger/', base=path.join(root,'backend/course-capsule-v1/adapters/d80-native-ledger-v1');
const identity=b=>({bytes:b.length,sha256:crypto.createHash('sha256').update(b).digest('hex')});
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json','.zip':'application/zip'};
assert.ok(process.argv.length===2 || (process.argv.length===3 && process.argv[2]==='--hosted'));
const hosted=process.argv[2]==='--hosted';
(async()=>{
  const server=http.createServer(async(req,res)=>{
    try{
      const target=path.resolve(docs,decodeURIComponent(new URL(req.url,'http://localhost').pathname).replace(/^\/+/,''));
      if(!target.startsWith(docs+path.sep)){res.writeHead(403);return res.end();}
      const bytes=await fs.readFile(target);res.writeHead(200,{'Content-Type':types[path.extname(target)]||'application/octet-stream'});res.end(bytes);
    }catch{res.writeHead(404);res.end();}
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const origin='http://127.0.0.1:'+server.address().port, errors=[],cases=[],downloads=[];
  let browser;
  try{
    const options={headless:true,args:['--disable-background-networking','--disable-component-update']};
    if(process.env.PLAYWRIGHT_BROWSER_PATH)options.executablePath=process.env.PLAYWRIGHT_BROWSER_PATH;
    browser=await chromium.launch(options);
    const context=await browser.newContext(), page=await context.newPage();page.setDefaultTimeout(15000);
    page.on('pageerror',e=>errors.push(e.message));
    await page.route('**/*',r=>r.request().url().startsWith(origin+'/')?r.continue():r.abort());
    for(const locale of ['id','en'])for(const width of [1280,390]){
      await page.setViewportSize({width,height:900});
      const file=locale==='en'?'ledger-en.html':'ledger.html';
      const url=`${origin}/backend/d80/native-ledger/${file}`;
      if(hosted){
        await page.goto(`${origin}/${locale}/index.html#course-D80`);
        const entry=page.locator(`#course-D80 a[href$="/backend/d80/native-ledger/${file}"]`);
        assert.equal(await entry.count(),1,'Localized course card must expose the functioning ledger');
        await page.goto(`${origin}/backend/d80/D80.html`);
        assert.ok(await page.locator('a[href*="native-ledger/ledger.html"]').count()>=1,'Native learner hub must reach the new tool');
      }
      await page.goto(url+'?kind=terms&flag=term_disagreement');
      await page.waitForSelector('#records .record');
      assert.equal(await page.locator('#records .record').count(),2);
      assert.ok((await page.locator('#records').innerText()).includes('hasil kali cawan'));
      assert.ok((await page.locator('#records').innerText()).includes('hasil kali cup'));
      await page.screenshot({path:path.join(base,`${hosted?'hosted-':''}terms-${locale}-${width}.png`),fullPage:false});
      await page.locator('#records').scrollIntoViewIfNeeded();
      await page.screenshot({path:path.join(base,`${hosted?'hosted-':''}records-${locale}-${width}.png`),fullPage:false});
      assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
      await page.locator('#flag').selectOption('unmapped_unit');
      assert.equal(await page.locator('#records .record').count(),11);
      assert.equal(await page.locator('#records .record a').count(),0);
      assert.ok((await page.locator('#records').innerText()).includes('o014.aljabr2.prelude'));
      await page.locator('#flag').selectOption('');await page.locator('#search').fill('math.category.functor');
      assert.equal(await page.locator('#records .record').count(),1);
      await page.locator('#language').click();await page.waitForSelector('#records .record');
      assert.equal(await page.locator('#search').inputValue(),'math.category.functor');
      assert.equal(await page.locator('html').getAttribute('lang'),locale==='en'?'id':'en');
      await page.goto(url+'?kind=segments&flag=unit_slice');await page.waitForSelector('#records .record');
      assert.equal(await page.locator('#count').innerText(),'1–25 / 1736');
      await page.locator('#next').click();assert.equal(await page.locator('#count').innerText(),'26–50 / 1736');
      await page.locator('#previous').click();assert.equal(await page.locator('#count').innerText(),'1–25 / 1736');
      const link=await page.locator('#records .record a').first().getAttribute('href');
      assert.ok(link.startsWith('https://kokunoyumeto.github.io/metode-aljabar-jilid-2-id/#unit-'));
      await page.locator('#unit').fill('unknown-unit');assert.equal(await page.locator('#records .record').count(),0);
      await page.goto(url+'?kind=corrections&flag=observed_not_modified_pending_consolidated_review');await page.waitForSelector('#records .record');
      assert.equal(await page.locator('#records .record').count(),1);
      assert.equal(await page.locator('#records .record').getAttribute('data-record-id'),'O014-O001');
      assert.equal(await page.locator('#records h3').count(),2);
      await page.goto(url+'?kind=diagrams&flag=reader_override');await page.waitForSelector('#records .record');
      assert.equal(await page.locator('#records .record').count(),13);
      assert.equal(await page.locator('#records h3').count(),13);
      assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
      await page.screenshot({path:path.join(base,`${hosted?'hosted-':''}diagrams-${locale}-${width}.png`),fullPage:false});
      cases.push({locale,width,conflicts_preserved:true,unmapped_locators_not_guessed:true,language_filter_preserved:true,
        precise_unit_links:true,pagination:true,pending_correction_preserved:true,overrides_and_originals_visible:true,no_horizontal_overflow:true});
    }
    for(const name of ['native-metadata.zip','projection.json']){
      const response=await context.request.get(origin+'/backend/d80/native-ledger/'+name);
      assert.equal(response.status(),200);const bytes=await response.body();
      assert.deepEqual(bytes,await fs.readFile(path.join(root,relative,name)));downloads.push({path:name,...identity(bytes)});
    }
    await page.goto(origin+'/backend/d80/native-ledger/ledger.html');await page.waitForSelector('#records .record');
    await page.evaluate(()=>{
      const row=globalThis.D80_NATIVE_LEDGER.rows.find(r=>r.kind==='terms');
      row.native.preferred_id='<img src=x onerror="globalThis.D80_XSS=true">';
      document.getElementById('search').value=row.id;document.getElementById('search').dispatchEvent(new Event('input'));
    });
    assert.equal(await page.locator('#records img').count(),0);
    assert.equal(await page.evaluate(()=>globalThis.D80_XSS===true),false);
    assert.ok((await page.locator('#records h2').innerText()).startsWith('<img'));
    // File-scheme mode has no fetch dependency and must render offline.
    const offline=await context.newPage();offline.on('pageerror',e=>errors.push(e.message));
    await offline.goto(require('node:url').pathToFileURL(path.join(root,relative,'ledger-en.html')).href);
    await offline.waitForSelector('#records .record');assert.equal(await offline.locator('#count').innerText(),'1–25 / 511');
    assert.deepEqual(errors,[]);
    const inputFiles=[];
    for(const name of ['ledger.html','ledger-en.html','ledger-ui.js','ledger.css','data.js','projection.json'])
      inputFiles.push({path:relative+name,...identity(await fs.readFile(path.join(root,relative,name)))});
    const receipt={schema:'d80-native-ledger-browser-tests/1',state:'pass',cases,downloads,input_files:inputFiles,
      external_network_blocked:true,desktop_interaction:false,offline_file_scheme:true,record_html_injection_refused:true,
      shared_course_entrypoints_checked:hosted,errors};
    await fs.writeFile(path.join(base,hosted?'hosted-browser-tests.json':'browser-tests.json'),JSON.stringify(receipt,null,2)+'\n');
    console.log(JSON.stringify({state:'pass',cases:cases.length,downloads:downloads.length,offline:true,errors:errors.length}));
  }finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));}
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
