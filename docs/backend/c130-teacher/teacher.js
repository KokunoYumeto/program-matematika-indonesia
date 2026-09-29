(function (root) {
  'use strict';
  function validateModel(model) {
    if (model.schema !== 'c130-teacher-planner/1' || model.course_id !== 'C130' ||
        !/^[a-f0-9]{64}$/.test(model.mapping_sha256) || model.questions.length !== 227) throw new Error('Invalid model');
    const ids = new Set();
    for (const q of model.questions) {
      if (ids.has(q.id) || !Number.isInteger(q.page) || q.page < 1 || q.page > 666 ||
          !Number.isInteger(q.chapter) || q.chapter < 1 || q.chapter > 15 ||
          !['numbered-exercise','graph-practice','learningcheckpoint','tryit'].includes(q.kind) ||
          !/^[a-f0-9]{64}$/.test(q.source.sha256) ||
          q.manual.some(m => !Number.isInteger(m.page) || m.page < 1 || m.page > 666)) throw new Error('Invalid question');
      ids.add(q.id);
    }
    return model;
  }
  function select(model, filter) {
    const needle = (filter.search || '').toLocaleLowerCase();
    return model.questions.filter(q => (!filter.chapter || String(q.chapter) === filter.chapter) &&
      (!filter.kind || q.kind === filter.kind) &&
      (!filter.support || (filter.support === 'manual' ? q.manual.length > 0 : filter.support === 'labs' ? q.labs.length > 0 : q.manual.length === 0)) &&
      (!needle || [q.id, q.number, q.display_number, q.title].join(' ').toLocaleLowerCase().includes(needle)) &&
      (!filter.selected || filter.ids.has(q.id)));
  }
  function exportSelection(model, selected) {
    const known = new Set(model.questions.map(q => q.id));
    if ([...selected].some(id => !known.has(id))) throw new Error('Unknown selection');
    return {schema: 'c130-assignment/1', course_id: 'C130', mapping_sha256: model.mapping_sha256,
      reader_sha256: model.reader.sha256, questions: model.questions.filter(q => selected.has(q.id))};
  }
  function importSelection(model, value) {
    if (!value || Object.keys(value).sort().join('|') !== ['schema','course_id','mapping_sha256','reader_sha256','questions'].sort().join('|') ||
        value.schema !== 'c130-assignment/1' || value.course_id !== 'C130' || value.mapping_sha256 !== model.mapping_sha256 ||
        value.reader_sha256 !== model.reader.sha256 || !Array.isArray(value.questions) || value.questions.length > model.questions.length) throw new Error('Edition mismatch');
    const ids = new Set();
    const expected = new Map(model.questions.map(q => [q.id, q]));
    for (const q of value.questions) {
      if (!q || ids.has(q.id) || !expected.has(q.id) || JSON.stringify(q) !== JSON.stringify(expected.get(q.id))) throw new Error('Changed or duplicate reference');
      ids.add(q.id);
    }
    if (JSON.stringify(exportSelection(model, ids)) !== JSON.stringify(value)) throw new Error('Noncanonical assignment');
    return ids;
  }
  const api = {validateModel, select, exportSelection, importSelection};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (typeof document === 'undefined') return;
  root.C130Planner = api;
  const payload = JSON.parse(document.getElementById('planner-data').textContent);
  const model = validateModel(payload.model), w = payload.words;
  const selected = new Set();
  const byId = id => document.getElementById(id);
  function element(tag, text) { const el = document.createElement(tag); if (text != null) el.textContent = text; return el; }
  function readerLink(page, text) {
    const a = element('a', text);
    a.href = (byId('local').checked ? 'reader.pdf' : model.reader.url) + '#page=' + page;
    return a;
  }
  function filtered() { return select(model, {chapter: byId('chapter').value, support: byId('support').value,
    kind: byId('kind').value, search: byId('search').value, selected: byId('selected-only').checked, ids: selected}); }
  function updateCount(rows) {
    byId('count').textContent = rows.length + ' / ' + model.questions.length + ' · ' + w.chosen + ': ' + selected.size;
  }
  function render() {
    const rows = filtered();
    const body = byId('questions'); body.replaceChildren();
    for (const q of rows) {
      const tr = element('tr'), choose = element('td'), input = element('input');
      input.type = 'checkbox'; input.checked = selected.has(q.id);
      input.setAttribute('aria-label', w.choose + ' ' + q.display_number + ': ' + q.title);
      input.addEventListener('change', () => {
        input.checked ? selected.add(q.id) : selected.delete(q.id);
        if (byId('selected-only').checked) { render(); byId('choose-visible').focus(); }
        else updateCount(rows); // Keep keyboard focus and expanded evidence in place.
      });
      choose.append(input); tr.append(choose);
      const title = element('td'); title.append(readerLink(q.page, q.display_number + ' · ' + q.title));
      title.append(element('small', w.page + ' ' + q.page + ' · ' + w.chapter + ' ' + q.chapter + ' · ' + w[q.kind]));
      const details = element('details'), summary = element('summary', w.identity);
      details.append(summary, element('code', q.id), element('p', q.source.path + ' · ' + w.lines + ' ' + q.source.lines.join('–')),
        element('code', q.source.sha256)); title.append(details); tr.append(title);
      const support = element('td');
      if (q.manual.length) {
        if (byId('solutions').checked) {
          for (const m of q.manual) support.append(readerLink(m.page, m.kind === 'guide-and-rubric' ? w.rubric : m.kind === 'checkpoint-answer' ? w['checkpoint-answer'] : w.manual), element('br'));
        } else support.append(element('span', w.manualAvailable));
      } else support.append(element('span', w.noManual));
      if (q.labs.length) {
        const detail = element('details'), summary = element('summary', w.lab + ' (' + q.labs.length + ')'); detail.append(summary);
        const a = element('a', w.downloadLabs); a.href = model.labs.url; detail.append(a);
        for (const lab of q.labs) detail.append(element('p', lab.id), element('small', (lab.paths || []).join('\n')));
        detail.append(element('p', w.labLimit)); support.append(detail);
      }
      tr.append(support); body.append(tr);
    }
    updateCount(rows);
    for (const link of document.querySelectorAll('.reader-reference'))
      link.href = (byId('local').checked ? 'reader.pdf' : model.reader.url) + '#page=' + link.dataset.page;
  }
  for (const id of ['chapter','kind','support','search','selected-only','local','solutions']) byId(id).addEventListener('input',render);
  byId('choose-visible').addEventListener('click',() => { filtered().forEach(q => selected.add(q.id)); render(); });
  byId('clear').addEventListener('click',() => { selected.clear(); render(); });
  byId('export').addEventListener('click',() => {
    const text = JSON.stringify(exportSelection(model,selected),null,2)+'\n';
    byId('exchange-text').value=text;byId('exchange').open=true;
    const blob = new Blob([text],{type:'application/json'});
    const url = URL.createObjectURL(blob), a = element('a'); a.href=url;a.download='C130-assignment.json';
    document.body.append(a);a.click();a.remove();
    setTimeout(() => URL.revokeObjectURL(url),1000);
  });
  function applyImport(text) {
    if(text.length>2000000)throw new Error('Oversized');
    const ids=importSelection(model,JSON.parse(text));
    selected.clear();ids.forEach(id=>selected.add(id));byId('message').textContent=w.imported;render();
  }
  byId('load-json').addEventListener('click',()=>{
    try { applyImport(byId('exchange-text').value); }
    catch (_) { byId('message').textContent=w.invalid; }
  });
  byId('import').addEventListener('change', async event => {
    const file=event.target.files[0];if(!file)return;
    try { if(file.size>2000000)throw new Error('Oversized');applyImport(await file.text());
    } catch (_) { byId('message').textContent=w.invalid; }
    event.target.value='';
  });
  byId('print').addEventListener('click',()=>window.print());
  byId('interactive').hidden=false;
  render();
})(typeof globalThis !== 'undefined' ? globalThis : this);
