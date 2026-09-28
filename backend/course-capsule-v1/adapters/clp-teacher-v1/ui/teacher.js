/* CLP source-identity assignment planner. No network, analytics, or storage. */
(() => {
  'use strict';
  const has = (q, kind, minimum = 1) => q.surfaces.some(s => s.components[kind].length >= minimum);
  const matches = (q, section, support, search) => {
    if (section && q.section !== section) return false;
    if (support === 'hint' && !has(q, 'hint')) return false;
    if (support === 'nohint' && has(q, 'hint')) return false;
    if (support === 'multi' && !has(q, 'solution', 2)) return false;
    return !search || JSON.stringify([q.id, q.native_id, q.section, q.label]).toLowerCase().includes(search.toLowerCase());
  };
  const exportSelection = (model, selected, locale) => ({
    schema: 'clp-assignment-selection/1', course_id: model.course_id, locale,
    input_sha256: model.input_identity.sha256, archive: model.archive,
    boundary: model.limitations[locale],
    exercises: model.questions.filter(q => selected.has(q.id)),
  });
  const importSelection = (model, data) => {
    if (data.schema !== 'clp-assignment-selection/1' || data.course_id !== model.course_id ||
        data.input_sha256 !== model.input_identity.sha256 || !Array.isArray(data.exercises)) {
      throw new Error('wrong-corpus');
    }
    const known = new Map(model.questions.map(q => [q.id, q])), ids = new Set();
    for (const q of data.exercises) {
      if (!known.has(q.id) || ids.has(q.id) || JSON.stringify(q) !== JSON.stringify(known.get(q.id))) {
        throw new Error('unknown-or-changed-exercise');
      }
      ids.add(q.id);
    }
    return ids;
  };
  globalThis.CLPTeacher = Object.freeze({has, matches, exportSelection, importSelection});
  if (typeof document === 'undefined') return;
  const {model, locale, words} = JSON.parse(document.getElementById('planner-data').textContent);
  const en = locale === 'en', $ = id => document.getElementById(id);
  let selected = new Set(), visible = [], limit = 60;
  const labels = en ? {question: 'Question', hint: 'Hint', answer: 'Answer', solution: 'Solution'}
    : {question: 'Soal', hint: 'Petunjuk', answer: 'Jawaban', solution: 'Penyelesaian'};
  function element(tag, text, className) {
    const e = document.createElement(tag);
    if (text !== undefined) e.textContent = text;
    if (className) e.className = className;
    return e;
  }
  function updateStatus(total) {
    $('status').textContent = en ? `${selected.size} selected · ${visible.length} shown of ${total} matching exercises`
      : `${selected.size} dipilih · ${visible.length} tampil dari ${total} soal yang sesuai`;
  }
  function render() {
    const matching = model.questions.filter(q => matches(q, $('section').value, $('support').value, $('search').value));
    visible = matching.slice(0, limit);
    const fragment = document.createDocumentFragment();
    for (const q of visible) {
      const article = element('article');
      article.classList.toggle('selected', selected.has(q.id));
      const label = element('label', undefined, 'question-label'), checkbox = element('input');
      checkbox.type = 'checkbox'; checkbox.checked = selected.has(q.id);
      checkbox.addEventListener('change', () => {
        if (checkbox.checked) selected.add(q.id); else selected.delete(q.id);
        article.classList.toggle('selected', checkbox.checked); updateStatus(matching.length);
      });
      label.append(checkbox, document.createTextNode(`${words.choose} ${q.label} · ${q.section}`));
      article.append(label, element('p', q.native_id, 'identity'));
      for (const s of q.surfaces) {
        article.append(element('p', `${s.format} · ` + Object.entries(labels).map(([key, title]) => `${title}: ${s.components[key].length}`).join(' · ')));
      }
      const details = element('details'); details.append(element('summary', words.details));
      details.addEventListener('toggle', () => {
        if (!details.open || details.dataset.loaded) return;
        for (const s of q.surfaces) {
          details.append(element('h3', s.format));
          details.append(element('p', (en ? 'English source: ' : 'Sumber Inggris: ') + JSON.stringify(s.source)));
          details.append(element('p', (en ? 'Indonesian alignment: ' : 'Pemetaan Bahasa Indonesia: ') + JSON.stringify(s.target)));
          details.append(element('pre', JSON.stringify(s, null, 2)));
        }
        details.dataset.loaded = 'true';
      });
      article.append(details); fragment.append(article);
    }
    if (visible.length < matching.length) {
      const more = element('button', en ? 'Show 60 more' : 'Tampilkan 60 lagi');
      more.addEventListener('click', () => {limit += 60; render();}); fragment.append(more);
    }
    $('exercises').replaceChildren(fragment); updateStatus(matching.length);
  }
  for (const id of ['section', 'support', 'search']) $(id).addEventListener('input', () => {limit = 60; render();});
  $('select-visible').addEventListener('click', () => {visible.forEach(q => selected.add(q.id)); render();});
  $('clear').addEventListener('click', () => {selected.clear(); render();});
  $('export').addEventListener('click', () => {
    const data = exportSelection(model, selected, locale);
    const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2) + '\n'], {type: 'application/json'}));
    const a = element('a'); a.href = url; a.download = `${model.course_id}-CLP-${locale}-assignment.json`;
    document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  $('import').addEventListener('change', async () => {
    $('error').textContent = '';
    try {
      const f = $('import').files[0]; if (!f) return;
      if (f.size > 16 * 1024 * 1024) throw new Error('too-large');
      const imported = importSelection(model, JSON.parse(await f.text()));
      selected = imported; render();
    } catch {
      $('error').textContent = en ? 'Import rejected: wrong edition, changed or repeated exercise, or invalid file. Your selection was not changed.'
        : 'Impor ditolak: edisi salah, soal berubah atau berulang, atau berkas tidak sah. Pilihan Anda tidak berubah.';
    } finally { $('import').value = ''; }
  });
  $('print').addEventListener('click', () => {
    const area = element('section', undefined, 'print-selection');
    area.append(element('h1', `${model.course_id} · ${words.title}`), element('p', model.limitations[locale]));
    const list = element('ol');
    for (const q of model.questions.filter(q => selected.has(q.id))) list.append(element('li', `${q.section} · ${q.label}\n${q.native_id}`));
    area.append(list); document.body.append(area); window.print(); area.remove();
  });
  render();
})();
