import assert from 'node:assert/strict';
import {readFile, writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';
import {learnerToolsByCourseId} from '../docs/learner-tools.js';

export const capabilityInput = 'docs/data/course-capsule-v1/course-capsules.json';
export const clpCapabilityInput = 'backend/course-capsule-v1/authority/clp-family-v231/learner-reader-actions-v1.json';
export const clpCapabilityValidationInput = 'docs/backend/clp/validation.json';
export const navigationOverlayInput = 'backend/authority/central-course-surface-navigation-overlay-v1.json';
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const contracts = {
  'b80-educator-map-v1':['B80','reference','backend/b80/B80-pengajar.html'],
  'b80-exercise-map-v1':['B80','practice_diagnostic_map','backend/b80/B80.html'],
  'c100-geometry-learning-map-v1':['C100','practice_diagnostic_map','backend/geometry/C100.html'],
  'c100-geometry-educator-map-v1':['C100','reference','backend/geometry/pengajar.html'],
  'c90-topology-course-map-v1':['C90','reference','backend/topology/C90.html'],
  'c70.open_learner_hub':['C70','course_reader','backend/c70/C70.html'],
  'c110.open_learner_hub':['C110','course_reader','backend/c110/C110.html'],
  'c120.open_learner_hub':['C120','course_reader','backend/c120/C120.html'],
  'd10.open_learner_hub':['D10','course_reader','backend/d10/D10.html'],
  'd40.open_learner_hub':['D40','course_reader','backend/d40/D40.html'],
  'd70.open_learner_hub':['D70','course_reader','backend/d70/D70.html'],
  'd80.open_learner_hub':['D80','course_reader','backend/d80/D80.html'],
  'd100.open_learner_hub':['D100','course_reader','backend/d100/D100.html'],
  'd120.open_learner_hub':['D120','course_reader','backend/d120/D120.html'],
};
for(const role of ['B70','C10','C20','C50']) for(const [suffix,kind,file] of [
  ['exercise-map','practice_diagnostic_map',role+'.html'],
  ['educator-map','reference',role+'-pengajar.html'],
  ['terminology','reference','istilah.html'],
]) contracts[role.toLowerCase()+'-lebl-'+suffix+'-v1']=[role,kind,'backend/lebl/'+file];
export function projectCapabilityTools(capsules, courseIds) {
  assert.equal(capsules.length, courseIds.length);
  assert.deepEqual(capsules.map(row=>row.course_id).sort(), [...courseIds].sort());
  const result = [], seen = new Set(), matchedLegacy = new Set();
  for (const capsule of capsules) for (const tool of capsule.layers.learner.tools ?? []) {
    assert.ok(!seen.has(tool.tool_id)); seen.add(tool.tool_id);
    const legacy = (learnerToolsByCourseId[capsule.course_id] ?? []).find(row=>row.tool_id===tool.tool_id);
    if (legacy) { assert.deepEqual(tool, legacy, 'Existing tool changed: '+tool.tool_id); matchedLegacy.add(tool.tool_id); continue; }
    // Explicit B80, Lebl, Geometry, Topology, C70, C110, C120, D10, D40, D70, D80, D100 and D120 presentation contracts; no generic auto-admission.
    const expected = contracts[tool.tool_id];
    assert.ok(expected); assert.deepEqual([capsule.course_id,tool.action_kind,tool.href],expected);
    assert.equal(capsule.locale, 'id-ID');
    assert.equal(tool.state, 'verified');
    assert.equal(tool.primary, false);
    assert.equal(tool.machine_data_is_learner_destination, false);
    assert.ok(tool.label && tool.scope && tool.limitations.length);
    assert.match(tool.href, /^backend\/[a-z0-9-]+\/[a-zA-Z0-9-]+\.html$/);
    assert.equal(tool.page.path, 'docs/'+tool.href);
    for (const fact of [tool.page, tool.resource, tool.evidence]) {
      assert.match(fact.path, /^docs\/backend\/[a-z0-9-]+\/[a-zA-Z0-9.-]+$/);
      assert.ok(!fact.path.includes('..'));
      assert.ok(Number.isSafeInteger(fact.bytes) && fact.bytes>0);
      assert.match(fact.sha256, /^[a-f0-9]{64}$/);
    }
    const contentLanguage = capsule.course_id === 'D100' ? 'en' : 'id';
    result.push({courseId:capsule.course_id, contentLanguage, ...tool});
  }
  assert.deepEqual([...matchedLegacy].sort(),Object.values(learnerToolsByCourseId).flat().map(t=>t.tool_id).sort());
  assert.deepEqual(result.map(t=>t.tool_id).sort(),Object.keys(contracts).sort());
  return result;
}
export function projectClpCapabilityTools(source, validation, courseIds) {
  assert.equal(source.schema_id, 'interlanguage/learner-reader-actions/v1');
  assert.equal(source.status, 'verified_route_evidence_projection');
  assert.deepEqual(source.summary, {
    action_count:7, bytes:35639691, chapter_or_unit_routes_claimed:false,
    course_count:4, native_html_claimed:false, pages:4077,
    route_granularity:'whole_file_only', verified_action_count:7,
  });
  assert.equal(validation.schema, 'clp-family-capability-validation/1');
  assert.equal(validation.state, 'pass');
  assert.deepEqual(validation.source, {
    path:clpCapabilityInput,
    bytes:Buffer.byteLength(JSON.stringify(source, null, 2) + '\n'),
    sha256:hash(Buffer.from(JSON.stringify(source, null, 2) + '\n')),
  });
  const expectedCourses=['B20','B30','B50','B60'];
  assert.ok(expectedCourses.every(courseId=>courseIds.includes(courseId)));
  const result=[];
  for(const courseId of expectedCourses){
    const actions=source.actions.filter(row=>row.course_id===courseId);
    assert.ok(actions.length>0);
    for(const action of actions){
      assert.equal(action.state,'verified');
      assert.equal(action.route_granularity,'whole_file_only');
      assert.equal(action.format,'application/pdf');
      assert.equal(action.license,'CC BY-NC-SA 4.0');
    }
    const pages=actions.reduce((sum,row)=>sum+row.pages,0);
    const files=actions.length;
    result.push({
      courseId, contentLanguage:'id', action_kind:'course_reader',
      evidence:null,
      href:`backend/clp/${courseId}.html`,
      label:`${courseId} · Rute baca keluarga CLP`,
      limitations:[
        'Tampilan hanya memproyeksikan rute PDF seluruh berkas yang telah diverifikasi.',
        'Jangkar bab atau unit dan pembaca HTML native tidak diklaim.',
        'Unduhan awal memerlukan jaringan; setiap PDF dapat dibaca luring setelah diunduh.',
        'Isi buku, identitas native, lisensi, dan bukti publik tetap berada pada edisi sumber.',
      ],
      machine_data_is_learner_destination:false,
      page:validation.outputs.course_entry_source_bodies[courseId],
      primary:false,
      resource:validation.outputs.learning_map,
      scope:`${files} PDF seluruh berkas, ${pages.toLocaleString('id-ID')} halaman; identitas byte, SHA-256, lisensi, dan rekaman publik dipertahankan`,
      state:'verified',
      tool_id:`${courseId.toLowerCase()}-clp-family-reader-routes-v1`,
    });
  }
  return result;
}
export async function syncCapabilityTools(root, courseIds) {
  const bytes = await readFile(resolve(root, capabilityInput));
  const clpBytes = await readFile(resolve(root, clpCapabilityInput));
  const clpValidationBytes = await readFile(resolve(root, clpCapabilityValidationInput));
  const clpValidation = JSON.parse(clpValidationBytes);
  const clpTools = projectClpCapabilityTools(JSON.parse(clpBytes), clpValidation, courseIds);
  const clpEvidence = {path:clpCapabilityValidationInput,bytes:clpValidationBytes.length,sha256:hash(clpValidationBytes)};
  for(const tool of clpTools) tool.evidence=clpEvidence;
  const tools = [...projectCapabilityTools(JSON.parse(bytes), courseIds), ...clpTools];
  const facts = [...new Map(tools.flatMap(t=>[t.page,t.resource,t.evidence]).map(f=>[f.path,f])).values()];
  const overlay = JSON.parse(await readFile(resolve(root,navigationOverlayInput),'utf8'));
  assert.equal(overlay.schema,'central-course-surface-navigation-overlay-v1');
  assert.equal(overlay.status,'pass');
  const overlayByPath = new Map(overlay.files.map(row=>[row.document,row]));
  for (const fact of facts) {
    const data = await readFile(resolve(root,fact.path));
    if (data.length===fact.bytes && hash(data)===fact.sha256) continue;
    // Course-capsule page facts bind the admitted semantic body. The central
    // navigation layer is an independently hash-bound, exactly reversible
    // presentation overlay. Accept a changed hosted HTML page only when the
    // overlay receipt binds both the original fact and the current bytes.
    const row=overlayByPath.get(fact.path);
    assert.ok(row, fact.path+' changed outside the central navigation overlay');
    assert.deepEqual(row.source_body,fact,fact.path+' source-body identity drift');
    assert.deepEqual(row.hosted_surface,{path:fact.path,bytes:data.length,sha256:hash(data)},fact.path+' hosted overlay identity drift');
    assert.equal(row.source_body_replay_exact,true,fact.path+' overlay is not reversible');
  }
  const source = {path:capabilityInput, bytes:bytes.length, sha256:hash(bytes)};
  const supplementSources = [{path:clpCapabilityInput,bytes:clpBytes.length,sha256:hash(clpBytes)}];
  await writeFile(resolve(root,'docs/interface/capability-tools.js'),
    '// Generated read-only projection of admitted native capabilities; not a backend admission.\n'
    + 'export const capabilityToolSource = '+JSON.stringify(source)+';\n'
    + 'export const capabilityToolSupplementSources = '+JSON.stringify(supplementSources)+';\n'
    + 'export const capabilityToolFiles = '+JSON.stringify(facts)+';\n'
    + 'export const capabilityTools = '+JSON.stringify(tools)+';\n');
  return facts;
}
