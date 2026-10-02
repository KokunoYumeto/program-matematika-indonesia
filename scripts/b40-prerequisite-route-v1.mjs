import assert from 'node:assert/strict';
import {validateHermitianRoute} from './finite-hermitian-route-v1.mjs';

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

export function currentRequirementDisposition(finding,route,evidence){
  const basis=route.schema==='b40-source-bound-proof-route/1';
  (basis?validateB40PrerequisiteRoute:validateHermitianRoute)(route);
  assert.equal(finding.id,'RT-FIN-01.'+(basis?'basis-extension':'hermitian-orthogonal-decomposition'));
  assert.equal(finding.downstream?.source_sha256??finding.downstream_source_sha256,route.consumer_source_sha256);
  assert.equal(evidence.consumer.sha256,route.consumer_source_sha256);
  assert.equal(evidence.source.sha256,route.source_sha256);
  assert.equal(evidence.reader_manifest.path,route.reader_manifest);
  for(const item of Object.values(evidence)){
    assert.match(item.sha256,/^[0-9a-f]{64}$/);assert.ok(item.bytes>0);
    assert.ok(!item.path.startsWith('/')&&!item.path.split('/').includes('..'));
  }
  return {
    id:finding.id,status:'proof_supplied_author_self_review',
    historical_finding_id:finding.id,
    required_statement:finding.required_statement,required_conditions:finding.required_conditions,
    consumer:{course:route.consumer_course,lesson:route.consumer_lesson,
      revision:route.consumer_revision,source:evidence.consumer,uses:route.uses},
    provider:{course:route.provider_course,source:evidence.source,
      route:evidence.route,reader_manifest:evidence.reader_manifest,
      reader_url:route.reader_url,content_language:route.content_language,
      proof_anchors:basis?[route.proof_anchor]:route.uses.map(use=>use.proof_anchor)},
    author_review:evidence.author_review,
    independent_review:false,whole_prerequisite_closure:false,native_catalogue_admission_changed:false,
    historical_issue_disposition:basis?'printed_sign_preserved_and_corrected_in_bridge':'matching_complex_linear_first_proof_supplied',
    scope:route.scope,limits:route.limits,provenance:route.provenance,
  };
}

export function renderCurrentRequirements(rows,locale){
  assert.ok(['en','id'].includes(locale));assert.equal(rows.length,2);
  const id=locale==='id';
  return '<aside data-current-proof-requirements="RT-FIN"><h4>'+
    (id?'Status pembuktian prasyarat saat ini':'Current prerequisite-proof status')+'</h4><p>'+
    (id?'Dua prasyarat tersedia untuk empat penggunaan yang dicatat. Materi penghubung diperiksa sendiri oleh AI penulis, bukan melalui pemeriksaan independen. Prasyarat lain masih diperiksa.':'Two prerequisites are supplied for four recorded uses. The proof bridges have author-instance AI self-review, not independent review. Other prerequisites remain under audit.')+
    '</p><ul>'+rows.map((row,i)=>'<li><a href="'+esc(row.provider.reader_url+'#'+row.provider.proof_anchors[0])+'" hreflang="en">'+
      (i===0?(id?'Perluasan basis dan proyeksi':'Basis extension and projection'):(id?'Basis ortonormal dan dekomposisi ortogonal':'Orthonormal bases and orthogonal decomposition'))+
      '</a> — English</li>').join('')+'</ul><p>'+
    (id?'Temuan terdahulu dipertahankan sebagai catatan historis, bukan status pembuktian saat ini.':'Earlier findings are retained as historical evidence, not the current proof status.')+'</p></aside>';
}
