import assert from 'node:assert/strict';
import {readFile, writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';

export const finalEditionInput = 'docs/interface/final-editions.json';
const exactKeys = (value, keys) => assert.deepEqual(Object.keys(value).sort(), [...keys].sort());
export function validateFinalEditions(input, courseIds) {
  assert.equal(input.schema, 'learner-interface-final-editions/v1');
  assert.equal(input.scope, 'presentation-only');
  assert.equal(input.anonymous_readback, true);
  assert.match(input.verified_at_utc, /^\d{4}-\d{2}-\d{2}T/);
  const ids = new Set(), resourceIds = new Set();
  for (const edition of input.editions) {
    exactKeys(edition, ['courseId','version','archive','repository','supersededSupplementIds','resources']);
    assert.ok(courseIds.includes(edition.courseId) && !ids.has(edition.courseId));
    ids.add(edition.courseId);
    assert.ok(edition.version);
    assert.match(edition.archive, /^https:\/\/doi\.org\/10\.5281\/zenodo\.\d+$/);
    assert.match(edition.repository, /^https:\/\/github\.com\/[\w-]+\/[\w.-]+$/);
    assert.equal(new Set(edition.supersededSupplementIds).size, edition.supersededSupplementIds.length);
    assert.equal(edition.resources.filter(r=>r.primary).length, 1);
    const urls = new Set();
    for (const row of edition.resources) {
      exactKeys(row, ['id','href','labels','contentLanguage','kind','format','primary','offlineAfterDownload','pages','bytes','sha256','evidence']);
      assert.ok(!resourceIds.has(row.id)); resourceIds.add(row.id);
      assert.ok(row.id.startsWith(edition.courseId + ':'));
      const url = new URL(row.href);
      assert.equal(url.protocol, 'https:'); assert.ok(!url.username && !url.password && !url.hash);
      assert.ok(['zenodo.org','kokunoyumeto.github.io'].includes(url.hostname));
      assert.ok(!urls.has(row.href)); urls.add(row.href);
      assert.equal(row.contentLanguage, 'id');
      assert.ok(row.labels.id && row.labels.en); exactKeys(row.labels,['id','en']);
      assert.ok(['reader','companion','portable_html'].includes(row.kind));
      assert.ok(['PDF','HTML','HTML ZIP'].includes(row.format));
      assert.equal(typeof row.primary, 'boolean');
      assert.equal(typeof row.offlineAfterDownload, 'boolean');
      assert.ok(Number.isSafeInteger(row.bytes) && row.bytes > 0);
      assert.match(row.sha256, /^[a-f0-9]{64}$/);
      assert.ok(row.pages === null || (row.format === 'PDF' && Number.isSafeInteger(row.pages) && row.pages > 0));
      assert.equal(row.evidence.anonymous_http_status,200);
      assert.equal(row.evidence.actual_sha256,row.sha256);
      assert.match(row.evidence.source_receipt_sha256,/^[a-f0-9]{64}$/);
      assert.ok(!/^(?:[A-Za-z]:|\/)|\.\./.test(row.evidence.source_receipt));
    }
  }
  return input.editions;
}
export async function syncFinalEditions(root, courseIds) {
  const bytes = await readFile(resolve(root, finalEditionInput));
  const editions = validateFinalEditions(JSON.parse(bytes), courseIds);
  const source = {path:finalEditionInput,bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex')};
  await writeFile(resolve(root,'docs/interface/final-editions.js'),
    '// Generated presentation bindings; corpus/backend authority remains unchanged.\n'
    + 'export const finalEditionSource = ' + JSON.stringify(source) + ';\n'
    + 'export const finalEditions = ' + JSON.stringify(editions,null,2) + ';\n');
}
