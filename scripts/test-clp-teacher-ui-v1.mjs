import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const base=new URL('../backend/course-capsule-v1/adapters/clp-teacher-v1/',import.meta.url);
const context=vm.createContext({});
vm.runInContext(await readFile(new URL('ui/teacher.js',base),'utf8'),context);
const api=context.CLPTeacher;
let tested=0;
for(const role of ['B20','B30','B50','B60']){
  const model=JSON.parse(await readFile(new URL(`site/${role}.teacher.json`,base),'utf8'));
  const ids=new Set(model.questions.filter((_,i)=>i%7===0).map(q=>q.id));
  const exported=api.exportSelection(model,ids,'id');
  assert.deepEqual([...api.importSelection(model,exported)],[...ids]);
  const en=api.exportSelection(model,ids,'en');
  assert.deepEqual([...api.importSelection(model,en)],[...ids]);
  assert.equal(en.boundary,model.limitations.en);
  const hints=model.questions.filter(q=>api.matches(q,'','hint',''));
  const noHints=model.questions.filter(q=>api.matches(q,'','nohint',''));
  assert.equal(hints.length+noHints.length,model.questions.length);
  assert.equal(api.matches(model.questions[0],'nonexistent','',''),false);
  assert.equal(api.matches(model.questions[0],'','',model.questions[0].native_id),true);
  for(const mutate of [d=>{d.course_id='D100'},d=>{d.input_sha256='0'.repeat(64)},d=>{d.exercises.push(d.exercises[0])},d=>{d.exercises[0].id='unknown'},d=>{d.exercises[0].surfaces[0].target.file='wrong'},d=>{d.exercises[0].surfaces[0].components.solution=[]}]){
    const bad=structuredClone(exported);mutate(bad);assert.throws(()=>api.importSelection(model,bad));tested++;
  }
  const multi=model.questions.filter(q=>api.matches(q,'','multi',''));
  assert.equal(multi.length,role==='B50'?2:role==='B60'?11:0);
}
console.log(JSON.stringify({state:'pass',courses:4,hostile_imports_rejected:tested,language_roundtrips:8}));
