import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadPortableCourseRoutes,renderPortableCourseRoute} from './portable-course-routes-v1.mjs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const bridge=JSON.parse(await readFile(resolve(root,'backend/cross-programme-v1/bridge.json')));
const ids=new Set(bridge.courses.advanced.map(c=>c.id));
const bound=await loadPortableCourseRoutes(root,ids);
assert.equal(bound.editions.length,2);
const haar=bound.editions.find(r=>r.slug==='haar-measure-and-quotient-integration');
assert.equal(haar.lesson_count,4);assert.equal(haar.prerequisite_chapters,7);
assert.equal(haar.supplements,1);assert.equal(haar.pdf_pages,140);assert.equal(haar.native_locations,215);
for(const route of bound.editions)for(const locale of ['id','en']){
  const html=renderPortableCourseRoute(route,locale);
  assert.ok(html.includes('index.'+locale+'.html'));
  assert.deepEqual([...html.matchAll(/data-portable-format="([^"]+)"/g)].map(m=>m[1]),['pdf','tex','zip','epub']);
  assert.equal(route.proof_dependency_closure,'not_established_by_format_validation');
  assert.equal(route.new_translation,false);
}
const cataloguePath=bound.catalogue.path;
const original=JSON.parse(await readFile(resolve(root,cataloguePath)));
let rejected=0;
for(const mutate of [
  c=>c.editions[0].course_id='not-a-curriculum-course',
  c=>c.editions.push(c.editions[0]),
  c=>c.editions[0].slug='../escape',
  c=>c.editions[0].edition.sha256='0'.repeat(64),
  c=>c.editions[0].content_language='id',
  c=>delete c.editions[0].notes.id,
]){
  const modified=structuredClone(original);mutate(modified);
  await assert.rejects(loadPortableCourseRoutes(root,ids,path=>path===cataloguePath?Promise.resolve(Buffer.from(JSON.stringify(modified))):readFile(resolve(root,path))));rejected++;
}
await assert.rejects(loadPortableCourseRoutes(root,ids,path=>path.endsWith('.pdf')?Promise.resolve(Buffer.from('changed')):readFile(resolve(root,path))));rejected++;
console.log(JSON.stringify({state:'pass',editions:bound.editions.length,localized_routes:4,negative_fixtures:rejected}));
