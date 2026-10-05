import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {createServer} from 'node:http';
import {createRequire} from 'node:module';
import {dirname,resolve,extname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {clpOriginalSources} from '../docs/interface/clp-original-downloads.js';
import {resourceBindings,interfaceCourses} from '../docs/interface/view.js';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const out=resolve(root,'outputs/clp-original-downloads-v1');
const read=async p=>JSON.parse(await readFile(p,'utf8'));
const sha=b=>createHash('sha256').update(b).digest('hex');
const baseline=await read(resolve(out,'hub-parent/BASELINE.json'));
const proof=await read(resolve(root,'docs/interface/evidence/clp-original-downloads-v1.json'));
const ids=['B20','B30','B50','B60'];
assert.deepEqual(Object.keys(clpOriginalSources),ids);
const urls=new Set(Object.values(clpOriginalSources).flat().map(r=>r.href));
assert.equal(urls.size,12);
for(const book of proof.books){
  assert.equal(book.combined_pdf_claimed,false);
  assert.equal(book.pdf_source_reproduction_verified,false);
  assert.match(book.observed_source_commit,/^[0-9a-f]{40}$/);
  for(const locale of ['en','id']){
    const resources=resourceBindings(interfaceCourses.find(c=>c.id===book.course_id),locale).filter(r=>urls.has(r.href));
    assert.equal(resources.length,3);
    assert.deepEqual(resources.map(r=>r.kind),['PDF','PDF','repository']);
    for(const r of resources){
      assert.equal(r.contentLanguage,'en');assert.equal(r.labelLanguage,locale);
      assert.equal(r.authorityRole,'upstream-authority');assert.equal(r.accessRole,'authoritative-original');
      assert.ok(r.note);assert.ok(!r.primary);
    }
    for(const f of book.files){
      const r=resources.find(r=>r.href===f.url);assert.ok(r);assert.equal(r.bytes,f.bytes);assert.equal(r.sha256,f.sha256);
    }
  }
}
function removeAdded(value){
  if(Array.isArray(value))return value.filter(r=>!r||typeof r!=='object'||!urls.has(r.url)).map(removeAdded);
  if(value&&typeof value==='object')return Object.fromEntries(Object.entries(value).map(([k,v])=>[k,removeAdded(v)]));
  return value;
}
const before=await read(resolve(out,'hub-parent/docs/interface/learner-access-manifest.json'));
const current=await read(resolve(root,'docs/interface/learner-access-manifest.json'));
assert.deepEqual(removeAdded(current),before,'Only twelve original-source bindings may be added');
const cards=html=>new Map([...html.matchAll(/<article class="course-card" id="course-([^"]+)"[\s\S]*?<\/article>/g)].map(m=>[m[1],m[0]]));
for(const locale of ['id','en']){
  const path=`docs/${locale}/index.html`;
  const old=cards(await readFile(resolve(out,'hub-parent',path),'utf8'));
  const now=cards(await readFile(resolve(root,path),'utf8'));
  assert.equal(now.size,40);
  for(const [id,html] of old)if(!ids.includes(id))assert.equal(now.get(id),html,'Unrelated course card '+id);
}
const oldOverlay=await read(resolve(out,'hub-parent/backend/authority/central-course-surface-navigation-overlay-v1.json'));
const overlay=await read(resolve(root,'backend/authority/central-course-surface-navigation-overlay-v1.json'));
const altered=new Set(overlay.clp_original_download_refresh.documents);
assert.equal(overlay.files.length,oldOverlay.files.length);
for(let i=0;i<overlay.files.length;i++)if(!altered.has(overlay.files[i].document))assert.deepEqual(overlay.files[i],oldOverlay.files[i]);
const allowed=new Set(['docs/interface/view.js','docs/interface/original-sources.js','scripts/build-multilingual-interface.mjs','scripts/test-course-downloads-v1.mjs','docs/interface/learner-access-manifest.json','docs/interface/course-downloads-v1.json','docs/interface/build-receipt.json','backend/authority/central-course-surface-navigation-overlay-v1.json',...['id','en'].flatMap(l=>[`docs/${l}/index.html`,`docs/${l}/learning-map.html`,`docs/${l}/learning-map-paired.html`,`docs/${l}/downloads/index.html`])]);
const changed=[];
for(const row of baseline.files){
  const bytes=await readFile(resolve(root,row.path));
  if(sha(bytes)!==row.sha256){assert.ok(allowed.has(row.path),'Unexpected changed path '+row.path);changed.push({path:row.path,bytes:bytes.length,sha256:sha(bytes),previous_sha256:row.sha256});}
}

const require=createRequire(import.meta.url);
assert.ok(process.env.OPEN_COURSES_NODE_MODULES);
const {chromium}=require(resolve(process.env.OPEN_COURSES_NODE_MODULES,'playwright'));
const docs=resolve(root,'docs'),mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json'};
const server=createServer(async(req,res)=>{try{
  let path=decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname);if(path.endsWith('/'))path+='index.html';
  const full=resolve(docs,'.'+path);assert.ok(full.startsWith(docs+'\\')||full.startsWith(docs+'/'));
  const bytes=await readFile(full);res.writeHead(200,{'Content-Type':mime[extname(full)]??'application/octet-stream'});res.end(bytes);
}catch{res.writeHead(404);res.end('Not found');}});
await new Promise(done=>server.listen(0,'127.0.0.1',done));
const origin='http://127.0.0.1:'+server.address().port,checks=[],captures=[];
await mkdir(resolve(out,'captures'),{recursive:true});let browser;
try{
  browser=await chromium.launch({executablePath:resolve(process.env['ProgramFiles(x86)'],'Microsoft/Edge/Application/msedge.exe'),headless:true,args:['--disable-gpu','--no-first-run','--disable-background-networking']});
  for(const locale of ['id','en'])for(const width of [390,1280])for(const js of [false,true]){
    const context=await browser.newContext({viewport:{width,height:1000},javaScriptEnabled:js});
    await context.route('**/*',route=>route.request().url().startsWith(origin)?route.continue():route.abort());
    const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
    for(const file of ['index.html','learning-map.html','learning-map-paired.html']){
      await page.goto(`${origin}/${locale}/${file}#course-B20`,{waitUntil:'load'});
      assert.equal(await page.locator('.course-card').count(),40);
      for(const id of ids)for(const r of clpOriginalSources[id])assert.equal(await page.locator(`#course-${id} [data-access-group="authoritative-original"] a[href="${r.href}"]`).count(),1);
      assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Horizontal overflow');
      if(file==='index.html'&&width===390&&js){
        const group=page.locator('#course-B20 [data-access-group="authoritative-original"]');
        await group.scrollIntoViewIfNeeded();const path=`captures/${locale}-390-clp-originals.png`;
        const bytes=await group.screenshot({path:resolve(out,path)});captures.push({path,bytes:bytes.length,sha256:sha(bytes)});
        const other=locale==='id'?'en':'id';await page.locator(`[data-locale-link="${other}"]`).click();assert.equal(await page.locator('html').getAttribute('lang'),other);assert.ok(page.url().includes('#course-B20'));
      }
      checks.push({locale,width,js,file,twelve_original_links:true});
    }
    await page.goto(`${origin}/${locale}/downloads/`,{waitUntil:'load'});
    for(const book of proof.books)for(const f of book.files)assert.equal(await page.locator(`[data-course="${book.course_id}"] a[href="${f.url}"]`).count(),locale==='en'?1:0);
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));assert.deepEqual(errors,[]);
    checks.push({locale,width,js,file:'downloads',english_only_downloads:true});await context.close();
  }
}finally{await browser?.close();await new Promise(done=>server.close(done));}
const report={schema:'clp-additive-integration-validation/1',state:'pass',parent:baseline.parent,checked_utc:new Date().toISOString(),model:'gpt-6-astra',effort:'ultra',new_original_pdf_links:8,new_source_repository_links:4,unchanged_other_course_cards:36,all_prior_resource_bindings_preserved:true,unchanged_navigation_rows:overlay.files.length-altered.size,changed,checks,captures,external_runtime_blocked:true,limits:['No new translation or mathematical review.','Author-hosted sources and PDFs are not asserted to be a reproduced source pair.','Deployed byte verification is a separate publication receipt.']};
await writeFile(resolve(out,'VALIDATION.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({state:'pass',browser_cases:checks.length,changed_files:changed.length,captures}));
