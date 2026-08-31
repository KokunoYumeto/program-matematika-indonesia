const dataUrl = './assessment-map-v1.json';

const moduleGrid = document.querySelector('#assessment-module-grid');
const staticFallback = document.querySelector('#assessment-static-fallback');
const status = document.querySelector('#assessment-result-status');
const search = document.querySelector('#assessment-search');
const category = document.querySelector('#assessment-category');
const solution = document.querySelector('#assessment-solution');
const reset = document.querySelector('#assessment-reset');

let assessmentMap = null;

const number = (value) => new Intl.NumberFormat('id-ID').format(value);

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function externalLink(label, href, className = '') {
  const link = element('a', className, label);
  link.href = href;
  link.target = '_blank';
  link.rel = 'noreferrer';
  return link;
}

function filteredAssessments(module, query, selectedCategory, selectedSolution) {
  return module.assessments.filter((item) => {
    if (selectedCategory !== 'all' && item.category !== selectedCategory) return false;
    if (selectedSolution === 'with' && !item.has_explicit_solution) return false;
    if (selectedSolution === 'without' && item.has_explicit_solution) return false;
    if (!query) return true;
    return [module.module_id, module.title, item.native_id, item.category_label]
      .some((value) => value.toLocaleLowerCase('id-ID').includes(query));
  });
}

function renderAssessment(item) {
  const row = element('li', 'assessment-item');
  const copy = element('div', 'assessment-item-copy');
  const title = element('strong', '', `Latihan ${number(item.ordinal)}`);
  const meta = element('span', '', item.category_label);
  const availability = element(
    'span',
    item.has_explicit_solution ? 'solution-state has-solution' : 'solution-state no-solution',
    item.has_explicit_solution ? 'solusi eksplisit tersedia' : 'tanpa solusi eksplisit dalam sumber',
  );
  copy.append(title, meta, availability);

  const actions = element('div', 'assessment-item-actions');
  actions.append(externalLink('Buka latihan ↗', item.route_url));
  if (item.solution_anchors.length === 1) {
    actions.append(externalLink('Buka solusi ↗', item.solution_anchors[0].route_url));
  }
  row.append(copy, actions);
  return row;
}

function renderModule(module, matching) {
  const card = element('article', 'assessment-module-card');
  const heading = element('div', 'assessment-module-heading');
  const titleWrap = element('div');
  titleWrap.append(
    element('span', 'module-code', `${String(module.ordinal).padStart(2, '0')} · ${module.module_id}`),
    element('h2', '', module.title),
  );
  heading.append(titleWrap, externalLink('Buka modul ↗', module.module_url, 'module-link'));

  const metrics = element('div', 'assessment-module-metrics');
  const withSolution = matching.filter((item) => item.has_explicit_solution).length;
  const withoutSolution = matching.length - withSolution;
  for (const [value, label] of [
    [matching.length, 'latihan cocok'],
    [withSolution, 'dengan solusi'],
    [withoutSolution, 'tanpa solusi sumber'],
  ]) {
    const metric = element('span');
    metric.append(element('strong', '', number(value)), document.createTextNode(` ${label}`));
    metrics.append(metric);
  }
  card.append(heading, metrics);

  if (matching.length) {
    const details = element('details', 'assessment-list-shell');
    const summary = element('summary', '', `Lihat ${number(matching.length)} latihan`);
    const list = element('ol', 'assessment-list');
    let filled = false;
    details.addEventListener('toggle', () => {
      if (!details.open || filled) return;
      const fragment = document.createDocumentFragment();
      for (const item of matching) fragment.append(renderAssessment(item));
      list.append(fragment);
      filled = true;
    });
    details.append(summary, list);
    card.append(details);
  } else {
    card.append(element('p', 'empty-module', 'Tidak ada latihan yang cocok dengan saringan ini.'));
  }
  return card;
}

function render() {
  if (!assessmentMap) return;
  const query = search.value.trim().toLocaleLowerCase('id-ID');
  const selectedCategory = category.value;
  const selectedSolution = solution.value;
  const fragment = document.createDocumentFragment();
  let visibleModules = 0;
  let visibleAssessments = 0;

  for (const module of assessmentMap.modules) {
    const matching = filteredAssessments(module, query, selectedCategory, selectedSolution);
    const moduleTextMatch = !query || [module.module_id, module.title]
      .some((value) => value.toLocaleLowerCase('id-ID').includes(query));
    if (!matching.length && !moduleTextMatch) continue;
    visibleModules += 1;
    visibleAssessments += matching.length;
    fragment.append(renderModule(module, matching));
  }

  moduleGrid.replaceChildren(fragment);
  status.textContent = `${number(visibleAssessments)} latihan dalam ${number(visibleModules)} modul ditampilkan`;
}

async function start() {
  try {
    const response = await fetch(dataUrl, { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    assessmentMap = await response.json();
    if (!Array.isArray(assessmentMap?.modules) || assessmentMap.modules.length !== 75) {
      throw new Error('Peta latihan tidak lengkap.');
    }
    for (const [key, label] of Object.entries(assessmentMap.category_labels)) {
      const option = document.createElement('option');
      option.value = key;
      option.textContent = label;
      category.append(option);
    }
    render();
    staticFallback.hidden = true;
  } catch (error) {
    status.textContent = 'Peta latihan tidak dapat dimuat. Gunakan daftar modul statis di bawah atau buka pembaca utama.';
    console.error(error);
  }
}

for (const control of [search, category, solution]) {
  control.addEventListener(control === search ? 'input' : 'change', render);
}
reset.addEventListener('click', () => {
  search.value = '';
  category.value = 'all';
  solution.value = 'all';
  render();
  search.focus();
});

start();
