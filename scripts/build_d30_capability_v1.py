#!/usr/bin/env python3
"""Build the D30 course-learning-capability/1 zero-copy projection."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from d30_capability_model_v1 import (
    AUTHORITATIVE_ORIGINALS,
    BUNDLE_FILES,
    CONCEPT_DOI,
    CONTENT_COMMIT,
    CONTENT_TREE,
    CONTRACT,
    COURSE_ID,
    DOI,
    EXPECTED_COUNTS,
    LOCAL_CHECKOUT_COMMIT,
    LOCAL_CHECKOUT_TREE,
    NATIVE_COURSE_ID,
    PAGES,
    PUBLIC_FILES,
    RECORD_ID,
    REPOSITORY,
    SOURCE_INPUTS,
    ZENODO_FILES,
    ZENODO_RECORD,
    canonical_json,
    file_identity,
    is_high_level,
    label_for,
    manifested_localized_title,
    reader_url,
    read_csv,
    read_json,
    read_jsonl,
    render_html,
    source_url,
    thin_record,
    thin_segment,
    unit_kind,
    write_bytes,
    write_json,
    write_jsonl,
)


PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_NATIVE = Path(r"C:\Users\Floris\Documents\interlanguage\04_mirrors\id\measure-theoretic-probability-stochastic-processes-id")
DEFAULT_OUTPUT = PROJECT / "backend/course-capsule-v1/adapters/d30-capability-v1"


def support(status: str, anchor: str, href: str | None) -> dict[str, Any]:
    return {"status": status, "source_anchor": anchor, "label": anchor if href else None, "href": href}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native", type=Path, default=DEFAULT_NATIVE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    native = args.native.resolve()
    output = args.output.resolve()

    source_lock = {
        "schema": "d30-capability-source-lock/1",
        "course_id": COURSE_ID,
        "native_course_id": NATIVE_COURSE_ID,
        "locale": "id-ID",
        "input_count": len(SOURCE_INPUTS),
        "inputs": [{"path": rel, **file_identity(native / rel)} for rel in SOURCE_INPUTS],
        "native_repository": {
            "repository": REPOSITORY,
            "reader_content_commit": CONTENT_COMMIT,
            "reader_content_tree": CONTENT_TREE,
            "local_checkout_observed_commit": LOCAL_CHECKOUT_COMMIT,
            "local_checkout_observed_tree": LOCAL_CHECKOUT_TREE,
        },
        "public_release": {"record_id": RECORD_ID, "doi": DOI, "concept_doi": CONCEPT_DOI, "record_url": ZENODO_RECORD},
    }

    backend_manifest = read_json(native / "backend/BACKEND_MANIFEST.json")
    release_manifest = read_json(native / "release/RELEASE_MANIFEST_CHECKPOINT_38.json")
    publication = read_json(native / "00_control/ZENODO_PUBLICATION_RECEIPT_CHECKPOINT_38.json")
    github = read_json(native / "00_control/GITHUB_PUBLICATION_RECEIPT.json")
    completion = read_json(native / "00_control/COMPLETION_AUDIT_CHECKPOINT_38.json")
    entities = read_jsonl(native / "backend/entities.jsonl")
    segments = read_jsonl(native / "backend/segments.jsonl")
    native_relations = read_csv(native / "backend/relations.csv")
    terms = read_csv(native / "backend/terms.csv")
    corrections = read_csv(native / "backend/corrections.csv")
    translations = read_csv(native / "backend/translations.csv")
    outcomes = read_csv(native / "backend/outcomes.csv")
    site_manifest_rows = read_csv(native / "build/site/PACKAGE_MANIFEST.csv")
    site_manifest = {row["path"]: row for row in site_manifest_rows}

    if (backend_manifest.get("entity_count"), backend_manifest.get("segment_count"), backend_manifest.get("relation_count")) != (2538, 6333, 3256):
        raise ValueError("D30-OWNER-BACKEND-COUNTS")
    if release_manifest.get("backend_manifest_sha256") != file_identity(native / "backend/BACKEND_MANIFEST.json")["sha256"]:
        raise ValueError("D30-OWNER-BACKEND-HASH")
    if publication.get("record_id") != RECORD_ID or publication.get("all_public_sha256_exact") is not True:
        raise ValueError("D30-OWNER-PUBLIC-STATE")
    if github.get("repository", {}).get("commit") != CONTENT_COMMIT or github.get("pages", {}).get("every_manifested_byte_exact") is not True:
        raise ValueError("D30-OWNER-GITHUB-STATE")
    if completion.get("all_required_items_proved") is not True:
        raise ValueError("D30-OWNER-COMPLETION")

    record_index = [thin_record(row) for row in entities]
    segment_index = [thin_segment(row) for row in segments]
    relations = [
        {
            "schema": "d30-native-relation-reference/1",
            "relation_id": row["relation_id"],
            "relation_type": row["relation_type"],
            "source_id": row["source_id"],
            "target_id": row["target_id"],
            "status": row["status"],
            "native_evidence_present": bool(row.get("evidence")),
            "body_embedded": False,
        }
        for row in native_relations
    ]
    rights = [row for row in record_index if row["record_type"] == "rights"]
    term_index = [
        {"schema": "d30-term-reference/1", "term_id": row["term_id"], "en": row["en"], "id_ID": row["id_ID"], "status": row["status"], "scope": row["scope"], "body_embedded": False}
        for row in terms
    ]
    correction_index = [
        {"schema": "d30-correction-reference/1", "correction_id": row["correction_id"], "change_kind": row["change_kind"], "source_id": row["source_id"], "target_id": row["target_id"], "evidence_locator": row["evidence"], "status": row["status"], "description_embedded": False}
        for row in corrections
    ]

    entity_by_id = {row["id"]: row for row in entities}
    thin_by_id = {row["native_id"]: row for row in record_index}
    high = sorted((row for row in entities if is_high_level(row)), key=lambda row: (str(row.get("path") or ""), int(row.get("order") or 0), row["id"]))
    high_ids = {row["id"] for row in high}
    localized_titles = {row["id"]: manifested_localized_title(native, row, site_manifest) for row in high}

    def high_ancestor(native_id: str) -> str | None:
        seen: set[str] = set()
        current = native_id
        while current and current not in seen:
            if current in high_ids:
                return current
            seen.add(current)
            current = str((entity_by_id.get(current) or {}).get("parent_id") or "")
        return None

    descendants: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in entities:
        root = high_ancestor(row["id"])
        if root and row["id"] != root:
            descendants[root].append(row)

    relation_sources: dict[tuple[str, str], list[str]] = defaultdict(list)
    previous: dict[str, list[str]] = defaultdict(list)
    for row in native_relations:
        relation_sources[(row["relation_type"], row["target_id"])].append(row["source_id"])
        if row["relation_type"] == "precedes" and row["source_id"] in high_ids and row["target_id"] in high_ids:
            previous[row["target_id"]].append(row["source_id"])

    license_by_id = {row["native_id"]: row.get("license", "see native rights record") for row in rights}

    def linked_support(kind: str, target_id: str) -> dict[str, Any]:
        linked = sorted(relation_sources.get((kind, target_id), []))
        if not linked:
            return support("not_present", f"native-relation:{kind}", None)
        native_id = linked[0]
        row = entity_by_id.get(native_id)
        href = reader_url(row) if row else PAGES + "#" + native_id
        return support("complete", native_id, href)

    shared_units: list[dict[str, Any]] = []
    learner_units: list[dict[str, Any]] = []
    for root in high:
        localized_title, title_source = localized_titles[root["id"]]
        children = sorted(descendants[root["id"]], key=lambda row: (int(row.get("order") or 0), row["id"]))
        exercises = [row for row in children if unit_kind(row) in {"exercise", "assessment-problem", "mastery-sequence"}]
        exercise_rows = []
        for sequence, row in enumerate(exercises, 1):
            exercise_rows.append({
                "id": row["id"], "unit_id": root["id"], "title": label_for(row), "kind": unit_kind(row),
                "sequence": sequence, "curriculum_status": row.get("translation_state") or "active", "href": reader_url(row),
                "hint": linked_support("hints", row["id"]), "check": linked_support("answers", row["id"]), "solution": linked_support("solves", row["id"]),
            })
        direct_sections = sorted({row["id"] for row in children if row.get("parent_id") == root["id"] and unit_kind(row) in {"section", "heading", "outcomes", "prerequisites"}})
        component = {"id": root.get("rights_id") or "rights-unasserted", "source": source_url(root), "license": license_by_id.get(root.get("rights_id"), "see native rights record")}
        shared_units.append({
            "id": root["id"], "title": localized_title, "href": reader_url(root), "sections": direct_sections,
            "objectives_href": None, "previous_units": sorted(set(previous[root["id"]])), "components": [component], "exercises": exercise_rows,
        })
        learner_units.append({
            "native_id": root["id"], "title": localized_title, "title_source": title_source, "unit_kind": unit_kind(root), "order": root.get("order"),
            "rights_id": root.get("rights_id"), "translation_state": root.get("translation_state"), "reader_url": reader_url(root),
            "original_url": source_url(root), "exercise_ids": [row["id"] for row in exercise_rows], "body_embedded": False,
        })

    prereq = []
    for row in native_relations:
        if row["relation_type"] not in {"depends-on", "prerequisite"}:
            continue
        source = entity_by_id.get(row["source_id"])
        prereq.append({
            "id": row["relation_id"], "unit": row["source_id"], "prerequisite": row["target_id"],
            "required_for_course": row["relation_type"] == "prerequisite", "sections": [], "exercises": [],
            "href": reader_url(source) if source else PAGES,
        })

    lab_roots = [row for row in high if unit_kind(row) == "lab"]
    lab_rows = []
    for lab in lab_roots:
        member_ids = {lab["id"], *(row["id"] for row in descendants[lab["id"]])}
        lab_rows.append({
            "id": lab["id"], "unit": lab["id"], "environment": "d30.native-pinned-runtime",
            "exercise_ids": sorted(row["id"] for row in descendants[lab["id"]] if unit_kind(row) in {"exercise", "mastery-sequence"}),
            "artifact_ids": sorted({row["target_id"] for row in native_relations if row["relation_type"] == "executes" and row["source_id"] in member_ids}),
        })

    endpoints = {row["source_id"] for row in native_relations} | {row["target_id"] for row in native_relations}
    external_nodes = sorted(endpoints - set(entity_by_id))
    public_files = [
        {"filename": name, "bytes": size, "sha256": digest, "url": ZENODO_FILES + name + "/content"}
        for name, (size, digest) in PUBLIC_FILES.items()
    ]
    public_evidence = {
        "schema": "d30-public-evidence/1", "record_id": RECORD_ID, "doi": DOI, "concept_doi": CONCEPT_DOI,
        "record_url": ZENODO_RECORD, "repository": REPOSITORY, "reader": PAGES, "content_commit": CONTENT_COMMIT,
        "content_tree": CONTENT_TREE, "anonymous_reader_byte_readback": True, "all_public_sha256_exact": True,
        "files": public_files, "authoritative_originals": list(AUTHORITATIVE_ORIGINALS),
    }
    counts = dict(EXPECTED_COUNTS)
    counts.update({
        "exercise_surfaces": sum(len(row["exercises"]) for row in shared_units),
        "prerequisite_routes": len(prereq),
        "external_relation_nodes": len(external_nodes),
        "relation_types": dict(sorted(Counter(row["relation_type"] for row in native_relations).items())),
        "translation_states": dict(sorted(Counter(row["translation_state"] for row in entities).items())),
        "entity_types": dict(sorted(Counter(row["record_type"] for row in entities).items())),
    })
    limitations = [
        "Adapter ini hanya memproyeksikan identitas, status, relasi, hak, hash, dan rute; badan prosa, rumus, kode, solusi, HTML, PDF, serta arsip native tidak disalin.",
        "Hak 42 komponen dipertahankan per rekaman; tidak ada lisensi payung untuk gabungan.",
        "Prasyarat O006/C140 hanya ditautkan sebagai dependensi eksternal tanpa byte lintas jalur.",
        "Tautan pembaca menunjuk permukaan publik native id-ID; antarmuka pusat tidak menerjemahkan isi kursus.",
        "Tidak ada klaim WCAG, pengujian teknologi bantu, PDF bertag, atau pertukaran reversible dari adapter ini.",
    ]
    learning_map = {
        "contract": CONTRACT, "course_id": COURSE_ID, "locale": "id-ID", "native_dataset": "o009.backend-manifest.v2",
        "source_catalog": {"path": "release/RELEASE_MANIFEST_CHECKPOINT_38.json", **file_identity(native / "release/RELEASE_MANIFEST_CHECKPOINT_38.json"), "url": ZENODO_FILES + "RELEASE_MANIFEST_CHECKPOINT_38.json/content"},
        "units": shared_units, "prerequisite_routes": prereq, "labs": lab_rows,
        "environments": [{"id": "d30.native-pinned-runtime", "runtime_version": "native checkpoint-38 runtime lock", "lock": f"{REPOSITORY}/blob/{CONTENT_COMMIT}/00_control/RUNTIME_LOCK.json"}],
        "artifacts": [{"id": "d30.public." + str(index), "kind": "public-release-file", "path": row["url"]} for index, row in enumerate(public_files, 1)],
        "sources": [{"id": row["native_id"], "role": "component-rights", "license": row.get("license", "see native rights record"), "identity": {"source_locator": row.get("source_locator"), "source_sha256": row.get("source_sha256")}} for row in rights],
        "external_relation_nodes": external_nodes, "limitations": limitations,
    }
    capabilities = {
        "schema": "d30-capabilities/1", "contract": CONTRACT, "course_id": COURSE_ID, "locale": "id-ID", "counts": counts,
        "scope": {"theory_units": 36, "overview_units": 3, "original_bridge_units": 4, "labs": 5, "mastery_problems": 36, "solved_mastery_problems": 36, "assessment_forms": 2, "assessment_forms_equivalent": True},
        "zero_copy": {"native_bodies_embedded": False, "native_ids_preserved": True, "native_hashes_preserved": True, "external_pinned_checkout_required_for_rebuild": True},
        "access": {"public_reader": PAGES, "public_record": ZENODO_RECORD, "original_repository": REPOSITORY, "reader_content_commit": CONTENT_COMMIT, "authoritative_originals": list(AUTHORITATIVE_ORIGINALS)},
        "accessibility": {"offline_html_is_canonical_accessible_surface": True, "wcag_conformance_claimed": False, "assistive_technology_testing_claimed": False, "tagged_pdf_claimed": False},
        "rights": {"component_specific": True, "blanket_license_claimed": False, "rights_records": len(rights)},
        "public_state_changed": False,
    }
    claim_boundary = {
        "schema": "d30-claim-boundary/1", "course_id": COURSE_ID, "admitted": ["stable native identities", "explicit native states", "native relations", "component rights", "public reader and original-source routes", "checkpoint-38 public hashes"],
        "not_claimed": ["copied native bodies", "blanket license", "cross-lane prerequisite bytes", "WCAG conformance", "assistive-technology testing", "tagged PDF", "reversible exchange"],
    }
    learner_map = {"schema": "d30-learner-map/1", "course_id": COURSE_ID, "contract": CONTRACT, "units": learner_units, "limitations": limitations}
    educator_map = {
        "schema": "d30-educator-map/1", "course_id": COURSE_ID, "contract": CONTRACT, "units": learner_units,
        "indices": {"relations": "relations-index.jsonl", "rights": "rights-index.jsonl", "terms": "terms-index.jsonl", "corrections": "corrections-index.jsonl"},
        "assessment": {"forms": 2, "problems_per_form": 8, "points_per_form": 100, "recommended_minutes": 240, "common_outcomes": 26},
        "limitations": limitations,
    }

    write_json(output / "input/source-lock.json", source_lock)
    write_jsonl(output / "data/native-record-index.jsonl", record_index)
    write_jsonl(output / "data/native-segment-index.jsonl", segment_index)
    write_jsonl(output / "data/relations-index.jsonl", relations)
    write_jsonl(output / "data/rights-index.jsonl", rights)
    write_jsonl(output / "data/terms-index.jsonl", term_index)
    write_jsonl(output / "data/corrections-index.jsonl", correction_index)
    write_json(output / "data/capabilities.json", capabilities)
    write_json(output / "data/claim-boundary.json", claim_boundary)
    write_json(output / "data/public-evidence.json", public_evidence)
    write_json(output / "data/learner-map.json", learner_map)
    write_json(output / "data/educator-map.json", educator_map)
    write_json(output / "data/learning-map.json", learning_map)
    write_json(output / "views/capabilities.json", capabilities)
    write_bytes(output / "views/D30.html", render_html("D30 · Probabilitas Teoretis-Ukuran dan Proses Stokastik", "Hub zero-copy untuk 57 permukaan tingkat-atas; isi tetap pada pembaca native yang dipatok.", learner_units))
    write_bytes(output / "views/D30-pengajar.html", render_html("D30 · Peta Pengajar", "Peta bukti zero-copy untuk hak komponen, relasi, asesmen, laboratorium, dan sumber asli.", learner_units, educator=True))
    readme = """# D30 zero-copy learning-capability adapter

This additive adapter projects the pinned O009/D30 modular backend into
`course-learning-capability/1`. It preserves native IDs, states, relations,
component rights, hashes, and public reader/original-source routes. It never
copies native prose, formulas, solutions, code, HTML, PDF, or archive payloads.

The native repository and checkpoint-38 Zenodo record remain authoritative.
The 42 rights records remain component-specific; no blanket license is claimed.
The O006/C140 prerequisite remains an external reference without copied bytes.

Build, validate, and package from the central checkout:

```text
python -B scripts/build_d30_capability_v1.py
python -B scripts/validate_d30_capability_v1.py
python -B scripts/package_d30_capability_v1.py
```

The learner and educator views link visibly back to `/en/` and `/id/`, and each
course surface links to both the public native reader and pinned original source.
No shared integration, Git, or publication state is changed by these scripts.
"""
    write_bytes(output / "README.md", readme.encode("utf-8"))

    fixtures = {
        "dropped-native-id": ("drop-native-id", "D30-NATIVE-ID-SET"),
        "copied-body": ("copy-body", "D30-ZERO-COPY"),
        "hash-drift": ("alter-hash", "D30-PUBLIC-IDENTITY"),
        "flattened-rights": ("flatten-rights", "D30-RIGHTS-BOUNDARY"),
        "bad-reader-link": ("bad-reader-link", "D30-PUBLIC-ROUTES"),
        "collapsed-state": ("collapse-state", "D30-STATE-FIDELITY"),
    }
    for name, (operation, expected) in fixtures.items():
        write_json(output / f"fixtures/negative/{name}.json", {"schema": "d30-negative-fixture/1", "case": name, "operation": operation, "expected_error": expected})

    output_paths = ["README.md", "input/source-lock.json", *[rel for rel, _ in BUNDLE_FILES.values()], "views/capabilities.json", "views/D30.html", "views/D30-pengajar.html", *[f"fixtures/negative/{name}.json" for name in fixtures]]
    manifest = {
        "schema": "d30-capability-manifest/1", "course_id": COURSE_ID, "native_course_id": NATIVE_COURSE_ID,
        "contract": CONTRACT, "locale": "id-ID", "content_policy": "identity_state_rights_evidence_only",
        "zero_copy_native_bodies": True, "native_bodies_copied": False, "zero_copy": True,
        "component_rights_preserved": True, "public_state_changed": False,
        "native_release": {"commit": CONTENT_COMMIT, "tree": CONTENT_TREE}, "counts": counts,
        "source_lock": {"path": "input/source-lock.json", **file_identity(output / "input/source-lock.json")},
        "outputs": [{"path": rel, **file_identity(output / rel)} for rel in sorted(output_paths)],
        "validation_path": "validation.json", "package_receipt_path": "build/PACKET_BUILD_RECEIPT.json",
    }
    write_json(output / "manifest.json", manifest)
    print(json.dumps({"result": "PASS", "output": str(output), "entities": len(record_index), "segments": len(segment_index), "high_level_units": len(high)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"D30 build failed: {exc}", file=sys.stderr)
        sys.exit(1)
