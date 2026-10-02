// Verify the actual merged learner pages, not a previous staging directory.
import assert from 'node:assert/strict';
import {readFile, writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {resolve, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {crossProgrammeRoutes} from '../docs/interface/cross-programme-routes.js';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const sha=b=>createHash('sha256').update(b).digest('hex');
const load=async p=>JSON.parse(await readFile(resolve(root,p)));
const bridge=await load('docs/data/cross-programme-v1/bridge.json');
const coverage=await load('docs/backend/program-backend-coverage.json');
const capsules=await load('backend/course-capsule-v1/generated/course-capsules.json');
const expected=bridge.courses.core.map(c=>c.id).sort();
assert.equal(expected.length,40);
assert.deepEqual(Object.keys(crossProgrammeRoutes).sort(),expected);
assert.deepEqual(coverage.roles.map(c=>c.role_id).sort(),expected);
assert.deepEqual(capsules.map(c=>c.course_id).sort(),expected);
assert.equal(bridge.counts.published_advanced_courses,71);
assert.equal(bridge.counts.published_advanced_lessons,951);
assert.equal(bridge.counts.cross_programme_course_edges,183);
assert.equal(bridge.counts.independently_verified_cross_programme_proof_matches,0);
const facts=[];
for (const locale of ['id','en']) {
  const programme='docs/'+locale+'/programme/index.html';
  const programmeBytes=await readFile(resolve(root,programme));
  const text=programmeBytes.toString('utf8');
  const b40=text.match(/<section id="core-B40">[\s\S]*?<\/section>/)?.[0];
  assert.ok(b40?.includes('data-b40-foundations="v1"'));
  assert.ok(b40.includes('href="https://kokunoyumeto.github.io/program-matematika-indonesia/en/readers/hefferon-foundations/" hreflang="en"'));
  assert.ok(b40.includes('data-b40-expanded="v1"'));
  assert.ok(b40.includes('href="https://kokunoyumeto.github.io/program-matematika-indonesia/en/readers/hefferon-linear-algebra/" hreflang="en"'));
  assert.ok(b40.includes(locale==='en'?'(partial book)':'(sebagian buku)'));
  const anchors=new Set([...text.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]));
  for (const id of expected) {
    const route=new URL(crossProgrammeRoutes[id][locale]);
    assert.equal(route.pathname,'/program-matematika-indonesia/'+locale+'/programme/');
    assert.equal(route.hash,'#core-'+id);
    assert.ok(anchors.has('core-'+id));
  }
  for(const c of bridge.courses.advanced)assert.ok(anchors.has('advanced-'+c.id));
  facts.push({path:programme,bytes:programmeBytes.length,sha256:sha(programmeBytes)});
  for(const name of ['index.html','learning-map.html','learning-map-paired.html']) {
    const path='docs/'+locale+'/'+name,b=await readFile(resolve(root,path)),html=b.toString('utf8');
    const rendered=html.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi,'');
    const links=[...rendered.matchAll(/data-cross-programme-course="([^"]+)" href="([^"]+)"/g)];
    assert.deepEqual(links.map(m=>m[1]).sort(),expected);
    for(const [,id,href] of links)assert.equal(href,crossProgrammeRoutes[id][locale]);
    assert.ok(html.includes('backend/d60/native-ledger/'+(locale==='en'?'ledger-en.html':'ledger.html')),
      'Current D60 consumer must survive the upstream-route merge');
    assert.ok(html.includes('backend/d80/native-ledger/'+(locale==='en'?'ledger-en.html':'ledger.html')),
      'Current D80 consumer must survive the upstream-route merge');
    assert.ok(!/^(?:<{7}|={7}|>{7})/m.test(html),'No unresolved Git merge markers');
    facts.push({path,bytes:b.length,sha256:sha(b)});
  }
}
const d60=capsules.find(c=>c.course_id==='D60');
assert.ok(d60.layers.learner.tools.some(t=>t.tool_id==='d60.native_ledger'));
for(const key of ['ledger_status','terminology_status','corrections_status'])
  assert.equal(d60.layers.translation[key],'available_unverified');
const result={schema:'current-core-advanced-integration/1',state:'pass',core_roles:40,
  advanced_courses:71,advanced_lessons:951,course_reading_edges:183,
  all_six_current_shells_have_both_route_and_d60_tools:true,
  all_six_current_shells_have_d80_tools:true,
  b40_existing_english_foundations_preserved_in_both_programmes:true,
  b40_expanded_english_reader_preserved_in_both_programmes:true,
  native_proof_closure_claimed:false,files:facts,
  provenance:{model:'gpt-6-astra',effort:'ultra',scope:'Combined current-checkout integration verification; upstream route authorship retained'}};
await writeFile(resolve(root,'backend/cross-programme-v1/CURRENT_INTEGRATION_VALIDATION.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({state:'pass',core_roles:40,advanced_courses:71,advanced_lessons:951,current_shells:6}));
