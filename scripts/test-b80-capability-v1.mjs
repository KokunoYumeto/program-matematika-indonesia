import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';
import { exportCatalog,importCatalog,json,line } from './native-catalog-exchange-v1.mjs';

const source={version:'1',empty:[],items:[{id:'a',math:'\\frac{x}{y} + α',absent:null,number:-0},{id:'b',math:'x²',array:[2,1]}]};
const exported=exportCatalog(source,'fixture');
assert.deepEqual(importCatalog(exported.shape,exported.records,'fixture'),source);
assert.deepEqual(importCatalog(JSON.parse(json(exported.shape)),exported.records.map(row=>JSON.parse(line(row))),'fixture'),source);
assert.ok(Object.is(JSON.parse(json(source)).items[0].number,-0));
const rejected=[];
for(const [name,mutate] of [
  ['removed_record',rows=>rows.pop()],
  ['duplicate_record',rows=>rows.push(structuredClone(rows[0]))],
  ['wrong_dataset',rows=>{rows[0].dataset='wrong';}],
  ['changed_native_id',rows=>{rows.find(row=>row.native_id).native_id='different';}],
  ['unmapped_table',rows=>{rows[0].table='unknown';}],
  ['duplicate_native_id',rows=>{const items=rows.filter(row=>row.table==='items');items[1].payload.id=items[0].payload.id;items[1].native_id=items[0].native_id;}],
]){
  const rows=structuredClone(exported.records);mutate(rows);
  assert.throws(()=>importCatalog(exported.shape,rows,'fixture'),undefined,name);rejected.push(name);
}
assert.throws(()=>exportCatalog({items:[{id:'same'},{id:'same'}]},'fixture'));
assert.equal(json(importCatalog(exported.shape,exported.records,'fixture')),json(source));

const page=await readFile(new URL('../docs/backend/b80/B80.html',import.meta.url),'utf8');
const resource=JSON.parse(await readFile(new URL('../docs/backend/b80/learning-map.json',import.meta.url),'utf8'));
const script=page.match(/<script>([\s\S]*?)<\/script>/)[1];
const controls=Object.fromEntries(['query','unit','kind','count'].map(id=>[id,{value:'',textContent:'',addEventListener(){}}]));
const rows=resource.units.flatMap(unit=>unit.exercises.map(ex=>({dataset:{unit:unit.id,kind:ex.kind},
  textContent:unit.title+' '+ex.title,hidden:false})));
const sandbox={document:{querySelector:selector=>controls[selector.slice(1)],querySelectorAll:()=>rows}};
vm.runInNewContext(script,sandbox);
assert.equal(rows.filter(row=>!row.hidden).length,75);
controls.unit.value=resource.units[0].id;vm.runInNewContext('update()',sandbox);
assert.equal(rows.filter(row=>!row.hidden).length,resource.units[0].exercises.length);
controls.unit.value='';controls.kind.value='mastery';vm.runInNewContext('update()',sandbox);
assert.equal(rows.filter(row=>!row.hidden).length,resource.units.flatMap(unit=>unit.exercises).filter(ex=>ex.kind==='mastery').length);
controls.kind.value='';controls.query.value='NOT A REAL EXERCISE XYZ';vm.runInNewContext('update()',sandbox);
assert.equal(rows.filter(row=>!row.hidden).length,0);
assert.match(controls.count.textContent,/^0 dari 75/);
controls.query.value='';vm.runInNewContext('update()',sandbox);assert.equal(rows.filter(row=>!row.hidden).length,75);
console.log(JSON.stringify({state:'pass',rejected_exchange_mutations:rejected,ui_filter_cases:5}));
