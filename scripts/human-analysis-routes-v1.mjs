// Navigation integration: OpenAI Codex — GPT-6 Astra, Ultra effort.
// Human textbook content remains Jiří Lebl's; this does not certify consumer proofs.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';

const base='backend/cross-programme-v1/inputs/lebl-public-20261003/';
const origin='https://kokunoyumeto.github.io/open-math-courses/human/lebl-basic-analysis/';
const hash=b=>createHash('sha256').update(b).digest('hex');
const fact=(path,b)=>({path,bytes:b.length,sha256:hash(b)});
const escape=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
// Topic-level reading placement only; not an asserted equivalence of proofs.
const placements={
  sec_rintprop:{courses:['C10'],id:'Sifat-sifat integral'},
  sec_rint:{courses:['C10','B30'],id:'Integral Riemann'},
  sec_liminter:{courses:['C20'],id:'Pertukaran limit'},
  sec_ftc:{courses:['C10','B30'],id:'Teorema dasar kalkulus'},
  sec_complexexp:{courses:['C50'],id:'Fungsi eksponensial kompleks dan trigonometri'},
  sec_factslimsseqs:{courses:['C10'],id:'Sifat-sifat limit barisan'},
  sec_metric:{courses:['C20','C90'],id:'Ruang metrik'},
};

export function validateHumanAnalysis(registry,receipt,coreIds){
  assert.equal(registry.schema,'published-human-analysis-routes/v1');
  assert.equal(receipt.schema,'verified-public-human-analysis-routes/1');
  assert.equal(receipt.state,'public_bytes_and_source_locators_verified');
  assert.equal(receipt.anonymous,true);
  assert.equal(receipt.whole_course_or_dependency_completion_claimed,false);
  assert.equal(registry.reading_url,origin);assert.equal(receipt.reading_url,origin);
  assert.equal(registry.attribution_url,origin+'ATTRIBUTION.html');
  assert.equal(receipt.attribution.url,registry.attribution_url);
  assert.equal(receipt.attribution.status,200);
  assert.equal(receipt.source_archive.url,origin+'basic-analysis-6.3-source.zip');
  assert.equal(receipt.source_archive.status,200);
  assert.match(registry.publication_commit,/^[0-9a-f]{40}$/);
  const rows=registry.routes,checks=receipt.routes;
  assert.equal(rows.length,7);assert.equal(checks.length,7);
  assert.equal(new Set(rows.map(r=>r.id)).size,7);
  assert.equal(new Set(checks.map(r=>r.id)).size,7);
  const routes=rows.map(row=>{
    const key=row.id.replace('human.lebl.analysis.','');
    assert.equal(row.id,'human.lebl.analysis.'+key);
    assert.ok(Object.hasOwn(placements,key),'Unknown source route');
    const spec=placements[key];
    assert.ok(spec.courses.every(id=>coreIds.has(id)),'Unknown curriculum role');
    assert.equal(row.reader,origin+key+'.html');
    assert.equal(row.author,'Jiří Lebl');assert.equal(row.licence,'CC-BY-SA-4.0');
    assert.equal(row.publication_commit,registry.publication_commit);
    assert.equal(row.source_archive,receipt.source_archive.url);
    assert.ok(row.title&&row.anchors.includes(key));
    assert.match(row.source_archive_member,/^ch-[a-z-]+\.tex$/);
    assert.match(row.source_label,/^sec:[a-z]+$/);
    for(const value of [row.reader_sha256,row.source_sha256])assert.match(value,/^[0-9a-f]{64}$/);
    const checked=checks.find(r=>r.id===row.id);assert.ok(checked);
    for(const [a,b] of [['url','reader'],['final_url','reader'],['sha256','reader_sha256'],['source_member','source_archive_member'],['source_sha256','source_sha256'],['source_label','source_label'],['author','author'],['licence','licence'],['publication_commit','publication_commit']])assert.equal(checked[a],row[b]);
    assert.equal(checked.status,200);assert.ok(checked.bytes>0);
    assert.equal(checked.mathematical_consumer_equivalence,'not_inferred');
    assert.equal(checked.verified_declared_anchors,row.anchors.length);
    return {id:row.id,titles:{en:row.title,id:spec.id},course_ids:spec.courses,
      content_language:'en',reader:{url:row.reader,bytes:checked.bytes,sha256:row.reader_sha256},
      source:{archive:receipt.source_archive.url,member:row.source_archive_member,sha256:row.source_sha256,label:row.source_label},
      author:row.author,licence:row.licence,publication_commit:row.publication_commit,
      upstream_commit:row.upstream_commit,anchors:row.anchors,
      relation:'supplementary_reading',mathematical_consumer_equivalence:'not_inferred',
      whole_course_completion:false};
  });
  assert.deepEqual(routes.map(r=>r.id.split('.').at(-1)).sort(),Object.keys(placements).sort());
  return {schema:'programme-human-analysis-readings/1',title:'Basic Analysis',author:'Jiří Lebl',
    licence:'CC-BY-SA-4.0',content_language:'en',reading_url:origin,
    attribution_url:registry.attribution_url,source_archive:receipt.source_archive,
    checked_utc:receipt.checked_utc,routes,
    integration_provenance:{model:'gpt-6-astra',effort:'ultra',scope:'Navigation and source-identity checks; no new textbook translation'}};
}

export async function loadHumanAnalysisRoutes(root,coreIds,read=p=>readFile(resolve(root,p))){
  const registryBytes=await read(base+'REGISTRY.json'),receiptBytes=await read(base+'READBACK.json');
  const registry=JSON.parse(registryBytes),receipt=JSON.parse(receiptBytes);
  assert.equal(hash(registryBytes),receipt.registry_sha256,'Reader verification must bind this exact registry');
  const data=validateHumanAnalysis(registry,receipt,coreIds);
  return {...data,evidence:{registry:fact(base+'REGISTRY.json',registryBytes),readback:fact(base+'READBACK.json',receiptBytes)}};
}

export function renderHumanAnalysisRoutes(data,courseId,locale){
  assert.ok(['en','id'].includes(locale));
  const rows=data.routes.filter(r=>r.course_ids.includes(courseId));if(!rows.length)return '';
  const copy=locale==='id'?{
    title:'Bacaan analisis dari Jiří Lebl',note:'Bagian pilihan dari Basic Analysis. Bacaan berbahasa Inggris; tersedia pembuktian dan latihan.',
    source:'Sumber LaTeX lengkap',credit:'Kredit dan lisensi',lang:'bahasa Inggris',
    ai:'Integrasi navigasi: OpenAI Codex — GPT-6 Astra, tingkat upaya Ultra. Teks buku ditulis oleh Jiří Lebl.'
  }:{title:'Analysis readings by Jiří Lebl',note:'Selected sections from Basic Analysis, with proofs and exercises. These readings are in English.',
    source:'Complete LaTeX sources',credit:'Credits and licence',lang:'English',
    ai:'Navigation integration: OpenAI Codex — GPT-6 Astra, Ultra effort. Textbook by Jiří Lebl.'};
  return '<aside data-human-analysis="'+escape(courseId)+'"><h4>'+copy.title+'</h4><p>'+copy.note+'</p><ul>'+rows.map(r=>'<li><a data-human-analysis-route="'+escape(r.id)+'" href="'+escape(r.reader.url)+'" hreflang="en">'+escape(r.titles[locale])+'</a> ('+copy.lang+')</li>').join('')+'</ul><p><a href="'+escape(data.source_archive.url)+'">'+copy.source+'</a> · <a href="'+escape(data.attribution_url)+'">'+copy.credit+'</a> · '+escape(data.licence)+'</p><small>'+copy.ai+'</small></aside>';
}
