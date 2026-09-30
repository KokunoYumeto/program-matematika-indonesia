/* Actual headless rendering checks for the two localized metadata replay guides. */
const assert=require('node:assert/strict');
const fs=require('node:fs/promises');
const path=require('node:path');
const http=require('node:http');
const crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),docs=path.join(root,'docs');
const playwright=require(process.env.D70_PLAYWRIGHT_PACKAGE||'playwright');
const digest=b=>crypto.createHash('sha256').update(b).digest('hex');
const fact=async name=>{const b=await fs.readFile(path.join(root,name));return {path:name,bytes:b.length,sha256:digest(b)};};
const mime={'.html':'text/html; charset=utf-8','.json':'application/json','.zip':'application/zip'};
const server=http.createServer(async(req,res)=>{
 try{
  const pathname=decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname);
  const filename=path.resolve(docs,'.'+pathname),relative=path.relative(docs,filename);
  if(relative.startsWith('..')||path.isAbsolute(relative)){res.writeHead(403);res.end();return;}
  const bytes=await fs.readFile(filename);res.writeHead(200,{'Content-Type':mime[path.extname(filename)]||'application/octet-stream'});res.end(bytes);
 }catch{res.writeHead(404);res.end();}
});
let browser;
(async()=>{
 await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',resolve);});
 const origin='http://127.0.0.1:'+server.address().port;
 browser=await playwright.chromium.launch({headless:true,executablePath:process.env.D70_BROWSER_EXECUTABLE||undefined,args:['--disable-background-networking','--no-first-run']});
 const context=await browser.newContext(),external=[];
 await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();external.push(route.request().url());return route.abort();});
 const page=await context.newPage(),errors=[];page.setDefaultTimeout(12000);page.on('pageerror',e=>errors.push(e.message));
 const checks=[];
 for(const locale of ['id','en']){
  const name=locale==='en'?'index.en.html':'index.html';
  await page.goto(origin+'/backend/d70-replay/'+name,{waitUntil:'networkidle'});
  assert.equal(await page.locator('html').getAttribute('lang'),locale);
  assert.match(await page.locator('h1').innerText(),locale==='en'?/reproduce native metadata/:/bangun ulang metadata native/);
  const link=page.locator('main a[href="D70_NATIVE_METADATA_REPLAY_V1.zip"]');
  assert.match(await link.innerText(),locale==='en'?/Download/:/Unduh/);
  const response=await page.request.get(origin+'/backend/d70-replay/D70_NATIVE_METADATA_REPLAY_V1.zip');
  assert.equal(response.status(),200);const bundle=await response.body();assert.equal(bundle.length,3001559);assert.equal(digest(bundle),'cde3a053dc0c16e6056c6827f05bf955c1f511c375d02e4e8d404db084bf850c');
  const guide=await page.locator('main').innerText();assert.match(guide,/13/);assert.match(guide,/26/);assert.match(guide,/Python 3\.10/);
  assert.match(guide,locale==='en'?/not reproduction of the full Li reader/:/bukan membuktikan produksi ulang seluruh pembaca Li/);
  assert.ok(await page.locator('main a[href="validation.json"]').count());
  assert.match(await page.locator('pre code').innerText(),/--bundle D70_NATIVE_METADATA_REPLAY_V1\.zip --source-archive 05_o013-sumber-backend-1\.0\.0\.zip/);
  for(const width of [1280,390]){
   await page.setViewportSize({width,height:width===390?844:900});await page.evaluate(()=>scrollTo(0,0));
   const dimensions=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth}));assert.ok(dimensions.scroll<=dimensions.width+1,'Horizontal overflow: '+locale+' '+width);
   const languageLink=page.locator('main nav a').first();await languageLink.focus();assert.equal(await languageLink.evaluate(el=>document.activeElement===el),true);
   assert.notEqual(await languageLink.evaluate(el=>getComputedStyle(el).outlineStyle),'none');
   if(process.env.D70_BROWSER_SCREENSHOTS){await fs.mkdir(process.env.D70_BROWSER_SCREENSHOTS,{recursive:true});await page.screenshot({path:path.join(process.env.D70_BROWSER_SCREENSHOTS,locale+'-'+width+'.png')});}
   checks.push({locale,viewport_width:width,no_horizontal_overflow:true,localized_instructions:true,keyboard_focus_visible:true,local_bundle_download_hash_verified:true});
  }
  await page.locator('main nav a[href="../d70/D70-pengajar.html"]').click();
  assert.equal(await page.locator('li[id^="d70-batas-"]').count(),8);
  assert.match(await page.locator('#d70-batas-07').innerText(),/teknologi pendukung/);
  assert.match(await page.locator('#d70-batas-08').innerText(),/belum terbukti/);
  await page.locator('#d70-batas-review a').click();
  assert.equal(await page.locator('html').getAttribute('lang'),'id');
  assert.equal(await page.locator('blockquote[lang="en"]').count(),8);
  assert.ok(await page.locator('main a[href="metadata-localization-choices.id.json"]').count());
  const reviewDimensions=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth}));
  assert.ok(reviewDimensions.scroll<=reviewDimensions.width+1,'Localized review horizontal overflow');
  await page.locator('main nav a[href="../d70/D70.html"]').click();
  assert.equal(await page.locator('li[id^="d70-batas-"]').count(),8);
  await page.locator('#d70-batas-review a').click();
  await page.locator('main nav a[href="../d70/D70-pengajar.html"]').click();
  const teacherSection=page.locator('#d70-metadata-replay');await teacherSection.scrollIntoViewIfNeeded();
  assert.ok(await teacherSection.evaluate(el=>{const r=el.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth+1;}),'Replay section exceeds teacher viewport');
  if(locale==='id'&&process.env.D70_BROWSER_SCREENSHOTS)await page.screenshot({path:path.join(process.env.D70_BROWSER_SCREENSHOTS,'teacher-390.png')});
  await page.locator('#d70-metadata-replay a[href="../d70-replay/'+name+'"]').click();
  assert.equal(await page.locator('html').getAttribute('lang'),locale);
  const opposite=locale==='id'?'en':'id';await page.locator('main nav a').first().click();assert.equal(await page.locator('html').getAttribute('lang'),opposite);
 }
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
 const inputs=await Promise.all(['docs/backend/d70-replay/index.html','docs/backend/d70-replay/index.en.html','docs/backend/d70/D70-pengajar.html','docs/backend/d70/D70.html','docs/backend/d70-replay/limitations-review.id.html','docs/backend/d70-replay/metadata-localization-choices.id.json','docs/backend/d70-replay/D70_NATIVE_METADATA_REPLAY_V1.zip','scripts/test-d70-native-replay-browser-v1.cjs'].map(fact));
 const report={schema:'d70-native-metadata-replay-browser-checks/1',state:'pass',test_kind:'actual_headless_browser',browser_version:browser.version(),locales:2,checks,language_switch:true,teacher_replay_round_trip:true,localized_limitation_occurrences:16,localized_review_navigation:true,external_requests_blocked:true,external_request_count:external.length,page_errors:errors,inputs,whole_native_parity_proven:false,semantic_canon_review:false,overall_backend_complete:false};
 await fs.writeFile(path.join(root,'backend/course-capsule-v1/adapters/d70-native-replay-v1/browser-checks.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({state:'pass',test_kind:report.test_kind,locales:2,viewport_cases:checks.length,language_switch:true,local_bundle_download_hash_verified:true}));
})().catch(error=>{console.error(error);process.exitCode=1;}).finally(async()=>{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));});
