import assert from 'node:assert/strict';

const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
export function validateB40PrerequisiteRoute(row,manifest){
  assert.equal(row.schema,'b40-source-bound-proof-route/1');
  assert.equal(row.provider_course,'B40');assert.equal(row.consumer_course,'RT-FIN');
  assert.equal(row.consumer_lesson,'representations-and-complete-reducibility');
  assert.equal(row.source_revision,'r2');
  assert.equal(row.source_sha256,'131f01c7611a96c60a0dfdaf08c7b17e0f1a864dd371968ecd858b19f4e49652');
  assert.equal(row.consumer_source_sha256,'659942bdf47420e6665d59c4e80cf973867730d3b231d7e9c80ab8177bd83712');
  assert.equal(row.consumer_reader_sha256,'fc0fe3b74413f9e6179c5a11761cd81cb1a07e2cef1b26d635957af63780b31c');
  assert.equal(row.reader_url,'https://kokunoyumeto.github.io/program-matematika-indonesia/en/readers/basis-projection-bridge/');
  assert.equal(row.reader_manifest,'docs/en/readers/basis-projection-bridge/READER_MANIFEST.json');
  assert.equal(row.proof_anchor,'extending-a-basis-and-choosing-a-complement');
  assert.equal(row.consumer_url,'https://kokunoyumeto.github.io/open-mathematics-courses/courses/RT-FIN/representations-and-complete-reducibility.html');
  assert.equal(row.content_language,'en');assert.equal(row.rights,'CC-BY-SA-2.5');
  for(const key of ['independent_mathematical_admission','whole_prerequisite_closure','hermitian_dependency_closed','native_catalogue_admission_changed'])assert.equal(row[key],false);
  assert.deepEqual(row.uses,[{locus:'Theorem 2.3',anchor:'2-averaging-separates-invariant-pieces'},{locus:'Exercise 5',anchor:'exercise-5-hard-an-isotypic-projection'}]);
  for(const key of ['scope','limits','editorial_note'])for(const locale of ['en','id'])assert.ok(row[key]?.[locale]?.length>80);
  if(manifest){
    assert.equal(manifest.schema,'b40-basis-projection-reader/1');
    assert.equal(manifest.source_sha256,row.source_sha256);
    assert.equal(manifest.formula_count,167);
    assert.equal(manifest.html_mathml_source_tex_exact,true);assert.equal(manifest.direct_latex_formula_replay_exact,true);
    assert.equal(manifest.whole_course_verified,false);assert.equal(manifest.hermitian_dependency_closed,false);
  }
  return row;
}

export function renderB40PrerequisiteRoute(row,locale,side){
  validateB40PrerequisiteRoute(row);
  assert.ok(['en','id'].includes(locale));assert.ok(['provider','consumer'].includes(side));
  const id=locale==='id', other=side==='provider'?'advanced-RT-FIN':'core-B40';
  const title=id?'Dari basis ke proyeksi — prasyarat khusus':'From bases to projections — exact prerequisite';
  const uses=row.uses.map(use=>'<li><a href="'+esc(row.consumer_url+'#'+use.anchor)+'" hreflang="en">'+esc(id?use.locus.replace('Theorem','Teorema').replace('Exercise','Latihan'):use.locus)+'</a> — English</li>').join('');
  return '<aside data-b40-prerequisite="'+side+'"><h4>'+title+'</h4><p><a href="'+esc(row.reader_url+'#'+row.proof_anchor)+'" hreflang="en">'+(id?'Baca pembuktian lengkap':'Read the complete proof')+'</a> — English</p><p>'+esc(row.scope[locale])+'</p><ol>'+uses+'</ol><p>'+esc(row.editorial_note[locale])+'</p><p>'+esc(row.limits[locale])+'</p><p><a data-b40-programme-step="'+side+'" href="#'+other+'">'+(side==='provider'?(id?'Lihat mata kuliah teori representasi':'See the representation-theory course'):(id?'Kembali ke fondasi aljabar linear':'Return to the linear-algebra foundation'))+'</a></p><p>'+(id?'Adaptasi dari Jim Hefferon; integrasi oleh OpenAI Codex GPT-6 Astra, upaya Ultra.':'Adapted from Jim Hefferon; integration by OpenAI Codex GPT-6 Astra, Ultra effort.')+' CC BY-SA 2.5.</p></aside>';
}
