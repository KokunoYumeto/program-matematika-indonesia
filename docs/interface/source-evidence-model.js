// Existing native identities are retained; this consumer allocates no tags or sources.
const requireValue = (value, message) => { if (!value) throw new Error(message); };
const hash = value => typeof value === 'string' && /^[a-f0-9]{64}$/.test(value);
const key = row => JSON.stringify([row.kind ?? row.record_kind, row.id]);
const locator = row => JSON.stringify([row.evidence_sha256, row.json_pointer]);
const equalSet = (a, b) => a.length === b.length && new Set(a).size === a.length && a.every(x => b.includes(x));
const equalMultiset = (a, b) => JSON.stringify([...a].sort()) === JSON.stringify([...b].sort());
export function validateProjection(data) {
  requireValue(data?.schema === 'existing-proof-evidence-projection/1', 'schema');
  for (const name of ['records', 'artifact_bindings', 'use_edges', 'source_uses']) requireValue(Array.isArray(data[name]), name);
  requireValue(hash(data.input_identity?.sha256), 'input_identity');
  const records = new Map(), sources = new Map(), uses = new Map();
  for (const r of data.records) {
    requireValue(['requirement', 'reported_provider', 'lesson_route'].includes(r.record_kind) && typeof r.id === 'string' && r.id, 'record identity');
    requireValue(!records.has(key(r)) && r.global_tag === null && r.native_record && hash(r.native_record_sha256), 'record identity or provenance');
    if (r.record_kind === 'requirement') {
      requireValue(r.required_statement === r.native_record.required_statement && JSON.stringify(r.required_conditions) === JSON.stringify(r.native_record.required_conditions), 'requirement scope');
      requireValue(r.current_proof_admission === 'not_changed_by_adapter', 'proof admission');
      requireValue(r.independent_review === r.native_record.independent_review && r.whole_prerequisite_closure === r.native_record.whole_prerequisite_closure, 'review claim');
      requireValue(r.provider_binding === 'sha256:' + r.native_record.provider.source.sha256.toLowerCase() && r.consumer_binding === 'sha256:' + r.native_record.consumer.source.sha256.toLowerCase(), 'record bindings');
      requireValue(r.provider_full_generality === r.source_use_provenance?.author_review?.supplied_generality || (r.provider_full_generality === null && r.source_use_provenance?.author_review?.supplied_generality == null), 'provider generality');
      const old = r.native_record.consumer.source.sha256.toLowerCase();
      const now = r.current_revision_observation?.current_consumer?.sha256?.toLowerCase();
      requireValue(r.current_revision_state === (now === old ? 'same_bytes' : now ? 'changed_requires_reconciliation' : 'not_located'), 'revision state');
    }
    if (r.record_kind === 'reported_provider') {
      requireValue(r.current_proof_admission === 'reported_not_newly_admitted' && r.independent_review === r.native_record.independent_proof_check && r.whole_prerequisite_closure === r.native_record.whole_prerequisite_closure, 'reported provider');
      const old = r.native_record.proof.source_sha256.toLowerCase(), now = r.current_revision_observation?.current_source?.sha256?.toLowerCase();
      requireValue(r.source_binding === 'sha256:' + old && r.current_revision_state === (now === old ? 'same_bytes' : now ? 'changed_requires_reconciliation' : 'not_located'), 'reported revision');
    }
    records.set(key(r), r);
  }
  for (const s of data.artifact_bindings) {
    requireValue(hash(s.sha256) && s.binding_id === 'sha256:' + s.sha256 && !sources.has(s.binding_id), 'source fingerprint');
    requireValue(s.bibliographic_registry_ref === null && Array.isArray(s.used_by) && s.used_by.length, 'source identity');
    for (const edge of s.used_by) requireValue(records.has(key(edge.record)), 'source reverse reference');
    sources.set(s.binding_id, s);
  }
  for (const r of records.values()) {
    const expected = [...sources.values()].filter(s => s.used_by.some(e => key(e.record) === key(r))).map(s => s.binding_id);
    requireValue(equalSet(data.record_to_artifacts?.[r.record_kind]?.[r.id] ?? [], expected), 'record forward references');
  }
  for (const u of data.source_uses) {
    requireValue(hash(u.use_locator?.evidence_sha256) && typeof u.use_locator?.json_pointer === 'string', 'source-use locator');
    const useIdentity = JSON.stringify([locator(u.use_locator), key(u.within_record), key(u.target)]);
    requireValue(!uses.has(useIdentity) && sources.has(u.source_binding) && records.has(key(u.within_record)), 'source-use reference');
    requireValue(typeof u.target?.kind === 'string' && typeof u.target?.id === 'string', 'result reference');
    requireValue(u.canonical_source_key === null && u.source_bytes_checked_by_adapter === false && u.proof_closed_by_adapter === false && u.accessed_utc === null, 'source-use claim');
    uses.set(useIdentity, u);
  }
  const sourceIndex = new Map(), targetIndex = new Map();
  for (const u of uses.values()) {
    if (!sourceIndex.has(u.source_binding)) sourceIndex.set(u.source_binding, []);
    sourceIndex.get(u.source_binding).push(locator(u.use_locator));
    if (!targetIndex.has(key(u.target))) targetIndex.set(key(u.target), []);
    targetIndex.get(key(u.target)).push(locator(u.use_locator));
  }
  requireValue(Object.keys(data.source_to_uses ?? {}).length === sourceIndex.size, 'source index size');
  for (const [s, list] of sourceIndex) requireValue(equalMultiset((data.source_to_uses[s] ?? []).map(locator), list), 'source-use forward index');
  const importedTargets = Object.entries(data.target_to_uses ?? {}).flatMap(([kind, rows]) => Object.entries(rows).map(([id, locators]) => [key({kind, id}), locators.map(locator)]));
  requireValue(importedTargets.length === targetIndex.size, 'result index size');
  for (const [k, list] of importedTargets) requireValue(equalMultiset(list, targetIndex.get(k) ?? []), 'source-use reverse index');
  const expectedEdges = data.records.filter(r => r.record_kind === 'requirement').flatMap(r => r.native_record.consumer.uses.map((u, i) => [r.id, i, JSON.stringify(u)]));
  requireValue(data.use_edges.length === expectedEdges.length, 'requirement use count');
  for (const e of data.use_edges) {
    const r = records.get(key(e.requirement));
    requireValue(e.kind === 'requirement_use' && r && !e.proof_closed_by_adapter && e.current_revision_state === r.current_revision_state, 'requirement use');
    requireValue(e.provider_binding === r.provider_binding && e.consumer_binding === r.consumer_binding, 'requirement binding');
    requireValue(JSON.stringify(e.required_conditions) === JSON.stringify(r.required_conditions), 'use conditions');
    requireValue(expectedEdges.some(([id, i, native]) => id === e.requirement.id && i === e.native_use_index && native === JSON.stringify(e.native_use)), 'native use');
  }
  requireValue(new Set(data.use_edges.map(e => JSON.stringify([e.requirement.id, e.native_use_index]))).size === data.use_edges.length, 'duplicate use');
  for (const [name, count] of Object.entries({requirements: data.records.filter(r => r.record_kind === 'requirement').length, reported_providers: data.records.filter(r => r.record_kind === 'reported_provider').length, lesson_routes: data.records.filter(r => r.record_kind === 'lesson_route').length, explicit_requirement_uses: data.use_edges.length, source_uses: data.source_uses.length, artifact_fingerprints: data.artifact_bindings.length, new_global_tags: 0, new_mathematical_admissions: 0})) requireValue(data.counts?.[name] === count, 'counts: ' + name);
  return data;
}

export function evidenceIndex(data) {
  validateProjection(data);
  const resultMap = new Map(data.records.map(r => [key(r), {kind: r.record_kind, id: r.id, record: r}]));
  for (const u of data.source_uses) if (!resultMap.has(key(u.target))) resultMap.set(key(u.target), {...u.target, record: null});
  const results = [...resultMap.values()].sort((a, b) => a.id.localeCompare(b.id) || a.kind.localeCompare(b.kind));
  return {
    data, results,
    result(kind, id) {
      const ref = {kind, id}, row = resultMap.get(key(ref));
      if (!row) return null;
      const uses = data.source_uses.filter(u => key(u.target) === key(ref) || key(u.within_record) === key(ref));
      const bindings = new Set([...(data.record_to_artifacts?.[kind]?.[id] ?? []), ...uses.map(u => u.source_binding)]);
      return {...row, uses, sources: data.artifact_bindings.filter(s => bindings.has(s.binding_id)), dependencies: data.use_edges.filter(e => key(e.requirement) === key(ref)), contexts: data.records.filter(r => uses.some(u => key(u.within_record) === key(r)))};
    },
    source(binding) {
      const source = data.artifact_bindings.find(s => s.binding_id === binding);
      if (!source) return null;
      const uses = data.source_uses.filter(u => u.source_binding === binding);
      const targets = new Set([...uses.flatMap(u => [key(u.target), key(u.within_record)]), ...source.used_by.map(u => key(u.record))]);
      return {source, uses, results: results.filter(r => targets.has(key(r)))};
    },
  };
}

// Consume the common registry as supplied. Never allocate keys or guess from titles.
export function readRegistry(text) {
  const records = text.split(/\r?\n/).filter(x => x.trim()).map(line => JSON.parse(line));
  const seen = new Set();
  for (const r of records) {
    requireValue(typeof r.key === 'string' && r.key && !seen.has(r.key), 'registry key');
    seen.add(r.key);
  }
  return records;
}
export function registryMatches(source, registry) {
  if (registry === null) return {state: 'not_loaded', records: []};
  const records = registry.filter(r => [r.sha256, r.source_sha256, ...(Array.isArray(r.files) ? r.files.map(f => f.sha256) : [])].some(h => typeof h === 'string' && h.toLowerCase() === source.sha256));
  return {state: records.length === 1 ? 'matched_by_declared_hash' : records.length ? 'ambiguous' : 'unresolved', records};
}
