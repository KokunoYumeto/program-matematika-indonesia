import { courses as authorityCourses, program, topics } from './courses.js';
import {
  deriveNextCourseIdsById,
  materializeLiveCourses,
} from './live-course-publications.js';
import { learnerDeliveryByCourseId } from './learner-delivery.js';
import { learnerToolsByCourseId } from './learner-tools.js';
import {
  clearLearnerState,
  createEmptyLearnerState,
  evaluateLearnerState,
  loadLearnerState,
  saveLearnerState,
  setCourseClaim,
  setCourseCompletion,
  setPrerequisiteWaiver,
} from './learner-state.js';

const courses = materializeLiveCourses(authorityCourses);
const nextCourseIdsById = deriveNextCourseIdsById(courses);

const stateLabels = {
  published: 'Edisi publik selesai',
  near: 'Hampir dirilis',
  production: 'Korpus terpilih',
  unresolved: 'Belum dibekukan',
};

const learnerStatusLabels = {
  completed: 'Selesai menurut catatan Anda',
  eligible: 'Prasyarat langsung terpenuhi',
  eligible_with_waiver: 'Prasyarat terpenuhi dengan waiver',
  blocked: 'Prasyarat belum lengkap',
};

const satisfactionLabels = {
  completed: 'selesai',
  placement: 'penempatan',
  equivalence: 'kesetaraan',
  waived: 'waiver',
  missing: 'belum',
};

const searchInput = document.querySelector('#course-search');
const topicSelect = document.querySelector('#topic-filter');
const statusSelect = document.querySelector('#status-filter');
const levelButtons = [...document.querySelectorAll('[data-level]')];
const topicLinks = document.querySelector('#topic-links');
const grid = document.querySelector('#course-grid');
const resultCount = document.querySelector('#result-count');
const resetButton = document.querySelector('#reset-filters');
const learnerSummary = document.querySelector('#learner-summary');
const learnerStorageStatus = document.querySelector('#learner-storage-status');
const placementCourse = document.querySelector('#placement-course');
const equivalenceCourse = document.querySelector('#equivalence-course');
const waiverTarget = document.querySelector('#waiver-target');
const waiverPrerequisite = document.querySelector('#waiver-prerequisite');
const learnerClaims = document.querySelector('#learner-claims');
const liveCompletedRoleCount = document.querySelector('#live-completed-role-count');
const livePublicationSummary = document.querySelector('#live-publication-summary');
let activeLevel = 'all';

const effectivePublishedCourses = courses.filter(({ state }) => state === 'published');
const effectiveCompletedRecordCount = new Set(effectivePublishedCourses.map(({ zenodo }) => zenodo).filter(Boolean)).size;
liveCompletedRoleCount.textContent = String(effectivePublishedCourses.length);
livePublicationSummary.textContent = `${effectivePublishedCourses.length} peran memakai ${effectiveCompletedRecordCount} rekaman edisi lengkap yang berbeda. Lapisan publikasi langsung memperbarui katalog tanpa menyamarkan keluaran terjemahan atau paket pembantu sebagai edisi kanonis; produksi yang belum selesai tetap dilabeli dengan jelas.`;

let browserStorage = null;
try {
  browserStorage = window.localStorage;
} catch {
  browserStorage = null;
}
const loadedLearnerState = loadLearnerState(browserStorage, courses);
let learnerState = loadedLearnerState.state;
let learnerEvaluation = evaluateLearnerState(courses, learnerState);

function normalize(value) {
  return value.toLocaleLowerCase('id-ID').normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}

function courseLabel(course) {
  return `${course.id} — ${course.title}`;
}

function renderTopicControls() {
  topics.forEach((topic) => {
    const option = document.createElement('option');
    option.value = topic;
    option.textContent = topic;
    topicSelect.append(option);

    const count = courses.filter((course) => course.topic === topic).length;
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'topic-pill';
    button.dataset.topic = topic;
    button.innerHTML = `<span>${topic}</span><b>${count}</b>`;
    button.addEventListener('click', () => {
      topicSelect.value = topic;
      renderCourses();
      document.querySelector('#katalog').scrollIntoView({ behavior: 'smooth' });
    });
    topicLinks.append(button);
  });
}

function prerequisiteLinks(course) {
  if (!course.prerequisites.length) return '<span class="no-prereq">Tidak ada — mulai di sini atau gunakan diagnosis awal.</span>';
  const satisfaction = new Map(learnerEvaluation[course.id].prerequisites.map((row) => [row.courseId, row.satisfaction]));
  return course.prerequisites.map((id) => {
    const kind = satisfaction.get(id) ?? 'missing';
    return `<a class="prereq-link prereq-${kind}" href="#course-${id}" data-course-link="${id}"><span>${id}</span><small>${satisfactionLabels[kind]}</small></a>`;
  }).join('');
}

function nextCourseLinks(course) {
  const nextIds = nextCourseIdsById[course.id] ?? [];
  if (!nextIds.length) return '<span class="no-next-course">Tidak ada lanjutan langsung dalam peta ini.</span>';
  return nextIds.map((id) => {
    const nextCourse = courses.find((candidate) => candidate.id === id);
    if (!nextCourse) return '';
    const nextCourseEvaluation = learnerEvaluation[nextCourse.id];
    const learnerRouteNote = nextCourseEvaluation?.status === 'blocked'
      ? `${learnerStatusLabels.blocked}${nextCourseEvaluation.missingPrerequisiteIds.length
        ? ` · Kurang: ${nextCourseEvaluation.missingPrerequisiteIds.join(', ')}`
        : ''}`
      : learnerStatusLabels[nextCourseEvaluation?.status] ?? 'Status pelajar tidak tersedia';
    const otherPrerequisites = `<small>${stateLabels[nextCourse.state]} · ${learnerRouteNote}</small>`;
    return `<a class="next-course-link" href="#course-${id}" data-course-link="${id}"><span>${id}</span><strong>${nextCourse.title}</strong>${otherPrerequisites}</a>`;
  }).join('');
}

function formatDownloadSize(bytes) {
  if (!Number.isInteger(bytes)) return '';
  return `${new Intl.NumberFormat('id-ID', { maximumFractionDigits: 1 }).format(bytes / 1_000_000)} MB`;
}

function deliveryBadges(course) {
  const delivery = learnerDeliveryByCourseId[course.id];
  if (!delivery) return '';
  const badges = [];
  if (delivery.online_html.status !== 'absent') badges.push('<span>HTML</span>');
  if (delivery.portable_html.status === 'verified') badges.push('<span class="verified">HTML luring terverifikasi</span>');
  if (delivery.epub.status === 'verified') badges.push('<span class="verified">EPUB terverifikasi</span>');
  if (delivery.capabilities.mathml.status === 'verified') badges.push('<span>MathML</span>');
  return badges.length ? `<div class="delivery-badges" aria-label="Format belajar tersedia">${badges.join('')}</div>` : '';
}

function actionLinks(course) {
  const links = [];
  const delivery = learnerDeliveryByCourseId[course.id];
  const portableHtml = delivery?.portable_html;
  const epub = delivery?.epub;
  const githubUnavailable = program.repositories.github.status === 'temporarily-unavailable';
  const learnerEntry = course.learner ?? course.reader;
  const readerIsSuspendedGithub = githubUnavailable && learnerEntry?.startsWith('https://github.com/KokunoYumeto/');
  const editionIsSuspendedGithub = githubUnavailable && course.edition?.startsWith('https://github.com/KokunoYumeto/');
  const repositoryIsSuspendedGithub = githubUnavailable && course.repository?.startsWith('https://github.com/KokunoYumeto/');
  const editionLabel = course.state === 'published' ? 'Buka edisi' : 'Buka edisi kerja';
  const learnerLabel = course.state === 'published' ? 'Mulai belajar — HTML' : 'Buka pembaca kerja — HTML';
  if (learnerEntry && !readerIsSuspendedGithub) links.push(`<a class="card-action primary" href="${learnerEntry}" target="_blank" rel="noreferrer">${learnerLabel} <span aria-hidden="true">↗</span></a>`);
  for (const tool of learnerToolsByCourseId[course.id] ?? []) {
    if (tool.state === 'planned') continue;
    links.push(`<a class="card-action learner-tool" href="${tool.href}">${tool.label} <span aria-hidden="true">→</span></a>`);
  }
  if (portableHtml?.status === 'verified') {
    links.push(`<a class="card-action offline" href="${portableHtml.url}" target="_blank" rel="noreferrer">Unduh HTML luring · ${formatDownloadSize(portableHtml.bytes)} <span aria-hidden="true">↓</span></a>`);
  }
  if (epub?.status === 'verified') {
    links.push(`<a class="card-action" href="${epub.url}" target="_blank" rel="noreferrer">Unduh EPUB · ${formatDownloadSize(epub.bytes)} <span aria-hidden="true">↓</span></a>`);
  }
  if (course.reader && course.reader !== learnerEntry && !readerIsSuspendedGithub) links.push(`<a class="card-action" href="${course.reader}" target="_blank" rel="noreferrer">Pembaca pemilik ↗</a>`);
  if (course.edition && course.edition !== learnerEntry && course.edition !== portableHtml?.url && course.edition !== epub?.url && !editionIsSuspendedGithub) links.push(`<a class="card-action${learnerEntry ? '' : ' primary'}" href="${course.edition}" target="_blank" rel="noreferrer">${editionLabel} <span aria-hidden="true">↗</span></a>`);
  if (course.zenodo) links.push(`<a class="card-action" href="${course.zenodo}" target="_blank" rel="noreferrer">Arsip DOI <span aria-hidden="true">↗</span></a>`);
  if (course.repository && course.repository !== course.edition && !repositoryIsSuspendedGithub) links.push(`<a class="card-action" href="${course.repository}" target="_blank" rel="noreferrer">Repositori <span aria-hidden="true">↗</span></a>`);
  if (course.release && !repositoryIsSuspendedGithub) links.push(`<a class="card-action" href="${course.release}" target="_blank" rel="noreferrer">Rilis <span aria-hidden="true">↗</span></a>`);
  for (const supplement of course.supplements ?? []) {
    const label = supplement.state === 'complete' ? supplement.title : `${supplement.title} — parsial`;
    links.push(`<a class="card-action" href="${supplement.url}" target="_blank" rel="noreferrer">${label} <span aria-hidden="true">↗</span></a>`);
  }
  if (!links.length) {
    const message = course.state === 'unresolved'
      ? 'Keputusan korpus masih terbuka'
      : editionIsSuspendedGithub
        ? 'Repositori GitHub sementara tidak tersedia'
        : 'Edisi sedang disiapkan';
    links.push(`<span class="card-action muted">${message}</span>`);
  }
  return links.join('');
}

function publicationProgress(course) {
  if (!course.progress) return '';
  const progress = course.progress;
  const stages = [
    ['Terjemahan', progress.translationBearingUnits],
    ['Siap integrasi', progress.integrationReadyUnits],
    ['Kanon', progress.canonicalUnits],
    ['Publik', progress.publicUnits],
  ].filter(([, value]) => Number.isInteger(value));
  const denominator = Number.isInteger(progress.totalUnits) ? `/${progress.totalUnits}` : '';
  const stageText = stages.map(([label, value]) => `${label} ${value}${denominator}`).join(' · ');
  const pageText = Number.isInteger(progress.publicPages) ? `${progress.publicPages.toLocaleString('id-ID')} halaman publik` : '';
  const boundaryText = progress.publicBoundary ?? '';
  const text = [stageText, pageText, boundaryText].filter(Boolean).join(' · ');
  return `<div><span>Progres ${progress.unitLabel}</span><p>${text}</p></div>`;
}

function learnerStatusBlock(course) {
  const evaluation = learnerEvaluation[course.id];
  const missing = evaluation.missingPrerequisiteIds.length
    ? `<small>Kurang: ${evaluation.missingPrerequisiteIds.join(', ')}</small>`
    : '<small>Semua prasyarat langsung terpenuhi.</small>';
  const checked = evaluation.status === 'completed' ? ' checked' : '';
  return `<div class="learner-course-state learner-${evaluation.status}">
    <div><strong>${learnerStatusLabels[evaluation.status]}</strong>${missing}</div>
    <label><input type="checkbox" data-completion="${course.id}"${checked}> Tandai selesai</label>
  </div>`;
}

function courseCard(course) {
  const selected = course.state !== 'unresolved';
  const learnerStatus = learnerEvaluation[course.id].status;
  return `
    <article class="course-card state-${course.state} learner-card-${learnerStatus}" id="course-${course.id}" data-course="${course.id}">
      <div class="card-topline">
        <span class="course-code">${course.id}</span>
        <span class="status status-${course.state}">${stateLabels[course.state]}</span>
      </div>
      <p class="course-topic">${course.topic}</p>
      <h3>${course.title}</h3>
      <p class="course-purpose">${course.purpose}</p>
      ${deliveryBadges(course)}
      ${learnerStatusBlock(course)}
      <div class="prerequisites"><span>Prasyarat</span><div>${prerequisiteLinks(course)}</div></div>
      <div class="next-courses"><span>Lanjut ke</span><div>${nextCourseLinks(course)}</div></div>
      <details>
        <summary>Detail mata kuliah</summary>
        <div class="detail-body">
          <div><span>${selected ? 'Korpus terpilih' : 'Kandidat — belum kanon'}</span><strong>${course.corpus}</strong></div>
          <div><span>Hasil belajar</span><p>${course.outcome}</p></div>
          ${publicationProgress(course)}
          <div><span>Keadaan edisi</span><p>${course.note}</p></div>
        </div>
      </details>
      <div class="card-actions">${actionLinks(course)}</div>
    </article>`;
}

function filteredCourses() {
  const query = normalize(searchInput.value.trim());
  return courses.filter((course) => {
    if (activeLevel !== 'all' && course.level !== activeLevel) return false;
    if (topicSelect.value !== 'all' && course.topic !== topicSelect.value) return false;
    if (statusSelect.value === 'selected' && course.state === 'unresolved') return false;
    if (statusSelect.value === 'unresolved' && course.state !== 'unresolved') return false;
    if (statusSelect.value === 'published' && course.state !== 'published') return false;
    if (statusSelect.value === 'production' && course.state !== 'production') return false;
    if (statusSelect.value === 'offline' && learnerDeliveryByCourseId[course.id]?.portable_html.status !== 'verified') return false;
    if (statusSelect.value === 'eligible' && !['eligible', 'eligible_with_waiver'].includes(learnerEvaluation[course.id].status)) return false;
    if (statusSelect.value === 'completed' && learnerEvaluation[course.id].status !== 'completed') return false;
    if (!query) return true;
    return normalize([course.id, course.title, course.topic, course.purpose, course.corpus].join(' ')).includes(query);
  });
}

function bindCourseLinks() {
  document.querySelectorAll('[data-course-link]').forEach((link) => {
    link.addEventListener('click', (event) => {
      const id = event.currentTarget.dataset.courseLink;
      if (!courses.some((course) => course.id === id)) return;
      event.preventDefault();
      resetFilters(false);
      requestAnimationFrame(() => {
        document.querySelector(`#course-${id}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' });
        history.replaceState(null, '', `#course-${id}`);
      });
    });
  });
}

function renderCourses() {
  const visible = filteredCourses();
  grid.innerHTML = visible.map(courseCard).join('');
  resultCount.textContent = `${visible.length} dari ${courses.length} mata kuliah ditampilkan`;
  document.querySelector('#empty-state').hidden = visible.length !== 0;
  bindCourseLinks();
  document.querySelectorAll('[data-completion]').forEach((control) => {
    control.addEventListener('change', () => {
      updateLearnerState(setCourseCompletion(learnerState, courses, control.dataset.completion, control.checked));
    });
  });
}

function setLevel(level) {
  activeLevel = level;
  levelButtons.forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.level === level)));
  renderCourses();
}

function resetFilters(scroll = true) {
  searchInput.value = '';
  topicSelect.value = 'all';
  statusSelect.value = 'all';
  setLevel('all');
  if (scroll) document.querySelector('#katalog').scrollIntoView({ behavior: 'smooth' });
}

function populateCourseSelect(select) {
  for (const course of courses) {
    const option = document.createElement('option');
    option.value = course.id;
    option.textContent = courseLabel(course);
    select.append(option);
  }
}

function updateWaiverPrerequisites() {
  const course = courses.find(({ id }) => id === waiverTarget.value);
  waiverPrerequisite.replaceChildren();
  for (const id of course?.prerequisites ?? []) {
    const prerequisite = courses.find((candidate) => candidate.id === id);
    const option = document.createElement('option');
    option.value = id;
    option.textContent = prerequisite ? courseLabel(prerequisite) : id;
    waiverPrerequisite.append(option);
  }
  document.querySelector('#add-waiver').disabled = waiverPrerequisite.options.length === 0;
}

function renderLearnerPanel() {
  const counts = Object.values(learnerEvaluation).reduce((result, { status }) => {
    result[status] = (result[status] ?? 0) + 1;
    return result;
  }, {});
  learnerSummary.textContent = `${counts.completed ?? 0} selesai • ${(counts.eligible ?? 0) + (counts.eligible_with_waiver ?? 0)} prasyarat terpenuhi • ${counts.blocked ?? 0} masih terhalang prasyarat`;

  const chips = [];
  for (const claim of learnerState.placementClaims) chips.push(`<span class="claim-chip">Penempatan: ${claim.courseId}<button type="button" data-remove-claim="placement" data-course-id="${claim.courseId}" aria-label="Hapus penempatan ${claim.courseId}">×</button></span>`);
  for (const claim of learnerState.equivalenceClaims) chips.push(`<span class="claim-chip">Kesetaraan: ${claim.courseId}<button type="button" data-remove-claim="equivalence" data-course-id="${claim.courseId}" aria-label="Hapus kesetaraan ${claim.courseId}">×</button></span>`);
  for (const waiver of learnerState.waivers) chips.push(`<span class="claim-chip">Waiver: ${waiver.targetCourseId} ← ${waiver.prerequisiteCourseId}<button type="button" data-remove-waiver="${waiver.targetCourseId}" data-prerequisite-id="${waiver.prerequisiteCourseId}" aria-label="Hapus waiver ${waiver.targetCourseId} dari ${waiver.prerequisiteCourseId}">×</button></span>`);
  learnerClaims.innerHTML = chips.length ? chips.join('') : '<span class="no-claims">Belum ada klaim penempatan, kesetaraan, atau waiver.</span>';
}

function updateLearnerState(nextState, statusMessage = null) {
  const saved = saveLearnerState(browserStorage, nextState, courses);
  learnerState = saved.state;
  learnerEvaluation = evaluateLearnerState(courses, learnerState);
  learnerStorageStatus.textContent = statusMessage ?? (saved.persisted
    ? 'Perubahan disimpan hanya di browser ini.'
    : 'Penyimpanan browser tidak tersedia; perubahan berlaku sampai halaman ditutup.');
  renderLearnerPanel();
  renderCourses();
}

for (const select of [placementCourse, equivalenceCourse, waiverTarget]) populateCourseSelect(select);
waiverTarget.value = 'D80';
updateWaiverPrerequisites();

document.querySelector('#add-placement').addEventListener('click', () => {
  updateLearnerState(setCourseClaim(learnerState, courses, 'placement', placementCourse.value, true));
});
document.querySelector('#add-equivalence').addEventListener('click', () => {
  updateLearnerState(setCourseClaim(learnerState, courses, 'equivalence', equivalenceCourse.value, true));
});
waiverTarget.addEventListener('change', updateWaiverPrerequisites);
document.querySelector('#add-waiver').addEventListener('click', () => {
  updateLearnerState(setPrerequisiteWaiver(learnerState, courses, waiverTarget.value, waiverPrerequisite.value, true));
});
document.querySelector('#reset-learner-state').addEventListener('click', () => {
  const cleared = clearLearnerState(browserStorage);
  learnerState = createEmptyLearnerState();
  learnerEvaluation = evaluateLearnerState(courses, learnerState);
  learnerStorageStatus.textContent = cleared
    ? 'Catatan kemajuan di browser ini telah dihapus.'
    : 'Tampilan telah direset, tetapi penyimpanan browser tidak dapat dihapus.';
  renderLearnerPanel();
  renderCourses();
});
learnerClaims.addEventListener('click', (event) => {
  const button = event.target.closest('button');
  if (!button) return;
  if (button.dataset.removeClaim) {
    updateLearnerState(setCourseClaim(learnerState, courses, button.dataset.removeClaim, button.dataset.courseId, false));
  } else if (button.dataset.removeWaiver) {
    updateLearnerState(setPrerequisiteWaiver(learnerState, courses, button.dataset.removeWaiver, button.dataset.prerequisiteId, false));
  }
});

levelButtons.forEach((button) => button.addEventListener('click', () => setLevel(button.dataset.level)));
searchInput.addEventListener('input', renderCourses);
topicSelect.addEventListener('change', renderCourses);
statusSelect.addEventListener('change', renderCourses);
resetButton.addEventListener('click', () => resetFilters());

learnerStorageStatus.textContent = loadedLearnerState.status === 'loaded'
  ? 'Catatan kemajuan dimuat dari browser ini.'
  : loadedLearnerState.status === 'recovered_invalid'
    ? 'Data lama tidak valid dan diabaikan; catatan dimulai kosong.'
    : loadedLearnerState.status === 'unavailable'
      ? 'Penyimpanan browser tidak tersedia; perubahan berlaku sampai halaman ditutup.'
      : 'Belum ada catatan kemajuan di browser ini.';

renderTopicControls();
renderLearnerPanel();
renderCourses();

const hashId = location.hash.match(/^#course-([A-D]\d{2,3})$/)?.[1];
if (hashId && courses.some((course) => course.id === hashId)) {
  requestAnimationFrame(() => document.querySelector(`#course-${hashId}`)?.scrollIntoView({ block: 'center' }));
}

// Existing root bookmarks remain valid; language links preserve the selected course.
document.querySelectorAll('[data-interface-locale]').forEach((link) => {
  const update = () => {
    const url = new URL(link.dataset.interfaceLocale + '/', location.href);
    url.search = location.search;
    url.hash = location.hash;
    link.href = url.href;
  };
  update();
  window.addEventListener('hashchange', update);
  link.addEventListener('click', update);
});
