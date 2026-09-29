import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile} from 'node:fs/promises';
import {resolve} from 'node:path';

export const clp1EvidencePaths = {
  clp1Navigation:'backend/course-capsule-v1/adapters/clp-teacher-v1/clp1-navigation.json',
  clp1NavigationValidation:'backend/course-capsule-v1/adapters/clp-teacher-v1/clp1-navigation-validation.json',
  clp1NavigationLock:'backend/course-capsule-v1/adapters/clp-teacher-v1/input/clp1-navigation-lock.json',
};
const identity=bytes=>({bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex')});
export async function loadClp1Evidence(root){
  const bytes={};
  for(const [key,path] of Object.entries(clp1EvidencePaths))bytes[key]=await readFile(resolve(root,path));
  return {bytes,data:Object.fromEntries(Object.entries(bytes).map(([key,value])=>[key,JSON.parse(value)]))};
}

export function validateClp1Evidence(data,bytes,hosted,tests){
  const map=data.clp1Navigation,check=data.clp1NavigationValidation,lock=data.clp1NavigationLock;
  const counts={questions:695,hints:620,answers:695,solutions:695,questions_without_recorded_hint:75,reparented_questions:30};
  assert.equal(lock.schema,'clp1-navigation-lock/1');
  assert.deepEqual(lock.mapping,identity(bytes.clp1Navigation),'B20 mapping identity drift');
  assert.deepEqual(lock.validation,identity(bytes.clp1NavigationValidation),'B20 validation identity drift');
  assert.equal(map.schema,'clp1-exact-navigation/1');
  assert.equal(check.state,'pass');
  assert.deepEqual(check.mapping,lock.mapping);
  assert.deepEqual(check.source_pdf_replays,[lock.mapping,lock.mapping]);
  assert.equal(check.independent_annotation_comparison.matched_supports,2010);
  assert.equal(new Set(check.negative_fixtures).size,17);
  assert.deepEqual(map.counts,counts);assert.deepEqual(check.counts,counts);
  assert.equal(map.inputs.native.sha256,lock.native_sha256);
  assert.equal(tests.input_identity.sha256,lock.native_sha256);
  assert.equal(tests.state,'pass');
  assert.deepEqual(tests.b20_navigation_identity,lock.mapping);
  assert.equal(tests.b20_printed_reader_links,2705);
  assert.equal(tests.other_clp_profiles_unchanged,true);
  assert.equal(map.questions.length,695);
  assert.equal(new Set(map.questions.map(q=>q.native_id)).size,695);
  assert.equal(new Set(map.questions.map(q=>q.common_id)).size,695);
  const supports=map.questions.flatMap(q=>q.supports);
  assert.equal(supports.length,2010);
  assert.equal(new Set(supports.map(s=>s.native_id)).size,2010);
  for(const [kind,n] of [['hint',620],['answer',695],['solution',695]])assert.equal(supports.filter(s=>s.kind===kind).length,n);
  assert.equal(map.questions.filter(q=>!q.supports.some(s=>s.kind==='hint')).length,75);
  assert.deepEqual(hosted.precise_target_exercise_alignment,{B20:true,B30:true,B50:true,B60:true});
  assert.deepEqual(hosted.b20_navigation,{
    mapping:lock.mapping,validation:lock.validation,counts,reader:map.reader,
    printed_reader_links:2705,native_states_preserved:true,
    scope:'source_target_structural_spans_and_pdf_start_pages_not_semantic_review',
  });
  return hosted.b20_navigation;
}
