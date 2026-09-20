import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

export const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
export const base = 'backend/course-capsule-v1/adapters/d60-surface-v1';
export const sha256 = b => createHash('sha256').update(b).digest('hex');
export const json = value => JSON.stringify(value, null, 2) + '\n';
const esc = value => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const tableBase = 'backend/v2.3/extensions/d60-algebraic-topology-v0.1.0/tables';
const practiceKinds = new Set(['exercise', 'question', 'proof_check']);

export async function loadInputs() {
  const witnessBytes = await readFile(resolve(project, base, 'reader-witness.json'));
  const witness = JSON.parse(witnessBytes);
  assert.equal(witness.schema, 'd60-reader-witness/1');
  const buffers = {};
  for (const item of witness.inputs) {
    assert.ok(item.path.startsWith('backend/v2.3/'));
    const bytes = await readFile(resolve(project, item.path));
    assert.equal(bytes.length, item.bytes, `Input size: ${item.path}`);
    assert.equal(sha256(bytes), item.sha256, `Input hash: ${item.path}`);
    buffers[item.path] = bytes;
  }
  const rows = name => buffers[`${tableBase}/${name}.jsonl`].toString('utf8').trim().split('\n').map(JSON.parse);
  return {witness, units: rows('units'), relations: rows('relations'), witnessIdentity: {path: `${base}/reader-witness.json`, bytes: witnessBytes.length, sha256: sha256(witnessBytes)}};
}

export function projectMap({witness, units, relations, witnessIdentity}) {
  assert.equal(witness.reader.language, 'id-ID');
  assert.ok(witness.reader.url.startsWith('https://kokunoyumeto.github.io/algebraic-topology-id/'));
  const ids = new Set(units.map(u => u.id));
  const nativeIds = new Set(units.map(u => u.payload.native_unit_id));
  assert.equal(ids.size, units.length, 'Duplicate projected ID');
  assert.equal(nativeIds.size, units.length, 'Duplicate native ID');
  const routes = new Map(witness.unit_routes.map(r => [r.id, r]));
  assert.equal(routes.size, witness.unit_routes.length, 'Duplicate witness ID');
  assert.equal(routes.size, units.length, 'Witness coverage');
  const result = units.map(({id, payload: p}) => {
    const w = routes.get(p.native_unit_id);
    assert.ok(w, `Missing witness ${p.native_unit_id}`);
    assert.ok(Number.isInteger(w.occurrences) && w.occurrences >= 0);
    assert.ok(!w.anchor || /^[a-zA-Z0-9_.:-]+$/.test(w.anchor), 'Unsafe anchor');
    assert.equal(p.title_locale, 'id-ID');
    const exact = w.occurrences === 1;
    return {
      id: p.native_unit_id, projected_id: id, title: p.title, kind: p.native_unit_kind,
      order: p.native_order, group: p.native_path[0] ?? p.native_unit_id,
      parent_id: p.parent_native_unit_id, native_path: p.native_path,
      concept_ids: p.native_concept_ids, route_unit_ids: p.route_unit_ids,
      edition_id: p.native_edition_id, resource_id: p.native_resource_id,
      rights_ids: p.current_rights_native_ids, provenance_relation: p.provenance_relation,
      translation_state: p.translation_state, source_locator: p.target_locator,
      locale: p.title_locale, practice: practiceKinds.has(p.native_unit_kind),
      route: {url: witness.reader.url + (exact ? '#' + w.anchor : ''), anchor: exact ? w.anchor : null,
        state: exact ? 'exact_unique_anchor' : 'course_fallback', anchor_occurrences: w.occurrences},
      support: {hints: [], answers: [], solves: []},
    };
  }).sort((a, b) => a.group.localeCompare(b.group, 'en') || a.order - b.order || a.id.localeCompare(b.id, 'en'));
  const byId = new Map(result.map(u => [u.id, u]));
  const supportRelations = [], unresolvedSupport = [], unitDependencies = [];
  for (const {id, payload: p} of relations) {
    const entry = {id, native_id: p.native_relation_id, type: p.relation_type, from: p.from_native_id, to: p.to_native_id};
    if (['hints', 'answers', 'solves'].includes(p.relation_type)) {
      if (!byId.has(p.from_native_id) || !byId.has(p.to_native_id)) { unresolvedSupport.push(entry); continue; }
      assert.equal(p.evidence_state, 'exact_owner_native_relation');
      assert.equal(byId.get(p.from_native_id).projected_id, p.from_projected_id, 'Support source identity');
      assert.equal(byId.get(p.to_native_id).projected_id, p.to_projected_id, 'Support target identity');
      byId.get(p.to_native_id).support[p.relation_type].push({unit_id: p.from_native_id, relation_id: id, native_relation_id: p.native_relation_id});
      supportRelations.push(entry);
    }
    if (p.relation_type === 'depends-on' && byId.has(p.from_native_id) && byId.has(p.to_native_id)) unitDependencies.push(entry);
  }
  for (const u of result) u.support_state = Object.values(u.support).some(x => x.length) ? 'explicit_native_relationships' : 'no_explicit_native_relationship_recorded';
  const kinds = {};
  for (const u of result) kinds[u.kind] = (kinds[u.kind] ?? 0) + 1;
  return {
    schema: 'd60-learning-map-v2', course_id: 'D60', locale: 'id-ID', title: 'Topologi Aljabar', reader: witness.reader, source_witness: witnessIdentity,
    inputs: witness.inputs, prerequisites: relations.filter(r => r.payload.relation_type === 'prerequisite').map(r => r.payload.target_course_role).sort(),
    counts: {units: result.length, kinds, exact_routes: result.filter(u => u.route.state === 'exact_unique_anchor').length,
      fallback_routes: result.filter(u => u.route.state === 'course_fallback').length, practice_units: result.filter(u => u.practice).length,
      support_relations: supportRelations.length, unresolved_support_relations: unresolvedSupport.length},
    units: result, support_relations: supportRelations, unresolved_support_relations: unresolvedSupport, unit_dependencies: unitDependencies,
    limitations: [
      'The interface is bilingual; all linked native reader content in this projection is Indonesian, not a new English translation.',
      'Missing or repeated anchors use an explicitly labelled whole-course fallback, never a guessed fragment.',
      'No recorded support relation means unknown support coverage, not proof that a solution does not exist.',
      'Current native IDs, revisions, source hashes and component rights are retained; no ambiguous supersession branches are flattened.',
      'Teacher alignment here means exact unit/support selection, not a verified syllabus, grading system or new teacher manual.',
      'This reproduces the central projection only, not the complete native textbook production pipeline. Native term/schema limitations remain.',
      'Downloaded plans contain metadata and links, not the full offline textbook. No reading progress is transmitted or stored.',
    ],
  };
}

function render(map, lang, teacher) {
  const en = lang === 'en', suffix = en ? '.en' : '', page = teacher ? 'D60-pengajar' : 'D60';
  const title = en ? (teacher ? 'Algebraic Topology · Teaching plan' : 'Algebraic Topology · Study navigator') : (teacher ? 'Topologi Aljabar · Rencana pengajaran' : 'Topologi Aljabar · Panduan belajar');
  const text = (id, english) => esc(en ? english : id);
  const nav = `<nav data-central-surface-navigation="v1" data-placement="top" aria-label="${text('Navigasi program', 'Program navigation')}"><a data-program-home data-course-card data-course-id="D60" data-interface-locale="${lang}" href="https://kokunoyumeto.github.io/program-matematika-indonesia/${lang}/#course-D60">${text('Program matematika', 'Mathematics program')}</a><a data-course-surface-contents href="${teacher ? 'D60' : 'D60-pengajar'}${suffix}.html">${text(teacher ? 'Panduan belajar' : 'Panduan pengajar', teacher ? 'Study navigator' : 'Teaching plan')}</a><span class="language"><a href="${page}.html" lang="id" ${en ? '' : 'aria-current="page"'}>Bahasa Indonesia</a> / <a href="${page}.en.html" lang="en" ${en ? 'aria-current="page"' : ''}>English</a></span></nav>`;
  const lectures = map.units.filter(u => u.kind === 'lecture');
  const supplements = map.units.filter(u => u.kind === 'capstone' || (u.kind === 'reader_unit' && !u.id.match(/rbt-u\d+/)));
  const links = rows => rows.map(u => `<li><a href="${esc(u.route.url)}" lang="id">${esc(u.title)}</a> <small>${esc(u.id)}${u.route.state === 'course_fallback' ? text(' — pembaca lengkap, tanpa jangkar unit', ' — full reader, no unit anchor') : ''}</small></li>`).join('');
  return `<!doctype html><html lang="${lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'none'; object-src 'none'; base-uri 'none'"><title>D60 · ${title}</title><link rel="stylesheet" href="d60.css"><script defer src="data.js"></script><script defer src="d60-ui.js"></script></head><body data-interface="${lang}" data-mode="${teacher ? 'teacher' : 'learner'}"><a class="skip" href="#main">${text('Langsung ke isi', 'Skip to content')}</a>${nav}<main id="main"><header><p class="eyebrow">D60 · ${text('Belajar dan mengajar', 'Study and teach')}</p><h1>${title}</h1><p>${text('Telusuri materi, pilih unit, lalu simpan rencana dengan tautan bacaan dan relasi latihan yang berasal dari backend buku.', 'Find material, choose units, and save a plan with reading links and the exercise relationships already recorded in the book backend.')}</p><p class="notice">${text('Bahasa antarmuka dapat dipilih. Bacaan yang ditautkan di sini berbahasa Indonesia. Ini bukan edisi bahasa Inggris baru.', 'Choose either interface language. The linked reading here is in Indonesian. This is not a new English edition.')}</p><div class="facts"><span>${map.counts.units} ${text('unit', 'units')}</span><span>${map.counts.practice_units} ${text('latihan / pertanyaan / pemeriksaan bukti', 'exercises / questions / proof checks')}</span><span>${map.counts.exact_routes} ${text('tautan unit tepat', 'exact unit links')}</span></div><p><a href="${esc(map.reader.url)}" lang="id">${text('Buka pembaca lengkap', 'Open the complete Indonesian reader')}</a> · <a href="https://doi.org/10.5281/zenodo.22168033">${text('Edisi tersimpan di Zenodo', 'Preserved edition on Zenodo')}</a> · <a href="https://github.com/KokunoYumeto/algebraic-topology-id">${text('Sumber yang dapat diedit', 'Editable source')}</a></p><p>${text('Prasyarat program', 'Program prerequisites')}: ${map.prerequisites.map(id => `<a href="../../${lang}/#course-${id}">${id}</a>`).join(' · ')}</p></header>
<section aria-labelledby="readings"><h2 id="readings">${text('Mulai membaca', 'Start reading')}</h2><details><summary>${text('30 kuliah Roberts', '30 Roberts lectures')}</summary><ol>${links(lectures)}</ol></details><details><summary>${text('Fomberg, asesmen, laboratorium dan capstone', 'Fomberg, assessments, laboratories and capstone')}</summary><ul>${links(supplements)}</ul></details></section>
<section id="workbench" hidden aria-labelledby="browse-title"><h2 id="browse-title">${text('Pilih bahan untuk rencana Anda', 'Choose material for your plan')}</h2><p>${text('Cari judul, ID atau konsep. Relasi petunjuk, jawaban dan solusi ditampilkan tanpa membuka jawabannya otomatis.', 'Search titles, IDs or concepts. Hint, answer and solution links remain closed until you open them.')}</p><div class="filters"><label>${text('Cari', 'Search')}<input type="search" id="search"></label><label>${text('Jenis', 'Kind')}<select id="kind"><option value="">${text('Semua jenis', 'All kinds')}</option><option value="practice">${text('Latihan dan pemeriksaan', 'Exercises and checks')}</option></select></label><label>${text('Kelompok bacaan', 'Reading group')}<select id="group"><option value="">${text('Semua kelompok', 'All groups')}</option></select></label></div><div class="toolbar"><button type="button" id="select-page">${text('Pilih halaman ini', 'Select this page')}</button><button type="button" id="clear">${text('Kosongkan pilihan', 'Clear selection')}</button><button type="button" id="export">${text('Unduh rencana JSON', 'Download plan JSON')}</button><button type="button" id="export-text">${text('Unduh rencana teks', 'Download text plan')}</button><span id="selection" role="status"></span></div><p id="results-status" role="status"></p><div id="unit-list"></div><div class="toolbar"><button type="button" id="previous">${text('Sebelumnya', 'Previous')}</button><button type="button" id="next">${text('Berikutnya', 'Next')}</button></div></section><noscript><p>${text('Daftar bacaan di atas berfungsi tanpa JavaScript. Aktifkan JavaScript untuk pencarian dan ekspor pilihan.', 'The reading lists above work without JavaScript. Enable it for search and selected-plan export.')}</p></noscript>
<section><h2>${text('Apa yang diverifikasi?', 'What is verified?')}</h2><p>${text('ID dan relasi berasal dari tabel native yang dipatok. Setiap tautan unit diperiksa pada HTML publik. Sebanyak 38 unit tanpa jangkar memakai pembaca lengkap dan diberi label. Tidak ada isi buku yang ditulis ulang.', 'IDs and relationships come from pinned native tables. Each unit destination was checked against the public HTML. The 38 units without anchors use an explicitly labelled full-reader link. No book text is rewritten.')}</p><p>${text('Rencana pengajar menghubungkan unit dan bahan pendukung dengan ID yang tepat. Ini bukan kurikulum pengajaran baru atau sistem penilaian. Tidak adanya relasi solusi berarti cakupan belum diketahui, bukan berarti solusi tidak ada.', 'Teaching plans preserve exact unit and support IDs. This is not a new teaching syllabus or grading system. An absent solution relation means unknown coverage, not that no solution exists.')}</p><p>${text('Rencana berisi metadata dan tautan; buku lengkap belum disertakan untuk penggunaan luring. Pilihan tidak dikirim ke server.', 'Plans contain metadata and links; they do not include the full book for offline reading. Your selections are not sent to a server.')}</p><a href="learning-map.json">${text('Data yang dapat digunakan ulang', 'Reusable data')}</a> · <a href="validation.json">${text('Bukti pemeriksaan', 'Validation evidence')}</a></section></main></body></html>\n`;
}

export async function build(out = resolve(project, 'docs/backend/d60')) {
  const inputs = await loadInputs(), map = projectMap(inputs);
  assert.equal(map.counts.units, 2204);
  assert.equal(map.counts.kinds.lecture, 30);
  assert.equal(map.counts.kinds.capstone, 1);
  const outputs = {'learning-map.json': json(map), 'data.js': 'globalThis.D60_DATA = ' + JSON.stringify(map) + ';\n'};
  for (const lang of ['id', 'en']) for (const teacher of [false, true]) {
    const name = (teacher ? 'D60-pengajar' : 'D60') + (lang === 'en' ? '.en' : '') + '.html';
    outputs[name] = render(map, lang, teacher)
      .replace('data-central-surface-navigation="v1" data-placement="top"', 'data-d60-navigation="v1"')
      .replace(/ data-(?:program-home|course-card|course-id|interface-locale|course-surface-contents)(?:="[^"]*")?/g, '');
  }
  for (const file of ['d60-ui.js', 'd60.css']) outputs[file] = await readFile(resolve(project, 'scripts/d60-surface', file), 'utf8');
  const validation = {schema: 'd60-surface-validation-v2', course_id: 'D60', state: 'pass', verification_scope: 'Structural build checks; independent tests recorded separately.', counts: map.counts,
    inputs: [...inputs.witness.inputs, inputs.witnessIdentity], reader: map.reader,
    checks: {input_hashes: true, native_ids_unique: true, reader_anchor_precision_preserved: true, explicit_support_identity_joins: true, body_content_copied: false},
    outputs: Object.entries(outputs).map(([path, text]) => ({path, bytes: Buffer.byteLength(text), sha256: sha256(text)})), limitations: map.limitations};
  outputs['validation.json'] = json(validation);
  await mkdir(out, {recursive: true});
  for (const [name, text] of Object.entries(outputs)) await writeFile(resolve(out, name), text);
  return {map, validation};
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const option = process.argv.find(x => x.startsWith('--output-root='));
  const {map} = await build(option ? resolve(option.slice(14)) : undefined);
  console.log(JSON.stringify({state: 'built', counts: map.counts}));
}
