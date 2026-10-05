import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {resolve,dirname} from 'node:path';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'../..');
const language=process.env.A00_HUB_LANGUAGE??'id';
assert.ok(['id','en'].includes(language));
const out=resolve(root,language==='en'?'outputs/a00-english-portable-formats-v1':'outputs/a00-portable-formats-v1');
const addedCount=language==='en'?4:5;
const read=async path=>JSON.parse(await readFile(path,'utf8'));
const baseline=await read(resolve(out,'hub-parent/BASELINE.json'));
const previous=await read(resolve(out,'hub-parent/docs/interface/learner-access-manifest.json'));
const current=await read(resolve(root,'docs/interface/learner-access-manifest.json'));
const {supplementalReaders}=await import('../../docs/interface/supplemental-readers.js');
const newRows=supplementalReaders.filter(r=>r.courseId==='A00'&&r.id.startsWith(`A00:${language}-format-`));
assert.equal(newRows.length,addedCount);
const urls=new Set(newRows.map(r=>r.href));
function removeAdded(value){
 if(Array.isArray(value))return value.filter(r=>!r||typeof r!=='object'||!urls.has(r.url)).map(removeAdded);
 if(value&&typeof value==='object')return Object.fromEntries(Object.entries(value).map(([k,v])=>[k,removeAdded(v)]));
 return value;
}
assert.deepEqual(removeAdded(current),previous,'Only the selected A00 resource bindings may change');
const cards=text=>new Map([...text.matchAll(/<article class="course-card" id="course-([^"]+)"[\s\S]*?<\/article>/g)].map(m=>[m[1],m[0]]));
const anchors=text=>[...text.matchAll(/<a\b[^>]*href="([^"]+)"[^>]*>/g)].map(m=>m[0]).sort();
const notes=text=>[...new Set([...text.matchAll(/<p class="footnote"[^>]*>(.*?)<\/p>/g)].map(m=>m[1]))].sort();
const cardChecks=[];
for(const lang of ['id','en']){
 const path=`docs/${lang}/index.html`;
 const old=cards(await readFile(resolve(out,'hub-parent',path),'utf8'));
 const now=cards(await readFile(resolve(root,path),'utf8'));
 assert.equal(now.size,40);assert.deepEqual([...now.keys()],[...old.keys()]);
 for(const [id,html] of old){
  if(id==='A00')continue;
  if(id==='B80'&&language==='id'){
   assert.deepEqual(anchors(now.get(id)),anchors(html));
   assert.deepEqual(notes(now.get(id)),notes(html));
  }else assert.equal(now.get(id),html,id+' unrelated course changed');
 }
 cardChecks.push({locale:lang,unchanged_course_cards:language==='en'?39:38,b80_links_and_unique_notes_preserved:true});
}
const previousSupplement=await readFile(resolve(out,'hub-parent/docs/interface/supplemental-readers.js'),'utf8');
const currentSupplement=await readFile(resolve(root,'docs/interface/supplemental-readers.js'),'utf8');
const block=language==='en'?/  \/\/ BEGIN A00 ENGLISH FORMAT PAIRS\n[\s\S]*?  \/\/ END A00 ENGLISH FORMAT PAIRS\n/:/  \/\/ BEGIN A00 FORMAT PAIRS\n[\s\S]*?  \/\/ END A00 FORMAT PAIRS\n/;
assert.equal(currentSupplement.replace(block,''),previousSupplement.replaceAll('\r\n','\n'));
const oldOverlay=await read(resolve(out,'hub-parent/backend/authority/central-course-surface-navigation-overlay-v1.json'));
const overlay=await read(resolve(root,'backend/authority/central-course-surface-navigation-overlay-v1.json'));
assert.equal(overlay.files.length,oldOverlay.files.length);
const altered=new Set(overlay[language==='en'?'a00_english_format_link_refresh':'a00_format_link_refresh'].documents);
for(let i=0;i<overlay.files.length;i++)if(!altered.has(overlay.files[i].document))assert.deepEqual(overlay.files[i],oldOverlay.files[i]);
const changed=[];
for(const fact of baseline.files){
 const bytes=await readFile(resolve(root,fact.path));const sha256=createHash('sha256').update(bytes).digest('hex');
 if(sha256!==fact.sha256)changed.push({path:fact.path,bytes:bytes.length,sha256,previous_sha256:fact.sha256});
}
const permitted=new Set(['docs/interface/view.js','docs/interface/locales.js','docs/interface/supplemental-readers.js','docs/interface/learner-access-manifest.json','docs/interface/course-downloads-v1.json','docs/interface/build-receipt.json','backend/authority/central-course-surface-navigation-overlay-v1.json','scripts/test-multilingual-interface.mjs','scripts/test-course-downloads-v1.mjs',...['id','en'].flatMap(l=>[`docs/${l}/index.html`,`docs/${l}/learning-map.html`,`docs/${l}/learning-map-paired.html`,`docs/${l}/downloads/index.html`])]);
if(language==='en')for(const name of ['capture_hub_parent.py','restore_hub_navigation.py','check_hub_additive.mjs','check_hub_browser.mjs','publish_hub.py'])permitted.add('scripts/a00-portable-formats-v1/'+name);
for(const fact of changed)assert.ok(permitted.has(fact.path),'Unexpected changed file '+fact.path);
const report={state:'pass',parent:baseline.parent,resource_data:`All prior resources preserved; only ${addedCount} ${language} A00 links added`,cardChecks,unchanged_other_navigation_rows:overlay.files.length-altered.size,changed};
await writeFile(resolve(out,'HUB_ADDITIVE_CHECK.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({state:'pass',changed_files:changed.length,new_a00_links:addedCount,other_course_resources_unchanged:39,cardChecks}));
