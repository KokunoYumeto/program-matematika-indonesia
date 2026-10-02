import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {projectD20EnglishLedgerTools} from './interface-capability-tools.mjs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const load=async path=>JSON.parse(await readFile(resolve(root,path),'utf8'));
const base='backend/course-capsule-v1/adapters/d20-native-ledger-v1/';
const inputs=Object.fromEntries(await Promise.all([
 base+'tests.json','docs/backend/d20/native-ledger/source-lock.json','docs/backend/d20/native-ledger/projection.json',
].map(async path=>[path,await readFile(resolve(root,path))])));
const checks=[];
const english=projectD20EnglishLedgerTools(inputs,['D20']);
assert.equal(english.length,1);assert.equal(english[0].contentLanguage,'en');assert.equal(english[0].labelLanguage,'en');
assert.equal(english[0].href,'backend/d20/native-ledger/ledger-en.html');
assert.ok(english[0].limitations.some(x=>x.includes('Indonesian')));checks.push('explicit_english_binding_without_relabelling_book');
const negatives=[];
function refuses(name,change){const changed={...inputs};change(changed);assert.throws(()=>projectD20EnglishLedgerTools(changed,['D20']));negatives.push(name);}
for(const [name,mutate] of [
 ['invented_semantic_approval',v=>{v.semantic_canon_review=true;}],
 ['invented_native_rebuild',v=>{v.native_book_rebuilt=true;}],
 ['wrong_segment_scope',v=>{v.summary.segments=2195;}],
 ['stale_projection',v=>{v.outputs['projection.json'].sha256='0'.repeat(64);}],
])refuses(name,changed=>{const v=JSON.parse(changed[base+'tests.json']);mutate(v);changed[base+'tests.json']=Buffer.from(JSON.stringify(v));});
refuses('changed_source_lock',changed=>{const key='docs/backend/d20/native-ledger/source-lock.json';changed[key]=Buffer.concat([changed[key],Buffer.from('\n')]);});
const access=await load('docs/interface/learner-access-manifest.json');
for(const locale of ['id','en']){
 const entry=access.courses.D20[locale];
 const rows=[...entry.program_hosted_reader.resources,...entry.authoritative_original.resources,...entry.offline_copies,...entry.alternatives];
 const suffix=locale==='en'?'ledger-en.html':'ledger.html';
 assert.ok(rows.some(r=>r.url.endsWith('/backend/d20/native-ledger/'+suffix)&&r.content_language===locale&&r.access_role==='tool'));
 checks.push('catalogue_'+locale+'_tool_binding');
}
assert.ok(access.courses.D20.en.authoritative_original.resources.some(r=>r.content_language==='en'&&r.url.includes('functional_analysis_operator_algebras_pdf.pdf')));
checks.push('original_english_book_remains_distinct');
const nav=await load('backend/authority/central-reader-navigation-v1.json');
const surface=nav.course_surfaces.find(r=>r.root==='docs/backend/d20/native-ledger');
assert.deepEqual(surface.documents.map(r=>r.locale).sort(),['en','id']);
for(const document of surface.documents){assert.deepEqual(document.course_ids,['D20']);assert.equal(document.related_course_surface_paths.length,2);}
checks.push('reciprocal_course_surface_navigation');
const over=await load('backend/course-capsule-v1/authority/integration-overrides-v1.json');
assert.equal(over.learner_tools.D20.filter(r=>r.tool_id==='d20.native_ledger').length,1);
assert.equal(over.educator_evidence.D20.resources.filter(r=>r.id.startsWith('D20:native-ledger-')).length,2);
for(const capability of ['translation_ledger','terminology','corrections'])assert.equal(over.native_capabilities.D20[capability].status,'available_unverified');
checks.push('no_duplicate_roles_or_false_semantic_admission');
const coverage=await load('backend/course-capsule-v1/generated/program-backend-coverage-v1.json');
assert.equal(coverage.roles.length,40);
assert.equal(coverage.roles.find(r=>r.role_id==='D20').native_capability_parity_completion,'not_yet_proven');
checks.push('full_programme_scope_and_honest_completion');
const receipt={schema:'d20-central-binding-tests/1',state:'pass',checks,negative_fixtures:negatives,whole_program_complete:false};
await writeFile(resolve(root,base+'central-binding-tests.json'),JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify(receipt));
