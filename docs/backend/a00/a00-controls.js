/* Pure helpers run in Node tests and the browser; no network or stored learner data. */
(() => {
  'use strict';
  function prerequisiteClosure(model, keys) {
    const selected=new Set(keys), required=new Set(), byKey=new Map(model.concepts.map(row=>[row.key,row]));
    function visit(key,visiting=new Set()) {
      if(!byKey.has(key)||visiting.has(key))throw new Error('A00-INVALID-CONCEPT-GRAPH');
      const next=new Set(visiting).add(key);
      for(const parent of byKey.get(key).prerequisite_keys){if(!required.has(parent)){visit(parent,next);required.add(parent);}}
    }
    for(const key of selected)visit(key);
    return model.concepts.filter(row=>required.has(row.key)&&!selected.has(row.key)).map(row=>row.key);
  }
  function selectAssessments(model,moduleIds,category='all',solution='all',query='') {
    const wanted=new Set(moduleIds),text=query.trim().toLowerCase();
    if(!['all','with','without'].includes(solution))throw new Error('A00-INVALID-SOLUTION-FILTER');
    if(category!=='all'&&!Object.hasOwn(model.category_labels,category))throw new Error('A00-INVALID-CATEGORY');
    if([...wanted].some(id=>!model.modules.some(row=>row.module_id===id)))throw new Error('A00-INVALID-MODULE');
    return model.assessments.filter(row=>wanted.has(row.module_id)&&
      (category==='all'||row.category===category)&&
      (solution==='all'||row.has_explicit_solution===(solution==='with'))&&
      (!text||[row.id,row.native_id,row.module_id,row.category_label].some(value=>value.toLowerCase().includes(text))));
  }
  function makeSelection(model,moduleIds,conceptKeys,category='all',solution='all',query='') {
    if(!moduleIds.length||new Set(moduleIds).size!==moduleIds.length||new Set(conceptKeys).size!==conceptKeys.length)
      throw new Error('A00-EMPTY-OR-DUPLICATE-SELECTION');
    const prerequisites=prerequisiteClosure(model,conceptKeys),wanted=new Set(moduleIds);
    const selectedConcepts=model.concepts.filter(row=>conceptKeys.includes(row.key));
    const rows=selectAssessments(model,moduleIds,category,solution,query);
    const evidenceModules=new Set(selectedConcepts.flatMap(row=>row.modules.map(m=>m.module_id)));
    return {schema:'pmi-concept-module-selection/1',course_id:'A00',sources:model.sources,
      reading_language:model.reading_language,source_revision:model.source_revision,
      modules:model.modules.filter(row=>wanted.has(row.module_id)).map(row=>({module_id:row.module_id,
        unit_id:row.unit_id,edition_id:row.edition_id,rights_id:row.rights_id,module_url:row.module_url})),
      selected_concepts:selectedConcepts.map(row=>({id:row.id,key:row.key,role:row.role})),
      unselected_prerequisite_concepts:prerequisites,
      selected_concept_evidence_modules_not_in_selection:[...evidenceModules].filter(id=>!wanted.has(id)).sort(),
      filters:{category,solution,query:query.trim()},assessment_scope:'module_inventory_not_exercise_to_concept_alignment',
      assessments:rows.map(row=>({id:row.id,native_id:row.native_id,module_id:row.module_id,
        category:row.category,route_url:row.route_url,statement_anchors:row.statement_anchors,
        solution_anchors:row.solution_anchors,solution_gap_id:row.solution_gap_id})),
      full_text_included:false,learning_outcome_validated:false,prerequisite_mastery_inferred:false};
  }
  function makeStudyPlan(model,moduleIds,conceptKeys,filters={},author={},locale='id') {
    if(!['id','en'].includes(locale))throw new Error('A00-INVALID-PLAN-LANGUAGE');
    const fields=['title','audience','goal','period','study','feedback'];
    if(!author||typeof author!=='object'||Array.isArray(author)||Object.keys(author).some(key=>!fields.includes(key)))
      throw new Error('A00-INVALID-PLAN-FIELDS');
    const intent={};
    for(const key of fields){
      const value=author[key]??'';
      if(typeof value!=='string'||value.length>2000)throw new Error('A00-INVALID-PLAN-TEXT');
      intent[key]=value.trim();
    }
    const selection=makeSelection(model,moduleIds,conceptKeys,filters.category??'all',filters.solution??'all',filters.query??'');
    const chosen=new Set(conceptKeys),missing=new Set(selection.unselected_prerequisite_concepts);
    const concepts=rows=>rows.map(c=>({id:c.id,key:c.key,labels:c.labels,definitions:c.definitions,
      source_objective_ids:[...c.objective_unit_ids],objective_ids_are_not_localized_ordinals:true,
      source_modules:c.modules.map(m=>({module_id:m.module_id,source_objective_numbers:m.objective_numbers,module_url:m.module_url}))}));
    return {schema:'pmi-source-bound-study-plan/1',course_id:'A00',interface_language:locale,
      reading_language:model.reading_language,author_intent:intent,
      author_intent_is_source_content:false,unfilled_author_fields:fields.filter(key=>!intent[key]),
      selected_source_concepts:concepts(model.concepts.filter(c=>chosen.has(c.key))),
      prerequisite_source_concepts:concepts(model.concepts.filter(c=>missing.has(c.key))),
      reading_order:'native_book_order_not_individualized_recommendation',
      readings:model.modules.filter(m=>moduleIds.includes(m.module_id)).map(m=>({module_id:m.module_id,title:m.title,
        ordinal:m.ordinal,module_url:m.module_url,unit_id:m.unit_id,rights_id:m.rights_id})),
      comparator:{kind:'existing_source_book',source_revision:model.source_revision,sources:model.sources},
      delivery:{plan_works_offline:true,textbook_bodies_included:false,linked_reading_requires_network_or_separate_book:true,
        server_submission:false,persistent_learner_tracking:false},
      learning_gain_estimated:false,learner_population_estimated:false,selection};
  }
  function renderStudyPlan(plan,L) {
    const esc=value=>String(value).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
    const link=(url,label)=>{
      if(typeof url!=='string'||!/^https:\/\/[^\s<>"']+$/.test(url))throw new Error('A00-INVALID-PLAN-LINK');
      return `<a href="${esc(url)}" hreflang="id">${esc(label)}</a>`;
    };
    const locale=plan.interface_language;
    if(!['id','en'].includes(locale)||plan.schema!=='pmi-source-bound-study-plan/1')throw new Error('A00-INVALID-PLAN');
    const title=plan.author_intent.title||L.planTitle;
    const notes=Object.entries(L.planFields).map(([key,label])=>`<dt>${esc(label)}</dt><dd>${esc(plan.author_intent[key]||'—')}</dd>`).join('');
    const concepts=rows=>`<ul>${rows.map(c=>`<li><strong>${esc(c.labels[locale])}</strong><p>${esc(c.definitions[locale])}</p><details><summary>${esc(L.identity)}</summary><code>${esc(c.id)}</code><ul>${c.source_objective_ids.map(id=>`<li><code>${esc(id)}</code></li>`).join('')}</ul></details></li>`).join('')}</ul>`;
    const byModule=new Map(plan.readings.map(m=>[m.module_id,[]]));
    for(const row of plan.selection.assessments){
      if(!byModule.has(row.module_id))throw new Error('A00-UNMAPPED-PLAN-ASSESSMENT');
      byModule.get(row.module_id).push(row);
    }
    const readings=plan.readings.map(m=>`<section><h3 lang="id">${m.ordinal}. ${link(m.module_url,m.title)}</h3><ol>${byModule.get(m.module_id).map(row=>`<li>${link(row.statement_anchors[0].route_url,L.read+' · '+row.native_id)} · ${row.solution_anchors.length?row.solution_anchors.map(a=>link(a.route_url,L.readSolution)).join(' · '):esc(L.noSolution)}</li>`).join('')}</ol></section>`).join('');
    const missingModules=plan.selection.selected_concept_evidence_modules_not_in_selection;
    return `<!doctype html><html lang="${locale}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'"><title>${esc(title)}</title><style>body{max-width:70rem;margin:2rem auto;padding:0 1rem;font:1rem/1.6 system-ui,sans-serif;color:#142d36}a{color:#075b78}dt{font-weight:bold}dd{margin:0 0 1rem;white-space:pre-wrap;overflow-wrap:anywhere}li{margin:.5rem 0}code{overflow-wrap:anywhere}section{border-top:1px solid #bdd0d9;margin:1.5rem 0}details{margin:.5rem 0}</style></head><body><main><h1>${esc(title)}</h1><p>${esc(L.planNote)}</p><dl>${notes}</dl><h2>${esc(L.conceptHeading)}</h2>${concepts(plan.selected_source_concepts)}<h2>${esc(L.unselectedPrerequisites)}</h2>${plan.prerequisite_source_concepts.length?concepts(plan.prerequisite_source_concepts):`<p>${esc(L.noUnselectedPrerequisites)}</p>`}${missingModules.length?`<p>${esc(L.planMissingModules)}: ${missingModules.map(esc).join(', ')}</p>`:''}<h2>${esc(L.readings)}</h2><p>${esc(L.planOrder)}</p>${readings}<section><h2>${esc(L.provenance)}</h2><p>${esc(L.sourceNote)}</p><p>${esc(L.boundary)}</p><p>${esc(L.planPortableNote)}</p><p>OpenStax · Prealgebra 2e · <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</a></p><p><code>${esc(plan.comparator.source_revision)}</code></p></section></main></body></html>\n`;
  }
  globalThis.A00ConceptControls=Object.freeze({prerequisiteClosure,selectAssessments,makeSelection,makeStudyPlan,renderStudyPlan});
})();
