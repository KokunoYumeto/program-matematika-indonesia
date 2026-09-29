import assert from 'node:assert/strict';
import {readFile, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadC120Delivery} from './c120-delivery-evidence-v1.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const {manifest, files, receipt} = await loadC120Delivery(root);
const path = resolve(root, 'backend/authority/learner-delivery-overrides-v1.json');
const overrides = JSON.parse(await readFile(path, 'utf8'));
const other = Object.fromEntries(Object.entries(overrides.courses).filter(([key]) => key !== 'C120'));
const note = 'Pembaca publik 26 unit diperiksa terhadap commit native dan transformasi navigasi deployment; isi main HTML sama dengan saksi lokal. Ini bukan sertifikasi WCAG atau peninjauan baru mutu terjemahan.';
const evidence = {
  kind: 'anonymous_public_readback_and_native_deployment_replay',
  locator: 'https://github.com/KokunoYumeto/program-matematika-indonesia/blob/main/backend/course-capsule-v1/adapters/c120-delivery-v1/deployed-readback.json',
  verified_date: receipt.finished_at.slice(0, 10), note,
};
const resource = (key, format, url) => {
  const row = files.get(key);
  assert.ok(row);
  return {status: 'verified', format, url, bytes: row.bytes, sha256: row.sha256, scope: 'whole_course', evidence};
};
const html = resource('index.html', 'text/html', manifest.reader);
const pdfName = 'Pengantar_Pemodelan_Matematika_Edisi_Bahasa_Indonesia_Lengkap.pdf';
const previous = overrides.courses.C120 ?? {};
overrides.courses.C120 = {
  ...previous,
  primary: html,
  online_html: html,
  pdf: resource(pdfName, 'application/pdf', manifest.reader + pdfName),
  capabilities: {
    ...(previous.capabilities ?? {}),
    semantic_html: {status: 'verified', evidence},
    mathml: {status: 'verified', evidence: {...evidence, note: 'Sebanyak 6.283 elemen MathML mempertahankan anotasi sumber TeX; tampilan matematika dan pembukaan pembahasan diuji pada bab pendulum. Tidak mengklaim uji semua pembaca layar.'}},
    print_profile: {status: 'verified', evidence: {...evidence, note: 'CSS cetak tersedia pada 26 unit; PDF lengkap sesuai byte edisi native. Tidak mengklaim audit visual baru semua halaman cetak.'}},
  },
};
assert.deepEqual(Object.fromEntries(Object.entries(overrides.courses).filter(([key]) => key !== 'C120')), other);
await writeFile(path, JSON.stringify(overrides, null, 2) + '\n');
console.log(JSON.stringify({state: 'pass', role: 'C120', public_files: files.size, native_books_changed: false, other_roles_unchanged: true}));
