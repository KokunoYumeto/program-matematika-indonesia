import assert from 'node:assert/strict';
import {readFile, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';

const start = '<!-- CURRENT-BACKEND-COVERAGE:START -->';
const end = '<!-- CURRENT-BACKEND-COVERAGE:END -->';
export function coverageCounts(model) {
  assert.equal(model.schema, 'program-backend-coverage/1');
  const rows = model.roles;
  assert.ok(Array.isArray(rows) && rows.length > 0, 'Missing course coverage');
  assert.equal(new Set(rows.map(r => r.role_id)).size, rows.length, 'Duplicate course role');
  const verified = rows.filter(r => r.common_adapter?.status === 'verified');
  const result = {
    roles: rows.length,
    native_families: new Set(rows.map(r => r.native_family_id)).size,
    locally_validated_adapter_roles: verified.length,
    locally_represented_families: new Set(verified.map(r => r.native_family_id)).size,
    native_capability_parity_verified_roles: rows.filter(r => r.native_capability_parity_completion === 'verified').length,
    roles_without_validated_common_adapter: rows.length - verified.length,
  };
  for (const [key, count] of Object.entries(result)) {
    assert.ok(Number.isSafeInteger(count) && count >= 0);
    assert.equal(model.summary[key], count, `Coverage summary differs from role evidence: ${key}`);
  }
  return result;
}

export function renderCoverageOverview(html, model) {
  const c = coverageCounts(model);
  assert.equal(html.split(start).length, 2, 'Missing or repeated overview start');
  assert.equal(html.split(end).length, 2, 'Missing or repeated overview end');
  assert.ok(html.indexOf(start) < html.indexOf(end), 'Reversed overview markers');
  const card = `<article id="current-backend-coverage"><h3>Cakupan integrasi saat ini</h3><p>${c.locally_validated_adapter_roles} dari ${c.roles} peran kurikulum mempunyai adapter bersama yang tervalidasi, mencakup ${c.locally_represented_families} dari ${c.native_families} keluarga sumber. Sebanyak ${c.roles_without_validated_common_adapter} peran belum mempunyai adapter tervalidasi.</p><p>Kesetaraan kemampuan backend asli tercatat terverifikasi untuk ${c.native_capability_parity_verified_roles} dari ${c.roles} peran. Adapter yang lulus bukan bukti bahwa seluruh backend, penerjemahan, bahan pengajar, atau edisi Inggris telah selesai. Angka ini dihitung dari matriks bukti, bukan dari snapshot rilis historis.</p><p><a href="coverage.html">Periksa bukti dan pekerjaan tersisa per mata kuliah</a> · <a href="program-backend-coverage.json">Matriks sumber angka</a></p></article>`;
  return html.slice(0, html.indexOf(start) + start.length) + '\n        ' + card + '\n        ' + html.slice(html.indexOf(end));
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
  const model = JSON.parse(await readFile(resolve(root, 'backend/course-capsule-v1/generated/program-backend-coverage-v1.json')));
  const path = resolve(root, 'docs/backend/index.html');
  const original = await readFile(path, 'utf8');
  const generated = renderCoverageOverview(original, model);
  if (process.argv.includes('--check')) assert.equal(original, generated, 'Backend overview is stale');
  else await writeFile(path, generated);
  console.log(JSON.stringify({state:'pass', ...coverageCounts(model)}));
}
