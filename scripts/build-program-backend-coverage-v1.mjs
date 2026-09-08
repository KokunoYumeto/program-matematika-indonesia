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
  clpRoutes:'backend/course-capsule-v1/authority/clp-family-v231/learner-reader-actions-v1.json',
  clpView:'docs/backend/clp/validation.json',
  a20:'backend/course-capsule-v1/adapters/a20-capability-v1/publication/GITHUB_READBACK_a2729467c523.json',
  a30Manifest:'backend/course-capsule-v1/adapters/a30-capability-v1/manifest.json',
  a30Validation:'backend/course-capsule-v1/adapters/a30-capability-v1/validation.json',
  a30Public:'backend/course-capsule-v1/adapters/a30-capability-v1/data/public-evidence.json',
  a30NativeReadback:'backend/course-capsule-v1/adapters/a30-capability-v1/input/public-native-readback.json',
  a30Integration:'backend/course-capsule-v1/adapters/a30-capability-v1/publication/GITHUB_READBACK_74b208108a25.json',
  b95Manifest:'backend/course-capsule-v1/adapters/b95-capability-v1/manifest.json',
  b95Validation:'backend/course-capsule-v1/adapters/b95-capability-v1/validation.json',
  b95Public:'backend/course-capsule-v1/adapters/b95-capability-v1/data/public-evidence.json',
  b95NativeReadback:'backend/course-capsule-v1/adapters/b95-capability-v1/input/public-native-readback.json',
  c140Manifest:'backend/course-capsule-v1/adapters/c140-capability-v1/manifest.json',
  c140Validation:'backend/course-capsule-v1/adapters/c140-capability-v1/validation.json',
  c140Public:'backend/course-capsule-v1/adapters/c140-capability-v1/data/public-evidence.json',
  c140SourceLock:'backend/course-capsule-v1/adapters/c140-capability-v1/input/source-lock.json',
  c140GithubRelease:'backend/course-capsule-v1/adapters/c140-capability-v1/input/github-release-readback.json',
  c140GithubPages:'backend/course-capsule-v1/adapters/c140-capability-v1/input/github-pages-readback.json',
  c140Zenodo:'backend/course-capsule-v1/adapters/c140-capability-v1/input/zenodo-readback.json',
  c140Package:'backend/course-capsule-v1/adapters/c140-capability-v1/build/PACKET_BUILD_RECEIPT.json',
  b40:'backend/course-capsule-v1/adapters/b40-capability-v1/publication/GITHUB_READBACK_35b2e2bd34d0.json',
  b80:'backend/course-capsule-v1/adapters/b80-capability-v1/publication/GITHUB_SOURCE_AND_PAGES_READBACK_20260904.json',
  lebl:'backend/course-capsule-v1/adapters/lebl-capability-v1/publication/GITHUB_READBACK_97960cc12b34.json',
  geometry:'backend/course-capsule-v1/adapters/geometry-capability-v1/publication/GITHUB_READBACK_a2584b9448c9.json',
  topology:'backend/course-capsule-v1/adapters/topology-capability-v1/publication/GITHUB_READBACK_d7141489fe34.json',
  c70:'backend/course-capsule-v1/adapters/c70-capability-v1/publication/GITHUB_READBACK_4eb34c5d866a.json',
  c110:'backend/course-capsule-v1/adapters/c110-capability-v1/publication/GITHUB_READBACK_c7ccbcc9a27a.json',
  c120:'backend/course-capsule-v1/adapters/c120-capability-v1/publication/GITHUB_READBACK_5cef326a811b.json',
  c60:'backend/course-capsule-v1/adapters/c60-capability-v1/publication/GITHUB_READBACK_306c9e080f89.json',
  b90:'backend/course-capsule-v1/adapters/b90-capability-v1/publication/GITHUB_READBACK_37dfd587bac2.json',
  d10:'backend/course-capsule-v1/adapters/d10-capability-v1/publication/GITHUB_READBACK_a290054a4e16.json',
  d30Manifest:'backend/course-capsule-v1/adapters/d30-capability-v1/manifest.json',
  d30Validation:'backend/course-capsule-v1/adapters/d30-capability-v1/validation.json',
  d30Public:'backend/course-capsule-v1/adapters/d30-capability-v1/data/public-evidence.json',
  d40:'backend/course-capsule-v1/adapters/d40-capability-v1/publication/GITHUB_READBACK_4f7d6c825751.json',
  d70:'backend/course-capsule-v1/adapters/d70-capability-v1/publication/GITHUB_READBACK_2ce9fbb5dacd.json',
  d80:'backend/course-capsule-v1/adapters/d80-capability-v1/publication/GITHUB_READBACK_b22cd627901c.json',
  d90:'backend/course-capsule-v1/adapters/d90-capability-v1/publication/GITHUB_READBACK_1ec3ed4846c8.json',
  d100:'backend/course-capsule-v1/adapters/d100-capability-v1/publication/GITHUB_READBACK_9b9480ff5b2c.json',
  d120:'backend/course-capsule-v1/adapters/d120-capability-v1/publication/GITHUB_READBACK_a42650f4815a.json',
  d50Publication:'backend/v2.3/admissions/d50-smooth-manifolds-v0.1.0/publication/PUBLICATION_BINDING_v0.63.21.json',
  gapAdmission:'backend/course-capsule-v1/validation/20260907/GAP_ADMISSION.json',
  gapZipA30:'backend/course-capsule-v1/packages/A30_PRECALCULUS_V231_ADAPTER.zip',
  gapZipB95:'backend/course-capsule-v1/packages/B95_OPENINTRO_STATISTICS_V231_ADAPTER.zip',
  gapZipC140:'backend/course-capsule-v1/packages/C140_MATHEMATICAL_STATISTICS_V231_ADAPTER.zip',
  centralV06324:'publication-history/PUBLICATION_RECEIPT_v0.63.24.json',
};
const bytes=Object.fromEntries(await Promise.all(Object.entries(sources).map(async([key,path])=>[key,await readFile(resolve(root,path))])));
const binarySourceKeys=new Set(['gapZipA30','gapZipB95','gapZipC140']);
const data=Object.fromEntries(Object.entries(bytes).filter(([key])=>!binarySourceKeys.has(key)).map(([key,value])=>[key,JSON.parse(value)]));
// The v2.3.1 admission receipt is an additive package witness.  It must not
// replace native course truth, but every package/twin/spec identity must remain
// discoverable from the central coverage matrix.
assert.equal(data.gapAdmission.schema,'gap-admission/1');
assert.equal(data.gapAdmission.contract,'interlanguage/global-modular-mathematics-lane-adapter/2.3.1');
assert.equal(data.gapAdmission.status,'pass');
const gapRoles=['A30','B95','C140'];
assert.deepEqual(Object.keys(data.gapAdmission.roles).sort(),gapRoles.slice().sort());
for(const role of gapRoles){
  const gap=data.gapAdmission.roles[role];
  assert.ok(gap.package?.package_id && gap.package?.path && Number.isInteger(gap.package.bytes) && /^[a-f0-9]{64}$/.test(gap.package.sha256),`${role}: package witness incomplete`);
  assert.equal(gap.twin?.status,'pass',`${role}: twin admission did not pass`);
  assert.ok(Number.isInteger(gap.twin.bytes) && /^[a-f0-9]{64}$/.test(gap.twin.sha256),`${role}: twin identity incomplete`);
  assert.ok(gap.spec?.path && Number.isInteger(gap.spec.bytes) && /^[a-f0-9]{64}$/.test(gap.spec.sha256),`${role}: specification identity incomplete`);
  assert.equal(gap.common_adapter?.status,'verified',`${role}: common adapter admission status drifted`);
  assert.equal(gap.common_adapter?.package_id,gap.package.package_id,`${role}: package id cross-link drifted`);
  assert.equal(gap.common_adapter?.payload_sha256,gap.package.sha256,`${role}: payload hash cross-link drifted`);
  assert.ok(gap.learner_tools?.page?.path && Number.isInteger(gap.learner_tools.page.bytes) && /^[a-f0-9]{64}$/.test(gap.learner_tools.page.sha256),`${role}: learner page witness incomplete`);
}
assert.equal(data.centralV06324.schema_id,'program-matematika-indonesia/multilingual-interface-publication/v1');
assert.equal(data.centralV06324.version,'0.63.24');
assert.equal(data.centralV06324.state,'published_open_and_anonymously_verified');
assert.equal(data.centralV06324.source_commit,'5a89e03c5c3a281e67ae3a1046fec268c5a4d361');
assert.equal(data.centralV06324.source_tree,'81e11fd88811fafb46f3e116b9625ff10d20fccb');
assert.equal(data.centralV06324.github.release.tag,'v0.63.24');
assert.equal(data.centralV06324.github.anonymous_readback.result,'PASS');
assert.equal(data.centralV06324.zenodo.doi,'10.5281/zenodo.22646380');
assert.equal(data.centralV06324.zenodo.access,'open');
assert.equal(data.centralV06324.zenodo.latest_concept_version_verified,true);
const gapZipKeyByRole={A30:'gapZipA30',B95:'gapZipB95',C140:'gapZipC140'};
for(const role of gapRoles){
  const publishedPacket=data.centralV06324.v231_gap_adapters.packets[role];
  assert.ok(publishedPacket,`${role}: v0.63.24 packet binding missing`);
  const zipKey=gapZipKeyByRole[role];
  assert.equal(publishedPacket.source_path,sources[zipKey],`${role}: published source path drifted`);
  assert.equal(publishedPacket.sha256,sha256(bytes[zipKey]),`${role}: published ZIP hash drifted`);
  assert.equal(publishedPacket.bytes,bytes[zipKey].length,`${role}: published ZIP byte count drifted`);
  assert.equal(publishedPacket.deterministic_and_checksum_closed,true,`${role}: published ZIP closure is not proved`);
}
const gapPublicEmbedding={
  status:'published_open_and_anonymously_verified',
  version:'0.63.24',
  github_release:data.centralV06324.github.release.url,
  zenodo:`https://doi.org/${data.centralV06324.zenodo.doi}`,
  receipt:{path:sources.centralV06324,bytes:bytes.centralV06324.length,sha256:sha256(bytes.centralV06324)},
};
assert.equal(data.capsules.length,40);assert.equal(data.families.families.length,33);
assert.equal(data.b40.state,'pass');
assert.equal(data.b80.state,'pass');
assert.equal(data.clpRoutes.status,'verified_route_evidence_projection');
assert.equal(data.clpRoutes.summary.action_count,7);assert.equal(data.clpRoutes.summary.course_count,4);
assert.equal(data.clpRoutes.summary.pages,4077);assert.equal(data.clpRoutes.summary.bytes,35639691);
assert.equal(data.clpRoutes.summary.route_granularity,'whole_file_only');
assert.equal(data.clpRoutes.summary.native_html_claimed,false);assert.equal(data.clpRoutes.summary.chapter_or_unit_routes_claimed,false);
assert.equal(data.clpView.state,'pass');
assert.deepEqual(data.clpView.source,{path:sources.clpRoutes,bytes:bytes.clpRoutes.length,sha256:sha256(bytes.clpRoutes)});
assert.equal(new Set(data.capsules.map(row=>row.course_id)).size,40,'Duplicate course role.');
assert.equal(data.a20.schema,'a20-integration-public-readback/1');
assert.equal(data.a20.state,'pass');assert.equal(data.a20.anonymous,true);assert.equal(data.a20.credentials_used,false);
assert.equal(data.a20.source_commit,'a2729467c523ca2327a112e24145cab2aad56c38');
assert.equal(data.a20.base_commit,'9475ee08e547fd3446c4dc1b7e187b46e71d62c9');
assert.equal(data.a20.expected_files,152);assert.equal(data.a20.verified_files,152);assert.deepEqual(data.a20.failures,[]);
assert.equal(data.a30Manifest.schema,'a30-capability-manifest/1');
assert.equal(data.a30Manifest.course_id,'A30');assert.equal(data.a30Manifest.contract,'course-learning-capability/1');
assert.equal(data.a30Manifest.projection.native_ids_preserved,true);
assert.equal(data.a30Manifest.projection.native_bodies_copied,false);
assert.equal(data.a30Manifest.projection.source_or_target_text_copied,false);
assert.equal(data.a30Manifest.projection.component_rights_preserved,true);
assert.equal(data.a30Manifest.projection.segment_state_asymmetry_preserved,true);
assert.equal(data.a30Manifest.outputs.length,48);
assert.equal(data.a30Manifest.canonical_jsonl_sha256,'4f2f51457adde0516c17b1633327a3bfbbf273a67925514bbb6c390f5e58a054');
for(const [key,value] of Object.entries({native_records:220680,chapters:12,modules:87,pdf_pages:3165,exercises:7250,solution_identities:4183,unsupported_exercises:3067,concepts:497,terms:513,corrections:703,component_rights:1875,relations:37974,segments:149955,units:26965}))assert.equal(data.a30Manifest.counts[key],value,`A30 manifest count drift: ${key}`);
assert.equal(data.a30Manifest.public_release.complete,true);assert.equal(data.a30Manifest.public_release.tag,'v1.0.0');
assert.equal(data.a30Manifest.public_release.final_derivative_revision_proved,false);
assert.equal(data.a30Validation.schema,'a30-capability-validation/1');assert.equal(data.a30Validation.course_id,'A30');
assert.equal(data.a30Validation.result,'pass');assert.deepEqual(data.a30Validation.counts,data.a30Manifest.counts);
assert.equal(data.a30Validation.negative_fixtures.length,27);assert.ok(data.a30Validation.negative_fixtures.every(({result})=>result==='rejected'));
assert.equal(data.a30Validation.checks.two_run_build_identity.file_count,49);
assert.equal(data.a30Validation.checks.two_run_build_identity.tree_sha256,'51b3c1cf9f3709a540fe59c9df63b186968ceb6c41fccce265c504bf970244cd');
assert.equal(data.a30Public.schema,'a30-public-evidence/1');assert.equal(data.a30Public.course_id,'A30');
assert.equal(data.a30Public.anonymous_readback,true);assert.equal(data.a30Public.credentials_used,false);
assert.equal(data.a30Public.repository.public,true);assert.equal(data.a30Public.repository.url,'https://github.com/KokunoYumeto/openstax-precalculus-2e-id');
assert.equal(data.a30Public.repository.tag,'v1.0.0');assert.equal(data.a30Public.github_release.assets.length,7);assert.equal(data.a30Public.github_release.total_bytes,499884557);
assert.equal(data.a30Public.zenodo.access_right,'open');assert.equal(data.a30Public.zenodo.assets.length,7);assert.equal(data.a30Public.zenodo.total_bytes,499884557);
assert.equal(data.a30Public.indonesian_reader.pdf_pages,3165);assert.equal(data.a30Public.indonesian_reader.bytes,305654938);
assert.equal(data.a30Public.indonesian_reader.sha256,'3cfd5294b91252cc766992f158b6601e80aa31b719b0b8bf69e1ff6d08a4fa3e');
assert.equal(data.a30NativeReadback.schema,'a30-native-public-readback/1');assert.equal(data.a30NativeReadback.course_id,'A30');
assert.equal(data.a30NativeReadback.state,'pass');assert.equal(data.a30NativeReadback.anonymous,true);assert.equal(data.a30NativeReadback.credentials_used,false);assert.deepEqual(data.a30NativeReadback.failures,[]);
assert.equal(data.a30NativeReadback.github_release.assets.length,7);assert.equal(data.a30NativeReadback.zenodo.assets.length,7);assert.equal(data.a30NativeReadback.zenodo.access_right,'open');
assert.equal(data.a30Integration.schema,'a30-integration-public-readback/1');assert.equal(data.a30Integration.state,'pass');
assert.equal(data.a30Integration.source_commit,'74b208108a258916eb160ac5b8d3b72f2844809b');
assert.equal(data.a30Integration.base_commit,'1edaf095c63b79b1f2d83fa6062f13bbdf2e4203');
assert.equal(data.a30Integration.anonymous,true);assert.equal(data.a30Integration.credentials_used,false);
assert.equal(data.a30Integration.expected_files,13);assert.equal(data.a30Integration.verified_files,13);assert.deepEqual(data.a30Integration.failures,[]);
for(const [surface,path,key] of [
  ['source',sources.a30Manifest,'a30Manifest'],['source',sources.a30Validation,'a30Validation'],
  ['source',sources.a30Public,'a30Public'],['source',sources.a30NativeReadback,'a30NativeReadback'],
  ['source','backend/course-capsule-v1/adapters/a30-capability-v1/views/A30.html',null],
  ['source','backend/course-capsule-v1/adapters/a30-capability-v1/views/A30-pengajar.html',null],
  ['source','docs/backend/a30/A30.html',null],['source','docs/backend/a30/A30-pengajar.html',null],
  ['source','backend/course-capsule-v1/generated/program-backend-coverage-v1.json',null],
  ['source','backend/course-capsule-v1/validation/SITE_VALIDATION_RECEIPT.json',null],
  ['pages','docs/backend/a30/A30.html',null],['pages','docs/backend/a30/A30-pengajar.html',null],
  ['pages','docs/backend/coverage.html',null]
]){
  const row=data.a30Integration.files.find(item=>item.surface===surface&&item.path===path);
  assert.ok(row,`A30 integration readback missing ${surface} ${path}`);assert.equal(row.http_status,200);
  if(key){assert.equal(row.bytes,bytes[key].length);assert.equal(row.sha256,sha256(bytes[key]));}
}
assert.equal(data.b95Manifest.schema,'b95-capability-manifest/1');
assert.equal(data.b95Manifest.course_id,'B95');assert.equal(data.b95Manifest.contract,'course-learning-capability/1');
assert.equal(data.b95Manifest.boundary_id,'R011-B039');assert.equal(data.b95Manifest.native_family,'openintro_statistics_fourth_edition');
assert.equal(data.b95Manifest.content_policy,'identity_structure_terminology_rights_evidence_only');
assert.equal(data.b95Manifest.projection.native_ids_preserved,true);assert.equal(data.b95Manifest.projection.native_bodies_copied,false);
assert.equal(data.b95Manifest.projection.component_rights_preserved,true);assert.equal(data.b95Manifest.projection.external_native_backend_required_for_replay,true);
assert.equal(data.b95Manifest.projection.reversible_exchange_claimed,false);assert.equal(data.b95Manifest.projection.public_access_state_changed,false);
assert.equal(data.b95Manifest.outputs.length,35);assert.equal(data.b95Manifest.negative_fixture_count,12);
for(const [key,value] of Object.entries({native_records:21746,chapters:9,sections:35,subsections:83,units:1089,segments:2231,exercises:448,exercise_units:322,guided_exercises:126,public_answer_ids:153,o001_gap_ids:105,concepts:826,terms:859,corrections:302,component_rights:80,relations:11127,evidence_records:2049,localizations:2231,reader_pages:462,source_files:1245}))assert.equal(data.b95Manifest.counts[key],value,`B95 manifest count drift: ${key}`);
assert.equal(data.b95Validation.schema,'b95-capability-validation/1');assert.equal(data.b95Validation.course_id,'B95');assert.equal(data.b95Validation.boundary_id,'R011-B039');
assert.equal(data.b95Validation.result,'pass');assert.deepEqual(data.b95Validation.counts,data.b95Manifest.counts);
assert.equal(data.b95Validation.negative_fixtures.length,12);assert.ok(data.b95Validation.negative_fixtures.every(({result})=>result==='rejected'));
assert.equal(data.b95Validation.checks.negative_fixtures_rejected,12);assert.equal(data.b95Validation.checks.public_reader_pages,462);
assert.equal(data.b95Validation.checks.two_run_build_identity.file_count,36);
assert.equal(data.b95Validation.checks.two_run_build_identity.tree_sha256,'dd580a0af4fb9b2262489ec46e4692069b7949b3dbdd19c8206254f1c0c156ae');
assert.equal(data.b95Public.schema,'b95-public-evidence/1');assert.equal(data.b95Public.course_id,'B95');assert.equal(data.b95Public.boundary_id,'R011-B039');
assert.equal(data.b95Public.anonymous_readback,true);assert.equal(data.b95Public.credentials_used,false);
assert.equal(data.b95Public.repository.public,true);assert.equal(data.b95Public.repository.url,'https://github.com/KokunoYumeto/statistika-berbasis-data-id');
assert.equal(data.b95Public.repository.tag,'r011-b039-2026.09.01.2');assert.equal(data.b95Public.release.public,true);
assert.equal(data.b95Public.release.asset_count,9);assert.equal(data.b95Public.release.assets.length,9);assert.equal(data.b95Public.release.aggregate_payload_bytes,110476928);
assert.ok(data.b95Public.release.assets.every(row=>row.github_readback&&row.zenodo_readback&&row.github_bytes===row.bytes&&row.zenodo_bytes===row.bytes&&row.github_sha256===row.sha256&&row.zenodo_sha256===row.sha256));
assert.equal(data.b95Public.zenodo.public,true);assert.equal(data.b95Public.zenodo.access_right,'open');assert.equal(data.b95Public.zenodo.record_id,22261912);
assert.equal(data.b95Public.reader.pdf_pages,462);assert.equal(data.b95Public.reader.pdf_sha256,'7ef1ed4390cd846cc636345d34a1ba3765f8afc32eb9446fd60c7862b7fde049');
assert.equal(data.b95NativeReadback.$schema,'interlanguage.r011-b039-final-completion/v1');assert.equal(data.b95NativeReadback.boundary_id,'R011-B039');
assert.equal(data.b95NativeReadback.status,'COMPLETE_TRANSLATED_ADMITTED_PUBLISHED_AND_PUBLICLY_READ_BACK');assert.equal(data.b95NativeReadback.complete_corpus,true);
assert.equal(data.b95NativeReadback.translation.source_files,1245);assert.equal(data.b95NativeReadback.translation.terminal_source_cursor,true);
assert.equal(data.b95NativeReadback.reader.pages,462);assert.equal(data.b95NativeReadback.reader.bytes,57049904);assert.equal(data.b95NativeReadback.reader.sha256,data.b95Public.reader.pdf_sha256);
assert.equal(data.b95NativeReadback.reader.untranslated_instructional_or_exercise_prose_pages,0);assert.equal(data.b95NativeReadback.backend.record_count,21746);
assert.equal(data.b95NativeReadback.release.asset_count,9);assert.equal(data.b95NativeReadback.publication.github.public,true);assert.equal(data.b95NativeReadback.publication.zenodo.public,true);
assert.equal(data.b95NativeReadback.publication.github.all_nine_assets_read_back_by_bytes_and_sha256,true);assert.equal(data.b95NativeReadback.publication.zenodo.all_nine_files_read_back_by_bytes_and_sha256,true);
assert.equal(data.b95NativeReadback.credentials_recorded,false);assert.equal(data.b95NativeReadback.next_action,null);
assert.equal(data.c140Manifest.schema,'c140-capability-manifest/1');
assert.equal(data.c140Manifest.course_id,'C140');assert.equal(data.c140Manifest.contract,'course-learning-capability/1');
assert.equal(data.c140Manifest.boundary_id,'C140-C5-54');assert.equal(data.c140Manifest.native_family,'penn_stat415_random_completeness_original_companion');
assert.equal(data.c140Manifest.content_policy,'identity_structure_terminology_corrections_rights_and_public_routes_only');
assert.deepEqual(data.c140Manifest.projection,{
  component_rights_preserved:true,
  external_native_backend_required_for_replay:true,
  native_bodies_copied:false,
  native_ids_preserved:true,
  public_access_state_changed:false,
  reversible_content_exchange_claimed:false,
  whole_course_component_boundary_proven:true,
});
for(const [key,value] of Object.entries({penn_documents:14,random_documents:1,companion_documents:39,public_documents:54,penn_units:6510,penn_segments:4932,penn_math_surfaces:3156,penn_terms:192,penn_corrections:242,random_entities:325,random_relations:474,random_terms:42,random_adverse_records:19,companion_entities:1523,companion_relations:1949,companion_theory_documents:13,companion_mastery_documents:13,companion_simulation_documents:6,companion_assessment_documents:4,companion_capstone_documents:2,companion_solved_problems:146,companion_rubrics:62,stable_entity_ids:8358,structural_relations:2423,terminology_rows:234,correction_and_adverse_rows:261,component_rights:9}))assert.equal(data.c140Manifest.counts[key],value,`C140 manifest count drift: ${key}`);
assert.equal(data.c140Manifest.outputs.length,37);assert.equal(data.c140Manifest.negative_fixture_count,12);
assert.equal(data.c140Validation.schema,'c140-capability-validation/1');assert.equal(data.c140Validation.course_id,'C140');assert.equal(data.c140Validation.boundary_id,'C140-C5-54');
assert.equal(data.c140Validation.result,'pass');assert.deepEqual(data.c140Validation.counts,data.c140Manifest.counts);
assert.equal(data.c140Validation.negative_fixtures.length,12);assert.equal(data.c140Validation.checks.negative_fixtures_rejected,12);
assert.equal(data.c140Validation.checks.two_run_build_identity.file_count,38);assert.equal(data.c140Validation.checks.two_run_build_identity.tree_sha256,'8983788c83539c5f1450a3a2d57ad94ccf448ba1496b96ef384f76c6c314797b');
assert.equal(data.c140Public.schema,'c140-public-evidence/1');assert.equal(data.c140Public.status,'pass');
assert.equal(data.c140Public.translation_provenance,'OpenAI Codex gpt-5.6-sol, Ultra');
assert.equal(data.c140Public.repository.url,'https://github.com/KokunoYumeto/penn-state-stat-415-id');assert.equal(data.c140Public.repository.anonymous_asset_readback,true);
assert.equal(data.c140Public.repository.release_tag,'v2026.08.31.c140-companion-c5');assert.equal(data.c140Public.repository.file_count,65);
assert.equal(data.c140Public.pages.anonymous_readback,true);assert.equal(data.c140Public.pages.course_document_files.length,54);
assert.equal(new Set(data.c140Public.pages.course_document_files.map(row=>row.path)).size,54);assert.ok(data.c140Public.pages.course_document_files.every(row=>row.http_status===200&&row.bytes>0&&/^[a-f0-9]{64}$/.test(row.sha256)));
assert.equal(data.c140Public.zenodo.access_right,'open');assert.equal(data.c140Public.zenodo.anonymous_readback,true);assert.equal(data.c140Public.zenodo.doi,'10.5281/zenodo.22208527');assert.equal(data.c140Public.zenodo.file_count,65);
assert.equal(data.c140SourceLock.schema,'c140-source-lock/1');assert.equal(data.c140SourceLock.boundary_id,'C140-C5-54');assert.equal(data.c140SourceLock.input_count,99);
assert.equal(data.c140GithubRelease.schema,'o006.c140.companion-c5.github-release-readback.v1');assert.equal(data.c140GithubRelease.status,'pass');assert.equal(data.c140GithubRelease.public_asset_readback_anonymous,true);
assert.equal(data.c140GithubPages.schema,'o006.c140.companion-c5.github-pages-readback.v1');assert.equal(data.c140GithubPages.status,'pass');
assert.equal(data.c140Zenodo.schema,'o006.c140.zenodo-c140-companion-c5-publication.v1');assert.equal(data.c140Zenodo.public.anonymous_readback,true);assert.equal(data.c140Zenodo.public.file_count,65);assert.equal(data.c140Zenodo.public.doi,'10.5281/zenodo.22208527');
assert.equal(data.c140Package.schema,'c140-capability-thin-packet-build-receipt/1');assert.equal(data.c140Package.result,'PASS');assert.equal(data.c140Package.zip_checks.member_count,45);assert.equal(data.c140Package.archive.sha256,'6c7745f1b999d72a517ec000259f1b230a922b56cf002a27f6506dea85baa296');
assert.equal(data.b40.anonymous,true);assert.equal(data.b40.credentials_used,false);
assert.equal(data.b80.anonymous,true);assert.equal(data.b80.credentials_used,false);
assert.equal(data.lebl.state,'pass');assert.equal(data.lebl.anonymous,true);assert.equal(data.lebl.credentials_used,false);
assert.equal(data.geometry.state,'pass');assert.equal(data.geometry.anonymous,true);assert.equal(data.geometry.credentials_used,false);
assert.equal(data.topology.state,'pass');assert.equal(data.topology.anonymous,true);assert.equal(data.topology.credentials_used,false);
assert.equal(data.c70.state,'pass');assert.equal(data.c70.anonymous,true);assert.equal(data.c70.credentials_used,false);
assert.equal(data.c110.state,'pass');assert.equal(data.c110.anonymous,true);assert.equal(data.c110.credentials_used,false);
assert.equal(data.c120.state,'pass');assert.equal(data.c120.anonymous,true);assert.equal(data.c120.credentials_used,false);
assert.equal(data.c60.state,'pass');assert.equal(data.c60.anonymous,true);assert.equal(data.c60.credentials_used,false);
assert.equal(data.b90.state,'pass');assert.equal(data.b90.anonymous,true);assert.equal(data.b90.credentials_used,false);
assert.equal(data.b90.source_commit,'37dfd587bac231dc985f6185f6a6c7e48122f856');
assert.equal(data.b90.base_commit,'47d42078b05e57705a2185ed531a3ea82f0490b6');
assert.equal(data.d10.state,'pass');assert.equal(data.d10.anonymous,true);assert.equal(data.d10.credentials_used,false);
assert.equal(data.d30Manifest.schema,'d30-capability-manifest/1');
assert.equal(data.d30Manifest.course_id,'D30');assert.equal(data.d30Manifest.contract,'course-learning-capability/1');
assert.equal(data.d30Manifest.zero_copy,true);assert.equal(data.d30Manifest.native_bodies_copied,false);
assert.equal(data.d30Manifest.component_rights_preserved,true);assert.equal(data.d30Manifest.public_state_changed,false);
assert.equal(data.d30Validation.schema,'d30-capability-validation/1');
assert.equal(data.d30Validation.course_id,'D30');assert.equal(data.d30Validation.contract,data.d30Manifest.contract);
assert.equal(data.d30Validation.result,'PASS');assert.ok(Object.values(data.d30Validation.checks).every(Boolean));
assert.deepEqual(data.d30Validation.counts,data.d30Manifest.counts);
assert.deepEqual(data.d30Validation.manifest,{path:'manifest.json',bytes:bytes.d30Manifest.length,sha256:sha256(bytes.d30Manifest)});
assert.equal(data.d30Public.schema,'d30-public-evidence/1');
assert.equal(data.d30Public.anonymous_reader_byte_readback,true);assert.equal(data.d30Public.all_public_sha256_exact,true);
assert.equal(data.d30Public.repository,'https://github.com/KokunoYumeto/measure-theoretic-probability-stochastic-processes-id');
assert.equal(data.d30Public.reader,'https://kokunoyumeto.github.io/measure-theoretic-probability-stochastic-processes-id/');
assert.equal(data.d30Public.doi,'10.5281/zenodo.22182655');assert.equal(data.d30Public.concept_doi,'10.5281/zenodo.22059941');
assert.equal(data.d30Public.content_commit,data.d30Manifest.native_release.commit);
assert.equal(data.d30Public.content_tree,data.d30Manifest.native_release.tree);
assert.equal(data.d30Public.files.length,6);assert.ok(data.d30Public.files.every(row=>row.bytes>0&&/^[a-f0-9]{64}$/.test(row.sha256)&&row.url.startsWith('https://zenodo.org/')));
const d30PublicOutput=data.d30Manifest.outputs.find(row=>row.path==='data/public-evidence.json');
assert.deepEqual(d30PublicOutput,{path:'data/public-evidence.json',bytes:bytes.d30Public.length,sha256:sha256(bytes.d30Public)});
assert.equal(data.d40.state,'pass');assert.equal(data.d40.anonymous,true);assert.equal(data.d40.credentials_used,false);
assert.equal(data.d70.state,'pass');assert.equal(data.d70.anonymous,true);assert.equal(data.d70.credentials_used,false);
assert.equal(data.d80.state,'pass');assert.equal(data.d80.anonymous,true);assert.equal(data.d80.credentials_used,false);
assert.equal(data.d90.state,'pass');assert.equal(data.d90.anonymous,true);assert.equal(data.d90.credentials_used,false);
assert.equal(data.d100.state,'pass');assert.equal(data.d100.anonymous,true);assert.equal(data.d100.credentials_used,false);
assert.equal(data.d120.state,'pass');assert.equal(data.d120.anonymous,true);assert.equal(data.d120.credentials_used,false);
assert.equal(data.d50Publication.schema,'d50-central-publication-binding/1');
assert.equal(data.d50Publication.status,'published_and_anonymously_byte_verified');
assert.equal(data.d50Publication.access_policy.public,true);
assert.equal(data.d50Publication.access_policy.credentials_recorded,false);
assert.equal(data.d50Publication.github.anonymous_asset_readback,'exact_bytes_sha256');
assert.equal(data.d50Publication.zenodo.access,'open');
assert.equal(data.d50Publication.zenodo.embedding.member_sha256,data.d50Publication.adapter.sha256);
assert.equal(data.d50Publication.zenodo.embedding.member_bytes,data.d50Publication.adapter.bytes);
const leblRoles=['B70','C10','C20','C50'];
const clpRoles=['B20','B30','B50','B60'];
const clpActionsByRole=new Map(clpRoles.map(role=>[role,data.clpRoutes.actions.filter(action=>action.course_id===role)]));
for(const role of clpRoles){
  const actions=clpActionsByRole.get(role);assert.ok(actions.length>0);
  for(const action of actions){assert.equal(action.state,'verified');assert.equal(action.route_granularity,'whole_file_only');}
  const page=data.clpView.outputs.course_entry_source_bodies[role];
  assert.deepEqual(page.path,`docs/backend/clp/${role}.html`);assert.match(page.sha256,/^[a-f0-9]{64}$/);assert.ok(page.bytes>0);
}
for(const filename of [...leblRoles.flatMap(role=>[role+'.html',role+'-pengajar.html']),'istilah.html','learning-map.json','validation.json','filters.js']){
  assert.ok(data.lebl.files.some(row=>row.surface==='pages'&&row.path==='docs/backend/lebl/'+filename&&row.http_status===200&&row.bytes>0&&/^[a-f0-9]{64}$/.test(row.sha256)),filename);
}
for(const path of ['docs/backend/b80/B80.html','docs/backend/b80/B80-pengajar.html','docs/backend/b80/learning-map.json']){
  const proof=data.b80.files.find(row=>row.path===path);
  assert.ok(proof&&proof.http_status===200&&proof.bytes>0,`Missing B80 public readback: ${path}`);
  assert.match(proof.sha256,/^[0-9a-f]{64}$/);
}
for(const filename of ['A20.html','A20-pengajar.html','capabilities.json','claim-boundary.json','data/concept-index.jsonl','data/corrections-index.jsonl','data/exercise-index.jsonl','data/module-index.jsonl','data/native-record-ledger.json','data/pedagogical-relation-index.jsonl','data/rights-index.jsonl','data/terms-index.jsonl','educator-map.json','learning-map.json','public-evidence.json','public-native-readback.json','source-lock.json','validation.json']){
  assert.ok(data.a20.files.some(row=>row.surface==='pages'&&row.path==='docs/backend/a20/'+filename&&row.http_status===200&&row.bytes>0&&/^[a-f0-9]{64}$/.test(row.sha256)),filename);
}
for(const filename of ['B40.html','B40-pengajar.html','concept-index.json','educator-map.json','learning-map.json','ledger-references.json','manifest.json','public-evidence.json','relation-index.json','rights-and-terms.json','validation.json']){
  assert.ok(data.b40.files.some(row=>row.surface==='pages'&&row.path==='docs/backend/b40/'+filename&&row.http_status===200&&row.bytes>0&&/^[a-f0-9]{64}$/.test(row.sha256)),filename);
}
for(const filename of ['C100.html','pengajar.html','konsep.html','istilah.html','gambar.html','catatan.html','learning-map.json','validation.json','geometry.js']){
  assert.ok(data.geometry.files.some(row=>row.surface==='pages'&&row.path==='docs/backend/geometry/'+filename&&row.http_status===200&&row.bytes>0&&/^[a-f0-9]{64}$/.test(row.sha256)),filename);
}
for(const filename of ['C90.html','latihan.html','pengajar.html','istilah.html','catatan.html','learning-map.json','validation.json','topology.js']){
  assert.ok(data.topology.files.some(row=>row.surface==='pages'&&row.path==='docs/backend/topology/'+filename&&row.http_status===200&&row.bytes>0&&/^[a-f0-9]{64}$/.test(row.sha256)),filename);
}
for(const filename of ['C70.html','C70-pengajar.html','learning-map.json','educator-map.json','concept-index.json','relation-index.json','rights-and-terms.json','ledger-references.json','public-evidence.json','validation.json']){
  assert.ok(data.c70.files.some(row=>row.surface==='pages'&&row.path==='docs/backend/c70/'+filename&&row.http_status===200&&row.bytes>0&&/^[a-f0-9]{64}$/.test(row.sha256)),filename);
}
for(const filename of ['C110.html','C110-pengajar.html','learning-map.json','educator-map.json','translation-alignments.json','rights-and-terms.json','ledger-references.json','validation.json']){
  assert.ok(data.c110.files.some(row=>row.surface==='pages'&&row.path==='docs/backend/c110/'+filename&&row.http_status===200&&row.bytes>0&&/^[a-f0-9]{64}$/.test(row.sha256)),filename);
}
for(const filename of ['C120.html','C120-pengajar.html','learning-map.json','educator-map.json','rights-and-terms.json','ledger-references.json','validation.json']){
  assert.ok(data.c120.files.some(row=>row.surface==='pages'&&row.path==='docs/backend/c120/'+filename&&row.http_status===200&&row.bytes>0&&/^[a-f0-9]{64}$/.test(row.sha256)),filename);
}
for(const filename of ['C60.html','C60-pengajar.html','capabilities.json','claim-boundary.json','concept-index.json','educator-map.json','learning-map.json','ledger-references.json','manifest.json','native-id-index.json','public-evidence.json','relation-index.json','rights-and-terms.json','validation.json']){
  assert.ok(data.c60.files.some(row=>row.surface==='pages'&&row.path==='docs/backend/c60/'+filename&&row.http_status===200&&row.bytes>0&&/^[a-f0-9]{64}$/.test(row.sha256)),filename);
}
for(const filename of ['B90.html','B90-pengajar.html','capabilities.json','learning-map.json','educator-map.json','public-evidence.json','claim-boundary.json','data/unit-index.jsonl','data/concept-index.jsonl','data/relation-index.jsonl','data/terms-index.jsonl','data/corrections-index.jsonl','data/rights-index.jsonl','source-lock.json','public-native-readback.json','validation.json']){
  assert.ok(data.b90.files.some(row=>row.surface==='pages'&&row.path==='docs/backend/b90/'+filename&&row.http_status===200&&row.bytes>0&&/^[a-f0-9]{64}$/.test(row.sha256)),filename);
}
for(const filename of ['D10.html','D10-pengajar.html','learning-map.json','educator-map.json','rights-and-terms.json','ledger-references.json','validation.json']){
  assert.ok(data.d10.files.some(row=>row.surface==='pages'&&row.path==='docs/backend/d10/'+filename&&row.http_status===200&&row.bytes>0&&/^[a-f0-9]{64}$/.test(row.sha256)),filename);
}
for(const filename of ['D40.html','D40-pengajar.html','learning-map.json','validation.json']){
  assert.ok(data.d40.files.some(row=>row.surface==='pages'&&row.path==='docs/backend/d40/'+filename&&row.http_status===200&&row.bytes>0&&/^[a-f0-9]{64}$/.test(row.sha256)),filename);
}
for(const filename of ['D70.html','D70-pengajar.html','learning-map.json','validation.json']){
  assert.ok(data.d70.files.some(row=>row.surface==='pages'&&row.path==='docs/backend/d70/'+filename&&row.http_status===200&&row.bytes>0&&/^[a-f0-9]{64}$/.test(row.sha256)),filename);
}
for(const filename of ['D80.html','D80-pengajar.html','learning-map.json','validation.json']){
  assert.ok(data.d80.files.some(row=>row.surface==='pages'&&row.path==='docs/backend/d80/'+filename&&row.http_status===200&&row.bytes>0&&/^[a-f0-9]{64}$/.test(row.sha256)),filename);
}
for(const filename of ['D90.html','D90-pengajar.html','capabilities.json','learning-map.json','educator-map.json','public-evidence.json','claim-boundary.json','data/rights-index.jsonl','data/corrections-index.jsonl','data/terms-index.jsonl','validation.json']){
  assert.ok(data.d90.files.some(row=>row.surface==='pages'&&row.path==='docs/backend/d90/'+filename&&row.http_status===200&&row.bytes>0&&/^[a-f0-9]{64}$/.test(row.sha256)),filename);
}
for(const filename of ['D100.html','D100-pengajar.html','learning-map.json','validation.json']){
  assert.ok(data.d100.files.some(row=>row.surface==='pages'&&row.path==='docs/backend/d100/'+filename&&row.http_status===200&&row.bytes>0&&/^[a-f0-9]{64}$/.test(row.sha256)),filename);
}
for(const filename of ['D120.html','D120-pengajar.html','learning-map.json','educator-map.json','validation.json']){
  assert.ok(data.d120.files.some(row=>row.surface==='pages'&&row.path==='docs/backend/d120/'+filename&&row.http_status===200&&row.bytes>0&&/^[a-f0-9]{64}$/.test(row.sha256)),filename);
}
const familyByRole=new Map();
for(const family of data.families.families)for(const role of family.roles){assert.ok(!familyByRole.has(role));familyByRole.set(role,family);}
assert.equal(familyByRole.size,40);
const frozenPublished=new Map(data.published.adapters.map(row=>[row.role_id,row]));
const frozenPackages=new Map(data.published.packages.map(row=>[row.package_id,row]));
assert.equal(frozenPublished.size,data.published.adapters.length,'Duplicate published role.');
const gapByRole=new Map(gapRoles.map(role=>[role,data.gapAdmission.roles[role]]));
const rows=data.capsules.map(capsule=>{
  const role=capsule.course_id,family=familyByRole.get(role),adapter=capsule.layers.interoperability.semantic_adapter,gap=gapByRole.get(role);
  assert.ok(family);
  if(role==='A30'){
    assert.equal(adapter.status,'verified');assert.equal(adapter.contract_version,data.a30Manifest.contract);
    assert.equal(adapter.mapping_scope,'zero_copy_projection_of_220680_native_records_87_modules_7250_exercise_problem_identities_4183_solution_identities_497_concepts_513_terms_703_corrections_1875_component_rights_and_segment_state_asymmetry_with_3067_unsupported_solution_cases_preserved');
    for(const [kind,path,key] of [
      ['central_adapter_manifest',sources.a30Manifest,'a30Manifest'],
      ['deterministic_validation_receipt',sources.a30Validation,'a30Validation'],
      ['verified_native_public_release',sources.a30Public,'a30Public'],
      ['anonymous_native_public_readback',sources.a30NativeReadback,'a30NativeReadback'],
    ]){
      const evidence=adapter.evidence.find(row=>row.kind===kind&&row.locator===path);
      assert.ok(evidence,`A30 missing exact ${kind} evidence`);
      assert.equal(evidence.bytes,bytes[key].length);assert.equal(evidence.sha256,sha256(bytes[key]));
    }
    assert.equal(capsule.course_native.repository,data.a30Public.repository.url);
    assert.equal(capsule.course_native.zenodo,`https://doi.org/${data.a30Public.zenodo.version_doi}`);
    assert.equal(capsule.layers.production.repository,data.a30Public.repository.url);
    assert.equal(capsule.layers.production.zenodo,`https://doi.org/${data.a30Public.zenodo.version_doi}`);
    assert.equal(capsule.course_native.status, data.gapAdmission.roles.A30.course_truth.publication_evidence ? 'verified' : 'available_unverified');
    assert.equal(capsule.layers.production.release_status, data.gapAdmission.roles.A30.course_truth.publication_evidence ? 'verified' : 'available_unverified');
    const pdf=data.a30Public.github_release.assets.find(row=>row.name==='OpenStax-Precalculus-2e-id-ID-1.0.0-reader.pdf');
    assert.ok(pdf);assert.equal(capsule.layers.learner.pdf.sha256,pdf.sha256);assert.equal(capsule.layers.learner.pdf.bytes,pdf.bytes);
  }
  if(role==='B95'){
    assert.equal(adapter.status,'verified');assert.equal(adapter.contract_version,data.b95Manifest.contract);
    assert.equal(adapter.mapping_scope,'zero_copy_projection_of_21746_native_records_1089_units_448_exercises_826_concepts_859_terms_302_corrections_80_component_rights_and_2231_segments_and_localizations_with_153_public_answer_and_105_o001_gap_identities');
    for(const [kind,path,key] of [
      ['central_adapter_manifest',sources.b95Manifest,'b95Manifest'],
      ['deterministic_validation_receipt',sources.b95Validation,'b95Validation'],
      ['verified_native_public_release',sources.b95Public,'b95Public'],
      ['anonymous_native_public_readback',sources.b95NativeReadback,'b95NativeReadback'],
    ]){
      const evidence=adapter.evidence.find(row=>row.kind===kind&&row.locator===path);
      assert.ok(evidence,`B95 missing exact ${kind} evidence`);
      assert.equal(evidence.bytes,bytes[key].length);assert.equal(evidence.sha256,sha256(bytes[key]));
    }
    assert.equal(capsule.course_native.repository,data.b95Public.repository.url);
    assert.equal(capsule.course_native.zenodo,`https://doi.org/${data.b95Public.zenodo.doi}`);
    assert.equal(capsule.course_native.edition,data.b95Public.reader.zenodo_url);
    assert.equal(capsule.layers.production.repository,data.b95Public.repository.url);
    assert.equal(capsule.layers.production.zenodo,`https://doi.org/${data.b95Public.zenodo.doi}`);
    assert.equal(capsule.layers.production.edition,data.b95Public.reader.zenodo_url);
    assert.equal(capsule.layers.production.release_status,'verified');
    assert.equal(capsule.layers.production.build_status,'verified');assert.equal(capsule.layers.production.deterministic_replay_status,'verified');
    assert.equal(capsule.layers.learner.status,'verified');
    assert.deepEqual(capsule.layers.learner.tools.map(({tool_id,label,href,state,primary})=>({tool_id,label,href,state,primary})),[{tool_id:'b95.open_learner_hub',label:'B95 · Statistika Terapan dan Analisis Data',href:'backend/b95/B95.html',state:'verified',primary:false}]);
    for(const key of ['primary','pdf']){
      assert.equal(capsule.layers.learner[key].status,'verified');assert.equal(capsule.layers.learner[key].url,data.b95Public.reader.zenodo_url);
      assert.equal(capsule.layers.learner[key].bytes,data.b95NativeReadback.reader.bytes);assert.equal(capsule.layers.learner[key].sha256,data.b95NativeReadback.reader.sha256);
    }
    for(const key of ['epub','portable_html'])assert.equal(capsule.layers.learner[key].status,'not_yet_produced');
    assert.equal(capsule.layers.learner.online_html.status,'available_unverified');
    assert.equal(capsule.layers.learner.online_html.scope,'course_gateway');
    assert.equal(capsule.layers.learner.online_html.url,'https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/B95/');
    assert.deepEqual(capsule.layers.learner.capabilities,{chapter_downloads:'not_yet_produced',mathml:'available_unverified',print_profile:'verified',semantic_html:'not_yet_produced'});
    assert.equal(capsule.layers.educator.status,'verified');assert.equal(capsule.layers.educator.unit_alignment_status,'verified');assert.equal(capsule.layers.educator.resources.length,14);
  }
  if(role==='C140'){
    assert.equal(adapter.status,'verified');assert.equal(adapter.contract_version,data.c140Manifest.contract);
    assert.equal(adapter.mapping_scope,'zero_copy_projection_of_complete_54_document_three_component_boundary_8358_stable_entity_ids_2423_structural_relations_234_terminology_rows_261_correction_or_adverse_rows_146_solved_problem_identities_62_rubrics_and_9_distinct_rights_projections');
    for(const [kind,path,key] of [
      ['central_adapter_manifest',sources.c140Manifest,'c140Manifest'],
      ['deterministic_validation_receipt',sources.c140Validation,'c140Validation'],
      ['verified_native_public_release',sources.c140Public,'c140Public'],
      ['native_source_lock',sources.c140SourceLock,'c140SourceLock'],
      ['anonymous_github_release_readback',sources.c140GithubRelease,'c140GithubRelease'],
      ['anonymous_github_pages_readback',sources.c140GithubPages,'c140GithubPages'],
      ['anonymous_zenodo_readback',sources.c140Zenodo,'c140Zenodo'],
      ['deterministic_package_receipt',sources.c140Package,'c140Package'],
    ]){
      const evidence=adapter.evidence.find(row=>row.kind===kind&&row.locator===path);
      assert.ok(evidence,`C140 missing exact ${kind} evidence`);
      assert.equal(evidence.bytes,bytes[key].length);assert.equal(evidence.sha256,sha256(bytes[key]));
    }
    assert.equal(capsule.course_native.repository,data.c140Public.repository.url);
    assert.equal(capsule.course_native.zenodo,`https://doi.org/${data.c140Public.zenodo.doi}`);
    assert.equal(capsule.layers.production.repository,data.c140Public.repository.url);
    assert.equal(capsule.layers.production.zenodo,`https://doi.org/${data.c140Public.zenodo.doi}`);
    assert.equal(capsule.layers.production.release_status,'available_unverified');
    assert.equal(capsule.layers.production.build_status,'verified');assert.equal(capsule.layers.production.deterministic_replay_status,'verified');
    assert.equal(capsule.layers.learner.status,'verified');assert.equal(capsule.layers.learner.online_html.status,'verified');
    assert.equal(capsule.layers.learner.online_html.url,data.c140Public.pages.base_url);assert.equal(capsule.layers.learner.tools.length,1);assert.equal(capsule.layers.learner.tools[0].tool_id,'c140.open_learner_hub');
    assert.equal(capsule.layers.learner.pdf.status,'verified');assert.equal(capsule.layers.learner.pdf.scope,'penn_spine_component_only_not_uniform_whole_course');
    assert.equal(capsule.layers.learner.epub.status,'verified');assert.equal(capsule.layers.learner.epub.scope,'penn_spine_component_only_not_uniform_whole_course');
    assert.equal(capsule.layers.educator.status,'verified');assert.equal(capsule.layers.educator.unit_alignment_status,'verified');assert.equal(capsule.layers.educator.resources.length,15);
  }
  if(role==='D30'){
    assert.equal(adapter.status,'verified');assert.equal(adapter.contract_version,data.d30Manifest.contract);
    assert.equal(adapter.mapping_scope,'zero_copy_projection_of_2538_entities_6333_segments_3256_relations_57_high_level_surfaces_5_labs_36_solved_mastery_problems_and_2_equivalent_assessments');
    for(const [kind,path,key] of [
      ['central_adapter_manifest',sources.d30Manifest,'d30Manifest'],
      ['deterministic_validation_receipt',sources.d30Validation,'d30Validation'],
      ['verified_native_public_release',sources.d30Public,'d30Public'],
    ]){
      const evidence=adapter.evidence.find(row=>row.kind===kind&&row.locator===path);
      assert.ok(evidence,`D30 missing exact ${kind} evidence`);
      assert.equal(evidence.bytes,bytes[key].length);assert.equal(evidence.sha256,sha256(bytes[key]));
    }
    assert.equal(capsule.course_native.repository,data.d30Public.repository);
    assert.equal(capsule.course_native.zenodo,`https://doi.org/${data.d30Public.doi}`);
    assert.equal(capsule.layers.production.repository,data.d30Public.repository);
    assert.equal(capsule.layers.production.zenodo,`https://doi.org/${data.d30Public.doi}`);
    assert.equal(capsule.layers.production.release_status,'verified');
    assert.equal(capsule.layers.learner.online_html.url,data.d30Public.reader);
    assert.equal(capsule.layers.learner.primary.url,data.d30Public.reader);
    const pdf=data.d30Public.files.find(row=>row.filename==='00_PROBABILITAS_TEORI_UKURAN_PROSES_STOKASTIK_ID_READER_CHECKPOINT_38.pdf');
    const portable=data.d30Public.files.find(row=>row.filename==='PROBABILITAS_TEORI_UKURAN_PROSES_STOKASTIK_ID_READER_CHECKPOINT_38.zip');
    assert.ok(pdf&&portable);assert.equal(capsule.layers.learner.pdf.sha256,pdf.sha256);assert.equal(capsule.layers.learner.pdf.bytes,pdf.bytes);
    assert.equal(capsule.layers.learner.portable_html.sha256,portable.sha256);assert.equal(capsule.layers.learner.portable_html.bytes,portable.bytes);
  }
  const integrated=['verified','legacy_verified'].includes(adapter.status);
  const publicRow=frozenPublished.get(role);
  const packet=publicRow?frozenPackages.get(publicRow.adapter_package_id):null;
  if(publicRow){
    assert.ok(packet,`${role}: published binding without a package`);
    assert.equal(packet.admission_state,'published');
    assert.equal(packet.public_replay_status,'published_public_asset_readback_verified');
    assert.equal(packet.native_family_id,family.native_family_id);
  }
  const centralTools=capsule.layers.learner.tools.map(tool=>({label:tool.label,href:'../'+tool.href}));
  if(clpRoles.includes(role))centralTools.push({label:`${role} · Rute baca keluarga CLP`,href:`../backend/clp/${role}.html`});
  const parityStatuses=[
    capsule.layers.curriculum.unit_identity_status,
    capsule.layers.translation.ledger_status,
    capsule.layers.translation.terminology_status,
    capsule.layers.translation.corrections_status,
    capsule.layers.production.build_status,
    capsule.layers.production.deterministic_replay_status,
    capsule.layers.learner.status,
    capsule.layers.educator.status,
    capsule.layers.educator.unit_alignment_status,
    capsule.layers.federation.status,
    adapter.status,
  ];
  const nativeCapabilityParityComplete=parityStatuses.every(status=>['verified','not_applicable'].includes(status));
  return {role_id:role,title:capsule.course.title,native_family_id:family.native_family_id,native_family_name:family.family_name,
    native_design_audit:{status:'historical_comparison_not_new_native_reaudit',pattern:family.core_pattern,recommended_reuse:family.recommended_reuse,limitations:family.limitations},
    common_adapter:{status:adapter.status,contract:adapter.contract_version??null,mapping_scope:adapter.mapping_scope,
      github_public_evidence:publicRow?'frozen_public_readback':role==='D50'?'new_anonymous_release_asset_readback':role==='B95'?'native_anonymous_release_asset_readback':role==='C140'?'native_anonymous_release_and_pages_readback':role==='D30'?'native_anonymous_source_and_pages_readback':role==='A30'?'new_anonymous_source_and_pages_readback':role==='A20'||role==='B40'||role==='B80'||role==='B90'||role==='C60'||role==='C70'||role==='C110'||role==='C120'||role==='D10'||role==='D40'||role==='D70'||role==='D80'||role==='D90'||role==='D100'||role==='D120'||leblRoles.includes(role)||['C90','C100'].includes(role)?'new_anonymous_source_and_pages_readback':'not_established',
      zenodo_preservation:publicRow?'frozen_public_readback':role==='D50'?'new_embedded_successor_readback':role==='B80'?'assigned_to_central_manager_not_yet_verified':'not_established',
      ...(gap?{admission:{status:'pass',receipt:{path:sources.gapAdmission,bytes:bytes.gapAdmission.length,sha256:sha256(bytes.gapAdmission)},package:gap.package,twin:gap.twin,spec:gap.spec,public_embedding:gapPublicEmbedding}}:{}),
      local_evidence:adapter.evidence??[],
      public_package:packet?{url:packet.public_asset_url,bytes:packet.archive.bytes,sha256:packet.archive.sha256,
        central_record:`https://doi.org/${data.published.snapshot.central_release_record_doi}`} : role==='D50'?{
        url:data.d50Publication.github.asset_url,bytes:data.d50Publication.adapter.bytes,sha256:data.d50Publication.adapter.sha256,
        central_record:`https://doi.org/${data.d50Publication.zenodo.doi}`,
        zenodo_container:data.d50Publication.zenodo.embedding.container_name,
        zenodo_member:data.d50Publication.zenodo.embedding.member_path}:null},
    learner:{tools:centralTools,
      unit_identity:capsule.layers.curriculum.unit_identity_status,
      relationship:clpRoles.includes(role)
        ?'central_view_consumes_verified_route_projection_pdf_runtime_adapter_consumption_not_claimed'
        :role==='A10' && capsule.layers.learner.tools.some(tool=>tool.tool_id==='a10.open_learner_hub')
          ?'central_navigator_consumes_native_metadata_projection_pdf_runtime_adapter_consumption_not_claimed'
        :['A20','A30','B40','B80','B90','B95','C60','C70','C110','C120','C140','D10','D30','D40','D70','D80','D90','D100','D120'].includes(role)||['lebl-learning-capability/1','geometry-learning-capability/1','topology-learning-capability/1'].includes(adapter.contract_version)
          ?'directly_consumes_adapter_outputs'
          :publicRow?.learner_runtime_relationship??'no_common_adapter_consumption_proven'},
    educator:{status:capsule.layers.educator.status,unit_alignment:capsule.layers.educator.unit_alignment_status,resources:capsule.layers.educator.resources},
    dimensions:{
      curriculum:{course_graph:capsule.layers.curriculum.status,unit_identity:capsule.layers.curriculum.unit_identity_status},
      source_translation_ledger:{ledger:capsule.layers.translation.ledger_status,corrections:capsule.layers.translation.corrections_status},
      terminology:{register:capsule.layers.translation.terminology_status},
      reproducible_production:{build:capsule.layers.production.build_status,replay:capsule.layers.production.deterministic_replay_status},
      accessibility:{semantic_html:capsule.layers.learner.capabilities.semantic_html,mathml:capsule.layers.learner.capabilities.mathml},
      learner:{delivery:capsule.layers.learner.status,central_tools:centralTools.length},
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
      ...(gap?['Paket adapter v2.3.1 telah dipertahankan dan dibaca kembali secara anonim dalam rilis pusat v0.63.24.']:[]),
      ...(role==='B80'?['Verifikasi pelestarian Zenodo yang ditangani pengelola pusat tanpa transaksi rilis yang bersaing.']:[]),
      'Selesaikan audit sembilan bidang kemampuan dan bukti penggunaannya; adapter yang lulus tidak otomatis berarti backend lengkap.'
    ],common_exchange_layer_completion:integrated?'verified':'not_yet_proven',
    native_capability_parity_completion:nativeCapabilityParityComplete?'verified':'not_yet_proven',
    // Matching layer flags do not prove the independent nine-dimension audit,
    // released consumer use, or public preservation required for completion.
    whole_course_backend_completion:role==='C140'?'selected_54_document_component_boundary_proven':'not_yet_proven'};
});
const integrated=rows.filter(row=>['verified','legacy_verified'].includes(row.common_adapter.status));
const commonExchangeLayerComplete=integrated.length===40&&new Set(integrated.map(row=>row.native_family_id)).size===33;
const nativeCapabilityParityVerifiedRoles=rows.filter(row=>row.native_capability_parity_completion==='verified').length;
const summary={roles:40,native_families:33,locally_validated_adapter_roles:integrated.length,
  locally_represented_families:new Set(integrated.map(row=>row.native_family_id)).size,
  roles_without_validated_common_adapter:40-integrated.length,
  github_evidenced_roles:rows.filter(row=>row.common_adapter.github_public_evidence!=='not_established').length,
  zenodo_evidenced_roles:rows.filter(row=>['frozen_public_readback','new_embedded_successor_readback'].includes(row.common_adapter.zenodo_preservation)).length,
  admitted_v231_roles:gapRoles.length,
  common_exchange_layer_complete:commonExchangeLayerComplete,
  native_capability_parity_verified_roles:nativeCapabilityParityVerifiedRoles,
  native_capability_parity_complete:nativeCapabilityParityVerifiedRoles===40,
  overall_program_backend_complete:commonExchangeLayerComplete&&nativeCapabilityParityVerifiedRoles===40&&rows.every(row=>row.whole_course_backend_completion==='verified')};
assert.equal(summary.locally_validated_adapter_roles+summary.roles_without_validated_common_adapter,40);
const model={schema:'program-backend-coverage/1',recorded_date:'2026-09-07',scope:'Backend integration, not textbook translation progress.',
  evidence_semantics:'Unknown means not proved by common-layer evidence, not absent native work. Common exchange-layer completion and native capability parity are reported separately. Frozen public readback is historical, not a fresh network recheck. A20 has an anonymous exact source-and-Pages readback over its integration commit. A30 has complete anonymous native GitHub/Zenodo release readback plus a central integration readback covering ten source/derived files and three changed Pages routes. A30, B95, and C140 adapter packets were preserved and anonymously read back in central v0.63.24. D30 is a direct locally validated zero-copy adapter whose GitHub evidence preserves the native repository, commit/tree, and anonymous reader readback; its central adapter publication is not inferred. D50 has a fresh exact GitHub release-asset readback and an exact adapter member inside the anonymously verified Zenodo successor navigator; it is not represented as a top-level Zenodo file.',
  evidence:Object.entries(sources).map(([key,path])=>({path,bytes:bytes[key].length,sha256:sha256(bytes[key])})),
  admission:{receipt:{path:sources.gapAdmission,bytes:bytes.gapAdmission.length,sha256:sha256(bytes.gapAdmission)},roles:gapRoles,public_embedding:gapPublicEmbedding},summary,roles:rows};
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const statuses={verified:'Diverifikasi',available_unverified:'Ada; belum diverifikasi',not_yet_produced:'Belum dibuat',unknown:'Belum terbukti',in_progress:'Dikerjakan'};
const dimensionNames={curriculum:'Kurikulum dan unit',source_translation_ledger:'Ledger sumber/penerjemahan',terminology:'Istilah',reproducible_production:'Produksi yang dapat diulang',accessibility:'Aksesibilitas',learner:'Pelajar',educator:'Pengajar',federation:'Federasi komponen',interoperability:'Pertukaran data'};
const details=row=>`<h3>Sembilan bidang kemampuan</h3><dl>${Object.entries(row.dimensions).map(([key,values])=>`<dt>${dimensionNames[key]}</dt><dd>${Object.entries(values).map(([name,value])=>`${esc(name)}: ${Array.isArray(value)?value.map(item=>`${esc(item.id)} — ${esc(statuses[item.status]??item.status)}`).join('; '):esc(statuses[value]??value??'Belum terbukti')}`).join('<br>')}</dd>`).join('')}</dl><h3>Pekerjaan tersisa</h3><ul>${row.next_required_work.map(text=>`<li>${esc(text)}</li>`).join('')}</ul><p>Lapisan pertukaran bersama: ${row.common_exchange_layer_completion==='verified'?'terverifikasi':'belum terbukti'}. Paritas kapabilitas native: ${row.native_capability_parity_completion==='verified'?'terverifikasi':'belum terbukti'}.</p>${row.common_adapter.public_package?`<p><a href="${esc(row.common_adapter.public_package.url)}">Paket adapter</a> · <a href="${esc(row.common_adapter.public_package.central_record)}">Rekaman pusat historis</a></p>`:''}<details><summary>Desain asli: temuan audit terdahulu</summary><p lang="en">${esc(row.native_design_audit.pattern)}</p><ul lang="en">${row.native_design_audit.recommended_reuse.map(text=>`<li>${esc(text)}</li>`).join('')}</ul><p>Temuan historis berikut harus diperiksa ulang sebelum dianggap masih berlaku:</p><ul lang="en">${row.native_design_audit.limitations.map(text=>`<li>${esc(text)}</li>`).join('')}</ul>${row.role_id==='B80'?'<p>Integrasi B80 sekarang menambahkan pertukaran reversibel serta tampilan pelajar/pengajar bersama.</p>':''}</details>`;
const htmlRows=rows.map(row=>`<tr id="role-${row.role_id}"><th scope="row"><a href="../id/#course-${row.role_id}">${row.role_id} · ${esc(row.title)}</a><small>${esc(row.native_family_name)}</small></th><td>${esc(statuses[row.common_adapter.status]??row.common_adapter.status)}<small>${esc(row.common_adapter.contract??'Belum ada kontrak bersama')}</small></td><td>${row.learner.tools.map(tool=>`<p><a href="${esc(tool.href)}">${esc(tool.label)}</a></p>`).join('')||'<span>Belum ada alat pusat terindeks</span>'}</td><td>${esc(statuses[row.educator.status]??row.educator.status)}${row.educator.resources.map(resource=>`<p><a href="${esc(resource.url)}">${esc(resource.title)}</a></p>`).join('')}</td><td><details><summary>Bukti dan pekerjaan berikutnya</summary>${details(row)}<p>Identitas unit: ${esc(statuses[row.learner.unit_identity]??row.learner.unit_identity)}. Keselarasan pengajar: ${esc(statuses[row.educator.unit_alignment]??row.educator.unit_alignment)}.</p><p>Zenodo: ${row.common_adapter.zenodo_preservation==='frozen_public_readback'?'readback rilis tercatat':row.common_adapter.zenodo_preservation==='new_embedded_successor_readback'?'adapter tersimpan sebagai anggota tepat dalam navigator penerus yang dibaca balik secara anonim':row.role_id==='B80'?'pelestarian ditugaskan; belum diverifikasi':'bukti adapter belum tersedia'}.</p></details></td></tr>`).join('\n');
const html=`<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Cakupan backend 40 peran</title><style>body{font:16px/1.5 system-ui;color:#183a35;background:#f5f5ed;margin:0}main{max-width:1400px;margin:auto;padding:28px}a{color:#086b63;text-underline-offset:3px}h1{font-size:2rem}small{display:block;color:#506660;margin-top:6px}.table{overflow:auto}table{border-collapse:collapse;width:100%;background:white}th,td{padding:14px;text-align:left;vertical-align:top;border-bottom:1px solid #cad6d0}thead{background:#e0eae3}th{min-width:220px}td{min-width:170px}p{max-width:90ch}details p{min-width:200px}dt{font-weight:650;margin-top:1rem}dd{margin-left:0}h3{font-size:1rem}a:focus-visible,summary:focus-visible{outline:3px solid #cf8728;outline-offset:3px}</style></head><body><main><nav><a href="index.html">Pusat belajar dan mengajar</a> · <a href="../id/">Program</a></nav><h1>Cakupan backend: 40 peran</h1><p>${summary.locally_validated_adapter_roles} peran mempunyai adapter bersama yang telah diuji; ${summary.roles_without_validated_common_adapter} belum. Ini <strong>bukan</strong> persentase penerjemahan buku, dan tidak berarti backend lengkap untuk semua peran yang sudah mempunyai adapter.</p><p>Readback GitHub tercatat untuk ${summary.github_evidenced_roles} peran; readback pelestarian Zenodo tercatat untuk ${summary.zenodo_evidenced_roles}. Increment A20, A30, CLP, B40, B80, B90, B95, Lebl, Geometry, Topology, C60, C70, C110, C120, D10, D30, D40, D70, D80, D90, D100, dan D120 sudah dapat dipakai di web; bukti pelestarian Zenodo tetap dihitung terpisah. Tanggal matriks: 7 September 2026. Temuan desain asli dan bukti rilis terdahulu bukan pemeriksaan ulang seluruh buku hari ini. “Belum terbukti” berarti bukti integrasi pusat belum cukup, bukan berarti pekerjaan asli tidak ada atau terjemahan belum selesai.</p><div class="table" role="region" aria-label="Cakupan semua peran" tabindex="0"><table><caption>Adapter, penggunaan oleh pelajar, dan bahan pengajar per peran</caption><thead><tr><th>Peran dan keluarga native</th><th>Adapter bersama</th><th>Alat pelajar</th><th>Bahan pengajar</th><th>Batas bukti</th></tr></thead><tbody>${htmlRows}</tbody></table></div><p><a href="program-backend-coverage.json">Matriks terbuka dengan identitas bukti</a></p></main></body></html>\n`;
for(const [path,content]of [['backend/course-capsule-v1/generated/program-backend-coverage-v1.json',json(model)],['docs/backend/program-backend-coverage.json',json(model)],['docs/backend/coverage.html',html]]){
  await mkdir(dirname(resolve(root,path)),{recursive:true});await writeFile(resolve(root,path),content);
}
console.log(JSON.stringify({state:'pass',...summary}));
