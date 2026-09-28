/* Judson exercise-reference planner. No requests, analytics, or persistent storage. */
(() => {
  'use strict';
  const canonical = value => JSON.stringify(value, function (key, item) {
    return item && typeof item === 'object' && !Array.isArray(item)
      ? Object.fromEntries(Object.keys(item).sort().map(k => [k, item[k]])) : item;
  });
  function matches(q, chapter, support, search) {
    if (chapter && q.chapter_id !== chapter) return false;
    if (support === 'hint' && !q.hint_count) return false;
    if (support === 'nohint' && q.hint_count) return false;
    if (support === 'response' && !q.response_slot_count) return false;
    if (support === 'sage' && q.primary_edition !== 'sage') return false;
    return !search || [q.id, q.native_id, q.source_path, q.source_xpath, q.target_identifier, q.label]
      .some(s => s.toLowerCase().includes(search.toLowerCase()));
  }
  function exportSelection(model, selected, locale) {
    const known = new Set(model.questions.map(q => q.id));
    if (!['id', 'en'].includes(locale) || [...selected].some(id => !known.has(id))) throw new Error('invalid-selection');
    return {schema: 'judson-assignment-selection/1', course_id: model.course_id, locale,
      input_sha256: model.input_identity.sha256, source_archive_sha256: model.archives.source.sha256,
      reference_only: true, exercises: model.questions.filter(q => selected.has(q.id))};
  }
  function importSelection(model, data) {
    if (!data || data.schema !== 'judson-assignment-selection/1' || data.course_id !== model.course_id ||
        data.input_sha256 !== model.input_identity.sha256 || data.source_archive_sha256 !== model.archives.source.sha256 ||
        data.reference_only !== true || !['id', 'en'].includes(data.locale) || !Array.isArray(data.exercises)) throw new Error('wrong-corpus');
    const known = new Map(model.questions.map(q => [q.id, q])), ids = new Set();
    for (const q of data.exercises) {
      if (!q || !known.has(q.id) || ids.has(q.id) || canonical(q) !== canonical(known.get(q.id))) throw new Error('changed-exercise');
      ids.add(q.id);
    }
    if (canonical(data) !== canonical(exportSelection(model, ids, data.locale))) throw new Error('changed-envelope-or-order');
    return ids;
  }
  globalThis.JudsonTeacher = Object.freeze({matches, exportSelection, importSelection});
  if (typeof document === 'undefined') return;
  const {model, locale, words} = JSON.parse(document.getElementById('planner-data').textContent);
  const en = locale === 'en', $ = id => document.getElementById(id);
  const chapters = new Map(model.chapters.map(c => [c.native_unit_id, c]));
  let selected = new Set(), visible = [], limit = 50;
  const el = (tag, text, cls) => {
    const n = document.createElement(tag);
    if (text !== undefined) n.textContent = text;
    if (cls) n.className = cls;
    return n;
  };
  const chapterTitle = q => chapters.get(q.chapter_id)[en ? 'english_title' : 'localized_title'];
  const groupTitle = q => q.exercise_group_kind === 'reading-questions'
    ? (en ? 'Reading question' : 'Pertanyaan bacaan') : (en ? 'Exercise' : 'Latihan');
  function updateStatus(total) {
    $('status').textContent = en ? `${selected.size} selected · ${visible.length} displayed of ${total} matching exercises`
      : `${selected.size} dipilih · ${visible.length} tampil dari ${total} soal yang sesuai`;
  }
  function readerLinks(q, container) {
    const online = el('a', en ? 'Read this exercise online · Bahasa Indonesia' : 'Baca soal ini daring · Bahasa Indonesia');
    online.href = q.current_reader_url; online.lang = 'id';
    const onlineLine = el('p'); onlineLine.append(online); container.append(onlineLine);
    for (const r of q.readers) {
      const line = el('p', undefined, 'reader');
      const a = el('a', (en ? 'Download frozen ' : 'Unduh arsip beku ') + r.edition.toUpperCase());
      a.href = model.archives[r.edition].public_url;
      line.append(a, document.createTextNode(' · Bahasa Indonesia'));
      if ($('local-books').checked) {
        const local = el('a', en ? 'Open local exercise' : 'Buka soal lokal');
        local.href = r.offline_href; local.lang = 'id'; line.append(document.createTextNode(' · '), local);
      }
      line.append(el('code', r.member + '#' + r.fragment)); container.append(line);
    }
  }
  function render() {
    const matching = model.questions.filter(q => matches(q, $('chapter').value, $('support').value, $('search').value)
      && (!$('selected-only').checked || selected.has(q.id)));
    visible = matching.slice(0, limit);
    const fragment = document.createDocumentFragment();
    for (const q of visible) {
      const article = el('article'); article.classList.toggle('selected', selected.has(q.id));
      const label = el('label', undefined, 'question-label'), check = el('input');
      check.type = 'checkbox'; check.checked = selected.has(q.id); check.dataset.exerciseId = q.id;
      check.addEventListener('change', () => {
        if (check.checked) selected.add(q.id); else selected.delete(q.id);
        article.classList.toggle('selected', check.checked);
        if ($('selected-only').checked) render(); else updateStatus(matching.length);
      });
      label.append(check, document.createTextNode(`${words.choose}: ${chapterTitle(q)} · ${groupTitle(q)} ${q.label}`));
      article.append(label, el('p', q.source_path + ' · ' + q.group_path, 'identity'));
      article.append(el('p', (en ? 'Supplied hints: ' : 'Petunjuk yang disediakan: ') + q.hint_count + ' · ' +
        (en ? 'Empty response slots: ' : 'Ruang respons kosong: ') + q.response_slot_count));
      if (q.primary_edition === 'sage') article.append(el('p', words.sage, 'badge'));
      readerLinks(q, article);
      const details = el('details'); details.append(el('summary', words.details));
      details.addEventListener('toggle', () => {
        if (details.open && !details.dataset.loaded) {
          details.append(el('pre', JSON.stringify(q, null, 2))); details.dataset.loaded = 'true';
        }
      });
      article.append(details); fragment.append(article);
    }
    if (visible.length < matching.length) {
      const more = el('button', en ? 'Show 50 more' : 'Tampilkan 50 lagi'); more.id = 'show-more';
      more.addEventListener('click', () => {limit += 50; render();}); fragment.append(more);
    }
    $('exercises').replaceChildren(fragment); updateStatus(matching.length);
  }
  for (const id of ['chapter', 'support', 'search', 'selected-only', 'local-books']) {
    $(id).addEventListener('input', () => {limit = 50; render();});
  }
  $('select-visible').addEventListener('click', () => {visible.forEach(q => selected.add(q.id)); render();});
  $('clear').addEventListener('click', () => {selected.clear(); render();});
  $('export').addEventListener('click', () => {
    const data = exportSelection(model, selected, locale);
    const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2) + '\n'], {type: 'application/json'}));
    const a = el('a'); a.href = url; a.download = `${model.course_id}-Judson-${locale}-assignment.json`;
    document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  $('import').addEventListener('change', async () => {
    $('error').textContent = '';
    try {
      const file = $('import').files[0]; if (!file) return;
      if (file.size > 8 * 1024 * 1024) throw new Error('too-large');
      const result = importSelection(model, JSON.parse(await file.text()));
      selected = result; render();
    } catch {
      $('error').textContent = en ? 'Import rejected: invalid file, wrong edition, or changed/duplicate exercises. Your selection was not changed.'
        : 'Impor ditolak: berkas tidak sah, edisi salah, atau soal berubah/berulang. Pilihan Anda tidak berubah.';
    } finally { $('import').value = ''; }
  });
  $('print').addEventListener('click', () => {
    $('error').textContent = '';
    if (!selected.size) { $('error').textContent = en ? 'Select exercises before printing.' : 'Pilih soal sebelum mencetak.'; return; }
    const area = el('section', undefined, 'print-selection');
    area.append(el('h1', `${model.course_id} · ${words.title}`), el('p', model.limitations[locale]));
    const list = el('ol');
    for (const q of model.questions.filter(q => selected.has(q.id))) {
      const r = q.readers.find(r => r.edition === q.primary_edition);
      list.append(el('li', `${chapterTitle(q)} · ${groupTitle(q)} ${q.label}\n${q.source_path} · ${q.group_path}\n${r.edition.toUpperCase()}: ${r.member}#${r.fragment}\n${q.native_id}`));
    }
    area.append(list); document.body.append(area);
    try { window.print(); } finally { area.remove(); }
  });
  render();
})();
