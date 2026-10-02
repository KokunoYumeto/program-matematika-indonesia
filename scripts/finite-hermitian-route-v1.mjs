import assert from 'node:assert/strict';
const escape=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
export function validateHermitianRoute(row,manifest){
  assert.equal(row.schema,'finite-hermitian-proof-route/1');
  assert.equal(row.provider_course,'B40');assert.equal(row.consumer_course,'RT-FIN');
  assert.equal(row.consumer_lesson,'representations-and-complete-reducibility');
  assert.equal(row.consumer_revision,'801f186833b9811fa826575ef0717e78a5047ab0');
  assert.equal(row.consumer_source_sha256,'659942bdf47420e6665d59c4e80cf973867730d3b231d7e9c80ab8177bd83712');
  assert.equal(row.reader_manifest,'docs/en/readers/finite-hermitian-spaces/READER_MANIFEST.json');
  assert.equal(row.reader_url,'https://kokunoyumeto.github.io/program-matematika-indonesia/en/readers/finite-hermitian-spaces/');
  assert.equal(row.source_sha256,'a8547e894bab4c4eb862086af6fc078519945e11aa9976ba823bde94cbef551c');
  assert.equal(row.content_language,'en');assert.equal(row.rights,'CC-BY-SA-4.0');
  assert.equal(row.proof_review,'author-instance self-review');
  for(const key of ['independent_mathematical_admission','whole_prerequisite_closure','native_catalogue_admission_changed'])assert.equal(row[key],false);
  assert.deepEqual(row.uses,[{consumer_locus:'Proposition 2.1',proof_anchor:'gramschmidt-with-the-coefficients-in-the-correct-order'},{consumer_locus:'Orthogonal splitting following Proposition 2.1',proof_anchor:'orthogonal-projection-and-decomposition'}]);
  for(const key of ['scope','limits'])for(const locale of ['en','id'])assert.ok(row[key]?.[locale]?.length>100);
  if(manifest){
    assert.equal(manifest.schema,'finite-hermitian-reader/1');assert.equal(manifest.source_sha256,row.source_sha256);
    assert.equal(manifest.formula_count,144);assert.equal(manifest.mathml_formula_identity,true);assert.equal(manifest.direct_latex_formula_identity,true);
    assert.equal(manifest.independent_review,false);assert.equal(manifest.whole_course_verified,false);
  }
  return row;
}
export function renderHermitianRoute(row,locale,side){
  validateHermitianRoute(row);assert.ok(['en','id'].includes(locale));assert.ok(['provider','consumer'].includes(side));
  const id=locale==='id', other=side==='provider'?'advanced-RT-FIN':'core-B40';
  const labels=id?['Basis ortonormal — Proposisi 2.1','Dekomposisi ortogonal — sesudah Proposisi 2.1']:['Orthonormal basis — Proposition 2.1','Orthogonal decomposition — after Proposition 2.1'];
  return '<aside data-hermitian-prerequisite="'+side+'"><h4>'+(id?'Basis ortonormal dan proyeksi ortogonal':'Orthonormal bases and orthogonal projections')+'</h4><p>'+escape(row.scope[locale])+'</p><ol>'+row.uses.map((use,i)=>'<li><a href="'+escape(row.reader_url+'#'+use.proof_anchor)+'" hreflang="en">'+labels[i]+'</a> — English</li>').join('')+'</ol><p>'+escape(row.limits[locale])+'</p><p><a href="#'+other+'">'+(side==='provider'?(id?'Lihat mata kuliah teori representasi':'See the representation-theory course'):(id?'Kembali ke fondasi aljabar linear':'Return to the linear-algebra foundation'))+'</a></p><p>'+(id?'Dikembangkan dari pernyataan John M. Erdman; pembuktian dan integrasi oleh OpenAI Codex GPT-6 Astra, upaya Ultra.':'Develops statements from John M. Erdman; proofs and integration by OpenAI Codex GPT-6 Astra, Ultra effort.')+' CC BY-SA 4.0.</p></aside>';
}
