import assert from 'node:assert/strict';

export const normalizeTitle = text => String(text).normalize('NFC').replace(/--/g, '–').replace(/\s+/g, ' ').trim().toLocaleLowerCase('id');
export const roles = {
  B70: { title: 'Persamaan diferensial', books: ['R007'], resource: 'R007' },
  C10: { title: 'Analisis Real I', books: ['R006-volume-1'], resource: 'R006' },
  C20: { title: 'Analisis Real II', books: ['R006-volume-1', 'R006-volume-2'], resource: 'R006' },
  C50: { title: 'Analisis Kompleks', books: ['R008'], resource: 'R008' },
};

export function projectionPolicy(input) {
  const unitFields = ['id', 'semantic_key', 'source_local_id', 'resource_id', 'edition_id', 'rights_id', 'parent_id', 'order_key', 'concept_ids'];
  const termFields = ['id', 'concept_id', 'preferred', 'variants', 'rejected_forms', 'scope_ids', 'evidence', 'ledger_binding', 'rights_id'];
  const notCopiedWhole = (rows, copied) => [...new Set(rows.flatMap(row => Object.keys(row)))].filter(key => !copied.includes(key)).sort();
  return {
    scope: 'Capability projection from frozen intake metadata; distinct from the intake projection of the native record stream.',
    whole_records_preserved: ['resources', 'editions', 'rights', 'relations'],
    units: {
      copied_fields: unitFields,
      not_copied_whole: notCopiedWhole(input.units, unitFields),
      partial_and_derived: {
        kind: 'unit_kind', title: 'manifest_binding.title_target or label', resource_key: 'manifest_binding.resource_key',
        source_components: 'manifest_binding.source_components, unchanged', target_components: 'manifest_binding.target_components, unchanged',
        support_state: 'exercise_metadata.solution_status only; no completeness inferred from support links',
        support: 'Union of explicit hints/answers/solves relations and typed parent_id children, retaining each evidence basis',
        navigation: 'Book membership and title-matched heading destinations; not verified exercise page coordinates',
        section_and_terms: 'Native ancestry and concept identity joins; no adjacency or spelling-only join',
      },
    },
    terms: {copied_fields: termFields, not_copied_whole: notCopiedWhole(input.terms, termFields),
      derived_fields: {source_term: 'ledger_binding.source_term or empty string', resource_scope: 'ledger_binding.resource_scope or empty string'}},
    recovery: 'Omitted capability fields remain in frozen intake where retained; complete native records remain in the pinned external stream. No full native roundtrip is claimed.',
  };
}

// A loss-accounted projection, not a replacement schema for the native books.
export function buildModel(input) {
  const { units, terms, relations, resources, editions, rights } = input;
  const books = input['reader-destinations'];
  const entrypoints = input['volume-entrypoints'];
  const summary = input['native-summary'];
  assert.equal(summary.native_unit_count, units.length);
  assert.equal(new Set(units.map(x => x.id)).size, units.length, 'Duplicate unit identity');
  for (const [name, list] of Object.entries({ terms, relations, resources, editions, rights })) {
    assert.equal(new Set(list.map(x => x.id)).size, list.length, `Duplicate ${name} identity`);
  }
  assert.equal(books.length, 4);
  assert.equal(new Set(books.map(x => x.book_id)).size, 4);
  const bookMap = new Map(books.map(x => [x.book_id, x]));
  for (const book of books) for (const destination of book.outline) {
    assert.ok(Number.isInteger(destination.page) && destination.page >= 1 && destination.page <= book.pages, 'Invalid PDF destination');
    assert.equal(destination.href, `${book.url}#page=${destination.page}`);
  }
  const byId = new Map(units.map(x => [x.id, x]));
  const rightsIds = new Set(rights.map(x => x.id));
  const resourceIds = new Set(resources.map(x => x.id));
  const editionIds = new Set(editions.map(x => x.id));
  function ancestors(unit) {
    const result = [], seen = new Set([unit.id]);
    while (unit.parent_id) {
      assert.ok(!seen.has(unit.parent_id), 'Cyclic unit ancestry');
      seen.add(unit.parent_id);
      unit = byId.get(unit.parent_id);
      assert.ok(unit, 'Unresolved unit parent');
      result.push(unit);
    }
    return result;
  }
  const volumeFiles = {
    'R006-volume-1': new Set([...entrypoints['realanal.tex'].inputs, 'realanal.tex']),
    'R006-volume-2': new Set([...entrypoints['realanal2.tex'].inputs, 'realanal2.tex']),
  };
  const classifications = new Map();
  const raRelative = path => path.replace(/^(?:translation\/ra\/|source\/ra(?:-v6\.3)?\/)/, '');
  const resourceKeys = {R006:'urn:uuid:884aba97-efd2-550c-a975-a98df314c5d8',R007:'urn:uuid:372b97ed-b680-56ea-830b-7b6748d2b465',R008:'urn:uuid:907ee9c9-fa99-55d1-bcff-29cdb73cd396'};
  function classify(unit) {
    if (classifications.has(unit.id)) return classifications.get(unit.id);
    const key = unit.manifest_binding.resource_key;
    assert.equal(unit.resource_id, resourceKeys[key], 'Resource key/UUID mismatch');
    let result;
    if (key === 'R007' || key === 'R008') result = { books: [key], basis: 'native_resource' };
    else {
      assert.equal(key, 'R006', 'Unexpected family resource');
      const paths = unit.manifest_binding.target_components.map(c => raRelative(c.path));
      const found = Object.entries(volumeFiles).filter(([, files]) => paths.some(p => files.has(p))).map(([id]) => id);
      const sourceFound = Object.entries(volumeFiles).filter(([, files]) => unit.manifest_binding.source_components.some(c => files.has(raRelative(c.path)))).map(([id]) => id);
      assert.deepEqual(sourceFound, found, 'Source and target book membership disagree');
      if (found.length) result = { books: found, basis: 'verified_volume_entrypoint_component' };
      else {
        const parent = ancestors(unit).find(p => p.manifest_binding.target_components.some(c => Object.values(volumeFiles).some(files => files.has(raRelative(c.path)))));
        result = parent ? { ...classify(parent), basis: 'native_parent_volume_component' }
          : { books: [], basis: 'shared_or_unresolved_family_component' };
      }
    }
    classifications.set(unit.id, result);
    return result;
  }
  const supportRelations = relations.filter(r => ['hints', 'answers', 'solves'].includes(r.predicate));
  for (const relation of supportRelations) {
    assert.ok(byId.has(relation.subject_id) && byId.has(relation.object_id), 'Unresolved support relation');
    assert.equal(byId.get(relation.object_id).unit_kind, 'exercise', 'Support relation targets non-exercise');
    assert.equal(byId.get(relation.subject_id).unit_kind, { hints: 'hint', answers: 'answer', solves: 'solution' }[relation.predicate]);
  }
  const mapped = units.map(unit => {
    assert.ok(rightsIds.has(unit.rights_id), 'Unresolved unit rights');
    assert.ok(resourceIds.has(unit.resource_id), 'Unresolved resource');
    assert.ok(editionIds.has(unit.edition_id), 'Unresolved edition');
    const lineage = ancestors(unit);
    const classification = classify(unit);
    const title = unit.manifest_binding.title_target || unit.label;
    const section = [unit, ...lineage].find(x => ['section', 'chapter'].includes(x.unit_kind));
    const destinations = classification.books.map(id => {
      const book = bookMap.get(id);
      for (const candidate of [unit, ...lineage]) {
        if (!['chapter', 'section', 'subsection'].includes(candidate.unit_kind)) continue;
        const matches = book.outline.filter(d => normalizeTitle(d.title) === normalizeTitle(candidate.manifest_binding.title_target || candidate.label));
        // Repeated titles are not sufficient for an exact destination join.
        if (matches.length === 1) return { book_id: id, ...matches[0], scope: 'title_matched_heading_navigation_not_verified_unit_page', heading_unit_id: candidate.id };
      }
      return { book_id: id, href: book.url, page: null, scope: 'whole_book_no_heading_match', heading_unit_id: null };
    });
    const support = [];
    for (const relation of supportRelations.filter(r => r.object_id === unit.id)) {
      let edge = support.find(s => s.id === relation.subject_id);
      if (!edge) { edge = {id: relation.subject_id, kind: byId.get(relation.subject_id).unit_kind, evidence: []}; support.push(edge); }
      edge.evidence.push({basis: 'explicit_native_relation', relation_id: relation.id});
    }
    if (unit.unit_kind === 'exercise') for (const child of units.filter(c => c.parent_id === unit.id && ['hint','answer','solution'].includes(c.unit_kind))) {
      const edge = support.find(s => s.id === child.id);
      if (edge) edge.evidence.push({ basis: 'native_parent_id' });
      else support.push({ id: child.id, kind: child.unit_kind, evidence: [{ basis: 'native_parent_id' }] });
    }
    if (unit.unit_kind === 'exercise') assert.ok(['full_solution', 'answer_only', 'hint_only', 'mixed_partial', 'none', 'unknown', 'not_applicable'].includes(unit.exercise_metadata?.solution_status), 'Invalid support state');
    return { id: unit.id, semantic_key: unit.semantic_key, source_local_id: unit.source_local_id,
      resource_id: unit.resource_id, resource_key: unit.manifest_binding.resource_key, edition_id: unit.edition_id,
      rights_id: unit.rights_id, parent_id: unit.parent_id, kind: unit.unit_kind, title,
      order_key: unit.order_key, section_id: section?.id ?? null, section_title: section ? section.manifest_binding.title_target || section.label : title,
      books: classification.books, book_assignment_basis: classification.basis,
      target_components: unit.manifest_binding.target_components, source_components: unit.manifest_binding.source_components,
      support_state: unit.exercise_metadata?.solution_status ?? null, support, destinations,
      concept_ids: unit.concept_ids, term_ids: terms.filter(t => unit.concept_ids.includes(t.concept_id)).map(t => t.id),
      inventory_layer: unit.source_local_id.includes('.logical.') ? 'logical_tex_unit' : 'native_editorial_or_semantic_unit' };
  });
  const mappedTerms = terms.map(term => {
    assert.ok(rightsIds.has(term.rights_id), 'Unresolved term rights');
    assert.equal(term.locale, 'id-ID');
    return { id: term.id, concept_id: term.concept_id, source_term: term.ledger_binding?.source_term ?? '',
      preferred: term.preferred, variants: term.variants, rejected_forms: term.rejected_forms,
      scope_ids: term.scope_ids, resource_scope: term.ledger_binding?.resource_scope ?? '',
      evidence: term.evidence, ledger_binding: term.ledger_binding ?? null, rights_id: term.rights_id };
  });
  return { contract: 'lebl-learning-capability/1', locale: 'id-ID', native_commit: summary.native_commit,
    native_dataset_id: summary.dataset_id, native_records: summary.native_record_count,
    books, roles, units: mapped, terms: mappedTerms, resources, editions, rights,
    relations, projection_policy: projectionPolicy(input), counts: { units: mapped.length, exercises: mapped.filter(x => x.kind === 'exercise').length,
      terms: terms.length, reader_pages: books.reduce((n, b) => n + b.pages, 0),
      outline_destinations: books.reduce((n, b) => n + b.outline.length, 0),
      units_with_shared_or_unresolved_book_assignment: mapped.filter(x => x.book_assignment_basis === 'shared_or_unresolved_family_component').length,
      explicit_support_relations: supportRelations.length },
    limitations: [
      'Native semantic/editorial units may overlap logical TeX units; record totals are not distinct tasks or pages.',
      'PDF heading destinations are not exact exercise page claims. Unmatched records link to the book.',
      'Unknown support stays unknown. Typed children and explicit support edges are exposed with their evidence, not certified as complete solutions; adjacency is never a join.',
      'C20 uses sequence-of-functions and metric-space material from Volume I as well as Volume II; book identity is not course identity.',
      'Metadata projection only: no full native-stream roundtrip, source-span replay, book build, PDF accessibility, or visual-layout certification.',
      'Saved navigation works offline; linked PDFs must be downloaded separately. No learner data is sent or stored.',
    ] };
}
