import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile} from 'node:fs/promises';
import {resolve} from 'node:path';

export const c120DeliveryBase = 'backend/course-capsule-v1/adapters/c120-delivery-v1';
const mapPath = 'backend/course-capsule-v1/adapters/c120-capability-v1/data/learning-map.json';
export const c120DeliveryInputs = [
  `${c120DeliveryBase}/input-manifest.json`, `${c120DeliveryBase}/published-tree.json`,
  `${c120DeliveryBase}/deployed-readback.json`, `${c120DeliveryBase}/deployed-structural-audit.json`, mapPath,
  `${c120DeliveryBase}/deployment-replay.json`,
];
const identity = bytes => ({bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex')});

export function validateC120Delivery(data) {
  const [manifest, tree, receipt, structural, learning, replay] = data.values;
  const sameIdentity = (actual, expected) => assert.deepEqual(actual, identity(expected));
  assert.equal(manifest.schema, 'c120-delivery-input/1');
  assert.equal(manifest.course_id, 'C120');
  assert.equal(receipt.schema, 'c120-delivery-deployed-readback/1');
  assert.equal(receipt.state, 'pass');
  assert.equal(receipt.anonymous, true);
  assert.equal(receipt.ambient_credentials_disabled, true);
  assert.deepEqual(receipt.remaining, []);
  assert.deepEqual(receipt.failures, []);
  assert.equal(receipt.commit, 'cf1f7b2d7374818d2f0f48c899addc7c83db3083');
  assert.equal(receipt.tree, '5c568732d20a6d21813c2d0afa2a3377b334a8f0');
  assert.equal(tree.commit, receipt.commit);
  assert.equal(tree.tree, receipt.tree);
  sameIdentity(receipt.input_manifest, data.bytes[0]);
  sameIdentity(receipt.published_tree, data.bytes[1]);
  sameIdentity(receipt.structural_audit, data.bytes[3]);
  sameIdentity(receipt.deployment_replay, data.bytes[5]);
  assert.equal(replay.state, 'pass');
  assert.equal(replay.commit, receipt.commit);
  assert.equal(replay.tree, receipt.tree);
  assert.deepEqual(replay.sources, receipt.deployment_sources);
  assert.equal(replay.sources.length, 4);
  for (const row of replay.sources) {
    const bytes = data.deployment[row.path];
    assert.ok(bytes, 'Missing inspected native deployment source');
    sameIdentity({bytes: row.bytes, sha256: row.sha256}, bytes);
    const gitBlob = createHash('sha1').update(Buffer.from(`blob ${bytes.length}\0`)).update(bytes).digest('hex');
    assert.equal(row.git_blob, gitBlob);
  }
  assert.equal(manifest.learning_map.path, mapPath);
  sameIdentity({bytes: manifest.learning_map.bytes, sha256: manifest.learning_map.sha256}, data.bytes[4]);
  for (const rows of [manifest.files, tree.files, receipt.files]) {
    assert.equal(rows.length, 253);
    assert.equal(new Set(rows.map(r => r.path)).size, 253, 'Duplicate file identity');
  }
  const native = new Map(tree.files.map(r => [r.path, r]));
  const files = new Map(receipt.files.map(r => [r.path, r]));
  for (const row of manifest.files) {
    const live = files.get(row.path), source = native.get(row.native_path);
    assert.ok(live && source, 'Missing delivery evidence');
    assert.equal(live.url, manifest.reader + row.path);
    assert.equal(live.status, 200);
    assert.equal(live.git_blob, source.sha);
    const transformation = replay.transformations.find(t => t.path === row.path);
    if (transformation) {
      assert.equal(transformation.source_git_blob, source.sha);
      assert.equal(transformation.source.bytes, source.size);
      assert.deepEqual(transformation.deployed, {bytes: live.bytes, sha256: live.sha256});
      assert.equal(transformation.transform, row.path.endsWith('.html') ? 'native_navigation_injection' : 'native_manifest_reseal');
      assert.equal(live.deployment_transform, transformation.transform);
    } else {
      assert.equal(live.bytes, source.size);
    }
    assert.match(live.sha256, /^[a-f0-9]{64}$/);
    assert.ok(['exact_bytes', 'line_endings_only', 'published_source_version', 'same_main_dom_native_deployment_replay'].includes(live.local_relation), `Unresolved native/public delta: ${row.path}`);
    if (live.local_relation === 'exact_bytes') {
      assert.equal(live.sha256, row.sha256);
      assert.equal(live.bytes, row.bytes);
    }
  }
  assert.equal(receipt.verified_bytes, receipt.files.reduce((sum, row) => sum + row.bytes, 0));
  assert.equal(replay.transformations.length, 53);
  assert.equal(new Set(replay.transformations.map(r => r.path)).size, 53);
  assert.equal(replay.transformations.filter(r => r.transform === 'native_navigation_injection').length, 27);
  assert.equal(replay.transformations.filter(r => r.transform === 'native_manifest_reseal').length, 26);
  assert.equal(structural.state, 'pass');
  assert.deepEqual(structural.findings, []);
  assert.deepEqual(structural.external_runtime_resources, []);
  assert.equal(structural.commit, receipt.commit);
  assert.equal(structural.tree, receipt.tree);
  assert.deepEqual(structural.unit_ids, learning.route.unit_ids);
  assert.equal(structural.unit_count, 26);
  assert.equal(structural.html_count, 27);
  assert.equal(structural.mathml_count, 6283);
  assert.equal(structural.image_count, 51);
  assert.equal(structural.pages.length, 27);
  assert.equal(structural.print_css_paths.length, 26);
  const html = new Set(receipt.files.filter(r => r.path.endsWith('.html')).map(r => r.path));
  assert.equal(html.size, 27);
  for (const page of structural.pages) {
    assert.ok(html.has(page.path));
    assert.equal(page.lang, 'id-ID');
    assert.equal(page.main, 1);
    assert.equal(page.h1, 1);
  }
  assert.equal(structural.html_comparisons.length, 27);
  assert.equal(new Set(structural.html_comparisons.map(r => r.path)).size, 27);
  for (const row of structural.html_comparisons) {
    assert.equal(row.main_dom_equal, true);
    const live = files.get(row.path);
    assert.deepEqual(row.published, {bytes: live.bytes, sha256: live.sha256});
  }
  return {files, manifest, receipt, structural};
}

export async function loadC120Delivery(root) {
  const bytes = [];
  for (const path of c120DeliveryInputs) bytes.push(await readFile(resolve(root, path)));
  const data = {bytes, values: bytes.map(b => JSON.parse(b)), deployment: {}};
  for (const row of data.values[5].sources) data.deployment[row.path] = await readFile(resolve(root, c120DeliveryBase, 'deployment', row.path));
  return {...validateC120Delivery(data), data};
}

export function validateC120DeliveryOverride(override, evidence) {
  assert.ok(override, 'Missing C120 delivery admission');
  const {files, manifest} = evidence;
  for (const [key, path] of [['primary', 'index.html'], ['online_html', 'index.html'],
    ['pdf', 'Pengantar_Pemodelan_Matematika_Edisi_Bahasa_Indonesia_Lengkap.pdf']]) {
    const actual = override[key], expected = files.get(path);
    assert.equal(actual.status, 'verified');
    assert.equal(actual.bytes, expected.bytes);
    assert.equal(actual.sha256, expected.sha256);
    assert.equal(actual.url, path === 'index.html' ? manifest.reader : manifest.reader + path);
    assert.equal(actual.evidence.kind, 'anonymous_public_readback_and_native_deployment_replay');
  }
  for (const key of ['semantic_html', 'mathml', 'print_profile']) {
    assert.equal(override.capabilities[key].status, 'verified');
    assert.equal(override.capabilities[key].evidence.kind, 'anonymous_public_readback_and_native_deployment_replay');
  }
  assert.notEqual(override.portable_html?.status, 'verified', 'A source archive is not a verified offline reader');
  assert.notEqual(override.epub?.status, 'verified', 'No EPUB evidence');
}
