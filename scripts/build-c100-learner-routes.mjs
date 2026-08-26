import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const owner = resolve(project, '..', 'foundations-of-geometry-id');
const docs = resolve(project, 'docs');
const routeRoot = resolve(docs, 'id-ID', 'courses', 'C100');
const readerRoot = resolve(routeRoot, 'reader');
const pilotRoot = resolve(project, 'backend', 'v2.1', 'pilots', 'c100-geometry');
const sourceHtml = resolve(owner, 'accessible', 'id-ID', 'index.html');
const sourceStyle = resolve(owner, 'accessible', 'id-ID', 'style.css');
const sourceReceipt = resolve(owner, '00_control', 'ZENODO_PUBLICATION_COMPLETE_COURSE_OPEN_20260825.json');
const sourceSolutionPdf = resolve(owner, 'solutions', 'id-ID', 'output', 'pdf', 'SOLUSI_DAN_PENGUASAAN_ID_BAB01_20.pdf');
const solutionRoute = resolve(routeRoot, 'solutions', 'SOLUSI_DAN_PENGUASAAN_ID_BAB01_20.pdf');

const EXPECTED = {
  html: { bytes: 3994608, sha256: '1d3b49bc17a5956164d25b53ef6a2e79939a44f066fa87d84d00a66cca6da7ca' },
  style: { bytes: 5098, sha256: '553a606757f117c9edefb0c5c339d490fd55cefd9c10b40e4d60774c30e32887' },
  receipt: { bytes: 6883, sha256: '7217c1ca89d398447adc23e108fa40aa5ceef1622d605bdd48f2bf9518dc6a14' },
  solutions: { bytes: 2698925, sha256: '01b618884353905e5be06ac7c85249f2aa0b127687a7e93038f5b65d5fddcdc7' },
};
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const verify = (name, bytes) => {
  assert.equal(bytes.length, EXPECTED[name].bytes, `${name}: jumlah byte otoritas berubah.`);
  assert.equal(sha256(bytes), EXPECTED[name].sha256, `${name}: SHA-256 otoritas berubah.`);
};
const esc = (value) => String(value)
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')
  .replaceAll("'", '&#39;');
const writeText = async (path, value) => {
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, value, 'utf8');
};
const writeBytes = async (path, value) => {
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, value);
};

const readOwnerOrMaterialized = async (ownerPath, materializedPath) => {
  try {
    return await readFile(ownerPath);
  } catch (error) {
    if (error?.code !== 'ENOENT') throw error;
    return readFile(materializedPath);
  }
};
const [htmlBytes, styleBytes, solutionBytes, unitBytes, pilotManifestBytes] = await Promise.all([
  readOwnerOrMaterialized(sourceHtml, resolve(readerRoot, 'index.html')),
  readOwnerOrMaterialized(sourceStyle, resolve(readerRoot, 'style.css')),
  readOwnerOrMaterialized(sourceSolutionPdf, solutionRoute),
  readFile(resolve(pilotRoot, 'units.jsonl')),
  readFile(resolve(pilotRoot, 'manifest.json')),
]);
verify('html', htmlBytes);
verify('style', styleBytes);
verify('solutions', solutionBytes);
const pilotManifest = JSON.parse(pilotManifestBytes.toString('utf8'));
const receiptFact = pilotManifest.input_authority.find(({ role }) => role === 'complete_open_course_publication_receipt');
assert.deepEqual(
  receiptFact,
  {
    bytes: EXPECTED.receipt.bytes,
    locator: 'foundations-of-geometry-id/00_control/ZENODO_PUBLICATION_COMPLETE_COURSE_OPEN_20260825.json',
    locator_base: 'owner_root',
    role: 'complete_open_course_publication_receipt',
    sha256: EXPECTED.receipt.sha256,
  },
  'C100 pilot must bind the terminal complete-course publication receipt.',
);
try {
  const receiptBytes = await readFile(sourceReceipt);
  verify('receipt', receiptBytes);
  const receipt = JSON.parse(receiptBytes.toString('utf8'));
  assert.equal(receipt.published.record_id, 22102628);
  assert.equal(receipt.published.license, 'cc-by-sa-4.0');
  assert.equal(receipt.anonymous_file_count, 17);
  assert.equal(receipt.all_anonymous_file_requests_verified, true);
} catch (error) {
  if (error?.code !== 'ENOENT') throw error;
}

const units = unitBytes.toString('utf8').trimEnd().split('\n').map((line) => JSON.parse(line));
assert.equal(units.length, 939, 'C100 harus memiliki tepat 939 unit v2.1.');
assert.equal(new Set(units.map(({ stable_unit_id: id }) => id)).size, 939, 'ID unit C100 tidak unik.');
const topLevel = units.filter(({ stable_unit_id: id }) => /^o004\.petrunin\.(?:preface|ch\d{2})$/.test(id));
assert.equal(topLevel.length, 21, 'C100 harus memiliki Prakata dan 20 bab tingkat atas.');
const chapters = topLevel.filter(({ stable_unit_id: id }) => /\.ch\d{2}$/.test(id));
assert.equal(chapters.length, 20);

// Preserve the validated semantic reader byte-for-byte.  The landing and unit
// wrappers carry current completion/navigation context without rewriting it.
await writeBytes(resolve(readerRoot, 'index.html'), htmlBytes);
await writeBytes(resolve(readerRoot, 'style.css'), styleBytes);
await writeBytes(solutionRoute, solutionBytes);

const commonStyle = `
  :root{color-scheme:light;--ink:#19231f;--muted:#59645f;--paper:#fbfaf6;--accent:#7b3f18;--accent2:#176b5d;--line:#ded8cf}
  *{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.62 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
  main{max-width:1040px;margin:0 auto;padding:clamp(1.25rem,4vw,4rem) clamp(1rem,4vw,2rem)}nav{font-size:.95rem;margin-bottom:2rem}a{color:var(--accent2)}
  h1{font:700 clamp(2rem,5vw,3.7rem)/1.06 Georgia,serif;margin:.25rem 0 1rem;max-width:18ch}h2{margin-top:2.4rem;line-height:1.2}.lede{font-size:1.15rem;color:var(--muted);max-width:72ch}
  .actions{display:flex;flex-wrap:wrap;gap:.7rem;margin:1.5rem 0 2rem}.button{display:inline-block;border:1px solid var(--accent2);border-radius:999px;padding:.62rem 1rem;text-decoration:none;background:white}.button.primary{background:var(--accent2);color:white}.button.download{border-color:var(--accent)}
  .notice{border-left:4px solid var(--accent);background:#f5eee8;padding:.85rem 1rem;margin:1.6rem 0;max-width:78ch}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:.8rem;list-style:none;padding:0}.grid li{background:white;border:1px solid var(--line);border-radius:12px;padding:.85rem 1rem}.grid a{font-weight:700}.grid small{display:block;color:var(--muted);margin-top:.25rem}.meta{color:var(--muted);font-size:.92rem}
  @media(max-width:600px){.actions{display:grid}.button{text-align:center}}
`;

const chapterList = chapters.map((unit) => {
  const chapter = Number(unit.stable_unit_id.slice(-2));
  return `<li><a href="units/bab-${String(chapter).padStart(2, '0')}/">Bab ${String(chapter).padStart(2, '0')} — ${esc(unit.title)}</a><small>${esc(unit.stable_unit_id)}</small></li>`;
}).join('\n');

const courseHtml = `<!doctype html>
<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>C100 — Bidang Euklides dan Kerabatnya | Program Matematika Indonesia</title><meta name="description" content="Kursus geometri Bahasa Indonesia lengkap: pembaca HTML semantik, PDF, solusi, EPUB, dan pendamping enam unit."><link rel="canonical" href="https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/C100/"><style>${commonStyle}</style></head>
<body><main><nav aria-label="Jejak navigasi"><a href="../../../">Program Matematika Indonesia</a> › <span aria-current="page">C100</span></nav>
<p class="meta">C100 · Geometri &amp; Topologi · edisi publik lengkap</p><h1>Bidang Euklides dan Kerabatnya</h1>
<p class="lede">Sebuah pengantar geometri Euklides, netral, hiperbolik, afin, proyektif, sferis, dan konstruksi—dengan Prakata, 20 bab, 253 latihan induk, seluruh 32 subbagian latihan, 247 petunjuk, dan 253 solusi.</p>
<div class="actions"><a class="button primary" href="reader/">Mulai membaca HTML</a><a class="button download" href="https://zenodo.org/records/22102628/files/BIDANG_EUKLIDES_DAN_KERABATNYA_ID_SPINE_COMPLETE.pdf?download=1">Unduh PDF</a><a class="button download" href="solutions/SOLUSI_DAN_PENGUASAAN_ID_BAB01_20.pdf">Buka solusi utama</a><a class="button" href="https://doi.org/10.5281/zenodo.22102628">DOI / semua berkas</a></div>
<div class="notice"><strong>Batas lisensi:</strong> halaman ini hanya menyajikan kursus utama CC BY-SA 4.0 dan pendamping asli enam unit dalam lini yang sama. Workbook Clemens/Snapp yang berlisensi terpisah tidak disalin atau dicampurkan ke sini.</div>
<h2>Bab</h2><ul class="grid">${chapterList}</ul>
<h2>Berkas pendamping</h2><div class="actions"><a class="button" href="https://zenodo.org/records/22102628/files/TRANSFORMASI_INVARIAN_DAN_PERMUKAAN_MODEL_ID_UNIT006.pdf?download=1">Pendamping konektif 6 unit</a><a class="button" href="https://zenodo.org/records/22102628/files/SOLUSI_DAN_PENGUASAAN_PENDAMPING_ID_UNIT001_006.pdf?download=1">Solusi pendamping</a><a class="button" href="https://zenodo.org/records/22102628/files/BIDANG_EUKLIDES_DAN_KERABATNYA_ID_EPUB_CH01_CH20.epub?download=1">EPUB</a><a class="button" href="https://zenodo.org/records/22102628/files/BIDANG_EUKLIDES_DAN_KERABATNYA_ID_HTML_CH01_CH20.zip?download=1">HTML luring (ZIP)</a></div>
<p class="meta">Pembaca HTML pusat mempertahankan tepat 3.994.608 byte edisi semantik pemilik. Produksi edisi turunan dibantu OpenAI Codex gpt-5.6-sol, Ultra. Karya asli oleh Anton Petrunin; edisi ini tidak disahkan oleh penulis asli.</p>
</main></body></html>\n`;
await writeText(resolve(routeRoot, 'index.html'), courseHtml);

for (const unit of chapters) {
  const chapter = Number(unit.stable_unit_id.slice(-2));
  const slug = `bab-${String(chapter).padStart(2, '0')}`;
  const unitHtml = `<!doctype html>
<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Bab ${String(chapter).padStart(2, '0')} — ${esc(unit.title)} | Bidang Euklides dan Kerabatnya</title><meta name="description" content="Pintu masuk pelajar untuk ${esc(unit.title)}."><link rel="canonical" href="https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/C100/units/${slug}/"><style>${commonStyle}</style></head>
<body><main><nav aria-label="Jejak navigasi"><a href="../../../../../">Program Matematika Indonesia</a> › <a href="../../">C100 — Geometri</a> › <span aria-current="page">Bab ${String(chapter).padStart(2, '0')}</span></nav>
<p class="meta">${esc(unit.stable_unit_id)}</p><h1>Bab ${String(chapter).padStart(2, '0')}: ${esc(unit.title)}</h1><p class="lede">Buka langsung bab ini dalam pembaca HTML lengkap. Rumus disajikan sebagai MathML, petunjuk tertaut dari latihan, dan gambar memiliki uraian alternatif statis.</p>
<div class="actions"><a class="button primary" href="../../reader/#${esc(unit.stable_unit_id)}">Baca bab ini</a><a class="button download" href="https://zenodo.org/records/22102628/files/BIDANG_EUKLIDES_DAN_KERABATNYA_ID_SPINE_COMPLETE.pdf?download=1">PDF lengkap</a><a class="button download" href="../../solutions/SOLUSI_DAN_PENGUASAAN_ID_BAB01_20.pdf">Solusi</a></div><p><a href="../../">← Kembali ke daftar 20 bab</a></p>
</main></body></html>\n`;
  await writeText(resolve(routeRoot, 'units', slug, 'index.html'), unitHtml);
}

const chapterWrapperById = new Map(chapters.map((unit) => {
  const chapter = Number(unit.stable_unit_id.slice(-2));
  return [unit.stable_unit_id, `bab-${String(chapter).padStart(2, '0')}`];
}));
const routeManifest = {
  schema_id: 'program-matematika-indonesia/unit-route-v2.1/v1',
  recorded_at: '2026-08-26T00:00:00+02:00',
  course_id: 'C100',
  central_root: '/id-ID/courses/C100/',
  learner_start: '/id-ID/courses/C100/',
  reader: {
    url: 'https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/C100/reader/',
    source_html: EXPECTED.html,
    source_style: EXPECTED.style,
    solution_pdf: {
      ...EXPECTED.solutions,
      pages: 331,
      route_state: 'central_exact_owner_solution_pdf_materialized_course_level_fallback_no_named_destination',
      url: 'https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/C100/solutions/SOLUSI_DAN_PENGUASAAN_ID_BAB01_20.pdf',
    },
    rights: 'CC BY-SA 4.0',
    owner_version_doi: '10.5281/zenodo.22102628',
  },
  units: units.map((unit) => {
    const wrapper = chapterWrapperById.get(unit.stable_unit_id);
    const nativeLearnerUrl = unit.learner_route.url;
    return {
      id: unit.stable_unit_id,
      kind: unit.native_unit_kind,
      order_key: unit.order_key,
      title: unit.title,
      central_url: wrapper
        ? `https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/C100/units/${wrapper}/`
        : nativeLearnerUrl,
      native_html_url: unit.native_unit_kind === 'independent_solution' ? null : nativeLearnerUrl,
      native_learner_url: nativeLearnerUrl,
      route_state: unit.learner_route.route_state,
    };
  }),
};
await writeText(resolve(docs, 'data', 'unit-route-C100-v2.1.json'), `${JSON.stringify(routeManifest, null, 2)}\n`);
console.log(JSON.stringify({ result: 'pass', course: 'C100', units: units.length, chapter_wrappers: chapters.length, reader_html_sha256: EXPECTED.html.sha256, solution_pdf_sha256: EXPECTED.solutions.sha256 }));
