import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';

export const d70NativeReplayPaths={
  d70NativeReplay:'backend/course-capsule-v1/adapters/d70-native-replay-v1/validation.json',
  d70ReplayBuild:'backend/course-capsule-v1/adapters/d70-native-replay-v1/build/BUILD_RECEIPT.json',
  d70ReplayBundle:'backend/course-capsule-v1/adapters/d70-native-replay-v1/build/D70_NATIVE_METADATA_REPLAY_V1.zip',
};
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
export function validateD70NativeReplay(data,bytes) {
  const replay=data.d70NativeReplay,build=data.d70ReplayBuild;
  assert.equal(replay.schema,'d70-portable-native-metadata-replay/1');assert.equal(replay.state,'pass');
  assert.equal(build.schema,'d70-native-metadata-replay-build/1');assert.equal(build.state,'pass');
  assert.deepEqual(replay.source_archive,{bytes:1295518,name:'05_o013-sumber-backend-1.0.0.zip',sha256:'6273206ffb42277f3040d638e1a0f0870596b823a239fa9d3947d964aa094ef9'});
  assert.deepEqual(build.native_source_zip_supplied_separately,replay.source_archive);
  assert.deepEqual(replay.dependency_bundle,{bytes:bytes.d70ReplayBundle.length,sha256:sha(bytes.d70ReplayBundle)});
  assert.deepEqual(build.bundle,{path:d70NativeReplayPaths.d70ReplayBundle,...replay.dependency_bundle});
  for(const key of ['dependency_files','dependency_bytes'])assert.equal(replay[key],build[key]);
  assert.equal(replay.dependency_files,26);assert.equal(replay.dependency_bytes,4322608);
  assert.equal(replay.source_members,68);assert.equal(build.member_count,34);
  assert.equal(build.native_book_bodies_included,false);assert.equal(build.whole_native_parity_proven,false);
  for(const flag of ['producer_tree_required','network_required_for_replay','fresh_tex_build','fresh_semantic_canon_review','whole_native_parity_proven','producer_files_modified'])assert.equal(replay[flag],false);
  for(const flag of ['packaged_sources_executed','two_isolated_replays_identical','native_source_copied_before_execution'])assert.equal(replay[flag],true);
  assert.equal(replay.supplied_input_archives,2);assert.equal(replay.input_archive_bytes,1295518+bytes.d70ReplayBundle.length);
  assert.deepEqual(replay.commands.map(c=>c.component),['duncan','cring']);
  for(const command of replay.commands){
    assert.equal(command.exit_code,0);
    assert.equal(command.command,`python -B repo/components/${command.component}/backend/validate_${command.component}_backend.py --regenerate`);
    const report=JSON.parse(command.output);assert.equal(report.result,'PASS');
    assert.ok(report.artifacts.length>0);assert.match(report.validator.sha256,/^[a-f0-9]{64}$/);
  }
  const originalArtifacts=replay.commands.flatMap(command=>{const report=JSON.parse(command.output);return [...report.artifacts,report.receipt];});
  assert.equal(originalArtifacts.length,13);assert.equal(replay.artifact_comparisons.length,13);
  assert.equal(new Set(replay.artifact_comparisons.map(row=>row.path)).size,13);
  for(const row of replay.artifact_comparisons){
    assert.equal(row.matches_shipped_bytes,true);
    const native=originalArtifacts.find(item=>item.path==='repo/'+row.path);assert.ok(native);
    assert.equal(row.bytes,native.bytes);assert.equal(row.sha256,native.sha256);
  }
  return {status:'verified_native_metadata_replay_not_full_book_replay',components:['duncan','cring'],
    metadata_artifacts:13,dependency_files:26,dependency_bytes:4322608,packaged_source_runs:2,
    producer_tree_required:false,fresh_tex_build:false,fresh_semantic_canon_review:false,whole_native_parity_proven:false,
    source_archive:replay.source_archive,dependency_bundle:replay.dependency_bundle,
    guide_id:'d70-replay/index.html',guide_en:'d70-replay/index.en.html',
    evidence:Object.entries(d70NativeReplayPaths).map(([key,path])=>({path,bytes:bytes[key].length,sha256:sha(bytes[key])})),
    note_id:'Dua pembangun metadata native dijalankan dari kode paket dalam dua direktori terpisah dan menghasilkan 13 berkas yang sama persis. Sebanyak 26 input tambahan disediakan; direktori pembuat buku tidak diperlukan. Replay seluruh Li dan keempat PDF tetap belum terbukti.',
    note_en:'Two native metadata builders run from packaged code in two isolated directories and reproduce 13 exact artifacts. Twenty-six additional inputs are supplied; no producer tree is required. Whole-Li and all four PDF replay remain unproven.'};
}
