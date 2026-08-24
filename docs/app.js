import { courses, program, topics } from './courses.js';

const stateLabels = {
  published: 'Edisi publik selesai',
  near: 'Hampir dirilis',
  production: 'Korpus terpilih',
  unresolved: 'Belum dibekukan'
};

const searchInput = document.querySelector('#course-search');
const topicSelect = document.querySelector('#topic-filter');
const statusSelect = document.querySelector('#status-filter');
const levelButtons = [...document.querySelectorAll('[data-level]')];
const topicLinks = document.querySelector('#topic-links');
const grid = document.querySelector('#course-grid');
const resultCount = document.querySelector('#result-count');
const resetButton = document.querySelector('#reset-filters');
let activeLevel = 'all';

function normalize(value) {
  return value.toLocaleLowerCase('id-ID').normalize('NFD').replace(/[\u0300-\u036f]/g, '');
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

function prerequisiteLinks(items) {
  if (!items.length) return '<span class="no-prereq">Tidak ada — mulai di sini atau gunakan diagnosis awal.</span>';
  return items.map((id) => `<a class="prereq-link" href="#course-${id}" data-course-link="${id}">${id}</a>`).join('');
}

function actionLinks(course) {
  const links = [];
  const githubUnavailable = program.repositories.github.status === 'temporarily-unavailable';
  const readerIsSuspendedGithub = githubUnavailable && course.reader?.startsWith('https://github.com/KokunoYumeto/');
  const editionIsSuspendedGithub = githubUnavailable && course.edition?.startsWith('https://github.com/KokunoYumeto/');
  const repositoryIsSuspendedGithub = githubUnavailable && course.repository?.startsWith('https://github.com/KokunoYumeto/');
  const editionLabel = course.state === 'published' ? 'Buka edisi' : 'Buka edisi kerja';
  if (course.reader && !readerIsSuspendedGithub) links.push(`<a class="card-action primary" href="${course.reader}" target="_blank" rel="noreferrer">Mulai belajar — HTML <span aria-hidden="true">↗</span></a>`);
  if (course.edition && course.edition !== course.reader && !editionIsSuspendedGithub) links.push(`<a class="card-action${course.reader ? '' : ' primary'}" href="${course.edition}" target="_blank" rel="noreferrer">${editionLabel} <span aria-hidden="true">↗</span></a>`);
  if (course.zenodo) links.push(`<a class="card-action" href="${course.zenodo}" target="_blank" rel="noreferrer">Arsip DOI <span aria-hidden="true">↗</span></a>`);
  if (course.repository && course.repository !== course.edition && !repositoryIsSuspendedGithub) links.push(`<a class="card-action" href="${course.repository}" target="_blank" rel="noreferrer">Repositori <span aria-hidden="true">↗</span></a>`);
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

function courseCard(course) {
  const selected = course.state !== 'unresolved';
  return `
    <article class="course-card state-${course.state}" id="course-${course.id}" data-course="${course.id}">
      <div class="card-topline">
        <span class="course-code">${course.id}</span>
        <span class="status status-${course.state}">${stateLabels[course.state]}</span>
      </div>
      <p class="course-topic">${course.topic}</p>
      <h3>${course.title}</h3>
      <p class="course-purpose">${course.purpose}</p>
      <div class="prerequisites">
        <span>Prasyarat</span>
        <div>${prerequisiteLinks(course.prerequisites)}</div>
      </div>
      <details>
        <summary>Detail mata kuliah</summary>
        <div class="detail-body">
          <div><span>${selected ? 'Korpus terpilih' : 'Kandidat — belum kanon'}</span><strong>${course.corpus}</strong></div>
          <div><span>Hasil belajar</span><p>${course.outcome}</p></div>
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
    if (!query) return true;
    return normalize([course.id, course.title, course.topic, course.purpose, course.corpus].join(' ')).includes(query);
  });
}

function renderCourses() {
  const visible = filteredCourses();
  grid.innerHTML = visible.map(courseCard).join('');
  resultCount.textContent = `${visible.length} dari ${courses.length} mata kuliah ditampilkan`;
  document.querySelector('#empty-state').hidden = visible.length !== 0;
  document.querySelectorAll('[data-course-link]').forEach((link) => {
    link.addEventListener('click', (event) => {
      const id = event.currentTarget.dataset.courseLink;
      const target = courses.find((course) => course.id === id);
      if (!target) return;
      event.preventDefault();
      resetFilters(false);
      requestAnimationFrame(() => {
        document.querySelector(`#course-${id}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' });
        history.replaceState(null, '', `#course-${id}`);
      });
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

levelButtons.forEach((button) => button.addEventListener('click', () => setLevel(button.dataset.level)));
searchInput.addEventListener('input', renderCourses);
topicSelect.addEventListener('change', renderCourses);
statusSelect.addEventListener('change', renderCourses);
resetButton.addEventListener('click', () => resetFilters());

renderTopicControls();
renderCourses();

const hashId = location.hash.match(/^#course-([A-D]\d+)$/)?.[1];
if (hashId && courses.some((course) => course.id === hashId)) {
  requestAnimationFrame(() => document.querySelector(`#course-${hashId}`)?.scrollIntoView({ block: 'center' }));
}
