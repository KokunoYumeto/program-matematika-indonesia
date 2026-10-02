/* One headless browser, serial local-only consumer checks; no user desktop interaction. */
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const http = require('node:http');
const path = require('node:path');
const crypto = require('node:crypto');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE_PATH || 'playwright');
const root = path.resolve(__dirname, '..');
const docs = path.join(root, 'docs');
const base = path.join(root, 'backend/course-capsule-v1/adapters/d60-native-ledger-v1');
const identity = b => ({bytes:b.length, sha256:crypto.createHash('sha256').update(b).digest('hex')});
const types = {'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json','.zip':'application/zip'};
(async () => {
  const server = http.createServer(async (req,res) => {
    try {
      const relative = decodeURIComponent(new URL(req.url,'http://localhost').pathname).replace(/^\/+/, '');
      const target = path.resolve(docs, relative);
      if (!target.startsWith(docs + path.sep)) {res.writeHead(403); return res.end();}
      const bytes = await fs.readFile(target); res.writeHead(200,{'Content-Type':types[path.extname(target)] || 'application/octet-stream'});res.end(bytes);
    } catch {res.writeHead(404);res.end();}
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const origin = 'http://127.0.0.1:' + server.address().port;
  let browser;
  const errors=[], cases=[], downloads=[];
  try {
    const launchOptions = {headless:true,args:['--disable-background-networking','--disable-component-update']};
    if (process.env.PLAYWRIGHT_BROWSER_PATH) launchOptions.executablePath = process.env.PLAYWRIGHT_BROWSER_PATH;
    browser = await chromium.launch(launchOptions);
    const context = await browser.newContext({acceptDownloads:true});
    const page = await context.newPage(); page.setDefaultTimeout(12000);
    page.on('pageerror',error=>errors.push(error.message));
    page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
    await page.route('**/*', route => route.request().url().startsWith(origin + '/') ? route.continue() : route.abort());
    const unit = 'unit:o012-rbt-l17';
    for (const locale of ['id','en']) for (const width of [1280,390]) {
      await page.setViewportSize({width,height:900});
      const suffix = locale==='en'?'.en':'', ledger=locale==='en'?'ledger-en':'ledger';
      for (const mode of ['D60','D60-pengajar']) {
        await page.goto(`${origin}/backend/d60/${mode}${suffix}.html?unit=${encodeURIComponent(unit)}`);
        await page.waitForSelector('#unit-list .unit');
        assert.equal(await page.locator('#unit-list .unit').count(),1);
        assert.equal(await page.locator('#unit-list .unit').getAttribute('data-unit-id'),unit);
        assert.equal(await page.locator('#kind').inputValue(),'');
        const native = page.locator('#unit-list a[href*="native-ledger"]').first();
        assert.equal(new URL(await native.getAttribute('href'),page.url()).searchParams.get('unit'),unit);
        await native.click();await page.waitForSelector('#records .record');
        assert.equal(await page.locator('#unit').inputValue(),unit);
        await page.locator('#search').fill('term:abelian-group:id-ID');
        assert.equal(await page.locator('#records .record').count(),1);
        assert.equal(await page.locator('#records .record').getAttribute('data-record-id'),'term:abelian-group:id-ID');
        assert.ok((await page.locator('#records .record .notice').first().innerText()).length>20);
        await page.locator('#records details').last().locator('summary').click();
        assert.ok((await page.locator('#records pre').last().innerText()).includes('"preferred": "grup abelian"'));
        if (mode==='D60') {
          await page.locator('#records .record').scrollIntoViewIfNeeded();
          await page.screenshot({path:path.join(base,`term-${locale}-${width}.png`),fullPage:false});
        }
        assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
        const returnLink=page.locator('nav a').filter({hasText:locale==='en'?'Study':'Belajar'}).first();
        assert.equal(new URL(await returnLink.getAttribute('href'),page.url()).searchParams.get('unit'),unit);
        await returnLink.click();await page.waitForSelector('#unit-list .unit');
        assert.equal(await page.locator('#unit-list .unit').count(),1);
        const language=page.locator('nav .language a[lang="'+(locale==='en'?'id':'en')+'"]');
        assert.equal(new URL(await language.getAttribute('href'),page.url()).searchParams.get('unit'),unit);
        await page.goto(`${origin}/backend/d60/${mode}${suffix}.html?unit=unknown-native-unit`);
        await page.waitForSelector('#workbench:not([hidden])');
        assert.equal(await page.locator('#unit-list .unit').count(),0);
        cases.push({locale,width,mode,exact_unit_roundtrip:true,ancestor_discovery_labelled:true,unknown_unit_refused:true});
      }
      await page.goto(`${origin}/backend/d60/native-ledger/${ledger}.html?kind=segments&flag=target_file_identity_differs`);
      await page.waitForSelector('#records .record');
      assert.equal(await page.locator('#records .record').count(),25);
      assert.ok((await page.locator('#count').innerText()).endsWith('/ 73'));
      await page.locator('#next').click();assert.ok((await page.locator('#count').innerText()).startsWith('26'));
      assert.equal(new URL(await page.locator('#language').getAttribute('href'),page.url()).searchParams.get('flag'),'target_file_identity_differs');
      await page.locator('#language').click();await page.waitForSelector('#records .record');
      assert.equal(await page.locator('#flag').inputValue(),'target_file_identity_differs');
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
      await page.goto(`${origin}/backend/d60/native-ledger/${ledger}.html?kind=rights&unit=${encodeURIComponent(unit)}`);
      await page.waitForSelector('#records .record');
      assert.equal(await page.locator('#records .record').count(),4, 'Preserve every rights record with an explicit native unit/path join');
      assert.equal(await page.locator('#records .record[data-record-id="rights:roberts-cc-by-4.0"]').count(),1);
      await page.screenshot({path:path.join(base,`browser-${locale}-${width}.png`),fullPage:false});
    }
    for (const name of ['native-metadata.zip','projection.json']) {
      const response=await context.request.get(`${origin}/backend/d60/native-ledger/${name}`);
      assert.equal(response.status(),200);const bytes=await response.body();
      assert.deepEqual(bytes,await fs.readFile(path.join(docs,'backend/d60/native-ledger',name)));
      downloads.push({path:name,...identity(bytes)});
    }
    const data=JSON.parse(await fs.readFile(path.join(docs,'backend/d60/native-ledger/projection.json'),'utf8'));
    await page.goto(`${origin}/backend/d60/native-ledger/ledger.html`);await page.waitForSelector('#records .record');
    const api=await page.evaluate(()=>{
      const a=globalThis.D60_NATIVE_LEDGER_API,d=globalThis.D60_NATIVE_LEDGER;
      return {terms:a.filter(d.rows,'terms').length,unknown:a.filter(d.rows,'terms','','unknown-native-unit').length,
        xss:a.filter(d.rows,'terms','<script>alert(1)</script>').length};
    });
    assert.deepEqual(api,{terms:528,unknown:0,xss:0});
    assert.deepEqual(errors,[]);
    const inputFiles=[];
    for (const name of ['ledger.html','ledger-en.html','ledger-ui.js','ledger.css','data.js','projection.json']) {
      const relative='docs/backend/d60/native-ledger/'+name;
      inputFiles.push({path:relative,...identity(await fs.readFile(path.join(root,relative)))});
    }
    for (const name of ['D60.html','D60.en.html','D60-pengajar.html','D60-pengajar.en.html','d60-ui.js','data.js']) {
      const relative='docs/backend/d60/'+name;
      inputFiles.push({path:relative,...identity(await fs.readFile(path.join(root,relative)))});
    }
    const receipt={schema:'d60-native-ledger-browser-tests/1',state:'pass',cases,downloads,api,input_files:inputFiles,
      input_projection:identity(await fs.readFile(path.join(docs,'backend/d60/native-ledger/projection.json'))),
      native_scope:data.summary,external_network_blocked:true,desktop_interaction:false,errors,
      limitations:['Local consumer behavior only; no independent canon review or full native-book rebuild.','English interface continues to link Indonesian reader content.']};
    await fs.writeFile(path.join(base,'browser-tests.json'),JSON.stringify(receipt,null,2)+'\n');
    console.log(JSON.stringify({state:'pass',cases:cases.length,downloads:downloads.length,errors:errors.length}));
  } finally {if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));}
})().catch(error=>{console.error(error.stack);process.exitCode=1;});
