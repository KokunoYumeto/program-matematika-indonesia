import assert from 'node:assert/strict';
import { mkdir,readFile,writeFile } from 'node:fs/promises';
import { dirname,resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { json,sha256 } from './native-catalog-exchange-v1.mjs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const sources={
  capsules:'backend/course-capsule-v1/generated/course-capsules.json',
  families:'backend/course-capsule-v1/authority/clp-family-v231/modular-backend-pattern-index-v2.1.json',
  published:'backend/course-capsule-v1/authority/clp-family-v231/v23-adapter-index-v2.json',
  b80:'backend/course-capsule-v1/adapters/b80-capability-v1/publication/GITHUB_SOURCE_AND_PAGES_READBACK_20260904.json',
  lebl:'backend/course-capsule-v1/adapters/lebl-capability-v1/publication/GITHUB_READBACK_97960cc12b34.json',
  geometry:'backend/course-capsule-v1/adapters/geometry-capability-v1/publication/GITHUB_READBACK_a2584b9448c9.json',
  topology:'backend/course-capsule-v1/adapters/topology-capability-v1/publication/GITHUB_READBACK_d7141489fe34.json',
  d40:'backend/course-capsule-v1/adapters/d40-capability-v1/publication/GITHUB_READBACK_4f7d6c825751.json',
  d80:'backend/course-capsule-v1/adapters/d80-capability-v1/publication/GITHUB_READBACK_b22cd627901c.json',
};
const bytes=Object.fromEntries(await Promise.all(Object.entries(sources).map(async([key,path])=>[key,await readFile(resolve(root,path))])));
const data=Object.fromEntries(Object.entries(bytes).map(([key,value])=>[key,JSON.parse(value)]));
assert.equal(data.capsules.length,40);assert.equal(data.families.families.length,33);
assert.equal(data.b80.state,'pass');
assert.equal(new Set(data.capsules.map(row=>row.course_id)).size,40,'Duplicate course role.');
assert.equal(data.b80.anonymous,true);assert.equal(data.b80.credentials_used,false);
assert.equal(data.lebl.state,'pass');assert.equal(data.lebl.anonymous,true);assert.equal(data.lebl.credentials_used,false);
assert.equal(data.geometry.state,'pass');assert.equal(data.geometry.anonymous,true);assert.equal(data.geometry.credentials_used,false);
assert.equal(data.topology.state,'pass');assert.equal(data.topology.anonymous,true);assert.equal(data.topology.credentials_used,false);
assert.equal(data.d40.state,'pass');assert.equal(data.d40.anonymous,true);assert.equal(data.d40.credentials_used,false);
assert.equal(data.d80.state,'pass');assert.equal(data.d80.anonymous,true);assert.equal(data.d80.credentials_used,false);
const leblRoles=['B70','C10','C20','C50'];
for(const filename of [...leblRoles.flatMap(role=>[role+'.html',role+'-pengajar.html']),'istilah.html','learning-map.json','validation.json','filters.js']){
  assert.ok(data.lebl.files.some(row=>row.surface==='pages'&&row.path==='docs/backend/lebl/'+filename&&row.http_status===200&&row.bytes>0&&/^[a-f0-9]{64}$/.test(row.sha256)),filename);
}
for(const path of ['docs/backend/b80/B80.html','docs/backend/b80/B80-pengajar.html','docs/backend/b80/learning-map.json']){
  const proof=data.b80.files.find(row=>row.path===path);
  assert.ok(proof&&proof.http_status===200&&proof.bytes>0,`Missing B80 public readback: ${path}`);
  assert.match(proof.sha256,/^[0-9a-f]{64}$/);
}
for(const filename of ['C100.html','pengajar.html','konsep.html','istilah.html','gambar.html','catatan.html','learning-map.json','validation.json','geometry.js']){
  assert.ok(data.geometry.files.some(row=>row.surface==='pages'&&row.path==='docs/backend/geometry/'+filename&&row.http_status===200&&row.bytes>0&&/^[a-f0-9]{64}$/.test(row.sha256)),filename);
}
for(const filename of ['C90.html','latihan.html','pengajar.html','istilah.html','catatan.html','learning-map.json','validation.json','topology.js']){
  assert.ok(data.topology.files.some(row=>row.surface==='pages'&&row.path==='docs/backend/topology/'+filename&&row.http_status===200&&row.bytes>0&&/^[a-f0-9]{64}$/.test(row.sha256)),filename);
}
for(const filename of ['D40.html','D40-pengajar.html','learning-map.json','validation.json']){
  assert.ok(data.d40.files.some(row=>row.surface==='pages'&&row.path==='docs/backend/d40/'+filename&&row.http_status===200&&row.bytes>0&&/^[a-f0-9]{64}$/.test(row.sha256)),filename);
}
for(const filename of ['D80.html','D80-pengajar.html','learning-map.json','validation.json']){
  assert.ok(data.d80.files.some(row=>row.surface==='pages'&&row.path==='docs/backend/d80/'+filename&&row.http_status===200&&row.bytes>0&&/^[a-f0-9]{64}$/.test(row.sha256)),filename);
}
const familyByRole=new Map();
for(const family of data.families.families)for(const role of family.roles){assert.ok(!familyByRole.has(role));familyByRole.set(role,family);}
assert.equal(familyByRole.size,40);
const frozenPublished=new Map(data.published.adapters.map(row=>[row.role_id,row]));
const frozenPackages=new Map(data.published.packages.map(row=>[row.package_id,row]));
assert.equal(frozenPublished.size,data.published.adapters.length,'Duplicate published role.');
const rows=data.capsules.map(capsule=>{
  const role=capsule.course_id,family=familyByRole.get(role),adapter=capsule.layers.interoperability.semantic_adapter;
  assert.ok(family);
  const integrated=['verified','legacy_verified'].includes(adapter.status);
  const publicRow=frozenPublished.get(role);
  const packet=publicRow?frozenPackages.get(publicRow.adapter_package_id):null;
  if(publicRow){
    assert.ok(packet,`${role}: published binding without a package`);
    assert.equal(packet.admission_state,'published');
    assert.equal(packet.public_replay_status,'published_public_asset_readback_verified');
    assert.equal(packet.native_family_id,family.native_family_id);
  }
  return {role_id:role,title:capsule.course.title,native_family_id:family.native_family_id,native_family_name:family.family_name,
    native_design_audit:{status:'historical_comparison_not_new_native_reaudit',pattern:family.core_pattern,recommended_reuse:family.recommended_reuse,limitations:family.limitations},
    common_adapter:{status:adapter.status,contract:adapter.contract_version??null,mapping_scope:adapter.mapping_scope,
      github_public_evidence:publicRow?'frozen_public_readback':role==='B80'||role==='D40'||role==='D80'||leblRoles.includes(role)||['C90','C100'].includes(role)?'new_anonymous_source_and_pages_readback':'not_established',
      zenodo_preservation:publicRow?'frozen_public_readback':role==='B80'?'assigned_to_central_manager_not_yet_verified':'not_established',
      local_evidence:adapter.evidence??[],
      public_package:packet?{url:packet.public_asset_url,bytes:packet.archive.bytes,sha256:packet.archive.sha256,
        central_record:`https://doi.org/${data.published.snapshot.central_release_record_doi}`} : null},
    learner:{tools:capsule.layers.learner.tools.map(tool=>({label:tool.label,href:'../'+tool.href})),
      unit_identity:capsule.layers.curriculum.unit_identity_status,
      relationship:['B80','D40','D80'].includes(role)||['lebl-learning-capability/1','geometry-learning-capability/1','topology-learning-capability/1'].includes(adapter.contract_version)?'directly_consumes_adapter_outputs':publicRow?.learner_runtime_relationship??'no_common_adapter_consumption_proven'},
    educator:{status:capsule.layers.educator.status,unit_alignment:capsule.layers.educator.unit_alignment_status,resources:capsule.layers.educator.resources},
    dimensions:{
      curriculum:{course_graph:capsule.layers.curriculum.status,unit_identity:capsule.layers.curriculum.unit_identity_status},
      source_translation_ledger:{ledger:capsule.layers.translation.ledger_status,corrections:capsule.layers.translation.corrections_status},
      terminology:{register:capsule.layers.translation.terminology_status},
      reproducible_production:{build:capsule.layers.production.build_status,replay:capsule.layers.production.deterministic_replay_status},
      accessibility:{semantic_html:capsule.layers.learner.capabilities.semantic_html,mathml:capsule.layers.learner.capabilities.mathml},
      learner:{delivery:capsule.layers.learner.status,central_tools:capsule.layers.learner.tools.length},
      educator:{materials:capsule.layers.educator.status,unit_alignment:capsule.layers.educator.unit_alignment_status},
      federation:{references:capsule.layers.federation.status,component_rights:capsule.layers.federation.components.map(row=>({id:row.id,status:row.rights_status}))},
      interoperability:{adapter:adapter.status,contract:adapter.contract_version??null},
    },
    layers:Object.fromEntries(Object.entries(capsule.layers).map(([name,layer])=>[name,{status:layer.status,
      evidence_count:layer.evidence?.length??0}])),
    next_required_work:[
      ...(!integrated?['Periksa backend asli dan implementasikan adapter bersama beserta penggunaan nyata oleh pelajar/pengajar.']:[]),
      ...(capsule.layers.translation.ledger_status!=='verified'?['Buktikan ledger sumber/penerjemahan asli; status ini tidak menyatakan terjemahan belum selesai.']:[]),
      ...(capsule.layers.translation.terminology_status!=='verified'?['Periksa register istilah dan kaitannya dengan teks serta alternatif istilah.']:[]),
      ...(capsule.layers.production.deterministic_replay_status!=='verified'?['Buktikan produksi asli yang dapat diulang; build adapter saja bukan bukti build buku.']:[]),
      ...(capsule.layers.educator.unit_alignment_status!=='verified'?['Hubungkan bahan pengajar dengan identitas unit/latihan yang dipakai pelajar.']:[]),
      ...(role==='B80'?['Verifikasi pelestarian Zenodo yang ditangani pengelola pusat tanpa transaksi rilis yang bersaing.']:[]),
      'Selesaikan audit sembilan bidang kemampuan dan bukti penggunaannya; adapter yang lulus tidak otomatis berarti backend lengkap.'
    ],whole_course_backend_completion:'not_yet_proven'};
});
const integrated=rows.filter(row=>['verified','legacy_verified'].includes(row.common_adapter.status));
const summary={roles:40,native_families:33,locally_validated_adapter_roles:integrated.length,
  locally_represented_families:new Set(integrated.map(row=>row.native_family_id)).size,
  roles_without_validated_common_adapter:40-integrated.length,
  github_evidenced_roles:rows.filter(row=>row.common_adapter.github_public_evidence!=='not_established').length,
  zenodo_evidenced_roles:rows.filter(row=>row.common_adapter.zenodo_preservation==='frozen_public_readback').length,
  overall_program_backend_complete:false};
assert.equal(summary.locally_validated_adapter_roles+summary.roles_without_validated_common_adapter,40);
const model={schema:'program-backend-coverage/1',recorded_date:'2026-09-04',scope:'Backend integration, not textbook translation progress.',
  evidence_semantics:'Unknown means not proved by common-layer evidence, not absent native work. Frozen public readback is historical, not a fresh network recheck.',
  evidence:Object.entries(sources).map(([key,path])=>({path,bytes:bytes[key].length,sha256:sha256(bytes[key])})),summary,roles:rows};
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const statuses={verified:'Diverifikasi',available_unverified:'Ada; belum diverifikasi',not_yet_produced:'Belum dibuat',unknown:'Belum terbukti',in_progress:'Dikerjakan'};
const dimensionNames={curriculum:'Kurikulum dan unit',source_translation_ledger:'Ledger sumber/penerjemahan',terminology:'Istilah',reproducible_production:'Produksi yang dapat diulang',accessibility:'Aksesibilitas',learner:'Pelajar',educator:'Pengajar',federation:'Federasi komponen',interoperability:'Pertukaran data'};
const details=row=>`<h3>Sembilan bidang kemampuan</h3><dl>${Object.entries(row.dimensions).map(([key,values])=>`<dt>${dimensionNames[key]}</dt><dd>${Object.entries(values).map(([name,value])=>`${esc(name)}: ${Array.isArray(value)?value.map(item=>`${esc(item.id)} — ${esc(statuses[item.status]??item.status)}`).join('; '):esc(statuses[value]??value??'Belum terbukti')}`).join('<br>')}</dd>`).join('')}</dl><h3>Pekerjaan tersisa</h3><ul>${row.next_required_work.map(text=>`<li>${esc(text)}</li>`).join('')}</ul><p>Backend lengkap: belum terbukti.</p>${row.common_adapter.public_package?`<p><a href="${esc(row.common_adapter.public_package.url)}">Paket adapter</a> · <a href="${esc(row.common_adapter.public_package.central_record)}">Rekaman pusat historis</a></p>`:''}<details><summary>Desain asli: temuan audit terdahulu</summary><p lang="en">${esc(row.native_design_audit.pattern)}</p><ul lang="en">${row.native_design_audit.recommended_reuse.map(text=>`<li>${esc(text)}</li>`).join('')}</ul><p>Temuan historis berikut harus diperiksa ulang sebelum dianggap masih berlaku:</p><ul lang="en">${row.native_design_audit.limitations.map(text=>`<li>${esc(text)}</li>`).join('')}</ul>${row.role_id==='B80'?'<p>Integrasi B80 sekarang menambahkan pertukaran reversibel serta tampilan pelajar/pengajar bersama.</p>':''}</details>`;
const htmlRows=rows.map(row=>`<tr id="role-${row.role_id}"><th scope="row"><a href="../id/#course-${row.role_id}">${row.role_id} · ${esc(row.title)}</a><small>${esc(row.native_family_name)}</small></th><td>${esc(statuses[row.common_adapter.status]??row.common_adapter.status)}<small>${esc(row.common_adapter.contract??'Belum ada kontrak bersama')}</small></td><td>${row.learner.tools.map(tool=>`<p><a href="${esc(tool.href)}">${esc(tool.label)}</a></p>`).join('')||'<span>Belum ada alat pusat terindeks</span>'}</td><td>${esc(statuses[row.educator.status]??row.educator.status)}${row.educator.resources.map(resource=>`<p><a href="${esc(resource.url)}">${esc(resource.title)}</a></p>`).join('')}</td><td><details><summary>Bukti dan pekerjaan berikutnya</summary>${details(row)}<p>Identitas unit: ${esc(statuses[row.learner.unit_identity]??row.learner.unit_identity)}. Keselarasan pengajar: ${esc(statuses[row.educator.unit_alignment]??row.educator.unit_alignment)}.</p><p>Zenodo: ${row.common_adapter.zenodo_preservation==='frozen_public_readback'?'readback rilis tercatat':row.role_id==='B80'?'pelestarian ditugaskan; belum diverifikasi':'bukti adapter belum tersedia'}.</p></details></td></tr>`).join('\n');
const html=`<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Cakupan backend 40 peran</title><style>body{font:16px/1.5 system-ui;color:#183a35;background:#f5f5ed;margin:0}main{max-width:1400px;margin:auto;padding:28px}a{color:#086b63;text-underline-offset:3px}h1{font-size:2rem}small{display:block;color:#506660;margin-top:6px}.table{overflow:auto}table{border-collapse:collapse;width:100%;background:white}th,td{padding:14px;text-align:left;vertical-align:top;border-bottom:1px solid #cad6d0}thead{background:#e0eae3}th{min-width:220px}td{min-width:170px}p{max-width:90ch}details p{min-width:200px}dt{font-weight:650;margin-top:1rem}dd{margin-left:0}h3{font-size:1rem}a:focus-visible,summary:focus-visible{outline:3px solid #cf8728;outline-offset:3px}</style></head><body><main><nav><a href="index.html">Pusat belajar dan mengajar</a> · <a href="../id/">Program</a></nav><h1>Cakupan backend: 40 peran</h1><p>${summary.locally_validated_adapter_roles} peran mempunyai adapter bersama yang telah diuji; ${summary.roles_without_validated_common_adapter} belum. Ini <strong>bukan</strong> persentase penerjemahan buku, dan tidak berarti backend lengkap untuk semua peran yang sudah mempunyai adapter.</p><p>Readback GitHub tercatat untuk ${summary.github_evidenced_roles} peran; readback pelestarian Zenodo tercatat untuk ${summary.zenodo_evidenced_roles}. Increment B80, Lebl, Geometry, Topology, D40, dan D80 sudah dapat dipakai di web; bukti pelestarian Zenodo tetap dihitung terpisah. Tanggal matriks: 4 September 2026. Temuan desain asli dan bukti rilis terdahulu bukan pemeriksaan ulang seluruh buku hari ini. “Belum terbukti” berarti bukti integrasi pusat belum cukup, bukan berarti pekerjaan asli tidak ada atau terjemahan belum selesai.</p><div class="table" role="region" aria-label="Cakupan semua peran" tabindex="0"><table><caption>Adapter, penggunaan oleh pelajar, dan bahan pengajar per peran</caption><thead><tr><th>Peran dan keluarga native</th><th>Adapter bersama</th><th>Alat pelajar</th><th>Bahan pengajar</th><th>Batas bukti</th></tr></thead><tbody>${htmlRows}</tbody></table></div><p><a href="program-backend-coverage.json">Matriks terbuka dengan identitas bukti</a></p></main></body></html>\n`;
for(const [path,content]of [['backend/course-capsule-v1/generated/program-backend-coverage-v1.json',json(model)],['docs/backend/program-backend-coverage.json',json(model)],['docs/backend/coverage.html',html]]){
  await mkdir(dirname(resolve(root,path)),{recursive:true});await writeFile(resolve(root,path),content);
}
console.log(JSON.stringify({state:'pass',...summary}));
