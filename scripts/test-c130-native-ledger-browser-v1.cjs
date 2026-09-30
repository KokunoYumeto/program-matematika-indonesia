/* Actual headless-browser checks; no desktop window, external requests or producer edits. */
const assert=require('node:assert/strict');
const fs=require('node:fs/promises');
const path=require('node:path');
const http=require('node:http');
const crypto=require('node:crypto');
const root=path.resolve(__dirname,'..');
const docs=path.join(root,'docs');
const playwright=require(process.env.C130_PLAYWRIGHT_PACKAGE||'playwright');
const shotRoot=process.env.C130_BROWSER_SCREENSHOTS;
const fact=async p=>{const b=await fs.readFile(path.join(root,p));return {path:p,bytes:b.length,sha256:crypto.createHash('sha256').update(b).digest('hex')};};
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json','.css':'text/css; charset=utf-8'};
const server=http.createServer(async(req,res)=>{
 try{
  const pathname=decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname);
  const filename=path.resolve(docs,'.'+pathname);
  if(path.relative(docs,filename).startsWith('..')||path.isAbsolute(path.relative(docs,filename))){res.writeHead(403);res.end();return;}
  const b=await fs.readFile(filename);res.writeHead(200,{'Content-Type':mime[path.extname(filename)]||'application/octet-stream'});res.end(b);
 }catch{res.writeHead(404);res.end();}
});
let browser;
(async()=>{
 await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',resolve);});
 const origin='http://127.0.0.1:'+server.address().port;
 browser=await playwright.chromium.launch({headless:true,executablePath:process.env.C130_BROWSER_EXECUTABLE||undefined,args:['--disable-background-networking','--no-first-run']});
 const context=await browser.newContext();
 await context.route('**/*',route=>new URL(route.request().url()).origin===origin?route.continue():route.abort());
 const page=await context.newPage();page.setDefaultTimeout(12000);
 const errors=[];page.on('pageerror',error=>errors.push(error.message));
 const checks=[];
 for(const locale of ['id','en']){
  const suffix=locale==='en'?'.en':'';
  await page.setViewportSize({width:1280,height:900});
  await page.goto(origin+'/backend/c130-native/ledger'+suffix+'.html',{waitUntil:'networkidle'});
  assert.equal(await page.locator('html').getAttribute('lang'),locale);
  assert.equal(await page.locator('#location-review .location-proof').count(),21);
  const proof=page.locator('#location-review .location-proof[data-segment-id="segment.r017.book1.ch07.text.block-133"]');
  await proof.locator('summary').click();
  assert.ok((await proof.innerText()).includes('42c1640cd736a36e55d812fa58c696edbaa56958b02a2cd17c2cc301d0b30179'));
  const reviewResponse=await page.request.get(origin+'/backend/c130-native/location-review.json');
  assert.equal(reviewResponse.status(),200);assert.equal((await reviewResponse.json()).records.length,21);
  const visible=()=>page.locator('.record:visible').count();
  assert.equal(await visible(),234);
  await page.locator('#kind').selectOption('term');assert.equal(await visible(),140);
  await page.locator('#kind').selectOption('correction');assert.equal(await visible(),94);
  await page.locator('#kind').selectOption('');
  await page.locator('#query').fill('term.additivity.id');assert.equal(await visible(),1);
  await page.locator('.record:visible summary').first().click();
  assert.equal(await page.locator('.record:visible details').first().getAttribute('open'),'');
  const labelled=await page.locator('#query').evaluate(el=>el.labels.length);
  assert.ok(labelled>0);assert.equal(await page.locator('#count').getAttribute('aria-live'),'polite');
  for(const width of [1280,390]){
   await page.setViewportSize({width,height:width===390?844:900});
   const sourceIdentity=page.locator('.record:visible details p').first();
   await sourceIdentity.scrollIntoViewIfNeeded();
   assert.ok(await sourceIdentity.evaluate(el=>{const r=el.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight;}),locale+' source identity is outside viewport');
   const dimensions=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth}));
   assert.ok(dimensions.scroll<=dimensions.width+1,locale+' horizontal overflow at '+width);
   await proof.scrollIntoViewIfNeeded();
   assert.ok(await proof.locator('details').evaluate(el=>el.open),locale+' review proof is not expanded');
   assert.ok((await page.evaluate(()=>document.documentElement.scrollWidth))<=width+1,locale+' review proof overflows at '+width);
   if(shotRoot){await fs.mkdir(shotRoot,{recursive:true});await proof.screenshot({path:path.join(shotRoot,locale+'-'+width+'-alignment-proof.png')});}
   await sourceIdentity.scrollIntoViewIfNeeded();
   if(shotRoot){await fs.mkdir(shotRoot,{recursive:true});await page.screenshot({path:path.join(shotRoot,locale+'-'+width+'.png')});}
   checks.push({locale,viewport_width:width,no_horizontal_overflow:true,filtered_record_and_source_reference_visible:true});
  }
  await page.locator('#query').fill('LINEARISASI NILAI MUTLAK');assert.equal(await visible(),1);
  await page.locator('#query').fill('CORR-CH10-MATRIX-AN-SIGNS');assert.equal(await visible(),1);
  await page.locator('#kind').selectOption('term');assert.equal(await visible(),0);
  await page.locator('#kind').selectOption('');await page.locator('#query').fill('no-such-record-234');assert.equal(await visible(),0);
  await page.locator('#query').fill('');assert.equal(await visible(),234);
  await page.locator('a[data-course-surface-contents][href="../c130-teacher/C130.teacher'+suffix+'.html"]').first().click();
  assert.equal(new URL(page.url()).pathname,'/backend/c130-teacher/C130.teacher'+suffix+'.html');
  await page.locator('a[data-course-surface-contents][href="../c130-native/ledger'+suffix+'.html"]').first().click();
  assert.equal(new URL(page.url()).pathname,'/backend/c130-native/ledger'+suffix+'.html');
  const other=locale==='id'?'.en':'';
  await page.locator('header nav a[href="ledger'+other+'.html"]').click();
  assert.equal(await page.locator('html').getAttribute('lang'),locale==='id'?'en':'id');
 }
 assert.deepEqual(errors,[]);
 const inputs=await Promise.all(['docs/backend/c130-native/ledger.html','docs/backend/c130-native/ledger.en.html','docs/backend/c130-native/ledger.js','docs/backend/c130-native/ledger.css','docs/backend/c130-native/location-review.json','scripts/test-c130-native-ledger-browser-v1.cjs'].map(fact));
 const report={schema:'c130-native-ledger-browser-checks/1',state:'pass',test_kind:'actual_headless_browser',browser_version:browser.version(),locales:2,visible_records:234,terms:140,corrections:94,filter_cases:18,location_review_records:21,alignment_file_mismatch_visible:true,source_details_opened:true,teacher_ledger_round_trip:true,language_switch:true,external_requests_blocked:true,page_errors:errors,checks,inputs,semantic_canon_review:false,overall_backend_complete:false};
 await fs.writeFile(path.join(root,'backend/course-capsule-v1/adapters/c130-native-ledger-v1/browser-checks.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({state:report.state,test_kind:report.test_kind,filter_cases:report.filter_cases,viewports:checks.length,teacher_ledger_round_trip:true,language_switch:true}));
})().catch(error=>{console.error(error);process.exitCode=1;}).finally(async()=>{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));});
