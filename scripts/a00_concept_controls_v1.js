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
  globalThis.A00ConceptControls=Object.freeze({prerequisiteClosure,selectAssessments,makeSelection});
})();
