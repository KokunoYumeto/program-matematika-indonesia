const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const base=path.join(root,'backend/course-capsule-v1/adapters/c130-teacher-v1');
const vm=require('node:vm');
const context={module:{exports:{}}};
vm.runInNewContext(fs.readFileSync(path.join(base,'ui/teacher.js'),'utf8'),context);
const api=context.module.exports;
const model=JSON.parse(fs.readFileSync(path.join(base,'site/planner-model.json'),'utf8'));
api.validateModel(model);
let positive=1,negative=0;
function good(check){assert.ok(check);positive++;}
function bad(fn){assert.throws(fn);negative++;}
const ids=new Set(model.questions.filter(q=>q.chapter===14).map(q=>q.id));
good(ids.size===24);
good(api.select(model,{chapter:'14'}).length===24);
good(api.select(model,{support:'manual'}).length===203);
good(api.select(model,{support:'none'}).length===24);
good(api.select(model,{search:'c130:graph-practice:'}).length===13);
good(api.select(model,{selected:true,ids}).length===24);
good(api.select(model,{kind:'learningcheckpoint'}).length===12);
good(api.select(model,{kind:'tryit'}).length===12);
good(api.select(model,{kind:'graph-practice'}).length===19);
good(api.select(model,{kind:'numbered-exercise'}).length===184);
good(api.select(model,{search:'14 / G19'}).length===1);
good(model.supplementary_solutions.length===132);
good(model.supplementary_solutions.filter(s=>s.page===null).length===0);
good(model.supplementary_solutions.filter(s=>s.printed_state==='native-reference-and-unique-solution-heading'&&Number.isInteger(s.page)).length===12);
good(model.supplementary_solutions.filter(s=>s.printed_state==='ordered-composite-literal-passages'&&Number.isInteger(s.page)).length===14);
good(model.supplementary_solutions.filter(s=>s.printed_state==='adjacent-example-and-solution-opening'&&Number.isInteger(s.page)).length===2);
for(const chosen of [new Set(),ids,new Set(model.questions.map(q=>q.id))]) {
 const exchange=api.exportSelection(model,chosen);
 good(JSON.stringify([...api.importSelection(model,exchange)])===JSON.stringify([...chosen]));
}
const canonical=api.exportSelection(model,ids);
function altered(fn){const copy=JSON.parse(JSON.stringify(canonical));fn(copy);bad(()=>api.importSelection(model,copy));}
altered(v=>v.mapping_sha256='0'.repeat(64));
altered(v=>v.reader_sha256='0'.repeat(64));
altered(v=>v.course_id='C80');
altered(v=>v.schema='other');
altered(v=>v.extra=true);
altered(v=>v.questions.push(v.questions[0]));
altered(v=>v.questions[0].page++);
altered(v=>v.questions[0].id='unknown');
altered(v=>v.questions[0].source.sha256='0'.repeat(64));
altered(v=>v.questions[0].manual=[]);
altered(v=>v.questions.reverse());
altered(v=>v.questions[0].title='<script>bad</script>');
bad(()=>api.exportSelection(model,new Set(['unknown'])));
bad(()=>api.importSelection(model,null));
const duplicate=structuredClone(model);duplicate.questions[1]=duplicate.questions[0];bad(()=>api.validateModel(duplicate));
const offpage=structuredClone(model);offpage.questions[0].page=667;bad(()=>api.validateModel(offpage));
const badAnswer=structuredClone(model);badAnswer.questions.find(q=>q.manual.length).manual[0].page=0;bad(()=>api.validateModel(badAnswer));
const badKind=structuredClone(model);badKind.questions[0].kind='invented';bad(()=>api.validateModel(badKind));
const crypto=require('node:crypto');
function fact(p){const b=fs.readFileSync(p);return {bytes:b.length,sha256:crypto.createHash('sha256').update(b).digest('hex')};}
const report={state:'pass',positive,negative,questions:model.questions.length,chapter14:ids.size,
 mapping_sha256:model.mapping_sha256,script:fact(path.join(base,'ui/teacher.js')),model:fact(path.join(base,'site/planner-model.json'))};
fs.writeFileSync(path.join(base,'ui-tests.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
