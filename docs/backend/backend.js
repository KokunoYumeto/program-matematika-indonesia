const dataUrl = '../data/course-capsule-v1/course-capsules.json';
// CLP v0.62.17 is an additive successor projection.  Prefer the generated
// capsule-sidecar mirror, then fall back to its explicitly versioned public
// mirror when the generic projection has not yet been copied into a staging
// tree.  Neither path changes the historical v0.62.16 snapshot.
const learnerReaderActionsUrls = [
  '../data/course-capsule-v1/learner-reader-actions-v1.json',
  '../data/clp-successor/v0.62.17/learner-reader-actions-v1.json',
];

const viewDescriptions = {
  learner: 'Buka edisi, lihat prasyarat, dan temukan format daring atau luring yang benar-benar tersedia.',
  educator: 'Lihat bahan pengajar yang sudah terindeks: latihan, solusi, asesmen, rubrik, laboratorium, dan dukungan aksesibilitas.',
  production: 'Periksa keadaan terjemahan, pembangunan deterministik, repositori, edisi, dan arsip publik.',
  interop: 'Lihat komponen zero-copy dan seberapa jauh setiap kursus dapat dipetakan ke kontrak bersama tanpa kehilangan identitas aslinya.',
};

const statusLabels = {
  verified: 'terverifikasi',
  legacy_verified: 'terverifikasi — kontrak lama',
  available_unverified: 'tersedia; belum diverifikasi penuh',
  in_progress: 'sedang dibuat',
  not_yet_produced: 'belum dibuat',
  not_applicable: 'tidak berlaku',
  unknown: 'belum diketahui',
};

const featureLabels = {
  outcome_evidence_map: 'peta capaian & bukti',
  prerequisite_diagnostics: 'diagnostik prasyarat',
  lesson_sequences: 'urutan pelajaran',
  pacing_plans: 'rencana tempo',
  worked_examples: 'contoh terbimbing',
  exercise_bank: 'bank latihan',
  staged_hints_answers_solutions: 'petunjuk → jawaban → solusi',
  solution_provenance: 'asal solusi',
  assessment_blueprints: 'rancangan asesmen',
  rubrics: 'rubrik',
  misconceptions_interventions: 'miskonsepsi & intervensi',
  activities_labs: 'aktivitas & laboratorium',
  accessibility_accommodations: 'akomodasi aksesibilitas',
  remix_selectors: 'pemilih untuk remix',
};

const resourceLabels = {
  'course-native-primary': 'sumber utama kursus',
  'problem-book': 'buku soal',
  solutions: 'solusi',
  workbook: 'buku kerja',
  'companion-reader': 'pembaca pendamping',
  'donor-reader': 'pembaca donor',
  'donor-archive': 'arsip donor',
  'course-volume': 'volume kursus',
  reference: 'referensi',
};

const state = { view: 'learner', query: '', level: 'all', courseState: 'all' };
let courses = [];
let dataReady = false;
let learnerReaderActionsByCourseId = new Map();

const grid = document.querySelector('#course-grid');
const search = document.querySelector('#course-search');
const level = document.querySelector('#level-filter');
const courseState = document.querySelector('#state-filter');
const resultCount = document.querySelector('#result-count');
const viewDescription = document.querySelector('#view-description');
const fallbackMarkup = grid.innerHTML;
const dynamicControls = [
  ...document.querySelectorAll('[data-view]'),
  search, level, courseState, document.querySelector('#reset-filters'),
];
dynamicControls.forEach((control) => { control.disabled = true; });

const escapeHtml = (value) => String(value ?? '')
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')
  .replaceAll("'", '&#039;');

const statusLabel = (status) => statusLabels[status] ?? status;
const external = ' target="_blank" rel="noreferrer"';
const externalHint = '<span class="sr-only"> (terbuka di tab baru)</span>';
const publicEvidenceUrl = (url) => typeof url === 'string' && /^https:\/\/[^/\s]+\//.test(url);
const link = (url, label, primary = false) => publicEvidenceUrl(url)
  ? '<a class="' + (primary ? 'primary' : '') + '" href="' + escapeHtml(url) + '"' + external + '>' + escapeHtml(label) + ' <span aria-hidden="true">↗</span>' + externalHint + '</a>'
  : '';
const deliverableStatuses = new Set(['verified', 'available_unverified']);
const deliveryLink = (resource, label, primary = false, allowedFormats = []) => {
  if (!deliverableStatuses.has(resource?.status)) return '';
  if (!publicEvidenceUrl(resource?.url)) return '';
  if (!allowedFormats.includes(resource?.format)) return '';
  return link(
    resource.url,
    label + (resource.scope && resource.scope !== 'whole_course' ? ' — bagian kursus' : ''),
    primary,
  );
};
const learnerToolLink = (tool, courseId) => {
  if (tool.machine_data_is_learner_destination !== false) return '';
  const href = '../' + tool.href.replace(/^\/+/, '');
  return '<a class="learner-tool' + (tool.primary ? ' primary' : '') + '" href="' + escapeHtml(href) + '" title="' + escapeHtml(tool.scope) + '">' + escapeHtml(tool.label) + '<span class="sr-only"> — ' + escapeHtml(courseId) + '</span></a>';
};

const clpCourseIds = ['B20', 'B30', 'B50', 'B60'];
const readerActionLink = (action, courseId) => '<a class="reader-action" href="' + escapeHtml(action.url) + '"' + external + '>' + escapeHtml(action.label ?? (courseId + ' — ' + action.role)) + ' <span aria-hidden="true">↗</span>' + externalHint + '</a>';

const validateReaderActionSidecar = (payload) => {
  if (!payload || payload.schema_id !== 'interlanguage/learner-reader-actions/v1') throw new Error('schema_id tidak cocok');
  if (payload.schema_version !== '1.0.0' || payload.locale !== 'id-ID' || payload.status !== 'verified_route_evidence_projection') throw new Error('status sidecar tidak cocok');
  const actions = Array.isArray(payload.actions) ? payload.actions : [];
  if (actions.length !== 7) throw new Error('sidecar CLP harus memuat tujuh aksi pembaca');
  if (new Set(actions.map((action) => action.action_id)).size !== 7) throw new Error('action_id sidecar tidak unik');
  if (JSON.stringify([...new Set(actions.map((action) => action.course_id))].sort()) !== JSON.stringify(clpCourseIds)) throw new Error('cakupan kursus sidecar tidak cocok');
  if (JSON.stringify(actions.map((action) => action.order)) !== JSON.stringify([1, 2, 3, 4, 5, 6, 7])) throw new Error('urutan sidecar tidak cocok');
  for (const action of actions) {
    if (!/^(B20|B30|B50|B60):reader:[a-z]+$/u.test(action.action_id)) throw new Error('action_id CLP tidak valid');
    if (!clpCourseIds.includes(action.course_id)) throw new Error('course_id CLP tidak valid');
    if (action.state !== 'verified' || action.format !== 'application/pdf' || action.route_granularity !== 'whole_file_only') throw new Error('aksi CLP bukan PDF whole-file terverifikasi');
    if (!Number.isInteger(action.pages) || action.pages <= 0 || !Number.isInteger(action.bytes) || action.bytes <= 0) throw new Error('ukuran aksi CLP tidak valid');
    if (!/^[0-9a-f]{64}$/iu.test(action.sha256) || !publicEvidenceUrl(action.url)) throw new Error('identitas publik aksi CLP tidak valid');
  }
  const summary = payload.summary ?? {};
  if (summary.course_count !== 4 || summary.action_count !== 7 || summary.verified_action_count !== 7 || summary.pages !== 4077 || summary.bytes !== 35639691) throw new Error('ringkasan sidecar CLP tidak cocok');
  if (actions.reduce((total, action) => total + action.pages, 0) !== summary.pages || actions.reduce((total, action) => total + action.bytes, 0) !== summary.bytes) throw new Error('jumlah sidecar CLP tidak cocok');
  return new Map(clpCourseIds.map((courseId) => [
    courseId,
    actions.filter((action) => action.course_id === courseId).sort((left, right) => left.order - right.order),
  ]));
};

const loadReaderActions = async () => {
  let lastError;
  for (const url of learnerReaderActionsUrls) {
    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error('HTTP ' + response.status);
      return validateReaderActionSidecar(await response.json());
    } catch (error) {
      lastError = error;
    }
  }
  if (lastError) console.warn?.('Rute pembaca CLP tidak dimuat:', lastError);
  return new Map();
};

const learnerPanel = (capsule) => {
  const layer = capsule.layers.learner;
  if (capsule.locale !== 'id-ID') {
    return '<p class="empty-note">Rute pelajar disembunyikan karena locale kapsul tidak terverifikasi sebagai Bahasa Indonesia.</p>';
  }
  const tools = (layer.tools ?? []).filter((tool) => tool.state === 'verified' && tool.machine_data_is_learner_destination === false);
  const readerActions = learnerReaderActionsByCourseId.get(capsule.course_id) ?? [];
  const readerActionHrefs = new Set(readerActions.map((action) => action.url));
  const actionRows = [
    ...readerActions.map((action) => ({ href: action.url, preserveDuplicate: true, html: readerActionLink(action, capsule.course_id) })),
    ...tools.map((tool) => ({ href: '../' + tool.href.replace(/^\/+/, ''), html: learnerToolLink(tool, capsule.course_id) })),
    ...(readerActionHrefs.has(layer.primary?.url) ? [] : [{ href: layer.primary?.url, html: deliveryLink(layer.primary, 'Buka sumber utama — ' + capsule.course_id, true, ['text/html', 'application/pdf', 'application/epub+zip', 'application/zip+html']) }]),
    { href: layer.online_html?.url, html: deliveryLink(layer.online_html, 'Baca daring — ' + capsule.course_id, false, ['text/html']) },
    { href: layer.pdf?.url, html: deliveryLink(layer.pdf, 'PDF — ' + capsule.course_id, false, ['application/pdf']) },
    { href: layer.epub?.url, html: deliveryLink(layer.epub, 'EPUB — ' + capsule.course_id, false, ['application/epub+zip']) },
    { href: layer.portable_html?.url, html: deliveryLink(layer.portable_html, 'HTML luring — ' + capsule.course_id, false, ['application/zip+html']) },
  ].filter((row) => row.html);
  // Seed de-duplication with sidecar destinations.  The seven sidecar rows
  // are retained even when a capsule's legacy `pdf`/`primary` field points at
  // the same file; generic aliases should not create extra duplicate buttons.
  const seenHrefs = new Set(readerActions.map((action) => action.url));
  const actions = actionRows.filter(({ href, preserveDuplicate }) => {
    if (preserveDuplicate) return true;
    if (seenHrefs.has(href)) return false;
    seenHrefs.add(href);
    return true;
  }).map(({ html }) => html).join('');
  return [
    '<div class="status-line"><span>Kesiapan akses</span><strong>' + escapeHtml(statusLabel(layer.status)) + '</strong></div>',
    readerActions.length ? '<div class="status-line"><span>Rute pembaca CLP</span><strong>' + readerActions.length + '</strong></div>' : '',
    tools.length ? '<div class="status-line"><span>Alat belajar terverifikasi</span><strong>' + tools.length + '</strong></div>' : '',
    '<div class="status-line"><span>HTML semantik</span><strong>' + escapeHtml(statusLabel(layer.capabilities.semantic_html)) + '</strong></div>',
    '<div class="status-line"><span>Format cetak</span><strong>' + escapeHtml(statusLabel(layer.capabilities.print_profile)) + '</strong></div>',
    '<div class="card-actions">' + actions + '</div>',
  ].join('');
};

const educatorPanel = (capsule) => {
  const layer = capsule.layers.educator;
  const features = layer.features.length
    ? '<ul class="feature-list">' + layer.features.map((item) => '<li>' + escapeHtml(featureLabels[item] ?? item) + '</li>').join('') + '</ul>'
    : '<p class="empty-note">Belum ada paket pengajar terstruktur yang terindeks. Edisi pelajar tetap dapat digunakan.</p>';
  const resources = layer.resources.length
    ? '<ul class="resource-list">' + layer.resources.map((item) => '<li><a href="' + escapeHtml(item.url) + '"' + external + '>' + escapeHtml(item.title) + ' — ' + escapeHtml(resourceLabels[item.resource_type] ?? item.resource_type) + '<span class="sr-only"> — ' + escapeHtml(capsule.course_id) + '</span> <span aria-hidden="true">↗</span>' + externalHint + '</a></li>').join('') + '</ul>'
    : '';
  const publicEvidence = layer.evidence.find((item) => publicEvidenceUrl(item.locator));
  const evidence = publicEvidence
    ? '<div class="card-actions">' + link(publicEvidence.locator, 'Buka bukti bahan — ' + capsule.course_id) + '</div>'
    : layer.evidence.length ? '<p class="empty-note">Bukti terindeks belum mempunyai tautan publik.</p>' : '';
  return [
    '<div class="status-line"><span>Lapisan pengajar</span><strong>' + escapeHtml(statusLabel(layer.status)) + '</strong></div>',
    features,
    resources,
    evidence,
  ].join('');
};

const productionPanel = (capsule) => {
  const translation = capsule.layers.translation;
  const production = capsule.layers.production;
  return [
    '<div class="status-line"><span>Terjemahan</span><strong>' + escapeHtml(statusLabel(translation.status)) + '</strong></div>',
    '<div class="status-line"><span>Ledger terjemahan</span><strong>' + escapeHtml(statusLabel(translation.ledger_status)) + '</strong></div>',
    '<div class="status-line"><span>Terminologi</span><strong>' + escapeHtml(statusLabel(translation.terminology_status)) + '</strong></div>',
    '<div class="status-line"><span>Koreksi</span><strong>' + escapeHtml(statusLabel(translation.corrections_status)) + '</strong></div>',
    '<div class="status-line"><span>Pembangunan ulang</span><strong>' + escapeHtml(statusLabel(production.deterministic_replay_status)) + '</strong></div>',
    '<div class="status-line"><span>Rilis</span><strong>' + escapeHtml(statusLabel(production.release_status)) + '</strong></div>',
    '<div class="card-actions">' + link(production.repository, 'Repositori — ' + capsule.course_id, true) + link(production.zenodo, 'Zenodo — ' + capsule.course_id) + '</div>',
  ].join('');
};

const interopPanel = (capsule) => {
  const federation = capsule.layers.federation;
  const adapter = capsule.layers.interoperability.semantic_adapter;
  const components = federation.components.length
    ? '<ul class="component-list">' + federation.components.map((item) => '<li>' + escapeHtml(resourceLabels[item.kind] ?? 'komponen kursus') + ' — ' + escapeHtml(item.title) + ' <small>Hak: ' + escapeHtml(statusLabel(item.rights_status ?? 'unknown')) + '</small></li>').join('') + '</ul>'
    : '<p class="empty-note">Belum ada komponen yang dipetakan.</p>';
  const actions = federation.components
    .filter((item) => item.url)
    .map((item, index) => link(item.url, (index === 0 ? 'Sumber kanonis' : item.title) + ' — ' + capsule.course_id, index === 0))
    .join('');
  return [
    '<div class="status-line"><span>Kontrak kapsul</span><strong>1.0.0</strong></div>',
    '<div class="status-line"><span>Adapter semantik</span><strong>' + escapeHtml(statusLabel(adapter.status)) + '</strong></div>',
    '<div class="status-line"><span>Komponen zero-copy</span><strong>' + federation.components.length + '</strong></div>',
    components,
    '<div class="card-actions">' + actions + '</div>',
  ].join('');
};

const card = (capsule) => {
  const panels = {
    learner: learnerPanel,
    educator: educatorPanel,
    production: productionPanel,
    interop: interopPanel,
  };
  const prerequisites = capsule.course.prerequisites.length
    ? capsule.course.prerequisites.join(', ')
    : 'tidak ada';
  return [
    '<article class="course-card" data-course-id="' + escapeHtml(capsule.course_id) + '">',
    '<div class="card-top"><span class="course-code">' + escapeHtml(capsule.course_id) + '</span><span class="state-badge ' + escapeHtml(capsule.course.state) + '">' + (capsule.course.state === 'published' ? 'Edisi selesai' : 'Sedang diproduksi') + '</span></div>',
    '<h3>' + escapeHtml(capsule.course.title) + '</h3>',
    '<p class="topic">' + escapeHtml(capsule.course.topic) + '</p>',
    '<p class="outcome">' + escapeHtml(capsule.course.outcome) + '</p>',
    '<p class="prerequisites"><strong>Prasyarat</strong>' + escapeHtml(prerequisites) + '</p>',
    '<div class="view-panel">' + panels[state.view](capsule) + '</div>',
    '</article>',
  ].join('');
};

const matches = (capsule) => {
  const haystack = [
    capsule.course_id,
    capsule.course.title,
    capsule.course.topic,
    capsule.course.outcome,
    capsule.course_native.corpus,
  ].join(' ').toLocaleLowerCase('id');
  if (state.query && !haystack.includes(state.query)) return false;
  if (state.level !== 'all' && capsule.course.level !== state.level) return false;
  if (state.courseState === 'published' && capsule.course.state !== 'published') return false;
  if (state.courseState === 'production' && capsule.course.state !== 'production') return false;
  if (state.courseState === 'educator' && !capsule.layers.educator.features.length && !capsule.layers.educator.resources.length) return false;
  if (state.courseState === 'adapter' && !['verified', 'legacy_verified', 'available_unverified'].includes(capsule.layers.interoperability.semantic_adapter.status)) return false;
  return true;
};

const render = () => {
  // The server-rendered course links remain usable while data is pending or
  // unavailable. Never replace them with an empty client-side collection.
  if (!dataReady) return;
  const visible = courses.filter(matches);
  grid.innerHTML = visible.length
    ? visible.map(card).join('')
    : '<p class="no-results">Tidak ada mata kuliah yang cocok. Hapus satu atau lebih saringan.</p>';
  resultCount.textContent = visible.length + ' dari ' + courses.length + ' mata kuliah ditampilkan';
};

document.querySelectorAll('[data-view]').forEach((button) => {
  button.addEventListener('click', () => {
    if (!dataReady) return;
    state.view = button.dataset.view;
    document.querySelectorAll('[data-view]').forEach((candidate) => {
      candidate.setAttribute('aria-pressed', String(candidate === button));
    });
    viewDescription.textContent = viewDescriptions[state.view];
    render();
  });
});

search.addEventListener('input', () => {
  if (!dataReady) return;
  state.query = search.value.trim().toLocaleLowerCase('id');
  render();
});
level.addEventListener('change', () => {
  if (!dataReady) return;
  state.level = level.value;
  render();
});
courseState.addEventListener('change', () => {
  if (!dataReady) return;
  state.courseState = courseState.value;
  render();
});
document.querySelector('#reset-filters').addEventListener('click', () => {
  if (!dataReady) return;
  state.query = '';
  state.level = 'all';
  state.courseState = 'all';
  search.value = '';
  level.value = 'all';
  courseState.value = 'all';
  render();
});

try {
  const response = await fetch(dataUrl);
  if (!response.ok) throw new Error('HTTP ' + response.status);
  courses = await response.json();
  if (!Array.isArray(courses) || courses.length !== 40) throw new Error('Jumlah mata kuliah tidak cocok.');
  // Fetch the small successor sidecar only after the catalog response has
  // succeeded.  This keeps the offline/rejected-catalog path non-blocking,
  // while making the seven CLP actions available in the first successful
  // render whenever the public sidecar is reachable.
  learnerReaderActionsByCourseId = await loadReaderActions();
  dataReady = true;
  document.querySelector('#summary-total').textContent = courses.length;
  document.querySelector('#summary-published').textContent = courses.filter((item) => item.course.state === 'published').length;
  document.querySelector('#summary-production').textContent = courses.filter((item) => item.course.state === 'production').length;
  document.querySelector('#summary-educator').textContent = courses.filter((item) => item.layers.educator.features.length || item.layers.educator.resources.length).length;
  render();
  dynamicControls.forEach((control) => { control.disabled = false; });
} catch (error) {
  dataReady = false;
  courses = [];
  dynamicControls.forEach((control) => { control.disabled = true; });
  grid.innerHTML = fallbackMarkup;
  resultCount.textContent = 'Data dinamis tidak dapat dimuat; daftar dasar tetap tersedia di bawah.';
  grid.querySelectorAll('[hidden]').forEach((item) => item.removeAttribute('hidden'));
  console.error(error);
}
