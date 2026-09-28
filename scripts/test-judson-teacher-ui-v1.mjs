import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const base=path.join(root,'backend/course-capsule-v1/adapters/judson-teacher-v1');
const context={};vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(base,'ui/teacher.js'),'utf8'),context);
const api=context.JudsonTeacher;let tests=0;
for(const role of ['C30','C40']){
  const model=JSON.parse(fs.readFileSync(path.join(base,'site',role+'.teacher.json')));
  for(const locale of ['id','en']){
    for(const selected of [new Set(),new Set(model.questions.slice(0,3).map(q=>q.id)),new Set(model.questions.map(q=>q.id))]){
      const packet=JSON.parse(JSON.stringify(api.exportSelection(model,selected,locale)));
      assert.deepEqual([...api.importSelection(model,packet)],[...selected]);tests++;
    }
  }
  for(const c of model.chapters){
    assert.equal(model.questions.filter(q=>api.matches(q,c.native_unit_id,'','')).length,
      model.questions.filter(q=>q.chapter_id===c.native_unit_id).length);tests++;
  }
  for(const mode of ['hint','nohint','response','sage']){
    const expected=model.questions.filter(q=>mode==='hint'?q.hint_count>0:mode==='nohint'?q.hint_count===0:mode==='response'?q.response_slot_count>0:q.primary_edition==='sage');
    assert.equal(model.questions.filter(q=>api.matches(q,'',mode,'')).length,expected.length);tests++;
  }
  const packet=JSON.parse(JSON.stringify(api.exportSelection(model,new Set([model.questions[0].id]),'id')));
  const bad=[
    p=>p.schema='other',p=>p.course_id='other',p=>p.input_sha256='other',p=>p.source_archive_sha256='other',
    p=>p.reference_only=false,p=>p.locale='other',p=>p.extra='untrusted',p=>p.exercises=null,
    p=>p.exercises.push(p.exercises[0]),p=>p.exercises[0].id='unknown',p=>p.exercises[0].native_id='wrong',
    p=>p.exercises[0].hint_count=999,p=>p.exercises[0].supplied_response_count=1,
    p=>p.exercises[0].readers[0].offline_href='javascript:alert(1)',p=>p.exercises[0].source_c14n_sha256='wrong',
    p=>p.exercises[0].support=[],p=>p.exercises[0]=null,
  ];
  for(const mutate of bad){const p=structuredClone(packet);mutate(p);assert.throws(()=>api.importSelection(model,p));tests++;}
  assert.throws(()=>api.exportSelection(model,new Set(['unknown']),'id'));tests++;
}
console.log(JSON.stringify({state:'pass',selectionAndRejectionChecks:tests,domBehaviour:'not covered by pure-function test'}));
