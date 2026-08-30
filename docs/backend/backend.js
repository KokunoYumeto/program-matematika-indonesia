const dataUrl = '../data/course-capsule-v1/course-capsules.json';

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

const grid = document.querySelector('#course-grid');
const search = document.querySelector('#course-search');
const level = document.querySelector('#level-filter');
const courseState = document.querySelector('#state-filter');
const resultCount = document.querySelector('#result-count');
const viewDescription = document.querySelector('#view-description');

const escapeHtml = (value) => String(value ?? '')
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')
  .replaceAll("'", '&#039;');

const statusLabel = (status) => statusLabels[status] ?? status;
const external = ' target="_blank" rel="noreferrer"';
const link = (url, label, primary = false) => url
  ? '<a class="' + (primary ? 'primary' : '') + '" href="' + escapeHtml(url) + '"' + external + '>' + escapeHtml(label) + ' ↗</a>'
  : '';

const learnerPanel = (capsule) => {
  const layer = capsule.layers.learner;
  const actions = [
    link(layer.primary?.url, 'Buka sumber utama', true),
    link(layer.online_html?.url, 'Baca daring'),
    link(layer.pdf?.url, 'PDF'),
    link(layer.epub?.url, 'EPUB'),
    link(layer.portable_html?.url, 'HTML luring'),
  ].filter(Boolean).join('');
  return [
    '<div class="status-line"><span>Kesiapan akses</span><strong>' + escapeHtml(statusLabel(layer.status)) + '</strong></div>',
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
    ? '<ul class="resource-list">' + layer.resources.map((item) => '<li><a href="' + escapeHtml(item.url) + '"' + external + '>' + escapeHtml(item.title) + ' — ' + escapeHtml(resourceLabels[item.resource_type] ?? item.resource_type) + ' ↗</a></li>').join('') + '</ul>'
    : '';
  const evidence = layer.evidence.length
    ? '<div class="card-actions">' + link(layer.evidence[0].locator, 'Buka bukti bahan') + '</div>'
    : '';
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
    '<div class="status-line"><span>Pembangunan ulang</span><strong>' + escapeHtml(statusLabel(production.deterministic_replay_status)) + '</strong></div>',
    '<div class="status-line"><span>Rilis</span><strong>' + escapeHtml(statusLabel(production.release_status)) + '</strong></div>',
    '<div class="card-actions">' + link(production.repository, 'Repositori', true) + link(production.zenodo, 'Zenodo') + '</div>',
  ].join('');
};

const interopPanel = (capsule) => {
  const federation = capsule.layers.federation;
  const adapter = capsule.layers.interoperability.semantic_adapter;
  const components = federation.components.length
    ? '<ul class="component-list">' + federation.components.map((item) => '<li>' + escapeHtml(resourceLabels[item.kind] ?? item.kind) + '</li>').join('') + '</ul>'
    : '<p class="empty-note">Belum ada komponen yang dipetakan.</p>';
  const actions = federation.components
    .filter((item) => item.url)
    .slice(0, 3)
    .map((item, index) => link(item.url, index === 0 ? 'Sumber kanonis' : item.title, index === 0))
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
  if (state.courseState === 'adapter' && !['verified', 'legacy_verified'].includes(capsule.layers.interoperability.semantic_adapter.status)) return false;
  return true;
};

const render = () => {
  const visible = courses.filter(matches);
  grid.innerHTML = visible.length
    ? visible.map(card).join('')
    : '<p class="no-results">Tidak ada mata kuliah yang cocok. Hapus satu atau lebih saringan.</p>';
  resultCount.textContent = visible.length + ' dari ' + courses.length + ' mata kuliah ditampilkan';
};

document.querySelectorAll('[data-view]').forEach((button) => {
  button.addEventListener('click', () => {
    state.view = button.dataset.view;
    document.querySelectorAll('[data-view]').forEach((candidate) => {
      candidate.setAttribute('aria-selected', String(candidate === button));
    });
    viewDescription.textContent = viewDescriptions[state.view];
    render();
  });
});

search.addEventListener('input', () => {
  state.query = search.value.trim().toLocaleLowerCase('id');
  render();
});
level.addEventListener('change', () => {
  state.level = level.value;
  render();
});
courseState.addEventListener('change', () => {
  state.courseState = courseState.value;
  render();
});
document.querySelector('#reset-filters').addEventListener('click', () => {
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
  document.querySelector('#summary-total').textContent = courses.length;
  document.querySelector('#summary-published').textContent = courses.filter((item) => item.course.state === 'published').length;
  document.querySelector('#summary-production').textContent = courses.filter((item) => item.course.state === 'production').length;
  document.querySelector('#summary-educator').textContent = courses.filter((item) => item.layers.educator.features.length || item.layers.educator.resources.length).length;
  render();
} catch (error) {
  resultCount.textContent = 'Data dinamis tidak dapat dimuat; daftar dasar tetap tersedia di bawah.';
  grid.querySelectorAll('[hidden]').forEach((item) => item.removeAttribute('hidden'));
  console.error(error);
}
