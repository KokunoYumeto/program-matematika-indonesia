// No remote service, student record or durable storage. All state is page-local.
'use strict';

const rows = [...document.querySelectorAll('.entry')];
const query = document.querySelector('#query');
const count = document.querySelector('#count');

function firstControl(ids) {
  for (const id of ids) {
    const control = document.querySelector(`#${id}`);
    if (control) return control;
  }
  return null;
}

const filters = [
  {control: firstControl(['context']), keys: ['context']},
  {control: firstControl(['chapter']), keys: ['chapter'], chapter: true},
  {control: firstControl(['module', 'completion-module']), keys: ['module', 'completionModule']},
  {control: firstControl(['kind']), keys: ['kind']},
  {control: firstControl(['classification']), keys: ['classification']},
  {control: firstControl(['status']), keys: ['status']},
  {control: firstControl(['record-type']), keys: ['recordType', 'entity', 'type']},
].filter(filter => filter.control);

const filterControls = [query, ...filters.map(filter => filter.control)].filter(Boolean);

function folded(value) {
  const text = String(value ?? '').normalize('NFKC').trim();
  try { return text.toLocaleLowerCase('id-ID'); }
  catch { return text.toLowerCase(); }
}

function comparable(value, chapter = false) {
  const result = folded(value);
  return chapter && /^\d+$/.test(result) ? String(Number(result)) : result;
}

function datasetValue(row, keys) {
  for (const key of keys) {
    const value = row.dataset?.[key];
    if (typeof value === 'string') return value;
  }
  return '';
}

function filterMatches(row, filter) {
  const selected = comparable(filter.control.value, filter.chapter);
  if (!selected) return true;
  return datasetValue(row, filter.keys)
    .split('|')
    .some(value => comparable(value, filter.chapter) === selected);
}

function update() {
  const needle = folded(query?.value);
  let visible = 0;
  for (const row of rows) {
    const haystack = folded(`${row.textContent ?? ''} ${row.dataset?.search ?? ''}`);
    const show = (!needle || haystack.includes(needle))
      && filters.every(filter => filterMatches(row, filter));
    row.hidden = !show;
    if (show) visible += 1;
  }
  if (count) count.textContent = `${visible} dari ${rows.length} rekaman ditampilkan.`;
}

for (const control of filterControls) {
  control.addEventListener?.('input', update);
  control.addEventListener?.('change', update);
}

function clearFilters() {
  for (const control of filterControls) control.value = '';
  update();
}

document.querySelector('#clear-filters')?.addEventListener('click', clearFilters);
update();

function revealFragment() {
  let id;
  try { id = decodeURIComponent(String(globalThis.location?.hash ?? '').slice(1)); }
  catch { return; }
  if (!id) return;
  const target = rows.find(row => row.id === id);
  if (!target) return;
  if (target.hidden) clearFilters();
  target.scrollIntoView?.({block: 'start'});
}

globalThis.addEventListener?.('hashchange', revealFragment);
revealFragment();

const MAX_EMBEDDED_JSON_LENGTH = 1_000_000;

function canonical(value, depth = 0) {
  if (depth > 40) throw new TypeError('Rekaman terlalu dalam.');
  if (value === null || typeof value === 'string' || typeof value === 'boolean') return value;
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (Array.isArray(value)) {
    if (value.length > 10_000) throw new TypeError('Larik terlalu panjang.');
    return value.map(item => canonical(item, depth + 1));
  }
  if (typeof value === 'object') {
    const keys = Object.keys(value).sort();
    if (keys.length > 10_000) throw new TypeError('Objek terlalu besar.');
    const result = Object.create(null);
    for (const key of keys) result[key] = canonical(value[key], depth + 1);
    return result;
  }
  throw new TypeError('Jenis nilai tidak didukung.');
}

function embeddedRecord(row, keys) {
  for (const key of keys) {
    const raw = row.dataset?.[key];
    if (typeof raw !== 'string' || !raw.trim()) continue;
    if (raw.length > MAX_EMBEDDED_JSON_LENGTH) return {state: 'invalid'};
    try {
      const parsed = JSON.parse(raw);
      if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return {state: 'invalid'};
      return {state: 'valid', value: canonical(parsed)};
    } catch {
      return {state: 'invalid'};
    }
  }
  return {state: 'missing'};
}

function fallbackRecord(row) {
  const record = {id: String(row.id ?? ''), label: String(row.textContent ?? '').trim().replace(/\s+/g, ' ')};
  for (const filter of filters) {
    const value = datasetValue(row, filter.keys);
    if (value) record[filter.keys[0]] = value;
  }
  return canonical(record);
}

function stableJson(value) {
  return `${JSON.stringify(canonical(value), null, 2)}\n`;
}

function setValue(control, value) {
  if (control) control.value = value;
}

function setText(control, value) {
  if (control) control.textContent = value;
}

const exportOutput = firstControl(['export', 'export-data']);
const exportStatus = document.querySelector('#export-status');
const exportButtons = [
  document.querySelector('#export-visible'),
  document.querySelector('#make-export'),
].filter((button, index, all) => button && all.indexOf(button) === index);

function exportVisible() {
  const visibleRows = rows.filter(row => !row.hidden);
  const records = [];
  let invalid = 0;
  for (const row of visibleRows) {
    const record = embeddedRecord(row, ['export', 'plan']);
    if (record.state === 'valid') records.push(record.value);
    else if (record.state === 'missing') records.push(fallbackRecord(row));
    else invalid += 1;
  }
  setValue(exportOutput, stableJson(records));
  const ignored = invalid ? `; ${invalid} rekaman rusak diabaikan` : '';
  setText(exportStatus, `${records.length} rekaman terlihat diekspor sebagai JSON lokal${ignored}.`);
}

for (const button of exportButtons) button.addEventListener?.('click', exportVisible);

const makePlan = document.querySelector('#make-plan');
const clearPlan = document.querySelector('#clear-plan');
const planOutput = document.querySelector('#plan');
const planStatus = document.querySelector('#plan-status');

makePlan?.addEventListener('click', () => {
  const selected = rows.filter(row => row.querySelector?.('.choose')?.checked);
  const records = [];
  let invalid = 0;
  for (const row of selected) {
    const record = embeddedRecord(row, ['plan']);
    if (record.state === 'valid') records.push(record.value);
    else invalid += 1;
  }
  setValue(planOutput, stableJson(records));
  const hidden = selected.filter(row => row.hidden).length;
  const ignored = invalid ? `; ${invalid} pilihan tanpa rekaman rencana yang sah diabaikan` : '';
  setText(planStatus, `${records.length} kegiatan dipilih; ${hidden} tersembunyi oleh filter${ignored}. Rencana JSON dapat disalin dari kotak di atas.`);
});

clearPlan?.addEventListener('click', () => {
  for (const row of rows) {
    const checkbox = row.querySelector?.('.choose');
    if (checkbox) checkbox.checked = false;
  }
  setValue(planOutput, '');
  setText(planStatus, 'Pilihan telah dibersihkan.');
});
