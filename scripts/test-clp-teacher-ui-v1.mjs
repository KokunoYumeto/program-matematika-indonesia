import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const base=new URL('../backend/course-capsule-v1/adapters/clp-teacher-v1/',import.meta.url);
const context=vm.createContext({URL});
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
  if(role==='B20'){
    assert.equal(model.navigation_reader.sha256,'911b2a0e3a9de6eccb9dd93042fa697e8f02e4bb1ecdacec86ade68744245021');
    assert.equal(model.questions.reduce((n,q)=>n+api.readingLinks(model,q).length,0),2705);
    for(const q of model.questions){
      const links=api.readingLinks(model,q);
      assert.equal(links[0].kind,'question');
      assert.equal(links.some(l=>l.kind==='hint'),api.has(q,'hint'));
      for(const link of links){
        const url=new URL(link.url);
        assert.equal(url.hash,`#page=${link.page}`);
        assert.equal(url.pathname,new URL(model.navigation_reader.url).pathname);
        assert.equal(url.searchParams.has('download'),false);
      }
    }
    const legacy=structuredClone(exported);
    delete legacy.navigation_sha256;
    for(const q of legacy.exercises)delete q.navigation;
    assert.deepEqual([...api.importSelection(model,legacy)],[...ids]);
    for(const mutate of [d=>{d.navigation_sha256='0'.repeat(64)},d=>{d.exercises[0].navigation.printed.page+=1},d=>{d.exercises[0].navigation.supports[0].printed.page+=1},d=>{d.exercises[0].navigation.supports=[]}]){
      const bad=structuredClone(exported);mutate(bad);assert.throws(()=>api.importSelection(model,bad));tested++;
    }
    const wrongPage=structuredClone(model.questions[0]);wrongPage.navigation.printed.page=999;assert.throws(()=>api.readingLinks(model,wrongPage));tested++;
    const wrongReader=structuredClone(model);wrongReader.navigation_reader.url='https://example.com/wrong.pdf';assert.throws(()=>api.readingLinks(wrongReader,model.questions[0]));tested++;
  } else {
    assert.equal(model.navigation_identity,undefined);
    assert.equal(api.readingLinks(model,model.questions[0]).length,0);
  }
}
console.log(JSON.stringify({state:'pass',courses:4,hostile_import_and_reader_cases_rejected:tested,language_roundtrips:8,b20_reader_links:2705,legacy_b20_assignment_preserved:true}));
