/* Pure selection helpers are also executed by the non-browser validation suite. */
(() => {
  'use strict';
  function selectExercises(data, moduleId, availability, query) {
    const text = query.trim().toLowerCase();
    return data.exercises.filter(row => row.module_id === moduleId &&
      (availability === 'all' || Boolean(row.solution_id) === (availability === 'provided')) &&
      (!text || [row.id, row.source_element_id, row.problem_id, row.solution_id].some(value =>
        value && value.toLowerCase().includes(text))));
  }
  function makeSelection(data, moduleIds) {
    const wanted = new Set(moduleIds);
    const modules = data.modules.filter(row => wanted.has(row.module_id));
    if (!modules.length || modules.length !== wanted.size) throw new Error('A10-INVALID-SELECTION');
    return {schema:'pmi-course-selection/1', course_id:'A10', edition_id:data.edition_id,
      native_release_sha256:data.native_release_sha256, source_pdf_sha256:data.pdf_sha256,
      selection_is_full_text:false, selection_is_a_new_curriculum_claim:false,
      modules:modules.map(row => ({module_id:row.module_id, module_unit_id:row.module_unit_id,
        translated_source_sha256:row.sha256, reader_url:row.url, route_scope:row.route_scope})),
      exercises:data.exercises.filter(row => wanted.has(row.module_id)).map(row => ({
        exercise_id:row.id, problem_id:row.problem_id, solution_id:row.solution_id,
        solution_status:row.solution_status, source_module_id:row.module_id,
        source_element_id:row.source_element_id, ordinal_within_module:row.ordinal_within_module,
        ordinal_is_printed_exercise_number:false})),
      limitations:['Metadata selection only; native mathematical text remains in the pinned edition.',
        'PDF links open modules, not verified individual exercise or solution destinations.']};
  }
  function selectTerms(data,moduleId,query) {
    const text=query.trim().toLowerCase();
    return data.terms.filter(row=>(row.scope==='whole_book' || !row.module_id || row.module_id===moduleId) &&
      (!text || [row.source_text,row.preferred_target_text,row.ledger_id].some(s=>s&&s.toLowerCase().includes(text))));
  }
  function selectCorrections(data,moduleId) {
    return data.corrections.filter(row=>row.module_id===moduleId);
  }
  globalThis.A10Selection = Object.freeze({selectExercises, makeSelection, selectTerms, selectCorrections});
  if (typeof document === 'undefined') return;
  const data = JSON.parse(document.getElementById('a10-data').textContent);
  const labels = data.labels;
  const moduleControl = document.getElementById('module');
  const statusControl = document.getElementById('availability');
  const queryControl = document.getElementById('query');
  const pageSize = 40;
  let offset = 0;
  const number = value => value.toLocaleString(data.locale);
  function element(tag, text, className) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  }
  function render() {
    const module = data.modules.find(row => row.module_id === moduleControl.value);
    const rows = selectExercises(data,module.module_id,statusControl.value,queryControl.value);
    if (offset >= rows.length) offset = 0;
    const list = document.getElementById('exercises'); list.replaceChildren();
    document.getElementById('module-reader').href = module.url;
    document.getElementById('module-summary').textContent = `${module.display_title} · ${labels.page} ${module.physical_page} · ${number(module.exercise_count)} ${labels.exercises} · ${number(module.solution_count)} ${labels.provided}`;
    document.getElementById('result-count').textContent = rows.length ?
      `${number(offset+1)}–${number(Math.min(offset+pageSize,rows.length))} / ${number(rows.length)}` : labels.empty;
    for (const row of rows.slice(offset,offset+pageSize)) {
      const item = element('li');
      item.append(element('strong',`${labels.sourceOrder} ${row.ordinal_within_module}`));
      item.append(element('span',row.solution_id ? labels.provided : labels.notProvided,'badge'));
      const detail = element('details'); detail.append(element('summary',labels.identities));
      const fields = [[labels.exercise,row.id],[labels.problem,row.problem_id],[labels.solution,row.solution_id || labels.notProvided],[labels.source,row.module_id+'#'+row.source_element_id]];
      for (const [key,value] of fields) {const p=element('p',key+': ');p.append(element('code',value));detail.append(p);}
      item.append(detail); list.append(item);
    }
    document.getElementById('previous').disabled = offset === 0;
    document.getElementById('next').disabled = offset+pageSize >= rows.length;
    renderGovernance(module.module_id);
  }
  function renderGovernance(moduleId) {
    const termList = document.getElementById('terms');
    if (!termList) return;
    const query = document.getElementById('term-query').value.trim().toLowerCase();
    const terms = selectTerms(data,moduleId,query);
    termList.replaceChildren();
    document.getElementById('term-count').textContent = `${number(Math.min(40,terms.length))} / ${number(terms.length)} · ${labels.refine}`;
    for (const row of terms.slice(0,40)) {
      const item=element('li');
      item.append(element('strong',row.preferred_target_text || row.source_text));
      item.append(element('span',row.evidence_kind==='curated_designation' ? labels.curated : labels.occurrence,'badge'));
      if (row.superseded_by.length) {
        for (const id of row.superseded_by) {
          const replacement=data.terms.find(t=>t.id===id);
          item.append(element('p',`${labels.superseded}: ${replacement.ledger_id} · ${replacement.preferred_target_text}`,'warning'));
        }
      }
      if (row.preferred_target_text) item.append(element('p',`${row.source_text} → ${row.preferred_target_text}`));
      item.append(element('code',row.ledger_id || row.id)); termList.append(item);
    }
    const corrections=selectCorrections(data,moduleId);
    document.getElementById('correction-count').textContent=number(corrections.length);
    const correctionList=document.getElementById('corrections'); correctionList.replaceChildren();
    for (const row of corrections) {
      const item=element('li');item.append(element('strong',row.ledger_id || labels.mapOnly));
      item.append(element('p',labels.correctionState+': '+row.status));
      item.append(element('code',row.source_locator || row.affected_source_id || row.target_id));
      correctionList.append(item);
    }
  }
  for (const control of [moduleControl,statusControl,queryControl]) control.addEventListener('input',()=>{offset=0;render();});
  document.getElementById('previous').addEventListener('click',()=>{offset=Math.max(0,offset-pageSize);render();});
  document.getElementById('next').addEventListener('click',()=>{offset+=pageSize;render();});
  document.getElementById('term-query')?.addEventListener('input',render);
  document.getElementById('download-selection')?.addEventListener('click',()=>{
    const selected=[...document.querySelectorAll('input[name="selected-module"]:checked')].map(n=>n.value);
    const notice=document.getElementById('selection-status');
    if (!selected.length) {notice.textContent=labels.selectFirst;return;}
    const result=makeSelection(data,selected);
    const url=URL.createObjectURL(new Blob([JSON.stringify(result,null,2)+'\n'],{type:'application/json'}));
    const link=element('a');link.href=url;link.download='A10-module-selection.json';link.click();
    setTimeout(()=>URL.revokeObjectURL(url),1000);notice.textContent=labels.selectionReady;
  });
  const requested=new URLSearchParams(location.search).get('module');
  if (data.modules.some(row=>row.module_id===requested)) moduleControl.value=requested;
  render();
})();
