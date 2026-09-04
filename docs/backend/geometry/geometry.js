// No remote service, student record or durable storage. Selection is page-local.
const rows = [...document.querySelectorAll('.entry')];
const query = document.querySelector('#query');
const chapter = document.querySelector('#chapter');
const kind = document.querySelector('#kind');
function update() {
  const needle = (query?.value ?? '').trim().toLocaleLowerCase('id');
  let visible = 0;
  for (const row of rows) {
    const show = (!needle || row.textContent.toLocaleLowerCase('id').includes(needle))
      && (!chapter?.value || row.dataset.chapter === chapter.value)
      && (!kind?.value || row.dataset.kind === kind.value);
    row.hidden = !show;
    if (show) visible++;
  }
  const count = document.querySelector('#count');
  if (count) count.textContent = `${visible} dari ${rows.length} rekaman ditampilkan.`;
}
for (const control of [query, chapter, kind]) control?.addEventListener('input', update);
update();
function revealFragment() {
  let id;
  try { id = decodeURIComponent((globalThis.location?.hash ?? '').slice(1)); } catch { return; }
  const target = rows.find(row => row.id === id);
  if (!target) return;
  if (target.hidden) {
    for (const control of [query, chapter, kind]) if (control) control.value = '';
    update();
  }
  target.scrollIntoView?.({block:'start'});
}
globalThis.addEventListener?.('hashchange', revealFragment);
revealFragment();
const make = document.querySelector('#make-plan');
const clear = document.querySelector('#clear-plan');
make?.addEventListener('click', () => {
  const selected = rows.filter(row => row.querySelector('.choose')?.checked);
  const result = selected.map((row, i) => {
    const entry = JSON.parse(row.dataset.plan);
    return `${i + 1}. ${entry.judul}\n${JSON.stringify(entry, null, 2)}`;
  }).join('\n\n');
  document.querySelector('#plan').value = result;
  document.querySelector('#plan-status').textContent = `${selected.length} kegiatan dipilih; ${selected.filter(r => r.hidden).length} tersembunyi oleh filter. Rencana dapat disalin dari kotak di atas.`;
});
clear?.addEventListener('click', () => {
  for (const row of rows) { const checkbox = row.querySelector('.choose'); if (checkbox) checkbox.checked = false; }
  document.querySelector('#plan').value = '';
  document.querySelector('#plan-status').textContent = 'Pilihan telah dibersihkan.';
});
