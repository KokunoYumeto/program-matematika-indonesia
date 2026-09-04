import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const code=readFileSync(new URL('./geometry-capability-controls-v1.js',import.meta.url),'utf8');
function control(value=''){return {value, textContent:'',events:{},addEventListener(k,f){this.events[k]=f;}};}
const controls=Object.fromEntries(['query','chapter','kind','count','make-plan','clear-plan','plan','plan-status'].map(k=>['#'+k,control()]));
const rows=[['Aksioma','02','concept'],['Metrik','01','exercise'],['Konsep lanjutan','19','concept']].map(([title,chapter,kind],i)=>{
  const checkbox={checked:false};return {id:'native-'+i,textContent:title,hidden:false,dataset:{chapter,kind,plan:JSON.stringify({id:'native-'+i,judul:title,bacaan:'reader/#native-'+i})},querySelector:()=>checkbox,checkbox};
});
const location={hash:''},events={};
vm.runInNewContext(code,{location,addEventListener:(name,f)=>events[name]=f,document:{querySelector:s=>controls[s],querySelectorAll:()=>rows}});
assert.equal(rows.filter(x=>!x.hidden).length,3);
controls['#query'].value='AKS';controls['#query'].events.input();assert.deepEqual(rows.map(x=>x.hidden),[false,true,true]);
controls['#query'].value='';controls['#chapter'].value='01';controls['#query'].events.input();assert.deepEqual(rows.map(x=>x.hidden),[true,false,true]);
controls['#kind'].value='concept';controls['#kind'].events.input();assert.equal(rows.filter(x=>!x.hidden).length,0);
rows[0].checkbox.checked=true;rows[1].checkbox.checked=true;controls['#make-plan'].events.click();
assert.ok(controls['#plan'].value.includes('native-0'));assert.ok(controls['#plan'].value.includes('native-1'));assert.ok(!controls['#plan'].value.includes('native-2'));
assert.ok(controls['#plan-status'].textContent.includes('2 tersembunyi'));
controls['#clear-plan'].events.click();assert.ok(rows.every(r=>!r.checkbox.checked));assert.equal(controls['#plan'].value,'');
controls['#make-plan'].events.click();assert.ok(controls['#plan-status'].textContent.startsWith('0 kegiatan'));
location.hash='#native-2';events.hashchange();assert.ok(!rows[2].hidden);assert.equal(controls['#chapter'].value,'');assert.equal(controls['#kind'].value,'');
controls['#query'].value='AKS';controls['#query'].events.input();location.hash='#native-1';events.hashchange();assert.ok(!rows[1].hidden);assert.equal(controls['#query'].value,'');
location.hash='#%broken';events.hashchange();
// Read-only pages lack planner, chapter and type controls.
vm.runInNewContext(code,{document:{querySelector:()=>null,querySelectorAll:()=>[]}});
console.log(JSON.stringify({state:'pass',scenarios:11,real_shipped_script:true,browser_qa:false}));
