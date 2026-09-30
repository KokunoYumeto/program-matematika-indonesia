(() => {
  'use strict';
  const query = document.getElementById('query');
  const kind = document.getElementById('kind');
  const count = document.getElementById('count');
  const records = Array.from(document.querySelectorAll('.record'));
  function filter() {
    const words = query.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    let shown = 0;
    for (const record of records) {
      const match = (!kind.value || record.dataset.kind === kind.value) &&
        words.every(word => record.dataset.search.toLocaleLowerCase().includes(word));
      record.hidden = !match;
      shown += Number(match);
    }
    count.textContent = `${count.dataset.label}: ${shown} / ${records.length}`;
  }
  query.addEventListener('input', filter);
  kind.addEventListener('change', filter);
  filter();
})();
