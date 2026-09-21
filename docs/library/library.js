/* Progressive enhancement: edition links and the complete catalogue work without JavaScript. */
(() => {
  'use strict';
  const form = document.querySelector('#library-filters');
  if (!form) return;
  const fields = ['search', 'collection', 'language', 'status'].map(id => document.getElementById(id));
  const [search, collection, language, status] = fields;
  const cards = [...document.querySelectorAll('.library-card')];
  const sections = [...document.querySelectorAll('.catalogue-section')];
  const count = document.querySelector('#results-count');
  const clear = document.querySelector('#reset-filters');
  const empty = document.querySelector('#empty-state');
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase();
  const searchable = new Map(cards.map(card => [card, normalize(card.textContent)]));

  function setEdition(card, editionId) {
    const select = card.querySelector('.edition-select');
    if (select) select.value = editionId;
    card.querySelectorAll('.edition-link').forEach(link => { link.hidden = link.dataset.edition !== editionId; });
  }

  function filter() {
    const words = normalize(search.value.trim()).split(/\s+/).filter(Boolean);
    let shown = 0;
    cards.forEach(card => {
      const matches = words.every(word => searchable.get(card).includes(word)) &&
        (collection.value === 'all' || card.dataset.collection === collection.value) &&
        (language.value === 'all' || card.dataset.languages.split(' ').includes(language.value)) &&
        (status.value === 'all' || card.dataset.status === status.value);
      card.hidden = !matches;
      if (matches) {
        shown++;
        const matchingEdition = card.querySelector(`.edition-link[data-language="${language.value}"]`);
        if (matchingEdition) setEdition(card, matchingEdition.dataset.edition);
      }
    });
    sections.forEach(section => {
      const visible = [...section.querySelectorAll('.library-card')].filter(card => !card.hidden).length;
      section.hidden = !visible;
      section.querySelector('.section-count').textContent = `${visible} ${visible === 1 ? 'entry' : 'entries'}`;
    });
    count.textContent = `${shown} of ${cards.length} catalogue entries shown · publication status is listed for each work`;
    empty.hidden = shown !== 0;
    clear.disabled = !search.value && collection.value === 'all' && language.value === 'all' && status.value === 'all';
  }

  function reset() {
    form.reset();
    filter();
    search.focus();
  }

  form.addEventListener('submit', event => event.preventDefault());
  fields.forEach(field => field.addEventListener(field === search ? 'input' : 'change', filter));
  clear.addEventListener('click', reset);
  document.querySelector('#empty-reset').addEventListener('click', reset);
  document.querySelectorAll('.edition-select').forEach(select => {
    const card = select.closest('.library-card');
    setEdition(card, select.value);
    select.addEventListener('change', () => setEdition(card, select.value));
  });
  document.documentElement.classList.add('js');
  form.hidden = false;
  document.querySelector('.results-bar').hidden = false;
  filter();

  // Collection links should always reveal their destination after a filter was applied.
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', () => {
      const destination = document.getElementById(link.getAttribute('href').slice(1));
      if (destination && (destination.hidden || destination.closest('[hidden]'))) {
        form.reset();
        filter();
      }
    });
  });
})();
