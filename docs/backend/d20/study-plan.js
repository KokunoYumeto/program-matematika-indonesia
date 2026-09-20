/* Shared native-metadata consumer. Local selection only: no fetch or storage. */
(() => {
  'use strict';
  const filterUnits=(map,query='',kind='',group='',concept='')=>{
    const q=query.trim().toLocaleLowerCase();
    return map.units.filter(u=>(!kind||(kind==='practice'?u.practice:u.kind===kind))&&(!group||u.group===group)&&
      (!concept||u.chapter_concept_ids.includes(concept))&&(!q||[u.id,u.title,u.title_en,u.number,...u.chapter_concept_ids].join(' ').toLocaleLowerCase().includes(q)));
  };
  const makePlan=(map,selection,locale)=>{
    if (!['id','en'].includes(locale)) throw new Error('Unknown interface locale');
    const chosen=new Set(selection), byId=new Map(map.units.map(u=>[u.id,u]));
    for(const id of chosen) if(!byId.has(id)) throw new Error('Unknown unit: '+id);
    const units=map.units.filter(u=>chosen.has(u.id)), support=new Set(units.flatMap(u=>u.support.map(r=>r.from)));
    return {schema:'native-study-plan/1',course_id:map.course_id,identity_namespace:map.identity_namespace,interface_locale:locale,content_locale:map.locale,
      units,supporting_units:map.units.filter(u=>support.has(u.id)),source_witness:map.source_witness,inputs:map.inputs,
      rights:map.rights,component_prerequisites:map.component_prerequisites,chapter_concept_links:map.chapter_concept_links,
      concept_prerequisites:map.concept_prerequisites,unresolved_external_course_relations:map.unresolved_external_course_relations,
      limitations:map.limitations,selected_order:'native_group_and_native_order',offline_book_included:false,answers_generated:false};
  };
  globalThis.COURSE_PLAN_API={filterUnits,makePlan};
  if(typeof document==='undefined') return;
  const map=globalThis.COURSE_PLAN_DATA; if(!map)return;
  const en=document.body.dataset.interface==='en',locale=en?'en':'id',t=(a,b)=>en?b:a,get=id=>document.getElementById(id);
  const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
  const byId=new Map(map.units.map(u=>[u.id,u])),selected=new Set(),size=40;
  const kinds={chapter:['Bab','Chapter'],preface:['Prakata','Preface'],section:['Bagian','Section'],exer:['Latihan','Exercise'],
    prop:['Proposisi','Proposition'],defn:['Definisi','Definition'],exam:['Contoh','Example'],proof:['Bukti','Proof'],
    cor:['Korolari','Corollary'],thm:['Teorema','Theorem'],lem:['Lema','Lemma'],original_solution:['Solusi pendamping','Companion solution']};
  const kindLabel=k=>kinds[k]?.[en?1:0]??k.replaceAll('_',' ');
  const title=u=>u.title||`${kindLabel(u.kind)} ${u.number||u.id}`;
  let page=0,current=[];
  const option=(select,value,text)=>{const o=el('option',text);o.value=value;get(select).append(o);};
  for(const k of [...new Set(map.units.map(u=>u.kind))].sort())option('kind',k,kindLabel(k));
  for(const id of [...new Set(map.units.map(u=>u.group))])option('group',id,byId.has(id)?title(byId.get(id)):map.components.find(c=>c.id===id)?.title??id);
  for(const c of map.concepts)option('concept',c.id,en?c.label_en:c.label_id_ID);
  get('kind').value=document.body.dataset.mode==='teacher'?'practice':'chapter';
  const selection=()=>{get('selection').textContent=selected.size+t(' unit dipilih',' units selected');get('export').disabled=get('export-text').disabled=!selected.size;};
  const link=u=>{const a=el('a',title(u));a.href=u.route.url;a.lang='id';return a;};
  const supportLabels={hints:['Petunjuk sumber','Source hint'],proves:['Bukti sumber','Source proof'],solves:['Solusi pendamping','Companion solution'],completes_source_proof:['Bukti pendamping','Companion proof']};
  function render(){
    current=filterUnits(map,get('search').value,get('kind').value,get('group').value,get('concept').value);
    page=Math.min(page,Math.max(0,Math.ceil(current.length/size)-1));get('unit-list').replaceChildren();
    for(const u of current.slice(page*size,(page+1)*size)){
      const card=el('article',undefined,'unit'),h=el('h3'),checkbox=el('input');checkbox.type='checkbox';checkbox.checked=selected.has(u.id);checkbox.setAttribute('aria-label',t('Pilih ','Select ')+title(u));
      checkbox.addEventListener('change',()=>{checkbox.checked?selected.add(u.id):selected.delete(u.id);selection();});h.append(checkbox,link(u));card.append(h,el('p',kindLabel(u.kind)+' · '+u.id,'metadata'));
      if(u.support.length){const d=el('details');d.append(el('summary',t('Buka tautan bahan pendukung','Show support links')));const list=el('ul');
        for(const r of u.support){const li=el('li',supportLabels[r.type]?.[en?1:0]+': ');li.append(link(byId.get(r.from)));list.append(li);}d.append(list);card.append(d);
      }else if(u.practice)card.append(el('p',t('Relasi bahan pendukung tidak tercatat. Cakupan tidak diketahui.','No support relation recorded. Coverage is unknown.'),'metadata'));
      if(u.exercise_support)card.append(el('p',t('Solusi pendamping: diterima; catatan antrean lama tetap disimpan.','Companion solution: admitted; the historical queued record is retained.'),'metadata'));
      const provenance=el('details');provenance.append(el('summary',t('Identitas dan sumber','Identity and source')),el('p',u.rights_ids.join(' · '),'metadata'),el('p','Reader SHA-256: '+u.route.page.sha256,'metadata'));
      const source=el('pre',JSON.stringify(u.source_record,null,2),'metadata');provenance.append(source);card.append(provenance);get('unit-list').append(card);
    }
    get('results-status').textContent=current.length?`${page*size+1}–${Math.min((page+1)*size,current.length)} / ${current.length}`:t('Tidak ada hasil.','No results.');
    get('previous').disabled=page===0;get('next').disabled=(page+1)*size>=current.length;get('select-page').disabled=!current.length;selection();
  }
  const download=(text,name,type)=>{const url=URL.createObjectURL(new Blob([text],{type})),a=el('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);};
  for(const id of ['search','kind','group','concept'])get(id).addEventListener(id==='search'?'input':'change',()=>{page=0;render();});
  get('previous').addEventListener('click',()=>{page--;render();});get('next').addEventListener('click',()=>{page++;render();});
  get('select-page').addEventListener('click',()=>{current.slice(page*size,(page+1)*size).forEach(u=>selected.add(u.id));render();});
  get('clear').addEventListener('click',()=>{selected.clear();render();});
  get('export').addEventListener('click',()=>download(JSON.stringify(makePlan(map,selected,locale),null,2)+'\n',map.course_id+'-plan.json','application/json'));
  get('export-text').addEventListener('click',()=>{
    const plan=makePlan(map,selected,locale),lines=[map.course_id+t(' · Rencana belajar',' · Study plan'),t('Bahasa bacaan: Indonesia','Reading language: Indonesian'),'Source lock SHA-256: '+map.source_witness.sha256,''];
    for(const u of plan.units){lines.push(title(u),u.id,u.route.url,'Reader SHA-256: '+u.route.page.sha256,'Rights: '+u.rights_ids.join(', '));for(const r of u.support)lines.push(r.type+': '+r.from+' '+byId.get(r.from).route.url);lines.push('');}
    lines.push(...plan.limitations);download(lines.join('\n')+'\n',map.course_id+'-plan.txt','text/plain;charset=utf-8');
  });
  get('workbench').hidden=false;render();
})();
