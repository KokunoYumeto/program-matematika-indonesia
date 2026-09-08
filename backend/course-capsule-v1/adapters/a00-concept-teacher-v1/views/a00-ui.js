(() => {
  'use strict';
  const get=id=>document.getElementById(id);
  const page=JSON.parse(get('a00-page-data').textContent),model=page.model,L=page.labels;
  const teacher=page.teacher,helpers=globalThis.A00ConceptControls;
  const element=(tag,text)=>{const node=document.createElement(tag);if(text!==undefined)node.textContent=text;return node;};
  const checked=name=>[...document.querySelectorAll(`input[name="${name}"]:checked`)].map(n=>n.value);
  let offset=0;
  function filterConcepts(){
    const query=get('concept-query').value.trim().toLowerCase(),role=get('concept-role').value;
    for(const concept of model.concepts){
      const card=get('concept-'+concept.key);
      card.hidden=(role!=='all'&&role!==concept.role)||
        ![...Object.values(concept.labels),...Object.values(concept.definitions),concept.key].join(' ').toLowerCase().includes(query);
    }
  }
  get('concept-query').addEventListener('input',filterConcepts);
  get('concept-role').addEventListener('change',filterConcepts);
  function revealLinkedConcept(){
    const id=decodeURIComponent(location.hash.slice(1));
    if(!id.startsWith('concept-'))return;
    const card=get(id);if(card){card.hidden=false;card.querySelector('details').open=true;}
  }
  globalThis.addEventListener('hashchange',revealLinkedConcept);revealLinkedConcept();
  if(!helpers||!Array.isArray(globalThis.A00AssessmentInventory)||globalThis.A00AssessmentInventory.length!==model.counts.assessments){
    get('results-status').textContent=L.loadFailure;return;
  }
  model.assessments=globalThis.A00AssessmentInventory;
  const selectedModules=()=>teacher?checked('module'): [get('module').value];
  const selectedConcepts=()=>teacher?checked('concept'):[];
  function render(){
    const modules=selectedModules();
    const rows=helpers.selectAssessments(model,modules,get('category').value,get('solution').value,get('assessment-query').value);
    if(offset>=rows.length)offset=0;
    get('results-status').textContent=rows.length?`${offset+1}–${Math.min(offset+40,rows.length)} / ${rows.length} · ${modules.length} ${L.modules}`:L.empty;
    const list=get('results');list.replaceChildren();
    for(const row of rows.slice(offset,offset+40)){
      const item=element('li'),module=model.modules.find(m=>m.module_id===row.module_id);
      const heading=element('strong'),moduleTitle=element('span',module.title);moduleTitle.lang='id';
      heading.append(moduleTitle,document.createTextNode(' · '+(L.categories[row.category]||row.category_label)));item.append(heading);
      const links=element('p');
      for(const [label,url] of [[L.read,row.statement_anchors[0].route_url],...[...row.solution_anchors].map(a=>[L.readSolution,a.route_url])]){
        if(links.childNodes.length)links.append(document.createTextNode(' · '));
        const link=element('a',label+' (id)');link.href=url;link.lang=page.locale;link.hreflang='id';links.append(link);
      }
      if(!row.has_explicit_solution)links.append(document.createTextNode(' · '+L.noSolution));
      item.append(links);const detail=element('details');detail.append(element('summary',L.identity));detail.append(element('code',row.module_id+'#'+row.native_id));item.append(detail);list.append(item);
    }
    get('previous').disabled=offset===0;get('next').disabled=offset+40>=rows.length;
    if(teacher){
      get('download-selection').disabled=modules.length===0;
      const keys=helpers.prerequisiteClosure(model,selectedConcepts());
      get('prerequisite-status').textContent=keys.length?L.unselectedPrerequisites+': '+keys.map(key=>model.concepts.find(c=>c.key===key).labels[page.locale]).join('; '):L.noUnselectedPrerequisites;
    }
  }
  for(const id of ['category','solution','assessment-query'])get(id).addEventListener('input',()=>{offset=0;render();});
  get('previous').addEventListener('click',()=>{offset=Math.max(0,offset-40);render();});
  get('next').addEventListener('click',()=>{offset+=40;render();});
  if(teacher){
    for(const node of document.querySelectorAll('input[name="module"],input[name="concept"]'))node.addEventListener('change',()=>{offset=0;render();});
    get('clear-modules').addEventListener('click',()=>{for(const node of document.querySelectorAll('input[name="module"]'))node.checked=false;offset=0;render();});
    get('select-concept-modules').addEventListener('click',()=>{
      const chosen=new Set(model.concepts.filter(c=>selectedConcepts().includes(c.key)).flatMap(c=>c.modules.map(m=>m.module_id)));
      for(const node of document.querySelectorAll('input[name="module"]'))if(chosen.has(node.value))node.checked=true;
      offset=0;render();
    });
    get('download-selection').addEventListener('click',()=>{
      const result=helpers.makeSelection(model,selectedModules(),selectedConcepts(),get('category').value,get('solution').value,get('assessment-query').value);
      const url=URL.createObjectURL(new Blob([JSON.stringify(result,null,2)+'\n'],{type:'application/json'}));
      const link=element('a');link.href=url;link.download='A00-concept-module-selection.json';link.click();
      setTimeout(()=>URL.revokeObjectURL(url),1000);get('export-status').textContent=L.exported;
    });
  }else get('module').addEventListener('change',()=>{offset=0;render();});
  render();get('assessment-controls').hidden=false;
})();
