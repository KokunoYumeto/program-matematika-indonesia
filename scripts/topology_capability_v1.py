"""C90 topology capability adapter over the frozen native PreTeXt backend.

The adapter copies metadata and receipts, never textbook prose or generated reader
assets. The native book remains authoritative; central pages are zero-copy routes.
"""
from __future__ import annotations

import csv
import hashlib
import html
import io
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = Path("backend/course-capsule-v1/adapters/topology-capability-v1")
DOCS = Path("docs/backend/topology")
READER_URL = "https://kokunoyumeto.github.io/topology-an-inquiry-based-approach-id/reader/complete/"
ZENODO_RECORD = "22229720"
ZENODO_CONCEPT = "22059894"
NATIVE_COMMIT = "b2869e5455f91984cc7a20104c7f76ce301a7b28"
NATIVE_TREE = "ccacfde62433f82bf9436feccaadf3fe0370dce3"
UPSTREAM_COMMIT = "0c2d8f614ef87aa00de373f3418146c2f1d13bb9"
UPSTREAM_TREE = "7df245934eedb7174d5ff8af18afff5a7abdde78"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def fact(path, data):
    return {
        "path": str(path).replace("\\", "/"),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def rows(data):
    # Preserve surplus CSV fields explicitly instead of DictReader's non-JSON
    # ``None`` key. This keeps malformed-but-evidentiary native rows lossless.
    return list(csv.DictReader(io.StringIO(data.decode("utf-8-sig")), restkey="_extra_columns"))


def xml_identity(data):
    root = ET.fromstring(data)
    identifier = root.attrib.get(XML_ID)
    assert identifier, "PreTeXt root is missing xml:id"
    title = identifier
    for child in root.iter():
        if child.tag.rsplit("}", 1)[-1] == "title":
            title = " ".join("".join(child.itertext()).split())
            break
    return identifier, title


def native_metadata_paths(native_root):
    repo = native_root / "repo"
    paths = [
        Path("repo/backend/complete_edition_source_backend_manifest.json"),
        Path("repo/backend/chapters_01_20_full_corpus_closure_manifest.json"),
        Path("repo/backend/o003_completion_current_manifest.json"),
        Path("00_control/TERMINOLOGY.csv"),
        Path("00_control/SOURCE_CORRECTIONS.csv"),
        Path("repo/LICENSES.md"),
        Path("repo/companion/RIGHTS.md"),
        Path("repo/qa/CHAPTERS01_20_COMPLETE_PDF_QA.json"),
        Path("repo/qa/CHAPTERS01_20_FULL_CORPUS_CLOSURE_QA.json"),
        Path("repo/qa/CHAPTER20_COMPLETE_HTML_QA.json"),
        Path("repo/qa/CHAPTER20_COMPLETE_DOCS_QA.json"),
        Path("repo/qa/NATIVE_INDONESIAN_TERMINOLOGY_QA_2026-08-31.md"),
        Path("repo/qa/ZENODO_COMPLETE_MAINTENANCE_RDM_STATE.json"),
        Path("repo/qa/ZENODO_COMPLETE_MAINTENANCE_PUBLICATION_RECEIPT.md"),
        Path("repo/qa/CHAPTER20_COMPLETE_TERMINOLOGY_MAINTENANCE_GITHUB_RECEIPT.md"),
    ]
    paths += [Path(f"repo/backend/chapter_{chapter:02d}_companion_manifest.json") for chapter in range(1, 21)]
    for pattern in ("chapter_*_entry_aliases.csv", "chapter_*_source_prompt_map.csv",
                    "chapter_*_grouping_nodes.json", "chapter_*_occurrence_entry_aliases.csv"):
        paths.extend(Path("repo/backend") / item.name for item in sorted((repo / "backend").glob(pattern)))
    unique = sorted(set(paths), key=lambda item: item.as_posix())
    for relative in unique:
        assert (native_root / relative).is_file(), relative
    return unique


def _manifest_entries(manifest):
    direct = manifest.get("entries")
    if isinstance(direct, list):
        return direct
    companion = manifest.get("companion") or {}
    return list(companion.get("source_entries") or []) + list(companion.get("mastery_entries") or [])


def _entry_stages(entry):
    surfaces = entry.get("surfaces") if isinstance(entry.get("surfaces"), dict) else {}
    stage_ids = entry.get("stage_ids") if isinstance(entry.get("stage_ids"), dict) else {}
    identifier = entry.get("id") or entry.get("entry_id")
    assert identifier

    def surface_id(stage):
        """Retain native schema drift: old manifests use strings, newer ones objects."""
        value = surfaces.get(stage)
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            return value.get("id") or value.get("xml_id")
        return None

    result = {
        # PreTeXt's rendered statement knowl is keyed by the exercise id even when
        # a newer manifest records a separate backend-only statement alias.
        "statement": entry.get("statement_id") or stage_ids.get("statement") or identifier,
        "hint": entry.get("hint_id") or surface_id("hint") or stage_ids.get("hint") or entry.get("hint") or identifier + "-hint",
        "answer": entry.get("answer_id") or surface_id("answer") or stage_ids.get("answer") or entry.get("answer") or identifier + "-answer",
        "solution": entry.get("solution_id") or surface_id("solution") or stage_ids.get("solution") or entry.get("solution") or identifier + "-solution",
    }
    assert all(isinstance(value, str) and value for value in result.values())
    return result


SOURCE_KINDS = {
    "activity_checkpoint", "exercise_guide", "source_prompt_guide",
    "source_support", "source_task_guide",
}


def normalize_entry(entry, chapter=None, module=None):
    identifier = entry.get("id") or entry.get("entry_id")
    kind = entry.get("entry_type") or entry.get("kind") or ("completion_mastery" if module else "unknown")
    stages = _entry_stages(entry)
    context = f"chapter_{chapter:02d}" if chapter else module["module_id"]
    return {
        "id": identifier,
        "context_id": context,
        "chapter": chapter,
        "completion_module": module["module_id"] if module else None,
        "kind": kind,
        "classification": "source_support" if kind in SOURCE_KINDS else "mastery",
        "title": entry.get("title") or identifier,
        "source_anchor": entry.get("source_anchor"),
        "source_locator": entry.get("authority_locator"),
        "component_rights": entry.get("license") or "CC BY 4.0",
        "stages": stages,
        "stage_urls": {name: READER_URL + "knowl/" + value + ".html" for name, value in stages.items()},
        "learner_url": "https://kokunoyumeto.github.io/program-matematika-indonesia/backend/topology/C90.html#" + identifier,
        "native": entry,
    }


def extract_entries(input_root):
    chapter_entries, chapter_counts = [], {}
    for chapter in range(1, 21):
        manifest = load_json(input_root / f"repo/backend/chapter_{chapter:02d}_companion_manifest.json")
        normalized = [normalize_entry(entry, chapter=chapter) for entry in _manifest_entries(manifest)]
        chapter_entries.extend(normalized)
        chapter_counts[chapter] = len(normalized)
    completion = load_json(input_root / "repo/backend/o003_completion_current_manifest.json")
    completion_entries = [normalize_entry(entry, module=module)
                          for module in completion["modules"] for entry in module["mastery_exercises"]]
    return chapter_entries, completion_entries, chapter_counts, completion


def freeze_native(native_root):
    """Create the immutable metadata intake once; later builds replay this intake."""
    native_root = Path(native_root).resolve()
    repo = native_root / "repo"
    destination = ROOT / BASE / "input"
    assert not destination.exists(), "Frozen topology input already exists; do not silently advance it"
    commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    tree = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD^{tree}"], text=True).strip()
    assert (commit, tree) == (NATIVE_COMMIT, NATIVE_TREE), (commit, tree)
    copied = []
    for relative in native_metadata_paths(native_root):
        data = (native_root / relative).read_bytes()
        assert not re.search(rb"(?i)[A-Z]:[\\/](?:Users|Documents)[\\/]", data), relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        copied.append(fact(relative, data))

    closure = load_json(destination / "repo/backend/chapters_01_20_full_corpus_closure_manifest.json")
    chapters = []
    source_paths = closure["direct_include_contract"]["main_chapters"]
    for sequence, (source_path, companion) in enumerate(zip(source_paths, closure["chapter_companions"]), start=1):
        source_relative = Path("repo/source") / Path(source_path).name
        source_data = (native_root / source_relative).read_bytes()
        source_id, source_title = xml_identity(source_data)
        wrapper_relative = Path("repo") / companion["wrapper"]["path"]
        wrapper_data = (native_root / wrapper_relative).read_bytes()
        companion_id, companion_title = xml_identity(wrapper_data)
        for page_id in (source_id, companion_id):
            assert (repo / "docs/reader/complete" / f"{page_id}.html").is_file(), page_id
        chapters.append({
            "sequence": sequence,
            "source_id": source_id,
            "source_title": source_title,
            "source_file": fact(source_relative, source_data),
            "source_url": READER_URL + source_id + ".html",
            "companion_id": companion_id,
            "companion_title": companion_title,
            "companion_file": fact(wrapper_relative, wrapper_data),
            "companion_url": READER_URL + companion_id + ".html",
            "component_manifest": companion["component_manifest"],
            "native_manifest_status": companion["component_manifest_status"],
        })

    chapter_entries, completion_entries, _, completion = extract_entries(destination)
    all_entries = chapter_entries + completion_entries
    ids = [entry["id"] for entry in all_entries]
    assert len(ids) == len(set(ids)) == 1227
    runtime = []
    for entry in all_entries:
        for stage, identifier in entry["stages"].items():
            relative = Path("knowl") / f"{identifier}.html"
            data = (repo / "docs/reader/complete" / relative).read_bytes()
            runtime.append({"entry_id": entry["id"], "stage": stage, "stage_id": identifier,
                            **fact(relative, data)})
    runtime_bytes = encoded({"contract": "topology-reader-destination-index/1", "records": runtime})
    (destination / "reader-destination-index.json").write_bytes(runtime_bytes)

    rdm = load_json(destination / "repo/qa/ZENODO_COMPLETE_MAINTENANCE_RDM_STATE.json")
    assert rdm["phase"] == "receipt_written" and rdm["record_id"] == ZENODO_RECORD
    assert rdm["concept_record_id"] == ZENODO_CONCEPT
    assert rdm["public_readback"]["files"] == rdm["files"]
    lock = {
        "contract": "topology-native-intake/1",
        "native_folder": native_root.name,
        "native_repository": "https://github.com/KokunoYumeto/topology-an-inquiry-based-approach-id",
        "native_commit": commit,
        "native_tree": tree,
        "upstream_authority": {"commit": UPSTREAM_COMMIT, "tree": UPSTREAM_TREE,
                               "archive_bytes": 2200204,
                               "archive_sha256": "d7cadeb10e6525568a90340bceadbc77dc1e5620053e257e8b3126acb8ce01f3"},
        "native_files": copied,
        "chapters": chapters,
        "reader_destination_index": fact("reader-destination-index.json", runtime_bytes),
        "reader_destination_records": len(runtime),
        "completion_module_ids": [module["module_id"] for module in completion["modules"]],
        "public_release": {"concept_doi": rdm["concept_doi"], "record_doi": rdm["doi"],
                           "record_id": rdm["record_id"], "version": rdm["version"],
                           "predecessor_record_id": rdm["predecessor_record_id"], "files": rdm["files"],
                           "verified_utc": rdm["public_readback"]["verified_utc"]},
        "snapshot_boundary": ("Inputs bind current Git commit b2869e5. The public source/backend ZIP is a prior "
                              "sealed snapshot; its aggregate manifest predates later receipt-state updates."),
    }
    (destination / "source-lock.json").write_bytes(encoded(lock))
    return lock


def read_inputs(root=ROOT):
    input_root = root / BASE / "input"
    lock = load_json(input_root / "source-lock.json")
    assert lock["contract"] == "topology-native-intake/1"
    assert lock["native_commit"] == NATIVE_COMMIT and lock["native_tree"] == NATIVE_TREE
    for expected in lock["native_files"]:
        assert fact(expected["path"], (input_root / expected["path"]).read_bytes()) == expected
    runtime_data = (input_root / "reader-destination-index.json").read_bytes()
    assert fact("reader-destination-index.json", runtime_data) == lock["reader_destination_index"]
    chapter_entries, completion_entries, chapter_counts, completion = extract_entries(input_root)
    return {"lock": lock, "input_root": input_root, "chapter_entries": chapter_entries,
            "completion_entries": completion_entries, "chapter_counts": chapter_counts,
            "completion": completion,
            "closure": load_json(input_root / "repo/backend/chapters_01_20_full_corpus_closure_manifest.json"),
            "complete": load_json(input_root / "repo/backend/complete_edition_source_backend_manifest.json"),
            "terms": rows((input_root / "00_control/TERMINOLOGY.csv").read_bytes()),
            "corrections": rows((input_root / "00_control/SOURCE_CORRECTIONS.csv").read_bytes()),
            "runtime": load_json(input_root / "reader-destination-index.json")["records"]}


def build_model(source):
    entries = source["chapter_entries"] + source["completion_entries"]
    assert len(entries) == 1227 and len({entry["id"] for entry in entries}) == 1227
    stage_index = {(row["entry_id"], row["stage"]): row for row in source["runtime"]}
    assert len(stage_index) == len(source["runtime"]) == 4908
    for entry in entries:
        entry["stage_facts"] = {}
        for stage, stage_id in entry["stages"].items():
            assert stage_index[(entry["id"], stage)]["stage_id"] == stage_id
            entry["stage_facts"][stage] = dict(stage_index[(entry["id"], stage)])
    aliases = []
    for chapter in (16, 17):
        path = source["input_root"] / f"repo/backend/chapter_{chapter:02d}_occurrence_entry_aliases.csv"
        for row in rows(path.read_bytes()):
            row["chapter"] = chapter
            aliases.append(row)
    assert len(aliases) == 3
    entry_ids = {entry["id"] for entry in entries}
    assert all(row["canonical_entry_id"] in entry_ids for row in aliases)
    terms = [{"id": row["id"], "native": row} for row in source["terms"]]
    corrections = [{"id": row["id"], "native": row} for row in source["corrections"]]
    assert len(terms) == len({item["id"] for item in terms}) == 299
    assert len(corrections) == len({item["id"] for item in corrections}) == 272
    chapters = []
    for item in source["lock"]["chapters"]:
        chapter = dict(item)
        chapter["entry_count"] = source["chapter_counts"][item["sequence"]]
        chapter["entry_ids"] = [entry["id"] for entry in source["chapter_entries"]
                                if entry["chapter"] == item["sequence"]]
        chapters.append(chapter)
    relations = [{"from": entry["id"], "type": "has_" + kind, "to": entry["stages"][kind],
                  "url": entry["stage_urls"][kind]}
                 for entry in entries for kind in ("hint", "answer", "solution")]
    correction_statuses = Counter(item["native"]["status"] for item in corrections)
    term_statuses = Counter(item["native"]["status"] for item in terms)
    counts = {
        "chapters": len(chapters), "chapter_companions": len(chapters),
        "completion_modules": len(source["completion"]["modules"]),
        "chapter_staged_records": len(source["chapter_entries"]),
        "source_support_records": sum(entry["classification"] == "source_support" for entry in source["chapter_entries"]),
        "chapter_mastery_records": sum(entry["classification"] == "mastery" for entry in source["chapter_entries"]),
        "completion_mastery_records": len(source["completion_entries"]),
        "staged_records": len(entries), "stage_surfaces": len(entries) * 4,
        "support_relations": len(relations), "occurrence_aliases": len(aliases),
        "terms": len(terms), "term_statuses": dict(term_statuses),
        "corrections": len(corrections), "correction_statuses": dict(correction_statuses),
        "unresolved_corrections": correction_statuses.get("unresolved", 0),
    }
    completion_modules = []
    for item in source["completion"]["modules"]:
        module = dict(item)
        module["reader_url"] = READER_URL + item["module_id"] + ".html"
        module["entry_ids"] = [entry["id"] for entry in source["completion_entries"]
                               if entry["completion_module"] == item["module_id"]]
        completion_modules.append(module)
    return {
        "contract": "topology-learning-capability/1", "role": "C90", "locale": "id-ID",
        "native_edition": {"repository": source["lock"]["native_repository"],
                           "commit": source["lock"]["native_commit"], "tree": source["lock"]["native_tree"],
                           "upstream_authority": source["lock"]["upstream_authority"],
                           "public_release": source["lock"]["public_release"], "reader_url": READER_URL},
        "counts": counts, "chapters": chapters, "completion_modules": completion_modules,
        "entries": entries, "support_relations": relations, "occurrence_aliases": aliases,
        "terms": terms, "corrections": corrections,
        "rights_accessibility": {
            "translated_spine": "CC BY-NC-SA 3.0 (conservative determination)",
            "original_companions_completion_lab": "CC BY 4.0",
            "other_components": "Per-component notices retained; no blanket license",
            "html_primary_accessible_surface": True, "pdf_tagged": False,
            "offline_html": source["lock"]["public_release"]["files"]["topologi-pendekatan-berbasis-inkuiri-edisi-lengkap-html.zip"],
            "pdf": source["lock"]["public_release"]["files"]["topologi-pendekatan-berbasis-inkuiri-edisi-lengkap-id.pdf"],
            "native_qa": {"source_closure_files": 278, "source_closure_edges": 277,
                          "expanded_reader_elements": 65255, "expanded_reader_xml_ids": 5609,
                          "expanded_reader_xrefs": 365, "unresolved_xrefs": 0,
                          "html_files_checked": 22373, "missing_image_alt": 0,
                          "empty_nondecorative_alt": 0, "unnamed_iframes": 0}},
        "projection_policy": {
            "profile": "thin_format_neutral_zero_copy", "native_book_authoritative": True,
            "metadata_inputs": "Exact current Git bytes frozen; native fields retained inside each projected record",
            "schema_drift": "Chapters 1-20 normalized without rewriting their native manifest objects",
            "stage_destinations": "All 4,908 statement/hint/answer/solution knowl bytes indexed; content not copied",
            "aliases": "Three physical occurrences canonicalized to existing staged records; not duplicated",
            "snapshot_boundary": source["lock"]["snapshot_boundary"], "full_native_roundtrip_claimed": False},
        "limitations": [
            "The adapter routes to the native PreTeXt reader; it does not convert or rewrite the textbook.",
            "The upstream spine's 252 exercise containers and 1,142 tasks are not interchangeable with 1,227 canonical staged-support records.",
            "Answers and solutions are separately licensed companion/mastery work, not upstream GVSU answer fields.",
            "Two source corrections remain unresolved and one terminology row remains provisional; both states are preserved.",
            "The PDF is untagged; the semantic HTML reader is the authoritative accessible surface.",
            "The current Git metadata snapshot postdates the sealed public source/backend ZIP's aggregate manifest; the distinction is explicit."]}
