import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const hash=b=>createHash('sha256').update(b).digest('hex');
const parent='6c949b47e0ca75e36ebd8fe86eb699fa941e0a2e';
const git=p=>execFileSync('git',['-C',root,'show',parent+':'+p],{maxBuffer:8*1024*1024});
const local=p=>readFile(resolve(root,p));
const checks=[];
for(const p of ['backend/cross-programme-v1/bridge.json','docs/data/cross-programme-v1/bridge.json']){
  const raw=await local(p),before=git(p),x=JSON.parse(raw),y=JSON.parse(before);
  delete x.human_analysis_readings;for(const c of x.courses.core)delete c.current_human_reading_resources;
  assert.equal(JSON.stringify(x),JSON.stringify(y),'Unexpected bridge change: '+p);
  checks.push({path:p,base_sha256:hash(before),current_sha256:hash(raw),only_new_human_routes:true});
}
for(const locale of ['en','id']){
  const p='docs/'+locale+'/programme/index.html',raw=await local(p),before=git(p);
  const text=raw.toString('utf8'),panels=text.match(/<aside data-human-analysis="[^"]+">[\s\S]*?<\/aside>/g)||[];
  assert.equal(panels.length,5);
  assert.equal(hash(text.replace(/<aside data-human-analysis="[^"]+">[\s\S]*?<\/aside>/g,'')),hash(before),'Unexpected reader-body change: '+p);
  checks.push({path:p,base_sha256:hash(before),current_sha256:hash(raw),only_five_new_reading_panels:true});
}
const p='backend/authority/central-course-surface-navigation-overlay-v1.json';
const x=JSON.parse(await local(p)),y=JSON.parse(git(p));
for(const row of x.files)if(/^docs\/(en|id)\/programme\/index.html$/.test(row.document)){
  const old=y.files.find(r=>r.document===row.document);row.source_body=old.source_body;row.hosted_surface=old.hosted_surface;
}
assert.equal(JSON.stringify(x),JSON.stringify(y),'Unrelated overlay records changed');
const receipt={schema:'additive-human-analysis-integration/1',state:'pass',parent,checks,
  unrelated_overlay_records_preserved:true,previous_course_content_preserved:true,
  existing_public_access_unchanged:true,publication:false};
await writeFile(resolve(root,'backend/cross-programme-v1/HUMAN_ANALYSIS_ADDITIVE_CHECK.json'),JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify({state:'pass',prior_course_content_preserved:true,unrelated_overlay_records_preserved:true}));
