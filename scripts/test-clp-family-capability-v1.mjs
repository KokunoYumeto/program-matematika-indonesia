import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import { dirname, join, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const temporaryParent = resolve(tmpdir());
const temporaryRoot = await mkdtemp(join(temporaryParent, 'clp-family-capability-'));
assert.ok(temporaryRoot.startsWith(temporaryParent + sep));
const courseIds = ['B20', 'B30', 'B50', 'B60'];
const htmlFiles = ['docs/backend/clp/CLP.html', ...courseIds.map((courseId) => `docs/backend/clp/${courseId}.html`)];
const outputFiles = [...htmlFiles, 'docs/backend/clp/learning-map.json', 'docs/backend/clp/validation.json'];
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const run = (root) => {
  const result = spawnSync(process.execPath, [resolve(project, 'scripts/build-clp-family-capability-v1.mjs'), '--output-root=' + root], { cwd: project, encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
};

try {
  const left = resolve(temporaryRoot, 'left');
  const right = resolve(temporaryRoot, 'right');
  run(left); run(right);
  for (const path of outputFiles) assert.deepEqual(await readFile(resolve(left, path)), await readFile(resolve(right, path)), path + ' is not deterministic');
  const modelPath = 'docs/backend/clp/learning-map.json';
  const validationPath = 'docs/backend/clp/validation.json';
  const modelBytes = await readFile(resolve(left, modelPath));
  const validationBytes = await readFile(resolve(left, validationPath));
  const model = JSON.parse(modelBytes);
  const validation = JSON.parse(validationBytes);
  assert.equal(model.schema, 'clp-family-learner-capability/1');
  assert.equal(model.status, 'verified-presentation-projection');
  assert.deepEqual(model.courses.map((row) => row.course_id), ['B20', 'B30', 'B50', 'B60']);
  assert.equal(model.courses.flatMap((row) => row.actions).length, 7);
  assert.equal(model.courses.reduce((sum, row) => sum + row.pages, 0), 4077);
  assert.equal(model.courses.reduce((sum, row) => sum + row.bytes, 0), 35639691);
  assert.equal(model.shared_adapter.counted_packages, 1);
  assert.equal(model.shared_adapter.archive.bytes, 545418367);
  assert.equal(model.shared_adapter.archive.sha256, 'f2e2714c5f1349092e8cb574d6495e604086c9df3bc4bdf5bbe5974b5f61360d');
  assert.equal(model.shared_adapter.owner_native_authoritative, true);
  assert.equal(validation.state, 'pass');
  assert.equal(validation.outputs.learning_map.bytes, modelBytes.length);
  assert.equal(validation.outputs.learning_map.sha256, sha256(modelBytes));
  const canonicalModel = await readFile(resolve(project, modelPath));
  const canonicalValidation = await readFile(resolve(project, validationPath));
  assert.deepEqual(canonicalModel, modelBytes);
  assert.deepEqual(canonicalValidation, validationBytes);
  const overlay = JSON.parse(await readFile(resolve(project, 'backend/authority/central-course-surface-navigation-overlay-v1.json')));
  for(const path of htmlFiles){
    const sourceHtml=await readFile(resolve(left,path));
    const canonicalHtml=await readFile(resolve(project,path));
    const courseId=/\/(B[2356]0)\.html$/u.exec(path)?.[1];
    const sourceFact=courseId ? validation.outputs.course_entry_source_bodies[courseId] : validation.outputs.family_index_source_body;
    assert.equal(sourceFact.bytes,sourceHtml.length); assert.equal(sourceFact.sha256,sha256(sourceHtml));
    if(!canonicalHtml.equals(sourceHtml)){
      const row=overlay.files.find(item=>item.document===path);
      assert.ok(row,path+' changed outside the reversible central navigation overlay');
      assert.deepEqual(row.source_body,sourceFact);
      assert.deepEqual(row.hosted_surface,{path,bytes:canonicalHtml.length,sha256:sha256(canonicalHtml)});
      assert.equal(row.source_body_replay_exact,true);
    }
  }
  const html = (await readFile(resolve(left, 'docs/backend/clp/CLP.html'))).toString('utf8');
  for (const course of model.courses) {
    assert.ok(html.includes(`id="course-${course.course_id}"`));
    assert.ok(html.includes(`${course.course_id}.html`));
    assert.ok(html.includes(course.authoritative_original.url.replaceAll('&', '&amp;')));
    assert.equal(course.authoritative_original.content_language, 'en');
    for (const action of course.actions) {
      assert.ok(html.includes(action.url.replaceAll('&', '&amp;')));
      assert.ok(html.includes(action.sha256));
    }
  }
  assert.ok(html.includes(model.shared_adapter.public_asset_url));
  assert.ok(html.includes('satu paket adapter bersama—bukan empat salinan'));
  for(const courseId of courseIds){
    const entry=(await readFile(resolve(left,`docs/backend/clp/${courseId}.html`))).toString('utf8');
    assert.ok(entry.includes(`id="course-${courseId}"`));
    assert.ok(entry.includes('data-authoritative-original'));
    for(const other of courseIds.filter(id=>id!==courseId)) assert.ok(!entry.includes(`id="course-${other}"`));
  }
  assert.ok(html.includes('tidak mengklaim pembaca HTML native'));
  console.log(JSON.stringify({ state: 'pass', deterministic_builds: 2, courses: 4, actions: 7, pages: 4077 }));
} finally {
  assert.ok(temporaryRoot.startsWith(temporaryParent + sep));
  await rm(temporaryRoot, { recursive: true, force: true });
}
