// Execute actual UI handlers in a small test host, not a browser or visual audit.
import assert from 'node:assert/strict';
import vm from 'node:vm';

export function testA00UI(html,controls,inventory,ui){
  class Element {
    constructor(tag='div'){this.tagName=tag;this.childNodes=[];this.listeners={};this.value='';this.checked=false;this.hidden=false;this.disabled=false;this.textContent='';}
    append(...nodes){this.childNodes.push(...nodes);}
    replaceChildren(...nodes){this.childNodes=[...nodes];}
    addEventListener(event,fn){(this.listeners[event]??=[]).push(fn);}
    fire(event){for(const callback of this.listeners[event]??[])callback({target:this});}
    click(){this.fire('click');}
    querySelector(selector){assert.equal(selector,'details');return this.detail??=new Element('details');}
  }
  const nodes=new Map([...html.matchAll(/\bid="([^"]+)"/g)].map(match=>[match[1],new Element()]));
  const encoded=html.match(/<script type="application\/json" id="a00-page-data">([\s\S]*?)<\/script>/)[1];
  nodes.get('a00-page-data').textContent=encoded;
  const page=JSON.parse(encoded),inputNodes=[];
  for(const match of html.matchAll(/<input type="checkbox" name="([^"]+)" value="([^"]+)"/g)){
    const node=new Element('input');node.name=match[1];node.value=match[2];inputNodes.push(node);
  }
  const get=id=>{assert.ok(nodes.has(id),'Unknown UI ID '+id);return nodes.get(id);};
  for(const id of ['category','solution','concept-role'])get(id).value='all';
  if(!page.teacher)get('module').value=html.match(/<option\b[^>]*\bvalue="([^"]+)" selected>/)[1];
  const globalEvents={},blobs=[];
  const context={document:{getElementById:id=>nodes.get(id),createElement:tag=>new Element(tag),createTextNode:text=>({textContent:text}),
    querySelectorAll:selector=>{
      const names=[...selector.matchAll(/input\[name="([^"]+)"\]/g)].map(match=>match[1]);
      return inputNodes.filter(node=>names.includes(node.name)&&(!selector.includes(':checked')||node.checked));
    }},location:{hash:''},addEventListener:(name,fn)=>{globalEvents[name]=fn;},
    Blob:class{constructor(parts){this.payload=parts.join('');}},URL:{createObjectURL:blob=>{blobs.push(blob.payload);return 'blob:test';},revokeObjectURL:()=>{}},setTimeout:callback=>{callback();return 1;}};
  vm.createContext(context);vm.runInContext(controls,context);vm.runInContext(inventory,context);vm.runInContext(ui,context);
  assert.equal(get('assessment-controls').hidden,false);
  const selectedModule=page.model.modules.find(row=>row.counts.explicit_solutions>0);
  if(page.teacher){
    assert.equal(get('download-selection').disabled,true);
    const checkbox=inputNodes.find(row=>row.name==='module'&&row.value===selectedModule.module_id);
    checkbox.checked=true;checkbox.fire('change');assert.equal(get('download-selection').disabled,false);
  }else{get('module').value=selectedModule.module_id;get('module').fire('change');}
  assert.ok(get('results').childNodes.length>0);
  const first=context.A00AssessmentInventory.find(row=>row.module_id===selectedModule.module_id&&row.has_explicit_solution);
  get('solution').value='with';get('solution').fire('input');
  get('assessment-query').value=first.native_id;get('assessment-query').fire('input');
  const expected=context.A00AssessmentInventory.filter(row=>row.module_id===selectedModule.module_id&&row.has_explicit_solution&&
    [row.id,row.native_id,row.module_id,row.category_label].some(value=>value.toLowerCase().includes(first.native_id.toLowerCase())));
  assert.equal(get('results').childNodes.length,Math.min(40,expected.length));
  for(const item of get('results').childNodes){
    assert.equal(item.childNodes[0].childNodes[0].lang,'id');
    for(const link of item.childNodes[1].childNodes.filter(node=>node.tagName==='a')){
      assert.equal(link.lang,page.locale);assert.equal(link.hreflang,'id');
    }
  }
  if(page.teacher){
    get('download-selection').fire('click');assert.equal(blobs.length,1);
    const exported=JSON.parse(blobs[0]);assert.equal(exported.filters.query,first.native_id);
    assert.deepEqual(exported.assessments.map(row=>row.id),Array.from(expected,row=>row.id));
    assert.equal(exported.full_text_included,false);
    get('plan-title').value='A00 <script>alert(1)</script> & plan';
    get('plan-audience').value='Independent adult learners';
    get('plan-goal').value='Review the selected source material';
    get('download-study-plan-json').fire('click');assert.equal(blobs.length,2);
    const plan=JSON.parse(blobs[1]);assert.equal(plan.schema,'pmi-source-bound-study-plan/1');
    assert.equal(plan.author_intent.audience,'Independent adult learners');
    assert.equal(plan.interface_language,page.locale);assert.equal(plan.reading_language,'id-ID');
    assert.equal(plan.author_intent_is_source_content,false);assert.equal(plan.learning_gain_estimated,false);
    assert.deepEqual(plan.selection.assessments.map(row=>row.id),exported.assessments.map(row=>row.id));
    get('download-study-plan-html').fire('click');assert.equal(blobs.length,3);
    assert.match(blobs[2],new RegExp('<html lang="'+page.locale+'">'));
    assert.ok(blobs[2].includes('&lt;script&gt;alert(1)&lt;/script&gt; &amp; plan'));
    assert.doesNotMatch(blobs[2],/<script|<iframe|<form/);
    assert.ok(blobs[2].includes(first.statement_anchors[0].route_url));
    assert.ok(blobs[2].includes(page.labels.planPortableNote));
    assert.ok(!blobs[2].includes(page.labels.portableNote),'A fixed study plan must not claim bundled selectors');
    get('clear-modules').fire('click');assert.equal(get('download-selection').disabled,true);
    assert.equal(get('download-study-plan-html').disabled,true);assert.equal(get('download-study-plan-json').disabled,true);
    const concept=inputNodes.find(row=>row.name==='concept');concept.checked=true;concept.fire('change');
    get('select-concept-modules').fire('click');
    const expectedModules=page.model.concepts.find(row=>row.key===concept.value).modules.map(row=>row.module_id);
    assert.deepEqual(inputNodes.filter(row=>row.name==='module'&&row.checked).map(row=>row.value).sort(),[...new Set(expectedModules)].sort());
  }
  get('concept-query').value='not-a-real-concept';get('concept-query').fire('input');
  assert.ok(page.model.concepts.every(c=>get('concept-'+c.key).hidden));
  const linked=page.model.concepts[0];context.location.hash='#concept-'+linked.key;globalEvents.hashchange();
  assert.equal(get('concept-'+linked.key).hidden,false);assert.equal(get('concept-'+linked.key).querySelector('details').open,true);
  return {locale:page.locale,teacher:page.teacher,actual_ui_handlers:true,selection_export:page.teacher,study_plan_exports:page.teacher,
    module_and_solution_and_query_filters:true,filtered_prerequisite_link_revealed:true,browser_used:false};
}
