/* Local-only selection: no fetch, telemetry, storage or generated answers. */
(() => {
  'use strict';
  const filterUnits = (map, query = '', kind = '', group = '') => {
    const q = query.trim().toLocaleLowerCase();
    return map.units.filter(u => (!kind || (kind === 'practice' ? u.practice : u.kind === kind)) &&
      (!group || u.group === group) && (!q || [u.title, u.id, ...u.concept_ids].join(' ').toLocaleLowerCase().includes(q)));
  };
  const makePlan = (map, selection, locale) => {
    const chosen = new Set(selection), known = new Map(map.units.map(u => [u.id, u]));
    for (const id of chosen) if (!known.has(id)) throw new Error('Unknown unit: ' + id);
    const units = map.units.filter(u => chosen.has(u.id));
    const supportIds = new Set(units.flatMap(u => Object.values(u.support).flat().map(r => r.unit_id)));
    return {schema: 'd60-study-plan/1', course_id: 'D60', interface_locale: locale, content_locale: map.locale,
      source_witness: map.source_witness, reader: map.reader, inputs: map.inputs,
      units, supporting_units: map.units.filter(u => supportIds.has(u.id)),
      limitations: map.limitations, selected_order: 'native_group_and_native_order',
      offline_book_included: false, answers_generated: false};
  };
  globalThis.D60_PLAN_API = {filterUnits, makePlan};
  if (typeof document === 'undefined') return;
  const map = globalThis.D60_DATA;
  if (!map) return;
  const en = document.body.dataset.interface === 'en', lang = en ? 'en' : 'id';
  const t = (id, english) => en ? english : id;
  const get = id => document.getElementById(id);
  const el = (tag, text, cls) => {const n = document.createElement(tag); if (text !== undefined) n.textContent = text; if (cls) n.className = cls; return n;};
  const byId = new Map(map.units.map(u => [u.id, u]));
  const selected = new Set(), pageSize = 40;
  let page = 0, current = [];
  const labels = {lecture: ['Kuliah', 'Lecture'], reader_unit: ['Bacaan', 'Reading'], exercise: ['Latihan', 'Exercise'],
    question: ['Pertanyaan', 'Question'], proof_check: ['Pemeriksaan bukti', 'Proof check'], solution: ['Solusi', 'Solution'],
    hint: ['Petunjuk', 'Hint'], answer: ['Jawaban', 'Answer'], section: ['Bagian', 'Section'], definition: ['Definisi', 'Definition'],
    theorem: ['Teorema', 'Theorem'], lemma: ['Lema', 'Lemma'], proof: ['Bukti', 'Proof'], capstone: ['Capstone', 'Capstone']};
  const labelKind = kind => labels[kind]?.[en ? 1 : 0] ?? kind.replaceAll('_', ' ');
  for (const kind of Object.keys(map.counts.kinds).sort()) {const o = el('option', labelKind(kind)); o.value = kind; get('kind').append(o);}
  for (const group of [...new Set(map.units.map(u => u.group))].sort()) {
    const o = el('option', byId.get(group)?.title ?? group); o.value = group; get('group').append(o);
  }
  get('kind').value = document.body.dataset.mode === 'teacher' ? 'practice' : 'lecture';
  const updateSelection = () => {
    get('selection').textContent = selected.size + t(' unit dipilih', ' units selected');
    get('export').disabled = get('export-text').disabled = selected.size === 0;
  };
  const link = u => {const a = el('a', u.title); a.href = u.route.url; a.lang = 'id'; return a;};
  function render() {
    current = filterUnits(map, get('search').value, get('kind').value, get('group').value);
    page = Math.min(page, Math.max(0, Math.ceil(current.length / pageSize) - 1));
    const shown = current.slice(page * pageSize, (page + 1) * pageSize), list = get('unit-list');
    list.replaceChildren();
    for (const u of shown) {
      const card = el('article', undefined, 'unit');
      const checkbox = el('input'); checkbox.type = 'checkbox'; checkbox.checked = selected.has(u.id);
      checkbox.setAttribute('aria-label', t('Pilih ', 'Select ') + u.title);
      checkbox.addEventListener('change', () => {if (checkbox.checked) selected.add(u.id); else selected.delete(u.id); updateSelection();});
      const heading = el('h3'); heading.append(checkbox, link(u)); card.append(heading);
      card.append(el('p', labelKind(u.kind) + ' · ' + u.id, 'metadata'));
      if (u.route.state === 'course_fallback') card.append(el('p', t('Tautan menuju pembaca lengkap: tidak ada jangkar unit unik.', 'Link opens the full reader: no unique unit anchor.'), 'notice'));
      const hasSupport = Object.values(u.support).some(rows => rows.length);
      if (hasSupport) {
        const details = el('details'); details.append(el('summary', t('Petunjuk, jawaban dan solusi yang tercatat', 'Recorded hints, answers and solutions')));
        for (const [type, rows] of Object.entries(u.support)) {
          if (!rows.length) continue;
          const title = {hints: t('Petunjuk', 'Hints'), answers: t('Jawaban', 'Answers'), solves: t('Solusi', 'Solutions')}[type];
          details.append(el('h4', title)); const ul = el('ul');
          for (const r of rows) {const li = el('li'), target = byId.get(r.unit_id); li.append(link(target));
            if (target.route.state === 'course_fallback') li.append(el('small', t(' — pembaca lengkap', ' — full reader'))); ul.append(li);}
          details.append(ul);
        }
        card.append(details);
      } else if (u.practice) card.append(el('p', t('Belum ada relasi bahan pendukung tercatat untuk ID ini. Cakupan solusi tidak diketahui.', 'No support relation is recorded for this ID. Solution coverage is unknown.'), 'metadata'));
      const provenance = el('details'); provenance.append(el('summary', t('Identitas, hak dan sumber', 'Identity, rights and source')));
      provenance.append(el('p', u.projected_id, 'metadata'), el('p', u.rights_ids.join(' · '), 'metadata'));
      provenance.append(el('p', u.source_locator.path + ':' + u.source_locator.line_start + '–' + u.source_locator.line_end, 'metadata'));
      provenance.append(el('p', 'SHA-256: ' + u.source_locator.file_sha256, 'metadata')); card.append(provenance);
      list.append(card);
    }
    get('results-status').textContent = current.length ? `${page * pageSize + 1}–${Math.min((page + 1) * pageSize, current.length)} / ${current.length}` : t('Tidak ada hasil.', 'No results.');
    get('previous').disabled = page === 0; get('next').disabled = (page + 1) * pageSize >= current.length;
    get('select-page').disabled = !shown.length; updateSelection();
  }
  const download = (text, name, type) => {
    const url = URL.createObjectURL(new Blob([text], {type})), a = el('a'); a.href = url; a.download = name;
    document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  };
  for (const id of ['search', 'kind', 'group']) get(id).addEventListener(id === 'search' ? 'input' : 'change', () => {page = 0; render();});
  get('previous').addEventListener('click', () => {page--; render();});
  get('next').addEventListener('click', () => {page++; render();});
  get('select-page').addEventListener('click', () => {current.slice(page * pageSize, (page + 1) * pageSize).forEach(u => selected.add(u.id)); render();});
  get('clear').addEventListener('click', () => {selected.clear(); render();});
  get('export').addEventListener('click', () => download(JSON.stringify(makePlan(map, selected, lang), null, 2) + '\n', 'D60-plan.json', 'application/json'));
  get('export-text').addEventListener('click', () => {
    const plan = makePlan(map, selected, lang);
    const lines = [t('Rencana belajar D60', 'D60 study plan'), t('Bahasa bacaan: Indonesia', 'Reading language: Indonesian'),
      'Reader SHA-256: ' + map.reader.sha256, 'Witness SHA-256: ' + map.source_witness.sha256, ''];
    for (const u of plan.units) {
      lines.push(u.title, u.id, u.route.url, u.route.state, 'Source SHA-256: ' + u.source_locator.file_sha256);
      for (const [type, rows] of Object.entries(u.support)) for (const r of rows) lines.push(type + ': ' + r.unit_id + ' ' + byId.get(r.unit_id).route.url);
      lines.push('');
    }
    lines.push(...plan.limitations); download(lines.join('\n') + '\n', 'D60-plan.txt', 'text/plain;charset=utf-8');
  });
  get('workbench').hidden = false; render();
})();
