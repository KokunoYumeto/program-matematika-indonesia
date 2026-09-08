import assert from 'node:assert/strict';

const unique = (rows, key) => {
  const result = new Map(rows.map(row => [row[key], row]));
  assert.equal(result.size, rows.length, 'Duplicate identity: ' + key);
  return result;
};

export function projectA00({graph, overlay, nativeConcepts, crosswalks, assessments, sources,rights}) {
  assert.equal(overlay.neutral_curation.sha256,sources.originalGraph.sha256);
  assert.equal(overlay.neutral_curation.bytes,sources.originalGraph.bytes);
  const native = unique(nativeConcepts, 'concept_key');
  assert.ok(rights&&nativeConcepts.every(row=>row.rights_component_id===rights.id),'Unresolved concept rights identity');
  const localized = unique(overlay.concepts, 'key');
  const concepts = unique(graph.concepts, 'key');
  const modules = unique(assessments.modules, 'module_id');
  assert.equal(concepts.size, 35); assert.equal(native.size, 35); assert.equal(localized.size, 35);
  assert.equal(modules.size, 75); assert.equal(overlay.locale, 'id-ID');
  const crosswalk = new Map();
  for (const row of crosswalks) {
    const moduleId = row.semantic_key.split(':').at(-1);
    assert.ok(modules.has(moduleId),'Crosswalk outside module inventory');
    assert.equal(row.payload.target_id,modules.get(moduleId).unit_id,'Module crosswalk target mismatch');
    assert.ok(!crosswalk.has(moduleId)); crosswalk.set(moduleId, row);
  }
  assert.equal(crosswalk.size,modules.size);
  const objectives = new Set(), nativeObjectiveIds = new Set();
  const projected = graph.concepts.map(concept => {
    const record = native.get(concept.key), term = localized.get(concept.key);
    assert.ok(record && term); assert.equal(record.label_en_us, concept.label_en_us);
    assert.equal(record.definition_en_us, concept.definition_en_us);
    assert.equal(record.concept_role, concept.role);
    assert.equal(record.mapping_source_sha256,'sha256:'+sources.graph.sha256);
    for(const id of record.objective_unit_ids){assert.ok(!nativeObjectiveIds.has(id),'Repeated native objective identity');nativeObjectiveIds.add(id);}
    assert.deepEqual(record.prerequisite_ids, concept.prerequisite_keys.map(key => {
      assert.ok(native.has(key), 'Missing prerequisite ' + key); return native.get(key).id;
    }));
    assert.equal(record.module_evidence_count, concept.evidence.length);
    const references = concept.evidence.map(evidence => {
      const module = modules.get(evidence.module_id), mapping = crosswalk.get(evidence.module_id);
      assert.ok(module && mapping, 'Unmapped evidence module');
      assert.equal(mapping.payload.target_id, module.unit_id);
      assert.ok(record.module_unit_ids.includes(mapping.payload.source_id), 'Native module identity mismatch');
      for (const ordinal of evidence.objective_numbers) {
        assert.ok(Number.isInteger(ordinal) && ordinal > 0);
        const key = evidence.module_id + ':' + ordinal;
        assert.ok(!objectives.has(key), 'Source objective assigned twice'); objectives.add(key);
      }
      return {...evidence, native_module_unit_id:mapping.payload.source_id,
        projected_unit_id:module.unit_id, source_objective_numbering:'frozen_en_US_not_localized_numbering',
        module_url:module.module_url};
    });
    assert.equal(record.objective_unit_ids.length, references.reduce((n,row)=>n+row.objective_numbers.length,0));
    return {id:record.id, key:concept.key, role:concept.role,
      labels:{id:term.label,en:concept.label_en_us}, definitions:{id:term.definition,en:concept.definition_en_us},
      prerequisite_keys:concept.prerequisite_keys, prerequisite_ids:record.prerequisite_ids,
      objective_unit_ids:record.objective_unit_ids, rights_component_id:record.rights_component_id,
      objective_identity_order_is_not_an_ordinal_crosswalk:true,
      modules:references};
  });
  assert.equal(objectives.size, 245);
  assert.equal(nativeObjectiveIds.size,245);
  const visiting = new Set(), visited = new Set();
  function visit(key) {
    assert.ok(!visiting.has(key), 'Concept prerequisite cycle');
    if (visited.has(key)) return;
    visiting.add(key); for (const parent of concepts.get(key).prerequisite_keys) visit(parent);
    visiting.delete(key); visited.add(key);
  }
  for (const key of concepts.keys()) visit(key);
  const rows = assessments.modules.flatMap(module => module.assessments.map(row => ({...row,module_id:module.module_id})));
  assert.equal(unique(rows,'id').size,8105);
  for(const row of rows) {
    assert.equal(row.statement_anchors.length,1);
    assert.equal(row.solution_anchors.length,row.has_explicit_solution?1:0);
    assert.equal(row.solution_gap_id===null,row.has_explicit_solution);
    assert.ok(assessments.category_labels[row.category]);
    const module=modules.get(row.module_id);
    for(const anchor of [row,...row.statement_anchors,...row.solution_anchors])
      assert.equal(anchor.route_url,module.module_url+'#'+anchor.native_id);
  }
  assert.equal(rows.filter(row=>row.has_explicit_solution).length,5240);
  const counts={concepts:35,prerequisite_edges:projected.reduce((n,row)=>n+row.prerequisite_keys.length,0),
    source_objectives:245,localized_objectives:overlay.localized_objective_accounting.localized_objective_items,
    evidence_modules:new Set(projected.flatMap(row=>row.modules.map(module=>module.module_id))).size,
    modules:75,assessments:8105,supplied_solutions:5240,explicit_solution_gaps:2865};
  assert.equal(counts.prerequisite_edges,76);assert.equal(counts.localized_objectives,246);assert.equal(counts.evidence_modules,60);
  assert.deepEqual(Object.fromEntries(['a00_core','a00_supporting','a10_bridge'].map(role=>
    [role,projected.filter(row=>row.role===role).length])),{a00_core:23,a00_supporting:6,a10_bridge:6});
  return {schema:'a00-concept-teacher-capability/1',course_id:'A00',sources,counts,
    concept_rights:rights,
    source_revision:graph.source.edition_commit,reading_language:'id-ID',
    labels_reused_without_translation:true,exercise_to_concept_alignment_claimed:false,
    mastery_or_automatic_diagnosis_claimed:false,
    localized_overlay_binding:{declared_original_neutral:overlay.neutral_curation,
      original_neutral_source:sources.originalGraph,emitted_neutral_metadata:sources.graph,
      metadata_transformation:'remove_machine_local_curriculum_source_path; add_authority_id_and_portable_path_locator; all_other_fields_equal',
      current_validation:'exact_concept_keys_native_english_definitions_native_ids_and_prerequisites_replayed; labels_preserved'},
    concepts:projected,category_labels:assessments.category_labels,
    modules:assessments.modules.map(({assessments:items,...module})=>module),
    assessments:rows};
}
