import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const base=path.join(root,'backend/course-capsule-v1/adapters/openlogic-teacher-v1');
const script=fs.readFileSync(path.join(base,'ui/teacher.js'));
const modelBytes=fs.readFileSync(path.join(base,'site/C80.teacher.json'));
const context={};vm.createContext(context);vm.runInContext(script.toString('utf8'),context);
const api=context.OpenLogicTeacher,model=JSON.parse(modelBytes);let positive=0,negative=0;
for(const locale of ['id','en'])for(const selected of [new Set(),new Set(model.questions.slice(0,3).map(q=>q.id)),new Set(model.questions.map(q=>q.id))]){
  const packet=JSON.parse(JSON.stringify(api.exportSelection(model,selected,locale)));
  assert.deepEqual([...api.importSelection(model,packet)],[...selected]);positive++;
}
for(const topic of Object.keys(model.topics)){
  assert.equal(model.questions.filter(q=>api.matches(q,topic,'',false,'')).length,model.questions.filter(q=>q.topic===topic).length);positive++;
}
for(const chapter of new Set(model.questions.map(q=>q.chapter))){
  assert.equal(model.questions.filter(q=>api.matches(q,'',chapter,false,'')).length,model.questions.filter(q=>q.chapter===chapter).length);positive++;
}
assert.equal(model.questions.filter(q=>api.matches(q,'','',true,'')).length,30);positive++;
const unique=new Map();for(const q of model.questions){const values=unique.get(q.source_problem_id)||[];values.push(q.id);unique.set(q.source_problem_id,values);}
const reused=[...unique.values()].filter(ids=>ids.length>1).flat();
assert.equal(reused.length,30);assert.equal(new Set(reused).size,30);
assert.equal(api.exportSelection(model,new Set(reused),'id').exercises.length,30);positive++;
const packet=JSON.parse(JSON.stringify(api.exportSelection(model,new Set(model.questions.slice(0,2).map(q=>q.id)),'id')));
const mutations=[p=>p.schema='wrong',p=>p.course_id='C90',p=>p.locale='zh',p=>p.edition_binding='wrong',
 p=>p.reader.sha256='wrong',p=>p.reference_only=false,p=>p.extra=true,p=>p.exercises=null,
 p=>p.exercises.push(p.exercises[0]),p=>p.exercises.reverse(),p=>p.exercises[0]=null,
 p=>p.exercises[0].id='unknown',p=>p.exercises[0].physical_page=1,p=>p.exercises[0].number='999',
 p=>p.exercises[0].solution_state='complete',p=>p.exercises[0].reader_url='javascript:alert(1)',
 p=>p.exercises[0].mapping.target.block.sha256='wrong',p=>p.exercises[0].mapping.source.byte_start=0,
 p=>p.exercises[0].local_reader_url='../unrelated',p=>p.exercises[0].source_problem_id=model.source_only[0].id];
for(const mutate of mutations){const copy=structuredClone(packet);mutate(copy);assert.throws(()=>api.importSelection(model,copy));negative++;}
for(const id of ['unknown',...model.source_only.map(q=>q.id)]){assert.throws(()=>api.exportSelection(model,new Set([id]),'id'));negative++;}
assert.throws(()=>api.exportSelection(model,new Set(),'zh'));negative++;
const hash=body=>({bytes:body.length,sha256:createHash('sha256').update(body).digest('hex')});
const result={schema:'openlogic-teacher-ui-tests/1',state:'pass',positive,negative,
 edition_binding:model.edition_binding,script:hash(script),model:hash(modelBytes),
 scope:'Selection/filter/import-export functions; browser DOM behaviour verified separately.'};
fs.writeFileSync(path.join(base,'ui-tests.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
