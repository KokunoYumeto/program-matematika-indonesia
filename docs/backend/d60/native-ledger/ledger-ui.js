/* Local read-only metadata consumer: no network, telemetry, storage or invented answers. */
(() => {
  'use strict';
  const filter = (rows, kind, query = '', unit = '', flag = '', context = null) => {
    const q = query.trim().toLocaleLowerCase();
    return rows.filter(row => row.kind === kind && (!unit || row.native_scope_ids.includes(unit) || row.current_unit_ids.includes(unit) ||
      (context && (row.native_scope_ids.some(id => context.discovery_scope_ids.includes(id)) || row.current_unit_ids.some(id => context.discovery_scope_ids.includes(id)) ||
        (kind === 'rights' && context.rights_component_ids.includes(row.id))))) &&
      (!flag || row.flags.includes(flag)) && (!q || JSON.stringify(row).toLocaleLowerCase().includes(q)));
  };
  globalThis.D60_NATIVE_LEDGER_API = {filter};
  if (typeof document === 'undefined') return;
  const data = globalThis.D60_NATIVE_LEDGER;
  if (!data) return;
  const en = document.body.dataset.interface === 'en';
  const t = (id, english) => en ? english : id;
  const get = id => document.getElementById(id);
  const el = (tag, text, cls) => {const node = document.createElement(tag); if (text !== undefined) node.textContent = text; if (cls) node.className = cls; return node;};
  const parameters = new URLSearchParams(location.search);
  if (['terms','segments','corrections','rights'].includes(parameters.get('kind'))) get('kind').value = parameters.get('kind');
  get('unit').value = parameters.get('unit') || '';
  get('search').value = parameters.get('q') || '';
  if ([...get('flag').options].some(o => o.value === parameters.get('flag'))) get('flag').value = parameters.get('flag');
  let page = 0;
  const pageSize = 25;
  const flags = {
    canon_not_independently_checked: t('Kanon belum diperiksa secara independen', 'Canon not independently checked'),
    native_envelope_missing: t('Penanda skema asli tidak lengkap', 'Native schema envelope incomplete'),
    native_terminology_status_missing: t('Status istilah asli tidak ada', 'Native terminology status missing'),
    target_file_identity_differs: t('Hash seluruh berkas target berbeda; isi belum disimpulkan', 'Whole target-file hash differs; no content conclusion'),
    supersession_branch_preserved: t('Cabang riwayat dipertahankan tanpa memilih satu sisi', 'History branch retained without silently choosing a side')
  };
  function render() {
    const unit = get('unit').value.trim(), context = data.unit_contexts[unit] || null;
    const visible = filter(data.rows, get('kind').value, get('search').value, unit, get('flag').value, context);
    page = Math.min(page, Math.max(0, Math.ceil(visible.length / pageSize) - 1));
    get('records').replaceChildren();
    for (const row of visible.slice(page * pageSize, (page + 1) * pageSize)) {
      const article = el('article', undefined, 'record'); article.dataset.recordId = row.id;
      const native = row.native;
      article.append(el('h2', native.preferred || native.display_title || row.id), el('p', row.id, 'metadata'));
      if (unit && !row.native_scope_ids.includes(unit) && !row.current_unit_ids.includes(unit)) article.append(el('p',
        row.kind === 'rights' && context?.rights_component_ids.includes(row.id) ? t('Hak komponen yang dihubungkan oleh unit asli.', 'Component rights explicitly linked by the native unit.') :
        t('Catatan pada cakupan induk dalam jalur asli unit; ditampilkan untuk penelusuran, bukan klaim bahwa pilihan ini berlaku pada setiap kalimat.', 'Record on an ancestor in the unit’s native path; shown for discovery, not a claim that this choice applies to every sentence.'), 'notice'));
      if (native.source_term) article.append(el('p', t('Istilah sumber: ', 'Source term: ') + native.source_term));
      if (native.terminology_status) article.append(el('p', t('Status yang dicatat pembuat edisi: ', 'Status recorded by the native edition: ') + native.terminology_status));
      if (row.flags.length) {const list = el('ul', undefined, 'notice'); for (const flag of row.flags) list.append(el('li', flags[flag])); article.append(list);}
      if (row.target_identity) {
        const target = row.target_identity;
        article.append(el('p', t('Lokasi target: ', 'Target location: ') + target.path + ':' + target.line_start + '–' + target.line_end));
        const detail = el('details'); detail.append(el('summary', t('Identitas kriptografis target', 'Target cryptographic identity')), el('pre', JSON.stringify(target, null, 2))); article.append(detail);
      }
      if (row.routes.length) {
        const nav = el('ul');
        for (const route of row.routes) {const li = el('li'), link = el('a', t('Baca: ', 'Read: ') + route.title); link.href = route.url; link.lang = 'id'; li.append(link);
          if (route.state === 'course_fallback') li.append(el('small', t(' — pembaca lengkap; jangkar unik tidak ada', ' — full reader; no unique anchor')));
          const study = el('a', t(' · pilih unit untuk belajar', ' · select study unit'));
          study.href = '../D60' + (en ? '.en' : '') + '.html?unit=' + encodeURIComponent(route.id); li.append(study);
          const teach = el('a', t(' · pilih unit untuk mengajar', ' · select teaching unit'));
          teach.href = '../D60-pengajar' + (en ? '.en' : '') + '.html?unit=' + encodeURIComponent(route.id); li.append(teach); nav.append(li);
        }
        article.append(nav);
      } else article.append(el('p', t('Catatan ini tidak memiliki cakupan unit native yang tercatat; jangan menebaknya.', 'No native unit scope is recorded for this item; do not guess it.')));
      const original = el('details'); original.append(el('summary', t('Kutipan lengkap rekaman asli (tanpa perubahan)', 'Complete original record quotation (unchanged)')), el('pre', JSON.stringify(native, null, 2))); article.append(original);
      get('records').append(article);
    }
    get('count').textContent = visible.length ? `${page * pageSize + 1}–${Math.min((page + 1) * pageSize, visible.length)} / ${visible.length}` : t('Tidak ada catatan dalam cakupan ini. Ini bukan bukti bahwa istilah, koreksi atau solusi tidak ada.', 'No recorded item in this scope. This does not prove terms, corrections or solutions are absent.');
    get('previous').disabled = page === 0; get('next').disabled = (page + 1) * pageSize >= visible.length;
    const query = new URLSearchParams(); query.set('kind', get('kind').value);
    if (get('unit').value.trim()) query.set('unit', get('unit').value.trim());
    if (get('search').value) query.set('q', get('search').value);
    if (get('flag').value) query.set('flag', get('flag').value);
    get('language').href = (en ? 'ledger.html' : 'ledger-en.html') + '?' + query;
    for (const a of document.querySelectorAll('nav a')) {
      const url = new URL(a.href);
      if (url.origin === location.origin && /\/D60(?:-pengajar)?(?:\.en)?\.html$/.test(url.pathname)) {
        url.search = unit ? new URLSearchParams({unit}).toString() : ''; a.href = url.href;
      }
    }
  }
  for (const id of ['search','unit','kind','flag']) get(id).addEventListener(['search','unit'].includes(id) ? 'input' : 'change', () => {page = 0; render();});
  get('previous').addEventListener('click', () => {page--; render();});
  get('next').addEventListener('click', () => {page++; render();});
  render();
})();
