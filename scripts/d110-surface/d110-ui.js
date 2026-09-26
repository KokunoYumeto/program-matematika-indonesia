/* D110 selection runs locally: no fetch, persistent storage, telemetry or generated answers. */
(() => {
  'use strict';

  const locales = new Set(['id', 'en']);
  const supportKinds = new Set(['solution', 'solution_support']);
  const filterUnits = (map, query = '', kind = '', chapter = '') => {
    if (typeof query !== 'string') throw new TypeError('Search must be a string.');
    const q = query.trim().toLowerCase();
    return map.units.filter(unit =>
      (!kind || (kind === 'practice' ? unit.practice === true : unit.kind === kind)) &&
      (!chapter || unit.chapter_id === chapter) &&
      (!q || [unit.id, unit.title?.id, unit.title?.en, unit.chapter_id, unit.section_id,
        ...(unit.concept_ids || [])].filter(Boolean).join(' ').toLowerCase().includes(q)));
  };

  const makePlan = (map, selection, locale) => {
    if (!locales.has(locale)) throw new RangeError('Unsupported interface locale: ' + locale);
    if (!map || map.schema !== 'd110-study-map/1' || map.course_id !== 'D110' || !Array.isArray(map.units)) {
      throw new TypeError('Expected the D110 study map.');
    }
    if (selection == null || typeof selection[Symbol.iterator] !== 'function') {
      throw new TypeError('Selection must contain complete unit IDs.');
    }
    const chosen = new Set(typeof selection === 'string' ? [selection] : selection);
    const known = new Map();
    for (const unit of map.units) {
      if (typeof unit.id !== 'string' || known.has(unit.id)) throw new Error('Invalid or duplicate unit ID: ' + unit.id);
      known.set(unit.id, unit);
    }
    for (const id of chosen) {
      if (typeof id !== 'string' || !known.has(id)) throw new Error('Unknown unit: ' + String(id));
    }
    const units = map.units.filter(unit => chosen.has(unit.id));
    const dependencies = new Set(), visited = new Set(), pending = [...chosen];
    const addDependency = id => {
      if (!known.has(id)) throw new Error('Unknown support dependency: ' + String(id));
      if (!chosen.has(id)) dependencies.add(id);
      if (!visited.has(id)) pending.push(id);
    };
    // Incoming relations are attached to their target. Include the complete
    // recorded source closure, including declarations supporting a solution.
    while (pending.length) {
      const id = pending.pop();
      if (visited.has(id)) continue;
      visited.add(id);
      const unit = known.get(id);
      for (const supportId of unit.supporting || []) addDependency(supportId);
      for (const relation of unit.supports || []) {
        if (relation.target_id !== id) throw new Error('Support target identity mismatch: ' + relation.relation_id);
        addDependency(relation.id);
      }
    }
    return {
      schema: 'd110-study-plan/1',
      course_id: 'D110',
      interface_locale: locale,
      reader_locale: locale,
      input_identity: map.input_identity,
      units,
      supporting_units: map.units.filter(unit => dependencies.has(unit.id)),
      limitations: map.limitations?.[locale] || [],
      selected_order: 'native_map_order',
      dependency_scope: 'recursive_recorded_supports',
      offline_book_included: false,
      offline_lean_environment_included: false,
      reader_links_require_network: true,
      answers_generated: false
    };
  };
  globalThis.D110_PLAN_API = Object.freeze({filterUnits, makePlan});
  if (typeof document === 'undefined') return;
  const map = globalThis.D110_DATA;
  if (!map) return;

  const lang = document.body.dataset.language;
  if (!locales.has(lang)) throw new RangeError('Unsupported page language.');
  const en = lang === 'en';
  const t = (id, english) => en ? english : id;
  const get = id => document.getElementById(id);
  const el = (tag, text, className) => {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  };
  const title = unit => unit.title?.[lang] || unit.id;
  const solutionSourceIds = new Set(map.units.flatMap(unit => (unit.supports || []).map(relation => relation.id)));
  const selected = new Set();
  const pageSize = 30;
  let page = 0;
  let current = [];
  const kinds = {
    book: ['Buku', 'Book'], chapter: ['Bab', 'Chapter'], class: ['Kelas', 'Class'],
    def: ['Definisi', 'Definition'], example: ['Contoh', 'Example'], exercise: ['Latihan', 'Exercise'],
    frontmatter: ['Bagian awal', 'Front matter'], inductive: ['Tipe induktif', 'Inductive type'],
    instance: ['Instans', 'Instance'], lemma: ['Lema', 'Lemma'], program: ['Program', 'Program'],
    section: ['Bagian', 'Section'], solution: ['Solusi', 'Solution'],
    solution_support: ['Bahan pendukung solusi', 'Solution support'],
    structure: ['Struktur', 'Structure'], theorem: ['Teorema', 'Theorem']
  };
  const kindLabel = kind => kinds[kind]?.[en ? 1 : 0] || t('Jenis sumber: ', 'Source kind: ') + kind;
  const allowedHosts = new Set(['kokunoyumeto.github.io', 'github.com']);
  const safeURL = route => {
    const value = typeof route === 'string' ? route : route?.url;
    if (typeof value !== 'string' || /[\u0000-\u0020\u007f]/.test(value)) return null;
    try {
      const url = new URL(value);
      if (url.protocol !== 'https:' || !allowedHosts.has(url.hostname) || url.username || url.password || url.port) return null;
      if (typeof route === 'object' && route.anchor && !url.hash) url.hash = route.anchor;
      return url.href;
    } catch { return null; }
  };
  const appendLink = (parent, route, label, language) => {
    const href = safeURL(route);
    if (!href) {
      parent.append(el('span', t('Tautan tidak tersedia atau tidak lolos pemeriksaan alamat.', 'Link unavailable or address validation failed.'), 'metadata'));
      return;
    }
    const link = el('a', label);
    link.href = href;
    link.lang = language;
    link.rel = 'noopener noreferrer';
    parent.append(link);
  };
  const appendReader = (parent, unit) => {
    const p = el('p', undefined, 'reader-link');
    appendLink(p, unit.reader_routes?.[lang], t('Buka pembaca bahasa Indonesia (daring)', 'Open the English reader (online)'), lang);
    parent.append(p);
    parent.append(el('p', t(
      'Tautan pembaca memberi konteks bagian atau bab. Tautan ini bukan bukti kesepadanan setiap unit kode antaredisi.',
      'The reader link provides section or chapter context. It does not establish equivalence of individual code units across editions.'
    ), 'metadata'));
  };
  const appendProvenance = (parent, unit, includeSourceLink = true) => {
    const details = el('details', undefined, 'provenance');
    details.append(el('summary', t('Identitas, hak, dan lokasi sumber', 'Identity, rights, and source location')));
    details.append(el('p', unit.id, 'metadata'));
    details.append(el('p', t('Identitas hak: ', 'Rights IDs: ') + ((unit.rights_ids || []).join(' · ') || t('Tidak tercatat', 'Not recorded')), 'metadata'));
    details.append(el('p', t(
      'Nomor baris merujuk pada berkas sumber asli berbahasa Inggris; bukan baris terjemahan atau halaman pembaca.',
      'Line numbers refer to the original English authoring source, not translated lines or reader pages.'
    ), 'metadata'));
    details.append(el('pre', JSON.stringify(unit.source_locator, null, 2), 'source-location'));
    if (includeSourceLink && unit.source_reference) {
      const p = el('p');
      appendLink(p, unit.source_reference, t('Buka berkas sumber yang dirujuk (daring)', 'Open the referenced source file (online)'), unit.source_reference.language || 'en');
      details.append(p);
    }
    parent.append(details);
  };
  const appendCode = (parent, unit) => {
    const code = unit.code?.[lang];
    if (typeof code !== 'string') {
      parent.append(el('p', t('Tidak ada cuplikan kode dalam peta ini; gunakan lokasi sumber yang tercatat.', 'No code excerpt is included in this map; use the recorded source location.'), 'metadata'));
      return;
    }
    parent.append(el('p', t(
      'Blok Lean dari sumber yang tercatat. Satu blok pelajar dapat digunakan oleh beberapa ID latihan; bahan solusi dapat berupa fragmen untuk satu lubang bukti. Antarmuka ini tidak menerjemahkan, melengkapi, atau menjalankan kode.',
      'Lean block from the recorded source. A learner block may be shared by several exercise IDs; solution material may be a fragment for one proof hole. This interface does not translate, complete, or execute code.'
    ), 'metadata'));
    const pre = el('pre', undefined, 'lean-code');
    pre.tabIndex = 0;
    pre.setAttribute('aria-label', t('Blok kode Lean dari sumber', 'Lean source-code block'));
    pre.append(el('code', code));
    parent.append(pre);
    const digest = unit.code.sha256?.[lang];
    if (digest) parent.append(el('p', 'SHA-256: ' + digest, 'metadata'));
  };
  const supportingUnits = unit => {
    return makePlan(map, [unit.id], lang).supporting_units;
  };
  const appendSupport = (card, unit) => {
    const support = supportingUnits(unit);
    if (!support.length) {
      card.append(el('p', t(
        'Tidak ada relasi solusi yang tercatat untuk latihan ini. Hal ini tidak membuktikan bahwa sumber tidak memiliki solusi.',
        'No solution relation is recorded for this exercise. This does not establish that the source has no solution.'
      ), 'metadata'));
      return;
    }
    if (!selected.has(unit.id)) {
      card.append(el('p', t('Pilih unit ini untuk mengakses bahan solusi yang tercatat.', 'Select this unit to access the recorded solution materials.'), 'metadata'));
      return;
    }
    const details = el('details', undefined, 'solutions');
    details.append(el('summary', t('Buka bahan solusi yang tercatat', 'Open recorded solution materials') + ' (' + support.length + ')'));
    // Delay even DOM insertion until the learner deliberately opens the details.
    let loaded = false;
    details.addEventListener('toggle', () => {
      if (!details.open || loaded) return;
      loaded = true;
      const relations = [unit, ...support].flatMap(target => target.supports || []);
      for (const source of support) {
        const block = el('div', undefined, 'support-unit');
        block.append(el('h4', title(source)), el('p', source.id, 'metadata'));
        for (const relation of relations.filter(item => item.id === source.id)) {
          block.append(el('p', t('Relasi sumber: ', 'Source relation: ') + relation.relation_id + ' → ' + relation.target_id, 'metadata'));
          const data = relation.source_record?.data || {};
          const qualifiers = [];
          if (data.hole_rank !== undefined) qualifiers.push(t('Nomor lubang bukti: ', 'Proof-hole rank: ') + data.hole_rank);
          if (data.hole_ranks !== undefined) qualifiers.push(t('Nomor lubang bukti: ', 'Proof-hole ranks: ') + (Array.isArray(data.hole_ranks) ? data.hole_ranks.join(', ') : data.hole_ranks));
          if (data.solved_hole_count !== undefined) qualifiers.push(t('Jumlah lubang bukti yang diisi: ', 'Number of proof holes filled: ') + data.solved_hole_count);
          if (typeof data.is_alternative === 'boolean') qualifiers.push(t('Alternatif yang tercatat: ', 'Recorded alternative: ') + (data.is_alternative ? t('ya', 'yes') : t('tidak', 'no')));
          if (qualifiers.length) block.append(el('p', qualifiers.join(' · '), 'metadata'));
          block.append(el('p', t('Relasi ini dapat mencatat fragmen bukti atau deklarasi pendukung; bukan klaim bahwa seluruh latihan telah diselesaikan.', 'This relation may record a proof fragment or supporting declaration; it does not claim that the entire exercise has been solved.'), 'metadata'));
        }
        appendCode(block, source);
        appendReader(block, source);
        appendProvenance(block, source);
        details.append(block);
      }
    });
    card.append(details);
  };

  for (const kind of [...new Set(map.units.map(unit => unit.kind))].sort()) {
    const option = el('option', kindLabel(kind));
    option.value = kind;
    get('kind').append(option);
  }
  for (const chapter of map.chapters || []) {
    const option = el('option', title(chapter));
    option.value = chapter.id;
    get('chapter').append(option);
  }
  get('kind').value = document.body.dataset.mode === 'teacher' ? 'practice' : 'section';
  const updateSelection = () => {
    get('selection').textContent = selected.size + t(' unit dipilih. Ekspor menyertakan sumber pendukung yang tercatat beserta ketergantungannya.', ' units selected. Exports include recorded supporting sources and their dependencies.');
    get('export').disabled = get('export-text').disabled = get('clear').disabled = selected.size === 0;
  };
  function render() {
    current = filterUnits(map, get('search').value, get('kind').value, get('chapter').value);
    page = Math.min(Math.max(page, 0), Math.max(0, Math.ceil(current.length / pageSize) - 1));
    const shown = current.slice(page * pageSize, (page + 1) * pageSize);
    const list = get('unit-list');
    list.replaceChildren();
    for (const unit of shown) {
      const card = el('article', undefined, 'unit');
      const heading = el('h3', title(unit));
      const checkbox = el('input');
      checkbox.type = 'checkbox';
      checkbox.checked = selected.has(unit.id);
      checkbox.setAttribute('aria-label', t('Pilih ', 'Select ') + title(unit) + ' — ' + unit.id);
      const selectionLabel = el('label', undefined, 'unit-choice');
      selectionLabel.append(checkbox, el('span', t('Pilih unit', 'Select unit')));
      card.append(heading, selectionLabel);
      card.append(el('p', kindLabel(unit.kind) + ' · ' + unit.id + (unit.practice ? t(' · Latihan tercatat', ' · Recorded practice') : ''), 'metadata'));
      const content = el('div');
      const renderContent = () => {
        content.replaceChildren();
        if (supportKinds.has(unit.kind) || solutionSourceIds.has(unit.id)) {
          content.append(el('p', t(
            'Bahan solusi ditampilkan melalui latihan terkait setelah latihan dipilih dan panel solusi dibuka.',
            'Solution materials are displayed through their related exercise after it is selected and its solution panel is opened.'
          ), 'metadata'));
          const targets = map.units.filter(target => (target.supports || []).some(relation => relation.id === unit.id));
          for (const target of targets) content.append(el('p', t('ID unit terkait: ', 'Related unit ID: ') + target.id, 'metadata'));
          appendProvenance(content, unit, false);
        } else {
          appendReader(content, unit);
          if (unit.code) {
            const codeDetails = el('details');
            codeDetails.append(el('summary', t('Cuplikan kode sumber yang tercatat', 'Recorded source-code excerpt')));
            appendCode(codeDetails, unit);
            content.append(codeDetails);
          }
          if (unit.practice === true || (unit.supports || []).length) appendSupport(content, unit);
          appendProvenance(content, unit);
        }
      };
      checkbox.addEventListener('change', () => {
        if (checkbox.checked) selected.add(unit.id); else selected.delete(unit.id);
        updateSelection();
        renderContent();
      });
      renderContent();
      card.append(content);
      list.append(card);
    }
    get('results-status').textContent = current.length
      ? t('Hasil ', 'Results ') + (page * pageSize + 1) + '–' + Math.min((page + 1) * pageSize, current.length) + t(' dari ', ' of ') + current.length
      : t('Tidak ada hasil.', 'No results.');
    get('previous').disabled = page === 0;
    get('next').disabled = (page + 1) * pageSize >= current.length;
    get('select-page').disabled = !shown.length;
    updateSelection();
  }
  const download = (text, name, type) => {
    const url = URL.createObjectURL(new Blob([text], {type}));
    const link = el('a');
    link.href = url;
    link.download = name;
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };
  const planText = plan => {
    const lines = [t('Rencana belajar D110', 'D110 study plan'),
      t('Bahasa antarmuka dan pembaca: Indonesia', 'Interface and reader language: English'),
      t('Daftar pilihan, rekaman sumber, dan cuplikan yang tersedia; bukan buku atau lingkungan Lean luring.',
        'Selections, source records, and available excerpts; not an offline book or Lean environment.'),
      t('Tautan pembaca memerlukan koneksi internet. Tidak ada jawaban yang dihasilkan.',
        'Reader links require an internet connection. No answers are generated.'),
      '', t('Identitas masukan:', 'Input identity:'), JSON.stringify(plan.input_identity, null, 2), ''];
    const appendUnit = unit => {
      lines.push(title(unit), t('ID unit: ', 'Unit ID: ') + unit.id, kindLabel(unit.kind),
        t('Latihan tercatat: ', 'Recorded practice: ') + (unit.practice ? t('ya', 'yes') : t('tidak', 'no')));
      const route = unit.reader_routes?.[lang];
      lines.push(t('Pembaca daring: ', 'Online reader: ') + (safeURL(route) || t('Tautan tidak tersedia', 'Link unavailable')));
      lines.push(t('Konteks bagian atau bab; kesepadanan tiap unit kode antaredisi tidak dinyatakan.',
        'Section or chapter context; no claim of cross-edition equivalence for each code unit.'));
      lines.push(t('Lokasi sumber asli berbahasa Inggris:', 'Original English source location:'), JSON.stringify(unit.source_locator, null, 2));
      if (unit.source_reference) lines.push(t('Berkas sumber daring: ', 'Online source file: ') + (safeURL(unit.source_reference) || t('Tautan tidak tersedia', 'Link unavailable')));
      lines.push(t('Identitas hak: ', 'Rights IDs: ') + (unit.rights_ids || []).join(' · '));
      lines.push(t('Identitas konsep: ', 'Concept IDs: ') + (unit.concept_ids || []).join(' · '));
      if ((unit.supporting || []).length) lines.push(t('ID bahan pendukung: ', 'Supporting unit IDs: ') + unit.supporting.join(' · '));
      for (const relation of unit.supports || []) lines.push(t('Relasi sumber: ', 'Source relation: ') + JSON.stringify(relation));
      if (typeof unit.code?.[lang] === 'string') lines.push(t('Cuplikan Lean yang tercatat:', 'Recorded Lean excerpt:'), unit.code[lang], 'SHA-256: ' + (unit.code.sha256?.[lang] || ''));
      lines.push(t('Rekaman sumber yang dipertahankan:', 'Preserved source record:'), JSON.stringify(unit.source_record, null, 2), '');
    };
    lines.push(t('Unit yang dipilih', 'Selected units'));
    plan.units.forEach(appendUnit);
    lines.push(t('Sumber pendukung yang tercatat beserta ketergantungannya', 'Recorded supporting sources and their dependencies'));
    plan.supporting_units.forEach(appendUnit);
    lines.push(t('Batas penggunaan', 'Limitations'), ...plan.limitations);
    return lines.join('\n') + '\n';
  };
  for (const id of ['search', 'kind', 'chapter']) get(id).addEventListener(id === 'search' ? 'input' : 'change', () => { page = 0; render(); });
  get('previous').addEventListener('click', () => { page--; render(); });
  get('next').addEventListener('click', () => { page++; render(); });
  get('select-page').addEventListener('click', () => {
    for (const unit of current.slice(page * pageSize, (page + 1) * pageSize)) selected.add(unit.id);
    render();
  });
  get('clear').addEventListener('click', () => { selected.clear(); render(); });
  get('export').addEventListener('click', () => download(JSON.stringify(makePlan(map, selected, lang), null, 2) + '\n', 'D110-plan-' + lang + '.json', 'application/json;charset=utf-8'));
  get('export-text').addEventListener('click', () => download(planText(makePlan(map, selected, lang)), 'D110-plan-' + lang + '.txt', 'text/plain;charset=utf-8'));
  const workbench = get('workbench');
  if (workbench) workbench.hidden = false;
  render();
})();
