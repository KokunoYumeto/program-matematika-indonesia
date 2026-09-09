/* Pure selection/export logic; shared by the static browser UI and Node tests. */
(() => {
  'use strict';
  const esc=x=>String(x).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
  function select(model,sectionIds,filters={}) {
    if(!Array.isArray(sectionIds)||new Set(sectionIds).size!==sectionIds.length||sectionIds.some(id=>!model.sections.some(s=>s.id===id)))throw Error('B10-INVALID-SECTIONS');
    if(Object.keys(filters).some(k=>!['hint','answer','solution','query'].includes(k)))throw Error('B10-INVALID-FILTER');
    for(const k of ['hint','answer','solution'])if(!['all','with','without'].includes(filters[k]??'all'))throw Error('B10-INVALID-FILTER');
    if(typeof(filters.query??'')!=='string')throw Error('B10-INVALID-QUERY');
    const query=(filters.query??'').trim().toLowerCase(),ids=new Set(sectionIds);
    return model.exercises.filter(e=>ids.has(e.section_id)&&['hint','answer','solution'].every(k=>(filters[k]??'all')==='all'||(e.support[k].length>0)===(filters[k]==='with'))&&(!query||[e.id,e.native_id,e.source_xpath].some(v=>v.toLowerCase().includes(query))));
  }
  function plan(model,sectionIds,exerciseIds,filters={},intent={},locale='id') {
    if(!['id','en'].includes(locale))throw Error('B10-INVALID-LOCALE');
    if(!sectionIds.length)throw Error('B10-EMPTY-PLAN');
    const allowed=new Set(select(model,sectionIds,filters).map(e=>e.id));
    if(!Array.isArray(exerciseIds)||!exerciseIds.length||new Set(exerciseIds).size!==exerciseIds.length||exerciseIds.some(id=>!allowed.has(id)))throw Error('B10-INVALID-EXERCISES');
    const fields=['title','audience','goal','period','study','feedback'];
    if(!intent||typeof intent!=='object'||Array.isArray(intent)||Object.keys(intent).some(k=>!fields.includes(k)))throw Error('B10-INVALID-INTENT');
    const author_intent={};
    for(const key of fields){const value=intent[key]??'';if(typeof value!=='string'||value.length>2000)throw Error('B10-INVALID-INTENT');author_intent[key]=value.trim();}
    const chosen=new Set(exerciseIds);
    return {schema:'b10-source-bound-study-plan/1',course_id:'B10',interface_language:locale,reading_language:'en',
      source_revision:model.source_revision,source_identities:model.source_identities,author_intent,author_intent_is_source_content:false,
      sections:model.sections.filter(s=>sectionIds.includes(s.id)),exercises:model.exercises.filter(e=>chosen.has(e.id)),filters,
      rights:model.rights,indonesian_course:model.indonesian_course,reading_order:'source_book_order',
      conceptual_prerequisites_inferred:false,mastery_inferred:false,learning_gain_estimated:false,
      delivery:{plan_works_offline:true,textbook_bodies_included:false,reading_requires_network_or_separate_reader:true,
        selectors_included:false,server_submission:false,persistent_learner_tracking:false}};
  }
  function renderPlan(p,L) {
    if(p.schema!=='b10-source-bound-study-plan/1'||!['en','id'].includes(p.interface_language))throw Error('B10-INVALID-PLAN');
    const link=(url,label)=>{if(typeof url!=='string'||!/^https:\/\/[^\s<>"']+$/.test(url))throw Error('B10-UNSAFE-LINK');return `<a href="${esc(url)}" hreflang="en">${esc(label)}</a>`;};
    const sections=p.sections.map(s=>`<section><h2>${esc(s.titles[p.interface_language])}</h2><p>${link(s.routes[0].url,L.readSection)}</p><ol>${p.exercises.filter(e=>e.section_id===s.id).map(e=>`<li>${link(e.routes[0].url,e.native_id)}${e.route_granularity==='containing_source_unit'?` — ${esc(L.containing)}`:''}<ul>${['hint','answer','solution'].map(k=>`<li>${esc(L[k])}: ${e.support[k].length?e.support[k].map(r=>link(r.routes[0].url,r.native_id)+(r.route_granularity==='containing_source_unit'?` (${esc(L.containing)})`:'')).join('; '):esc(L.absent)}</li>`).join('')}</ul></li>`).join('')}</ol></section>`).join('');
    return `<!doctype html><html lang="${p.interface_language}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none';style-src 'unsafe-inline';base-uri 'none';form-action 'none'"><title>${esc(p.author_intent.title||L.plan)}</title><style>body{max-width:70rem;margin:2rem auto;padding:0 1rem;font:1rem/1.6 system-ui;color:#142d36}a{color:#075b78}li{margin:.6rem 0;overflow-wrap:anywhere}dd{white-space:pre-wrap;margin:0 0 1rem}dt{font-weight:bold}section{border-top:1px solid #bdd0d9}</style></head><body><main><h1>${esc(p.author_intent.title||L.plan)}</h1><p>${esc(L.boundary)}</p><p>${esc(L.planOffline)}</p><dl>${Object.entries(L.fields).map(([k,v])=>`<dt>${esc(v)}</dt><dd>${esc(p.author_intent[k]||'—')}</dd>`).join('')}</dl>${sections}<h2>${esc(L.provenance)}</h2><p>Oscar Levin · Discrete Mathematics: An Open Introduction, 4th Edition</p><p><code>${esc(p.source_revision)}</code></p><ul>${p.rights.map(r=>`<li>${esc(r.attribution)}: ${esc(r.license_expression)}</li>`).join('')}</ul></main></body></html>\n`;
  }
  globalThis.B10Selection=Object.freeze({select,plan,renderPlan});
})();
