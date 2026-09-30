import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadD100IndonesianEvidence,validateD100IndonesianEvidence,validateD100TranslationClaims,d100TranslationKeys} from './d100-indonesian-evidence-v1.mjs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const actual=await loadD100IndonesianEvidence(root);
const sha=body=>createHash('sha256').update(body).digest('hex');
const json=value=>Buffer.from(JSON.stringify(value)+'\n');
const replace=(bytes,name,change)=>{const value=JSON.parse(bytes[name]);change(value);bytes[name]=json(value);};
const reseal=bytes=>replace(bytes,'evidence.json',report=>{for(const row of report.files){row.bytes=bytes[row.path].length;row.sha256=sha(bytes[row.path]);}});
const editRows=(bytes,name,change)=>{
  const rows=bytes[name].toString('utf8').trimEnd().split('\n').map(line=>JSON.parse(line));
  change(rows);bytes[name]=Buffer.from(rows.map(row=>JSON.stringify(row)).join('\n')+'\n');reseal(bytes);
};
const cases=[
  ['english_report',b=>replace(b,'evidence.json',r=>{r.target_locale='en';})],
  ['invented_canon_review',b=>replace(b,'evidence.json',r=>{r.semantic_canon_review='verified';})],
  ['english_source_lock',b=>{replace(b,'source-lock.json',r=>{r.target_locale='en';});reseal(b);}],
  ['english_stream_substitution',b=>{replace(b,'source-lock.json',r=>{r.sources[0].records.path='backend/english/release-en-v1.0.0/classical/records.jsonl';});reseal(b);}],
  ['missing_witness',b=>editRows(b,'metadata-witnesses.jsonl',r=>r.pop())],
  ['duplicate_witness',b=>editRows(b,'metadata-witnesses.jsonl',r=>{r[1]=r[0];})],
  ['wrong_language_term',b=>editRows(b,'metadata-witnesses.jsonl',rows=>{
    const row=rows.find(r=>JSON.parse(r.native_record).entity_class==='term');
    const native=JSON.parse(row.native_record);native.language='en';
    row.native_record=JSON.stringify(native)+'\r\n';row.source_line_sha256=sha(row.native_record);
  })],
  ['provisional_erasure',b=>editRows(b,'metadata-witnesses.jsonl',rows=>{
    const row=rows.find(r=>JSON.parse(r.native_record).entity_class==='term'&&JSON.parse(r.native_record).status==='provisional');
    const native=JSON.parse(row.native_record);native.status='admitted';
    row.native_record=JSON.stringify(native)+'\r\n';row.source_line_sha256=sha(row.native_record);
  })],
  ['english_segment',b=>editRows(b,'segment-index.jsonl',r=>{r[0].language='en';})],
  ['missing_segment',b=>editRows(b,'segment-index.jsonl',r=>r.pop())],
  ['duplicate_segment_line',b=>editRows(b,'segment-index.jsonl',r=>{r[1].source_line=r[0].source_line;r[1].lane=r[0].lane;})],
];
for(const [name,change] of cases){const bytes={...actual.bytes};change(bytes);assert.throws(()=>validateD100IndonesianEvidence(bytes),undefined,name);}
const overrides=JSON.parse(await readFile(resolve(root,'backend/course-capsule-v1/authority/integration-overrides-v1.json')));
const native=overrides.native_capabilities.D100;
validateD100TranslationClaims(native,actual.evidence);
for(const key of d100TranslationKeys){
  for(const kind of ['wrong_locale','english_evidence','erased_scope']){
    const claims=structuredClone(native);
    if(kind==='wrong_locale')claims[key].locale='en';
    if(kind==='english_evidence')claims[key].evidence=overrides.semantic_adapters.D100.evidence;
    if(kind==='erased_scope')delete claims[key].verification_scope;
    assert.throws(()=>validateD100TranslationClaims(claims,actual.evidence),undefined,key+'/'+kind);
  }
}
console.log(JSON.stringify({state:'pass',evidence_negatives:cases.length,admission_negatives:12,scope:'structure_not_semantic_review'}));
