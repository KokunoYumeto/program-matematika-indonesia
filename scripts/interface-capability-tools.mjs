import assert from 'node:assert/strict';
import {readFile, writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';
import {learnerToolsByCourseId} from '../docs/learner-tools.js';

export const capabilityInput = 'docs/data/course-capsule-v1/course-capsules.json';
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
export function projectCapabilityTools(capsules, courseIds) {
  assert.equal(capsules.length, courseIds.length);
  assert.deepEqual(capsules.map(row=>row.course_id).sort(), [...courseIds].sort());
  const result = [], seen = new Set(), matchedLegacy = new Set();
  for (const capsule of capsules) for (const tool of capsule.layers.learner.tools ?? []) {
    assert.ok(!seen.has(tool.tool_id)); seen.add(tool.tool_id);
    const legacy = (learnerToolsByCourseId[capsule.course_id] ?? []).find(row=>row.tool_id===tool.tool_id);
    if (legacy) { assert.deepEqual(tool, legacy, 'Existing tool changed: '+tool.tool_id); matchedLegacy.add(tool.tool_id); continue; }
    // This release accepts only the audit's frozen B80 addition. New capability
    // families need their own explicit presentation contract, not auto-admission.
    assert.equal(capsule.course_id, 'B80');
    const expected = {'b80-educator-map-v1':['reference','backend/b80/B80-pengajar.html'], 'b80-exercise-map-v1':['practice_diagnostic_map','backend/b80/B80.html']}[tool.tool_id];
    assert.ok(expected); assert.deepEqual([tool.action_kind,tool.href],expected);
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
    result.push({courseId:capsule.course_id, contentLanguage:'id', ...tool});
  }
  assert.deepEqual([...matchedLegacy].sort(),Object.values(learnerToolsByCourseId).flat().map(t=>t.tool_id).sort());
  assert.deepEqual(result.map(t=>t.tool_id).sort(),['b80-educator-map-v1','b80-exercise-map-v1']);
  return result;
}
export async function syncCapabilityTools(root, courseIds) {
  const bytes = await readFile(resolve(root, capabilityInput));
  const tools = projectCapabilityTools(JSON.parse(bytes), courseIds);
  const facts = [...new Map(tools.flatMap(t=>[t.page,t.resource,t.evidence]).map(f=>[f.path,f])).values()];
  for (const fact of facts) {
    const data = await readFile(resolve(root,fact.path));
    assert.equal(data.length,fact.bytes,fact.path); assert.equal(hash(data),fact.sha256,fact.path);
  }
  const source = {path:capabilityInput, bytes:bytes.length, sha256:hash(bytes)};
  await writeFile(resolve(root,'docs/interface/capability-tools.js'),
    '// Generated read-only projection of admitted native capabilities; not a backend admission.\n'
    + 'export const capabilityToolSource = '+JSON.stringify(source)+';\n'
    + 'export const capabilityToolFiles = '+JSON.stringify(facts)+';\n'
    + 'export const capabilityTools = '+JSON.stringify(tools)+';\n');
  return facts;
}
