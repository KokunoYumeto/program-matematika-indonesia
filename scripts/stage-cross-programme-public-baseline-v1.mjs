import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,resolve,posix} from 'node:path';
import {fileURLToPath} from 'node:url';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const packageRoot=resolve(root,'backend/cross-programme-v1');
const baseline=resolve(packageRoot,'current-public-baseline');
const stage=resolve(packageRoot,'public-staging');
const hash=b=>createHash('sha256').update(b).digest('hex');
const asJson=b=>JSON.parse(b.toString('utf8'));
const serialize=x=>Buffer.from(JSON.stringify(x,null,2)+'\n');
const fact=(path,b)=>({path,bytes:b.length,sha256:hash(b)});
const args=new Set(process.argv.slice(2));
const freeze=asJson(await readFile(resolve(packageRoot,'inputs/20261002/MANIFEST.json')));
const commit=freeze.commits.core.commit;
const repo='https://raw.githubusercontent.com/KokunoYumeto/program-matematika-indonesia/'+commit+'/';
async function frozenWrite(path,b){
  await mkdir(dirname(path),{recursive:true});
  try{assert.deepEqual(await readFile(path),b,'Refusing to overwrite a frozen public input');return;}
  catch(e){if(e.code!=='ENOENT')throw e;}
  await writeFile(path,b,{flag:'wx'});
}
if(args.has('--capture')){
  const pages=['en','id'].flatMap(locale=>['index.html','learning-map.html','learning-map-paired.html'].map(name=>'docs/'+locale+'/'+name));
  const pending=[...pages,'docs/interface/view.js','docs/interface/app.js','docs/interface/styles.css','docs/interface/locales.js','scripts/build-multilingual-interface.mjs'];
  const seen=new Set(),files=[];let total=0;
  while(pending.length){
    const path=pending.shift();if(seen.has(path))continue;seen.add(path);
    assert.ok(seen.size<=64,'Bounded public-module closure exceeds 64 files');
    assert.ok(!path.includes('..')&&!path.startsWith('/')&&/^(docs|scripts)\//.test(path));
    const response=await fetch(repo+path,{signal:AbortSignal.timeout(30000),headers:{'User-Agent':'Open-Courses-exact-baseline'}});
    assert.equal(response.status,200,'Missing pinned public baseline '+path);
    const bytes=Buffer.from(await response.arrayBuffer());total+=bytes.length;
    assert.ok(bytes.length<=16*1024*1024&&total<=96*1024*1024,'Baseline byte bound exceeded');
    await frozenWrite(resolve(baseline,path),bytes);files.push({...fact(path,bytes),url:repo+path});
    // Only follow actual relative imports in reader runtime modules. Build-tool
    // inputs are not enumerated, and native course bodies are never acquired.
    if(path.startsWith('docs/')&&path.endsWith('.js')){
      for(const m of bytes.toString('utf8').matchAll(/\bimport\s+[\s\S]*?\sfrom\s*['"]([^'"]+)['"]/g)){
        if(!m[1].startsWith('.'))continue;
        const target=posix.normalize(posix.join(posix.dirname(path),m[1]));
        assert.ok(target.startsWith('docs/')&&target.endsWith('.js'),'Unexpected runtime import '+target);
        pending.push(target);
      }
    }
  }
  const manifest={schema:'current-public-interface-baseline/1',source_commit:commit,source_tree:freeze.commits.core.tree,files:files.sort((a,b)=>a.path.localeCompare(b.path)),total_bytes:total,no_local_checkout_assumed_current:true};
  await frozenWrite(resolve(baseline,'MANIFEST.json'),serialize(manifest));
  console.log(JSON.stringify({state:'baseline_frozen',files:files.length,bytes:total,commit}));process.exit(0);
}
const manifest=asJson(await readFile(resolve(baseline,'MANIFEST.json')));
assert.equal(manifest.source_commit,commit);
const sources=new Map();for(const row of manifest.files){const b=await readFile(resolve(baseline,row.path));assert.equal(b.length,row.bytes);assert.equal(hash(b),row.sha256);sources.set(row.path,b);}
const bridge=asJson(await readFile(resolve(packageRoot,'bridge.json')));
const routeBytes=await readFile(resolve(root,'docs/interface/cross-programme-routes.js'));
const routeText=routeBytes.toString('utf8');
const routeRows=JSON.parse(routeText.match(/Object\.freeze\((\{.*\})\);/s)[1]);
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
function link(id,locale){assert.ok(routeRows[id]?.[locale]);return '<p class="cross-programme-route"><a data-cross-programme-course="'+id+'" href="'+esc(routeRows[id][locale])+'">'+(locale==='id'?'Open Courses: persiapan dan studi lanjutan':'Open Courses: preparation and further study')+'</a></p>';}
const originalView=sources.get('docs/interface/view.js').toString('utf8');
const oldMarker="  const t = interfaceCopy[locale], c = coursePresentation(course, locale);";
assert.equal(originalView.split(oldMarker).length,2,'View insertion marker must be unique');
const viewAddition="\n  const furtherRoute = crossProgrammeRoutes[course.id];\n  if (!furtherRoute?.[locale]) throw new Error('Missing cross-programme native course route: ' + course.id + ' ' + locale);\n  const furtherLabel = locale === 'id' ? 'Open Courses: persiapan dan studi lanjutan' : 'Open Courses: preparation and further study';\n  const furtherLink = '<p class=\"cross-programme-route\"><a data-cross-programme-course=\"' + course.id + '\" href=\"' + escapeMarkup(furtherRoute[locale]) + '\">' + furtherLabel + '</a></p>';";
const oldEnd="+ '<div class=\"resource-list\">' + renderResourceLinks(course, locale) + '</div></article>';";
const newEnd="+ '<div class=\"resource-list\">' + renderResourceLinks(course, locale) + '</div>' + furtherLink + '</article>';";
assert.equal(originalView.split(oldEnd).length,2,'View end marker must be unique');
const importLine="import { crossProgrammeRoutes } from './cross-programme-routes.js';\n";
const changedView=importLine+originalView.replace(oldMarker,oldMarker+viewAddition).replace(oldEnd,newEnd);
assert.equal(changedView.replace(importLine,'').replace(viewAddition,'').replace(newEnd,oldEnd),originalView,'Runtime source preservation failed');
const outputs=new Map(sources);outputs.set('docs/interface/view.js',Buffer.from(changedView));
const changed=[];
const productionLabel=locale=>locale==='id'?'Integrasi tautan lintas program dikerjakan oleh OpenAI Codex — GPT-6.1 Sol, tingkat upaya Ultra; tidak ada klaim peninjauan manusia.':'Cross-programme link integration produced by OpenAI Codex — GPT-6.1 Sol, Ultra effort; no human review is claimed.';
for(const locale of ['en','id'])for(const name of ['index.html','learning-map.html','learning-map-paired.html']){
  const path='docs/'+locale+'/'+name;const original=sources.get(path).toString('utf8');let count=0;
  let target=original.replace(/(<article\b[^>]*\bid="course-([A-Z]\d+)"[\s\S]*?)(<\/article>)/g,(all,body,id,end)=>{count++;return body+link(id,locale)+end;});
  assert.equal(count,40,'Must preserve and extend every current public course card '+path);
  if(name!=='index.html'){
    assert.equal(target.split(oldMarker).length,2);assert.equal(target.split(oldEnd).length,2);
    const runtimeRoutes=routeText.replace(/^\/\/[^\n]*\n/,'').replace('export const','const');
    target=target.replace(oldMarker,oldMarker+viewAddition).replace(oldEnd,newEnd);
    assert.equal(target.split('function renderCourseCard(').length,2);
    target=target.replace('function renderCourseCard(',runtimeRoutes+'\nfunction renderCourseCard(');
    const roundtrip=target.replace(runtimeRoutes+'\n','').replace(viewAddition,'').replace(newEnd,oldEnd).replace(/<p class="cross-programme-route">[\s\S]*?<\/p>/g,'');
    assert.equal(roundtrip,original,'Offline runtime/source/resource regression '+path);
  }else assert.equal(target.replace(/<p class="cross-programme-route">[\s\S]*?<\/p>/g,''),original,'Online source/resource regression '+path);
  assert.equal(target.split('</main>').length,2);
  target=target.replace('</main>','<p class="cross-programme-production">'+productionLabel(locale)+'</p></main>');
  outputs.set(path,Buffer.from(target));changed.push({path,cards:count,all_inherited_bytes_recoverable:true});
}
// Future deterministic rebuilds receive the same two additive dependency inputs.
const generatorPath='scripts/build-multilingual-interface.mjs';const originalGenerator=sources.get(generatorPath).toString('utf8');
const generatorMarker="  await read('docs/interface/central-hosted-readers.js'),";
assert.equal(originalGenerator.split(generatorMarker).length,2);
const inputMarker="'docs/interface/view.js', 'docs/interface/app.js'";assert.equal(originalGenerator.split(inputMarker).length,2);
const oldMainEnd="+ '</section></main><footer><nav>";
assert.equal(originalGenerator.split(oldMainEnd).length,2);
const newMainEnd="+ '</section><p class=\"cross-programme-production\">' + (locale === 'id' ? '"+productionLabel('id')+"' : '"+productionLabel('en')+"') + '</p></main><footer><nav>";
outputs.set(generatorPath,Buffer.from(originalGenerator.replace(generatorMarker,generatorMarker+"\n  await read('docs/interface/cross-programme-routes.js'),").replace(inputMarker,"'docs/interface/view.js', 'docs/interface/cross-programme-routes.js', 'docs/data/cross-programme-v1/bridge.json', 'docs/interface/app.js'").replace(oldMainEnd,newMainEnd)));
for(const path of ['docs/interface/cross-programme-routes.js','docs/data/cross-programme-v1/bridge.json','docs/en/programme/index.html','docs/id/programme/index.html'])outputs.set(path,await readFile(resolve(root,path)));
const rows=[];for(const [path,b] of outputs){const full=resolve(stage,path);if(args.has('--check'))assert.deepEqual(await readFile(full),b,'Staging bytes changed '+path);else{await mkdir(dirname(full),{recursive:true});await writeFile(full,b);}rows.push(fact(path,b));}
const changedPaths=[...changed.map(x=>x.path),'docs/interface/view.js',generatorPath,'docs/interface/cross-programme-routes.js','docs/data/cross-programme-v1/bridge.json','docs/en/programme/index.html','docs/id/programme/index.html'];
const receipt={schema:'cross-programme-public-baseline-reconciliation/1',state:'local_additive_current_public_baseline',base_commit:commit,base_tree:manifest.source_tree,baseline:fact('current-public-baseline/MANIFEST.json',await readFile(resolve(baseline,'MANIFEST.json'))),counts:bridge.counts,changed_pages:changed,explicit_changed_paths:changedPaths,preserved_runtime_files:rows.filter(r=>!changedPaths.includes(r.path)),outputs:rows,source_and_resource_byte_roundtrip:'pass',public_deployment:false,no_older_local_catalogue_overwrite:true};
if(!args.has('--check'))await writeFile(resolve(packageRoot,'PUBLIC_BASELINE_RECONCILIATION.json'),serialize(receipt));
console.log(JSON.stringify({state:args.has('--check')?'baseline_exact_replay_pass':receipt.state,files:rows.length,changed:changedPaths.length,preserved:receipt.preserved_runtime_files.length}));
