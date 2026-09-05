import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { gzipSync } from 'node:zlib';
import vm from 'node:vm';
import { courses as canonicalCourses } from '../docs/courses.js';
import { interfaceCourses, interfaceTopics, coursePresentation, resourceBindings, renderCourseCard, renderResourceLinks, safeResourceUrl, isOriginalSource, contentLanguageName, learnerAccessProjection, learnerAccessRoles } from '../docs/interface/view.js';
import { additionalOriginalSources } from '../docs/interface/original-sources.js';
import { supportedLocales, interfaceCopy, englishResources, englishBindingExceptions, siteOrigin } from '../docs/interface/locales.js';
import { verifiedReaderActions, readerActionSource } from '../docs/interface/reader-actions.js';
import { projectReaderActions, readerActionInput } from './interface-reader-actions.mjs';
import { finalEditions, finalEditionSource } from '../docs/interface/final-editions.js';
import { validateFinalEditions, finalEditionInput } from './interface-final-editions.mjs';
import {capabilityTools, capabilityToolSource} from '../docs/interface/capability-tools.js';
import {supplementalReaders} from '../docs/interface/supplemental-readers.js';
import {projectCapabilityTools, capabilityInput} from './interface-capability-tools.mjs';
import { LEARNER_STATE_STORAGE_KEY, createEmptyLearnerState, evaluateLearnerState, setCourseCompletion, setCourseClaim, setPrerequisiteWaiver, normalizeLearnerState } from '../docs/learner-state.js';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const ids = canonicalCourses.map((c) => c.id);
for (const course of interfaceCourses) for (const locale of supportedLocales) {
  const bindings = resourceBindings(course, locale);
  assert.ok(bindings.length);
  assert.ok(bindings.every(row => learnerAccessRoles.includes(row.accessRole)), course.id + ': every resource has a typed learner access role');
  assert.equal(new Set(bindings.map(row => row.href + '\u0000' + row.accessRole)).size, bindings.length, course.id + ': resource URL/role pairs are unique');
  for (const href of new Set(bindings.map(row => row.href))) {
    const sameUrl = bindings.filter(row => row.href === href);
    if (sameUrl.length < 2) continue;
    assert.deepEqual(new Set(sameUrl.map(row => row.accessRole)), new Set(['hosted-reader','authoritative-original']), course.id + ': only a program original may have a dual-role URL');
    assert.ok(sameUrl.some(row => row.origin === 'program-original'), course.id + ': dual-role URL must be a program original');
  }
  const sources = bindings.filter(isOriginalSource);
  assert.ok(sources.length, course.id + ': original source must be available in every interface language');
  const visible = renderResourceLinks(course, locale).split('<details class="resource-details">')[0];
  assert.ok(visible.includes('data-access-group="hosted-reader"'));
  assert.ok(visible.includes('data-access-group="authoritative-original"'));
  for (const source of sources) {
    assert.ok(visible.includes('href="'+source.href.replaceAll('&','&amp;')+'"'), 'Source must not be collapsed: '+course.id);
    assert.ok(visible.includes('data-original-source="'+source.origin+'"'));
    assert.equal(source.accessRole,'authoritative-original');
  }
  for (const source of additionalOriginalSources[course.id] ?? []) {
    assert.equal(sources.filter(r=>r.href===safeResourceUrl(source.href) && r.contentLanguage===source.contentLanguage).length,1);
  }
  for (const source of (englishResources[course.id] ?? []).filter(isOriginalSource)) {
    assert.ok(sources.some(r=>r.href===source.href && r.contentLanguage==='en'));
  }
  const projection=learnerAccessProjection(course,locale);
  assert.equal(projection.course_id,course.id); assert.equal(projection.interface_locale,locale);
  assert.equal(projection.authoritative_original.status,'available');
  assert.equal(projection.authoritative_original.resources.length,sources.length);
  const hosted=bindings.filter(row=>row.contentLanguage===locale&&row.accessRole==='hosted-reader');
  assert.equal(projection.program_hosted_reader.status,hosted.length?'available':'not-yet-hosted');
  assert.equal(projection.program_hosted_reader.resources.length,hosted.length);
  if(!hosted.length) assert.ok(visible.includes(interfaceCopy[locale].noHostedReader));
}
assert.notEqual(contentLanguageName('zh','en'),'shared metadata');
assert.notEqual(contentLanguageName('de','id'),'metadata bersama');
assert.ok(contentLanguageName('bn','en'));
assert.throws(()=>coursePresentation(interfaceCourses[0],'pt-BR'),/Unsupported interface locale/);
assert.throws(()=>resourceBindings(interfaceCourses[0],'pt-BR'),/Unsupported interface locale/);
assert.equal(isOriginalSource({origin:'published-translation'}),false);
assert.equal(isOriginalSource({origin:'published-english-component'}),false);
assert.equal(isOriginalSource({origin:'program-mirror'}),false);
assert.equal(isOriginalSource({accessRole:'authoritative-original'}),true);
const a00English=resourceBindings(interfaceCourses.find(c=>c.id==='A00'),'en');
assert.equal(a00English.filter(r=>r.primary).length,1);
assert.equal(a00English.find(r=>r.primary).origin,'program-mirror');
assert.equal(a00English.find(r=>r.primary).accessRole,'hosted-reader');
assert.equal(a00English.find(r=>r.origin==='upstream-original').href,'https://openstax.org/details/books/prealgebra-2e');
assert.ok(renderResourceLinks(interfaceCourses.find(c=>c.id==='A00'),'en').split('<details class="resource-details">')[0].includes('Authoritative original source'));
assert.equal(a00English.find(r=>r.kind==='HTML ZIP').offlineAfterDownload,true);
assert.equal(a00English.find(r=>r.kind==='HTML ZIP').accessRole,'offline-copy');
const a00MirrorEvidence=JSON.parse(await readFile(resolve(root,'docs/interface/evidence/a00-original-english-mirror.json'),'utf8'));
assert.equal(a00MirrorEvidence.status,'published_and_anonymously_verified');
assert.equal(a00MirrorEvidence.work_kind,'presentation_mirror_of_original_source');
assert.equal(a00MirrorEvidence.program_mirror.reader_url,a00English.find(r=>r.primary).href);
assert.equal(a00MirrorEvidence.source.publisher_url,a00English.find(r=>r.origin==='upstream-original').href);
assert.equal(a00MirrorEvidence.program_mirror.offline_zip_sha256,a00English.find(r=>r.kind==='HTML ZIP').sha256);
assert.equal(a00MirrorEvidence.public_verification.pages_files_verified,3041);
assert.equal(a00MirrorEvidence.public_verification.all_exact,true);
const a10English=resourceBindings(interfaceCourses.find(c=>c.id==='A10'),'en');
assert.equal(a10English.filter(r=>r.primary).length,1);
assert.equal(a10English.find(r=>r.primary).origin,'program-mirror');
assert.equal(a10English.find(r=>r.primary).accessRole,'hosted-reader');
assert.equal(a10English.find(r=>r.origin==='upstream-original').href,'https://openstax.org/details/books/elementary-algebra-2e');
assert.ok(renderResourceLinks(interfaceCourses.find(c=>c.id==='A10'),'en').split('<details class="resource-details">')[0].includes('Authoritative original source'));
assert.equal(a10English.find(r=>r.kind==='HTML ZIP').offlineAfterDownload,true);
assert.equal(a10English.find(r=>r.kind==='HTML ZIP').accessRole,'offline-copy');
const a10MirrorEvidence=JSON.parse(await readFile(resolve(root,'docs/interface/evidence/a10-original-english-mirror.json'),'utf8'));
assert.equal(a10MirrorEvidence.status,'published_and_anonymously_verified');
assert.equal(a10MirrorEvidence.work_kind,'presentation_mirror_of_original_source');
assert.equal(a10MirrorEvidence.program_mirror.reader_url,a10English.find(r=>r.primary).href);
assert.equal(a10MirrorEvidence.source.publisher_url,a10English.find(r=>r.origin==='upstream-original').href);
assert.equal(a10MirrorEvidence.program_mirror.offline_zip_sha256,a10English.find(r=>r.kind==='HTML ZIP').sha256);
assert.equal(a10MirrorEvidence.public_verification.pages_files_verified,4108);
assert.equal(a10MirrorEvidence.public_verification.all_exact,true);
const a20English=resourceBindings(interfaceCourses.find(c=>c.id==='A20'),'en');
assert.equal(a20English.filter(r=>r.primary).length,1);
assert.equal(a20English.find(r=>r.primary).origin,'program-mirror');
assert.equal(a20English.find(r=>r.primary).accessRole,'hosted-reader');
assert.equal(a20English.find(r=>r.origin==='upstream-original').href,'https://openstax.org/books/intermediate-algebra-2e/pages/1-introduction');
assert.ok(renderResourceLinks(interfaceCourses.find(c=>c.id==='A20'),'en').split('<details class="resource-details">')[0].includes('Authoritative original source'));
assert.equal(a20English.find(r=>r.kind==='HTML ZIP').offlineAfterDownload,true);
assert.equal(a20English.find(r=>r.kind==='HTML ZIP').accessRole,'offline-copy');
const a20MirrorEvidence=JSON.parse(await readFile(resolve(root,'docs/interface/evidence/a20-original-english-mirror.json'),'utf8'));
assert.equal(a20MirrorEvidence.status,'published_and_anonymously_verified');
assert.equal(a20MirrorEvidence.work_kind,'presentation_mirror_of_original_source');
assert.equal(a20MirrorEvidence.program_mirror.reader_url,a20English.find(r=>r.primary).href);
assert.equal(a20MirrorEvidence.source.publisher_url,a20English.find(r=>r.origin==='upstream-original').href);
assert.equal(a20MirrorEvidence.program_mirror.offline_zip_sha256,a20English.find(r=>r.kind==='HTML ZIP').sha256);
assert.equal(a20MirrorEvidence.public_verification.pages_files_verified,4094);
assert.equal(a20MirrorEvidence.public_verification.all_exact,true);
for (const id of ['B80','D120']) {
  const idBindings=resourceBindings(interfaceCourses.find(c=>c.id===id),'id');
  const dualRoleUrl=idBindings.find(row=>row.origin==='program-original').href;
  assert.ok(idBindings.some(row=>row.href===dualRoleUrl&&row.accessRole==='hosted-reader'),id+': program original remains a hosted reader');
  assert.ok(idBindings.some(row=>row.href===dualRoleUrl&&row.accessRole==='authoritative-original'),id+': program original is also identified as the authoritative original');
}
const unmappedOriginal=renderResourceLinks({id:'ZZZ',learner:null,reader:null,edition:null,zenodo:null,repository:null,supplements:[]},'en');
assert.ok(unmappedOriginal.includes(interfaceCopy.en.noAuthoritativeOriginal));
assert.deepEqual(['B80','D120'].map(id=>additionalOriginalSources[id][0].origin),['program-original','program-original']);
assert.equal(new Set(supplementalReaders.map(row=>row.id)).size,supplementalReaders.length);
for (const row of supplementalReaders) {
  assert.ok(ids.includes(row.courseId) && row.id.startsWith(row.courseId+':'));
  assert.equal(row.contentLanguage,'id');
  assert.ok(row.labels.id && row.labels.en && row.notes.id && row.notes.en);
  assert.ok(['companion','portable_html','html_download'].includes(row.kind));
  assert.ok(['HTML','HTML ZIP'].includes(row.format));
  assert.equal(new URL(row.href).protocol,'https:');
  assert.ok(['zenodo.org','kokunoyumeto.github.io'].includes(new URL(row.href).hostname));
  assert.match(row.sha256,/^[a-f0-9]{64}$/);
  assert.match(row.evidenceFile,/^docs\/interface\/evidence\/[a-z0-9-]+\.json$/);
  const proof=JSON.parse(await readFile(resolve(root,row.evidenceFile),'utf8'));
  const fact=proof.public_readback.find(item=>item.url===row.href);
  assert.ok(fact,'Reader must have actual public-byte evidence');
  assert.equal(fact.bytes,row.bytes); assert.equal(fact.sha256,row.sha256);
  if(row.offlineAfterDownload) {
    assert.equal(row.kind,'portable_html');
    assert.equal(proof.offline_dependency_replay.external_runtime_dependencies,0);
    assert.equal(proof.offline_dependency_replay.missing_local_references,0);
    assert.equal(proof.offline_dependency_replay.unresolved_fragments,0);
    assert.equal(proof.offline_dependency_replay.scripts,0);
    assert.ok(row.notes.en.includes('Extract'));
  } else assert.notEqual(row.kind,'portable_html');
  for (const locale of supportedLocales) {
    const rows=resourceBindings(interfaceCourses.find(c=>c.id===row.courseId),locale);
    const actual=rows.filter(item=>item.href===row.href);
    assert.equal(actual.length,1); assert.equal(actual[0].primary,false);
    assert.equal(actual[0].contentLanguage,'id'); assert.equal(actual[0].note,row.notes[locale]);
  }
}
assert.deepEqual(supplementalReaders.map(row=>row.id),['D20:complete-companion-html','D20:complete-offline-html','B10:complete-html-download']);
const b10Download=supplementalReaders.find(row=>row.courseId==='B10');
assert.equal(b10Download.offlineAfterDownload,false);
assert.equal(b10Download.kind,'html_download');
assert.ok(b10Download.notes.en.includes('MathJax and online features require internet'));
const b10Proof=JSON.parse(await readFile(resolve(root,b10Download.evidenceFile),'utf8'));
assert.equal(b10Proof.fully_offline_claim_supported,false);
assert.equal(b10Proof.mathjax_dependency,'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js');
assert.equal(resourceBindings(interfaceCourses.find(c=>c.id==='B10'),'id').find(row=>row.primary).href,'https://kokunoyumeto.github.io/discrete-mathematics-open-introduction-id/');
assert.equal(resourceBindings(interfaceCourses.find(c=>c.id==='D20'),'id').find(row=>row.primary).href,'https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/D20/');
const capsuleBytes = await readFile(resolve(root,capabilityInput));
const capsules = JSON.parse(capsuleBytes);
assert.deepEqual(projectCapabilityTools(capsules,ids),capabilityTools);
assert.equal(capabilityToolSource.sha256,createHash('sha256').update(capsuleBytes).digest('hex'));
assert.equal(capabilityToolSource.bytes,capsuleBytes.length);
for (const corrupt of [
  c=>{c.find(r=>r.course_id==='B80').locale='en';},
  c=>{c.find(r=>r.course_id==='B80').layers.learner.tools[0].state='planned';},
  c=>{c.find(r=>r.course_id==='B80').layers.learner.tools[0].href='backend/b80/learning-map.json';},
  c=>{c.find(r=>r.course_id==='B80').layers.learner.tools[0].primary=true;},
  c=>{c.find(r=>r.course_id==='B80').layers.learner.tools[0].machine_data_is_learner_destination=true;},
  c=>{c.find(r=>r.course_id==='B80').layers.learner.tools[0].page.path='../../secret';},
  c=>{c.find(r=>r.course_id==='B80').layers.learner.tools.pop();},
  c=>{c.find(r=>r.course_id==='A00').layers.learner.tools[0].label='changed';},
  c=>{c.find(r=>r.course_id==='C20').layers.learner.tools.pop();},
  c=>{c.find(r=>r.course_id==='B70').layers.learner.tools[0].href='backend/lebl/C50.html';},
  c=>{c.find(r=>r.course_id==='C50').locale='en';},
  c=>{c.find(r=>r.course_id==='C100').layers.learner.tools[0].href='backend/geometry/C100.html';},
  c=>{c.find(r=>r.course_id==='C100').layers.learner.tools.pop();},
  c=>{c.find(r=>r.course_id==='C90').layers.learner.tools[0].href='backend/topology/learning-map.json';},
  c=>{c.find(r=>r.course_id==='C90').layers.learner.tools.pop();},
  c=>{c.find(r=>r.course_id==='D40').layers.learner.tools[0].href='backend/d40/learning-map.json';},
  c=>{c.find(r=>r.course_id==='D40').layers.learner.tools.pop();},
  c=>{c.find(r=>r.course_id==='D70').layers.learner.tools[0].href='backend/d70/learning-map.json';},
  c=>{c.find(r=>r.course_id==='D70').layers.learner.tools.pop();},
  c=>{c.find(r=>r.course_id==='D80').layers.learner.tools[0].href='backend/d80/learning-map.json';},
  c=>{c.find(r=>r.course_id==='D80').layers.learner.tools.pop();},
  c=>{c.find(r=>r.course_id==='D10').layers.learner.tools[0].href='backend/d10/learning-map.json';},
  c=>{c.find(r=>r.course_id==='D10').layers.learner.tools.pop();},
  c=>{c.find(r=>r.course_id==='D120').layers.learner.tools[0].href='backend/d120/learning-map.json';},
  c=>{c.find(r=>r.course_id==='D120').layers.learner.tools.pop();},
  c=>{c.find(r=>r.course_id==='C120').layers.learner.tools[0].href='backend/c120/learning-map.json';},
  c=>{c.find(r=>r.course_id==='C120').layers.learner.tools.pop();},
]) { const changed=structuredClone(capsules); corrupt(changed); assert.throws(()=>projectCapabilityTools(changed,ids)); }
assert.equal(Object.values(englishResources).filter(rows=>rows.length).length,40);
assert.equal(englishResources.B80.find(r=>r.pages).pages,161);
assert.equal(englishResources.D50.find(r=>r.pages).pages,658);
assert.ok(!englishBindingExceptions.B80 && !englishBindingExceptions.D50);
assert.equal(englishResources.B80[0].kind,'HTML');
assert.equal(englishResources.D50[0].kind,'PDF');
assert.equal(englishResources.D50.find(r=>r.kind==='HTML ZIP').offlineAfterDownload,undefined);
assert.ok(englishResources.D50.find(r=>r.kind==='HTML ZIP').label.includes('MathJax requires internet'));
assert.deepEqual(englishResources.D70.filter(r=>r.pages).map(r=>r.pages),[457,102,68,7]);
assert.equal(englishResources.D80.find(r=>r.pages).pages,820);
assert.ok(!englishBindingExceptions.D70 && !englishBindingExceptions.D80);
assert.ok(!englishBindingExceptions.D100);
assert.equal(englishResources.D100[0].kind,'HTML');
assert.equal(englishResources.D100[0].origin,'program-mirror');
assert.equal(englishResources.D100[0].href,'https://kokunoyumeto.github.io/program-matematika-indonesia/en/courses/D100/reader/');
assert.deepEqual(englishResources.D100.slice(1,4).map(r=>r.href),[
  'https://kokunoyumeto.github.io/program-matematika-indonesia/en/courses/D100/reader/ak.html',
  'https://kokunoyumeto.github.io/program-matematika-indonesia/en/courses/D100/reader/bgk.html',
  'https://kokunoyumeto.github.io/program-matematika-indonesia/en/courses/D100/reader/companion.html',
]);
assert.deepEqual(englishResources.D100.slice(1,4).map(r=>[r.units,r.exercises]),[[30,693],[30,495],[32,13]]);
assert.ok(englishResources.D100.some(r=>r.label.includes('Original English-edition website') && r.href==='https://kokunoyumeto.github.io/algebraic-geometry-bridge-id/en/'));
assert.deepEqual(englishResources.D100.slice(0,4).map(r=>[r.bytes,r.sha256]),[
  [1120,'d316fafa4e8ca49006ad5051d5b950d0029756d63c5642269826d8f0a890f019'],
  [4915565,'92e0db157501daff37b452d5e77220b66a6c16d99fdd09784364cc752dcd46e5'],
  [4343251,'cfc5289c2cf05e489d5cfbeb4ba4f7358edfdef81a805642a1dc9d488ca1a3aa'],
  [1487123,'f49a5bfb33757c63591dd05e794f855938c5f98f1d4e130f67cc1a63aa16d549'],
]);
assert.ok(englishResources.D100.some(r=>r.kind==='archive' && r.href==='https://doi.org/10.5281/zenodo.22340270'));
assert.deepEqual(englishResources.D100.filter(r=>r.pages).map(r=>r.pages),[504,381,89]);
assert.equal(englishResources.D100.filter(r=>r.pages).reduce((n,r)=>n+r.pages,0),974);
assert.deepEqual(englishResources.D100.filter(r=>r.pages).map(r=>[r.bytes,r.sha256]),[
  [16029193,'547a0e8f5185cd133edac64cac42ecb7590947ff74d45efe0eb66db7c0a62b46'],
  [2953314,'dffad20f1945c6f0183414cd88fa29e34e230dac14b7fae429ad09c96be4c0f1'],
  [808762,'9272957782c4c8cf7c1b2a12c7edbf445db64270e0a62a37688b9301d925b6a2'],
]);
for (const locale of supportedLocales) {
  const tools=resourceBindings(interfaceCourses.find(c=>c.id==='B80'),locale).filter(r=>r.capabilityToolId);
  assert.equal(tools.length,2);
  for(const tool of tools) {
    assert.equal(tool.contentLanguage,'id'); assert.equal(tool.primary,false);
    if(locale==='id') assert.ok(tool.note.includes('14') && tool.note.includes('75') && tool.note.includes('4'));
    else assert.match(tool.note,/Indonesian-language capability.*source-specific scope/);
    assert.ok(!tool.note.includes('72 latihan inti'));
  }
  for(const role of ['B70','C10','C20','C50']){
    const leblTools=resourceBindings(interfaceCourses.find(c=>c.id===role),locale).filter(r=>r.capabilityToolId);
    assert.equal(leblTools.length,3);
    for(const tool of leblTools){assert.equal(tool.contentLanguage,'id');assert.equal(tool.primary,false);assert.ok(tool.href.includes('/backend/lebl/'));}
  }
  const geometryTools=resourceBindings(interfaceCourses.find(c=>c.id==='C100'),locale).filter(r=>r.capabilityToolId);
  assert.equal(geometryTools.length,2);
  assert.deepEqual(geometryTools.map(tool=>tool.href).sort(),[
    'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/geometry/C100.html',
    'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/geometry/pengajar.html',
  ]);
  for(const tool of geometryTools){
    assert.equal(tool.contentLanguage,'id'); assert.equal(tool.primary,false);
    if(locale==='id') assert.ok(tool.note.includes('939')&&tool.note.includes('491'));
    else assert.match(tool.note,/Indonesian-language capability.*source-specific scope/);
  }
  const topologyTools=resourceBindings(interfaceCourses.find(c=>c.id==='C90'),locale).filter(r=>r.capabilityToolId);
  assert.equal(topologyTools.length,1);
  assert.deepEqual(topologyTools.map(tool=>tool.href).sort(),[
    'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/topology/C90.html',
  ]);
  for(const tool of topologyTools){
    assert.equal(tool.contentLanguage,'id'); assert.equal(tool.primary,false);
    if(locale==='id') assert.ok(tool.note.includes('1.227')&&tool.note.includes('4.908'));
    else assert.match(tool.note,/Indonesian-language capability.*source-specific scope/);
  }
  const d40Tools=resourceBindings(interfaceCourses.find(c=>c.id==='D40'),locale).filter(r=>r.capabilityToolId);
  assert.equal(d40Tools.length,1);
  assert.deepEqual(d40Tools.map(tool=>tool.href),[
    'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d40/D40.html',
  ]);
  for(const tool of d40Tools){
    assert.equal(tool.contentLanguage,'id'); assert.equal(tool.primary,false);
    if(locale==='id') assert.ok(tool.note.includes('68')&&tool.note.includes('14')&&tool.note.includes('130'));
    else assert.match(tool.note,/Indonesian-language capability.*source-specific scope/);
  }
  const d70Tools=resourceBindings(interfaceCourses.find(c=>c.id==='D70'),locale).filter(r=>r.capabilityToolId);
  assert.equal(d70Tools.length,1);
  assert.deepEqual(d70Tools.map(tool=>tool.href),[
    'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d70/D70.html',
  ]);
  for(const tool of d70Tools){
    assert.equal(tool.contentLanguage,'id'); assert.equal(tool.primary,false);
    if(locale==='id') assert.ok(tool.note.includes('716')&&tool.note.includes('54')&&tool.note.includes('20'));
    else assert.match(tool.note,/Indonesian-language capability.*source-specific scope/);
  }
  const d80Tools=resourceBindings(interfaceCourses.find(c=>c.id==='D80'),locale).filter(r=>r.capabilityToolId);
  assert.equal(d80Tools.length,1);
  assert.deepEqual(d80Tools.map(tool=>tool.href),[
    'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d80/D80.html',
  ]);
  for(const tool of d80Tools){
    assert.equal(tool.contentLanguage,'id'); assert.equal(tool.primary,false);
    if(locale==='id') assert.ok(tool.note.includes('146')&&tool.note.includes('2')&&tool.note.includes('jembatan mandiri'));
    else assert.match(tool.note,/Indonesian-language capability.*source-specific scope/);
  }
  const d10Tools=resourceBindings(interfaceCourses.find(c=>c.id==='D10'),locale).filter(r=>r.capabilityToolId);
  assert.equal(d10Tools.length,1);
  assert.deepEqual(d10Tools.map(tool=>tool.href),[
    'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d10/D10.html',
  ]);
  for(const tool of d10Tools){
    assert.equal(tool.contentLanguage,'id'); assert.equal(tool.labelLanguage,'id'); assert.equal(tool.primary,false);
    if(locale==='id') assert.ok(tool.note.includes('94')&&tool.note.includes('1.096')&&tool.note.includes('276'));
    else assert.match(tool.note,/Indonesian-language capability.*source-specific scope/);
  }
  const d100Tools=resourceBindings(interfaceCourses.find(c=>c.id==='D100'),locale).filter(r=>r.capabilityToolId);
  assert.equal(d100Tools.length,1);
  assert.deepEqual(d100Tools.map(tool=>tool.href),[
    'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d100/D100.html',
  ]);
  for(const tool of d100Tools){
    assert.equal(tool.contentLanguage,'en'); assert.equal(tool.labelLanguage,'en'); assert.equal(tool.primary,false);
    if(locale==='id') assert.match(tool.note,/Kapabilitas berbahasa Inggris/);
    else {
      assert.ok(tool.note.includes('60 source-course aggregates'));
      assert.ok(tool.note.includes('1,041 source exercises'));
      assert.doesNotMatch(tool.note,/Indonesian-language capability/);
    }
  }
  const d120Tools=resourceBindings(interfaceCourses.find(c=>c.id==='D120'),locale).filter(r=>r.capabilityToolId);
  assert.equal(d120Tools.length,1);
  assert.deepEqual(d120Tools.map(tool=>tool.href),[
    'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d120/D120.html',
  ]);
  for(const tool of d120Tools){
    assert.equal(tool.contentLanguage,'id'); assert.equal(tool.labelLanguage,'id'); assert.equal(tool.primary,false);
    if(locale==='id') assert.ok(tool.note.includes('Sembilan unit')&&tool.note.includes('54')&&tool.note.includes('71'));
    else assert.match(tool.note,/Indonesian-language capability.*source-specific scope/);
  }
  const c120Tools=resourceBindings(interfaceCourses.find(c=>c.id==='C120'),locale).filter(r=>r.capabilityToolId);
  assert.equal(c120Tools.length,1);
  assert.deepEqual(c120Tools.map(tool=>tool.href),[
    'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/c120/C120.html',
  ]);
  for(const tool of c120Tools){
    assert.equal(tool.contentLanguage,'id'); assert.equal(tool.labelLanguage,'id'); assert.equal(tool.primary,false);
    if(locale==='id') assert.ok(tool.note.includes('Dua puluh enam unit')&&tool.note.includes('4.105')&&tool.note.includes('141'));
    else assert.match(tool.note,/Indonesian-language capability.*source-specific scope/);
  }
  for(const courseId of ['A10','A20','B80','D50','D70','D80','D100']) {
    const resources=resourceBindings(interfaceCourses.find(c=>c.id===courseId),locale);
    for(const target of englishResources[courseId]) assert.equal(resources.filter(r=>r.href===target.href && r.contentLanguage==='en').length,1);
    if(locale==='en') assert.equal(resources.filter(r=>r.primary).length,1);
  }
}
const editionBytes = await readFile(resolve(root, finalEditionInput));
const editionInput = JSON.parse(editionBytes);
assert.deepEqual(validateFinalEditions(editionInput, ids), finalEditions);
assert.equal(finalEditionSource.bytes, editionBytes.length);
assert.equal(finalEditionSource.sha256, createHash('sha256').update(editionBytes).digest('hex'));
assert.deepEqual(finalEditions.map(r=>r.courseId), ['A10','A20','A30','B95','C140','D100']);
const finalResources = finalEditions.flatMap(r=>r.resources);
assert.equal(finalResources.length,14);
assert.equal(finalResources.reduce((n,r)=>n+(r.pages??0),0),9886);
for (const corrupt of [
  input=>{input.editions[0].courseId='Z999';},
  input=>{input.editions[0].prerequisites=[];},
  input=>{input.editions[0].resources[0].contentLanguage='en';},
  input=>{input.editions[0].resources[0].evidence.actual_sha256='0'.repeat(64);},
  input=>{input.editions[0].resources[0].href='javascript:alert(1)';},
  input=>{input.editions[0].resources[0].primary=false;},
  input=>{input.editions[0].resources[0].pages=-1;},
]) {const input=structuredClone(editionInput);corrupt(input);assert.throws(()=>validateFinalEditions(input,ids));}
for (const edition of finalEditions) for(const locale of supportedLocales) {
  const course=interfaceCourses.find(r=>r.id===edition.courseId);
  assert.equal(course.state,'published');
  const bindings=resourceBindings(course,locale);
  assert.deepEqual(bindings.filter(r=>r.editionResourceId).map(r=>r.editionResourceId),edition.resources.map(r=>r.id));
  assert.ok(bindings.some(r=>r.href===edition.archive));
  for(const id of edition.supersededSupplementIds) assert.ok(!bindings.some(r=>r.supplementId===id));
  for(const old of ['22142022','22184511','22192066','22164344','22164552']) assert.ok(!bindings.some(r=>r.href.includes(old)));
  for(const row of bindings.filter(r=>r.editionResourceId)) assert.equal(row.contentLanguage,'id');
}
for(const locale of supportedLocales) {
  const stats=resourceBindings(interfaceCourses.find(r=>r.id==='C140'),locale);
  for(const id of ['random-mathematical-statistics-html','random-mathematical-statistics-pdf','random-mathematical-statistics-doi']) assert.ok(stats.some(r=>r.supplementId===id));
  const geo=resourceBindings(interfaceCourses.find(r=>r.id==='D100'),locale).filter(r=>r.editionResourceId);
  const d100Edition=editionInput.editions.find(e=>e.courseId==='D100');
  assert.equal(geo.length,6); assert.equal(geo.reduce((n,r)=>n+(d100Edition.resources.find(e=>e.id===r.editionResourceId)?.pages??0),0),975);
  assert.ok(!resourceBindings(interfaceCourses.find(r=>r.id==='B95'),locale).some(r=>r.href.includes('/id-ID/courses/B95/')));
  for(const id of ['A20','A30','B95']) assert.ok(!resourceBindings(interfaceCourses.find(r=>r.id===id),locale).some(r=>r.editionResourceId && r.format !== 'PDF'));
}
const actionBytes = await readFile(resolve(root, readerActionInput));
const actionInput = JSON.parse(actionBytes);
assert.deepEqual(projectReaderActions(actionInput, ids), verifiedReaderActions);
assert.equal(readerActionSource.bytes, actionBytes.length);
assert.equal(readerActionSource.sha256, createHash('sha256').update(actionBytes).digest('hex'));
assert.equal(verifiedReaderActions.length, 7);
assert.equal(verifiedReaderActions.reduce((sum, action) => sum + action.pages, 0), 4077);
for (const corrupt of [
  (input) => { input.actions[0].evidence.status = 'pending'; },
  (input) => { input.actions[1].action_id = input.actions[0].action_id; },
  (input) => { input.actions[0].sha256 = 'not-a-hash'; },
  (input) => { input.actions[0].url = 'javascript:alert(1)'; },
  (input) => { input.summary.pages += 1; },
]) { const changed = structuredClone(actionInput); corrupt(changed); assert.throws(() => projectReaderActions(changed, ids)); }
assert.equal(ids.length, 40);
assert.equal(new Set(ids).size, 40);
assert.equal(canonicalCourses.reduce((n, c) => n + c.prerequisites.length, 0), 83);
assert.deepEqual(interfaceCourses.map((c) => [c.id, c.level, c.topic, c.prerequisites]), canonicalCourses.map((c) => [c.id, c.level, c.topic, c.prerequisites]));
assert.deepEqual(Object.keys(englishResources).sort(), [...ids].sort());
for (const bad of ['javascript:alert(1)', 'data:text/html,foo', 'http://example.org/', '//example.org/evil\npath']) assert.throws(() => safeResourceUrl(bad));
assert.equal(safeResourceUrl('backend/index.html'), siteOrigin + 'backend/index.html');
assert.equal(LEARNER_STATE_STORAGE_KEY, 'program-matematika-indonesia/learner-state/v1');
let state = createEmptyLearnerState();
state = setCourseCompletion(state, canonicalCourses, 'A00', true);
state = setCourseClaim(state, canonicalCourses, 'placement', 'A10', true);
state = setPrerequisiteWaiver(state, canonicalCourses, 'B10', 'A30', true);
assert.deepEqual(evaluateLearnerState(canonicalCourses, state), evaluateLearnerState(interfaceCourses, state));
assert.deepEqual(normalizeLearnerState(JSON.parse(JSON.stringify(state)), canonicalCourses), state);
for (const course of interfaceCourses) for (const locale of supportedLocales) {
  const copy = coursePresentation(course, locale);
  assert.ok(copy.title && copy.purpose && copy.outcome && copy.topic, course.id + ' copy ' + locale);
  const bindings = resourceBindings(course, locale);
  assert.ok(bindings.length);
  assert.equal(new Set(bindings.map((row) => row.href + '\u0000' + row.accessRole)).size, bindings.length, 'No duplicate resource URL/role pair');
  const projected = bindings.filter((row) => row.actionId);
  const expected = verifiedReaderActions.filter((row) => row.courseId === course.id);
  assert.deepEqual(projected.map((row) => row.actionId), expected.map((row) => row.actionId));
  for (const row of projected) {
    assert.equal(row.contentLanguage, 'id', 'Interface language does not translate a book');
    assert.ok(row.label.endsWith(locale === 'id' ? ' halaman' : ' pages'), 'Localized reader labels');
    assert.ok(row.offlineAfterDownload);
  }
  for (const row of bindings) {
    assert.equal(Intl.getCanonicalLocales(row.contentLanguage)[0],row.contentLanguage, 'Actual BCP 47 material language');
    assert.equal(new URL(row.href).protocol, 'https:');
  }
  const card = renderCourseCard(course, locale);
  for (const prereq of course.prerequisites) assert.ok(card.includes('data-course-link="' + prereq + '"'));
  for (const next of canonicalCourses.filter((row) => row.prerequisites.includes(course.id))) assert.ok(card.includes('data-course-link="' + next.id + '"'));
  if (locale === 'en' && !englishResources[course.id].length) {
    assert.ok(englishBindingExceptions[course.id]);
    assert.ok(card.includes(interfaceCopy.en.noHostedReader));
    assert.ok(!bindings.some((row) => row.primary));
  }
}

// Unit-execute the built offline script against a minimal document model.
// No browser, screenshot, network, or user-visible window is launched.
function executeOffline(html, locale, sharedStorage = new Map(), options = {}) {
  const nodes = new Map(), documentEvents = new Map(), windowEvents = new Map();
  let address = new URL(options.url ?? 'https://example.test/hub/' + locale + '/?level=C#course-C30');
  const historyRows = [address.href];
  const fakeNode = (id, value = '') => ({
    id, value, innerHTML: '', textContent: '', hidden: false, disabled: false, checked: false, dataset: {}, files: [],
    events: new Map(), addEventListener(type, fn) { this.events.set(type, fn); },
    scrollIntoView() {}, focus() { this.focused = true; }, click() {}, getAttribute(name) { return this[name]; },
  });
  for (const id of ['search','topic','level','show','course-grid','result-count','empty-state','progress-summary','claims','storage-message','placement-course','equivalence-course','waiver-target','waiver-prereq','add-placement','add-equivalence','add-waiver','reset-filters','clear-progress','export-progress','import-progress']) {
    nodes.set('#' + id, fakeNode(id, ['topic','level','show'].includes(id) ? 'all' : id.endsWith('-course') || id === 'waiver-target' ? 'A00' : ''));
  }
  const localeLinks = [...html.matchAll(/<a data-locale-link="([^"]+)" data-locale-base="([^"]+)" href="([^"]+)"/g)].map((match) => ({ ...fakeNode(match[1]), 'data-locale-base': match[2], href: match[3] }));
  assert.deepEqual(localeLinks.map(link => link.id), supportedLocales, 'Use actual generated language anchors');
  const classNames = new Set();
  const doc = {
    documentElement: { lang: locale, classList: { add: (name) => classNames.add(name) } },
    querySelector(selector) {
      if (nodes.has(selector)) return nodes.get(selector);
      if (/^#course-[A-D]\d{2,3}$/.test(selector) && nodes.get('#course-grid').innerHTML.includes('id="' + selector.slice(1) + '"')) return fakeNode(selector);
      return null;
    },
    querySelectorAll: (selector) => selector === '[data-locale-link]' ? localeLinks : [],
    addEventListener: (type, fn) => documentEvents.set(type, fn),
    createElement: () => fakeNode('temporary'),
  };
  const fakeStorage = {
    getItem: (key) => sharedStorage.get(key) ?? null,
    setItem: (key, value) => { if (options.failWrites) throw new Error('Quota exceeded'); sharedStorage.set(key, value); },
    removeItem: (key) => sharedStorage.delete(key),
  };
  const win = { localStorage: fakeStorage, confirm: () => true, addEventListener: (type, fn) => windowEvents.set(type, fn) };
  if (options.noStorage) Object.defineProperty(win, 'localStorage', { get() { throw new Error('Unavailable'); } });
  const context = vm.createContext({
    console, URL, URLSearchParams, Blob, Intl, document: doc, window: win,
    get location() { return address; },
    history: {
      replaceState(_state, _title, url) { if (options.failHistory) throw new Error('History unavailable'); address = new URL(url, address); historyRows[historyRows.length - 1] = address.href; },
      pushState(_state, _title, url) { if (options.failHistory) throw new Error('History unavailable'); address = new URL(url, address); historyRows.push(address.href); },
    },
    requestAnimationFrame: (fn) => fn(), setTimeout: () => 0,
  });
  const code = html.match(/<script>\n([\s\S]*)\n<\/script>/)?.[1];
  assert.ok(code, 'Offline inline script');
  new vm.Script(code, { filename: locale + '-offline.js' }).runInContext(context, { timeout: 5000 });
  assert.ok(classNames.has('js'), 'Initialization completed');
  return { doc, nodes, documentEvents, windowEvents, localeLinks, historyRows, sharedStorage, fakeStorage, context, address: () => address };
}
const sizes = [];
const receipt = JSON.parse(await readFile(resolve(root, 'docs/interface/build-receipt.json'), 'utf8'));
for (const item of [...receipt.inputs, ...receipt.outputs]) {
  const bytes = await readFile(resolve(root, item.path));
  assert.equal(bytes.length, item.bytes, item.path);
  assert.equal(createHash('sha256').update(bytes).digest('hex'), item.sha256, item.path);
}
for (const locale of supportedLocales) for (const file of ['index.html', 'learning-map.html', 'learning-map-paired.html']) {
  const html = await readFile(resolve(root, 'docs', locale, file), 'utf8');
  assert.ok(html.includes('<html lang="' + locale + '">'));
  const staticHtml = html.replace(/<script[\s\S]*?<\/script>/g, '');
  const cardIds = [...staticHtml.matchAll(/<article class="course-card" id="course-([^"]+)"/g)].map((m) => m[1]);
  assert.deepEqual(cardIds, ids, locale + '/' + file + ' static coverage');
  assert.equal([...staticHtml.matchAll(/data-reader-action="([^"]+)"/g)].length, 7, 'Seven verified CLP actions visible in static markup');
  for (const action of verifiedReaderActions) assert.ok(staticHtml.includes(action.href.replaceAll('&', '&amp;')));
  assert.equal([...staticHtml.matchAll(/data-edition-resource="([^"]+)"/g)].length,14);
  for (const resource of finalResources) assert.ok(staticHtml.includes(resource.href.replaceAll('&','&amp;')));
  assert.equal([...staticHtml.matchAll(/data-capability-tool="([^"]+)"/g)].length,24);
  assert.equal([...staticHtml.matchAll(/data-supplemental-reader="([^"]+)"/g)].length,supplementalReaders.length);
  for (const row of supplementalReaders) assert.ok(staticHtml.includes(row.href.replaceAll('&','&amp;')));
  for(const courseId of ['A10','A20','B80','D50','D70','D80','D100']) for(const row of englishResources[courseId]) assert.ok(staticHtml.includes(row.href.replaceAll('&','&amp;')));
  const elementIds = [...staticHtml.matchAll(/\bid="([^"]+)"/g)].map((m) => m[1]);
  assert.equal(new Set(elementIds).size, elementIds.length, 'No duplicate DOM ids');
  for (const match of staticHtml.matchAll(/href="#([^"]+)"/g)) assert.ok(elementIds.includes(match[1]), 'Resolvable fragment: ' + match[1]);
  for (const code of supportedLocales) assert.ok(html.includes('data-locale-link="' + code + '"'));
  assert.ok(html.includes('hreflang="x-default"'));
  assert.ok(html.includes('No') || locale === 'id');
  for (const match of staticHtml.matchAll(/(?:src|href)="([^"]+)"/g)) {
    if (match[1].startsWith('#')) continue;
    if (/^https:\/\//.test(match[1])) continue;
    if (file === 'learning-map-paired.html') {
      assert.ok(supportedLocales.some(code => match[1] === '../' + code + '/learning-map-paired.html'), 'Only paired language anchors may be relative');
    } else assert.equal(file, 'index.html', 'Standalone document must have no relative dependency: ' + match[1]);
    const target = resolve(root, 'docs', locale, match[1], match[1].endsWith('/') ? 'index.html' : '');
    await readFile(target);
  }
  sizes.push({ locale, file, bytes: Buffer.byteLength(html), gzipBytes: gzipSync(html).length });
  if (file !== 'index.html') {
    assert.ok(!/<script[^>]+src=|<link[^>]+rel="stylesheet"/.test(html), 'Self-contained executable/style');
    // Preserve a compact payload while retaining typed access roles, evidence-bound mirrors, and tools.
    assert.ok(Buffer.byteLength(html) < 400000, 'Offline map size budget');
    // D100's complete bilingual access block now includes four byte-identified
    // central routes plus the separate edition host. Keep one measured budget
    // for that additional offline access evidence without dropping any route.
    assert.ok(gzipSync(html).length < 77000, 'Compressed map size budget');
    const run = executeOffline(html, locale);
    // Compact payload must preserve all effective data, not just course counts.
    assert.deepEqual(JSON.parse(vm.runInContext('JSON.stringify(interfaceCourses)',run.context)),JSON.parse(JSON.stringify(interfaceCourses)));
    for (const c of interfaceCourses) {
      const actual=JSON.parse(vm.runInContext('JSON.stringify(resourceBindings(interfaceCourses.find(c=>c.id==='+JSON.stringify(c.id)+'),'+JSON.stringify(locale)+'))',run.context));
      assert.deepEqual(actual,resourceBindings(c,locale),'Online/offline binding equality: '+c.id);
    }
    assert.ok(run.nodes.get('#course-grid').innerHTML.includes('id="course-C30"'));
    for (const link of run.localeLinks) { assert.ok(link.href.endsWith('?level=C#course-C30')); }
    run.nodes.get('#search').value = 'zzzz-no-matches';
    run.nodes.get('#search').events.get('input')();
    assert.equal(run.nodes.get('#course-grid').innerHTML, '');
    assert.equal(run.nodes.get('#empty-state').hidden, false);
    assert.equal(run.address().hash, '', 'Changing a filter clears a stale course fragment');
    const reload = executeOffline(html, locale, run.sharedStorage, { url: run.address().href });
    assert.equal(reload.nodes.get('#course-grid').innerHTML, '', 'Reload preserves zero-match filter');
    for (const link of run.localeLinks) assert.ok(link.href.includes('q=zzzz-no-matches') && !link.href.includes('#course-'));
    run.nodes.get('#reset-filters').events.get('click')();
    assert.equal((run.nodes.get('#course-grid').innerHTML.match(/<article /g) ?? []).length, 40);
    const event = { target: { closest: (selector) => selector === '[data-course-link]' ? { dataset: { courseLink: 'A00' } } : null }, button: 0, preventDefault() {} };
    run.documentEvents.get('click')(event);
    assert.equal(run.historyRows.length, 2, 'Course navigation creates history, not replace-only');
    assert.equal(run.address().hash, '#course-A00');
    assert.ok(run.windowEvents.has('popstate') && run.windowEvents.has('hashchange'));
    run.documentEvents.get('change')({ target: { matches: () => true, dataset: { completion: 'A00' }, checked: true } });
    const stored = JSON.parse(run.sharedStorage.get(LEARNER_STATE_STORAGE_KEY));
    assert.ok(stored.completedCourseIds.includes('A00'));
    const otherLocale = locale === 'id' ? 'en' : 'id';
    const otherHtml = await readFile(resolve(root, 'docs', otherLocale, 'learning-map.html'), 'utf8');
    const next = executeOffline(otherHtml, otherLocale, run.sharedStorage, { url: 'https://example.test/hub/' + otherLocale + '/' });
    assert.ok(next.nodes.get('#course-grid').innerHTML.includes('data-completion="A00" checked'), 'Progress crosses locales');
    next.nodes.get('#show').value = 'completed';
    next.nodes.get('#show').events.get('change')();
    next.doc.activeElement = { dataset: { completion: 'A00' } };
    next.documentEvents.get('change')({ target: { matches: () => true, dataset: { completion: 'A00' }, checked: false } });
    assert.equal(next.nodes.get('#result-count').focused, true, 'Removing a visible completed card restores focus to results');
    next.nodes.get('#show').value = 'eligible';
    next.nodes.get('#show').events.get('change')();
    next.nodes.get('#result-count').focused = false;
    next.doc.activeElement = { dataset: { completion: 'A00' } };
    next.documentEvents.get('change')({ target: { matches: () => true, dataset: { completion: 'A00' }, checked: true } });
    assert.equal(next.nodes.get('#result-count').focused, true, 'Completing an eligible card restores focus to results');
    for (const base of ['file:///C:/Learning%20folder/Matematika%20%E6%95%B0%E5%AD%A6/docs/', 'https://example.test/unpacked/docs/']) {
      const fileUrl = base + locale + '/' + file;
      const unknown = executeOffline(html, locale, new Map(), { url: fileUrl + '?progress=QUERY_SENTINEL#completedCourseIds=FRAGMENT_SENTINEL', failHistory: true });
      for (const action of [() => {}, () => unknown.windowEvents.get('hashchange')(), () => unknown.windowEvents.get('popstate')()]) {
        action();
        for (const link of unknown.localeLinks) assert.ok(!link.href.includes('SENTINEL') && !new URL(link.href).hash, 'Only known navigation fragments propagate');
      }
      for (const fragment of ['#top', '#katalog', '#progress', '#about']) {
        unknown.address().hash = fragment; unknown.windowEvents.get('hashchange')();
        for (const link of unknown.localeLinks) assert.equal(new URL(link.href).hash, fragment);
      }
      const offline = executeOffline(html, locale, new Map(), { noStorage: true, failHistory: true, url: fileUrl + '?level=C&progress=private&claims=private#course-C30' });
      for (const link of offline.localeLinks) {
        const actual = new URL(link.href);
        const expected = file === 'learning-map-paired.html' ? base + link.id + '/learning-map-paired.html' : siteOrigin + link.id + '/';
        assert.equal(actual.origin + actual.pathname, new URL(expected).origin + new URL(expected).pathname);
        assert.equal(actual.search, '?level=C');
        assert.equal(actual.hash, '#course-C30');
        assert.ok(!actual.href.includes('private'), 'Do not propagate unknown/progress query data');
      }
      offline.nodes.get('#search').value = 'new search';
      offline.nodes.get('#search').events.get('input')();
      assert.ok(offline.address().href.includes('#course-C30'), 'Throwing history leaves old address unchanged');
      for (const link of offline.localeLinks) {
        assert.equal(new URL(link.href).searchParams.get('q'), 'new search', 'Current filters survive rejected history write');
        assert.equal(new URL(link.href).hash, '', 'Stale course fragment is cleared in navigation despite rejected history');
      }
      offline.nodes.get('#reset-filters').events.get('click')();
      offline.documentEvents.get('click')(event);
      for (const link of offline.localeLinks) assert.equal(new URL(link.href).hash, '#course-A00', 'Course navigation fallback retains current fragment');
      const imported = JSON.stringify(state);
      await offline.nodes.get('#import-progress').events.get('change')({ target: { files: [{ size: imported.length, text: async () => imported }], value: 'record.json' } });
      assert.ok(offline.nodes.get('#course-grid').innerHTML.includes('data-completion="A00" checked'), 'Import moves progress into isolated/offline context');
      offline.nodes.get('#show').value = 'completed';
      offline.nodes.get('#show').events.get('change')();
      for (const link of offline.localeLinks) {
        assert.equal(new URL(link.href).search, '?show=completed');
        assert.equal(new URL(link.href).hash, '');
        assert.ok(!link.href.includes('placement') && !link.href.includes('waiver') && !link.href.includes('completedCourseIds'));
      }
    }
    const quota = executeOffline(html, locale, new Map(), { failWrites: true, url: 'https://example.test/' + locale + '/' });
    quota.documentEvents.get('change')({ target: { matches: () => true, dataset: { completion: 'A00' }, checked: true } });
    for (const event of [{ key: 'unrelated-preference', storageArea: quota.fakeStorage }, { key: LEARNER_STATE_STORAGE_KEY, storageArea: quota.fakeStorage }, { key: null, storageArea: quota.fakeStorage }]) {
      quota.windowEvents.get('storage')(event);
      assert.ok(quota.nodes.get('#course-grid').innerHTML.includes('data-completion="A00" checked'), 'Failed-write progress survives cross-tab events');
    }
    const sync = executeOffline(html, locale, new Map(), { url: 'https://example.test/' + locale + '/' });
    sync.sharedStorage.set(LEARNER_STATE_STORAGE_KEY, JSON.stringify(setCourseCompletion(createEmptyLearnerState(), canonicalCourses, 'A00', true)));
    sync.windowEvents.get('storage')({ key: 'unrelated-preference', storageArea: sync.fakeStorage });
    assert.ok(!sync.nodes.get('#course-grid').innerHTML.includes('data-completion="A00" checked'));
    sync.windowEvents.get('storage')({ key: LEARNER_STATE_STORAGE_KEY, storageArea: {} });
    assert.ok(!sync.nodes.get('#course-grid').innerHTML.includes('data-completion="A00" checked'));
    sync.windowEvents.get('storage')({ key: LEARNER_STATE_STORAGE_KEY, storageArea: sync.fakeStorage });
    assert.ok(sync.nodes.get('#course-grid').innerHTML.includes('data-completion="A00" checked'), 'Matching persisted progress event still synchronizes');
  }
}
console.log(JSON.stringify({ status: 'pass', courses: ids.length, edges: 83, locales: supportedLocales, tests: ['graph-identity','explicit-language-bindings','static-40-course-catalogs','all-internal-fragments','safe-https-links','offline-script-execution','search-and-reset','course-history','shared-progress','storage-unavailable','receipt-hashes','rendered-language-anchors','paired-static-local-closure','standalone-online-fallback','file-and-unicode-paths','history-rejection-current-view','navigation-no-progress-data','isolated-progress-import'], sizes }));
