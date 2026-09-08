"""Replay A10's immutable native JSONL into a metadata-only learning projection.

The ZIP stays compressed and records are streamed. Native bodies and historical
translation text are never retained. Native record hashes permit exact source
rehydration; this projection is not a replacement native backend.
"""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from acquire_a10_capability_inputs_v1 import INPUTS, file_identity

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "work/a10-native-inputs-v1"
ADAPTER = ROOT / "backend/course-capsule-v1/adapters/a10-capability-v1"
AUTHORITY = ROOT / "backend/v2.3/authorities/A10_ELEMENTARY_ALGEBRA_PUBLIC_RELEASE_AUTHORITY_20260906.json"
AUTHORITY_SHA = "5ae589b75842923a0ebc530d649498bec9bb962ae0d14ab1cb44a9aedb573678"
EXPORT_SHA = "f15ef8af0fec60c316896d0c60d8c01b1924b826eb1e8f4c62c883b8c59dd564"
CONTRACT = "course-learning-capability/1"
PDF_URL = INPUTS["reader.pdf"]["url"]
EXPECTED = {"artifact": 491, "asset": 4024, "concept": 144, "correction": 678,
            "course": 1, "edition": 1, "placement": 55273, "program": 1,
            "qa_event": 575, "relation": 91373, "resource": 1, "rights": 4025,
            "segment": 26824, "source_alias": 55357, "term": 1060,
            "translation": 26824, "translation_event": 240068, "unit": 55273, "work": 1}
PEDAGOGY = {"has_problem", "has_solution", "solves", "solution_status", "defines", "denotes"}

# Explicit field allowlists prevent the accidental ingestion of mathematical
# bodies while retaining native field names and scope. Hashes bind omitted data.
FIELDS = {
    "unit": "id kind parent_unit_id source_module_id source_element_id source_fragment_sha256 rights_id solution_status",
    "placement": "id unit_id parent_unit_id ordinal topology_path",
    "relation": "id predicate subject_id object_id object_uri ordinal qualifier confidence evidence_path evidence_element_id status",
    "term": "id concept_id module_unit_id owner_unit_id segment_id scope normalized_key ledger_id preferred_target_text source_text target_locale register rejected_or_variant mapping_status status evidence_path live_ledger_path milestone_witness source_path xml_path",
    "correction": "id target_id affected_source_id ledger_id scope defect_type status source_locator source_sha256 evidence_path live_ledger_path milestone_witness upstream_disposition",
    "rights": "id subject_id inheritance_id scope_kind license_id license_url attribution_text evidence_path evidence_element_id review_status third_party_status status",
    "concept": "id preferred_label source_language source_definition_unit_id mapping_status status",
    "segment": "id owner_unit_id source_module_id rights_id source_fragment_sha256 source_language role field_kind translatable translation_policy",
    "translation": "id segment_id source_segment_sha256 target_path target_sha256 target_locale state status alignment",
}


def require(condition: bool, code: str) -> None:
    if not condition:
        raise ValueError(code)


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def project_record(row: dict, raw: bytes) -> dict:
    result = {**{key: row.get(key) for key in FIELDS[row["record_type"]].split()},
              "native_record_sha256": sha(raw)}
    if row["record_type"] == "unit" and row["kind"] == "module":
        result["native_module_title"] = row["title"]
    return result


def replay_native(native: Path) -> dict:
    """Verify all 19 export streams, including unprojected history and assets."""
    for name, expected in INPUTS.items():
        require(file_identity(native / name) == {k: expected[k] for k in ("bytes", "sha256")},
                f"A10-INPUT-IDENTITY:{name}")
    require(file_identity(AUTHORITY)["sha256"] == AUTHORITY_SHA, "A10-AUTHORITY-IDENTITY")
    result = {kind: [] for kind in FIELDS}
    ledger = []
    all_ids: set[str] = set()
    refs: set[str] = set()
    predicates = Counter()
    with zipfile.ZipFile(native / "backend-core.zip") as archive:
        raw_manifest = archive.read("exports/manifest.json")
        require(sha(raw_manifest) == EXPORT_SHA, "A10-EXPORT-MANIFEST")
        manifest = json.loads(raw_manifest)
        require(manifest["record_counts"] == EXPECTED, "A10-EXPECTED-RECORD-COUNTS")
        specs = [row for row in manifest["files"] if row["format"] == "jsonl"]
        require(len(specs) == len(EXPECTED), "A10-EXPORT-TYPES")
        for spec in specs:
            kind = spec["record_type"]
            digest, id_digest = hashlib.sha256(), hashlib.sha256()
            size = count = 0
            previous = ""
            with archive.open("exports/" + spec["path"]) as stream:
                for raw in stream:
                    digest.update(raw); size += len(raw); count += 1
                    row = json.loads(raw)
                    rid = row["id"]
                    require(row["record_type"] == kind and row["schema_version"] == "1.1.0", "A10-RECORD-SCHEMA")
                    require(rid not in all_ids and previous < rid, "A10-NATIVE-ID-UNIQUENESS-ORDER")
                    all_ids.add(rid); previous = rid
                    id_digest.update((rid + "\n").encode())
                    if kind == "relation":
                        predicates[row["predicate"]] += 1
                        refs.update(value for value in (row["subject_id"], row["object_id"]) if value)
                    if kind in result:
                        result[kind].append(project_record(row, raw))
            require((count, size, digest.hexdigest()) == (spec["rows"], spec["bytes"], spec["sha256"]),
                    f"A10-EXPORT-STREAM:{kind}")
            ledger.append({**spec, "path": "exports/" + spec["path"], "id_sequence_sha256": id_digest.hexdigest()})
    require(not (refs - all_ids), "A10-RELATION-REFERENCE")
    result["native_ledger"] = {"schema": "a10-native-record-ledger/1", "records": sum(EXPECTED.values()),
        "record_counts": EXPECTED, "streams": ledger, "stable_identifiers": manifest["stable_identifiers"],
        "native_manifest_sha256": EXPORT_SHA, "native_predicate_counts": dict(sorted(predicates.items())),
        "loss_accounting": "All 19 JSONL streams are hash/count/ID verified. Selected metadata fields are projected; native bodies, CSV duplicates, historical event payloads and nonselected record bodies remain only in the pinned native release."}
    result["all_ids"] = all_ids
    return result


def pdf_routes(native: Path, modules: list[dict]) -> dict:
    """Independently resolve named destinations from immutable PDF page objects."""
    from pypdf import PdfReader

    reader = PdfReader(native / "reader.pdf", strict=True)
    require(len(reader.pages) == 1627, "A10-PDF-PAGE-COUNT")
    destinations = reader.named_destinations
    module_routes = {}
    for module in modules:
        mid = module["module_id"]
        name = "/module-" + mid
        require(name in destinations, f"A10-PDF-MODULE-NAME:{mid}")
        dest = destinations[name]
        page = reader.get_destination_page_number(dest) + 1
        require(1 <= page <= 1627, "A10-PDF-PAGE-RANGE")
        module_routes[mid] = {"module_id": mid, "named_destination": name, "physical_page": page,
            "url": PDF_URL + f"#page={page}", "route_scope": "module_start_not_exercise_or_solution",
            "pdf_page_object": [dest.page.idnum, dest.page.generation]}
    pages = [module_routes[m["module_id"]]["physical_page"] for m in modules]
    require(pages == sorted(set(pages)) and len(pages) == 82, "A10-PDF-MODULE-ORDER")
    elements = []
    for name, dest in sorted(destinations.items()):
        match = re.fullmatch(r"/(m\d+)--(.+)", name)
        if match:
            page = reader.get_destination_page_number(dest) + 1
            elements.append({"source_module_id": match[1], "source_element_id": match[2],
                "named_destination": name, "physical_page": page,
                "pdf_page_object": [dest.page.idnum, dest.page.generation],
                "destination_left": float(dest.left) if dest.left is not None else None,
                "destination_top": float(dest.top) if dest.top is not None else None,
                "item_reading_route_verified": False})
    return {"schema": "a10-pdf-routes/1", "pdf_sha256": INPUTS["reader.pdf"]["sha256"],
            "modules": list(module_routes.values()), "elements": elements,
            "page_count": 1627, "named_destination_count": len(destinations)}


def derive_projection(native: Path = NATIVE) -> dict:
    data = replay_native(native)
    authority = json.loads(AUTHORITY.read_text(encoding="utf-8"))
    modules = authority["modules"]
    require([m["ordinal"] for m in modules] == list(range(1, 83)), "A10-MODULE-SEQUENCE")
    routes = pdf_routes(native, modules)
    route_by_module = {r["module_id"]: r for r in routes["modules"]}
    units = {r["id"]: r for r in data["unit"]}
    placements = {r["unit_id"]: r for r in data["placement"]}
    concepts = {r["id"] for r in data["concept"]}
    rights = {r["id"] for r in data["rights"]}
    segments = {r["id"]: r for r in data["segment"]}
    native_modules = {r["source_module_id"]: r for r in data["unit"] if r["kind"] == "module"}
    require(set(native_modules) == set(route_by_module), "A10-MODULE-IDENTITIES")
    require(len(placements) == len(units) and set(placements) == set(units), "A10-PLACEMENT-COVERAGE")
    scoped_units: dict[tuple[str, str], list[dict]] = defaultdict(list)
    siblings = set()
    for unit in data["unit"]:
        placement = placements[unit["id"]]
        parent = unit["parent_unit_id"]
        require(placement["parent_unit_id"] == parent, "A10-PLACEMENT-PARENT")
        require(parent is None or parent in units, "A10-UNIT-PARENT")
        require(unit["rights_id"] in rights, "A10-UNIT-RIGHTS")
        sibling_key = (parent, placement["ordinal"])
        require(sibling_key not in siblings, "A10-SIBLING-ORDINAL")
        siblings.add(sibling_key)
        if unit["source_element_id"]:
            scoped_units[unit["source_module_id"], unit["source_element_id"]].append(unit)

    def order_key(uid: str) -> tuple[int, ...]:
        seen = set(); path = []
        while uid:
            require(uid not in seen, "A10-PLACEMENT-CYCLE")
            seen.add(uid)
            p = placements[uid]
            require(isinstance(p["ordinal"], int) and p["ordinal"] >= 0, "A10-PLACEMENT-ORDINAL")
            path.append(p["ordinal"]); uid = p["parent_unit_id"]
        return tuple(reversed(path))

    for row in routes["elements"]:
        matches = scoped_units.get((row["source_module_id"], row["source_element_id"]), [])
        require(len(matches) == 1, "A10-PDF-SCOPED-ELEMENT-JOIN")
        row["native_unit_id"] = matches[0]["id"]
        row["native_unit_kind"] = matches[0]["kind"]
    pedagogical = [r for r in data["relation"] if r["predicate"] in PEDAGOGY]
    rel = defaultdict(list)
    for r in pedagogical:
        rel[r["predicate"], r["subject_id"]].append(r)
    exercise_rows = []
    by_module = defaultdict(list)
    for unit in data["unit"]:
        if unit["kind"] == "exercise":
            by_module[unit["source_module_id"]].append(unit)
    element_routes = {row["native_unit_id"]: row for row in routes["elements"]}
    module_rows = []
    for module in modules:
        mid = module["module_id"]
        ordered = sorted(by_module[mid], key=lambda u: order_key(u["id"]))
        for ordinal, unit in enumerate(ordered, 1):
            eid = unit["id"]
            problem_links = rel["has_problem", eid]
            solution_links = rel["has_solution", eid]
            missing_links = rel["solution_status", eid]
            require(len(problem_links) == 1 and len(solution_links) <= 1, "A10-EXERCISE-LINK-COUNT")
            problem = units[problem_links[0]["object_id"]]
            require(problem["kind"] == "problem" and problem["parent_unit_id"] == eid, "A10-PROBLEM-PARENT")
            solution = units[solution_links[0]["object_id"]] if solution_links else None
            if solution:
                require(solution["kind"] == "solution" and solution["parent_unit_id"] == eid, "A10-SOLUTION-PARENT")
                inverse = rel["solves", solution["id"]]
                require(len(inverse) == 1 and inverse[0]["object_id"] == eid, "A10-SOLVES-EXERCISE-NOT-PROBLEM")
                require(not missing_links and unit["solution_status"] == "provided" and
                        solution_links[0]["qualifier"] == "provided_upstream", "A10-PROVIDED-SOLUTION-STATE")
            else:
                require(len(missing_links) == 1 and missing_links[0]["object_id"] is None and
                        missing_links[0]["qualifier"] == unit["solution_status"] == "not_provided_upstream",
                        "A10-EXPLICIT-MISSING-SOLUTION")
            require(problem["source_module_id"] == mid and (not solution or solution["source_module_id"] == mid), "A10-EXERCISE-MODULE")
            exact = element_routes.get(eid)
            exercise_rows.append({**unit, "module_id": mid, "ordinal_within_module": ordinal,
                "ordinal_is_printed_exercise_number": False, "placement_order": list(order_key(eid)),
                "problem_id": problem["id"], "solution_id": solution["id"] if solution else None,
                "problem_source_sha256": problem["source_fragment_sha256"],
                "solution_source_sha256": solution["source_fragment_sha256"] if solution else None,
                "module_reading_url": route_by_module[mid]["url"],
                "declared_exercise_pdf_page": exact["physical_page"] if exact else None,
                "declared_exercise_pdf_destination": exact["named_destination"] if exact else None,
                "exercise_reading_route_verified": False,
                "has_problem_relation_id": problem_links[0]["id"],
                "solution_state_relation_id": (solution_links or missing_links)[0]["id"]})
        solved = sum(u["solution_status"] == "provided" for u in ordered)
        module_rows.append({**module, "module_unit_id": native_modules[mid]["id"],
            "title_en": native_modules[mid]["native_module_title"],
            "native_record_sha256": native_modules[mid]["native_record_sha256"],
            "exercise_count": len(ordered), "solution_count": solved,
            "missing_solution_count": len(ordered) - solved, **route_by_module[mid]})
    require(len(exercise_rows) == 9406 and sum(r["solution_id"] is not None for r in exercise_rows) == 6106,
            "A10-EXERCISE-SOLUTION-COUNTS")
    require({r["problem_id"] for r in exercise_rows} == {u["id"] for u in data["unit"] if u["kind"] == "problem"}, "A10-ALL-PROBLEMS-USED")
    require({r["solution_id"] for r in exercise_rows if r["solution_id"]} == {u["id"] for u in data["unit"] if u["kind"] == "solution"}, "A10-ALL-SOLUTIONS-USED")
    term_history = [r for r in data["relation"] if r["predicate"] == "supersedes"]
    terms_by_id = {r["id"]: r for r in data["term"]}
    successors = defaultdict(list)
    predecessors = defaultdict(list)
    for relation in term_history:
        require(relation["subject_id"] in terms_by_id and relation["object_id"] in terms_by_id,
                "A10-TERM-SUPERSESSION-REFERENCE")
        successors[relation["object_id"]].append(relation["subject_id"])
        predecessors[relation["subject_id"]].append(relation["object_id"])
    for term in data["term"]:
        require(not term["concept_id"] or term["concept_id"] in concepts, "A10-TERM-CONCEPT")
        for key in ("module_unit_id", "owner_unit_id"):
            require(not term[key] or term[key] in units, "A10-TERM-UNIT")
        require(not term["segment_id"] or term["segment_id"] in segments, "A10-TERM-SEGMENT")
        term["evidence_kind"] = "curated_designation" if term["ledger_id"] else "source_occurrence_not_target_decision"
        owner = units.get(term["owner_unit_id"]) or units.get(term["module_unit_id"])
        term["module_id"] = owner["source_module_id"] if owner else None
        term["provenance_module_id"] = term["module_id"]
        term["superseded_by"] = sorted(successors[term["id"]])
        term["supersedes"] = sorted(predecessors[term["id"]])
        term["current_use_status"] = "superseded_in_native_ledger" if term["superseded_by"] else "native_record_not_superseded"
    for correction in data["correction"]:
        require(correction["target_id"] in data["all_ids"], "A10-CORRECTION-TARGET")
        owner = units.get(correction["target_id"])
        segment = segments.get(correction["target_id"])
        correction["module_id"] = owner["source_module_id"] if owner else (segment["source_module_id"] if segment else None)
        correction["target_record_type"] = "unit" if owner else ("segment" if segment else "other_native_record")
    for right in data["rights"]:
        require(right["subject_id"] in data["all_ids"] and (not right["inheritance_id"] or right["inheritance_id"] in rights), "A10-RIGHTS-REFERENCE")
    translations = []
    used_segments = set()
    for target in data["translation"]:
        sid = target["segment_id"]
        require(sid in segments and sid not in used_segments, "A10-CURRENT-TRANSLATION-UNIQUENESS")
        used_segments.add(sid); segment = segments[sid]
        require(segment["owner_unit_id"] in units and segment["rights_id"] in rights, "A10-SEGMENT-REFERENCE")
        require(target["state"] == "language_reviewed" and target["alignment"] == "current" and target["target_locale"] == "id", "A10-TRANSLATION-STATE")
        require(target["source_segment_sha256"] == segment["source_fragment_sha256"], "A10-TRANSLATION-SOURCE-BINDING")
        translations.append({"segment": segment, "translation": target})
    require(used_segments == set(segments), "A10-TRANSLATION-COVERAGE")
    require(sum(bool(t["ledger_id"]) for t in data["term"]) == 600, "A10-CURATED-TERM-COUNT")
    claim_boundary = {"schema": "a10-capability-claim-boundary/1", "native_text_copied": False,
        "native_source_formats_changed": False, "complete_native_backend_reconstructed": False,
        "full_native_replay_requires_pinned_release": True, "central_projection_rebuildable": True,
        "module_page_routes_verified": True, "exercise_numbers_are_module_local_projection_order": True,
        "supplied_solution_identity_is_not_a_verified_solution_page": True,
        "indonesian_semantic_html_claimed": False, "indonesian_mathml_claimed": False,
        "pdf_ua_claimed": False, "wcag_conformance_claimed": False,
        "official_teacher_manual_claimed": False, "complete_solution_key_claimed": False,
        "component_rights_flattened": False, "source_occurrences_are_target_term_decisions": False}
    counts = {"native_records": sum(EXPECTED.values()), "modules": 82, "pdf_pages": 1627,
        "exercises": 9406, "solutions": 6106, "missing_solutions": 3300,
        "concepts": 144, "terms": 1060, "curated_terms": 600, "source_term_occurrences": 460,
        "corrections": 678, "rights_records": 4025, "current_translations": 26824,
        "module_routes": 82, "declared_exercise_destinations": sum(bool(r["declared_exercise_pdf_destination"]) for r in exercise_rows),
        "verified_exercise_reading_routes": 0,
        "pdf_element_kinds": dict(sorted(Counter(r["native_unit_kind"] for r in routes["elements"]).items()))}
    english_path = ROOT / "docs/interface/evidence/a10-original-english-mirror.json"
    english = json.loads(english_path.read_text(encoding="utf-8"))
    require(english["course_id"] == "A10" and english["content_language"] == "en" and
            english["status"] == "published_and_anonymously_verified", "A10-ENGLISH-MIRROR-EVIDENCE")
    return {"source_lock": {"schema": "a10-capability-inputs/1", "inputs": [{"name": name, **spec} for name, spec in INPUTS.items()],
                "authority_path": AUTHORITY.relative_to(ROOT).as_posix(), "authority_sha256": AUTHORITY_SHA,
                "english_evidence_path": english_path.relative_to(ROOT).as_posix(),
                "english_evidence_sha256": file_identity(english_path)["sha256"],
                "export_manifest_sha256": EXPORT_SHA},
            "english_source_mirror": english,
            "native_record_ledger": data["native_ledger"], "module_index": module_rows,
            "exercise_index": exercise_rows, "unit_reference_index": data["unit"],
            "placement_index": data["placement"], "pedagogical_relation_index": pedagogical,
            "concept_index": data["concept"], "terms_index": data["term"],
            "terminology_history_index": term_history,
            "corrections_index": data["correction"], "rights_index": data["rights"],
            "translation_index": translations, "pdf_route_evidence": routes,
            "capabilities": {"schema": CONTRACT, "course_id": "A10", "locale": "id-ID", "counts": counts},
            "claim_boundary": claim_boundary}
