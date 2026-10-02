import assert from 'node:assert/strict';

const provider='https://kokunoyumeto.github.io/methods-of-algebra-volume-2-en/';
const consumer='https://kokunoyumeto.github.io/open-mathematics-courses/courses/derived-categories-and-sheaf-operations/';
const pins=[
  ['chapter2-unit-021','definition-of-an-abelian-category',8424,'86b85ff540c9859bb8172dd218a65a945cde870880fdd734928a342d5c2870b6'],
  ['chapter2-unit-023','some-diagram-lemmas',24152,'65ce863946f2f3f4fa33f4aa088f59e6aa82ed8403e93f8939e1c269e6863a5d'],
  ['chapter3-unit-037','complexes-on-an-abelian-category',13395,'206451f9e042699e30881d1f8a0085b95e626166dd56fb638286effec90ab759'],
];
const esc=value=>String(value).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const bilingual=value=>{for(const lang of ['id','en'])assert.ok(typeof value?.[lang]==='string'&&value[lang].trim().length>0,'Missing localized review text: '+lang);};

export function validateD80PrerequisiteRoute(record){
  assert.equal(record.schema,'d80-source-bound-lesson-route/1');
  assert.equal(record.provider_course,'D80');
  assert.equal(record.consumer_course,'derived-categories-and-sheaf-operations');
  assert.equal(record.consumer_lesson,'complexes-cones-and-localization');
  assert.equal(record.relation,'writer_reported_proof_prerequisite');
  assert.equal(record.admission,'verified_public_reading_route');
  assert.equal(record.independent_mathematical_admission,false);
  assert.equal(record.whole_prerequisite_closure,false);
  assert.equal(record.distinct_course_relationships,1);
  assert.equal(record.source_report_repetitions,32);
  assert.equal(record.provider.url,provider);
  assert.equal(record.provider.sha256,'fbc3f62e83215690adb4f4909f7df05e6cc1472e5c9d7558b04611a427543a16');
  assert.equal(record.provider.bytes,4494800);
  assert.equal(record.provider.content_language,'en');
  assert.equal(record.provider.author,'Wen-Wei Li');
  assert.equal(record.provider.rights,'CC-BY-4.0');
  assert.equal(record.consumer.url,consumer+'complexes-cones-and-localization.html');
  assert.equal(record.consumer.bytes,57574);
  assert.equal(record.consumer.sha256,'d62cbe582b8510f9a4f9653813ff681a529c4f4986cce648355a5167f0341c7c');
  assert.equal(record.consumer.editable_source.url,consumer+'src/complexes-cones-and-localization.md');
  assert.equal(record.consumer.editable_source.sha256,'c54c6fe875fb64263430224ba9a2b9270db48cc4f77b92f4b1e46b00671898c2');
  assert.equal(record.consumer.editable_source.bytes,31676);
  assert.equal(record.consumer.course_complete,false);
  assert.equal(record.consumer.content_language,'en');
  assert.equal(record.consumer.rights,'GFDL-1.2-or-later; original independent passages retain CC0');
  assert.equal(record.readings.length,3);
  for(const [i,[unit,heading,bytes,sha256]] of pins.entries()){
    const row=record.readings[i];assert.equal(row.id,unit);
    assert.equal(row.anchor,unit+'--'+heading);
    assert.equal(row.url,provider+'#'+row.anchor);
    assert.equal(row.content_language,'en');assert.equal(row.rights,'CC-BY-4.0');
    assert.ok(row.title.en&&row.title.id);
    assert.equal(row.editable_source.url,'https://raw.githubusercontent.com/KokunoYumeto/methods-of-algebra-volume-2-en/main/source/en/'+unit+'.tex');
    assert.equal(row.editable_source.bytes,bytes);assert.equal(row.editable_source.sha256,sha256);
  }
  for(const key of ['public_byte_identity','public_section_anchors','consumer_use_loci_present'])assert.equal(record.verification[key],true);
  assert.equal(record.verification.producer_files_changed,false);
  assert.equal(record.provenance.model,'gpt-6-astra');assert.equal(record.provenance.effort,'ultra');
  assert.equal(record.provenance.human_review_claimed,false);
  bilingual(record.scope);
  const notice=record.reader_notice;
  assert.equal(notice.kind,'confirmed_diagram_correspondence_defect');
  assert.equal(notice.figure_id,'chapter2-unit-023-d015');
  assert.equal(notice.producer_fix_complete,false);
  bilingual(notice.label);bilingual(notice.text);
  const source='https://raw.githubusercontent.com/KokunoYumeto/methods-of-algebra-volume-2-en/674ef26c04dba544e80a95a3f320a9961649407c/';
  assert.equal(notice.pdf.url,source+'output/pdf/methods-of-algebra-volume-2-independent-english-edition.pdf#page=119');
  assert.equal(notice.pdf.bytes,3894743);
  assert.equal(notice.pdf.sha256,'8193d44ef52c9c39807e769ad04507130f163481f82aa9cfaa0a1a3022ef7aa5');
  assert.equal(notice.tex_url,source+'source/en/chapter2-unit-023.tex');
  assert.deepEqual(notice.evidence,{path:'backend/cross-programme-v1/d80-diagram-notice-evidence-v1.json',bytes:3171,sha256:'5d3e3f84ed46b09f19987ddec91b1c3c782e12dd92dc9325b096958073c553d2'});
  assert.equal(record.use_loci.length,2);
  assert.deepEqual(record.use_loci.map(r=>r.consumer_locus),['Lemma 1.2, entire proof','Lemma 2.4, final paragraph']);
  assert.deepEqual(record.use_loci.map(r=>r.provider_labels),[
    ['prop:Abel-cat-pull-push','prop:Abel-cat-exact-aux','prop:snake-lemma','prop:long-exact-sequence-ses'],
    ['prop:5-lemma'],
  ]);
  for(const row of record.use_loci){bilingual(row.label);bilingual(row.conditions);bilingual(row.comparison);}
  bilingual(record.verification.mathematical_review);bilingual(record.change_policy);bilingual(record.provenance.scope);
  return record;
}

export function renderD80PrerequisiteRoute(record,locale,side){
  validateD80PrerequisiteRoute(record);assert.ok(['id','en'].includes(locale));
  assert.ok(['provider','consumer'].includes(side));
  const id=locale==='id';
  const label=id?'Bacaan prasyarat untuk pelajaran ini':'Prerequisite readings for this lesson';
  const disclaimer=id?'Tautan dan edisi sumber telah diperiksa. Ini bukan pengesahan bahwa seluruh pembuktian prasyarat atau mata kuliah telah selesai.':'Links and source editions have been checked. This does not certify that all prerequisite proofs or the course are complete.';
  const readings='<ol>'+record.readings.map(r=>'<li><a href="'+esc(r.url)+'" hreflang="en">'+esc(r.title[locale])+'</a> — English</li>').join('')+'</ol>';
  const target='<a href="'+esc(record.consumer.url)+'" hreflang="en">'+esc(record.consumer.title[locale])+'</a>';
  const counterpart=side==='provider'?'advanced-'+record.consumer_course:'core-D80';
  const within='<p><a data-d80-programme-step="'+side+'" href="#'+esc(counterpart)+'">'+(side==='provider'?(id?'Lihat mata kuliah lanjutan dalam program':'See the further course in the programme'):(id?'Kembali ke fondasi aljabar dalam program':'Return to the algebra foundation in the programme'))+'</a></p>';
  const notes='<details data-d80-use-notes><summary>'+(id?'Catatan penggunaan sumber dan pembuktian':'Source and proof-use notes')+'</summary><ol>'+record.use_loci.map(r=>'<li><strong>'+esc(r.label[locale])+'</strong><p>'+esc(r.conditions[locale])+'</p><p>'+esc(r.comparison[locale])+'</p></li>').join('')+'</ol><p>'+esc(record.verification.mathematical_review[locale])+'</p><p>'+esc(record.change_policy[locale])+'</p></details>';
  const notice=record.reader_notice;
  const warning='<p data-d80-reader-notice><strong>'+esc(notice.label[locale])+'.</strong> '+esc(notice.text[locale])+' <a href="'+esc(notice.pdf.url)+'" hreflang="en">'+(id?'Diagram yang benar — PDF, halaman 119':'Correct diagram — PDF, page 119')+'</a> · <a href="'+esc(notice.tex_url)+'" hreflang="en">'+(id?'Sumber LaTeX':'LaTeX source')+'</a> — English.</p>';
  return '<aside data-d80-prerequisite="'+side+'"><h4>'+(side==='provider'?(id?'Persiapan untuk pelajaran lanjutan':'What this prepares you for'):label)+'</h4><p>'+target+' — English</p>'+readings+within+'<p>'+esc(record.scope[locale])+'</p>'+warning+'<p>'+esc(disclaimer)+'</p>'+notes+'<p>'+(id?'Sumber: ':'Source: ')+'Wen-Wei Li, <i>Methods of Algebra, Volume 2</i>, CC BY 4.0. '+(id?'Integrasi jalur: OpenAI Codex gpt-6-astra, upaya Ultra.':'Route integration: OpenAI Codex gpt-6-astra, Ultra effort.')+'</p></aside>';
}
