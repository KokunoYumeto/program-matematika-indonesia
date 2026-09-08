import assert from 'node:assert/strict';
import {readFile,access} from 'node:fs/promises';
import {resolve} from 'node:path';
import vm from 'node:vm';

const base=resolve(process.argv[2] ?? 'backend/course-capsule-v1/adapters/a10-capability-v1');
const rows=(await readFile(resolve(base,'data/exercise-index.jsonl'),'utf8')).trim().split('\n').map(JSON.parse);
const modules=(await readFile(resolve(base,'data/module-index.jsonl'),'utf8')).trim().split('\n').map(JSON.parse);
let assertions=0;
for (const suffix of ['', '-en', '-pengajar', '-pengajar-en']) {
  const html=await readFile(resolve(base,`views/A10${suffix}.html`),'utf8');
  assert.match(html,new RegExp(`<html lang="${suffix.endsWith('-en')?'en':'id'}">`));
  const data=JSON.parse(html.match(/<script type="application\/json" id="a10-data">([\s\S]*?)<\/script>/)[1]);
  const code=html.match(/<script>([\s\S]*?)<\/script>/)[1];
  const context=vm.createContext({});new vm.Script(code).runInContext(context,{timeout:1000});
  const helpers=context.A10Selection;
  assert.equal(data.exercises.length,9406);assert.equal(data.modules.length,82);
  assert.equal(new Set(data.exercises.map(r=>r.id)).size,9406);
  assert.equal(data.html_reader.content_language,'id-ID');
  assert.equal(data.html_reader.reading_language_follows_interface,false);
  for (const [index,row] of rows.entries()) {
    for (const key of ['exercise_html_url','problem_html_url','solution_html_url'])
      assert.equal(data.exercises[index][key],row[key]);
    assert.ok(row.exercise_html_url.endsWith('#'+encodeURIComponent(row.module_id+'--'+row.source_element_id)));
    assert.equal(Boolean(row.solution_html_url),Boolean(row.solution_id));
  }
  for (const module of modules) {
    const expected=rows.filter(r=>r.module_id===module.module_id);
    for (const state of ['all','provided','missing']) {
      const actual=helpers.selectExercises(data,module.module_id,state,'');
      const ids=expected.filter(r=>state==='all'||Boolean(r.solution_id)===(state==='provided')).map(r=>r.id);
      assert.deepEqual(Array.from(actual,r=>r.id),ids);assertions++;
    }
  }
  const sample=rows.find(r=>r.solution_id===null);
  assert.equal(helpers.selectExercises(data,sample.module_id,'missing',sample.id).length,1);
  const selectedIds=modules.filter(m=>m.exercise_count).slice(0,3).map(m=>m.module_id);
  const selection=helpers.makeSelection(data,selectedIds.reverse());
  assert.deepEqual(Array.from(selection.modules,m=>m.module_id),modules.filter(m=>selectedIds.includes(m.module_id)).map(m=>m.module_id));
  assert.deepEqual(Array.from(selection.exercises,r=>r.exercise_id),rows.filter(r=>selectedIds.includes(r.module_id)).map(r=>r.id));
  assert.ok(selection.exercises.every(r=>r.ordinal_is_printed_exercise_number===false));
  assert.throws(()=>helpers.makeSelection(data,[]));assert.throws(()=>helpers.makeSelection(data,['unknown']));
  assert.equal(selection.selection_is_full_text,false);
  assert.equal(selection.selection_is_a_new_curriculum_claim,false);
  assert.equal(selection.source_html_body_sha256,data.html_reader.reader_body.sha256);
  for (const module of selection.modules) {
    const source=modules.find(m=>m.module_id===module.module_id);
    assert.equal(module.reader_url,source.html_url);assert.equal(module.pdf_url,source.url);
  }
  for (const exercise of selection.exercises) {
    const original=rows.find(r=>r.id===exercise.exercise_id);
    assert.equal(exercise.exercise_html_url,original.exercise_html_url);
    assert.equal(exercise.solution_html_url,original.solution_html_url);
    assert.equal(exercise.reading_language,'id-ID');
  }
  const price=helpers.selectTerms(data,'m82452','cost per pound');
  const old=price.find(t=>t.ledger_id==='EA2-T0309');
  const current=price.find(t=>t.ledger_id==='EA2-T0452');
  assert.ok(old && current);
  assert.deepEqual(Array.from(old.superseded_by),[current.id]);
  assert.equal(old.current_use_status,'superseded_in_native_ledger');
  assert.equal(current.preferred_target_text,'harga per pound AS');
  assert.ok(helpers.selectCorrections(data,'m82543').some(c=>c.id==='urn:il:v1:correction:bd448c4a-4ad8-5315-ab77-b2d79c31f22e'));
  assert.ok(html.includes('<noscript>'));
  assert.ok(html.includes('../data/rights-index.jsonl'));
  assert.ok(html.includes('../data/translation-index.jsonl'));
  for(const [,href] of html.matchAll(/href="([^"]+)"/g)) {
    if (/^https?:|^#/.test(href) || href==='../validation.json') continue;
    await access(resolve(base,'views',href));
  }
  assert.equal(/<script[^>]+src=|<link[^>]+rel="stylesheet"/.test(html),false);
  for (const module of modules) assert.ok(html.includes(module.url.replaceAll('&','&amp;')));
  for (const module of modules) assert.ok(html.includes(module.html_url));
  assert.ok(html.includes('id="module-html-reader"'));
}
console.log(JSON.stringify({result:'pass',views:4,module_filter_cases:assertions,
  additional_checks:['identity_search','ordered_multi_module_export','empty_and_unknown_selection_rejected',
    'superseded_term_replacement','whole_book_scope','segment_targeted_correction',
    'local_download_targets','self_contained_controls','non_javascript_module_routes'],
  browser_testing_claimed:false}));
