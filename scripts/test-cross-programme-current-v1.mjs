// Verify the actual merged learner pages, not a previous staging directory.
import assert from 'node:assert/strict';
import {readFile, writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {resolve, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {crossProgrammeRoutes} from '../docs/interface/cross-programme-routes.js';
import {validateD80PrerequisiteRoute,renderD80PrerequisiteRoute} from './d80-prerequisite-route-v1.mjs';
import {validateB40PrerequisiteRoute,renderB40PrerequisiteRoute,currentRequirementDisposition,renderCurrentRequirements} from './b40-prerequisite-route-v1.mjs';
import {validateHermitianRoute,renderHermitianRoute} from './finite-hermitian-route-v1.mjs';
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
assert.equal(bridge.source_snapshots.advanced.commit,'801f186833b9811fa826575ef0717e78a5047ab0');
assert.equal(bridge.counts.published_advanced_courses,72);
assert.equal(bridge.counts.published_advanced_lessons,1061);
assert.equal(bridge.counts.cross_programme_course_edges,184);
assert.equal(bridge.advanced_snapshot_intake.consumer_source.matching_inspected_proof_snapshot,true);
assert.ok(bridge.courses.advanced.some(c=>c.id==='AG-RG'&&c.lessons.length===6));
assert.ok(!bridge.courses.advanced.some(c=>c.id==='CORE-B40'),'Local proof draft must not acquire an invented public route');
assert.equal(bridge.counts.independently_verified_cross_programme_proof_matches,0);
assert.equal(bridge.result_requirement_findings_context?.role,'historical_snapshot','Historical findings must be distinguished from current prerequisite evidence');
assert.equal(bridge.current_result_requirements?.length,2);
assert.equal(bridge.counts.requirements_supplied_with_author_self_review,2);
assert.equal(bridge.counts.actual_uses_bound_to_supplied_requirements,4);
for(const requirement of bridge.current_result_requirements){
  assert.equal(requirement.status,'proof_supplied_author_self_review');
  assert.equal(requirement.independent_review,false);
  assert.equal(requirement.whole_prerequisite_closure,false);
  assert.equal(requirement.native_catalogue_admission_changed,false);
  assert.equal(requirement.consumer.source.sha256,'659942bdf47420e6665d59c4e80cf973867730d3b231d7e9c80ab8177bd83712');
  assert.equal(requirement.consumer.uses.length,2);
  assert.equal(requirement.provider.content_language,'en');
}
const b40Course=bridge.courses.core.find(c=>c.id==='B40');
assert.equal(b40Course.language_access.en.program_hosted_reader.status,'not-yet-hosted','Preserve the frozen language-access snapshot');
assert.equal(bridge.policy.current_reading_resources_are_additive_to_frozen_language_access,true);
assert.equal(b40Course.current_reading_resources.length,2);
const expanded=b40Course.current_reading_resources.find(r=>r.marker==='data-b40-expanded="v1"');
assert.equal(expanded.href,'https://kokunoyumeto.github.io/program-matematika-indonesia/en/readers/hefferon-linear-algebra/');
assert.equal(expanded.content_language,'en');
assert.equal(expanded.source_commit,'510658a897f399bdaf8916fd3ae309648aa0c4a9');
assert.deepEqual(expanded.coverage,{sections:33,native_units:2577,full_book:false,proof_dependency_closure:false});
for(const resource of b40Course.current_reading_resources){
  const manifestBytes=await readFile(resolve(root,resource.source_manifest.path));
  assert.equal(manifestBytes.length,resource.source_manifest.bytes);
  assert.equal(sha(manifestBytes),resource.source_manifest.sha256);
  const manifest=JSON.parse(manifestBytes);
  assert.equal(resource.native_sections.length,manifest.sections.length);
  for(let i=0;i<manifest.sections.length;i++){
    const bound=resource.native_sections[i],native=manifest.sections[i];
    assert.equal(bound.section,native.section);assert.equal(bound.native_units,native.units);
    for(const [key,nativeKey] of [['reader','reader'],['native_unit_index','public_index']]){
      const row=bound[key],content=await readFile(resolve(root,row.path));
      assert.equal(content.length,row.bytes);assert.equal(sha(content),row.sha256);
      assert.equal(row.sha256,native[nativeKey].sha256);
      assert.equal(row.url,'https://kokunoyumeto.github.io/program-matematika-indonesia/'+row.path.slice(5));
    }
  }
}
const d80route=validateD80PrerequisiteRoute(await load('backend/cross-programme-v1/d80-prerequisite-route-v1.json'));
const b40route=validateB40PrerequisiteRoute(await load('backend/cross-programme-v1/b40-prerequisite-route-v1.json'));
const hermitianRoute=validateHermitianRoute(await load('backend/cross-programme-v1/finite-hermitian-route-v1.json'),await load('docs/en/readers/finite-hermitian-spaces/READER_MANIFEST.json'));
assert.deepEqual(bridge.source_bound_lesson_routes,[d80route,b40route,hermitianRoute]);
const historicalBytes=await readFile(resolve(root,'backend/cross-programme-v1/PROOF_SCOPE_FINDINGS.json'));
assert.deepEqual(bridge.result_requirement_findings,JSON.parse(historicalBytes),'Original findings remain unchanged');
assert.deepEqual(bridge.result_requirement_findings_context.source,{path:'backend/cross-programme-v1/PROOF_SCOPE_FINDINGS.json',bytes:historicalBytes.length,sha256:sha(historicalBytes)});
let rejectedDispositionFixtures=0;
for(let i=0;i<2;i++){
  const current=bridge.current_result_requirements[i],route=[b40route,hermitianRoute][i];
  const finding=bridge.result_requirement_findings.requirements.find(row=>row.id===current.id);
  const evidence={consumer:current.consumer.source,source:current.provider.source,
    route:current.provider.route,reader_manifest:current.provider.reader_manifest,author_review:current.author_review};
  for(const fact of Object.values(evidence)){
    const bytes=await readFile(resolve(root,fact.path));assert.equal(bytes.length,fact.bytes);assert.equal(sha(bytes),fact.sha256);
  }
  assert.deepEqual(current,currentRequirementDisposition(finding,route,evidence));
  const mutations=[
    (f,r,e)=>{e.consumer.sha256='0'.repeat(64);},
    (f,r,e)=>{e.source.sha256='0'.repeat(64);},
    (f,r,e)=>{e.reader_manifest.path='docs/wrong.json';},
    (f,r,e)=>{e.author_review.bytes=0;},
    (f,r,e)=>{f.id='another-requirement';},
    (f,r,e)=>{r.uses.pop();},
    (f,r,e)=>{r.independent_mathematical_admission=true;},
    (f,r,e)=>{r.whole_prerequisite_closure=true;},
  ];
  for(const mutate of mutations){
    const fixture=[finding,route,evidence].map(row=>structuredClone(row));
    mutate(...fixture);assert.throws(()=>currentRequirementDisposition(...fixture));rejectedDispositionFixtures++;
  }
  const reader=await readFile(resolve(root,dirname(current.provider.reader_manifest.path),'index.html'),'utf8');
  for(const anchor of current.provider.proof_anchors)assert.ok(reader.includes('id="'+anchor+'"'));
}
const invalidHermitian=[r=>r.whole_prerequisite_closure=true,r=>r.independent_mathematical_admission=true,r=>r.source_sha256='bad',r=>r.content_language='id',r=>r.uses.pop(),r=>r.limits.id=''];
for(const mutate of invalidHermitian){const invalid=structuredClone(hermitianRoute);mutate(invalid);assert.throws(()=>validateHermitianRoute(invalid));}
const invalidB40=[r=>r.hermitian_dependency_closed=true,r=>r.independent_mathematical_admission=true,r=>r.source_sha256='bad',r=>r.reader_url='https://example.org/',r=>r.uses.pop(),r=>r.scope.id=''];
for(const mutate of invalidB40){const invalid=structuredClone(b40route);mutate(invalid);assert.throws(()=>validateB40PrerequisiteRoute(invalid));}
assert.deepEqual(bridge,await load('backend/cross-programme-v1/bridge.json'));
const facts=[];
for (const locale of ['id','en']) {
  const programme='docs/'+locale+'/programme/index.html';
  const programmeBytes=await readFile(resolve(root,programme));
  const text=programmeBytes.toString('utf8');
  assert.ok(!/^(?:<{7}|={7}|>{7})/m.test(text),'No unresolved programme merge markers');
  assert.ok(text.includes('data-advanced-snapshot="801f1868"'));
  const currentStatus=renderCurrentRequirements(bridge.current_result_requirements,locale);
  assert.ok(text.split('<section id="advanced-RT-FIN">')[1]?.split('</section>')[0].includes(currentStatus));
  assert.equal((text.match(/data-current-proof-requirements=/g)||[]).length,1);
  const b40=text.match(/<section id="core-B40">[\s\S]*?<\/section>/)?.[0];
  assert.ok(b40?.includes('data-b40-foundations="v1"'));
  assert.ok(b40.includes('href="https://kokunoyumeto.github.io/program-matematika-indonesia/en/readers/hefferon-foundations/" hreflang="en"'));
  assert.ok(b40.includes('data-b40-expanded="v1"'));
  assert.ok(b40.includes('href="https://kokunoyumeto.github.io/program-matematika-indonesia/en/readers/hefferon-linear-algebra/" hreflang="en"'));
  assert.ok(b40.includes(locale==='en'?'(partial book)':'(sebagian buku)'));
  assert.ok(b40.includes(locale==='en'?'33 sections through Computer Graphics':'33 bagian hingga Grafika Komputer'));
  assert.ok(!/\b(?:30|31|32) (?:sections|bagian)\b/.test(b40));
  for(const resource of b40Course.current_reading_resources){
    assert.ok(b40.includes(resource.marker+' href="'+resource.href+'" hreflang="'+resource.content_language+'"'));
    assert.ok(b40.includes(resource.labels[locale]));
  }
  for(const [section,side] of [['core-D80','provider'],['advanced-'+d80route.consumer_course,'consumer']]){
    const local=text.split('<section id="'+section+'">')[1]?.split('</section>')[0];
    assert.ok(local?.includes(renderD80PrerequisiteRoute(d80route,locale,side)),'Missing exact D80 '+side+' route in '+locale);
  }
  assert.equal((text.match(/data-d80-prerequisite=/g)||[]).length,2);
  for(const [section,side] of [['core-B40','provider'],['advanced-RT-FIN','consumer']]){
    const local=text.split('<section id="'+section+'">')[1]?.split('</section>')[0];
    assert.ok(local?.includes(renderB40PrerequisiteRoute(b40route,locale,side)),'Missing exact B40 '+side+' route in '+locale);
  }
  assert.equal((text.match(/data-b40-prerequisite=/g)||[]).length,2);
  for(const [section,side] of [['core-B40','provider'],['advanced-RT-FIN','consumer']]){
    const local=text.split('<section id="'+section+'">')[1]?.split('</section>')[0];
    assert.ok(local?.includes(renderHermitianRoute(hermitianRoute,locale,side)),'Missing exact Hermitian '+side+' route in '+locale);
  }
  assert.equal((text.match(/data-hermitian-prerequisite=/g)||[]).length,2);
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
  advanced_courses:72,advanced_lessons:1061,course_reading_edges:184,
  all_six_current_shells_have_both_route_and_d60_tools:true,
  all_six_current_shells_have_d80_tools:true,
  b40_existing_english_foundations_preserved_in_both_programmes:true,
  b40_expanded_english_reader_preserved_in_both_programmes:true,
  b40_machine_discovery:{current_readers:2,expanded_sections:33,expanded_native_units:2577,section_indices_hash_bound:true,frozen_snapshot_preserved:true},
  d80_source_bound_prerequisite_readings:3,
  d80_distinct_relationships:1,
  d80_forward_reverse_localized_renderings:4,
  b40_exact_projection_uses:2,
  b40_forward_reverse_localized_renderings:4,
  b40_invalid_route_fixtures_rejected:invalidB40.length,
  b40_basis_bridge_alone_closes_hermitian_dependency:false,
  hermitian_exact_uses_supplied_with_author_self_review:2,
  hermitian_forward_reverse_localized_renderings:4,
  hermitian_invalid_route_fixtures_rejected:invalidHermitian.length,
  current_requirement_dispositions:{supplied_with_author_self_review:2,recorded_uses:4,
    historical_findings_preserved:true,source_facts_rehashed:true,negative_fixtures_rejected:rejectedDispositionFixtures},
  native_proof_closure_claimed:false,files:facts,
  provenance:{model:'gpt-6-astra',effort:'ultra',scope:'Combined current-checkout integration verification; upstream route authorship retained'}};
await writeFile(resolve(root,'backend/cross-programme-v1/CURRENT_INTEGRATION_VALIDATION.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({state:'pass',core_roles:40,advanced_courses:72,advanced_lessons:1061,current_shells:6}));
