import assert from 'node:assert/strict';
import vm from 'node:vm';
export function testUI(html,modelJS,controls,ui){
 class Element{constructor(tag='div'){this.tagName=tag;this.children=[];this.listeners={};this.value='';this.checked=false;this.disabled=false;this.textContent='';}append(...n){this.children.push(...n);}replaceChildren(...n){this.children=[...n];}setAttribute(k,v){this[k]=v;}addEventListener(k,f){this.listeners[k]=f;}fire(k){this.listeners[k]?.({target:this});}click(){this.fire('click');}}
 const nodes=new Map([...html.matchAll(/\bid="([^"]+)"/g)].map(m=>[m[1],new Element()]));
 const inputs=[...html.matchAll(/<input type="checkbox" name="section" value="([^"]+)"( checked)?>/g)].map(m=>{const e=new Element('input');e.value=m[1];e.checked=!!m[2];return e;});
 const data=html.match(/id="b10-page-data">([\s\S]*?)<\/script>/)[1];nodes.get('b10-page-data').textContent=data;
 for(const k of ['hint','answer','solution'])nodes.get(k).value='all';const blobs=[];
 const ctx={document:{getElementById:id=>nodes.get(id),createElement:t=>new Element(t),querySelectorAll:s=>{assert.match(s,/^input\[name="section"\](:checked)?$/);return s.endsWith(':checked')?inputs.filter(x=>x.checked):inputs;}},Blob:class{constructor(parts){this.payload=parts.join('');}},URL:{createObjectURL:b=>{blobs.push(b.payload);return 'blob:test';},revokeObjectURL:()=>{}},setTimeout:fn=>fn()};
 vm.createContext(ctx);for(const code of [modelJS,controls,ui])vm.runInContext(code,ctx);
 const model=ctx.B10Model,page=JSON.parse(data),get=id=>nodes.get(id);
 assert.equal(get('download-json').disabled,true);assert.equal(get('results').children.length,Math.min(30,model.exercises.filter(e=>e.section_id===inputs[0].value).length));
 inputs.forEach(e=>e.checked=true);inputs[0].fire('change');get('select-all').click();assert.equal(get('download-json').disabled,false);
 get('download-json').click();assert.equal(JSON.parse(blobs.at(-1)).exercises.length,768);
 const firstPageID=get('results').children[0].children[0].value;get('next').click();assert.notEqual(get('results').children[0].children[0].value,firstPageID);
 get('previous').click();assert.equal(get('results').children[0].children[0].value,firstPageID);
 get('solution').value='with';get('solution').fire('input');get('download-json').click();assert.equal(JSON.parse(blobs.at(-1)).exercises.length,337);
 get('clear').click();assert.equal(get('download-json').disabled,true);
 const chosen=model.exercises.find(e=>e.support.solution.length&&e.support.answer.length);assert.ok(chosen);
 get('query').value=chosen.id;get('query').fire('input');const checkbox=get('results').children[0].children[0];checkbox.checked=true;checkbox.fire('change');
 get('intent-title').value='<script>alert(1)</script> & study';get('intent-audience').value='Independent learners';get('download-json').click();
 const plan=JSON.parse(blobs.at(-1));assert.equal(plan.exercises.length,1);assert.equal(plan.exercises[0].id,chosen.id);assert.equal(plan.reading_language,'en');assert.equal(plan.interface_language,page.locale);
 get('download-html').click();assert.ok(blobs.at(-1).includes('&lt;script&gt;alert(1)&lt;/script&gt; &amp; study'));assert.doesNotMatch(blobs.at(-1),/<script|<form|<iframe/);
 assert.ok(blobs.at(-1).includes(chosen.routes[0].url));assert.ok(blobs.at(-1).includes(page.labels.planOffline));
 for(const row of get('results').children)for(const child of row.children)if(child?.tagName==='a')assert.equal(child.hreflang,'en');
 get('query').value='no-exercise-with-this-id';get('query').fire('input');assert.equal(get('download-json').disabled,true);assert.equal(get('results').children[0].textContent,page.labels.empty);
 return {locale:page.locale,teacher:page.teacher,actual_handlers:true,all_exercises_export:768,solution_filter:337,individual_selection:true,pagination:true,empty_state:true,html_escaping:true,browser_used:false};
}
