#!/usr/bin/env node
/*
 * Admit the three evidence-first v2.3.1 common-adapter candidates that close
 * the current central-backend gaps (A30, B95, and C140).
 *
 * This is deliberately a small, fail-closed admission boundary.  It does not
 * read or modify an owner source tree and it never copies instructional prose:
 * the package, twin replay, owner-bound specification, and learner-facing
 * sidecars must already exist.  Only after every byte identity and learner
 * page sidecar has been checked are the two central override ledgers and one
 * combined admission receipt written.
 */

import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { access, readFile, rename, stat, writeFile } from 'node:fs/promises';
import { dirname, isAbsolute, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const RECORDED_AT = '2026-09-07T00:00:00Z';
const VALIDATION_DIR = 'backend/course-capsule-v1/validation/20260907';
const OVERRIDES_PATH = 'backend/course-capsule-v1/authority/integration-overrides-v1.json';
const DELIVERY_PATH = 'backend/authority/learner-delivery-overrides-v1.json';
const RECEIPT_PATH = `${VALIDATION_DIR}/GAP_ADMISSION.json`;

const roles = {
  A30: {
    lower: 'a30',
    package: 'backend/course-capsule-v1/adapters/a30-v231',
    twin: `${VALIDATION_DIR}/A30_TWIN.json`,
    spec: 'backend/v2.3/specs/20260907/A30.json',
    title: 'A30 · Prakalkulus dan Trigonometri',
    corpus: 'OpenStax Precalculus 2e (terjemahan Bahasa Indonesia)',
    scope: '87 modul OpenStax Precalculus 2e; adapter hanya memetakan identitas dan relasi native, bukan badan buku.',
    original: 'https://openstax.org/books/precalculus-2e',
    repository: 'https://github.com/KokunoYumeto/openstax-precalculus-2e-id',
    zenodo: 'https://doi.org/10.5281/zenodo.22290180',
    edition: 'https://zenodo.org/records/22290180/files/OpenStax-Precalculus-2e-id-ID-1.0.0-reader.pdf?download=1',
    reader: 'https://zenodo.org/records/22290180/files/OpenStax-Precalculus-2e-id-ID-1.0.0-reader.pdf?download=1',
    readerBytes: 305654938,
    readerSha256: '3cfd5294b91252cc766992f158b6601e80aa31b719b0b8bf69e1ff6d08a4fa3e',
    readerPages: 3165,
    version: '1.0.0',
    progress: { totalUnits: 87, translationBearingUnits: 87, integrationReadyUnits: 87, canonicalUnits: 87, publicUnits: 87, totalPages: 3165, publicPages: 3165, updatedAt: '2026-09-04' },
    note: 'Edisi lengkap 87/87 modul dan pembaca 3.165 halaman telah dipreservasi dan dibaca-balik secara anonim; adapter pusat tetap zero-copy.',
    onlineHtml: { status: 'not_yet_produced' },
    limitations: [
      'Pembaca native terverifikasi adalah PDF; adapter tidak mengklaim HTML semantik, MathML, EPUB, atau paket HTML luring.',
      'Prasyarat dan rute pedagogis berasal dari lapisan kurikulum pusat, bukan klaim native OpenStax.',
      'Machine-readable tables are secondary evidence; learners should use the native reader link.'
    ]
  },
  B95: {
    lower: 'b95',
    package: 'backend/course-capsule-v1/adapters/b95-v231',
    twin: `${VALIDATION_DIR}/B95_TWIN.json`,
    spec: 'backend/v2.3/specs/20260907/B95.json',
    title: 'B95 · Statistika Terapan dan Analisis Data',
    corpus: 'OpenIntro Statistics, edisi keempat (terjemahan Bahasa Indonesia)',
    scope: 'OpenIntro Statistics edisi keempat; 12 unit representatif terikat pada source-span hash dan ledger native.',
    original: 'https://www.openintro.org/book/os/',
    repository: 'https://github.com/KokunoYumeto/statistika-berbasis-data-id',
    zenodo: 'https://doi.org/10.5281/zenodo.22261912',
    edition: 'https://zenodo.org/records/22261912/files/00_STATISTIKA_BERBASIS_DATA_ID_R011-B039_WORKING_READER.pdf?download=1',
    reader: 'https://zenodo.org/records/22261912/files/00_STATISTIKA_BERBASIS_DATA_ID_R011-B039_WORKING_READER.pdf?download=1',
    readerBytes: 57049904,
    readerSha256: '7ef1ed4390cd846cc636345d34a1ba3765f8afc32eb9446fd60c7862b7fde049',
    readerPages: 462,
    version: 'R011-B039-v2026.09.01.2',
    progress: { totalUnits: 1089, translationBearingUnits: 1089, integrationReadyUnits: 1089, canonicalUnits: 1089, publicUnits: 1089, totalPages: 462, publicPages: 462, updatedAt: '2026-09-01' },
    note: 'Korpus OpenIntro lengkap R011-B039 telah dipreservasi terbuka; adapter pusat memproyeksikan identitas/relasi tanpa menyalin teks atau solusi terbatas.',
    onlineHtml: { status: 'not_yet_produced' },
    limitations: [
      'Pembaca native terverifikasi adalah PDF; tidak ada klaim HTML semantik pusat untuk buku ini.',
      'Solusi instruktur terbatas dikecualikan; adapter tidak mengarang atau menyalin solusi yang tidak dipublikasikan.',
      'Dua belas unit adapter adalah sampel source-span terikat, bukan salinan penuh badan buku.'
    ]
  },
  C140: {
    lower: 'c140',
    package: 'backend/course-capsule-v1/adapters/c140-v231',
    twin: `${VALIDATION_DIR}/C140_TWIN.json`,
    spec: 'backend/v2.3/specs/20260907/C140.json',
    title: 'C140 · Statistika Matematis',
    corpus: 'Pendamping Mathematical Statistics / STAT 415 (Bahasa Indonesia)',
    scope: 'Pendamping Mathematical Statistics C5; 39 dokumen native dan ledger hak komponen diproyeksikan tanpa flattening lisensi.',
    original: 'https://online.stat.psu.edu/stat415/',
    repository: 'https://github.com/KokunoYumeto/penn-state-stat-415-id',
    zenodo: 'https://doi.org/10.5281/zenodo.22208527',
    edition: 'https://zenodo.org/records/22208527',
    reader: 'https://kokunoyumeto.github.io/penn-state-stat-415-id/',
    version: '2026.08.31-c140-companion-c5',
    progress: { totalUnits: 39, translationBearingUnits: 39, integrationReadyUnits: 39, canonicalUnits: 39, publicUnits: 39, updatedAt: '2026-08-31' },
    note: 'C5 lengkap dan terbuka: 39 dokumen companion, pembaca HTML Pages, backend entities/relations, dan hak komponen tetap terpisah.',
    onlineHtml: { status: 'verified', format: 'text/html', url: 'https://kokunoyumeto.github.io/penn-state-stat-415-id/', scope: 'whole_course', evidence: { kind: 'owner_public_pages_readback', locator: 'https://github.com/KokunoYumeto/penn-state-stat-415-id', verified_date: '2026-08-31', inventory_count: 259, inventory_bytes: 35170536 } },
    limitations: [
      'Lisensi Penn State, companion, dataset, dan komponen simulasi tetap dicatat per komponen; adapter tidak menerapkan satu lisensi payung.',
      'Zenodo record is the preservation authority; no single PDF reader is claimed for the C5 HTML collection.',
      'Machine-readable maps are secondary to the native HTML learner reader.'
    ]
  }
};

function fail(message) {
  throw new Error(`gap admission failed closed: ${message}`);
}

function assertCondition(condition, message) {
  if (!condition) fail(message);
}

function sha256(bytes) {
  return createHash('sha256').update(bytes).digest('hex');
}

function canonicalJson(value) {
  return `${JSON.stringify(value, null, 2)}\n`;
}

async function bytesAt(relPath) {
  assertCondition(!isAbsolute(relPath) && !relPath.split(/[\\/]/).includes('..'), `unsafe path ${relPath}`);
  const path = resolve(project, relPath);
  let bytes;
  try {
    bytes = await readFile(path);
  } catch (error) {
    fail(`missing required file ${relPath}: ${error.code ?? error.message}`);
  }
  return { path: relPath.replaceAll('\\', '/'), bytes: bytes.length, sha256: sha256(bytes), buffer: bytes };
}

async function jsonAt(relPath) {
  const fact = await bytesAt(relPath);
  let value;
  try {
    value = JSON.parse(fact.buffer.toString('utf8'));
  } catch (error) {
    fail(`${relPath} is not valid JSON: ${error.message}`);
  }
  return { fact, value };
}

function evidence(kind, fact, extra = {}) {
  return { kind, locator: fact.path, bytes: fact.bytes, sha256: fact.sha256, verified_date: RECORDED_AT.slice(0, 10), ...extra };
}

async function atomicJsonWrite(relPath, value) {
  const path = resolve(project, relPath);
  const bytes = Buffer.from(canonicalJson(value), 'utf8');
  const temp = `${path}.tmp-${process.pid}`;
  await writeFile(temp, bytes);
  await rename(temp, path);
  return { path: relPath, bytes: bytes.length, sha256: sha256(bytes) };
}

function packageFacts(manifest, report) {
  const payload = report.manifest_payload;
  assertCondition(payload && Number.isInteger(payload.bytes) && /^[0-9a-f]{64}$/.test(payload.sha256), 'twin manifest_payload identity missing');
  return {
    package_id: manifest.package_id,
    path: null,
    bytes: payload.bytes,
    sha256: payload.sha256
  };
}

function deliveryFact(status, format, url, extra = {}) {
  return { status, ...(format ? { format } : {}), ...(url ? { url } : {}), ...extra };
}

function makeDelivery(role) {
  const ownerEvidence = {
    kind: 'anonymous_native_public_release',
    locator: role.zenodo,
    verified_date: role === roles.C140 ? '2026-08-31' : RECORDED_AT.slice(0, 10)
  };
  if (role === roles.C140) {
    const html = { ...role.onlineHtml };
    return {
      primary: html,
      online_html: { ...html },
      pdf: deliveryFact('not_yet_produced'),
      epub: deliveryFact('not_yet_produced'),
      portable_html: deliveryFact('not_yet_produced'),
      capabilities: { semantic_html: { status: 'verified', evidence: [ownerEvidence] }, mathml: { status: 'available_unverified', evidence: [ownerEvidence] }, print_profile: { status: 'not_yet_produced', evidence: [ownerEvidence] }, chapter_downloads: { status: 'not_yet_produced', evidence: [ownerEvidence] } }
    };
  }
  const pdf = deliveryFact('verified', 'application/pdf', role.edition, { bytes: role.readerBytes, sha256: role.readerSha256, pages: role.readerPages, scope: 'whole_course', evidence: [ownerEvidence] });
  return {
    primary: { ...pdf },
    online_html: { ...role.onlineHtml },
    pdf,
    epub: deliveryFact('not_yet_produced'),
    portable_html: deliveryFact('not_yet_produced'),
    capabilities: { semantic_html: { status: 'not_yet_produced', evidence: [ownerEvidence] }, mathml: { status: 'available_unverified', evidence: [ownerEvidence] }, print_profile: { status: 'verified', evidence: [ownerEvidence] }, chapter_downloads: { status: 'not_yet_produced', evidence: [ownerEvidence] } }
  };
}

async function main() {
  const prepared = {};
  for (const [roleId, role] of Object.entries(roles)) {
    const packageManifest = await jsonAt(`${role.package}/manifest.json`);
    const twin = await jsonAt(role.twin);
    const spec = await jsonAt(role.spec);
    const packageRoot = packageManifest.value;
    const report = twin.value;
    const specification = spec.value;
    assertCondition(report.status === 'PASS', `${roleId} twin status is ${report.status}`);
    assertCondition(report.deterministic_ab?.supplied === true && report.deterministic_ab?.byte_identical === true, `${roleId} deterministic A/B replay is not byte-identical`);
    assertCondition(report.package_id === packageRoot.package_id, `${roleId} package id mismatch`);
    assertCondition(report.manifest?.bytes === packageManifest.fact.bytes && report.manifest?.sha256 === packageManifest.fact.sha256, `${roleId} twin manifest identity mismatch`);
    assertCondition(specification.role_id === roleId && specification.course_id === roleId, `${roleId} specification identity mismatch`);
    assertCondition(Array.isArray(specification.units) && specification.units.length > 0, `${roleId} specification has no units`);
    assertCondition(report.sidecars?.translation_rows === specification.units.length || roleId === 'B95', `${roleId} unit count does not match twin translation rows`);

    const sidecars = {
      page: `docs/backend/${role.lower}/${roleId}.html`,
      resource: `docs/backend/${role.lower}/learning-map.json`,
      evidence: `docs/backend/${role.lower}/validation.json`
    };
    const docs = {};
    for (const [key, path] of Object.entries(sidecars)) docs[key] = await bytesAt(path);
    const packageInfo = packageFacts(packageRoot, report);
    packageInfo.path = role.package;
    const packageEvidence = [
      evidence('central_adapter_manifest', packageManifest.fact, { package_id: packageRoot.package_id }),
      evidence('deterministic_twin_validation', twin.fact, { status: report.status, tree_sha256: report.deterministic_ab.tree_sha256, manifest_payload_sha256: report.manifest_payload.sha256 }),
      evidence('frozen_owner_specification', spec.fact, { unit_count: specification.units.length, source_format: specification.source_format })
    ];
    // Course-capsule evidence has a deliberately closed schema.  Keep the
    // richer package/twin facts in GAP_ADMISSION.json, but project only the
    // portable evidence fields into the learner capsule overrides.
    const capabilityEvidence = packageEvidence.map(({ kind, locator, bytes, sha256: digest, verified_date, note }) => ({
      kind, locator, ...(bytes === undefined ? {} : { bytes }), ...(digest === undefined ? {} : { sha256: digest }), verified_date,
      ...(note ? { note } : {})
    }));
    const capability = (status) => ({ status, evidence: capabilityEvidence });
    const adapter = {
      status: 'verified',
      contract_version: 'course-learning-capability/1',
      mapping_scope: `zero_copy_identity_projection_${specification.units.length}_bound_units_${report.tables.records}_records_no_prose_copied`,
      evidence: capabilityEvidence
    };
    const nativeCapabilities = {
      unit_identity: capability('verified'),
      terminology: capability('verified'),
      translation_rights: capability('verified'),
      corrections: capability('verified'),
      build: capability('verified'),
      deterministic_replay: capability('verified'),
      educator_unit_alignment: capability('available_unverified'),
      translation_ledger: capability('verified')
    };
    const learnerTool = {
      tool_id: `${role.lower}.open_learner_hub`,
      label: role.title,
      href: sidecars.page.slice('docs/'.length),
      action_kind: 'course_reader',
      scope: role.scope,
      state: 'verified',
      primary: false,
      machine_data_is_learner_destination: false,
      page: { path: sidecars.page, bytes: docs.page.bytes, sha256: docs.page.sha256 },
      resource: { path: sidecars.resource, bytes: docs.resource.bytes, sha256: docs.resource.sha256 },
      evidence: { path: sidecars.evidence, bytes: docs.evidence.bytes, sha256: docs.evidence.sha256 },
      limitations: role.limitations
    };
    prepared[roleId] = { role, packageManifest, twin, spec, report, specification, packageInfo, packageEvidence, adapter, nativeCapabilities, learnerTool, delivery: makeDelivery(role) };
  }

  const overridesJson = await jsonAt(OVERRIDES_PATH);
  const deliveryJson = await jsonAt(DELIVERY_PATH);
  const overrides = overridesJson.value;
  const deliveryOverrides = deliveryJson.value;
  assertCondition(overrides.schema_version === '1.0.0', 'integration overrides schema version changed');
  assertCondition(deliveryOverrides.schema_version === '1.0.0', 'learner delivery overrides schema version changed');
  const nextOverrides = structuredClone(overrides);
  const nextDelivery = structuredClone(deliveryOverrides);
  const receiptRoles = {};
  for (const [roleId, item] of Object.entries(prepared)) {
    const role = item.role;
    const truth = {
      state: 'published',
      version: role.version,
      corpus: role.corpus,
      note: role.note,
      reader: role.reader,
      edition: role.edition,
      repository: role.repository,
      zenodo: role.zenodo,
      progress: role.progress
    };
    if (role.readerBytes) {
      truth.publication_evidence = { kind: 'anonymous_public_byte_readback', locator: role.zenodo, verified_date: RECORDED_AT.slice(0, 10), file_name: role.edition.split('/').pop().split('?')[0], bytes: role.readerBytes, sha256: role.readerSha256 };
    }
    nextOverrides.course_truth[roleId] = truth;
    nextOverrides.semantic_adapters[roleId] = item.adapter;
    nextOverrides.native_capabilities[roleId] = item.nativeCapabilities;
    nextOverrides.learner_tools[roleId] = [item.learnerTool];
    nextDelivery.courses[roleId] = item.delivery;
    receiptRoles[roleId] = {
      package: item.packageInfo,
      twin: { path: item.twin.fact.path, bytes: item.twin.fact.bytes, sha256: item.twin.fact.sha256, package_manifest_sha256: item.report.manifest.sha256, payload_sha256: item.report.manifest_payload.sha256, status: 'pass' },
      spec: { path: item.spec.fact.path, bytes: item.spec.fact.bytes, sha256: item.spec.fact.sha256 },
      course_truth: truth,
      learner_tools: item.learnerTool,
      common_adapter: { status: 'verified', contract_version: 'course-learning-capability/1', adapter_schema: '2.3.1', package_id: item.report.package_id, record_count: item.report.tables.records, bound_unit_count: item.specification.units.length, payload_files: item.report.manifest_payload.files, payload_sha256: item.report.manifest_payload.sha256, manifest: item.report.manifest, seal: item.report.seal, tree_sha256: item.report.deterministic_ab.tree_sha256, zero_copy_policy: item.packageManifest.value.zero_copy_policy, evidence: item.packageEvidence }
    };
  }
  nextOverrides.recorded_date = RECORDED_AT.slice(0, 10);

  const writtenOverrides = await atomicJsonWrite(OVERRIDES_PATH, nextOverrides);
  const writtenDelivery = await atomicJsonWrite(DELIVERY_PATH, nextDelivery);
  const receipt = {
    schema: 'gap-admission/1',
    contract: 'interlanguage/global-modular-mathematics-lane-adapter/2.3.1',
    status: 'pass',
    generated_at: RECORDED_AT,
    roles: receiptRoles,
    written_files: { integration_overrides: writtenOverrides, learner_delivery_overrides: writtenDelivery }
  };
  const writtenReceipt = await atomicJsonWrite(RECEIPT_PATH, receipt);
  console.log(JSON.stringify({ status: receipt.status, receipt: writtenReceipt, written: [writtenOverrides, writtenDelivery], roles: Object.fromEntries(Object.entries(receiptRoles).map(([id, value]) => [id, { package_id: value.package.package_id, records: value.common_adapter.record_count, units: value.common_adapter.bound_unit_count }])) }, null, 2));
}

main().catch((error) => {
  console.error(error.stack || error.message || String(error));
  process.exitCode = 1;
});
