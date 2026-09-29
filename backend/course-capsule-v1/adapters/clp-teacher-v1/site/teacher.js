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
    ...(model.navigation_identity ? {navigation_sha256: model.navigation_identity.sha256} : {}),
    exercises: model.questions.filter(q => selected.has(q.id)),
  });
  const importSelection = (model, data) => {
    if (data.schema !== 'clp-assignment-selection/1' || data.course_id !== model.course_id ||
        data.input_sha256 !== model.input_identity.sha256 || !Array.isArray(data.exercises)) {
      throw new Error('wrong-corpus');
    }
    const known = new Map(model.questions.map(q => [q.id, q])), ids = new Set();
    if (data.navigation_sha256 !== undefined && data.navigation_sha256 !== model.navigation_identity?.sha256) {
      throw new Error('wrong-navigation-edition');
    }
    for (const q of data.exercises) {
      const current = known.get(q.id);
      // Old source-bound assignments remain usable. Only the absent derived
      // navigation may be supplied from this verified model; never ignore a
      // changed or partially supplied navigation object.
      let expected = current;
      if (current?.navigation && !Object.hasOwn(q, 'navigation') && data.navigation_sha256 === undefined) {
        expected = {...current}; delete expected.navigation;
      }
      if (!current || ids.has(q.id) || JSON.stringify(q) !== JSON.stringify(expected)) {
        throw new Error('unknown-or-changed-exercise');
      }
      ids.add(q.id);
    }
    return ids;
  };
  const readingLinks = (model, q) => {
    if (!q.navigation) return [];
    const reader = model.navigation_reader;
    if (!reader || !model.navigation_identity) throw new Error('missing-reader-binding');
    const base = new URL(reader.url);
    if (base.protocol !== 'https:' || base.hostname !== 'zenodo.org') throw new Error('invalid-reader-origin');
    // Keep the canonical download identity in metadata, but do not request an
    // attachment when the learner follows a page reference in a PDF viewer.
    base.searchParams.delete('download');
    return [{kind:'question',...q.navigation.printed}, ...q.navigation.supports.map(s => ({kind:s.kind,...s.printed}))].map(item => {
      if (!Number.isInteger(item.page) || item.page < 1 || item.page > reader.pages || item.fragment !== `page=${item.page}`) {
        throw new Error('invalid-reader-page');
      }
      const url = new URL(base); url.hash = item.fragment;
      return {kind:item.kind, page:item.page, url:url.href};
    });
  };
  globalThis.CLPTeacher = Object.freeze({has, matches, exportSelection, importSelection, readingLinks});
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
      const reading = readingLinks(model, q);
      if (reading.length) {
        const links = element('nav', undefined, 'reading-links');
        links.setAttribute('aria-label', en ? 'Indonesian PDF references' : 'Rujukan PDF Bahasa Indonesia');
        for (const item of reading) {
          const a = element('a', `${labels[item.kind]} · PDF ${item.page}`);
          a.href = item.url; a.hreflang = 'id'; a.target = '_blank'; a.rel = 'noopener';
          links.append(a);
        }
        article.append(links);
      }
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
        if (q.navigation) details.append(element('pre', JSON.stringify(q.navigation, null, 2)));
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
  function showJSON() {
    const text = JSON.stringify(exportSelection(model, selected, locale), null, 2) + '\n';
    $('assignment-text').value = text;
    $('exchange').open = true;
    return text;
  }
  function importError() {
    $('error').textContent = en ? 'Import rejected: wrong edition, changed or repeated exercise, or invalid file. Your selection was not changed.'
      : 'Impor ditolak: edisi salah, soal berubah atau berulang, atau berkas tidak sah. Pilihan Anda tidak berubah.';
  }
  function loadJSON(text) {
    if (text.length > 16 * 1024 * 1024) throw new Error('too-large');
    const imported = importSelection(model, JSON.parse(text));
    selected = imported; render();
  }
  $('show-json').addEventListener('click',showJSON);
  $('load-text').addEventListener('click', () => {
    $('error').textContent = '';
    try { loadJSON($('assignment-text').value); } catch { importError(); }
  });
  $('export').addEventListener('click', () => {
    const text = showJSON();
    const url = URL.createObjectURL(new Blob([text], {type: 'application/json'}));
    const a = element('a'); a.href = url; a.download = `${model.course_id}-CLP-${locale}-assignment.json`;
    document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  $('import').addEventListener('change', async () => {
    $('error').textContent = '';
    try {
      const f = $('import').files[0]; if (!f) return;
      if (f.size > 16 * 1024 * 1024) throw new Error('too-large');
      loadJSON(await f.text());
    } catch {
      importError();
    } finally { $('import').value = ''; }
  });
  $('print').addEventListener('click', () => {
    const area = element('section', undefined, 'print-selection');
    area.append(element('h1', `${model.course_id} · ${words.title}`), element('p', model.limitations[locale]));
    const list = element('ol');
    for (const q of model.questions.filter(q => selected.has(q.id))) {
      const references = readingLinks(model,q).map(r => `${labels[r.kind]}: PDF ${r.page}`).join(' · ');
      list.append(element('li', `${q.section} · ${q.label}\n${q.native_id}${references ? '\n'+references : ''}`));
    }
    area.append(list); document.body.append(area); window.print(); area.remove();
  });
  render();
})();
