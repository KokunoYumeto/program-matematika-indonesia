/* Actual serial headless checks of the A00 concordance; no producer or external requests. */
const assert=require('node:assert/strict');
const fs=require('node:fs/promises');
const path=require('node:path');
const http=require('node:http');
const crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),docs=path.join(root,'docs');
const playwright=require(process.env.A00_PLAYWRIGHT_PACKAGE||'playwright');
const screenshots=process.env.A00_BROWSER_SCREENSHOTS;
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const fact=async p=>{const b=await fs.readFile(path.join(root,p));return {path:p,bytes:b.length,sha256:hash(b)};};
const server=http.createServer(async(req,res)=>{
  try{
    const name=path.resolve(docs,'.'+decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname));
    const relative=path.relative(docs,name);
    if(relative.startsWith('..')||path.isAbsolute(relative)){res.writeHead(403);res.end();return;}
    const body=await fs.readFile(name);
    const types={'.html':'text/html; charset=utf-8','.json':'application/json','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8'};
    res.writeHead(200,{'Content-Type':types[path.extname(name)]||'application/octet-stream'});res.end(body);
  }catch{res.writeHead(404);res.end();}
});
let browser;
(async()=>{
  await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',resolve);});
  const origin='http://127.0.0.1:'+server.address().port;
  browser=await playwright.chromium.launch({headless:true,executablePath:process.env.A00_BROWSER_EXECUTABLE||undefined,args:['--disable-background-networking','--no-first-run']});
  const context=await browser.newContext();
  await context.route('**/*',r=>new URL(r.request().url()).origin===origin?r.continue():r.abort());
  const page=await context.newPage();page.setDefaultTimeout(12000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  const proofPath='docs/backend/a00/native-ledger/term-locations.json';
  const proofBytes=await fs.readFile(path.join(root,proofPath)),proof=JSON.parse(proofBytes);
  assert.equal(proof.choices.length,20);assert.equal(proof.summary.choice_variant_matches,3419);
  const checks=[];
  for(const locale of ['id','en']){
    const filename=locale==='id'?'ledger.html':'ledger-en.html';
    const teacher=locale==='id'?'A00-pengajar.html':'A00-pengajar-en.html';
    const course=locale==='id'?'A00.html':'A00-en.html';
    await page.setViewportSize({width:1280,height:900});
    await page.goto(origin+'/backend/a00/'+filename,{waitUntil:'networkidle'});
    assert.equal(await page.locator('html').getAttribute('lang'),locale);
    assert.equal(await page.locator('[data-search]').count(),95);
    assert.equal(await page.locator('.term-locations').count(),20);
    assert.equal(await page.locator('#count').innerText(),'95 / 95');
    assert.ok(await page.locator('#search').evaluate(el=>el.labels.length>0));
    assert.equal(await page.locator('#count').getAttribute('aria-live'),'polite');
    for(const item of proof.choices){
      const detail=page.locator('.term-locations[data-choice-id="'+item.choice_id+'"]');
      assert.equal(await detail.count(),1);
      assert.ok((await detail.locator('summary').innerText()).includes(String(item.match_count)));
      assert.equal(await detail.locator('li').count(),Math.min(8,item.match_count));
      assert.equal(await detail.locator('q[lang="id"]').count(),Math.min(8,item.match_count));
    }
    const visible=()=>page.locator('[data-search]:visible').count();
    for(const query of ['m81272','bilangan','M81243','not-a-real-term']){
      const expected=await page.locator('[data-search]').evaluateAll((rows,q)=>rows.filter(r=>r.dataset.search.toLocaleLowerCase().includes(q.toLocaleLowerCase())).length,query);
      await page.locator('#search').fill(query);assert.equal(await visible(),expected);
      assert.equal(await page.locator('#count').innerText(),expected+' / 95');
    }
    await page.locator('#search').fill('');assert.equal(await visible(),95);
    const first=page.locator('.term-locations').first();
    await first.locator('summary').click();
    assert.equal(await first.getAttribute('open'),'');
    const firstId=await first.getAttribute('data-choice-id');
    const firstProof=proof.choices.find(r=>r.choice_id===firstId);
    assert.equal(await first.locator('q').first().innerText(),firstProof.matches[0].excerpt);
    for(const width of [1280,390]){
      await page.setViewportSize({width,height:width===390?844:900});
      await first.scrollIntoViewIfNeeded();
      await first.evaluate(el=>el.closest('tr').scrollIntoView({block:'start'}));
      assert.ok(await first.evaluate(el=>el.open));
      const dimensions=await page.evaluate(()=>({viewport:innerWidth,document:document.documentElement.scrollWidth}));
      assert.ok(dimensions.document<=dimensions.viewport+1,locale+' document overflows at '+width);
      if(width===390){
        assert.ok(await first.evaluate(el=>el.getBoundingClientRect().width>=innerWidth*.75),locale+' contextual prose is squeezed into a narrow phone column');
        assert.equal(await first.evaluate(el=>getComputedStyle(el.closest('tr')).display),'block');
      }
      if(screenshots){await fs.mkdir(screenshots,{recursive:true});await page.screenshot({path:path.join(screenshots,locale+'-'+width+'-concordance.png')});}
      checks.push({locale,width,open_context:true,no_document_horizontal_overflow:true});
    }
    const response=await page.request.get(origin+'/backend/a00/native-ledger/term-locations.json');
    assert.equal(response.status(),200);const downloaded=await response.body();
    assert.equal(hash(downloaded),hash(proofBytes));assert.equal(downloaded.length,proofBytes.length);
    await page.locator('nav a[href="'+teacher+'"]').first().click();
    assert.equal(new URL(page.url()).pathname,'/backend/a00/'+teacher);
    await page.locator('a[data-course-surface-contents][href="'+filename+'"]').first().click();
    assert.equal(new URL(page.url()).pathname,'/backend/a00/'+filename);
    await page.locator('nav a[href="'+course+'"]').first().click();
    assert.equal(new URL(page.url()).pathname,'/backend/a00/'+course);
    await page.locator('a[data-course-surface-contents][href="'+filename+'"]').first().click();
    const other=locale==='id'?'ledger-en.html':'ledger.html';
    await page.locator('nav a[href="'+other+'"]').first().click();
    assert.equal(await page.locator('html').getAttribute('lang'),locale==='id'?'en':'id');
  }
  assert.deepEqual(errors,[]);
  const inputs=await Promise.all(['docs/backend/a00/ledger.html','docs/backend/a00/ledger-en.html',proofPath,'scripts/test-a00-native-ledger-browser-v1.cjs'].map(fact));
  const report={schema:'a00-native-ledger-browser-checks/1',state:'pass',test_kind:'actual_headless_browser',browser_version:browser.version(),locales:2,visible_rows_per_locale:95,choice_details:20,choice_variant_matches:3419,filter_cases:8,checks,teacher_ledger_round_trip:true,learner_ledger_round_trip:true,language_switch:true,proof_download_byte_identity:true,external_requests_blocked:true,page_errors:errors,inputs,semantic_canon_review:false,overall_backend_complete:false};
  await fs.writeFile(path.join(root,'backend/course-capsule-v1/adapters/a00-native-ledger-v1/browser-checks.json'),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({state:'pass',test_kind:report.test_kind,viewports:checks.length,filter_cases:8,proof_download_byte_identity:true,teacher_ledger_round_trip:true,learner_ledger_round_trip:true}));
})().catch(e=>{console.error(e);process.exitCode=1;}).finally(async()=>{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));});
