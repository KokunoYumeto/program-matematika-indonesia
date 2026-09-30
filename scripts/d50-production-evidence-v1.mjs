import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile} from 'node:fs/promises';
import {resolve} from 'node:path';

export const d50ProductionPaths = {
  d50ProductionAudit:'backend/course-capsule-v1/adapters/d50-surface-v1/production/native-production-audit.json',
  d50NativeRebuild:'backend/course-capsule-v1/adapters/d50-surface-v1/production/native-rebuild-receipt.json',
  d50ReaderCurrent:'backend/course-capsule-v1/adapters/d50-surface-v1/production/current-reader-readback.json',
};
const sha=b=>createHash('sha256').update(b).digest('hex');
export async function loadD50ProductionEvidence(root) {
  const raw={},data={};
  for(const [key,path] of Object.entries(d50ProductionPaths)) {
    raw[key]=await readFile(resolve(root,path));data[key]=JSON.parse(raw[key]);
  }
  const a=data.d50ProductionAudit,n=data.d50NativeRebuild,p=data.d50ReaderCurrent;
  assert.equal(a.state,'pass');assert.equal(a.source_members,1282);
  assert.equal(a.all_source_checksums_verified,true);assert.equal(a.native_receipt_two_cycles_validated,true);
  assert.equal(a.native_receipt.bytes,raw.d50NativeRebuild.length);assert.equal(a.native_receipt.sha256,sha(raw.d50NativeRebuild));
  assert.equal(n.status,'pass');assert.deepEqual(n.clean_rebuilds.map(c=>c.cycle),[1,2]);
  assert.deepEqual(n.clean_rebuilds[0].outputs,n.clean_rebuilds[1].outputs);
  assert.equal(a.source_archive.sha256,'94bdc7c1f9ceec599daf59c0d303721be009a140d5a7bd5f794ac8887b935ae3');
  assert.equal(a.fresh_pdf_build,false);assert.equal(a.fresh_html_backend_replay.tex_executed,false);
  assert.equal(a.fresh_html_backend_replay.matches_frozen_native_outputs,true);
  assert.equal(a.fresh_html_backend_replay.commands.length,4);
  assert.ok(a.fresh_html_backend_replay.commands.every(c=>c.exit_code===0));
  assert.deepEqual(Object.keys(a.fresh_html_backend_replay.outputs).sort(),['backend_csv','backend_jsonl','backend_manifest','html_entry','html_manifest']);
  for(const [key,fact] of Object.entries(a.fresh_html_backend_replay.outputs)) assert.deepEqual(fact,n.clean_rebuilds[0].outputs[key]);
  const html=await readFile(resolve(root,'docs/backend/d50/reader/index.html'));
  assert.equal(p.state,'pass');assert.equal(p.anonymous,true);assert.equal(p.bytes,html.length);assert.equal(p.sha256,sha(html));
  assert.equal(p.native_body_sha256,a.fresh_html_backend_replay.outputs.html_entry.sha256);
  return {data,raw,evidence:Object.entries(d50ProductionPaths).map(([key,path])=>({kind:key,locator:path,bytes:raw[key].length,sha256:sha(raw[key])}))};
}

export function validateD50ProductionClaims(claims,proof) {
  for(const key of ['build','deterministic_replay']) {
    assert.equal(claims[key].status,'verified');
    for(const source of proof.evidence.slice(0,2)) {
      const found=claims[key].evidence.find(e=>e.locator===source.locator);
      assert.ok(found);assert.equal(found.bytes,source.bytes);assert.equal(found.sha256,source.sha256);
    }
  }
}

export function validateD50DeliveryOverride(row,proof) {
  const p=proof.data.d50ReaderCurrent;
  for(const key of ['primary','online_html']) {
    assert.equal(row[key].status,'verified');assert.equal(row[key].url,p.url);
    assert.equal(row[key].bytes,p.bytes);assert.equal(row[key].sha256,p.sha256);
    assert.equal(row[key].dependency_free,false);
  }
  const pdf=proof.data.d50NativeRebuild.clean_rebuilds[0].outputs.pdf;
  assert.equal(row.pdf.status,'verified');assert.equal(row.pdf.bytes,pdf.bytes);assert.equal(row.pdf.sha256,pdf.sha256);
  assert.equal(row.portable_html.status,'available_unverified');
  assert.equal(row.portable_html.dependency_free,false);
  assert.equal(row.capabilities.semantic_html.status,'verified');
}
