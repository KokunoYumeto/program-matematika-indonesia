/* Source-bound reference planner. No network requests or persistent storage. */
(() => {
  'use strict';
  const canonical = value => JSON.stringify(value, (key, item) =>
    item && typeof item === 'object' && !Array.isArray(item)
      ? Object.fromEntries(Object.keys(item).sort().map(k => [k, item[k]])) : item);
  function matches(q, topic, chapter, reused, search) {
    if (topic && q.topic !== topic || chapter && q.chapter !== chapter || reused && q.source_reuse_count < 2) return false;
    const term = search.trim().toLowerCase();
    return !term || [q.id, q.source_problem_id, q.unit_id, q.number, q.section_title_id || '',
      q.mapping.source_path, q.mapping.target_path].some(s => s.toLowerCase().includes(term));
  }
  function exportSelection(model, selected, locale) {
    const known = new Set(model.questions.map(q => q.id));
    if (!['id', 'en'].includes(locale) || [...selected].some(id => !known.has(id))) throw Error('invalid-selection');
    return {schema: 'openlogic-assignment-selection/1', course_id: 'C80', locale,
      edition_binding: model.edition_binding, reader: model.reader, reference_only: true,
      exercises: model.questions.filter(q => selected.has(q.id))};
  }
  function importSelection(model, packet) {
    if (!packet || packet.schema !== 'openlogic-assignment-selection/1' || packet.course_id !== 'C80' ||
      packet.edition_binding !== model.edition_binding || packet.reference_only !== true ||
      !['id', 'en'].includes(packet.locale) || !Array.isArray(packet.exercises)) throw Error('wrong-corpus');
    const known = new Map(model.questions.map(q => [q.id, q])), selected = new Set();
    for (const q of packet.exercises) {
      if (!q || !known.has(q.id) || selected.has(q.id) || canonical(q) !== canonical(known.get(q.id))) throw Error('changed-reference');
      selected.add(q.id);
    }
    if (canonical(packet) !== canonical(exportSelection(model, selected, packet.locale))) throw Error('changed-envelope-or-order');
    return selected;
  }
  globalThis.OpenLogicTeacher = Object.freeze({matches, exportSelection, importSelection});
  if (typeof document === 'undefined') return;
  const {model, locale, words: w} = JSON.parse(document.getElementById('planner-data').textContent);
  const en = locale === 'en', $ = id => document.getElementById(id);
  let selected = new Set(), visible = [], limit = 50, downloadUrl = null;
  const el = (tag, text, cls) => {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (cls) node.className = cls;
    return node;
  };
  const title = q => `${w[q.component]} · ${w.exercise} ${q.number} · ${w.page} ${q.physical_page}`;
  function status(total) {
    $('status').textContent = en ? `${selected.size} selected · ${visible.length} displayed of ${total} matching references`
      : `${selected.size} dipilih · ${visible.length} tampil dari ${total} rujukan yang sesuai`;
  }
  function render() {
    const all = model.questions.filter(q => matches(q, $('topic').value, $('chapter').value,
      $('reused-only').checked, $('search').value) && (!$('selected-only').checked || selected.has(q.id)));
    visible = all.slice(0, limit);
    const fragment = document.createDocumentFragment();
    for (const q of visible) {
      const card = el('article'); card.classList.toggle('selected', selected.has(q.id));
      const label = el('label', undefined, 'question-label'), checkbox = el('input');
      checkbox.type = 'checkbox'; checkbox.checked = selected.has(q.id); checkbox.dataset.exerciseId = q.id;
      checkbox.addEventListener('change', () => {
        if (checkbox.checked) selected.add(q.id); else selected.delete(q.id);
        card.classList.toggle('selected', checkbox.checked);
        if ($('selected-only').checked) render(); else status(all.length);
      });
      label.append(checkbox, document.createTextNode(`${w.choose}: ${title(q)}`));
      card.append(label, el('p', model.topics[q.topic][locale]));
      if (q.section_title_id) { const section = el('p', q.section_title_id); section.lang = 'id'; card.append(section); }
      if (q.source_reuse_count > 1) card.append(el('p', en ? `Source reused in ${q.source_reuse_count} reader contexts`
        : `Sumber digunakan dalam ${q.source_reuse_count} konteks pembaca`, 'badge'));
      const link = el('a', `${w.read} · Bahasa Indonesia`); link.lang = 'id';
      link.href = $('local-reader').checked ? q.local_reader_url : q.reader_url;
      const line = el('p'); line.append(link); card.append(line, el('p', w.notaudited, 'detail'), el('code', q.id));
      const details = el('details'); details.append(el('summary', w.details));
      details.addEventListener('toggle', () => {
        if (details.open && !details.dataset.loaded) { details.append(el('pre', JSON.stringify(q.mapping, null, 2))); details.dataset.loaded = 'true'; }
      });
      card.append(details); fragment.append(card);
    }
    if (visible.length < all.length) {
      const more = el('button', en ? 'Show 50 more' : 'Tampilkan 50 lagi'); more.id = 'show-more';
      more.addEventListener('click', () => {limit += 50; render();}); fragment.append(more);
    }
    $('exercises').replaceChildren(fragment); status(all.length);
  }
  for (const id of ['topic','chapter','search','reused-only','selected-only','local-reader']) {
    $(id).addEventListener('input', () => {limit = 50; render();});
  }
  $('select-visible').addEventListener('click', () => {visible.forEach(q => selected.add(q.id)); render();});
  $('clear').addEventListener('click', () => {selected.clear(); render();});
  $('export').addEventListener('click', () => {
    const packet = exportSelection(model, selected, locale);
    const text = JSON.stringify(packet,null,2)+'\n';
    $('packet').value = text; $('exchange').open = true;
    if (downloadUrl) URL.revokeObjectURL(downloadUrl);
    downloadUrl = URL.createObjectURL(new Blob([text], {type:'application/json'}));
    $('download').href = downloadUrl; $('download').download = `C80-OpenLogic-${locale}-assignment.json`;
    $('download').hidden = false;
  });
  function restore(text) {
    if (text.length > 8*1024*1024) throw Error('too-large');
    const restored = importSelection(model, JSON.parse(text));
    selected = restored; render();
  }
  function importError() {
    $('error').textContent = en ? 'Import rejected: wrong edition, invalid file, or changed/duplicate references. Your selection was not changed.'
      : 'Impor ditolak: edisi salah, berkas tidak sah, atau rujukan berubah/berulang. Pilihan Anda tidak berubah.';
  }
  $('apply-packet').addEventListener('click', () => {
    $('error').textContent = '';
    try {restore($('packet').value);} catch {importError();}
  });
  $('import').addEventListener('change', async () => {
    $('error').textContent = '';
    try {
      const file = $('import').files[0]; if (!file) return;
      if (file.size > 8*1024*1024) throw Error('too-large');
      restore(await file.text());
    } catch {
      importError();
    } finally { $('import').value = ''; }
  });
  $('print').addEventListener('click', () => {
    $('error').textContent = '';
    if (!selected.size) { $('error').textContent = en ? 'Select exercises before printing.' : 'Pilih soal sebelum mencetak.'; return; }
    const area = el('section', undefined, 'print-selection');
    area.append(el('h1', `C80 · ${w.title}`), el('p', model.limitations[locale]), el('p', `PDF SHA-256: ${model.reader.sha256}`));
    const list = el('ol');
    for (const q of model.questions.filter(q => selected.has(q.id))) {
      const li = el('li', `${title(q)}\n${model.topics[q.topic][locale]}\n${q.id}\n`);
      const link = el('a', q.reader_url); link.href = q.reader_url; li.append(link); list.append(li);
    }
    area.append(list); document.body.append(area);
    try {window.print();} finally {area.remove();}
  });
  render();
})();
