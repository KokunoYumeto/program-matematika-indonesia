/* Native quoted metadata; rendering uses textContent, never record HTML. */
(() => {
  'use strict';
  const filter = (rows,kind,search='',unit='',flag='') => {
    const query=search.trim().toLocaleLowerCase();
    const exactId=query && rows.some(row=>row.kind===kind && row.id.toLocaleLowerCase()===query);
    return rows.filter(row=>row.kind===kind && (!unit || row.unit_ids.includes(unit)) &&
      (!flag || row.flags.includes(flag)) && (!query || (exactId?row.id.toLocaleLowerCase()===query:JSON.stringify(row).toLocaleLowerCase().includes(query))));
  };
  globalThis.D80_NATIVE_LEDGER_API={filter};
  if(typeof document==='undefined') return;
  const data=globalThis.D80_NATIVE_LEDGER, en=document.body.dataset.locale==='en';
  const t=(id,english)=>en?english:id, $=id=>document.getElementById(id);
  const labels={unit_slice:t('Lokasi sumber tingkat unit, bukan rentang per segmen.','Unit-level source location, not an exact segment span.'),
    exact_source_span:t('Rentang sumber eksak menurut catatan asli.','Exact source span according to the native ledger.'),
    provisional:t('Istilah sementara.','Provisional term.'),term_disagreement:t('Daftar istilah dan kontrol memilih istilah berbeda; keduanya dipertahankan.','Term and control ledgers disagree; both choices are preserved.'),
    reader_override:t('Pembaca menggunakan deskripsi pengganti; catatan diagram asli tetap tersedia.','The reader uses a replacement description; the original diagram record is preserved.'),
    canon_not_independently_checked:t('Belum diperiksa terhadap kanon secara independen.','Not independently checked against the canon.'),
    observed_not_modified_pending_consolidated_review:t('Diamati, belum diterapkan.','Observed, not applied.'),
    accepted_disclosed:t('Diterima dan dijelaskan dalam catatan asli.','Accepted and disclosed in the native record.'),
    accepted_recorded:t('Diterima dan dicatat; bukan pengesahan baru.','Accepted and recorded; not new certification.'),
    unmapped_unit:t('Tidak ada pemetaan unit eksak; lihat lokasi asli.','No exact unit join; inspect the original locator.')};
  const controls=['kind','search','unit','flag'];let page=0;
  const initial=new URLSearchParams(location.search);
  for(const name of controls) if(initial.has(name)) $(name).value=initial.get(name);
  if(!$("kind").value) $("kind").value='terms';
  function element(tag,text,className){const node=document.createElement(tag);if(text!==undefined)node.textContent=text;if(className)node.className=className;return node;}
  function render(){
    const chosen=filter(data.rows,$('kind').value,$('search').value,$('unit').value.trim(),$('flag').value);
    page=Math.min(page,Math.max(0,Math.ceil(chosen.length/25)-1));
    const start=page*25, root=$('records');root.replaceChildren();
    for(const row of chosen.slice(start,start+25)){
      const card=element('article',undefined,'record');card.dataset.recordId=row.id;
      const title=row.kind==='terms'?row.native.preferred_id:row.kind==='diagrams'?(row.related_native.reader_override?.description_id || row.native.alt_text_id):row.id;
      card.append(element('h2',title),element('p',row.id,'metadata'));
      for(const flag of row.flags)card.append(element('p',labels[flag] || flag,'notice'));
      if(row.kind==='terms'){
        const c=row.related_native.terminology_control;
        card.append(element('p',t('Padanan Inggris: ','English correspondence: ')+c.english),
          element('p',t('Pilihan pada kontrol: ','Control-ledger choice: ')+c.o013_o014_preferred_id),
          element('p',t('Lokasi pengenalan pertama yang dicatat: ','Recorded first introduction: ')+(c.first_o014_unit || t('belum dicatat','not recorded'))),
          element('p',row.unit_links.length?t('Tautan berikut menunjukkan pengenalan pertama yang dicatat, bukan semua kemunculan.','The following link marks the recorded first introduction, not all occurrences.'):
            t('Lokasi ini tidak cocok dengan ID unit eksak; tidak ada tautan unit yang ditebak.','This locator does not match an exact unit ID; no unit link has been guessed.')));
        if(c.variants)card.append(element('p',t('Varian yang dicatat: ','Recorded variants: ')+c.variants));
      } else if(row.kind==='segments'){
        const r=row.native;
        card.append(element('p',t('Sumber: ','Source: ')+r.source_path+' · '+t('baris ','lines ')+r.source_start_line+'–'+r.source_end_line));
        if(r.target_path)card.append(element('p',t('Terjemahan: ','Translation: ')+r.target_path+' · '+t('baris ','lines ')+r.target_start_line+'–'+r.target_end_line));
        if(r.target_anchor)card.append(element('p',t('Penanda asli: ','Native anchor: ')+r.target_anchor));
      } else if(row.kind==='corrections'){
        const r=row.native;
        card.append(element('h3',t('Pernyataan sumber (kutipan)','Source statement (quotation)')),element('pre',r.source_claim),
          element('h3',t('Pernyataan terjemahan (kutipan)','Target statement (quotation)')),element('pre',r.target_claim),
          element('p',t('Sumber: ','Source: ')+r.source_path+' · '+r.source_line),
          element('p',t('Terjemahan: ','Translation: ')+r.target_path+' · '+r.target_lines));
      } else if(row.kind==='diagrams' && row.related_native.reader_override){
        card.append(element('h3',t('Deskripsi asli yang tetap dipertahankan','Preserved original description')),element('p',row.native.alt_text_id));
      }
      for(const route of row.unit_links){
        const a=element('a',t('Baca unit: ','Read unit: ')+route.title);a.href=route.url;a.rel='noopener';card.append(a);
      }
      for(const [caption,value] of [[t('Catatan asli (kutipan; bahasa sumber dipertahankan)','Original record (quotation; source language retained)'),row.native],
        [t('Kontrol/deskripsi terkait (kutipan asli)','Related control/description (original quotation)'),row.related_native]]){
        if(!Object.keys(value).length)continue;
        const details=element('details');details.append(element('summary',caption),element('pre',JSON.stringify(value,null,2)));card.append(details);
      }
      root.append(card);
    }
    if(!chosen.length)root.append(element('p',t('Tidak ada catatan yang cocok.','No matching records.')));
    $('count').textContent=(chosen.length?start+1:0)+'–'+Math.min(start+25,chosen.length)+' / '+chosen.length;
    $('previous').disabled=page===0;$('next').disabled=start+25>=chosen.length;
    const params=new URLSearchParams();for(const name of controls)if($(name).value)params.set(name,$(name).value);
    history.replaceState(null,'',location.pathname+'?'+params.toString());
    $('language').href=(en?'ledger.html':'ledger-en.html')+'?'+params.toString();
  }
  for(const name of controls)$(name).addEventListener(name==='search'||name==='unit'?'input':'change',()=>{page=0;render();});
  $('previous').addEventListener('click',()=>{page--;render();});$('next').addEventListener('click',()=>{page++;render();});render();
})();
