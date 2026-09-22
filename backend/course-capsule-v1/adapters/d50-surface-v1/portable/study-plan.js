/* D50 portable consumer. No network calls, persistence, tracking, or new answers. */
(() => {
  'use strict';
  const filter=(map,q='',kind='',group='',concept='')=>{
    q=q.trim().toLocaleLowerCase();
    return map.units.filter(u=>(!kind||(kind==='practice'?u.practice:u.kind===kind))&&(!group||u.group===group)&&
      (!concept||u.concept_ids.includes(concept))&&(!q||[u.id,u.title,u.source_record.source_local_id].join(' ').toLocaleLowerCase().includes(q)));
  };
  const plan=(map,selected,language)=>{
    if(!['id','en'].includes(language))throw new Error('Unknown interface language');
    const ids=new Set(selected),byId=new Map(map.units.map(u=>[u.id,u]));
    for(const id of ids)if(!byId.has(id))throw new Error('Unknown selectable unit: '+id);
    const units=map.units.filter(u=>ids.has(u.id)),supportIds=new Set(units.flatMap(u=>u.support.map(r=>r.from)));
    return {schema:'d50-portable-study-plan/1',course_id:'D50',interface_locale:language,content_locale:'id-ID',
      units,supporting_units:map.units.filter(u=>supportIds.has(u.id)),
      semantic_exam_groups:map.semantic_exam_groups.filter(g=>g.occurrence_ids.some(id=>ids.has(id))),
      placeholder_slots_count:map.placeholder_slots.length,placeholder_slots_are_exercises:false,
      prerequisites:map.prerequisites,concept_relations:map.concept_relations,rights:map.rights,
      source_witness:map.source_witness,reader:map.reader,reader_archive:map.reader_archive,
      hosted_reader_url:map.hosted_reader_url??null,
      limitations:map.limitations[language],new_solutions_generated:false,full_reader_in_this_json:false};
  };
  globalThis.D50_PLAN_API={filter,plan};
  if(typeof document==='undefined')return;
  const map=globalThis.D50_DATA;if(!map)return;
  const lang=document.body.dataset.language,en=lang==='en',t=(a,b)=>en?b:a,$=id=>document.getElementById(id);
  const el=(tag,text)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;return e;};
  const kinds={lecture_worksheet_pair:['Unit kuliah dan lembar kerja','Lecture and worksheet unit'],lecture:['Kuliah','Lecture'],worksheet:['Lembar kerja','Worksheet'],
    exercise:['Latihan','Exercise'],solution:['Solusi sumber','Source solution'],source_supplied_solution:['Solusi sumber','Source solution'],
    official_exam_bank:['Bank ujian','Exam bank'],official_exam_form:['Formulir ujian','Exam form'],official_exam_learner_form:['Soal dalam formulir ujian','Exam learner form'],
    official_exam_solution_form:['Solusi sumber dalam formulir ujian','Exam source-solution form'],exam_problem_occurrence:['Kemunculan soal ujian','Exam problem occurrence'],
    source_supplied_exam_solution:['Solusi ujian dari sumber','Source exam solution'],original_exam_solution_repair:['Solusi ujian tambahan asli','Original additional exam solution'],
    separately_provenanced_original_exam_solution_repairs:['Kumpulan solusi ujian tambahan asli','Original additional exam solution collection'],
    original_cc_by_sa_bridge:['Modul jembatan asli','Original bridge module'],original_bridge_assessment:['Latihan modul jembatan','Bridge assessment'],
    original_bridge_theory:['Teori modul jembatan','Bridge theory'],original_bridge_exercise:['Latihan jembatan dengan solusi asli','Bridge exercise with original solution'],
    original_bridge_mastery_problem:['Soal penguasaan dengan solusi asli','Mastery problem with original solution'],
    lecture_section:['Bagian kuliah','Lecture section'],worksheet_section:['Bagian lembar kerja','Worksheet section'],
    original_bridge_reader_anchor:['Bagian modul jembatan','Bridge section'],source_supplied_hint:['Petunjuk sumber','Source hint']};
  const label=k=>kinds[k]?.[en?1:0]??k;
  const title=u=>u.title||label(u.kind)+' · '+(u.kind==='lecture_worksheet_pair'?u.order:u.source_record.source_display_id??u.source_record.source_local_id??u.id);
  if(document.body.dataset.mode==='teacher'){
    document.querySelector('nav:not([data-central-surface-navigation]) a[href="index.html"]').href='teacher.html';
    document.querySelector('nav:not([data-central-surface-navigation]) a[href="index.en.html"]').href='teacher.en.html';
  }
  const byId=new Map(map.units.map(u=>[u.id,u])),chosen=new Set();let page=0,shown=[];const size=30;
  const option=(id,value,text)=>{const e=el('option',text);e.value=value;$(id).append(e);};
  option('kind','',t('Semua jenis','All kinds'));option('kind','practice',t('Semua soal latihan','All practice problems'));
  for(const k of [...new Set(map.units.map(u=>u.kind))].sort())option('kind',k,label(k));
  option('group','',t('Semua kelompok','All groups'));
  for(const id of [...new Set(map.units.map(u=>u.group))])option('group',id,title(byId.get(id)));
  option('concept','',t('Semua konsep','All concepts'));
  for(const c of map.concepts)option('concept',c.id,c.labels['id-ID']+' · '+c.id);
  $('kind').value=document.body.dataset.mode==='teacher'?'practice':'lecture_worksheet_pair';
  const link=u=>{const a=el('a',title(u));a.href=u.route.portable_href;a.lang='id';return a;};
  const selection=()=>{$('selection').textContent=chosen.size+t(' unit dipilih',' units selected');$('export').disabled=!chosen.size;};
  function render(){
    shown=filter(map,$('search').value,$('kind').value,$('group').value,$('concept').value);
    page=Math.min(page,Math.max(0,Math.ceil(shown.length/size)-1));$('items').replaceChildren();
    for(const u of shown.slice(page*size,(page+1)*size)){
      const card=el('article'),h=el('h3'),box=el('input');box.type='checkbox';box.checked=chosen.has(u.id);box.setAttribute('aria-label',t('Pilih ','Select ')+title(u));
      box.addEventListener('change',()=>{box.checked?chosen.add(u.id):chosen.delete(u.id);selection();});h.append(box,link(u));card.append(h,el('small',u.id));
      if(u.route.state.startsWith('enclosing_'))card.append(el('p',t('Tautan membuka bagian induk; unit ini tidak memiliki jangkar tersendiri.','This link opens the enclosing section; this unit has no separate anchor.')));
      if(u.support.length){const d=el('details');d.append(el('summary',t('Lihat bahan pendukung','Show support')));const list=el('ul');
        for(const r of u.support){const tag=r.type==='annotates'?t('Petunjuk sumber','Source hint'):r.provenance==='original_not_source_supplied'?t('Solusi tambahan asli — bukan solusi sumber','Original additional solution — not supplied by the source'):t('Solusi sumber','Source solution');
          const li=el('li',tag+': ');li.append(link(byId.get(r.from)));list.append(li);}d.append(list);card.append(d);
      }else if(u.practice&&!u.inline_original_solution)card.append(el('p',t('Solusi sumber tidak tercatat; alat ini tidak membuat jawaban baru.','No source solution is recorded; this tool does not generate an answer.')));
      if(u.inline_original_solution)card.append(el('p',t('Petunjuk dan solusi asli berada dalam bacaan yang sama; membuka bacaan dapat menampilkan jawaban.','Original hints and solutions are in the same reading; opening it may expose the answer.')));
      const detail=el('details');detail.append(el('summary',t('Identitas dan asal sumber','Identity and provenance')),el('p',t('Lisensi komponen: ','Component rights: ')+u.rights_ids.join(', ')),el('p',t('SHA-256 bacaan: ','Reader SHA-256: ')+u.route.reader.sha256),el('pre',JSON.stringify(u.source_record,null,2)));card.append(detail);$('items').append(card);
    }
    $('results').textContent=shown.length?`${page*size+1}–${Math.min((page+1)*size,shown.length)} / ${shown.length}`:t('Tidak ada hasil.','No results.');
    $('previous').disabled=page===0;$('next').disabled=(page+1)*size>=shown.length;$('select-page').disabled=!shown.length;selection();
  }
  for(const id of ['search','kind','group','concept'])$(id).addEventListener(id==='search'?'input':'change',()=>{page=0;render();});
  $('previous').addEventListener('click',()=>{page--;render();});$('next').addEventListener('click',()=>{page++;render();});
  $('select-page').addEventListener('click',()=>{shown.slice(page*size,(page+1)*size).forEach(u=>chosen.add(u.id));render();});
  $('clear').addEventListener('click',()=>{chosen.clear();render();});
  $('export').addEventListener('click',()=>{const b=new Blob([JSON.stringify(plan(map,chosen,lang),null,2)+'\n'],{type:'application/json'}),url=URL.createObjectURL(b),a=el('a');a.href=url;a.download='D50-plan.json';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);});
  $('controls').hidden=false;render();
})();
