// Read only the frozen native metadata; never compile or mutate a producer.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const native=resolve(root,'../openstax-prealgebra/modular_backend');
const output=resolve(root,'backend/course-capsule-v1/adapters/a00-concept-teacher-v1/input');
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const specs={
  originalGraph:['curation/a00-concept-prerequisites.v1.json','acfddef3015112ca0b3805e8a22b782433da4d8d835d7f357fd2b223d03fbe23'],
  graph:['generated/prealgebra2e-volume/metadata/a00-concept-prerequisites.v1.json','254f151384102f03256909bb803bf9a6611573afc4f4c1a1601545d28d8a060f'],
  overlay:['generated/prealgebra2e-volume/metadata/a00-concept-terms.id-ID.v1.json','0a3adf325286cd848eb69860e3197bf534a5d21aed57c1a1c3ef91988cd724cd'],
  nativeConcepts:['generated/prealgebra2e-volume/content/concepts.jsonl','b77c318843abc614020398d682f65dfe9ccc6b88db2994d47a070be8125f2236'],
  nativeManifest:['generated/prealgebra2e-volume/backend.volume.manifest.json','e27b23f6bff5c56949e149af6decb8ecd9d7bf30ab049d65a5dd344e232b913d'],
  rights:['generated/prealgebra2e-volume/registry/rights.jsonl','e4ee15296e81cd04a219eb3df8ef06123fe15a94dcf620d09d4e230ffd108e7b'],
};
const input={},sources={};
for(const [key,[path,expected]] of Object.entries(specs)) {
  const bytes=await readFile(resolve(native,path));
  assert.equal(hash(bytes),expected,key+': frozen source changed');
  sources[key]={provider:'openstax-prealgebra-native',path,bytes:bytes.length,sha256:hash(bytes)};
  input[key]=path.endsWith('.jsonl')?bytes.toString('utf8').trim().split('\n').map(JSON.parse):JSON.parse(bytes);
}
const portable=structuredClone(input.originalGraph);
delete portable.curriculum_source.path;
portable.curriculum_source.authority_id=input.graph.curriculum_source.authority_id;
portable.curriculum_source.path_locator=input.graph.curriculum_source.path_locator;
assert.deepEqual(portable,input.graph,'Source/emitted difference is not metadata-only');
const contract=input.nativeManifest.curriculum_mapping;
assert.equal(contract.neutral_curation.source_authority.sha256,'sha256:'+sources.originalGraph.sha256);
assert.equal(contract.neutral_curation.sha256,'sha256:'+sources.graph.sha256);
assert.equal(contract.localized_overlay.sha256,'sha256:'+sources.overlay.sha256);
assert.equal(input.overlay.neutral_curation.sha256,sources.originalGraph.sha256);
for(const [key,path] of Object.entries({
  crosswalks:'backend/v2.2/packages/a00-openstax-prealgebra-v0.1.0/tables/identity_crosswalks.jsonl',
  assessments:'docs/id-ID/courses/A00/latihan/assessment-map-v1.json',
  anchorAudit:'docs/id-ID/courses/A00/latihan/anchor-audit-v1.json',
})) {
  const bytes=await readFile(resolve(root,path));
  sources[key]={provider:'central-admitted-A00',path,bytes:bytes.length,sha256:hash(bytes)};
  if(key==='crosswalks')input.crosswalks=bytes.toString('utf8').trim().split('\n').map(JSON.parse);
}
assert.equal(sources.assessments.sha256,'2a350672680c57ad4a8d7daeb46827f12487b9cf0793597f55970ca4d9471858');
assert.equal(sources.anchorAudit.sha256,'d50bd0203359a13f2eac176e021920635ed07258ee9622ab0d89e09c6ac12926');
const keys=['id','concept_key','concept_role','label_en_us','definition_en_us','prerequisite_ids',
  'module_evidence_count','objective_evidence_count','module_unit_ids','objective_unit_ids',
  'rights_component_id','mapping_source_sha256'];
const artifacts={
  'neutral-graph.json':input.graph,
  'localized-terms.json':input.overlay,
  'concept-identities.json':input.nativeConcepts.map(row=>Object.fromEntries(keys.map(key=>[key,row[key]]))),
  'module-crosswalks.json':input.crosswalks.map(row=>({semantic_key:row.semantic_key,
    payload:{source_id:row.payload.source_id,target_id:row.payload.target_id}})),
  'native-curriculum-contract.json':contract,
  'concept-rights.json':input.rights.find(row=>row.id==='urn:uuid:81c77a9e-bdec-54bc-9575-49590af7efd3'),
};
assert.equal(artifacts['concept-rights.json'].license,'CC BY-NC-SA 4.0');
await mkdir(output,{recursive:true});
const snapshots=[];
for(const [path,value] of Object.entries(artifacts)) {
  const bytes=Buffer.from(JSON.stringify(value,null,2)+'\n');
  assert.doesNotMatch(bytes.toString('utf8'),/(?:^|["'\s])[A-Za-z]:[\\/]|codex:\/\/threads\//m);
  await writeFile(resolve(output,path),bytes);
  snapshots.push({path,bytes:bytes.length,sha256:hash(bytes)});
}
const lock={schema:'a00-concept-source-lock/1',sources,snapshots,
  original_to_emitted:{result:'equal_after_three_metadata_changes',
    removed:['/curriculum_source/path'],added:['/curriculum_source/authority_id','/curriculum_source/path_locator'],
    concept_revision:false,original_private_path_not_exported:true,
    evidence_timing:'retrospective_source_comparison_not_historical_canon_consultation'},
  limitations:['Native source identity and mapping replay do not establish linguistic correctness.',
    'Raw original graph is not copied because it contains a private machine-local locator.',
    'Small metadata snapshots are included; textbook bodies and the native database are not copied.']};
await writeFile(resolve(output,'source-lock.json'),JSON.stringify(lock,null,2)+'\n');
console.log(JSON.stringify({status:'pass',metadata_snapshots:snapshots.length,source_transform:lock.original_to_emitted}));
