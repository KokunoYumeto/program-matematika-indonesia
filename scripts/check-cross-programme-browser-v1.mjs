import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createServer} from 'node:http';
import {createHash} from 'node:crypto';
import {resolve,dirname,extname} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const dir=resolve(root,'backend/cross-programme-v1');
const current=process.argv.includes('--current');
const advancedCount=current?72:71;
const docs=current?resolve(root,'docs'):resolve(dir,'public-staging/docs');
const captureDir=current?'current-browser-captures':'browser-captures';
const require=createRequire(import.meta.url);
assert.ok(process.env.OPEN_COURSES_NODE_MODULES,'Set OPEN_COURSES_NODE_MODULES to the supplied dependency runtime; no installation is needed');
const {chromium}=require(resolve(process.env.OPEN_COURSES_NODE_MODULES,'playwright'));
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json'};
const server=createServer(async(req,res)=>{try{let path=decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname);if(path.endsWith('/'))path+='index.html';const full=resolve(docs,'.'+path);assert.ok(full.startsWith(docs+'/')||full.startsWith(docs+'\\'));const b=await readFile(full);res.writeHead(200,{'Content-Type':mime[extname(full)]??'application/octet-stream'});res.end(b);}catch{res.writeHead(404);res.end('Not in the exact bounded test fixture');}});
await new Promise(done=>server.listen(0,'127.0.0.1',done));const origin='http://127.0.0.1:'+server.address().port;
await mkdir(resolve(dir,captureDir),{recursive:true});let browser;
const checks=[],captures=[];
try{
  const browserPath=process.env.OPEN_COURSES_BROWSER_EXECUTABLE??resolve(process.env['ProgramFiles(x86)'],'Microsoft/Edge/Application/msedge.exe');
  browser=await chromium.launch({executablePath:browserPath,headless:true,args:['--disable-gpu','--no-first-run','--disable-background-networking']});
  for(const locale of ['en','id'])for(const width of [1280,390,320]){
    const context=await browser.newContext({viewport:{width,height:900},javaScriptEnabled:false});
    await context.route('**/*',route=>route.request().url().startsWith(origin)?route.continue():route.abort());const page=await context.newPage();
    await page.goto(origin+'/'+locale+'/programme/',{waitUntil:'load'});assert.equal(await page.locator('section[id^="core-"]').count(),40);assert.equal(await page.locator('section[id^="advanced-"]').count(),advancedCount);
    const overflow=await page.evaluate(()=>({inner:innerWidth,document:document.documentElement.scrollWidth}));assert.ok(overflow.document<=overflow.inner+1,'Horizontal overflow '+locale+' '+width);
    const proofNotice=await page.locator('.notice').innerText();assert.ok(proofNotice.length>100);
    if(current){
      for(const courseId of ['derived-categories-and-sheaf-operations','harmonic-analysis-on-locally-compact-groups']){
        const section=page.locator('aside[data-portable-course="'+courseId+'"]');
        assert.equal(await section.count(),1);
        assert.deepEqual(await section.locator('[data-portable-format]').evaluateAll(nodes=>nodes.map(n=>n.dataset.portableFormat)),['pdf','tex','zip','epub']);
        const href=await section.locator('[data-portable-reader]').getAttribute('href');
        assert.ok(href.endsWith('index.'+locale+'.html'));
        if(width===390&&courseId==='harmonic-analysis-on-locally-compact-groups'){
          await section.scrollIntoViewIfNeeded();
          const path=captureDir+'/'+locale+'-390-portable-haar.png';
          const bytes=await page.screenshot({path:resolve(dir,path),fullPage:false});
          captures.push({path,bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex')});
        }
        await page.goto(origin+new URL(href).pathname.replace('/program-matematika-indonesia',''));
        assert.equal(await page.locator('html').getAttribute('lang'),locale);
        assert.equal(await page.locator('.downloads a').count(),4);
        assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
        await page.goto(origin+'/'+locale+'/programme/');
      }
      checks.push({locale,width,portable_course_routes:2,localized_reader_targets:true,ordered_formats:['pdf','tex','zip','epub'],horizontal_overflow:false});
      assert.equal(await page.locator('[data-advanced-snapshot="801f1868"]').count(),1);
      const b40Expanded=page.locator('#core-B40 a[data-b40-expanded="v1"]');
      assert.equal(await b40Expanded.count(),1);
      assert.ok((await b40Expanded.innerText()).includes(locale==='en'?'34 sections through Complex Vector Spaces':'34 bagian hingga Ruang Vektor Kompleks'));
      assert.equal(await page.locator('#advanced-AG-RG details ol li').count(),6);
      const route=JSON.parse(await readFile(resolve(dir,'d80-prerequisite-route-v1.json')));
      const provider=page.locator('#core-D80 aside[data-d80-prerequisite="provider"]');
      assert.equal(await provider.locator('a[hreflang="en"]').count(),6);
      const diagramNotice=provider.locator('[data-d80-reader-notice]');
      assert.ok(await diagramNotice.isVisible());
      assert.ok((await diagramNotice.innerText()).includes(route.reader_notice.text[locale]));
      assert.equal(await diagramNotice.locator('a[href="'+route.reader_notice.pdf.url+'"]').count(),1);
      for(const reading of route.readings)assert.equal(await provider.locator('a[href="'+reading.url+'"]').count(),1);
      await provider.locator('a[data-d80-programme-step="provider"]').click();
      assert.ok(page.url().endsWith('#advanced-'+route.consumer_course));
      await page.locator('a[data-d80-programme-step="consumer"]').click();assert.ok(page.url().endsWith('#core-D80'));
      await provider.locator('details summary').click();
      assert.ok((await provider.innerText()).includes(route.use_loci[1].comparison[locale]));
      const openOverflow=await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1);assert.ok(openOverflow,'D80 notes overflow');
      if(width!==320){await provider.scrollIntoViewIfNeeded();const path=captureDir+'/'+locale+'-'+width+'-D80-prerequisite.png';const b=await page.screenshot({path:resolve(dir,path),fullPage:false});captures.push({path,bytes:b.length,sha256:createHash('sha256').update(b).digest('hex')});}
      checks.push({locale,width,d80_forward_reverse_clicks:'pass',three_exact_english_source_links:true,localized_use_notes:true,visible_five_lemma_diagram_notice:true,correct_pdf_page_link:true,horizontal_overflow:false});
    }
    if(width!==320){await page.locator('#core-B40').scrollIntoViewIfNeeded();const path=captureDir+'/'+locale+'-'+width+'-core-B40.png';const b=await page.screenshot({path:resolve(dir,path),fullPage:false});captures.push({path,bytes:b.length,sha256:createHash('sha256').update(b).digest('hex')});}
    await page.locator(current?'a[data-b40-programme-step="provider"]':'#core-B40 a[href="#advanced-RT-FIN"]').click();assert.ok(page.url().endsWith('#advanced-RT-FIN'));await page.locator(current?'a[data-b40-programme-step="consumer"]':'#advanced-RT-FIN a[href="#core-B40"]').click();assert.ok(page.url().endsWith('#core-B40'));
    checks.push({locale,width,mode:'javascript_disabled',course_sections:40+advancedCount,forward_reverse_clicks:'pass',horizontal_overflow:false,remote_runtime_blocked:true});await context.close();
  }
  if(current)for(const width of [1280,390,320]){
    const context=await browser.newContext({viewport:{width,height:900},javaScriptEnabled:false});
    await context.route('**/*',route=>route.request().url().startsWith(origin)?route.continue():route.abort());
    const page=await context.newPage();await page.goto(origin+'/en/readers/basis-projection-bridge/',{waitUntil:'load'});
    assert.equal(await page.locator('math').count(),167);
    assert.equal(await page.locator('nav').count(),2);
    assert.equal(await page.locator('a[href="00-basis-projection.tex"]').count(),1);
    assert.equal(await page.locator('a[href="01-editable-source.zip"]').count(),1);
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Proof reader horizontal overflow');
    await page.locator('#extending-a-basis-and-choosing-a-complement').scrollIntoViewIfNeeded();
    if(width!==320){const path=captureDir+'/en-'+width+'-B40-proof-bridge.png';const bytes=await page.screenshot({path:resolve(dir,path),fullPage:false});captures.push({path,bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex')});}
    checks.push({locale:'en',width,reader:'basis-projection-bridge',native_mathml_formulas:167,no_remote_math_runtime:true,horizontal_overflow:false,direct_latex_and_zip_links:true});
    await context.close();
  }
  for(const locale of ['en','id'])for(const name of ['index.html','learning-map.html','learning-map-paired.html']){
    const context=await browser.newContext({viewport:{width:390,height:900}});await context.route('**/*',route=>route.request().url().startsWith(origin)?route.continue():route.abort());const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(String(e)));
    await page.goto(origin+'/'+locale+'/'+name,{waitUntil:'networkidle'});assert.equal(await page.locator('a[data-cross-programme-course]').count(),40);assert.equal(await page.locator('.course-card').count(),40);
    if(current)assert.ok(await page.locator('#course-D60 a[href*="native-ledger"]').count()>0,'D60 native tools must coexist with advanced routes');
    await page.locator('#search').fill('linear');await page.waitForTimeout(150);assert.equal(await page.locator('#course-B40 a[data-cross-programme-course="B40"]').count(),1);
    assert.deepEqual(errors,[],'Current public runtime regression '+locale+' '+name);
    checks.push({locale,page:name,mode:'javascript_enabled',initial_links:40,re_render_B40_link:'pass',runtime_errors:0,remote_runtime_blocked:true});await context.close();
  }
}finally{if(browser)await browser.close();await new Promise(done=>server.close(done));}
const receipt={schema:'cross-programme-headless-browser-qa/1',status:'pass',engine:'Chromium browser, headless; no visible browser window',current_checkout:current,checks,captures,capture_inspection:'pending_actual_visual_inspection',native_readers_or_learner_state_modified:false};await writeFile(resolve(dir,current?'CURRENT_BROWSER_VALIDATION.json':'BROWSER_VALIDATION.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify({status:'pass',checks:checks.length,captures:captures.length,no_visible_window:true}));
