import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile} from 'node:fs/promises';
import {resolve} from 'node:path';

export const d100IdBase = 'backend/course-capsule-v1/adapters/d100-indonesian-evidence-v1';
export const d100IdFiles = ['source-lock.json','metadata-witnesses.jsonl','segment-index.jsonl','evidence.json'];
export const d100TranslationKeys = ['translation_ledger','terminology','translation_rights','corrections'];
export const d100TranslationVerification = Object.freeze({
  evidence_locale:'id-ID', scope:'native_ledger_structure_and_identity_only',
  semantic_canon_review:'not_established',
});
const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');
const pins = [
  ['classical','units-01-30-corr1',38025813,'90d4e621bde73f34e5487156c61f51aa6788d7ffb37644febd82f7d392b4b1e2',23869],
  ['bgk','bgk-units-01-30-corr1',25933440,'e30f72fbcadd7ca9f9ad4b295bdb3f0a3ce2ec1071532553dad11256557cb9b0',21690],
  ['original','original-bridge-corr1',4815165,'fc074bb8bf4d80c1d63f74522a531f0aae752b1c112ee869a8dca7218cd3532e',1064],
];
const rows = bytes => bytes.toString('utf8').trimEnd().split('\n').map(line=>JSON.parse(line));

export function validateD100IndonesianEvidence(bytes) {
  const report = JSON.parse(bytes['evidence.json']);
  const lock = JSON.parse(bytes['source-lock.json']);
  assert.equal(report.schema,'d100-indonesian-ledger-evidence/1');
  assert.equal(report.state,'pass');
  assert.equal(report.course_id,'D100');
  assert.equal(report.target_locale,'id-ID','D100 wrong-language evidence');
  assert.equal(report.verification_scope,d100TranslationVerification.scope);
  assert.equal(report.semantic_canon_review,'not_established','D100 cannot invent canon review');
  assert.equal(report.native_edited,false);
  assert.equal(report.book_bodies_copied,false);
  assert.equal(report.record_rows,46623);
  assert.deepEqual(report.counts,{correction:371,rights:149,segment:15829,term:905});
  assert.equal(lock.schema,'d100-indonesian-source-lock/1');
  assert.equal(lock.course_id,'D100');
  assert.equal(lock.target_locale,'id-ID','D100 wrong-language source lock');
  assert.equal(lock.repository,'https://github.com/KokunoYumeto/algebraic-geometry-bridge-id');
  assert.equal(lock.sources.length,3);
  for (const [i,[lane,directory,size,sha,count]] of pins.entries()) {
    const source = lock.sources[i];
    assert.equal(source.lane,lane);
    assert.deepEqual(source.records,{path:`backend/${directory}/records.jsonl`,bytes:size,sha256:sha},'D100 native input binding drift');
    assert.equal(report.inventories[i].lane,lane);
    assert.equal(report.inventories[i].records,count);
  }
  assert.deepEqual(report.files.map(row=>row.path),d100IdFiles.filter(name=>name!=='evidence.json').sort());
  for (const item of report.files) {
    assert.equal(bytes[item.path].length,item.bytes,'D100 witness byte drift');
    assert.equal(sha256(bytes[item.path]),item.sha256,'D100 witness hash drift');
  }
  const identities = new Set(), lines = new Set(), counts = new Map(), termStates = new Map();
  const seen = (entry,row) => {
    const pin = pins.find(p=>p[0]===entry.lane);
    assert.ok(pin,'D100 unexpected lane');
    assert.ok(Number.isInteger(entry.source_line)&&entry.source_line>0&&entry.source_line<=pin[4]);
    assert.match(entry.source_line_sha256,/^[a-f0-9]{64}$/);
    const id = entry.lane+':'+row.stable_id;
    assert.ok(row.stable_id&&!identities.has(id),'D100 duplicate identity');
    identities.add(id);
    const line = entry.lane+':'+entry.source_line;
    assert.ok(!lines.has(line),'D100 duplicate source line');
    lines.add(line);
    const key = [entry.lane,row.entity_class,row.language].join('|');
    counts.set(key,(counts.get(key)??0)+1);
  };
  for (const entry of rows(bytes['metadata-witnesses.jsonl'])) {
    assert.equal(sha256(Buffer.from(entry.native_record,'utf8')),entry.source_line_sha256,'D100 raw witness line drift');
    const row = JSON.parse(entry.native_record);
    assert.equal(row.schema,'ag-bridge-backend-record');
    assert.equal(row.schema_version,'1.0.0');
    assert.ok(['term','correction','rights'].includes(row.entity_class));
    if(row.entity_class!=='rights')assert.equal(row.language,'id-ID','D100 wrong-language native metadata');
    if(row.entity_class==='term') {
      const payload = row.payload.ledger_row??row.payload;
      assert.ok(payload.preferred_target,'D100 missing preferred target');
      assert.equal(payload.target_language??'id-ID','id-ID','D100 wrong-language term payload');
      const key=entry.lane+'|'+row.status;
      termStates.set(key,(termStates.get(key)??0)+1);
    }
    seen(entry,row);
  }
  for (const entry of rows(bytes['segment-index.jsonl'])) {
    assert.equal(entry.language,'id-ID','D100 wrong-language segment');
    assert.match(entry.content_sha256,/^[a-f0-9]{64}$/);
    assert.ok(!('markdown' in entry)&&!('payload' in entry),'D100 book body copied');
    seen(entry,{...entry,entity_class:'segment'});
  }
  const expected = new Map();
  for(const inventory of report.inventories) {
    for(const row of inventory.entity_locales)if(['term','correction','rights','segment'].includes(row.entity))
      expected.set([inventory.lane,row.entity,row.language].join('|'),row.count);
    for(const [state,count] of Object.entries(inventory.term_states))
      assert.equal(termStates.get(inventory.lane+'|'+state),count,'D100 native term state drift');
  }
  assert.deepEqual([...counts].sort(),[...expected].sort(),'D100 inventory scope drift');
  assert.equal(termStates.get('classical|provisional'),4,'D100 provisional states must survive');
  return report;
}

export async function loadD100IndonesianEvidence(root) {
  const bytes={};
  for(const name of d100IdFiles)bytes[name]=await readFile(resolve(root,d100IdBase,name));
  const report=validateD100IndonesianEvidence(bytes);
  const evidence=['source-lock.json','evidence.json'].map((name,index)=>({
    kind:index?'indonesian_native_ledger_structural_validation':'indonesian_native_ledger_source_lock',
    locator:`${d100IdBase}/${name}`,bytes:bytes[name].length,sha256:sha256(bytes[name]),verified_date:'2026-09-30',
  }));
  return {bytes,report,evidence};
}

export function validateD100TranslationClaims(claims,evidence) {
  for(const key of d100TranslationKeys) {
    assert.equal(claims[key]?.status,'verified',`D100/${key}: missing native ledger claim`);
    assert.equal(claims[key]?.locale,'id-ID',`D100/${key}: wrong-language claim`);
    assert.equal(claims[key]?.verification_scope,d100TranslationVerification.scope);
    assert.deepEqual(claims[key]?.evidence,evidence,`D100/${key}: must use Indonesian native evidence, not the English adapter`);
  }
}
