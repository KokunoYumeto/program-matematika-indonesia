/* Native records are data: never interpolate them as HTML. */
'use strict';
const data=globalThis.D20_LEDGER,en=document.body.dataset.locale==='en';
const t=(id,english)=>en?english:id;
const byId=id=>document.getElementById(id);
const controls={kind:byId('kind'),search:byId('search'),chapter:byId('chapter')};
let page=0;
function element(tag,text,className){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(className)e.className=className;return e;}
for(const chapter of data.chapters){const o=element('option',chapter.id+' · '+(en?chapter.title_en:chapter.title_id));o.value=chapter.id;controls.chapter.append(o);}
const initial=new URLSearchParams(location.hash.slice(1));
for(const [key,control] of Object.entries(controls))if(initial.has(key))control.value=initial.get(key);
if(!controls.kind.value)controls.kind.value='terminology';
function render(){
  const needle=controls.search.value.toLocaleLowerCase();
  const rows=data.rows.filter(r=>r.kind===controls.kind.value&&(!controls.chapter.value||r.chapter_ids.includes(controls.chapter.value))&&(!needle||JSON.stringify(r.native).toLocaleLowerCase().includes(needle)));
  const last=Math.max(0,Math.ceil(rows.length/20)-1);page=Math.min(page,last);
  const state=new URLSearchParams(Object.entries(controls).map(([key,c])=>[key,c.value]).filter(([,v])=>v));
  history.replaceState(null,'','#'+state);byId('language').hash=state.toString();
  byId('count').textContent=t(`${rows.length} catatan · halaman ${page+1} dari ${last+1}`,`${rows.length} records · page ${page+1} of ${last+1}`);
  const cards=rows.slice(page*20,page*20+20).map(row=>{
    const article=element('article',undefined,'record'),n=row.native;
    article.append(element('h2',row.kind==='terminology'?n.source_term+' → '+n.preferred:row.id));
    article.append(element('p',row.id,'metadata'));
    if(row.kind==='terminology'){
      article.append(element('p',t('Istilah pilihan bahasa Indonesia: ','Preferred Indonesian term: ')+n.preferred));
      article.append(element('p',t('Varian yang dicatat: ','Recorded variants: ')+(n.variants?.join('; ')||t('Tidak dicatat','Not recorded'))));
      article.append(element('p',t('Alternatif yang ditolak: ','Rejected alternatives: ')+(n.rejected?.join('; ')||t('Tidak dicatat','Not recorded'))));
      article.append(element('p',t('Bukti asli (kutipan): ','Original evidence (quoted): ')+(n.evidence||t('Tidak dicatat','Not recorded'))));
    }
    if(row.kind==='segments'){
      for(const side of ['source','target']){
        const label=side==='source'?t('Sumber bahasa Inggris','English source'):t('Terjemahan bahasa Indonesia','Indonesian translation');
        article.append(element('p',`${label}: ${n[side+'_path']} · ${n[side+'_line_start']}–${n[side+'_line_end']}`,'metadata'));
        article.append(element('p',t('Fragmen cocok dengan identitas yang dicatat.','Fragment matches the recorded identity.')));
      }
    }
    if(row.kind==='corrections')article.append(element('p',t('Ringkasan asli (kutipan): ','Original summary (quoted): ')+(n.summary||'')));
    for(const route of row.reader_routes){const a=element('a',t('Buka bab berbahasa Indonesia','Open Indonesian chapter'));a.href=route.url;a.hreflang='id';const p=element('p');p.append(a);article.append(p);}
    const details=element('details'),summary=element('summary',t('Catatan asli lengkap dan bukti','Complete original record and evidence'));
    details.append(summary,element('pre',JSON.stringify({native:n,fragment_check:row.fragment_check},null,2)));article.append(details);
    return article;
  });
  byId('records').replaceChildren(...cards);
  if(!rows.length)byId('records').append(element('p',t('Tidak ada catatan yang sesuai.','No matching records.')));
  byId('previous').disabled=page===0;byId('next').disabled=page>=last;
}
for(const control of Object.values(controls))control.addEventListener('input',()=>{page=0;render();});
byId('previous').addEventListener('click',()=>{page--;render();});
byId('next').addEventListener('click',()=>{page++;render();});
render();
